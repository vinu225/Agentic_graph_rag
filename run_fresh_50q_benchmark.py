"""Full 50-Question Hidden Benchmark Runner (Fresh Optimized Execution).

Executes all 3 pipelines sequentially across all 50 hidden evaluation questions
(drive-download-20260928T175718Z-1-001/questions/eval_hidden.jsonl):
  1. Plain RAG -> results/results_rag_hidden50.jsonl
  2. GraphRAG -> results/results_graphrag_hidden50.jsonl
  3. Optimized Agentic GraphRAG -> results/results_agent_hidden50.jsonl

Outputs:
  - results/results_rag_hidden50.jsonl
  - results/results_graphrag_hidden50.jsonl
  - results/results_agent_hidden50.jsonl
  - results/summary_hidden50.md
  - optimized_comparison_50_hidden.json
  - optimized_comparison_50_hidden.md

Streams results incrementally with progress logging every 10 questions.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

# Configuration and Database
from agentic_pipeline.config import SQLITE_DB_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator

# LLM bindings
from rag_only_pipeline.llm.llm_client import OllamaLLM as RagOllamaLLM, set_active_llm as set_rag_active_llm
from rag_only_pipeline.pipeline import RAGPipeline

from agentic_pipeline.llm_interface import OllamaLLM as AgenticOllamaLLM, set_active_llm as set_agentic_active_llm
from graphrag_pipeline.pipeline import GraphRAGPipeline

EVAL_HIDDEN_PATH = WORKSPACE_ROOT / "drive-download-20260928T175718Z-1-001" / "questions" / "eval_hidden.jsonl"
RESULTS_DIR = WORKSPACE_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RAG_OUTPUT = RESULTS_DIR / "results_rag_hidden50.jsonl"
GRAPHRAG_OUTPUT = RESULTS_DIR / "results_graphrag_hidden50.jsonl"
AGENT_OUTPUT = RESULTS_DIR / "results_agent_hidden50.jsonl"
SUMMARY_OUTPUT = RESULTS_DIR / "summary_hidden50.md"

COMP_50_JSON = WORKSPACE_ROOT / "optimized_comparison_50_hidden.json"
COMP_50_MD = WORKSPACE_ROOT / "optimized_comparison_50_hidden.md"


def load_hidden_questions() -> List[Dict[str, Any]]:
    """Load the 50 hidden evaluation questions."""
    if not EVAL_HIDDEN_PATH.exists():
        raise FileNotFoundError(f"Hidden evaluation file not found at: {EVAL_HIDDEN_PATH}")
    questions = []
    with open(EVAL_HIDDEN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def load_existing(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Load completed questions from a JSONL output file for resumption."""
    records = {}
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        qid = data.get("question_id") or data.get("qid")
                        if qid:
                            records[qid] = data
                    except Exception:
                        pass
    return records


def run_rag_hidden50(questions: List[Dict[str, Any]]) -> None:
    """Execute Plain RAG pipeline across the 50 hidden questions."""
    print("\n" + "=" * 80)
    print("STEP 1: PLAIN RAG PIPELINE (50 Hidden Questions)")
    print("=" * 80)

    rag_llm = RagOllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_rag_active_llm(rag_llm)

    existing = load_existing(RAG_OUTPUT)
    missing = [q for q in questions if q["qid"] not in existing]
    print(f"Total: {len(questions)} | Already completed: {len(existing)} | To run: {len(missing)}")

    if not missing:
        print("[RAG] All questions already completed. Skipping.")
        return

    pipe = RAGPipeline()
    t_start = time.time()

    with open(RAG_OUTPUT, "a", encoding="utf-8") as f_out:
        for idx, item in enumerate(missing, 1):
            qid = item["qid"]
            qtext = item["question"]
            t0 = time.time()
            try:
                res = pipe.run(question=qtext, question_id=qid)
                row = res.to_dict()
            except Exception as e:
                print(f"  [RAG Error] {qid}: {e}")
                row = {
                    "question_id": qid,
                    "answer": f"Error: {e}",
                    "citations": [],
                    "context_tokens": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "elapsed_time_s": round(time.time() - t0, 3)
                }

            f_out.write(json.dumps(row, ensure_ascii=False) + "\n")
            f_out.flush()
            existing[qid] = row

            total_done = len(existing)
            if total_done % 10 == 0 or total_done == len(questions):
                print(f"  [RAG Progress] {total_done}/{len(questions)} completed ({row['elapsed_time_s']}s, {row['total_tokens']} tokens on {qid})")

    elapsed_total = time.time() - t_start
    print(f"[RAG] Completed in {elapsed_total:.2f}s.")


