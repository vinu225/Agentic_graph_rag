# 50 Hidden Evaluation Questions — Benchmark Summary

This report documents the benchmark execution of all 3 pipelines across the **50 hidden evaluation questions** (`eval_hidden.jsonl`) for TigerGraph hackathon submission.

Ground truth is held out by TigerGraph for official evaluation. All pipelines were evaluated using their validated current implementations.

---

## 1. Execution & Completeness Overview

| Pipeline | Questions Answered | Total Tokens | Mean Tokens/Q | Total Time (s) | Mean Latency (s) | Total Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Plain RAG** | 50 / 50 | 112,272 | 2245.4 | 464.96s | 9.30s | N/A |
| **GraphRAG** | 50 / 50 | 115,240 | 2304.8 | 397.66s | 7.95s | N/A |
| **Agentic GraphRAG** | 50 / 50 | 285,814 | 5716.3 | 1006.50s | 20.13s | 179 |

---

## 2. Integrity & Validation Audit

- **Total Rows Generated:** 150 / 150 rows.
- **Malformed JSON Lines:** 0
- **Missing Required Fields:** 0
- **Agent Trace Compliance:** 100% of Agent records contain detailed step-by-step investigation traces including actions, tools, arguments, durations, and token counts.
- **Anomalies / Errors flagged:** 0

---

## 3. Submission Artifacts

- [results_rag_hidden50.jsonl](file:///C:/LATEST/RAG/Agentic_graph_rag/results/results_rag_hidden50.jsonl)
- [results_graphrag_hidden50.jsonl](file:///C:/LATEST/RAG/Agentic_graph_rag/results/results_graphrag_hidden50.jsonl)
- [results_agent_hidden50.jsonl](file:///C:/LATEST/RAG/Agentic_graph_rag/results/results_agent_hidden50.jsonl)
