# 3-Pipeline Comparative Benchmark Report (Full 100 Evaluation Questions)

This report documents the systematic evaluation of all three architectures across all 100 questions from `eval_public.jsonl`:
1. **Pipeline 1 (Plain RAG)**: Fixed top-8 BM25 retrieval over document text chunks.
2. **Pipeline 2 (GraphRAG)**: Single-retrieval structured Knowledge Graph lookup + narrative chunk augmentation.
3. **Pipeline 3 (Agentic GraphRAG)**: Autonomous orchestrator with dynamic planning, tool calling, and evidence evaluation.

---

## 1. Summary Results (100 Questions)

| Pipeline | Overall Accuracy | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pipeline 1: Plain RAG** | **66.0%** (66/100) | 2292 | 229,213 | 12.95s | 21.6m (1294.5s) | N/A (1 step) |
| **Pipeline 2: GraphRAG** | **80.0%** (80/100) | 2235 | 223,524 | 8.00s | 13.3m (800.1s) | N/A (1 step) |
| **Pipeline 3: Agentic GraphRAG** | **84.0%** (84/100) | 6390 | 638,977 | 23.08s | 38.5m (2308.4s) | 3.14 steps |

---

## 2. Accuracy by Query Type Breakdown

| Query Type | Questions | Plain RAG Accuracy | GraphRAG Accuracy | Agentic GraphRAG Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 0.0% | 47.6% | 90.5% |
| **lookup** | 19 | 100.0% | 89.5% | 94.7% |
| **multi_hop** | 28 | 82.1% | 75.0% | 53.6% |
| **superlative** | 10 | 60.0% | 100.0% | 100.0% |
| **temporal** | 22 | 81.8% | 100.0% | 100.0% |

### Token Consumption by Query Type (Average Tokens / Question)

| Query Type | Questions | Plain RAG Tokens | GraphRAG Tokens | Agentic GraphRAG Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 1984 | 2325 | 10424 |
| **lookup** | 19 | 2157 | 2987 | 3388 |
| **multi_hop** | 28 | 2385 | 1771 | 4953 |
| **superlative** | 10 | 2089 | 2893 | 9957 |
| **temporal** | 22 | 2678 | 1792 | 5338 |

### Latency by Query Type (Average Seconds / Question)

| Query Type | Questions | Plain RAG Latency | GraphRAG Latency | Agentic GraphRAG Latency |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 17.40s | 8.24s | 35.29s |
| **lookup** | 19 | 8.94s | 9.17s | 13.60s |
| **multi_hop** | 28 | 13.67s | 6.98s | 21.56s |
| **superlative** | 10 | 11.36s | 11.12s | 27.49s |
| **temporal** | 22 | 11.95s | 6.64s | 19.57s |

---

## 3. Headline Findings Grounded in Full 100-Question Scale

1. **Overall Performance Trajectory (Agentic > GraphRAG > Plain RAG)**:
   - **Agentic GraphRAG** leads overall at **84.0%** (84/100 correct), outperforming **GraphRAG** at **80.0%** (+4.0%) and decisively surpassing **Plain RAG** at **66.0%** (+18.0%).
   - While the 15-question sample showed a 100% vs 93.3% vs 66.7% spread, scaling to 100 questions reveals a realistic, nuanced distribution where the difficulty of unstructured multi-hop queries challenges both graph pipelines.

2. **The Aggregation & Superlative Paradigm Shift**:
   - On **aggregation questions** (21 total), Plain RAG collapsed to **0.0% (0/21)**. A fixed top-k text retriever cannot capture the full set of events across disparate documents (Frac@8 retrieval gap).
   - In stark contrast, **Agentic GraphRAG reached 90.5% (19/21)** and **GraphRAG reached 47.6% (10/21)** by translating natural language counting queries into deterministic SQL queries across the entire knowledge graph.
   - On **superlatives** (10 questions) and **temporals** (22 questions), Agentic GraphRAG achieved a perfect **100.0% (10/10 and 22/22)**, proving that structured relational filtering eliminates ranking hallucination.

3. **Trade-offs in Token Efficiency and Wall-Clock Latency**:
   - **GraphRAG** is the fastest and most token-economical pipeline overall: **8.00s avg latency** and **2,235 tokens/question** (Total wall-clock: **13.3 minutes**, Total tokens: **223,524**).
   - **Plain RAG** consumed **2,292 tokens/question** with **12.95s avg latency** (Total wall-clock: **21.6 minutes**, Total tokens: **229,213**).
   - **Agentic GraphRAG** trades resource intensity for reasoning precision: it consumed **6,390 tokens/question** (2.86x Plain RAG) and **23.08s avg latency** across **3.14 average steps** (Total wall-clock: **38.5 minutes**, Total tokens: **638,977**).