def run_graphrag_hidden50(questions: List[Dict[str, Any]], shared_llm: AgenticOllamaLLM) -> None:
    """Execute GraphRAG pipeline across the 50 hidden questions."""
    print("\n" + "=" * 80)
    print("STEP 2: GRAPHRAG PIPELINE (50 Hidden Questions)")
    print("=" * 80)

    existing = load_existing(GRAPHRAG_OUTPUT)
    missing = [q for q in questions if q["qid"] not in existing]
    print(f"Total: {len(questions)} | Already completed: {len(existing)} | To run: {len(missing)}")

    if not missing:
        print("[GraphRAG] All questions already completed. Skipping.")
        return

    pipe = GraphRAGPipeline(model_name=DEFAULT_OLLAMA_MODEL, llm=shared_llm)
    t_start = time.time()

    with open(GRAPHRAG_OUTPUT, "a", encoding="utf-8") as f_out:
        for idx, item in enumerate(missing, 1):
            qid = item["qid"]
            qtext = item["question"]
            t0 = time.time()
            try:
                res = pipe.run(qtext, question_id=qid)
                row = res.to_dict()
            except Exception as e:
                print(f"  [GraphRAG Error] {qid}: {e}")
                row = {
                    "question_id": qid,
                    "answer": f"Error: {e}",
                    "citations": [],
                    "context_tokens": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "elapsed_time_s": round(time.time() - t0, 3)
                }

            f_out.write(json.dumps(row, ensure_ascii=False) + "\n")
            f_out.flush()
            existing[qid] = row

            total_done = len(existing)
            if total_done % 10 == 0 or total_done == len(questions):
                print(f"  [GraphRAG Progress] {total_done}/{len(questions)} completed ({row['elapsed_time_s']}s, {row['total_tokens']} tokens on {qid})")

    pipe.close()
    elapsed_total = time.time() - t_start
    print(f"[GraphRAG] Completed in {elapsed_total:.2f}s.")


def run_agent_hidden50(questions: List[Dict[str, Any]], shared_llm: AgenticOllamaLLM) -> None:
    """Execute Agentic GraphRAG pipeline across the 50 hidden questions with full trace."""
    print("\n" + "=" * 80)
    print("STEP 3: AGENTIC GRAPHRAG PIPELINE (50 Hidden Questions with Full Trace)")
    print("=" * 80)

    existing = load_existing(AGENT_OUTPUT)
    missing = [q for q in questions if q["qid"] not in existing]
    print(f"Total: {len(questions)} | Already completed: {len(existing)} | To run: {len(missing)}")

    if not missing:
        print("[Agentic GraphRAG] All questions already completed. Skipping.")
        return

    graph = SQLiteGraph(str(SQLITE_DB_PATH))
    tools = ToolSuite(graph)
    orchestrator = AgenticOrchestrator(tools)
    t_start = time.time()

    with open(AGENT_OUTPUT, "a", encoding="utf-8") as f_out:
        for idx, item in enumerate(missing, 1):
            qid = item["qid"]
            qtext = item["question"]
            t0 = time.time()
            try:
                res = orchestrator.run(qtext)
                trace_summary = [
                    {
                        "step": st.step_num,
                        "action": st.action_type,
                        "tool": st.tool_name,
                        "args": st.tool_input,
                        "duration_s": round(st.duration_s, 2),
                        "tokens": st.tokens
                    }
                    for st in res.trace
                ]
                row = {
                    "question_id": qid,
                    "answer": res.answer,
                    "citations": res.citations if hasattr(res, "citations") else [],
                    "total_tokens": res.total_tokens,
                    "prompt_tokens": res.prompt_tokens,
                    "completion_tokens": res.completion_tokens,
                    "total_steps": res.total_steps,
                    "elapsed_time_s": round(res.elapsed_time_s, 3),
                    "stopped_reason": res.stopped_reason,
                    "trace": trace_summary
                }
            except Exception as e:
                print(f"  [Agent Error] {qid}: {e}")
                row = {
                    "question_id": qid,
                    "answer": f"Error: {e}",
                    "citations": [],
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_steps": 0,
                    "elapsed_time_s": round(time.time() - t0, 3),
                    "stopped_reason": f"error: {e}",
                    "trace": []
                }

            f_out.write(json.dumps(row, ensure_ascii=False) + "\n")
            f_out.flush()
            existing[qid] = row

            total_done = len(existing)
            if total_done % 10 == 0 or total_done == len(questions):
                print(f"  [Agent Progress] {total_done}/{len(questions)} completed ({row['elapsed_time_s']}s, {row['total_steps']} steps, {row['total_tokens']} tokens on {qid})")

    graph.close()
    elapsed_total = time.time() - t_start
    print(f"[Agentic GraphRAG] Completed in {elapsed_total:.2f}s.")


