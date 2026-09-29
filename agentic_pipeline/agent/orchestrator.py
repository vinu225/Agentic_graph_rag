"""Orchestrator and agent loop for Agentic GraphRAG.
Implements autonomous planning, tool execution, evidence accumulation, trace logging, and stopping logic.
"""

import time
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_pipeline.config import DEFAULT_MAX_AGENT_STEPS, DEFAULT_TOKEN_BUDGET
from agentic_pipeline.llm_interface import generate, LLMResponse, ToolCall
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class TraceStep:
    step_num: int
    action_type: str  # 'thought', 'tool_call', 'observation', 'final_answer'
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    thought: Optional[str] = None
    tokens: int = 0
    duration_s: float = 0.0


@dataclass
class AgentResult:
    question: str
    answer: str
    evidence: List[Dict[str, Any]]
    trace: List[TraceStep]
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    total_steps: int
    elapsed_time_s: float
    stopped_reason: str


class AgenticOrchestrator:
    """Manages autonomous investigation loop over the tool suite."""

    def __init__(
        self,
        tool_suite: ToolSuite,
        max_steps: int = DEFAULT_MAX_AGENT_STEPS,
        token_budget: int = DEFAULT_TOKEN_BUDGET
    ):
        self.tool_suite = tool_suite
        self.max_steps = max_steps
        self.token_budget = token_budget

    def dispatch_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        active_events: List[Dict[str, Any]],
        collected_evidence: List[Dict[str, Any]]
    ) -> Any:
        """Execute tool call against ToolSuite."""
        if tool_name == "link_entities":
            return self.tool_suite.link_entities(**tool_args)

        elif tool_name == "get_events":
            events = self.tool_suite.get_events(**tool_args)
            active_events.clear()
            active_events.extend(events)
            return {"returned_count": len(events), "events_preview": events[:5]}

        elif tool_name == "get_event_attributes":
            return self.tool_suite.get_event_attributes(**tool_args)

        elif tool_name == "count_or_rank":
            # Passes current active_events into count_or_rank
            metric = tool_args.get("metric", "competitors")
            operation = tool_args.get("operation", "count")
            threshold = tool_args.get("threshold")
            threshold_op = tool_args.get("threshold_op", "gt")
            limit = tool_args.get("limit", 1)

            res = self.tool_suite.count_or_rank(
                events=active_events,
                metric=metric,
                operation=operation,
                threshold=threshold,
                threshold_op=threshold_op,
                limit=limit
            )
            return res

        elif tool_name == "retrieve_chunks":
            return self.tool_suite.retrieve_chunks(**tool_args)

        elif tool_name == "evaluate_evidence":
            return self.tool_suite.evaluate_evidence(
                question=tool_args.get("question", ""),
                evidence=collected_evidence
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def run(self, question: str) -> AgentResult:
        """Run the autonomous investigation loop."""
        start_time = time.time()
        trace: List[TraceStep] = []
        collected_evidence: List[Dict[str, Any]] = []
        active_events: List[Dict[str, Any]] = []

        total_prompt_tokens = 0
        total_completion_tokens = 0

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        tool_schemas = self.tool_suite.get_tool_schemas()
        stopped_reason = "max_steps_reached"
        final_answer = ""

        for step_idx in range(1, self.max_steps + 1):
            step_start = time.time()

            # Check token budget
            total_current_tokens = total_prompt_tokens + total_completion_tokens
            if total_current_tokens >= self.token_budget:
                stopped_reason = "token_budget_exceeded"
                break

            # 1. Call LLM
            llm_resp: LLMResponse = generate(
                messages=messages,
                tools=tool_schemas,
                temperature=0.0
            )

            total_prompt_tokens += llm_resp.prompt_tokens
            total_completion_tokens += llm_resp.completion_tokens
            step_duration = time.time() - step_start

            # 2. Check if final answer generated (no more tool calls)
            if not llm_resp.tool_calls:
                final_answer = llm_resp.content or "No answer could be determined from the evidence."
                trace.append(TraceStep(
                    step_num=step_idx,
                    action_type="final_answer",
                    thought=final_answer,
                    tokens=llm_resp.total_tokens,
                    duration_s=step_duration
                ))
                stopped_reason = "evidence_sufficient_answered"
                break

            # 3. Process tool calls
            for tool_call in llm_resp.tool_calls:
                call_start = time.time()
                tool_output = self.dispatch_tool(
                    tool_name=tool_call.name,
                    tool_args=tool_call.arguments,
                    active_events=active_events,
                    collected_evidence=collected_evidence
                )
                call_duration = time.time() - call_start

                # Record evidence
                collected_evidence.append({
                    "step": step_idx,
                    "tool": tool_call.name,
                    "args": tool_call.arguments,
                    "output": tool_output
                })

                trace.append(TraceStep(
                    step_num=step_idx,
                    action_type="tool_call",
                    tool_name=tool_call.name,
                    tool_input=tool_call.arguments,
                    tool_output=tool_output,
                    tokens=llm_resp.total_tokens,
                    duration_s=call_duration
                ))

                # Update conversation history with assistant tool call and tool result
                messages.append({
                    "role": "assistant",
                    "content": llm_resp.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.name,
                                "arguments": json.dumps(tool_call.arguments)
                            }
                        }
                    ]
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_output)
                })

        total_elapsed = time.time() - start_time
        total_tokens = total_prompt_tokens + total_completion_tokens

        return AgentResult(
            question=question,
            answer=final_answer,
            evidence=collected_evidence,
            trace=trace,
            total_tokens=total_tokens,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            total_steps=len(trace),
            elapsed_time_s=total_elapsed,
            stopped_reason=stopped_reason
        )
