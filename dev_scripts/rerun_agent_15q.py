"""Rerun full 15-question agent benchmark with the applied general fixes.
Compares new metrics against old benchmark numbers, checks for regressions,
and updates results_agentic.jsonl, comparison_15q.json, and comparison_15q.md.
"""

import sys
import json
import time
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List
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

SELECTED_QIDS = [
    # Aggregation
    "pub-001", "pub-003", "pub-010",
    # Temporal
    "pub-002", "pub-006", "pub-007",
    # Superlative
    "pub-004", "pub-008", "pub-021",
    # Multi-hop
    "pub-005", "pub-011", "pub-014",
    # Lookup
    "pub-009", "pub-025", "pub-029",
]

def normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.lower().replace("–", "-").replace("—", "-")
    return re.sub(r"[^a-z0-9\s-]", " ", t)

def evaluate_correctness(prediction: str, gold_answers: List[str]) -> bool:
    if not prediction or not gold_answers:
        return False
    norm_pred = normalize_text(prediction)
    for gold in gold_answers:
        norm_gold = normalize_text(str(gold)).strip()
        if not norm_gold:
            continue
        if norm_gold.isdigit():
            if re.search(r"\b" + re.escape(norm_gold) + r"\b", norm_pred):
                return True
        else:
            if norm_gold in norm_pred:
                return True
            words = [w for w in norm_gold.split() if len(w) >= 3]
            if words and all(w in norm_pred for w in words):
                return True
    return False

def load_selected_questions():
    questions_map = {}
    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                questions_map[item.get("qid")] = item
    return [questions_map[qid] for qid in SELECTED_QIDS if qid in questions_map]

