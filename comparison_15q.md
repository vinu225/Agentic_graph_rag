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
| **Agentic GraphRAG** | 100.0% | 4780 | 17.87s |

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
| `pub-001` | aggregation | `['5']` | ❌ | ✅ | ✅ | 1969 | 2010 | 8652 | 24.045s | 10.158s | 33.537s |
| `pub-003` | aggregation | `['8']` | ❌ | ✅ | ✅ | 2167 | 2655 | 7023 | 26.532s | 26.958s | 22.953s |
| `pub-010` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1915 | 1709 | 5217 | 19.206s | 7.03s | 18.458s |
| `pub-002` | temporal | `['Chen Ding']` | ✅ | ✅ | ✅ | 1944 | 1657 | 4134 | 8.51s | 7.755s | 16.349s |
| `pub-006` | temporal | `['Rafaela Silva']` | ❌ | ✅ | ✅ | 2715 | 1565 | 4124 | 9.345s | 6.761s | 15.605s |
| `pub-007` | temporal | `['Renaud Lavillenie']` | ✅ | ✅ | ✅ | 2651 | 2046 | 6261 | 9.907s | 7.36s | 21.749s |
| `pub-004` | superlative | `["Athletics at the 2008 Summer Olympics – Men's marathon"]` | ❌ | ✅ | ✅ | 2644 | 3332 | 5021 | 5.688s | 13.175s | 16.401s |
| `pub-008` | superlative | `['Sailing at the 2000 Summer Olympics – Soling']` | ✅ | ✅ | ✅ | 1868 | 1980 | 6548 | 8.088s | 40.173s | 22.501s |
| `pub-021` | superlative | `["Alpine skiing at the 1988 Winter Olympics – Men's giant slalom"]` | ✅ | ✅ | ✅ | 1908 | 2727 | 6534 | 7.818s | 13.705s | 21.4s |
| `pub-005` | multi_hop | `['Naim Süleymanoğlu']` | ✅ | ✅ | ✅ | 1903 | 1006 | 2698 | 8.122s | 6.232s | 12.012s |
| `pub-011` | multi_hop | `['Martina Sáblíková']` | ✅ | ✅ | ✅ | 2101 | 1438 | 2700 | 8.5s | 7.424s | 14.02s |
| `pub-014` | multi_hop | `['Carolina Marín']` | ✅ | ✅ | ✅ | 2243 | 1175 | 2722 | 10.361s | 53.534s | 13.233s |
| `pub-009` | lookup | `['26']` | ✅ | ✅ | ✅ | 2378 | 3327 | 2901 | 6.944s | 12.169s | 10.909s |
| `pub-025` | lookup | `['23']` | ✅ | ✅ | ✅ | 2230 | 3218 | 4238 | 5.942s | 10.241s | 17.742s |
| `pub-029` | lookup | `['28']` | ✅ | ✅ | ✅ | 1773 | 2737 | 2930 | 5.47s | 7.256s | 11.198s |