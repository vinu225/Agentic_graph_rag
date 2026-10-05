"""Benchmark retrieval recall (BM25 vs Vector vs Hybrid RRF) across all 100 public evaluation questions.

Evaluates:
- Recall@5, Recall@8, Recall@10 (Hit@k)
- Frac@k (fraction of all gold docs retrieved)
- Breakdown by query type: aggregation, lookup, multi_hop, superlative, temporal
"""

import sys
import os
import json
import time
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from rag_only_pipeline.config import EVAL_PUBLIC_PATH
from rag_only_pipeline.retrieval.bm25_index import BM25Index
from rag_only_pipeline.retrieval.vector_index import VectorIndex
from rag_only_pipeline.retrieval.hybrid_retriever import HybridRetriever


def load_eval_questions() -> List[Dict[str, Any]]:
    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate_retrieval():
    print("=" * 80)
    print("EVALUATING RETRIEVAL RECALL: BM25 vs VECTOR vs HYBRID (RRF)")
    print("=" * 80)

    # 1. Initialize or build Vector Index
    v_idx = VectorIndex()
    if not v_idx.load():
        print("[VectorIndex] Not found on disk. Building FAISS index over all 20,100 chunks...")
        t0 = time.time()
        v_idx.build(batch_size=128)
        print(f"[VectorIndex] Built and saved in {time.time() - t0:.2f}s.")
    else:
        print(f"[VectorIndex] Loaded existing FAISS index with {v_idx.index.ntotal} vectors.")

    # 2. Initialize BM25 and Hybrid
    bm25 = BM25Index()
    hybrid = HybridRetriever(bm25_index=bm25, vector_index=v_idx)

    questions = load_eval_questions()
    print(f"Loaded {len(questions)} evaluation questions from {EVAL_PUBLIC_PATH.name}\n")

    # Metrics containers
    # Methods: 'bm25', 'vector', 'hybrid'
    methods = ["bm25", "vector", "hybrid"]
    k_vals = [5, 8, 10]

    hits = {m: {k: 0 for k in k_vals} for m in methods}
    frac_recalls = {m: {k: 0.0 for k in k_vals} for m in methods}

    type_stats = defaultdict(lambda: {
        m: {k: {"hits": 0, "total": 0, "frac_sum": 0.0} for k in k_vals}
        for m in methods
    })

    deltas_at_8 = []

    t_start = time.time()
    for idx, q_item in enumerate(questions, 1):
        qid = q_item["qid"]
        qtype = q_item.get("qtype", "unknown")
        qtext = q_item["question"]
        gold_docs: Set[str] = set(q_item.get("gold_doc_ids", []))

        if not gold_docs:
            continue

        # Retrieve top 10 for each method
        bm25_res = bm25.search(qtext, top_k=10)
        vec_res = v_idx.search(qtext, top_k=10)
        hyb_res = hybrid.search(qtext, top_k=10)

        retrieved_docs = {
            "bm25": [c["doc_id"] for c in bm25_res],
            "vector": [c["doc_id"] for c in vec_res],
            "hybrid": [c["doc_id"] for c in hyb_res],
        }

        # Check hits and fraction recall for each k
        b8_hit = any(d in gold_docs for d in retrieved_docs["bm25"][:8])
        h8_hit = any(d in gold_docs for d in retrieved_docs["hybrid"][:8])
        v8_hit = any(d in gold_docs for d in retrieved_docs["vector"][:8])

        if b8_hit != h8_hit:
            deltas_at_8.append({
                "qid": qid,
                "qtype": qtype,
                "question": qtext,
                "bm25_hit": b8_hit,
                "hybrid_hit": h8_hit,
                "vector_hit": v8_hit,
                "gold_docs": list(gold_docs)
            })

        for m in methods:
            for k in k_vals:
                top_k_docs = set(retrieved_docs[m][:k])
                matched = top_k_docs.intersection(gold_docs)

                is_hit = len(matched) > 0
                frac = len(matched) / len(gold_docs)

                if is_hit:
                    hits[m][k] += 1
                frac_recalls[m][k] += frac

                type_stats[qtype][m][k]["total"] += 1
                if is_hit:
                    type_stats[qtype][m][k]["hits"] += 1
                type_stats[qtype][m][k]["frac_sum"] += frac

        if idx % 20 == 0 or idx == len(questions):
            print(f"  [Evaluation Progress] {idx}/{len(questions)} questions evaluated...")

    total_q = len(questions)
    elapsed = time.time() - t_start

    print("\n" + "=" * 80)
    print(f"OVERALL RETRIEVAL RECALL RESULTS (Total Questions: {total_q}, Time: {elapsed:.2f}s)")
    print("=" * 80)

    print(f"\n{'Metric':<25} | {'BM25-Only':<15} | {'Vector-Only':<15} | {'Hybrid (RRF)':<15} | {'Hybrid vs BM25 Delta':<20}")
    print("-" * 100)

    for k in k_vals:
        bm25_hit_rate = (hits["bm25"][k] / total_q) * 100
        vec_hit_rate = (hits["vector"][k] / total_q) * 100
        hyb_hit_rate = (hits["hybrid"][k] / total_q) * 100
        delta = hyb_hit_rate - bm25_hit_rate
        sign = "+" if delta >= 0 else ""
        print(f"Hit@{k:<21} | {bm25_hit_rate:>6.1f}% ({hits['bm25'][k]:>2}/{total_q}) | {vec_hit_rate:>6.1f}% ({hits['vector'][k]:>2}/{total_q}) | {hyb_hit_rate:>6.1f}% ({hits['hybrid'][k]:>2}/{total_q}) | {sign}{delta:>5.1f}%")

    print("-" * 100)
    for k in k_vals:
        bm25_frac = (frac_recalls["bm25"][k] / total_q) * 100
        vec_frac = (frac_recalls["vector"][k] / total_q) * 100
        hyb_frac = (frac_recalls["hybrid"][k] / total_q) * 100
        delta = hyb_frac - bm25_frac
        sign = "+" if delta >= 0 else ""
        print(f"Frac@{k} (All Gold Docs) | {bm25_frac:>6.1f}%         | {vec_frac:>6.1f}%         | {hyb_frac:>6.1f}%         | {sign}{delta:>5.1f}%")

    # Breakdown by query type at k=8
    print("\n" + "=" * 80)
    print("RECALL@8 BREAKDOWN BY QUERY TYPE (BM25 vs HYBRID)")
    print("=" * 80)

    print(f"\n{'Query Type':<16} | {'Count':<6} | {'BM25 Hit@8':<14} | {'Vector Hit@8':<14} | {'Hybrid Hit@8':<14} | {'Hybrid vs BM25 Delta':<20}")
    print("-" * 95)

    for qtype in sorted(type_stats.keys()):
        cnt = type_stats[qtype]["bm25"][8]["total"]
        b_hits = type_stats[qtype]["bm25"][8]["hits"]
        v_hits = type_stats[qtype]["vector"][8]["hits"]
        h_hits = type_stats[qtype]["hybrid"][8]["hits"]

        b_pct = (b_hits / cnt) * 100 if cnt else 0.0
        v_pct = (v_hits / cnt) * 100 if cnt else 0.0
        h_pct = (h_hits / cnt) * 100 if cnt else 0.0
        delta = h_pct - b_pct
        sign = "+" if delta >= 0 else ""

        print(f"{qtype:<16} | {cnt:<6} | {b_pct:>5.1f}% ({b_hits:>2}/{cnt:<2}) | {v_pct:>5.1f}% ({v_hits:>2}/{cnt:<2}) | {h_pct:>5.1f}% ({h_hits:>2}/{cnt:<2}) | {sign}{delta:>5.1f}%")

    if deltas_at_8:
        print("\n" + "=" * 80)
        print(f"DISCREPANCY QUESTIONS AT k=8 ({len(deltas_at_8)} questions where BM25 != Hybrid):")
        print("=" * 80)
        for d in deltas_at_8:
            status = "IMPROVED (Hybrid won)" if d["hybrid_hit"] else "DEGRADED (BM25 won)"
            print(f"- [{d['qid']}] ({d['qtype']}) -> {status}")
            print(f"  Question: {d['question']}")
            print(f"  BM25 Hit: {d['bm25_hit']} | Hybrid Hit: {d['hybrid_hit']} | Vector Hit: {d['vector_hit']}")
            print()
    else:
        print("\n[Notice] No discrepancies at k=8: BM25 and Hybrid achieved identical Hit@8 across all 100 questions.")


if __name__ == "__main__":
    evaluate_retrieval()
