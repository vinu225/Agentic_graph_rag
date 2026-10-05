# 3-Pipeline Comparative Benchmark Report (50 Hidden Questions - Submission Deliverable)

This report documents the fresh evaluation across all 50 hidden questions from `eval_hidden.jsonl`.
It benchmarks **Pipeline 1 (Plain RAG)**, **Pipeline 2 (GraphRAG)**, and **Pipeline 3 (Optimized Agentic GraphRAG)**.
> **Note on Ground Truth**: Ground truth answers for these 50 hidden questions are held out by TigerGraph for official grading.

---

## 1. Summary Results (50 Hidden Questions)

| Pipeline | Questions Answered | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pipeline 1: Plain RAG** | **50 / 50** | 2245 | 112,272 | 8.99s | 7.5m (449.4s) | N/A (1 step) |
| **Pipeline 2: GraphRAG** | **50 / 50** | 2305 | 115,240 | 7.74s | 6.4m (386.8s) | N/A (1 step) |
| **Pipeline 3: Optimized Agent** | **50 / 50** | **5716** | **285,814** | **19.89s** | **16.6m (994.3s)** | **3.58 steps** |

---

## 2. Resource Consumption by Query Type

| Query Type | Questions | Plain RAG Avg Tokens | GraphRAG Avg Tokens | Optimized Agent Avg Tokens | Agent Avg Latency | Agent Avg Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **aggregation** | 15 | 1949 | 2175 | **6550** | 21.33s | 3.73 |
| **lookup** | 7 | 2510 | 2888 | **5385** | 20.45s | 3.71 |
| **multi_hop** | 10 | 2526 | 2280 | **5111** | 19.91s | 3.30 |
| **superlative** | 10 | 1959 | 2775 | **6437** | 20.42s | 3.90 |
| **temporal** | 8 | 2578 | 1481 | **4300** | 15.99s | 3.12 |

---

## 3. Question-by-Question Detailed Results (All 50 Hidden Questions)

| ID | Type | Plain RAG Answer | GraphRAG Answer | Agentic GraphRAG Answer | RAG Tok | GR Tok | Agent Tok | Agent Steps |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `eval-001` | multi_hop | `The gold medal in the event held at t...` | `Li Ting and Sun Tiantian [Q942805#c0].` | `The gold medal in the Women's doubles...` | 2706 | 1228 | 4563 | 3 |
| `eval-002` | lookup | `29 nations competed in Fencing at the...` | `33 [Q5443142#c0]` | `The number of nations that competed i...` | 3046 | 2750 | 4208 | 3 |
| `eval-003` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 6.` | `According to the provided corpus, the...` | 1894 | 2411 | 5449 | 3 |
| `eval-004` | multi_hop | `The gold medal in the event held at S...` | `The gold medalist in the event held a...` | `The gold medal in the event held at t...` | 2348 | 2210 | 2875 | 2 |
| `eval-005` | superlative | `The sailing event at the 2016 Summer ...` | `The sailing event at the 2016 Summer ...` | `The sailing event at the 2016 Summer ...` | 1897 | 3367 | 6538 | 4 |
| `eval-006` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 3` | `According to the provided corpus, the...` | 1985 | 2281 | 6860 | 4 |

Full details available in [`optimized_comparison_50_hidden.md`](../optimized_comparison_50_hidden.md).
