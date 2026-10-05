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
| `eval-007` | temporal | `The gold medal in the men's heavyweig...` | `Oleksandr Usyk [Q326384#c0].` | `The gold medal in the men's heavyweig...` | 2134 | 1331 | 4098 | 3 |
| `eval-008` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 1804 | 1836 | 6781 | 4 |
| `eval-009` | superlative | `The sailing event at the 2004 Summer ...` | `The sailing event at the 2004 Summer ...` | `The sailing event at the 2004 Summer ...` | 1908 | 2453 | 6515 | 4 |
| `eval-010` | lookup | `32 [Q10497009#c0]` | `The number of nations that competed i...` | `The Flyweight boxing event at the 199...` | 1752 | 2485 | 4362 | 3 |
| `eval-011` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 2033 | 1928 | 6813 | 4 |
| `eval-012` | lookup | `32 [Q25991452#c0]` | `32 [Q25991452#c0].` | `The number of nations that competed i...` | 1938 | 3163 | 2943 | 2 |
| `eval-013` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 5.` | `According to the provided corpus, the...` | 1894 | 2285 | 5352 | 3 |
| `eval-014` | multi_hop | `Michaela Dorfmeister won the gold med...` | `None of the provided events were held...` | `The gold medal in the Men's individua...` | 2159 | 3165 | 6792 | 4 |
| `eval-015` | lookup | `35 [Q26219858#c0]` | `The number of nations that competed i...` | `The number of nations that competed i...` | 2907 | 2871 | 7378 | 5 |
| `eval-016` | lookup | `22 [Q848278#c0].` | `The provided context does not include...` | `The number of nations that competed i...` | 2051 | 3204 | 4203 | 3 |
| `eval-017` | multi_hop | `The gold medal in the event held at E...` | `The gold medalist in the event held a...` | `The gold medal in the event held at E...` | 2122 | 3360 | 2699 | 2 |
| `eval-018` | multi_hop | `not found in corpus` | `Sara Kolak [Q26234144#c0].` | `The gold medal in the event held at t...` | 3055 | 1472 | 6087 | 4 |
| `eval-019` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: Total count...` | `According to the provided corpus, the...` | 2043 | 1559 | 6735 | 4 |
| `eval-020` | multi_hop | `The gold medal in the event held at R...` | `Jin Jong-oh [Q2353475#c0].` | `The gold medal in the event held at R...` | 2081 | 1373 | 5989 | 4 |
| `eval-021` | temporal | `The gold medal in the men's 200 metre...` | `Tyler Clary [Q2071160#c0].` | `The gold medal in the men's 200 metre...` | 3145 | 2293 | 4151 | 3 |
| `eval-022` | lookup | `40 [Q15055036#c0]` | `The number of nations that competed i...` | `At the 2014 Winter Olympics, 40 natio...` | 2851 | 3069 | 7325 | 5 |
| `eval-023` | aggregation | `not found in corpus` | `GRAPH AGGREGATION RESULT: 6.` | `According to the provided corpus, the...` | 1845 | 2136 | 6970 | 4 |
| `eval-024` | superlative | `The cross-country skiing event at the...` | `The cross-country skiing event at the...` | `The cross-country skiing event at the...` | 2096 | 2305 | 6672 | 4 |
| `eval-025` | superlative | `The rowing event at the 2016 Summer O...` | `The rowing event at the 2016 Summer O...` | `The rowing event at the 2016 Summer O...` | 1984 | 3149 | 6677 | 4 |
| `eval-026` | lookup | `22 nations competed in Fencing at the...` | `The number of nations that competed i...` | `The number of nations that competed i...` | 3023 | 2676 | 7279 | 5 |
| `eval-027` | superlative | `The cycling event at the 2012 Summer ...` | `The cycling event at the 2012 Summer ...` | `The cycling event at the 2012 Summer ...` | 1812 | 3167 | 6528 | 4 |
| `eval-028` | aggregation | `not found in corpus` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 1903 | 2195 | 6812 | 4 |
| `eval-029` | aggregation | `not found in corpus` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 1848 | 2150 | 6669 | 4 |
| `eval-030` | superlative | `The alpine skiing event at the 1994 W...` | `The alpine skiing event at the 1994 W...` | `The alpine skiing event at the 1994 W...` | 1946 | 2419 | 6547 | 4 |
| `eval-031` | temporal | `The gold medal in the men's 62 kg wei...` | `Kim Un-guk [Q1139399#c0].` | `The gold medal in the men's 62 kg wei...` | 2443 | 1561 | 4123 | 3 |
| `eval-032` | multi_hop | `The gold medal in the event held at P...` | `The question cannot be answered based...` | `The gold medal in the event held at P...` | 2559 | 3177 | 5992 | 4 |
| `eval-033` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 4.   All fo...` | `According to the provided corpus, the...` | 1960 | 1882 | 6729 | 4 |
| `eval-034` | temporal | `The gold medal in the men's freestyle...` | `Bakhtiyar Akhmedov [Q581364#c0].` | `The gold medal in the men's freestyle...` | 2600 | 1306 | 4155 | 3 |
| `eval-035` | superlative | `The rowing event at the 2012 Summer O...` | `The rowing event at the 2012 Summer O...` | `The rowing event at the 2012 Summer O...` | 1936 | 3664 | 6701 | 4 |
| `eval-036` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 2207 | 2631 | 6870 | 4 |
| `eval-037` | superlative | `The sailing event at the 1996 Summer ...` | `The sailing event at the 1996 Summer ...` | `The sailing event at the 1996 Summer ...` | 1727 | 2428 | 6582 | 4 |
| `eval-038` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 10` | `According to the provided corpus, the...` | 2130 | 3218 | 6270 | 3 |
| `eval-039` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 2000 | 1971 | 6643 | 4 |
| `eval-040` | multi_hop | `The gold medalist in the event held a...` | `The gold medalist in the event held a...` | `The gold medal in the Women's 10,000 ...` | 2146 | 3292 | 7229 | 4 |
| `eval-041` | aggregation | `According to the provided corpus, the...` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 1932 | 1809 | 7887 | 4 |
| `eval-042` | temporal | `The gold medal in the mixed trap shoo...` | `Dmitry Monakov [Q7500750#c0].` | `The gold medal in the mixed trap shoo...` | 2978 | 1109 | 4086 | 3 |
| `eval-043` | multi_hop | `not found in corpus` | `The gold medal in the event held at C...` | `The gold medal in the event held at C...` | 3368 | 2301 | 6192 | 4 |
| `eval-044` | temporal | `The gold medal in the women's 75 kg w...` | `Lydia Valentín [Q1997032#c0].` | `The gold medal in the women's 75 kg w...` | 2769 | 1494 | 4126 | 3 |
| `eval-045` | temporal | `Hannah Kearney won the gold medal in ...` | `Hannah Kearney [Q905561#c0].` | `The gold medal in the women's moguls ...` | 2394 | 1390 | 5559 | 4 |
| `eval-046` | temporal | `The gold medal in the light flyweight...` | `Brahim Asloum [Q4951841#c0].` | `The gold medal in the light flyweight...` | 2158 | 1362 | 4103 | 3 |
| `eval-047` | superlative | `The cycling event at the 2004 Summer ...` | `The cycling event at the 2004 Summer ...` | `The cycling event at the 2004 Summer ...` | 2095 | 2231 | 5005 | 3 |
| `eval-048` | aggregation | `not found in corpus` | `GRAPH AGGREGATION RESULT: 3.` | `According to the provided corpus, the...` | 1760 | 2335 | 5403 | 3 |
| `eval-049` | superlative | `The shooting event at the 1988 Summer...` | `The shooting event at the 1988 Summer...` | `The shooting event at the 1988 Summer...` | 2188 | 2570 | 6601 | 4 |
| `eval-050` | multi_hop | `not found in corpus` | `David Rudisha [Q1049551#c0].` | `The gold medal in the event held at t...` | 2712 | 1218 | 2688 | 2 |
