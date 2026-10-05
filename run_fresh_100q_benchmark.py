"""Full 100-Question 3-Pipeline Benchmark Runner (Fresh Optimized Execution).

Executes all 3 pipelines sequentially across all 100 public evaluation questions
(drive-download-20260928T175718Z-1-001/questions/eval_public.jsonl):
  1. Plain RAG -> results/results_rag_100.jsonl
  2. GraphRAG -> results/results_graphrag_100.jsonl
  3. Optimized Agentic GraphRAG -> results/results_agent_100_optimized.jsonl

Scores all 3 pipelines against eval_public.jsonl ground truth.
Outputs:
  - comparison_100_final.json
  - comparison_100_final.md
  - metrics_dashboard.html (auto-updated)

Supports resume and atomic line streaming with progress every 10 questions.
"""

import sys
import os
import json
import time
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

# Configuration and Database
from agentic_pipeline.config import SQLITE_DB_PATH, EVAL_PUBLIC_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator

# LLM Bindings
from rag_only_pipeline.llm.llm_client import OllamaLLM as RagOllamaLLM, set_active_llm as set_rag_active_llm
from rag_only_pipeline.pipeline import RAGPipeline

from agentic_pipeline.llm_interface import OllamaLLM as AgenticOllamaLLM, set_active_llm as set_agentic_active_llm
from graphrag_pipeline.pipeline import GraphRAGPipeline

RESULTS_DIR = WORKSPACE_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RAG_OUTPUT = RESULTS_DIR / "results_rag_100.jsonl"
GRAPHRAG_OUTPUT = RESULTS_DIR / "results_graphrag_100.jsonl"
AGENT_OUTPUT = RESULTS_DIR / "results_agent_100_optimized.jsonl"

COMPARISON_FINAL_JSON = WORKSPACE_ROOT / "comparison_100_final.json"
COMPARISON_FINAL_MD = WORKSPACE_ROOT / "comparison_100_final.md"
BASELINE_100_JSON = WORKSPACE_ROOT / "comparison_100.json"


def normalize_text(text: str) -> str:
    """Normalize text for fair string comparison."""
    if not text:
        return ""
    t = text.lower().replace("–", "-").replace("—", "-")
    return re.sub(r"[^a-z0-9\s-]", " ", t)


def evaluate_correctness(prediction: str, gold_answers: List[str]) -> bool:
    """Determine if prediction matches or contains any gold answer."""
    if not prediction or not gold_answers:
        return False

    norm_pred = normalize_text(prediction)

    for gold in gold_answers:
        norm_gold = normalize_text(str(gold)).strip()
        if not norm_gold:
            continue

        # 1. Exact numeric match with word boundary check
        if norm_gold.isdigit():
            m = re.search(r"\b" + re.escape(norm_gold) + r"\b", norm_pred)
            if m:
                return True
            continue

        # 2. Exact substring match
        if norm_gold in norm_pred:
            return True

        # 3. Surname / Multi-word match
        gold_words = norm_gold.split()
        if len(gold_words) >= 2:
            # Significant surname check
            surname = gold_words[-1]
            if len(surname) >= 4 and surname in norm_pred:
                return True
            # All individual words match
            if all(w in norm_pred for w in gold_words if len(w) > 2):
                return True

    return False


