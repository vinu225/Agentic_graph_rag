# 3-Pipeline Benchmark Report (15 Stratified Questions)

This benchmark compares three distinct retrieval-augmented architectures on the same 15 questions from `eval_public.jsonl` (3 stratified across each of the 5 query types):
1. **Pipeline 1 (RAG)**: Fixed top-k BM25 retrieval over document chunks.
2. **Pipeline 2 (GraphRAG)**: Single-step structured Knowledge Graph retrieval + narrative chunk augmentation.
3. **Pipeline 3 (Agentic GraphRAG)**: Autonomous orchestrator with dynamic planning, tool calling, and evidence evaluation.

---

## Summary Results

| Pipeline | Overall Accuracy | Avg Tokens | Avg Latency (s) |
| :--- | :---: | :---: | :---: |
| **RAG** | 66.7% | 2161 | 10.97s |
| **GraphRAG** | 93.3% | 2172 | 15.33s |
| **Agentic GraphRAG** | 100.0% | 5907 | 21.28s |

### Accuracy by Query Type

| Query Type | Questions | RAG Accuracy | GraphRAG Accuracy | Agentic Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 3 | 0.0% | 66.7% | 100.0% |
| **lookup** | 3 | 100.0% | 100.0% | 100.0% |
| **multi_hop** | 3 | 100.0% | 100.0% | 100.0% |
| **superlative** | 3 | 66.7% | 100.0% | 100.0% |
| **temporal** | 3 | 66.7% | 100.0% | 100.0% |

---

## Detailed Question-by-Question Comparison Table

| Question ID | Query Type | Gold Answer | RAG Correct? | GraphRAG Correct? | Agent Correct? | RAG Tokens | GraphRAG Tokens | Agent Tokens | RAG Latency | GraphRAG Latency | Agent Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pub-001` | aggregation | `['5']` | ❌ | ✅ | ✅ | 1969 | 2010 | 10170 | 24.045s | 10.158s | 24.817s |
| `pub-003` | aggregation | `['8']` | ❌ | ✅ | ✅ | 2167 | 2655 | 9203 | 26.532s | 26.958s | 60.791s |
| `pub-010` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1915 | 1709 | 8966 | 19.206s | 7.03s | 29.512s |
| `pub-002` | temporal | `['Chen Ding']` | ✅ | ✅ | ✅ | 1944 | 1657 | 4337 | 8.51s | 7.755s | 16.83s |
| `pub-006` | temporal | `['Rafaela Silva']` | ❌ | ✅ | ✅ | 2715 | 1565 | 4353 | 9.345s | 6.761s | 16.889s |
| `pub-007` | temporal | `['Renaud Lavillenie']` | ✅ | ✅ | ✅ | 2651 | 2046 | 7294 | 9.907s | 7.36s | 24.841s |
| `pub-004` | superlative | `["Athletics at the 2008 Summer Olympics – Men's marathon"]` | ❌ | ✅ | ✅ | 2644 | 3332 | 7901 | 5.688s | 13.175s | 19.856s |
| `pub-008` | superlative | `['Sailing at the 2000 Summer Olympics – Soling']` | ✅ | ✅ | ✅ | 1868 | 1980 | 7995 | 8.088s | 40.173s | 21.597s |
| `pub-021` | superlative | `["Alpine skiing at the 1988 Winter Olympics – Men's giant slalom"]` | ✅ | ✅ | ✅ | 1908 | 2727 | 9535 | 7.818s | 13.705s | 26.079s |
| `pub-005` | multi_hop | `['Naim Süleymanoğlu']` | ✅ | ✅ | ✅ | 1903 | 1006 | 2924 | 8.122s | 6.232s | 13.27s |
| `pub-011` | multi_hop | `['Martina Sáblíková']` | ✅ | ✅ | ✅ | 2101 | 1438 | 4310 | 8.5s | 7.424s | 18.156s |
| `pub-014` | multi_hop | `['Carolina Marín']` | ✅ | ✅ | ✅ | 2243 | 1175 | 2970 | 10.361s | 53.534s | 14.259s |
| `pub-009` | lookup | `['26']` | ✅ | ✅ | ✅ | 2378 | 3327 | 2869 | 6.944s | 12.169s | 10.453s |
| `pub-025` | lookup | `['23']` | ✅ | ✅ | ✅ | 2230 | 3218 | 2878 | 5.942s | 10.241s | 10.749s |
| `pub-029` | lookup | `['28']` | ✅ | ✅ | ✅ | 1773 | 2737 | 2898 | 5.47s | 7.256s | 11.102s |