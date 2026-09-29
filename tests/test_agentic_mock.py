"""Unit tests for Step 3:
Tests AgenticOrchestrator, tool dispatching, trace generation, and token tracking using MockLLM.
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import MockLLM, LLMResponse, ToolCall, set_active_llm


class TestAgenticMock(unittest.TestCase):

    def setUp(self):
        self.test_db = f"test_agent_{os.getpid()}_{id(self)}.db"
        self.graph = SQLiteGraph(self.test_db)

        # Seed sample data into test DB
        self.graph.upsert_event({
            "doc_id": "doc_shoot_1",
            "title": "Shooting at the 2004 Summer Olympics – Men's 10 metre air rifle",
            "sport": "Shooting",
            "games": "2004 Summer",
            "competitors": 47,
            "gold": "Zhu Qinan"
        })
        self.graph.upsert_event({
            "doc_id": "doc_shoot_2",
            "title": "Shooting at the 2004 Summer Olympics – Women's 10 metre air rifle",
            "sport": "Shooting",
            "games": "2004 Summer",
            "competitors": 44,
            "gold": "Du Li"
        })
        self.graph.upsert_event({
            "doc_id": "doc_shoot_3",
            "title": "Shooting at the 2004 Summer Olympics – Men's trap",
            "sport": "Shooting",
            "games": "2004 Summer",
            "competitors": 35,
            "gold": "Alexey Alipov"
        })

        self.tools = ToolSuite(self.graph)
        self.mock_llm = MockLLM()
        set_active_llm(self.mock_llm)

    def tearDown(self):
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except Exception:
                pass

    def test_multi_step_agentic_loop(self):
        """Simulate an agent investigating pub-003:
        Step 1: LLM calls get_events(games='2004 Summer', sport='Shooting')
        Step 2: LLM calls count_or_rank(operation='count', threshold=37, threshold_op='gt')
        Step 3: LLM outputs final answer: 'According to the corpus, 2 shooting events had > 37 competitors.'
        """
        # Script Step 1
        resp_step1 = LLMResponse(
            content="I need to retrieve shooting events at the 2004 Summer Olympics.",
            tool_calls=[
                ToolCall(
                    id="call_1",
                    name="get_events",
                    arguments={"games": "2004 Summer", "sport": "Shooting"}
                )
            ],
            prompt_tokens=100,
            completion_tokens=25,
            total_tokens=125
        )

        # Script Step 2
        resp_step2 = LLMResponse(
            content="Now I will count how many of these events have more than 37 competitors.",
            tool_calls=[
                ToolCall(
                    id="call_2",
                    name="count_or_rank",
                    arguments={"operation": "count", "threshold": 37, "threshold_op": "gt"}
                )
            ],
            prompt_tokens=150,
            completion_tokens=30,
            total_tokens=180
        )

        # Script Step 3 (Final Answer)
        resp_step3 = LLMResponse(
            content="According to the corpus, 2 shooting events had more than 37 competitors.",
            tool_calls=[],
            prompt_tokens=200,
            completion_tokens=20,
            total_tokens=220
        )

        self.mock_llm.queue_response(resp_step1)
        self.mock_llm.queue_response(resp_step2)
        self.mock_llm.queue_response(resp_step3)

        orchestrator = AgenticOrchestrator(self.tools, max_steps=5)
        result = orchestrator.run("How many shooting events at 2004 Summer had more than 37 competitors?")

        # Assertions
        self.assertEqual(result.answer, "According to the corpus, 2 shooting events had more than 37 competitors.")
        self.assertEqual(result.stopped_reason, "evidence_sufficient_answered")
        self.assertEqual(result.total_steps, 3)
        self.assertEqual(len(result.evidence), 2)
        self.assertEqual(result.evidence[1]["output"]["count"], 2)
        self.assertEqual(result.total_tokens, 125 + 180 + 220)
        self.assertTrue(result.elapsed_time_s >= 0.0)

        # Trace assertions
        self.assertEqual(result.trace[0].action_type, "tool_call")
        self.assertEqual(result.trace[0].tool_name, "get_events")
        self.assertEqual(result.trace[1].action_type, "tool_call")
        self.assertEqual(result.trace[1].tool_name, "count_or_rank")
        self.assertEqual(result.trace[2].action_type, "final_answer")


if __name__ == "__main__":
    unittest.main()