---

## 4. Failure Pattern Analysis (New Discoveries at 100-Question Scale)

Scaling from 15 to 100 questions uncovered key systemic failure patterns that were invisible in the stratified sample:

1. **Multi-Hop Venue/Date Entity Disconnection (Agentic & GraphRAG Bottleneck)**:
   - In the 15-question sample, multi-hop accuracy was 100% for all pipelines. At 100 questions, multi-hop accuracy dropped to **53.6% (15/28)** for Agentic GraphRAG and **75.0% (21/28)** for GraphRAG, while Plain RAG achieved **82.1% (23/28)**.
   - **Root Cause**: Many 100-question multi-hop queries identify events solely through dates and venue names without specifying the sport (e.g., `pub-022`: *"Beijing Science and Technology University Gymnasium on August 12, 2008"*, `pub-023`: *"Estadi Olímpic Lluís Companys, Barcelona on August 9, 1992"*, `pub-028`: *"Olympic Aquatic Centre on August 14, 2004"*).
   - In the SQLite graph schema, venues are embedded inside the raw text chunks (`documents.text`), not extracted into dedicated queryable columns in the `events` table. Plain RAG finds these instantly via BM25 keyword matching on venue names. The Agent, prioritizing structured graph queries (`get_events`), received 0 events and exhausted its step budget before navigating back to unstructured text search.

2. **GraphRAG Off-by-One Compound Aggregation Under-Counting**:
   - GraphRAG scored only 47.6% on aggregation compared to 90.5% for Agentic.
   - **Root Cause**: GraphRAG's single-turn LLM query extractor struggled with multi-clause thresholds (e.g., *events with > 73 competitors and held in year X*), frequently under-counting by 1 (`pub-010`, `pub-020`, `pub-024`, `pub-027`, `pub-051`, `pub-058`, `pub-069`, `pub-078`, `pub-092`). The Agent's multi-step verification loop (`evaluate_evidence`) inspected the matching event list, caught missing criteria, and recalculated correctly.

3. **Ground Truth String Formatting Artifacts**:
   - In `pub-015` (`Dani KingLaura TrottJoanna Rowsell`) and `pub-099` (`Erik LesserDaniel BöhmArnd PeifferSimon Schempp`), the evaluation dataset concatenated multiple team members without spaces or separators.
   - Both Agentic GraphRAG and GraphRAG accurately identified and named all athletes in proper English syntax, but strict normalized substring evaluation flagged them as mismatches because the unspaced concatenation did not appear verbatim.

---

## 5. Token Efficiency & Resource Consumption Summary

| Metric | Plain RAG | GraphRAG | Agentic GraphRAG | Winner |
| :--- | :---: | :---: | :---: | :--- |
| **Accuracy** | 66.0% | 80.0% | **84.0%** | **Agentic (+18.0% over RAG)** |
| **Total Tokens** | 229,213 | **223,524** | 638,977 | **GraphRAG (most efficient)** |
| **Avg Tokens / Question** | 2,292 | **2,235** | 6,390 | **GraphRAG** |
| **Total Wall-Clock Time** | 21.6 min | **13.3 min** | 38.5 min | **GraphRAG (2.89x faster than Agent)** |
| **Avg Latency / Question** | 12.95s | **8.00s** | 23.08s | **GraphRAG** |
| **Accuracy per 100k Tokens** | 28.8% | **35.8%** | 13.1% | **GraphRAG** |

---

## 6. Question-by-Question Comparison Table (All 100 Questions)