def main():
    print("=" * 80)
    print("RERUNNING FULL 15-QUESTION AGENT BENCHMARK (AFTER FIXES)")
    print("=" * 80)

    # 1. Load questions
    questions = load_selected_questions()
    print(f"Loaded {len(questions)} test questions.")

    # 2. Load existing comparison_15q.json to get old baseline
    old_comp_path = WORKSPACE_ROOT / "comparison_15q.json"
    old_records = {}
    old_summary = {}
    if old_comp_path.exists():
        with open(old_comp_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            old_summary = old_data.get("summary", {})
            for q in old_data.get("questions", []):
                old_records[q["question_id"]] = q

    # Backup old results_agentic.jsonl
    ag_path = WORKSPACE_ROOT / "results_agentic.jsonl"
    ag_backup = WORKSPACE_ROOT / "results_agentic_pre_fix.jsonl"
    if ag_path.exists() and not ag_backup.exists():
        shutil.copy(ag_path, ag_backup)
        print(f"Backed up old agentic results to: {ag_backup}")

    # Load existing RAG and GraphRAG (untouched)
    gr_path = WORKSPACE_ROOT / "results_graphrag.jsonl"
    existing_gr = {}
    with open(gr_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                existing_gr[item["question_id"]] = item

    rag_path = WORKSPACE_ROOT / "rag_only_pipeline" / "results_rag.jsonl"
    existing_rag = {}
    with open(rag_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                existing_rag[item["question_id"]] = item

    # Initialize agent
    print(f"Connecting to Ollama model ({DEFAULT_OLLAMA_MODEL})...")
    shared_llm = OllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_active_llm(shared_llm)

    graph = SQLiteGraph(str(SQLITE_DB_PATH))
    tools = ToolSuite(graph)
    orchestrator = AgenticOrchestrator(tools)

    new_ag_results = []
    comparison_records = []

    print("\nRunning Agent on all 15 questions...\n")
    for idx, q_item in enumerate(questions, 1):
        qid = q_item["qid"]
        qtype = q_item["qtype"]
        qtext = q_item["question"]
        gold_answers = q_item["answer"]

        print(f"[{idx}/15] Running {qid} ({qtype})...")
        t0 = time.time()
        try:
            res = orchestrator.run(qtext)
            ag_ans = res.answer
            ag_tokens = res.total_tokens
            ag_prompt_tok = res.prompt_tokens
            ag_comp_tok = res.completion_tokens
            ag_steps = res.total_steps
            ag_latency = res.elapsed_time_s
            ag_stopped = res.stopped_reason
        except Exception as e:
            print(f"  Error on {qid}: {e}")
            ag_ans = f"Error: {e}"
            ag_tokens = 0
            ag_prompt_tok = 0
            ag_comp_tok = 0
            ag_steps = 0
            ag_latency = round(time.time() - t0, 3)
            ag_stopped = f"error: {e}"

        ag_corr = evaluate_correctness(ag_ans, gold_answers)
        
        # Check against old correctness
        old_q = old_records.get(qid, {}).get("agent", {})
        old_corr = old_q.get("correct", None)
        corr_diff = ""
        if old_corr is not None:
            if old_corr == ag_corr:
                corr_diff = "(unchanged)"
            elif not old_corr and ag_corr:
                corr_diff = "🎉 FIXED (was False -> now True)"
            elif old_corr and not ag_corr:
                corr_diff = "⚠️ REGRESSION (was True -> now False)"

        print(f"   Correct: {ag_corr} {corr_diff} | Steps: {ag_steps} | Tokens: {ag_tokens} | Latency: {ag_latency:.2f}s | Stopped: {ag_stopped}")
        print(f"   Ans: {ag_ans[:90]}...\n")

        ag_record = {
            "question_id": qid,
            "answer": ag_ans,
            "total_tokens": ag_tokens,
            "prompt_tokens": ag_prompt_tok,
            "completion_tokens": ag_comp_tok,
            "total_steps": ag_steps,
            "elapsed_time_s": round(ag_latency, 3),
            "stopped_reason": ag_stopped
        }
        new_ag_results.append(ag_record)

        # RAG record
        r_rec = existing_rag.get(qid, {})
        rag_ans = r_rec.get("answer", "N/A")
        rag_tokens = r_rec.get("total_tokens", 0)
        rag_lat = r_rec.get("elapsed_time_s", 0.0)
        rag_corr = evaluate_correctness(rag_ans, gold_answers)

        # GraphRAG record
        g_rec = existing_gr.get(qid, {})
        gr_ans = g_rec.get("answer", "N/A")
        gr_tokens = g_rec.get("total_tokens", 0)
        gr_lat = g_rec.get("elapsed_time_s", 0.0)
        gr_corr = evaluate_correctness(gr_ans, gold_answers)

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
                "latency": round(ag_latency, 3),
                "total_steps": ag_steps,
                "stopped_reason": ag_stopped
            }
        })

    graph.close()

    # Save new results_agentic.jsonl
    with open(ag_path, "w", encoding="utf-8") as f:
        for r in new_ag_results:
            f.write(json.dumps(r) + "\n")
    print(f"[Saved] New results_agentic.jsonl ({len(new_ag_results)} records)")

    # Compute new statistics
    total_q = len(comparison_records)
    rag_acc = sum(1 for r in comparison_records if r["rag"]["correct"]) / total_q * 100
    gr_acc = sum(1 for r in comparison_records if r["graphrag"]["correct"]) / total_q * 100
    ag_acc = sum(1 for r in comparison_records if r["agent"]["correct"]) / total_q * 100

    ag_avg_tokens = sum(r["agent"]["tokens"] for r in comparison_records) / total_q
    ag_avg_lat = sum(r["agent"]["latency"] for r in comparison_records) / total_q
    ag_avg_steps = sum(r["agent"]["total_steps"] for r in comparison_records) / total_q

    rag_avg_tokens = sum(r["rag"]["tokens"] for r in comparison_records) / total_q
    rag_avg_lat = sum(r["rag"]["latency"] for r in comparison_records) / total_q

    gr_avg_tokens = sum(r["graphrag"]["tokens"] for r in comparison_records) / total_q
    gr_avg_lat = sum(r["graphrag"]["latency"] for r in comparison_records) / total_q

    type_stats = defaultdict(lambda: {
        "total": 0, 
        "rag_corr": 0, "gr_corr": 0, "ag_corr": 0,
        "rag_tokens": 0, "gr_tokens": 0, "ag_tokens": 0,
        "rag_lat": 0.0, "gr_lat": 0.0, "ag_lat": 0.0
    })
    for r in comparison_records:
        qt = r["query_type"]
        type_stats[qt]["total"] += 1
        if r["rag"]["correct"]: type_stats[qt]["rag_corr"] += 1
        if r["graphrag"]["correct"]: type_stats[qt]["gr_corr"] += 1
        if r["agent"]["correct"]: type_stats[qt]["ag_corr"] += 1
        type_stats[qt]["rag_tokens"] += r["rag"]["tokens"]
        type_stats[qt]["gr_tokens"] += r["graphrag"]["tokens"]
        type_stats[qt]["ag_tokens"] += r["agent"]["tokens"]
        type_stats[qt]["rag_lat"] += r["rag"]["latency"]
        type_stats[qt]["gr_lat"] += r["graphrag"]["latency"]
        type_stats[qt]["ag_lat"] += r["agent"]["latency"]

    new_summary = {
        "total_questions": total_q,
        "overall_accuracy": {
            "RAG": round(rag_acc, 1),
            "GraphRAG": round(gr_acc, 1),
            "Agent": round(ag_acc, 1)
        },
        "average_tokens": {
            "RAG": round(rag_avg_tokens, 1),
            "GraphRAG": round(gr_avg_tokens, 1),
            "Agent": round(ag_avg_tokens, 1)
        },
        "average_latency_s": {
            "RAG": round(rag_avg_lat, 2),
            "GraphRAG": round(gr_avg_lat, 2),
            "Agent": round(ag_avg_lat, 2)
        },
        "agent_average_steps": round(ag_avg_steps, 2),
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
                }
            }
            for qt, s in type_stats.items()
        }
    }

    # Save new comparison_15q.json
    with open(old_comp_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": new_summary,
            "questions": comparison_records
        }, f, indent=2, ensure_ascii=False)
    print(f"[Saved] Updated comparison_15q.json")

    # Save updated Markdown report
    md_lines = [
        "# 3-Pipeline Benchmark Report (15 Stratified Questions)",
        "",
        "This benchmark compares three distinct retrieval-augmented architectures on the same 15 questions from `eval_public.jsonl` (3 stratified across each of the 5 query types):",
        "1. **Pipeline 1 (RAG)**: Fixed top-k BM25 retrieval over document chunks.",
        "2. **Pipeline 2 (GraphRAG)**: Single-step structured Knowledge Graph retrieval + narrative chunk augmentation.",
        "3. **Pipeline 3 (Agentic GraphRAG)**: Autonomous orchestrator with dynamic planning, tool calling, and evidence evaluation.",
        "",
        "---",
        "",
        "## Summary Results",
        "",
        "| Pipeline | Overall Accuracy | Avg Tokens | Avg Latency (s) |",
        "| :--- | :---: | :---: | :---: |",
        f"| **RAG** | {rag_acc:.1f}% | {rag_avg_tokens:.0f} | {rag_avg_lat:.2f}s |",
        f"| **GraphRAG** | {gr_acc:.1f}% | {gr_avg_tokens:.0f} | {gr_avg_lat:.2f}s |",
        f"| **Agentic GraphRAG** | {ag_acc:.1f}% | {ag_avg_tokens:.0f} | {ag_avg_lat:.2f}s |",
        "",
        "### Accuracy by Query Type",
        "",
        "| Query Type | Questions | RAG Accuracy | GraphRAG Accuracy | Agentic Accuracy |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]
    for qt, s in sorted(new_summary["by_type"].items()):
        md_lines.append(f"| **{qt}** | {s['total']} | {s['accuracy']['RAG']:.1f}% | {s['accuracy']['GraphRAG']:.1f}% | {s['accuracy']['Agent']:.1f}% |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Detailed Question-by-Question Comparison Table",
        "",
        "| Question ID | Query Type | Gold Answer | RAG Correct? | GraphRAG Correct? | Agent Correct? | RAG Tokens | GraphRAG Tokens | Agent Tokens | RAG Latency | GraphRAG Latency | Agent Latency |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ])
    for r in comparison_records:
        gold_str = str(r["gold_answer"])
        rag_c = "✅" if r["rag"]["correct"] else "❌"
        gr_c = "✅" if r["graphrag"]["correct"] else "❌"
        ag_c = "✅" if r["agent"]["correct"] else "❌"
        md_lines.append(
            f"| `{r['question_id']}` | {r['query_type']} | `{gold_str}` | {rag_c} | {gr_c} | {ag_c} | "
            f"{r['rag']['tokens']} | {r['graphrag']['tokens']} | {r['agent']['tokens']} | "
            f"{r['rag']['latency']}s | {r['graphrag']['latency']}s | {r['agent']['latency']}s |"
        )

    md_path = WORKSPACE_ROOT / "comparison_15q.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[Saved] Updated comparison_15q.md")

    # Explicit comparison print
    print("\n" + "=" * 80)
    print("BENCHMARK COMPARISON: OLD vs NEW (AGENTIC PIPELINE)")
    print("=" * 80)
    old_ag_acc = old_summary.get("overall_accuracy", {}).get("Agent", 86.7)
    old_ag_tok = old_summary.get("average_tokens", {}).get("Agent", 6389.1)
    old_ag_lat = old_summary.get("average_latency_s", {}).get("Agent", 26.06)

    print(f"Agent Overall Accuracy: {old_ag_acc:.1f}%  ->  {ag_acc:.1f}%  (delta: {ag_acc - old_ag_acc:+.1f}%)")
    print(f"Agent Average Tokens:   {old_ag_tok:.0f}     ->  {ag_avg_tokens:.0f}     (delta: {ag_avg_tokens - old_ag_tok:+.0f} tokens)")
    print(f"Agent Average Latency:  {old_ag_lat:.2f}s    ->  {ag_avg_lat:.2f}s    (delta: {ag_avg_lat - old_ag_lat:+.2f}s)")
    print(f"Agent Average Steps:    (unlogged)  ->  {ag_avg_steps:.2f} steps")
    print("=" * 80)

if __name__ == "__main__":
    main()
