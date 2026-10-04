"""Full 100-Question 3-Pipeline Benchmark Runner.

Executes:
1. Reuses results/results_rag_100.jsonl (copied from rag_only_pipeline/results_rag.jsonl).
2. Runs all 100 questions through GraphRAG pipeline -> results/results_graphrag_100.jsonl.
3. Runs all 100 questions through Agentic GraphRAG pipeline -> results/results_agent_100.jsonl.
4. Scores all three pipelines against eval_public.jsonl ground truth.
5. Produces comparison_100.json and comparison_100.md.

Supports incremental progress saving and automatic resumption.
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

from agentic_pipeline.config import SQLITE_DB_PATH, EVAL_PUBLIC_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import OllamaLLM, set_active_llm
from graphrag_pipeline.pipeline import GraphRAGPipeline

RESULTS_DIR = WORKSPACE_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RAG_OUTPUT = RESULTS_DIR / "results_rag_100.jsonl"
GRAPHRAG_OUTPUT = RESULTS_DIR / "results_graphrag_100.jsonl"
AGENT_OUTPUT = RESULTS_DIR / "results_agent_100.jsonl"
COMPARISON_JSON = WORKSPACE_ROOT / "comparison_100.json"
COMPARISON_MD = WORKSPACE_ROOT / "comparison_100.md"


def normalize_text(text: str) -> str:
    """Normalize text for fair string comparison."""
    if not text:
        return ""
    t = text.lower().replace("–", "-").replace("—", "-")
    return re.sub(r"[^a-z0-9\s-]", " ", t)


def evaluate_correctness(prediction: str, gold_answers: List[str]) -> bool:
    """Determine if prediction contains or matches gold answer."""
    if not prediction or not gold_answers:
        return False

    norm_pred = normalize_text(prediction)

    for gold in gold_answers:
        norm_gold = normalize_text(str(gold)).strip()
        if not norm_gold:
            continue

        # If numeric gold answer (e.g. '5', '8', '26')
        if norm_gold.isdigit():
            # Check for word boundary of the digit
            if re.search(r"\b" + re.escape(norm_gold) + r"\b", norm_pred):
                return True
        else:
            # Exact substring match
            if norm_gold in norm_pred:
                return True
            # Sub-phrase match for names / titles
            words = [w for w in norm_gold.split() if len(w) >= 3]
            if words and all(w in norm_pred for w in words):
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


def load_existing_jsonl(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load already-processed records from a JSONL file."""
    records = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    item = json.loads(line)
                    qid = item.get("question_id")
                    if qid:
                        records[qid] = item
    return records


def run_graphrag_100(questions: List[Dict[str, Any]], existing_gr: Dict[str, Dict[str, Any]], shared_llm: OllamaLLM):
    """Run GraphRAG pipeline over all 100 questions sequentially with incremental progress."""
    missing = [q for q in questions if q["qid"] not in existing_gr]
    print(f"\n[GraphRAG] Total questions: {len(questions)} | Already completed: {len(existing_gr)} | To run: {len(missing)}")

    if not missing:
        print("[GraphRAG] All 100 questions already evaluated. Skipping execution.")
        return

    pipe = GraphRAGPipeline(model_name=DEFAULT_OLLAMA_MODEL, llm=shared_llm)

    with open(GRAPHRAG_OUTPUT, "a", encoding="utf-8") as fg:
        for idx, q_item in enumerate(missing, 1):
            qid = q_item["qid"]
            qtext = q_item["question"]
            t0 = time.time()
            try:
                res = pipe.run(qtext, question_id=qid)
                res_dict = res.to_dict()
            except Exception as e:
                print(f"  [GraphRAG Error] {qid}: {e}")
                res_dict = {
                    "question_id": qid,
                    "answer": f"Error: {e}",
                    "citations": [],
                    "context_tokens": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "elapsed_time_s": round(time.time() - t0, 3)
                }

            fg.write(json.dumps(res_dict) + "\n")
            fg.flush()
            existing_gr[qid] = res_dict

            total_done = len(existing_gr)
            if total_done % 10 == 0 or idx == len(missing):
                print(f"  [GraphRAG Progress] {total_done}/100 questions completed ({res_dict['elapsed_time_s']}s on {qid}, {res_dict['total_tokens']} tokens)")

    pipe.close()
    print("[GraphRAG] Execution complete for all 100 questions.")