def load_all_questions() -> List[Dict[str, Any]]:
    """Load all 100 questions from eval_public.jsonl."""
    questions = []
    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def load_existing(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load already processed records for resuming."""
    records = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        item = json.loads(line)
                        qid = item.get("question_id") or item.get("qid")
                        if qid:
                            records[qid] = item
                    except Exception:
                        pass
    return records


def run_rag_100(questions: List[Dict[str, Any]]) -> None:
    """Execute Plain RAG pipeline across all 100 questions."""
    print("\n" + "=" * 80)
    print("STEP 1: PLAIN RAG PIPELINE (100 Questions)")
    print("=" * 80)

    rag_llm = RagOllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_rag_active_llm(rag_llm)

    existing = load_existing(RAG_OUTPUT)
    missing = [q for q in questions if q["qid"] not in existing]
    print(f"Total: {len(questions)} | Already completed: {len(existing)} | To run: {len(missing)}")

    if not missing:
        print("[RAG] All 100 questions already completed. Skipping.")
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
    print(f"[RAG] Execution complete in {elapsed_total:.2f}s.")


def run_graphrag_100(questions: List[Dict[str, Any]], shared_llm: AgenticOllamaLLM) -> None:
    """Execute GraphRAG pipeline across all 100 questions."""
    print("\n" + "=" * 80)
    print("STEP 2: GRAPHRAG PIPELINE (100 Questions)")
    print("=" * 80)

    existing = load_existing(GRAPHRAG_OUTPUT)
    missing = [q for q in questions if q["qid"] not in existing]
    print(f"Total: {len(questions)} | Already completed: {len(existing)} | To run: {len(missing)}")

    if not missing:
        print("[GraphRAG] All 100 questions already completed. Skipping.")
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
    print(f"[GraphRAG] Execution complete in {elapsed_total:.2f}s.")


def run_agent_100(questions: List[Dict[str, Any]], shared_llm: AgenticOllamaLLM) -> None:
    """Execute Optimized Agent pipeline across all 100 questions."""
    print("\n" + "=" * 80)
    print("STEP 3: OPTIMIZED AGENTIC GRAPHRAG PIPELINE (100 Questions)")
    print("=" * 80)

    existing = load_existing(AGENT_OUTPUT)
    missing = [q for q in questions if q["qid"] not in existing]
    print(f"Total: {len(questions)} | Already completed: {len(existing)} | To run: {len(missing)}")

    if not missing:
        print("[Agentic GraphRAG] All 100 questions already completed. Skipping.")
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
    print(f"[Agentic GraphRAG] Execution complete in {elapsed_total:.2f}s.")


def score_and_build_reports(questions: List[Dict[str, Any]]):
    """Score all 3 pipelines across all 100 questions, output comparison JSON/MD, and update dashboard."""
    print("\n" + "=" * 80)
    print("STEP 4: SCORING ALL 3 PIPELINES & GENERATING FINAL REPORTS")
    print("=" * 80)

    rag_records = load_existing(RAG_OUTPUT)
    graphrag_records = load_existing(GRAPHRAG_OUTPUT)
    agent_records = load_existing(AGENT_OUTPUT)

    # Load baseline pre-optimization comparison for delta calculations
    baseline_summary = {}
    if BASELINE_100_JSON.exists():
        try:
            with open(BASELINE_100_JSON, "r", encoding="utf-8") as fb:
                b_data = json.load(fb)
                baseline_summary = b_data.get("summary", {})
        except Exception:
            pass

    comparison_data = []
    type_stats = defaultdict(lambda: {
        "total": 0,
        "rag_corr": 0, "gr_corr": 0, "ag_corr": 0,
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

    for q_item in questions:
        qid = q_item["qid"]
        qtype = q_item.get("qtype", "unknown")
        qtext = q_item["question"]
        gold_answers = q_item.get("answer", [])

        # RAG
        r_rec = rag_records.get(qid, {})
        rag_ans = r_rec.get("answer", "")
        rag_tokens = r_rec.get("total_tokens", 0)
        rag_lat = r_rec.get("elapsed_time_s", 0.0)
        rag_corr = evaluate_correctness(rag_ans, gold_answers)

        # GraphRAG
        g_rec = graphrag_records.get(qid, {})
        gr_ans = g_rec.get("answer", "")
        gr_tokens = g_rec.get("total_tokens", 0)
        gr_lat = g_rec.get("elapsed_time_s", 0.0)
        gr_corr = evaluate_correctness(gr_ans, gold_answers)

        # Agent
        a_rec = agent_records.get(qid, {})
        ag_ans = a_rec.get("answer", "")
        ag_tokens = a_rec.get("total_tokens", 0)
        ag_lat = a_rec.get("elapsed_time_s", 0.0)
        ag_steps = a_rec.get("total_steps", 0)
        ag_stopped = a_rec.get("stopped_reason", "unknown")
        ag_trace = a_rec.get("trace", [])
        ag_corr = evaluate_correctness(ag_ans, gold_answers)

        # Accumulate
        total_rag_tokens += rag_tokens
        total_gr_tokens += gr_tokens
        total_ag_tokens += ag_tokens

        total_rag_lat += rag_lat
        total_gr_lat += gr_lat
        total_ag_lat += ag_lat
        ag_steps_sum += ag_steps

        type_stats[qtype]["total"] += 1
        if rag_corr: type_stats[qtype]["rag_corr"] += 1
        if gr_corr: type_stats[qtype]["gr_corr"] += 1
        if ag_corr: type_stats[qtype]["ag_corr"] += 1

        type_stats[qtype]["rag_tokens"] += rag_tokens
        type_stats[qtype]["gr_tokens"] += gr_tokens
        type_stats[qtype]["ag_tokens"] += ag_tokens

        type_stats[qtype]["rag_lat"] += rag_lat
        type_stats[qtype]["gr_lat"] += gr_lat
        type_stats[qtype]["ag_lat"] += ag_lat
        type_stats[qtype]["ag_steps"] += ag_steps

        comparison_data.append({
            "question_id": qid,
            "query_type": qtype,
            "question": qtext,
            "gold_answer": gold_answers,
            "rag": {
                "answer": rag_ans,
                "correct": rag_corr,
                "tokens": rag_tokens,
                "elapsed_time_s": rag_lat,
                "citations": r_rec.get("citations", [])
            },
            "graphrag": {
                "answer": gr_ans,
                "correct": gr_corr,
                "tokens": gr_tokens,
                "elapsed_time_s": gr_lat,
                "citations": g_rec.get("citations", [])
            },
            "agent": {
                "answer": ag_ans,
                "correct": ag_corr,
                "tokens": ag_tokens,
                "elapsed_time_s": ag_lat,
                "total_steps": ag_steps,
                "stopped_reason": ag_stopped,
                "trace": ag_trace
            }
        })

    total_q = len(questions)
    rag_corr_total = sum(d["rag"]["correct"] for d in comparison_data)
    gr_corr_total = sum(d["graphrag"]["correct"] for d in comparison_data)
    ag_corr_total = sum(d["agent"]["correct"] for d in comparison_data)

    rag_acc = (rag_corr_total / total_q) * 100
    gr_acc = (gr_corr_total / total_q) * 100
    ag_acc = (ag_corr_total / total_q) * 100

    summary_obj = {
        "benchmark_scale": f"{total_q} questions",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_questions": total_q,
        "accuracy": {
            "rag": round(rag_acc, 1),
            "graphrag": round(gr_acc, 1),
            "agent": round(ag_acc, 1)
        },
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
                "accuracy": {
                    "rag": round((stats["rag_corr"] / stats["total"]) * 100, 1),
                    "graphrag": round((stats["gr_corr"] / stats["total"]) * 100, 1),
                    "agent": round((stats["ag_corr"] / stats["total"]) * 100, 1)
                },
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
        "questions": comparison_data
    }

    # Save comparison_100_final.json
    with open(COMPARISON_FINAL_JSON, "w", encoding="utf-8") as fj:
        json.dump(full_export, fj, indent=2, ensure_ascii=False)
    print(f"[Saved] {COMPARISON_FINAL_JSON}")

    # Build comparison_100_final.md
    md_lines = [
        "# 3-Pipeline Comparative Benchmark Report (Final Submission - 100 Questions)\n",
        "This report documents the definitive evaluation across all 100 questions from `eval_public.jsonl`.",
        "It benchmarks **Pipeline 1 (Plain RAG)**, **Pipeline 2 (GraphRAG)**, and **Pipeline 3 (Optimized Agentic GraphRAG)**.\n",
        "> **Note on Historical Baseline**: The original unoptimized run is preserved unedited in `comparison_100.md`.",
        "> This report (`comparison_100_final.md`) reflects the submission-ready system incorporating lightweight schema projection, compact context injection, and concise synthesis prompting.\n",
        "---\n",
        "## 1. Summary Results (100 Questions)\n",
        "| Pipeline | Overall Accuracy | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        f"| **Pipeline 1: Plain RAG** | **{rag_acc:.1f}%** ({rag_corr_total}/{total_q}) | {summary_obj['tokens']['rag_avg']} | {total_rag_tokens:,} | {summary_obj['latency']['rag_avg_s']:.2f}s | {total_rag_lat/60:.1f}m ({total_rag_lat:.1f}s) | N/A (1 step) |",
        f"| **Pipeline 2: GraphRAG** | **{gr_acc:.1f}%** ({gr_corr_total}/{total_q}) | {summary_obj['tokens']['graphrag_avg']} | {total_gr_tokens:,} | {summary_obj['latency']['graphrag_avg_s']:.2f}s | {total_gr_lat/60:.1f}m ({total_gr_lat:.1f}s) | N/A (1 step) |",
        f"| **Pipeline 3: Optimized Agent** | **{ag_acc:.1f}%** ({ag_corr_total}/{total_q}) | **{summary_obj['tokens']['agent_avg']}** | **{total_ag_tokens:,}** | **{summary_obj['latency']['agent_avg_s']:.2f}s** | **{total_ag_lat/60:.1f}m ({total_ag_lat:.1f}s)** | **{summary_obj['agent_steps']['avg_steps']:.2f} steps** |\n",
        "---\n",
        "## 2. Accuracy by Query Type Breakdown\n",
        "| Query Type | Questions | Plain RAG Accuracy | GraphRAG Accuracy | Optimized Agent Accuracy |",
        "| :--- | :---: | :---: | :---: | :---: |"
    ]

    for qtype, s in full_export["type_breakdown"].items():
        md_lines.append(f"| **{qtype}** | {s['total']} | {s['accuracy']['rag']:.1f}% | {s['accuracy']['graphrag']:.1f}% | **{s['accuracy']['agent']:.1f}%** |")

    md_lines.extend([
        "\n### Token Consumption by Query Type (Average Tokens / Question)\n",
        "| Query Type | Questions | Plain RAG Tokens | GraphRAG Tokens | Optimized Agent Tokens |",
        "| :--- | :---: | :---: | :---: | :---: |"
    ])

    for qtype, s in full_export["type_breakdown"].items():
        md_lines.append(f"| **{qtype}** | {s['total']} | {s['tokens_avg']['rag']} | {s['tokens_avg']['graphrag']} | **{s['tokens_avg']['agent']}** |")

    md_lines.extend([
        "\n---\n",
        "## 3. Question-by-Question Detailed Results (All 100 Questions)\n",
        "| ID | Type | Gold Answer | RAG | GraphRAG | Agent | RAG Tok | GR Tok | Agent Tok | RAG Time | GR Time | Agent Time |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ])

    for row in comparison_data:
        qid = row["question_id"]
        qtype = row["query_type"]
        gold_str = str(row["gold_answer"])
        if len(gold_str) > 25:
            gold_str = gold_str[:22] + "..."
        r_mark = "✅" if row["rag"]["correct"] else "❌"
        g_mark = "✅" if row["graphrag"]["correct"] else "❌"
        a_mark = "✅" if row["agent"]["correct"] else "❌"

        md_lines.append(
            f"| `{qid}` | {qtype} | `{gold_str}` | {r_mark} | {g_mark} | {a_mark} | "
            f"{row['rag']['tokens']} | {row['graphrag']['tokens']} | {row['agent']['tokens']} | "
            f"{row['rag']['elapsed_time_s']:.3f}s | {row['graphrag']['elapsed_time_s']:.3f}s | {row['agent']['elapsed_time_s']:.3f}s |"
        )

    with open(COMPARISON_FINAL_MD, "w", encoding="utf-8") as fmd:
        fmd.write("\n".join(md_lines) + "\n")
    print(f"[Saved] {COMPARISON_FINAL_MD}")

    # Update dashboard
    try:
        from generate_dashboard import WORKSPACE_ROOT as D_ROOT, json_path as D_JSON, html_path as D_HTML
        import subprocess
        subprocess.run([sys.executable, str(WORKSPACE_ROOT / "generate_dashboard.py")], check=True)
        print("[Dashboard] Successfully regenerated metrics_dashboard.html")
    except Exception as e:
        print(f"[Dashboard Update Warning] {e}")

    print("\n" + "=" * 80)
    print("100-QUESTION BENCHMARK COMPLETE")
    print(f"Overall Accuracy:  RAG: {rag_acc:.1f}% | GraphRAG: {gr_acc:.1f}% | Agent: {ag_acc:.1f}%")
    print(f"Total Tokens:      RAG: {total_rag_tokens:,} | GraphRAG: {total_gr_tokens:,} | Agent: {total_ag_tokens:,}")
    print(f"Total Wall-Clock:  RAG: {total_rag_lat/60:.1f}m | GraphRAG: {total_gr_lat/60:.1f}m | Agent: {total_ag_lat/60:.1f}m")
    print("=" * 80)


def main():
    questions = load_all_questions()
    print(f"Loaded {len(questions)} evaluation questions from {EVAL_PUBLIC_PATH.name}")

    # Set up global Agentic / GraphRAG LLM
    shared_agentic_llm = AgenticOllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_agentic_active_llm(shared_agentic_llm)

    # Clean existing fresh files if user wants complete fresh run
    # (Since we backed up existing results to archive/pre_fresh_100q_backup)
    for p in [RAG_OUTPUT, GRAPHRAG_OUTPUT, AGENT_OUTPUT]:
        if p.exists():
            p.unlink()
            print(f"Cleared {p.name} for fresh benchmark execution.")

    # Run pipelines sequentially
    run_rag_100(questions)
    run_graphrag_100(questions, shared_agentic_llm)
    run_agent_100(questions, shared_agentic_llm)

    # Score and generate all reports
    score_and_build_reports(questions)


if __name__ == "__main__":
    main()