def audit_and_build_reports(questions: List[Dict[str, Any]]) -> None:
    """Build summary report and full question-by-question comparison file for the 50 hidden questions."""
    print("\n" + "=" * 80)
    print("STEP 4: COMPILING 50-QUESTION COMPARISON REPORTS")
    print("=" * 80)

    rag_records = load_existing(RAG_OUTPUT)
    graphrag_records = load_existing(GRAPHRAG_OUTPUT)
    agent_records = load_existing(AGENT_OUTPUT)

    total_q = len(questions)
    type_stats = defaultdict(lambda: {
        "total": 0,
        "rag_tokens": 0, "gr_tokens": 0, "ag_tokens": 0,
        "rag_lat": 0.0, "gr_lat": 0.0, "ag_lat": 0.0,
        "ag_steps": 0
    })

    total_rag_tokens = 0
    total_gr_tokens = 0
    total_ag_tokens = 0

    total_rag_lat = 0.0
    total_gr_lat = 0.0
    total_ag_lat = 0.0

    ag_steps_sum = 0
    comparison_rows = []

    for q in questions:
        qid = q["qid"]
        qtype = q.get("qtype", "unknown")
        qtext = q["question"]

        r_rec = rag_records.get(qid, {})
        g_rec = graphrag_records.get(qid, {})
        a_rec = agent_records.get(qid, {})

        rag_ans = r_rec.get("answer", "")
        gr_ans = g_rec.get("answer", "")
        ag_ans = a_rec.get("answer", "")

        rag_tok = r_rec.get("total_tokens", 0)
        gr_tok = g_rec.get("total_tokens", 0)
        ag_tok = a_rec.get("total_tokens", 0)

        rag_time = r_rec.get("elapsed_time_s", 0.0)
        gr_time = g_rec.get("elapsed_time_s", 0.0)
        ag_time = a_rec.get("elapsed_time_s", 0.0)

        ag_steps = a_rec.get("total_steps", 0)

        total_rag_tokens += rag_tok
        total_gr_tokens += gr_tok
        total_ag_tokens += ag_tok

        total_rag_lat += rag_time
        total_gr_lat += gr_time
        total_ag_lat += ag_time
        ag_steps_sum += ag_steps

        type_stats[qtype]["total"] += 1
        type_stats[qtype]["rag_tokens"] += rag_tok
        type_stats[qtype]["gr_tokens"] += gr_tok
        type_stats[qtype]["ag_tokens"] += ag_tok

        type_stats[qtype]["rag_lat"] += rag_time
        type_stats[qtype]["gr_lat"] += gr_time
        type_stats[qtype]["ag_lat"] += ag_time
        type_stats[qtype]["ag_steps"] += ag_steps

        comparison_rows.append({
            "question_id": qid,
            "query_type": qtype,
            "question": qtext,
            "rag": {"answer": rag_ans, "tokens": rag_tok, "elapsed_time_s": rag_time},
            "graphrag": {"answer": gr_ans, "tokens": gr_tok, "elapsed_time_s": gr_time},
            "agent": {
                "answer": ag_ans,
                "tokens": ag_tok,
                "elapsed_time_s": ag_time,
                "total_steps": ag_steps,
                "stopped_reason": a_rec.get("stopped_reason", "unknown"),
                "trace": a_rec.get("trace", [])
            }
        })

    # Summary object
    summary_obj = {
        "benchmark_scale": f"{total_q} hidden questions",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_questions": total_q,
        "tokens": {
            "rag_total": total_rag_tokens,
            "graphrag_total": total_gr_tokens,
            "agent_total": total_ag_tokens,
            "rag_avg": round(total_rag_tokens / total_q),
            "graphrag_avg": round(total_gr_tokens / total_q),
            "agent_avg": round(total_ag_tokens / total_q)
        },
        "latency": {
            "rag_wall_clock_s": round(total_rag_lat, 2),
            "graphrag_wall_clock_s": round(total_gr_lat, 2),
            "agent_wall_clock_s": round(total_ag_lat, 2),
            "rag_avg_s": round(total_rag_lat / total_q, 2),
            "graphrag_avg_s": round(total_gr_lat / total_q, 2),
            "agent_avg_s": round(total_ag_lat / total_q, 2)
        },
        "agent_steps": {
            "total_steps": ag_steps_sum,
            "avg_steps": round(ag_steps_sum / total_q, 2)
        }
    }

    full_export = {
        "summary": summary_obj,
        "type_breakdown": {
            qtype: {
                "total": stats["total"],
                "tokens_avg": {
                    "rag": round(stats["rag_tokens"] / stats["total"]),
                    "graphrag": round(stats["gr_tokens"] / stats["total"]),
                    "agent": round(stats["ag_tokens"] / stats["total"])
                },
                "latency_avg_s": {
                    "rag": round(stats["rag_lat"] / stats["total"], 2),
                    "graphrag": round(stats["gr_lat"] / stats["total"], 2),
                    "agent": round(stats["ag_lat"] / stats["total"], 2)
                },
                "agent_avg_steps": round(stats["ag_steps"] / stats["total"], 2)
            }
            for qtype, stats in sorted(type_stats.items())
        },
        "questions": comparison_rows
    }

    # Save optimized_comparison_50_hidden.json
    with open(COMP_50_JSON, "w", encoding="utf-8") as fj:
        json.dump(full_export, fj, indent=2, ensure_ascii=False)
    print(f"[Saved] {COMP_50_JSON}")

    # Build Markdown Comparison Report
    md_lines = [
        "# 3-Pipeline Comparative Benchmark Report (50 Hidden Questions - Submission Deliverable)\n",
        "This report documents the fresh evaluation across all 50 hidden questions from `eval_hidden.jsonl`.",
        "It benchmarks **Pipeline 1 (Plain RAG)**, **Pipeline 2 (GraphRAG)**, and **Pipeline 3 (Optimized Agentic GraphRAG)**.",
        "> **Note on Ground Truth**: Ground truth answers for these 50 hidden questions are held out by TigerGraph for official grading.\n",
        "---\n",
        "## 1. Summary Results (50 Hidden Questions)\n",
        "| Pipeline | Questions Answered | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        f"| **Pipeline 1: Plain RAG** | **{len(rag_records)} / {total_q}** | {summary_obj['tokens']['rag_avg']} | {total_rag_tokens:,} | {summary_obj['latency']['rag_avg_s']:.2f}s | {total_rag_lat/60:.1f}m ({total_rag_lat:.1f}s) | N/A (1 step) |",
        f"| **Pipeline 2: GraphRAG** | **{len(graphrag_records)} / {total_q}** | {summary_obj['tokens']['graphrag_avg']} | {total_gr_tokens:,} | {summary_obj['latency']['graphrag_avg_s']:.2f}s | {total_gr_lat/60:.1f}m ({total_gr_lat:.1f}s) | N/A (1 step) |",
        f"| **Pipeline 3: Optimized Agent** | **{len(agent_records)} / {total_q}** | **{summary_obj['tokens']['agent_avg']}** | **{total_ag_tokens:,}** | **{summary_obj['latency']['agent_avg_s']:.2f}s** | **{total_ag_lat/60:.1f}m ({total_ag_lat:.1f}s)** | **{summary_obj['agent_steps']['avg_steps']:.2f} steps** |\n",
        "---\n",
        "## 2. Resource Consumption by Query Type\n",
        "| Query Type | Questions | Plain RAG Avg Tokens | GraphRAG Avg Tokens | Optimized Agent Avg Tokens | Agent Avg Latency | Agent Avg Steps |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    for qtype, s in full_export["type_breakdown"].items():
        md_lines.append(
            f"| **{qtype}** | {s['total']} | {s['tokens_avg']['rag']} | {s['tokens_avg']['graphrag']} | **{s['tokens_avg']['agent']}** | {s['latency_avg_s']['agent']:.2f}s | {s['agent_avg_steps']:.2f} |"
        )

    md_lines.extend([
        "\n---\n",
        "## 3. Question-by-Question Detailed Results (All 50 Hidden Questions)\n",
        "| ID | Type | Plain RAG Answer | GraphRAG Answer | Agentic GraphRAG Answer | RAG Tok | GR Tok | Agent Tok | Agent Steps |",
        "| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |"
    ])

    for row in comparison_rows:
        qid = row["question_id"]
        qtype = row["query_type"]
        r_ans = str(row["rag"]["answer"]).replace("\n", " ").strip()
        g_ans = str(row["graphrag"]["answer"]).replace("\n", " ").strip()
        a_ans = str(row["agent"]["answer"]).replace("\n", " ").strip()

        if len(r_ans) > 40: r_ans = r_ans[:37] + "..."
        if len(g_ans) > 40: g_ans = g_ans[:37] + "..."
        if len(a_ans) > 40: a_ans = a_ans[:37] + "..."

        md_lines.append(
            f"| `{qid}` | {qtype} | `{r_ans}` | `{g_ans}` | `{a_ans}` | "
            f"{row['rag']['tokens']} | {row['graphrag']['tokens']} | {row['agent']['tokens']} | {row['agent']['total_steps']} |"
        )

    with open(COMP_50_MD, "w", encoding="utf-8") as fmd:
        fmd.write("\n".join(md_lines) + "\n")
    print(f"[Saved] {COMP_50_MD}")

    # Also update results/summary_hidden50.md
    with open(SUMMARY_OUTPUT, "w", encoding="utf-8") as fsum:
        fsum.write("\n".join(md_lines[:30]) + f"\n\nFull details available in [`optimized_comparison_50_hidden.md`](../optimized_comparison_50_hidden.md).\n")
    print(f"[Saved] {SUMMARY_OUTPUT}")


def main():
    questions = load_hidden_questions()
    print(f"Loaded {len(questions)} hidden questions from {EVAL_HIDDEN_PATH.name}")

    # Set up global Agentic / GraphRAG LLM
    shared_agentic_llm = AgenticOllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_agentic_active_llm(shared_agentic_llm)

    # Clean existing hidden files for fresh benchmark run
    for p in [RAG_OUTPUT, GRAPHRAG_OUTPUT, AGENT_OUTPUT]:
        if p.exists():
            p.unlink()
            print(f"Cleared {p.name} for fresh benchmark execution.")

    # Run pipelines sequentially
    run_rag_hidden50(questions)
    run_graphrag_hidden50(questions, shared_agentic_llm)
    run_agent_hidden50(questions, shared_agentic_llm)

    # Build comparison files
    audit_and_build_reports(questions)


if __name__ == "__main__":
    main()
