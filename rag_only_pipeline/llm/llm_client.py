"""LLM client for the independent RAG pipeline.
Provides:
1. MockLLM (default): Deterministic offline generation with realistic grounding & citations.
2. OllamaLLM: Local OpenAI-compatible API client pointing to http://localhost:11434/v1.
3. Central generate() function.
"""

import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from rag_only_pipeline.config import DEFAULT_MODEL, OLLAMA_API_BASE

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLM:
    """Abstract base class for RAG LLM clients."""

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        raise NotImplementedError


class MockLLM(BaseLLM):
    """Deterministic Mock LLM for offline testing and verification.
    Generates grounded mock answers using the retrieved chunks provided in the prompt.
    """

    def __init__(self, scripted_responses: Optional[List[str]] = None):
        self.scripted_responses: List[str] = list(scripted_responses or [])
        self.call_history: List[List[Dict[str, str]]] = []

    def queue_response(self, text: str) -> None:
        self.scripted_responses.append(text)

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        self.call_history.append(messages)

        # Approximate prompt token calculation (~4 chars per token)
        prompt_text = "".join(m.get("content", "") for m in messages)
        prompt_tokens = max(1, len(prompt_text) // 4)

        if self.scripted_responses:
            content = self.scripted_responses.pop(0)
            comp_tokens = max(1, len(content) // 4)
            return LLMResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                total_tokens=prompt_tokens + comp_tokens,
                raw_response={"mock": True}
            )

        # Extract available chunk IDs from prompt context
        user_msg = messages[-1]["content"] if messages else ""
        chunk_ids = re.findall(r"--- \[CHUNK \d+: ([A-Za-z0-9_#\-]+)\]", user_msg)

        if not chunk_ids:
            content = "not found in corpus"
        else:
            primary_chunk = chunk_ids[0]
            # Inspect user question
            q_match = re.search(r"QUESTION:\s*(.*?)(?:\n\n|\Z)", user_msg, re.DOTALL)
            q_text = q_match.group(1).strip() if q_match else "question"

            # Check if there is gold winner or competitors in context
            gold_match = re.search(r"gold:\s*([^\n]+)", user_msg)
            comp_match = re.search(r"competitors:\s*([^\n]+)", user_msg)

            if "Who won" in q_text and gold_match:
                winner = gold_match.group(1).strip()
                content = f"{winner} [{primary_chunk}]."
            elif "how many" in q_text.lower() and comp_match:
                val = comp_match.group(1).strip()
                content = f"{val} [{primary_chunk}]."
            else:
                content = f"Based on the provided corpus, the answer is grounded in [{primary_chunk}]."

        comp_tokens = max(1, len(content) // 4)
        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=comp_tokens,
            total_tokens=prompt_tokens + comp_tokens,
            raw_response={"mock": True}
        )


class OllamaLLM(BaseLLM):
    """Client for local Ollama instance with thinking mode suppression."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        api_base: str = OLLAMA_API_BASE
    ):
        self.model_name = model_name
        self.api_base = api_base.rstrip("/")
        if self.api_base.endswith("/v1"):
            self.native_base = self.api_base[:-3]
        else:
            self.native_base = self.api_base
        self.native_endpoint = f"{self.native_base}/api/chat"
        self.v1_endpoint = f"{self.api_base}/chat/completions" if self.api_base.endswith("/v1") else f"{self.api_base}/v1/chat/completions"

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        # First attempt: native Ollama endpoint with explicit think=False
        native_payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        req_data = json.dumps(native_payload).encode("utf-8")
        req = urllib.request.Request(
            self.native_endpoint,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))

            msg = res_data.get("message", {})
            content = msg.get("content", "").strip()
            # Strip any leaked <think> blocks if present
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

            prompt_tokens = res_data.get("prompt_eval_count", 0)
            completion_tokens = res_data.get("eval_count", 0)
            total_tokens = prompt_tokens + completion_tokens

            return LLMResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                raw_response=res_data
            )

        except urllib.error.HTTPError as he:
            # If native /api/chat returned 404, fallback to OpenAI /v1 endpoint
            if he.code != 404:
                logger.error(f"Ollama native endpoint HTTP error {he.code}: {he}")
                raise
        except urllib.error.URLError as ue:
            # If connection refused on native host
            logger.error(f"Failed to connect to Ollama at {self.native_endpoint}: {ue}")
            raise ConnectionError(
                f"Could not connect to Ollama at {self.native_endpoint}. "
                f"Ensure Ollama is running (`ollama serve`). Details: {ue}"
            )

        # Fallback to OpenAI-compatible endpoint
        v1_payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        v1_data = json.dumps(v1_payload).encode("utf-8")
        v1_req = urllib.request.Request(
            self.v1_endpoint,
            data=v1_data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(v1_req, timeout=120) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))

            choice = res_data.get("choices", [{}])[0]
            message_obj = choice.get("message", {})
            content = message_obj.get("content", "").strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

            usage = res_data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            return LLMResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                raw_response=res_data
            )
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to Ollama fallback at {self.v1_endpoint}: {e}")
            raise ConnectionError(
                f"Could not connect to Ollama at {self.v1_endpoint}. Details: {e}"
            )


# Global active LLM client (defaults to MockLLM)
_active_llm: BaseLLM = MockLLM()


def set_active_llm(llm: BaseLLM) -> None:
    """Set the active LLM backend."""
    global _active_llm
    _active_llm = llm


def get_active_llm() -> BaseLLM:
    """Get the currently active LLM backend."""
    global _active_llm
    return _active_llm


def generate(
    messages: List[Dict[str, str]],
    temperature: float = 0.0,
    max_tokens: int = 1024
) -> LLMResponse:
    """Central entry point for all LLM completions in the RAG pipeline."""
    return _active_llm.generate(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
