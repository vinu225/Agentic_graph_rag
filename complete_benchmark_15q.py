"""Complete the remaining questions for the 15-question benchmark.
Resumes from existing results in results_graphrag.jsonl and results_agentic.jsonl,
runs only the missing questions, and generates comparison_15q.json and comparison_15q.md.
"""

import sys
import json
import time
import re
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
from graphrag_pipeline.pipeline import GraphRAGPipeline

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

def load_rag_results():
    rag_file = WORKSPACE_ROOT / "rag_only_pipeline" / "results_rag.jsonl"
    results = {}
    if rag_file.exists():
        with open(rag_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    results[item["question_id"]] = item
    return results

def load_existing_jsonl(path: Path) -> Dict[str, Dict[str, Any]]:
    results = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    qid = item.get("question_id")
                    if qid:
                        results[qid] = item
    return results

def main():
    print("=" * 80)
    print("RESUMING 3-PIPELINE COMPARISON BENCHMARK (15 STRATIFIED QUESTIONS)")
    print("=" * 80)

    questions = load_selected_questions()
    rag_data = load_rag_results()
    
    gr_path = WORKSPACE_ROOT / "results_graphrag.jsonl"
    ag_path = WORKSPACE_ROOT / "results_agentic.jsonl"
    
    existing_gr = load_existing_jsonl(gr_path)
    existing_ag = load_existing_jsonl(ag_path)

    print(f"Loaded {len(questions)} test questions.")
    print(f"Pre-existing GraphRAG results: {len(existing_gr)}")
    print(f"Pre-existing Agentic results: {len(existing_ag)}")

    missing_gr = [q for q in questions if q["qid"] not in existing_gr]
    missing_ag = [q for q in questions if q["qid"] not in existing_ag]
    print(f"Missing GraphRAG questions: {[q['qid'] for q in missing_gr]}")
    print(f"Missing Agentic questions: {[q['qid'] for q in missing_ag]}")

    shared_llm = None
    graphrag_pipe = None
    orchestrator = None
    agent_graph = None

    if missing_gr or missing_ag:
        print(f"\nInitializing Ollama model ({DEFAULT_OLLAMA_MODEL})...")
        shared_llm = OllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
        set_active_llm(shared_llm)

    if missing_gr:
        graphrag_pipe = GraphRAGPipeline(model_name=DEFAULT_OLLAMA_MODEL, llm=shared_llm)
        with open(gr_path, "a", encoding="utf-8") as fg:
            for q_item in missing_gr:
                qid = q_item["qid"]
                qtext = q_item["question"]
                print(f"[GraphRAG] Running {qid}...")
                t0 = time.time()
                try:
                    res = graphrag_pipe.run(qtext, question_id=qid)
                    res_dict = res.to_dict()
                except Exception as e:
                    print(f"  GraphRAG error on {qid}: {e}")
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
        graphrag_pipe.close()

    if missing_ag:
        agent_graph = SQLiteGraph(str(SQLITE_DB_PATH))
        agent_tools = ToolSuite(agent_graph)
        orchestrator = AgenticOrchestrator(agent_tools)
        with open(ag_path, "a", encoding="utf-8") as fa:
            for q_item in missing_ag:
                qid = q_item["qid"]
                qtext = q_item["question"]
                print(f"[Agentic] Running {qid}...")
                t0 = time.time()
                try:
                    res = orchestrator.run(qtext)
                    ag_dict = {
                        "question_id": qid,
                        "answer": res.answer,
                        "total_tokens": res.total_tokens,
                        "prompt_tokens": res.prompt_tokens,
                        "completion_tokens": res.completion_tokens,
                        "total_steps": res.total_steps,
                        "elapsed_time_s": res.elapsed_time_s,
                        "stopped_reason": res.stopped_reason
                    }
                except Exception as e:
                    print(f"  Agentic error on {qid}: {e}")
                    ag_dict = {
                        "question_id": qid,
                        "answer": f"Error: {e}",
                        "total_tokens": 0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_steps": 0,
                        "elapsed_time_s": round(time.time() - t0, 3),
                        "stopped_reason": f"error: {e}"
                    }
                fa.write(json.dumps(ag_dict) + "\n")
                fa.flush()
                existing_ag[qid] = ag_dict
        agent_graph.close()

    # Now assemble the complete comparison records for all 15 questions
    comparison_records = []
    for q_item in questions:
        qid = q_item["qid"]
        qtype = q_item["qtype"]
        question = q_item["question"]
        gold_answers = q_item["answer"]

        # RAG
        rag_res = rag_data.get(qid, {})
        rag_ans = rag_res.get("answer", "not evaluated")
        rag_tokens = rag_res.get("total_tokens", 0)
        rag_latency = rag_res.get("elapsed_time_s", 0.0)
        rag_corr = evaluate_correctness(rag_ans, gold_answers)

        # GraphRAG
        gr_res = existing_gr.get(qid, {})
        gr_ans = gr_res.get("answer", "not evaluated")
        gr_tokens = gr_res.get("total_tokens", 0)
        gr_latency = gr_res.get("elapsed_time_s", 0.0)
        gr_corr = evaluate_correctness(gr_ans, gold_answers)

        # Agent
        ag_res = existing_ag.get(qid, {})
        ag_ans = ag_res.get("answer", "not evaluated")
        ag_tokens = ag_res.get("total_tokens", 0)
        ag_latency = ag_res.get("elapsed_time_s", 0.0)
        ag_corr = evaluate_correctness(ag_ans, gold_answers)

        record = {
            "question_id": qid,
            "query_type": qtype,
            "question": question,
            "gold_answer": gold_answers,
            "rag": {
                "answer": rag_ans,
                "correct": rag_corr,
                "tokens": rag_tokens,
                "latency": round(rag_latency, 3)
            },
            "graphrag": {
                "answer": gr_ans,
                "correct": gr_corr,
                "tokens": gr_tokens,
                "latency": round(gr_latency, 3)
            },
            "agent": {
                "answer": ag_ans,
                "correct": ag_corr,
                "tokens": ag_tokens,
                "latency": round(ag_latency, 3),
                "total_steps": ag_res.get("total_steps", 0),
                "stopped_reason": ag_res.get("stopped_reason", "")
            }
        }
        comparison_records.append(record)

    total_q = len(comparison_records)
    rag_acc = sum(1 for r in comparison_records if r["rag"]["correct"]) / total_q * 100
    gr_acc = sum(1 for r in comparison_records if r["graphrag"]["correct"]) / total_q * 100
    ag_acc = sum(1 for r in comparison_records if r["agent"]["correct"]) / total_q * 100

    rag_avg_tokens = sum(r["rag"]["tokens"] for r in comparison_records) / total_q
    gr_avg_tokens = sum(r["graphrag"]["tokens"] for r in comparison_records) / total_q
    ag_avg_tokens = sum(r["agent"]["tokens"] for r in comparison_records) / total_q

    rag_avg_lat = sum(r["rag"]["latency"] for r in comparison_records) / total_q
    gr_avg_lat = sum(r["graphrag"]["latency"] for r in comparison_records) / total_q
    ag_avg_lat = sum(r["agent"]["latency"] for r in comparison_records) / total_q

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

    summary_data = {
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

    # Save comparison_15q.json
    json_path = WORKSPACE_ROOT / "comparison_15q.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary_data,
            "questions": comparison_records
        }, f, indent=2, ensure_ascii=False)
    print(f"[Saved] Detailed JSON report: {json_path}")

    # Build Markdown Report
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

    for qt, s in sorted(summary_data["by_type"].items()):
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
    print(f"[Saved] Markdown report: {md_path}")

    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETED")
    print("=" * 80)
    print(f"Overall Accuracy:  RAG: {rag_acc:.1f}% | GraphRAG: {gr_acc:.1f}% | Agent: {ag_acc:.1f}%")
    print(f"Average Tokens:    RAG: {rag_avg_tokens:.0f} | GraphRAG: {gr_avg_tokens:.0f} | Agent: {ag_avg_tokens:.0f}")
    print(f"Average Latency:   RAG: {rag_avg_lat:.2f}s | GraphRAG: {gr_avg_lat:.2f}s | Agent: {ag_avg_lat:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    main()
