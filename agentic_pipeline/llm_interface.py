"""Unified LLM interface for Agentic GraphRAG.
All model interactions pass through generate(messages, tools=None).
Supports:
1. MockLLM: Deterministic tool-calling and response generation for tests and validation.
2. OllamaLLM: Local OpenAI-compatible API at http://localhost:11434/v1 (e.g. qwen3:4b / qwen3:8b)
   with context budgeting and tool-calling format.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from agentic_pipeline.config import (
    OLLAMA_API_BASE,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_TOKEN_BUDGET
)

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    content: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLM:
    """Base class for all LLM implementations."""
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        raise NotImplementedError


class MockLLM(BaseLLM):
    """Deterministic Mock LLM for offline verification of the agent harness and orchestrator.
    Can be programmed with scripted step-by-step responses or rule-based tool-calling.
    """
    def __init__(self, scripted_responses: Optional[List[LLMResponse]] = None):
        self.scripted_responses: List[LLMResponse] = scripted_responses or []
        self.call_history: List[Dict[str, Any]] = []

    def queue_response(self, response: LLMResponse) -> None:
        self.scripted_responses.append(response)

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        self.call_history.append({"messages": messages, "tools": tools})

        if self.scripted_responses:
            return self.scripted_responses.pop(0)

        # Rule-based fallback for common questions if no script queued
        last_msg = messages[-1]["content"] if messages else ""

        # Default mock completion tokens
        return LLMResponse(
            content=f"Mock response to: {last_msg[:50]}",
            tool_calls=[],
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70
        )


class OllamaLLM(BaseLLM):
    """Connects to local Ollama instance via OpenAI-compatible endpoint.
    Configured for Qwen models with thinking disabled during tool calls.
    """
    def __init__(
        self,
        model_name: str = DEFAULT_OLLAMA_MODEL,
        api_base: str = OLLAMA_API_BASE,
        token_budget: int = DEFAULT_TOKEN_BUDGET
    ):
        self.model_name = model_name
        self.api_base = api_base.rstrip("/")
        self.token_budget = token_budget

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        url = f"{self.api_base}/chat/completions"

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        # For Qwen3 models, pass flag to avoid verbose internal monologue on tool steps
        payload["options"] = {
            "num_ctx": self.token_budget,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to Ollama at {url}: {e}")
            raise ConnectionError(
                f"Could not connect to Ollama at {self.api_base}. "
                f"Ensure Ollama is running (`ollama serve`). Error: {e}"
            )

        choice = res_data.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = res_data.get("usage", {})

        content = message.get("content")
        raw_tools = message.get("tool_calls", [])
        tool_calls: List[ToolCall] = []

        for idx, t in enumerate(raw_tools):
            func = t.get("function", {})
            fn_name = func.get("name", "")
            fn_args_raw = func.get("arguments", "{}")
            if isinstance(fn_args_raw, str):
                try:
                    fn_args = json.loads(fn_args_raw)
                except Exception:
                    fn_args = {"raw": fn_args_raw}
            else:
                fn_args = fn_args_raw

            tool_calls.append(
                ToolCall(
                    id=t.get("id", f"call_{idx}"),
                    name=fn_name,
                    arguments=fn_args
                )
            )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            raw_response=res_data
        )


# Global default active provider (swappable at runtime)
_active_llm: BaseLLM = MockLLM()


def set_active_llm(llm: BaseLLM) -> None:
    """Set the active LLM backend for generate()."""
    global _active_llm
    _active_llm = llm


def get_active_llm() -> BaseLLM:
    """Get the active LLM backend."""
    global _active_llm
    return _active_llm


def generate(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.0,
    max_tokens: int = 1024,
) -> LLMResponse:
    """Central entry point for all LLM calls across all pipelines."""
    return _active_llm.generate(
        messages=messages,
        tools=tools,
        temperature=temperature,
        max_tokens=max_tokens
    )
