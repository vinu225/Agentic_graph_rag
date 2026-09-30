"""Unified LLM interface for Agentic GraphRAG.
All model interactions pass through generate(messages, tools=None).
Supports:
1. MockLLM: Deterministic tool-calling and response generation for tests and validation.
2. OllamaLLM: Local OpenAI-compatible API at http://localhost:11434/v1 (e.g. qwen3:4b / qwen3:8b)
   with context budgeting and tool-calling format.
"""

import re
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
    """Connects to local Ollama instance with thinking mode suppression.
    Calls native /api/chat with think=False, falling back to /v1/chat/completions if 404.
    Scrubs <think>...</think> from responses and ensures tool calls are parsed from
    actual message content, never from leaked thinking blocks.
    """
    def __init__(
        self,
        model_name: str = DEFAULT_OLLAMA_MODEL,
        api_base: str = OLLAMA_API_BASE,
        token_budget: int = DEFAULT_TOKEN_BUDGET
    ):
        self.model_name = model_name
        self.api_base = api_base.rstrip("/")
        if self.api_base.endswith("/v1"):
            self.native_base = self.api_base[:-3]
        else:
            self.native_base = self.api_base
        self.native_endpoint = f"{self.native_base}/api/chat"
        self.v1_endpoint = f"{self.api_base}/chat/completions" if self.api_base.endswith("/v1") else f"{self.api_base}/v1/chat/completions"
        self.token_budget = token_budget

    def _parse_tool_calls(
        self,
        raw_tools: List[Dict[str, Any]],
        scrubbed_content: str
    ) -> List[ToolCall]:
        tool_calls: List[ToolCall] = []

        if raw_tools:
            for idx, t in enumerate(raw_tools):
                func = t.get("function", {})
                fn_name = func.get("name", "")
                fn_args_raw = func.get("arguments", {})
                if isinstance(fn_args_raw, str):
                    try:
                        fn_args = json.loads(fn_args_raw)
                    except Exception:
                        fn_args = {"raw": fn_args_raw}
                elif isinstance(fn_args_raw, dict):
                    fn_args = fn_args_raw
                else:
                    fn_args = {}

                tool_calls.append(
                    ToolCall(
                        id=t.get("id", f"call_{idx}"),
                        name=fn_name,
                        arguments=fn_args
                    )
                )
            return tool_calls

        # Fallback: Parse tool calls from actual message content
        # Note: scrubbed_content has ALREADY been stripped of any <think>...</think> blocks.
        if not scrubbed_content:
            return []

        # Check for <tool_call> tags
        tc_matches = re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", scrubbed_content, flags=re.DOTALL)
        for idx, tc_text in enumerate(tc_matches):
            try:
                tc_json = json.loads(tc_text)
                name = tc_json.get("name") or tc_json.get("function", {}).get("name")
                args = tc_json.get("arguments") or tc_json.get("function", {}).get("arguments", {})
                if name:
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"raw": args}
                    tool_calls.append(ToolCall(id=f"call_content_{idx}", name=name, arguments=args))
            except Exception:
                pass

        if tool_calls:
            return tool_calls

        # Check for ```json ... ``` blocks containing "name" and "arguments"
        code_blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", scrubbed_content, flags=re.DOTALL)
        for idx, block in enumerate(code_blocks):
            try:
                tc_json = json.loads(block)
                if "name" in tc_json and ("arguments" in tc_json or "parameters" in tc_json):
                    name = tc_json["name"]
                    args = tc_json.get("arguments", tc_json.get("parameters", {}))
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"raw": args}
                    tool_calls.append(ToolCall(id=f"call_block_{idx}", name=name, arguments=args))
            except Exception:
                pass

        return tool_calls

    def _clean_content_after_tool_extraction(self, content: str) -> str:
        cleaned = re.sub(r"<tool_call>.*?</tool_call>", "", content, flags=re.DOTALL)
        cleaned = re.sub(r'```(?:json)?\s*\{.*?"name".*?\}\s*```', "", cleaned, flags=re.DOTALL)
        return cleaned.strip()

    def _format_messages_for_native(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted = []
        for msg in messages:
            m = dict(msg)
            if "tool_calls" in m and m["tool_calls"]:
                tcs = []
                for tc in m["tool_calls"]:
                    tc_copy = dict(tc)
                    if "function" in tc_copy:
                        fn = dict(tc_copy["function"])
                        if isinstance(fn.get("arguments"), str):
                            try:
                                fn["arguments"] = json.loads(fn["arguments"])
                            except Exception:
                                pass
                        tc_copy["function"] = fn
                    tcs.append(tc_copy)
                m["tool_calls"] = tcs
            formatted.append(m)
        return formatted

    def _format_messages_for_v1(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted = []
        for msg in messages:
            m = dict(msg)
            if "tool_calls" in m and m["tool_calls"]:
                tcs = []
                for tc in m["tool_calls"]:
                    tc_copy = dict(tc)
                    if "function" in tc_copy:
                        fn = dict(tc_copy["function"])
                        if isinstance(fn.get("arguments"), dict):
                            fn["arguments"] = json.dumps(fn["arguments"])
                        tc_copy["function"] = fn
                    tcs.append(tc_copy)
                m["tool_calls"] = tcs
            formatted.append(m)
        return formatted

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        # 1. First attempt: native Ollama /api/chat with think=False explicitly
        native_messages = self._format_messages_for_native(messages)
        native_payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": native_messages,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": self.token_budget,
            }
        }
        if tools:
            native_payload["tools"] = tools

        native_req = urllib.request.Request(
            self.native_endpoint,
            data=json.dumps(native_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(native_req, timeout=120) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))

            msg = res_data.get("message", {})
            content = msg.get("content", "") or ""
            # Strip any leaked <think> blocks as a safety net BEFORE any tool parsing
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            content = re.sub(r"<think>.*", "", content, flags=re.DOTALL).strip()

            raw_tools = msg.get("tool_calls") or []
            tool_calls = self._parse_tool_calls(raw_tools, content)
            if not raw_tools and tool_calls:
                content = self._clean_content_after_tool_extraction(content)

            prompt_tokens = res_data.get("prompt_eval_count", 0)
            completion_tokens = res_data.get("eval_count", 0)
            total_tokens = prompt_tokens + completion_tokens

            return LLMResponse(
                content=content if content else None,
                tool_calls=tool_calls,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                raw_response=res_data
            )
        except urllib.error.HTTPError as he:
            # Fallback to OpenAI-compatible endpoint if native /api/chat returns 404
            if he.code != 404:
                logger.error(f"Ollama native endpoint HTTP error {he.code}: {he}")
                raise
        except urllib.error.URLError as ue:
            logger.error(f"Failed to connect to Ollama at {self.native_endpoint}: {ue}")
            raise ConnectionError(
                f"Could not connect to Ollama at {self.native_endpoint}. "
                f"Ensure Ollama is running (`ollama serve`). Details: {ue}"
            )

        # 2. Fallback attempt: OpenAI-compatible /v1/chat/completions endpoint
        v1_messages = self._format_messages_for_v1(messages)
        v1_payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": v1_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "options": {
                "num_ctx": self.token_budget,
                "temperature": temperature,
            }
        }
        if tools:
            v1_payload["tools"] = tools
            v1_payload["tool_choice"] = "auto"

        v1_req = urllib.request.Request(
            self.v1_endpoint,
            data=json.dumps(v1_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(v1_req, timeout=120) as response:
                res_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to Ollama at {self.v1_endpoint}: {e}")
            raise ConnectionError(
                f"Could not connect to Ollama at {self.v1_endpoint}. "
                f"Ensure Ollama is running (`ollama serve`). Error: {e}"
            )

        choice = res_data.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = res_data.get("usage", {})

        content = message.get("content") or ""
        # Strip any leaked <think> blocks BEFORE tool parsing
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        content = re.sub(r"<think>.*", "", content, flags=re.DOTALL).strip()

        raw_tools = message.get("tool_calls") or []
        tool_calls = self._parse_tool_calls(raw_tools, content)
        if not raw_tools and tool_calls:
            content = self._clean_content_after_tool_extraction(content)

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        return LLMResponse(
            content=content if content else None,
            tool_calls=tool_calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
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
