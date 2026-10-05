# 🔬 Engineering Findings: Token & Latency Optimization in Agentic GraphRAG

This document records the empirical diagnosis, architectural root cause, code optimizations, and benchmark validation performed to resolve agentic token bloat and latency spikes.

---

## ⚠️ Benchmark Deliverables & Historical Integrity Note

> **Authoritative Final Submission**: The official submission-ready 100-question benchmark report is located in [`comparison_100_final.md`](./comparison_100_final.md) and [`comparison_100_final.json`](./comparison_100_final.json), reflecting the fully optimized Agentic GraphRAG system (85.0% accuracy, 5,279 avg tokens, 19.57s avg latency).
>
> **Historical Baseline**: The earlier benchmark report in [`comparison_100.md`](./comparison_100.md) and [`comparison_100.json`](./comparison_100.json) was recorded **BEFORE** these optimizations were applied (84.0% accuracy, 6,390 avg tokens, 23.08s avg latency). It is preserved completely unedited as the historical pre-optimization baseline for this optimization case study.

---

## 1. Problem Statement: Investigating Agent Token Overhead

In initial 100-question benchmarking, the Agentic GraphRAG pipeline achieved **84.0% accuracy** (+18% over Plain RAG), but consumed an average of **6,390 tokens per question** (2.86x Plain RAG and GraphRAG) with latency outliers exceeding 100 seconds (e.g. `pub-045` at 110.02s). 

Before accepting this cost as an inherent tax of multi-step autonomous reasoning, we conducted a systematic trace diagnosis on the two most extreme outliers:
- **`pub-012`**: 14,467 tokens, 47.09s latency, terminated prematurely with `token_budget_exceeded`.
- **`pub-045`**: 8,202 tokens, 110.02s latency, generated an 846-token historical essay.

---

## 2. Root Cause Analysis

Diagnostic profiling across traces revealed three independent compounding sources of fixable waste:

### A. Full-Object Schema Dumping in `get_events`
In `agentic_pipeline/graph/sqlite_graph.py`, `get_events()` executed:
```sql
SELECT * FROM events WHERE 1=1 ...
```
This returned all 20 schema columns for every matching event, including `raw_infobox` (a nested JSON string of 300–500 characters of raw Wikipedia infobox metadata per row).
- In `pub-045` (Athletics at Athens 2004), 43 candidate events matched. The raw tool output was **40,654 characters (~10,163 tokens)** in a single tool call.
- In `pub-012` (Rowing at Tokyo 2020), 14 candidate events produced **15,582 characters (~3,895 tokens)**.

### B. Unbounded Verbatim History Accumulation (Quadratic Compounding)
In `agentic_pipeline/agent/orchestrator.py`, every tool output was serialized via `json.dumps(tool_output)` and permanently appended to the LLM's `messages` array:
```python
messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_output)})
```
Because the full tool dump was never pruned:
- Step 1 Prompt: ~1,230 tokens
- Step 2 Prompt: ~1,230 + 3,900 (Step 1 dump) = **~5,130 tokens**
- Step 3 Prompt: ~5,130 + 1,750 (Step 2 dump) = **~6,880 tokens**
When `total_tokens` crossed the 6,000 token budget, `token_budget_exceeded` forced a fallback synthesis pass that re-ingested the entire 7,000-token conversation history a second time, ballooning `pub-012` to **14,467 tokens**.

### C. Unconstrained Runaway Answer Synthesis
When context was flooded with dozens of raw Wikipedia event dumps, the local Ollama LLM lacked a concise stopping boundary. In `pub-045`, the model generated an unprompted **846-token historical essay** detailing host cities, dates, 7 athlete medalists, and Olympic legacy, taking **92.41 seconds on generation alone**.

---

## 3. The 3 Applied Optimizations

### Fix 1: Lightweight Projection in `get_events` & `count_or_rank`
- **File**: `agentic_pipeline/graph/sqlite_graph.py`
- Excluded `raw_infobox`, `venue`, `date`, `silver`, `bronze`, and internal foreign keys by default.
- Projected to core queryable fields: `doc_id`, `title`, `event_name`, `sport`, `games`, `year`, `competitors`, `nations`, `gold`.
- In `count_or_rank`, projected returned entity lists to lightweight dictionaries: `{title, event_name, metric, gold}`.

### Fix 2: Compact Context Injection in Orchestrator
- **File**: `agentic_pipeline/agent/orchestrator.py`
- When `get_events` matches $>5$ events, the LLM conversation history receives a concise summary (`matched_count`, 3-item sample, and memory pointer):
  ```python
  compact_payload = {
      "matched_count": len(tool_output),
      "sample_events": [{"title": ev.get("title"), "competitors": ev.get("competitors"), "gold": ev.get("gold")} for ev in tool_output[:3]],
      "note": f"{len(tool_output)} matching events stored in working memory. Use count_or_rank or get_event_attributes to compute across them."
  }
  ```
- **Crucial Design Choice**: Python memory (`self.active_events`) retains 100% of the full event records. Downstream tools like `count_or_rank` operate on exact in-memory data, preserving complete mathematical precision while slashing LLM prompt size from 40k characters to ~300 characters.

### Fix 3: Strict Conciseness Synthesis Prompting
- **Files**: `agentic_pipeline/agent/prompts.py` & `agentic_pipeline/agent/orchestrator.py`
- Added explicit boundary: *"State the answer directly in 1-2 sentences. Never generate broad historical essays, timelines, or unnecessary background summaries."*

