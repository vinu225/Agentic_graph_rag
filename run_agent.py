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
from typing import Optional, List

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_pipeline.config import SQLITE_DB_PATH, EVAL_PUBLIC_PATH, DEFAULT_OLLAMA_MODEL, OLLAMA_API_BASE
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import OllamaLLM, MockLLM, set_active_llm


def print_step_trace(step, valid: bool = True):
    """Format and print a single step trace with full details."""
    if step.action_type == "tool_call":
        print(f"\n  [Step {step.step_num}] ACTION: TOOL CALL")
        print(f"    Tool:      {step.tool_name}")
        print(f"    Arguments: {json.dumps(step.tool_input)}")
        print(f"    Valid:     {'YES (parsed successfully)' if valid else 'NO'}")
        out_str = json.dumps(step.tool_output, default=str)
        if len(out_str) > 300:
            out_str = out_str[:300] + f"... [truncated, total {len(out_str)} chars]"
        print(f"    Output:    {out_str}")
        print(f"    Tokens:    {step.tokens} (cumulative step call)")
        print(f"    Latency:   {step.duration_s:.2f}s")
    elif step.action_type == "final_answer":
        print(f"\n  [Step {step.step_num}] ACTION: FINAL ANSWER")
        print(f"    Thought / Answer: {step.thought}")
        print(f"    Tokens:           {step.tokens} (cumulative step call)")
        print(f"    Latency:          {step.duration_s:.2f}s")


def run_single(question: str, gold_answer: Optional[str] = None, qid: Optional[str] = None, qtype: Optional[str] = None, model_name: str = DEFAULT_OLLAMA_MODEL, use_mock: bool = False):
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
    header = f"[{qid}] ({qtype}) " if qid else ""
    print(f"\n{'='*70}\n{header}Question: {question}\nInvestigating...")
    result = orchestrator.run(question)

    print("\n--- AGENTIC EXECUTION TRACE ---")
    evaluate_evidence_used = False
    for step in result.trace:
        if step.action_type == "tool_call" and step.tool_name == "evaluate_evidence":
            evaluate_evidence_used = True
        print_step_trace(step)

    print("\n" + "=" * 70)
    print("--- EXECUTION SUMMARY ---")
    print(f"QUESTION:          {question}")
    print(f"FINAL ANSWER:      {result.answer}")
    if gold_answer is not None:
        print(f"GOLD ANSWER:       {gold_answer}")
    print(f"STOPPED REASON:    {result.stopped_reason}")
    print(f"EVALUATE EVIDENCE: {'Triggered early stop check' if evaluate_evidence_used else 'Not invoked directly; concluded on evidence'}")
    print(f"TOTAL STEPS:       {result.total_steps}")
    print(f"TOTAL TOKENS:      {result.total_tokens} (prompt: {result.prompt_tokens}, completion: {result.completion_tokens})")
    print(f"TOTAL LATENCY:     {result.elapsed_time_s:.2f}s")
    print("=" * 70 + "\n")

    graph.close()
    return result


def run_targeted_eval(target_qids: List[str], model_name: str = DEFAULT_OLLAMA_MODEL):
    """Run specific question IDs from eval_public.jsonl."""
    if not EVAL_PUBLIC_PATH.exists():
        print(f"Error: {EVAL_PUBLIC_PATH} not found.")
        return

    questions_map = {}
    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            questions_map[data.get("qid")] = data

    for qid in target_qids:
        if qid not in questions_map:
            print(f"Warning: {qid} not found in {EVAL_PUBLIC_PATH}")
            continue
        data = questions_map[qid]
        run_single(
            question=data.get("question"),
            gold_answer=data.get("answer"),
            qid=qid,
            qtype=data.get("qtype"),
            model_name=model_name
        )


def run_sample_eval(num_questions: int = 5, model_name: str = DEFAULT_OLLAMA_MODEL):
    """Run first N questions from eval_public.jsonl."""
    if not EVAL_PUBLIC_PATH.exists():
        print(f"Error: {EVAL_PUBLIC_PATH} not found.")
        return

    target_qids = []
    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx >= num_questions:
                break
            data = json.loads(line)
            target_qids.append(data.get("qid"))

    run_targeted_eval(target_qids, model_name=model_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic GraphRAG Runner")
    parser.add_argument("--question", type=str, help="Single question to answer")
    parser.add_argument("--gold", type=str, help="Gold answer for single question")
    parser.add_argument("--eval-sample", type=int, default=0, help="Number of public eval questions to test")
    parser.add_argument("--qids", type=str, help="Comma-separated question IDs to test (e.g. pub-001,pub-002,pub-004)")
    parser.add_argument("--model", type=str, default=DEFAULT_OLLAMA_MODEL, help="Ollama model name")
    parser.add_argument("--mock", action="store_true", help="Use MockLLM instead of Ollama")

    args = parser.parse_args()

    if args.qids:
        qids_list = [q.strip() for q in args.qids.split(",") if q.strip()]
        run_targeted_eval(qids_list, model_name=args.model)
    elif args.eval_sample > 0:
        run_sample_eval(num_questions=args.eval_sample, model_name=args.model)
    elif args.question:
        run_single(args.question, gold_answer=args.gold, model_name=args.model, use_mock=args.mock)
    else:
        sample_q = "According to the provided corpus, how many shooting events at the 2004 Summer Olympics had more than 37 competitors?"
        run_single(sample_q, gold_answer="['8']", model_name=args.model, use_mock=args.mock)
