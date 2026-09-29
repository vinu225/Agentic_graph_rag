"""Runner script for Agentic GraphRAG.
Supports:
- Single query execution from command line
- Connecting to local Ollama (qwen3:4b / qwen3:8b) or MockLLM
- Running on 5 to 10 sample public evaluation questions
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_pipeline.config import SQLITE_DB_PATH, EVAL_PUBLIC_PATH, DEFAULT_OLLAMA_MODEL, OLLAMA_API_BASE
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import OllamaLLM, MockLLM, set_active_llm


def run_single(question: str, model_name: str = DEFAULT_OLLAMA_MODEL, use_mock: bool = False):
    """Run agent on a single question and display complete trace."""
    graph = SQLiteGraph(str(SQLITE_DB_PATH))
    tool_suite = ToolSuite(graph)

    if use_mock:
        print("[Mode] Using MockLLM")
        set_active_llm(MockLLM())
    else:
        print(f"[Mode] Connecting to Ollama at {OLLAMA_API_BASE} with model '{model_name}'...")
        set_active_llm(OllamaLLM(model_name=model_name))

    orchestrator = AgenticOrchestrator(tool_suite)
    print(f"\nQuestion: {question}\nInvestigating...")
    result = orchestrator.run(question)

    print("\n" + "=" * 60)
    print(f"FINAL ANSWER: {result.answer}")
    print(f"STOPPED REASON: {result.stopped_reason}")
    print(f"TOTAL TOKENS: {result.total_tokens} (prompt: {result.prompt_tokens}, completion: {result.completion_tokens})")
    print(f"STEPS COUNT: {result.total_steps}")
    print(f"ELAPSED TIME: {result.elapsed_time_s:.2f}s")
    print("=" * 60)

    print("\n--- AGENTIC EXECUTION TRACE ---")
    for step in result.trace:
        if step.action_type == "tool_call":
            print(f"[Step {step.step_num}] TOOL CALL: {step.tool_name}({step.tool_input}) -> {step.tool_output}")
        elif step.action_type == "final_answer":
            print(f"[Step {step.step_num}] FINAL ANSWER: {step.thought}")

    graph.close()


def run_sample_eval(num_questions: int = 5, model_name: str = DEFAULT_OLLAMA_MODEL):
    """Run first N questions from eval_public.jsonl."""
    if not EVAL_PUBLIC_PATH.exists():
        print(f"Error: {EVAL_PUBLIC_PATH} not found.")
        return

    graph = SQLiteGraph(str(SQLITE_DB_PATH))
    tool_suite = ToolSuite(graph)
    set_active_llm(OllamaLLM(model_name=model_name))
    orchestrator = AgenticOrchestrator(tool_suite)

    print(f"\n=== Running Sample Evaluation on First {num_questions} Public Questions ===")
    print(f"Model: {model_name}\n")

    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx >= num_questions:
                break
            data = json.loads(line)
            qid = data.get("qid")
            q = data.get("question")
            gold_answer = data.get("answer")
            qtype = data.get("qtype")

            print(f"\n[{qid}] ({qtype}) {q}")
            print(f"  Gold Answer: {gold_answer}")
            try:
                res = orchestrator.run(q)
                print(f"  Agent Answer: {res.answer}")
                print(f"  Tokens: {res.total_tokens} | Steps: {res.total_steps} | Time: {res.elapsed_time_s:.2f}s | Reason: {res.stopped_reason}")
            except Exception as e:
                print(f"  Execution Error: {e}")

    graph.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic GraphRAG Runner")
    parser.add_argument("--question", type=str, help="Single question to answer")
    parser.add_argument("--eval-sample", type=int, default=0, help="Number of public eval questions to test (e.g. 5)")
    parser.add_argument("--model", type=str, default=DEFAULT_OLLAMA_MODEL, help="Ollama model name")
    parser.add_argument("--mock", action="store_true", help="Use MockLLM instead of Ollama")

    args = parser.parse_args()

    if args.eval_sample > 0:
        run_sample_eval(num_questions=args.eval_sample, model_name=args.model)
    elif args.question:
        run_single(args.question, model_name=args.model, use_mock=args.mock)
    else:
        # Default run single sample question
        sample_q = "According to the provided corpus, how many shooting events at the 2004 Summer Olympics had more than 37 competitors?"
        run_single(sample_q, model_name=args.model, use_mock=args.mock)