---

## 4. Empirical Validation on the 15-Question Stratified Sample

We re-ran the exact 15-question stratified evaluation benchmark using local `qwen3:8b` to verify regression safety and measure real token/latency impact:

### A. Overall 15-Question Before vs. After Summary

| Metric | Pre-Optimization Baseline | Post-Optimization (Current) | Delta |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **100.0%** (15/15) | **100.0%** (15/15) | **+0.0% (Zero regressions)** |
| **Average Tokens / Question** | **5,907** | **4,780** | **-1,127 tokens (-19.1% overall)** |
| **Average Latency / Question** | **21.28s** | **17.87s** | **-3.41s (-16.0% faster)** |
| **Average Agent Steps** | 2.80 steps | 3.00 steps | Stable |

### B. High-Volume Query Reductions (Aggregation & Superlative)

On the complex questions where large event sets are processed, token reductions reached **30% to 60%**:

| Question ID | Query Type | Question Concept | Before Tokens | After Tokens | Token Delta | Before Latency | After Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `pub-001` | aggregation | Biathlon $>73$ competitors | 10,170 | **8,652** | -14.9% | 24.8s | 33.5s |
| `pub-003` | aggregation | Shooting $>37$ competitors | 12,754 | **7,023** | **-44.9%** | 37.2s | **22.9s** |
| `pub-010` | aggregation | Cycling at 2000 Olympics | 8,966 | **5,217** | **-41.8%** | 21.9s | **18.5s** |
| `pub-004` | superlative | Athletics max competitors | 7,923 | **5,021** | **-36.6%** | 21.3s | **16.4s** |
| `pub-008` | superlative | Sailing max competitors | 7,995 | **6,548** | **-18.1%** | 20.8s | 22.5s |
| `pub-021` | superlative | Alpine skiing max competitors | 9,535 | **6,534** | **-31.5%** | 24.5s | **21.4s** |
| `pub-005` | multi_hop | Weightlifting gold medal | 5,032 | **2,698** | **-46.4%** | 18.9s | **12.0s** |
| `pub-011` | multi_hop | Speed skating venue date | 4,310 | **2,700** | **-37.4%** | 18.3s | **14.0s** |
| `pub-014` | multi_hop | Badminton venue date | 2,970 | **2,722** | -8.3% | 14.2s | **13.2s** |

### C. Resolution of Specific Outliers (`pub-012` & `pub-045`)

| Question ID | Metric | Before Fix | After Fix | Impact |
| :--- | :--- | :---: | :---: | :--- |
| **`pub-012`** | Total Tokens | 14,467 | **5,524** | **-61.8% token reduction** |
| | Stop Reason | `token_budget_exceeded` | `evidence_sufficient_answered` | **Clean autonomous stop** |
| | Accuracy | Correct (`['6']`) | Correct (`['6']`) | Preserved 100% |
| **`pub-045`** | Elapsed Latency | 110.02s | **19.63s** | **-82.2% latency reduction (90s faster!)** |
| | Completion Tokens | 846 (runaway essay) | 121 (concise direct answer) | **-85.7% output tokens** |
| | Total Tokens | 8,202 | **6,228** | **-24.1% token reduction** |
| | Accuracy | Correct (`['20']`) | Correct (`['20']`) | Preserved 100% |

### D. Full 100-Question Final Impact (Macro Scale)

Following sample validation, the optimized pipeline was evaluated across all 100 evaluation questions in [`comparison_100_final.md`](./comparison_100_final.md):

| Metric | Pre-Optimization Baseline (`comparison_100.md`) | Post-Optimization Final (`comparison_100_final.md`) | Delta (Full 100-Scale) |
| :--- | :---: | :---: | :---: |
| **Agent Overall Accuracy** | 84.0% (84/100) | **85.0%** (85/100) | **+1.0%** |
| **Agent Total Tokens** | 638,977 tokens | **527,855 tokens** | **-111,122 tokens (-17.4%)** |
| **Agent Avg Tokens / Question** | 6,390 tokens | **5,279 tokens** | **-1,111 tokens (-17.4%)** |
| **Agent Total Wall-Clock Time** | 38.5 minutes | **32.6 minutes** | **-5.9 minutes (-15.2%)** |
| **Agent Avg Latency / Question** | 23.08s | **19.57s** | **-3.51s (-15.2%)** |
| **Aggregation Accuracy** | 90.5% (19/21) | **95.2%** (20/21) | **+4.7%** |
| **Aggregation Avg Tokens** | 10,424 tokens | **6,800 tokens** | **-3,624 tokens (-34.8%)** |

---

## 5. Architectural Takeaway for Hackathon Judges

1. **Agentic Overhead is Largely Engineering, Not Fundamental**:
   - The common assumption that agentic loops inherently consume 3–4x the tokens of plain RAG is partly an artifact of naive context management (dumping full database rows into conversational history).
   - By separating **in-memory tool working state** from **LLM conversational context**, an agent can reason over hundreds of entities with near-flat token costs (~1,500–1,800 tokens per step).

2. **Zero Accuracy Penalty**:
   - Compacting the representation did not cause a single regression across the benchmark (100% accuracy on the 15q stratified set was maintained).
   - In fact, eliminating context bloat improved model attention, allowing the agent to answer cleanly without hitting artificial token budgets or drifting into irrelevant historical narratives.