| QID | Type | Gold Target | RAG | GraphRAG | Agent | RAG Tok | GR Tok | AG Tok | RAG Lat | GR Lat | AG Lat |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pub-001` | aggregation | `['5']` | ❌ | ✅ | ✅ | 1969 | 2010 | 10170 | 24.045s | 20.426s | 25.773s |
| `pub-002` | temporal | `['Chen Ding']` | ✅ | ✅ | ✅ | 1944 | 1657 | 4337 | 8.51s | 7.753s | 18.177s |
| `pub-003` | aggregation | `['8']` | ❌ | ✅ | ❌ | 2167 | 2659 | 12754 | 26.532s | 14.436s | 37.198s |
| `pub-004` | superlative | `["Athletics at the 2008 Summer Olympi...` | ❌ | ✅ | ✅ | 2644 | 3332 | 7923 | 5.688s | 11.14s | 21.288s |
| `pub-005` | multi_hop | `['Naim Süleymanoğlu']` | ✅ | ✅ | ✅ | 1903 | 1006 | 5032 | 8.122s | 5.746s | 18.907s |
| `pub-006` | temporal | `['Rafaela Silva']` | ❌ | ✅ | ✅ | 2715 | 1565 | 4343 | 9.345s | 5.92s | 15.899s |
| `pub-007` | temporal | `['Renaud Lavillenie']` | ✅ | ✅ | ✅ | 2651 | 2046 | 7294 | 9.907s | 6.425s | 23.853s |
| `pub-008` | superlative | `['Sailing at the 2000 Summer Olympics...` | ✅ | ✅ | ✅ | 1868 | 1980 | 7995 | 8.088s | 8.741s | 20.818s |
| `pub-009` | lookup | `['26']` | ✅ | ✅ | ✅ | 2378 | 3351 | 2869 | 6.944s | 14.877s | 10.736s |
| `pub-010` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1915 | 1709 | 8966 | 19.206s | 5.188s | 21.95s |
| `pub-011` | multi_hop | `['Martina Sáblíková']` | ✅ | ✅ | ✅ | 2101 | 1438 | 4310 | 8.5s | 6.058s | 18.277s |
| `pub-012` | aggregation | `['6']` | ❌ | ❌ | ✅ | 1911 | 2673 | 14467 | 5.26s | 6.158s | 47.091s |
| `pub-013` | temporal | `['Allison Schmitt']` | ✅ | ✅ | ✅ | 2911 | 1612 | 4398 | 9.922s | 5.617s | 17.263s |
| `pub-014` | multi_hop | `['Carolina Marín']` | ✅ | ✅ | ✅ | 2243 | 1175 | 2970 | 10.361s | 5.133s | 14.219s |
| `pub-015` | multi_hop | `['Dani KingLaura TrottJoanna Rowsell']` | ❌ | ❌ | ❌ | 2488 | 1309 | 2948 | 11.778s | 8.341s | 12.995s |
| `pub-016` | temporal | `['Arnd Peiffer']` | ✅ | ✅ | ✅ | 2347 | 2050 | 6171 | 9.307s | 6.079s | 20.539s |
| `pub-017` | multi_hop | `['Yi Siling']` | ✅ | ✅ | ✅ | 1894 | 1045 | 4294 | 7.978s | 4.961s | 16.586s |
| `pub-018` | temporal | `['Kevin Jackson']` | ✅ | ✅ | ✅ | 2793 | 1133 | 4372 | 12.462s | 4.881s | 16.349s |
| `pub-019` | aggregation | `['3']` | ❌ | ✅ | ✅ | 2064 | 2525 | 10443 | 8.609s | 5.985s | 37.979s |
| `pub-020` | aggregation | `['4']` | ❌ | ❌ | ✅ | 2105 | 1812 | 8440 | 15.942s | 5.248s | 23.049s |
| `pub-021` | superlative | `["Alpine skiing at the 1988 Winter Ol...` | ✅ | ✅ | ✅ | 1908 | 2727 | 9535 | 7.818s | 11.107s | 24.5s |
| `pub-022` | multi_hop | `['Ayumi Tanimoto']` | ✅ | ✅ | ❌ | 2697 | 2363 | 3988 | 9.359s | 7.042s | 19.008s |
| `pub-023` | multi_hop | `['Hwang Young-Cho']` | ✅ | ❌ | ❌ | 2150 | 3050 | 7232 | 12.902s | 11.651s | 35.12s |
| `pub-024` | aggregation | `['3']` | ❌ | ❌ | ✅ | 1882 | 2058 | 8793 | 8.924s | 5.518s | 21.62s |
| `pub-025` | lookup | `['23']` | ✅ | ✅ | ✅ | 2230 | 3218 | 2878 | 5.942s | 9.934s | 11.333s |
| `pub-026` | temporal | `['Jaroslav Kulhavý']` | ✅ | ✅ | ✅ | 2153 | 1842 | 7128 | 8.679s | 6.645s | 22.827s |
| `pub-027` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1877 | 2012 | 10388 | 14.037s | 5.242s | 40.948s |
| `pub-028` | multi_hop | `['Michael Phelps']` | ✅ | ❌ | ❌ | 2241 | 3767 | 8180 | 9.663s | 8.505s | 41.638s |
| `pub-029` | lookup | `['28']` | ✅ | ✅ | ✅ | 1773 | 2737 | 2899 | 5.47s | 7.007s | 11.342s |
| `pub-030` | multi_hop | `['Emese Szász']` | ❌ | ✅ | ✅ | 3490 | 2368 | 4307 | 6.576s | 7.689s | 16.817s |
| `pub-031` | multi_hop | `['Dmitry Berestov']` | ✅ | ✅ | ✅ | 1927 | 922 | 4992 | 8.752s | 6.016s | 19.189s |
| `pub-032` | lookup | `['34']` | ✅ | ❌ | ✅ | 2773 | 3291 | 2873 | 7.39s | 9.877s | 10.728s |
| `pub-033` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1998 | 2380 | 10931 | 5.037s | 7.845s | 27.007s |
| `pub-034` | lookup | `['23']` | ✅ | ✅ | ✅ | 2284 | 2046 | 2868 | 6.572s | 8.44s | 11.654s |
| `pub-035` | lookup | `['30']` | ✅ | ✅ | ✅ | 1838 | 2901 | 2904 | 5.591s | 7.129s | 11.127s |
| `pub-036` | temporal | `['Zou Shiming']` | ✅ | ✅ | ✅ | 2308 | 1403 | 4345 | 8.569s | 6.741s | 15.901s |
| `pub-037` | superlative | `["Shooting at the 2008 Summer Olympic...` | ❌ | ✅ | ✅ | 2298 | 3380 | 8177 | 8.861s | 12.862s | 19.649s |
| `pub-038` | multi_hop | `['Pyrros Dimas']` | ❌ | ✅ | ✅ | 1962 | 1215 | 4926 | 7.855s | 5.501s | 18.155s |
| `pub-039` | temporal | `['Sandra Perković']` | ✅ | ✅ | ✅ | 2995 | 1489 | 4339 | 9.68s | 5.711s | 15.741s |
| `pub-040` | temporal | `['Jason Lamy Chappuis']` | ✅ | ✅ | ✅ | 2119 | 2247 | 5792 | 8.581s | 6.653s | 22.342s |
| `pub-041` | multi_hop | `['Nino Schurter']` | ✅ | ✅ | ✅ | 2273 | 797 | 2911 | 11.511s | 4.88s | 11.846s |
| `pub-042` | lookup | `['47']` | ✅ | ✅ | ❌ | 1663 | 2760 | 4980 | 5.222s | 8.798s | 19.136s |
| `pub-043` | multi_hop | `['Kjetil André Aamodt']` | ✅ | ✅ | ✅ | 2392 | 1158 | 4379 | 8.631s | 5.395s | 16.921s |
| `pub-044` | superlative | `["Fencing at the 2008 Summer Olympics...` | ✅ | ✅ | ✅ | 2166 | 2544 | 12109 | 8.199s | 9.805s | 35.362s |
| `pub-045` | aggregation | `['20']` | ❌ | ❌ | ✅ | 1965 | 3107 | 8202 | 11.364s | 7.277s | 110.025s |
| `pub-046` | lookup | `['50']` | ✅ | ✅ | ✅ | 2211 | 2841 | 5092 | 5.749s | 11.629s | 20.997s |
| `pub-047` | lookup | `['24']` | ✅ | ✅ | ✅ | 1935 | 3406 | 7806 | 5.508s | 11.616s | 29.049s |
| `pub-048` | temporal | `['Servet Tazegül']` | ❌ | ✅ | ✅ | 3697 | 1752 | 4362 | 11.187s | 6.813s | 16.681s |
| `pub-049` | temporal | `['Martin Fourcade']` | ✅ | ✅ | ✅ | 2412 | 1942 | 8067 | 8.537s | 10.109s | 27.862s |
| `pub-050` | multi_hop | `['Lee Sang-hwa']` | ✅ | ✅ | ✅ | 2595 | 1147 | 4308 | 28.087s | 5.43s | 17.836s |
| `pub-051` | aggregation | `['6']` | ❌ | ❌ | ✅ | 2057 | 2779 | 11882 | 37.656s | 6.341s | 32.213s |
| `pub-052` | lookup | `['20']` | ✅ | ✅ | ✅ | 2056 | 2880 | 3010 | 5.76s | 6.958s | 16.179s |
| `pub-053` | superlative | `["Shooting at the 2016 Summer Olympic...` | ❌ | ✅ | ✅ | 2272 | 3046 | 12836 | 8.571s | 10.934s | 36.182s |
| `pub-054` | lookup | `['24']` | ✅ | ✅ | ✅ | 2572 | 3243 | 2887 | 6.115s | 7.32s | 14.928s |
| `pub-055` | temporal | `['Sebastián Crismanich']` | ❌ | ✅ | ✅ | 3329 | 1854 | 6628 | 15.838s | 7.072s | 23.086s |
| `pub-056` | temporal | `['Yevgeny Dementyev']` | ✅ | ✅ | ✅ | 2690 | 1609 | 8088 | 9.624s | 9.19s | 29.182s |
| `pub-057` | temporal | `['Allyson Felix']` | ❌ | ✅ | ✅ | 3036 | 1555 | 4343 | 9.487s | 5.566s | 16.44s |
| `pub-058` | aggregation | `['5']` | ❌ | ❌ | ✅ | 1929 | 2509 | 11639 | 11.15s | 6.063s | 28.311s |
| `pub-059` | temporal | `['Laura Dahlmeier']` | ✅ | ✅ | ✅ | 2466 | 1388 | 5779 | 19.539s | 5.527s | 20.835s |
| `pub-060` | multi_hop | `['Yana Shemyakina']` | ✅ | ❌ | ❌ | 2446 | 2375 | 7566 | 8.797s | 9.464s | 34.509s |
| `pub-061` | lookup | `['34']` | ✅ | ✅ | ✅ | 2150 | 2995 | 2871 | 7.338s | 7.079s | 10.729s |
| `pub-062` | temporal | `['Tirunesh Dibaba']` | ✅ | ✅ | ✅ | 2777 | 2868 | 4358 | 9.423s | 7.521s | 16.638s |
| `pub-063` | lookup | `['41']` | ✅ | ❌ | ✅ | 2567 | 3314 | 2896 | 6.343s | 11.276s | 11.158s |
| `pub-064` | multi_hop | `['Gabriela Szabo']` | ✅ | ✅ | ❌ | 2232 | 1769 | 5559 | 10.025s | 6.659s | 25.329s |
| `pub-065` | aggregation | `['5']` | ❌ | ✅ | ✅ | 2005 | 2200 | 9744 | 13.514s | 8.351s | 22.998s |
| `pub-066` | superlative | `["Weightlifting at the 1992 Summer Ol...` | ✅ | ✅ | ✅ | 1956 | 2724 | 9708 | 8.49s | 12.454s | 26.462s |
| `pub-067` | multi_hop | `['Rosannagh MacLennan']` | ✅ | ✅ | ❌ | 3364 | 875 | 2873 | 28.934s | 5.029s | 12.128s |
| `pub-068` | lookup | `['24']` | ✅ | ✅ | ✅ | 1863 | 3253 | 2847 | 22.577s | 9.656s | 10.996s |
| `pub-069` | aggregation | `['3']` | ❌ | ❌ | ✅ | 2088 | 1773 | 10260 | 31.814s | 5.283s | 25.994s |
| `pub-070` | aggregation | `['3']` | ❌ | ✅ | ✅ | 1846 | 1550 | 10386 | 24.107s | 5.513s | 33.561s |
| `pub-071` | lookup | `['24']` | ✅ | ✅ | ✅ | 1909 | 2694 | 2895 | 5.463s | 8.921s | 11.194s |
| `pub-072` | temporal | `['Lee Sang-hwa']` | ✅ | ✅ | ✅ | 2866 | 2357 | 5790 | 9.386s | 6.896s | 22.607s |
| `pub-073` | multi_hop | `['Yang Ling']` | ✅ | ✅ | ❌ | 2130 | 2627 | 6765 | 9.444s | 10.599s | 26.64s |
| `pub-074` | lookup | `['17']` | ✅ | ✅ | ✅ | 2411 | 2817 | 3055 | 6.02s | 9.557s | 11.863s |
| `pub-075` | lookup | `['32']` | ✅ | ✅ | ✅ | 1994 | 3654 | 2945 | 5.547s | 7.77s | 12.887s |
| `pub-076` | multi_hop | `['Julia Mancuso']` | ✅ | ❌ | ❌ | 2205 | 3321 | 3920 | 7.759s | 10.449s | 16.482s |
| `pub-077` | multi_hop | `['Kaillie Humphries']` | ✅ | ✅ | ❌ | 2890 | 1177 | 7085 | 10.381s | 5.508s | 32.382s |
| `pub-078` | aggregation | `['7']` | ❌ | ❌ | ✅ | 2074 | 2496 | 10421 | 4.896s | 5.805s | 24.49s |
| `pub-079` | multi_hop | `['Leontien Zijlaard']` | ✅ | ✅ | ✅ | 2350 | 923 | 5099 | 26.465s | 5.517s | 20.275s |
| `pub-080` | lookup | `['17']` | ✅ | ✅ | ✅ | 2556 | 1673 | 2876 | 24.182s | 8.392s | 11.008s |
| `pub-081` | multi_hop | `['Guo Wenjun']` | ✅ | ✅ | ❌ | 2327 | 2793 | 7164 | 28.867s | 9.393s | 27.641s |
| `pub-082` | aggregation | `['12']` | ❌ | ✅ | ✅ | 1969 | 2993 | 11696 | 32.084s | 22.693s | 38.692s |
| `pub-083` | multi_hop | `['Pernilla Wiberg']` | ✅ | ❌ | ✅ | 1924 | 3341 | 4445 | 5.886s | 8.732s | 26.153s |
| `pub-084` | superlative | `["Fencing at the 1992 Summer Olympics...` | ✅ | ✅ | ✅ | 1963 | 3159 | 9793 | 7.505s | 10.97s | 29.308s |
| `pub-085` | superlative | `["Sailing at the 2008 Summer Olympics...` | ❌ | ✅ | ✅ | 1882 | 3209 | 11808 | 23.191s | 11.713s | 36.007s |
| `pub-086` | multi_hop | `['Shani Davis']` | ✅ | ✅ | ✅ | 2154 | 1232 | 6407 | 23.859s | 4.965s | 24.511s |
| `pub-087` | aggregation | `['17']` | ❌ | ✅ | ❌ | 1966 | 3148 | 7805 | 21.693s | 6.637s | 62.603s |
| `pub-088` | superlative | `["Alpine skiing at the 1992 Winter Ol...` | ✅ | ✅ | ✅ | 1937 | 2831 | 9690 | 27.205s | 11.512s | 25.327s |
| `pub-089` | aggregation | `['5']` | ❌ | ✅ | ✅ | 2004 | 2418 | 11007 | 15.534s | 7.0s | 29.016s |
| `pub-090` | temporal | `['Aslanbek Khushtov']` | ✅ | ✅ | ✅ | 2586 | 1467 | 4386 | 26.167s | 5.841s | 17.659s |
| `pub-091` | lookup | `['18']` | ✅ | ✅ | ✅ | 1818 | 3685 | 2920 | 26.104s | 8.05s | 11.261s |
| `pub-092` | aggregation | `['6']` | ❌ | ❌ | ✅ | 1982 | 1956 | 11456 | 24.128s | 5.776s | 27.911s |
| `pub-093` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1885 | 2055 | 9058 | 9.866s | 10.252s | 22.648s |
| `pub-094` | temporal | `['Oleg Kucherenko']` | ✅ | ✅ | ✅ | 2000 | 1169 | 4414 | 8.522s | 5.632s | 18.183s |
| `pub-095` | multi_hop | `['Valerie Vili']` | ❌ | ✅ | ✅ | 3265 | 1717 | 2893 | 26.661s | 5.798s | 11.876s |
| `pub-096` | multi_hop | `['Fazliddin Gaibnazarov']` | ✅ | ✅ | ✅ | 2895 | 1175 | 3004 | 29.373s | 5.713s | 14.009s |
| `pub-097` | temporal | `['Yana Shemyakina']` | ✅ | ✅ | ✅ | 3061 | 2749 | 4327 | 30.668s | 7.838s | 15.787s |
| `pub-098` | multi_hop | `['Bekzat Sattarkhanov']` | ✅ | ✅ | ❌ | 1856 | 2273 | 8101 | 6.462s | 7.007s | 40.457s |
| `pub-099` | multi_hop | `['Erik LesserDaniel BöhmArnd PeifferS...` | ❌ | ❌ | ❌ | 2375 | 1229 | 3034 | 9.695s | 8.214s | 13.738s |
| `pub-100` | temporal | `['Missy Franklin']` | ✅ | ✅ | ✅ | 3055 | 1670 | 4371 | 9.667s | 5.724s | 16.666s |