def run_agent_100(questions: List[Dict[str, Any]], existing_ag: Dict[str, Dict[str, Any]], shared_llm: OllamaLLM):
    """Run Agent pipeline over all 100 questions sequentially with incremental progress and full trace logging."""
    missing = [q for q in questions if q["qid"] not in existing_ag]
    print(f"\n[Agentic GraphRAG] Total questions: {len(questions)} | Already completed: {len(existing_ag)} | To run: {len(missing)}")

    if not missing:
        print("[Agentic GraphRAG] All 100 questions already evaluated. Skipping execution.")
        return

    graph = SQLiteGraph(str(SQLITE_DB_PATH))
    tools = ToolSuite(graph)
    orchestrator = AgenticOrchestrator(tools)

    with open(AGENT_OUTPUT, "a", encoding="utf-8") as fa:
        for idx, q_item in enumerate(missing, 1):
            qid = q_item["qid"]
            qtype = q_item.get("qtype", "unknown")
            qtext = q_item["question"]
            t0 = time.time()
            try:
                res = orchestrator.run(qtext)
                trace_summary = [
                    {
                        "step": s.step_num,
                        "action": s.action_type,
                        "tool": s.tool_name,
                        "args": s.tool_input,
                        "duration_s": round(s.duration_s, 2),
                        "tokens": s.tokens
                    }
                    for s in res.trace
                ]
                ag_dict = {
                    "question_id": qid,
                    "answer": res.answer,
                    "citations": [],
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
                ag_dict = {
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

            fa.write(json.dumps(ag_dict) + "\n")
            fa.flush()
            existing_ag[qid] = ag_dict

            total_done = len(existing_ag)
            if total_done % 10 == 0 or idx == len(missing):
                print(f"  [Agent Progress] {total_done}/100 questions completed ({ag_dict['elapsed_time_s']}s, {ag_dict['total_steps']} steps, {ag_dict['total_tokens']} tokens on {qid})")

    graph.close()
    print("[Agentic GraphRAG] Execution complete for all 100 questions.")


def build_comparison_reports(questions: List[Dict[str, Any]], rag_records: Dict[str, Any], gr_records: Dict[str, Any], ag_records: Dict[str, Any]):
    """Score all 3 pipelines across all 100 questions and output comparison_100.json and comparison_100.md."""
    print("\n" + "=" * 80)
    print("SCORING ALL 3 PIPELINES ACROSS 100 QUESTIONS")
    print("=" * 80)

    comparison_records = []
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

    total_ag_steps = 0

    rag_correct_total = 0
    gr_correct_total = 0
    ag_correct_total = 0

    total_q = len(questions)

    for q_item in questions:
        qid = q_item["qid"]
        qtype = q_item["qtype"]
        qtext = q_item["question"]
        gold_answers = q_item["answer"]

        # RAG
        r = rag_records.get(qid, {})
        rag_ans = r.get("answer", "N/A")
        rag_tokens = r.get("total_tokens", 0)
        rag_lat = r.get("elapsed_time_s", 0.0)
        rag_corr = evaluate_correctness(rag_ans, gold_answers)

        # GraphRAG
        g = gr_records.get(qid, {})
        gr_ans = g.get("answer", "N/A")
        gr_tokens = g.get("total_tokens", 0)
        gr_lat = g.get("elapsed_time_s", 0.0)
        gr_corr = evaluate_correctness(gr_ans, gold_answers)

        # Agent
        a = ag_records.get(qid, {})
        ag_ans = a.get("answer", "N/A")
        ag_tokens = a.get("total_tokens", 0)
        ag_lat = a.get("elapsed_time_s", 0.0)
        ag_steps = a.get("total_steps", 0)
        ag_stopped = a.get("stopped_reason", "unknown")
        ag_corr = evaluate_correctness(ag_ans, gold_answers)

        # Aggregation counters
        if rag_corr: rag_correct_total += 1
        if gr_corr: gr_correct_total += 1
        if ag_corr: ag_correct_total += 1

        total_rag_tokens += rag_tokens
        total_gr_tokens += gr_tokens
        total_ag_tokens += ag_tokens

        total_rag_lat += rag_lat
        total_gr_lat += gr_lat
        total_ag_lat += ag_lat

        total_ag_steps += ag_steps

        # Category counters
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

        comparison_records.append({
            "question_id": qid,
            "query_type": qtype,
            "question": qtext,
            "gold_answer": gold_answers,
            "rag": {
                "answer": rag_ans,
                "correct": rag_corr,
                "tokens": rag_tokens,
                "latency": round(rag_lat, 3)
            },
            "graphrag": {
                "answer": gr_ans,
                "correct": gr_corr,
                "tokens": gr_tokens,
                "latency": round(gr_lat, 3)
            },
            "agent": {
                "answer": ag_ans,
                "correct": ag_corr,
                "tokens": ag_tokens,
                "latency": round(ag_lat, 3),
                "total_steps": ag_steps,
                "stopped_reason": ag_stopped
            }
        })

    # Summary Metrics
    rag_acc = (rag_correct_total / total_q) * 100
    gr_acc = (gr_correct_total / total_q) * 100
    ag_acc = (ag_correct_total / total_q) * 100

    summary_data = {
        "total_questions": total_q,
        "overall_accuracy": {
            "RAG": round(rag_acc, 1),
            "GraphRAG": round(gr_acc, 1),
            "Agent": round(ag_acc, 1)
        },
        "average_tokens": {
            "RAG": round(total_rag_tokens / total_q, 1),
            "GraphRAG": round(total_gr_tokens / total_q, 1),
            "Agent": round(total_ag_tokens / total_q, 1)
        },
        "total_tokens": {
            "RAG": total_rag_tokens,
            "GraphRAG": total_gr_tokens,
            "Agent": total_ag_tokens
        },
        "average_latency_s": {
            "RAG": round(total_rag_lat / total_q, 2),
            "GraphRAG": round(total_gr_lat / total_q, 2),
            "Agent": round(total_ag_lat / total_q, 2)
        },
        "total_wall_clock_s": {
            "RAG": round(total_rag_lat, 1),
            "GraphRAG": round(total_gr_lat, 1),
            "Agent": round(total_ag_lat, 1)
        },
        "agent_average_steps": round(total_ag_steps / total_q, 2),
        "by_type": {
            qt: {
                "total": s["total"],
                "accuracy": {
                    "RAG": round(s["rag_corr"] / s["total"] * 100, 1),
                    "GraphRAG": round(s["gr_corr"] / s["total"] * 100, 1),
                    "Agent": round(s["ag_corr"] / s["total"] * 100, 1)
                },
                "tokens": {
                    "RAG": round(s["rag_tokens"] / s["total"], 1),
                    "GraphRAG": round(s["gr_tokens"] / s["total"], 1),
                    "Agent": round(s["ag_tokens"] / s["total"], 1)
                },
                "latency_s": {
                    "RAG": round(s["rag_lat"] / s["total"], 2),
                    "GraphRAG": round(s["gr_lat"] / s["total"], 2),
                    "Agent": round(s["ag_lat"] / s["total"], 2)
                },
                "agent_avg_steps": round(s["ag_steps"] / s["total"], 2)
            }
            for qt, s in sorted(type_stats.items())
        }
    }

    # Write comparison_100.json
    with open(COMPARISON_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary_data,
            "questions": comparison_records
        }, f, indent=2, ensure_ascii=False)
    print(f"[Saved] {COMPARISON_JSON}")

    # Build Markdown Report
    md_lines = [
        "# 3-Pipeline Comparative Benchmark Report (Full 100 Evaluation Questions)",
        "",
        "This report documents the systematic evaluation of all three architectures across all 100 questions from `eval_public.jsonl`:",
        "1. **Pipeline 1 (Plain RAG)**: Fixed top-8 BM25 retrieval over document text chunks.",
        "2. **Pipeline 2 (GraphRAG)**: Single-retrieval structured Knowledge Graph lookup + narrative chunk augmentation.",
        "3. **Pipeline 3 (Agentic GraphRAG)**: Autonomous orchestrator with dynamic planning, tool calling, and evidence evaluation.",
        "",
        "---",
        "",
        "## 1. Summary Results (100 Questions)",
        "",
        "| Pipeline | Overall Accuracy | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        f"| **Pipeline 1: Plain RAG** | **{rag_acc:.1f}%** ({rag_correct_total}/100) | {total_rag_tokens/total_q:.0f} | {total_rag_tokens:,} | {total_rag_lat/total_q:.2f}s | {total_rag_lat/60:.1f}m ({total_rag_lat:.1f}s) | N/A (1 step) |",
        f"| **Pipeline 2: GraphRAG** | **{gr_acc:.1f}%** ({gr_correct_total}/100) | {total_gr_tokens/total_q:.0f} | {total_gr_tokens:,} | {total_gr_lat/total_q:.2f}s | {total_gr_lat/60:.1f}m ({total_gr_lat:.1f}s) | N/A (1 step) |",
        f"| **Pipeline 3: Agentic GraphRAG** | **{ag_acc:.1f}%** ({ag_correct_total}/100) | {total_ag_tokens/total_q:.0f} | {total_ag_tokens:,} | {total_ag_lat/total_q:.2f}s | {total_ag_lat/60:.1f}m ({total_ag_lat:.1f}s) | {total_ag_steps/total_q:.2f} steps |",
        "",
        "---",
        "",
        "## 2. Accuracy by Query Type Breakdown",
        "",
        "| Query Type | Questions | Plain RAG Accuracy | GraphRAG Accuracy | Agentic GraphRAG Accuracy |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]

    for qt, s in sorted(summary_data["by_type"].items()):
        md_lines.append(f"| **{qt}** | {s['total']} | {s['accuracy']['RAG']:.1f}% | {s['accuracy']['GraphRAG']:.1f}% | {s['accuracy']['Agent']:.1f}% |")

    md_lines.extend([
        "",
        "### Token Consumption by Query Type (Average Tokens / Question)",
        "",
        "| Query Type | Questions | Plain RAG Tokens | GraphRAG Tokens | Agentic GraphRAG Tokens |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])

    for qt, s in sorted(summary_data["by_type"].items()):
        md_lines.append(f"| **{qt}** | {s['total']} | {s['tokens']['RAG']:.0f} | {s['tokens']['GraphRAG']:.0f} | {s['tokens']['Agent']:.0f} |")

    md_lines.extend([
        "",
        "### Latency by Query Type (Average Seconds / Question)",
        "",
        "| Query Type | Questions | Plain RAG Latency | GraphRAG Latency | Agentic GraphRAG Latency |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])

    for qt, s in sorted(summary_data["by_type"].items()):
        md_lines.append(f"| **{qt}** | {s['total']} | {s['latency_s']['RAG']:.2f}s | {s['latency_s']['GraphRAG']:.2f}s | {s['latency_s']['Agent']:.2f}s |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Headline Findings at Full Scale (100 Questions)",
        "",
        f"- **Aggregation & Superlative Scalability**: Plain RAG achieved {summary_data['by_type'].get('aggregation', {}).get('accuracy', {}).get('RAG', 0.0)}% on aggregation questions due to chunk truncation (Frac@8 retrieval gap). Both GraphRAG and Agentic bypass top-k chunk limits via structured SQL aggregation over all candidate events in the graph.",
        f"- **Autonomy vs Token Efficiency**: Agentic GraphRAG required {total_ag_tokens/total_rag_tokens:.1f}x tokens ({total_ag_tokens:,} vs {total_rag_tokens:,}) compared to Plain RAG, averaging {total_ag_steps/total_q:.2f} steps per question.",
        f"- **Single-Turn vs Multi-Turn Graph Performance**: GraphRAG completed the 100 questions in {total_gr_lat/60:.1f} minutes ({total_gr_lat/total_q:.2f}s/q) while Agentic took {total_ag_lat/60:.1f} minutes ({total_ag_lat/total_q:.2f}s/q).",
        "",
        "---",
        "",
        "## 4. Question-by-Question Comparison Table (All 100 Questions)",
        "",
        "| QID | Type | Gold Target | RAG | GraphRAG | Agent | RAG Tok | GR Tok | AG Tok | RAG Lat | GR Lat | AG Lat |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ])

    for r in comparison_records:
        gold_repr = str(r["gold_answer"])
        if len(gold_repr) > 40:
            gold_repr = gold_repr[:37] + "..."
        r_c = "✅" if r["rag"]["correct"] else "❌"
        g_c = "✅" if r["graphrag"]["correct"] else "❌"
        a_c = "✅" if r["agent"]["correct"] else "❌"
        md_lines.append(
            f"| `{r['question_id']}` | {r['query_type']} | `{gold_repr}` | {r_c} | {g_c} | {a_c} | "
            f"{r['rag']['tokens']} | {r['graphrag']['tokens']} | {r['agent']['tokens']} | "
            f"{r['rag']['latency']}s | {r['graphrag']['latency']}s | {r['agent']['latency']}s |"
        )

    with open(COMPARISON_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[Saved] {COMPARISON_MD}")

    print("\n" + "=" * 80)
    print("100-QUESTION BENCHMARK COMPLETE")
    print(f"Overall Accuracy:  RAG: {rag_acc:.1f}% | GraphRAG: {gr_acc:.1f}% | Agent: {ag_acc:.1f}%")
    print(f"Total Tokens:      RAG: {total_rag_tokens:,} | GraphRAG: {total_gr_tokens:,} | Agent: {total_ag_tokens:,}")
    print(f"Total Wall-Clock:  RAG: {total_rag_lat/60:.1f}m | GraphRAG: {total_gr_lat/60:.1f}m | Agent: {total_ag_lat/60:.1f}m")
    print("=" * 80)


def main():
    print("=" * 80)
    print("STARTING FULL 100-QUESTION 3-PIPELINE BENCHMARK")
    print("=" * 80)

    # 1. Load questions
    questions = load_all_questions()
    print(f"Loaded {len(questions)} evaluation questions from {EVAL_PUBLIC_PATH}")

    # 2. Load existing RAG results
    existing_rag = load_existing_jsonl(RAG_OUTPUT)
    print(f"Loaded {len(existing_rag)} RAG records from {RAG_OUTPUT}")

    # 3. Load existing GraphRAG results
    existing_gr = load_existing_jsonl(GRAPHRAG_OUTPUT)
    print(f"Loaded {len(existing_gr)} existing GraphRAG records from {GRAPHRAG_OUTPUT}")

    # 4. Load existing Agent results
    existing_ag = load_existing_jsonl(AGENT_OUTPUT)
    print(f"Loaded {len(existing_ag)} existing Agent records from {AGENT_OUTPUT}")

    # Initialize shared local LLM
    shared_llm = OllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_active_llm(shared_llm)

    # Step 1: Run GraphRAG sequentially
    run_graphrag_100(questions, existing_gr, shared_llm)

    # Step 2: Run Agentic GraphRAG sequentially
    run_agent_100(questions, existing_ag, shared_llm)

    # Step 3: Score and generate comparison reports
    build_comparison_reports(questions, existing_rag, existing_gr, existing_ag)


if __name__ == "__main__":
    main()
