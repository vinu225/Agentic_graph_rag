# 3-Pipeline Comparative Benchmark Report (Final Submission - 100 Questions)

This report documents the definitive evaluation across all 100 questions from `eval_public.jsonl`.
It benchmarks **Pipeline 1 (Plain RAG)**, **Pipeline 2 (GraphRAG)**, and **Pipeline 3 (Optimized Agentic GraphRAG)**.

> **Note on Historical Baseline**: The original unoptimized run is preserved unedited in `comparison_100.md`.
> This report (`comparison_100_final.md`) reflects the submission-ready system incorporating lightweight schema projection, compact context injection, and concise synthesis prompting.

---

## 1. Summary Results (100 Questions)

| Pipeline | Overall Accuracy | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pipeline 1: Plain RAG** | **66.0%** (66/100) | 2292 | 229,213 | 12.95s | 21.6m (1294.5s) | N/A (1 step) |
| **Pipeline 2: GraphRAG** | **80.0%** (80/100) | 2235 | 223,524 | 8.00s | 13.3m (800.1s) | N/A (1 step) |
| **Pipeline 3: Optimized Agent** | **85.0%** (85/100) | **5279** | **527,855** | **19.57s** | **32.6m (1956.6s)** | **3.40 steps** |

---

## 2. Agentic Optimization Impact (Full 100-Question Scale: Pre- vs Post-Optimization)

| Metric | Pre-Optimization Baseline (`comparison_100.md`) | Post-Optimization Final (`comparison_100_final.md`) | Delta (Full 100-Scale) |
| :--- | :---: | :---: | :---: |
| **Agent Overall Accuracy** | 84.0% | **85.0%** | **+1.0%** |
| **Agent Avg Tokens / Question** | 6390 | **5279** | **-1111 tokens (-17.4%)** |
| **Agent Total Tokens** | 638,977 | **527,855** | **-111,122 tokens (-17.4%)** |
| **Agent Avg Latency / Question** | 23.08s | **19.57s** | **-3.51s (-15.2%)** |
| **Agent Total Wall-Clock Time** | 38.5 min | **32.6 min** | **-5.9 min (-15.2%)** |
| **Agent Average Steps** | 3.14 steps | **3.40 steps** | +0.26 steps |

---

## 3. Accuracy by Query Type Breakdown

| Query Type | Questions | Plain RAG Accuracy | GraphRAG Accuracy | Optimized Agent Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 0.0% | 47.6% | **95.2%** |
| **lookup** | 19 | 100.0% | 89.5% | **94.7%** |
| **multi_hop** | 28 | 82.1% | 75.0% | **53.6%** |
| **superlative** | 10 | 60.0% | 100.0% | **100.0%** |
| **temporal** | 22 | 81.8% | 100.0% | **100.0%** |

### Token Consumption by Query Type (Average Tokens / Question)

| Query Type | Questions | Plain RAG Tokens | GraphRAG Tokens | Optimized Agent Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 1984 | 2325 | **6800** |
| **lookup** | 19 | 2157 | 2987 | **5016** |
| **multi_hop** | 28 | 2385 | 1771 | **4120** |
| **superlative** | 10 | 2089 | 2893 | **6303** |
| **temporal** | 22 | 2678 | 1792 | **5062** |

### Latency by Query Type (Average Seconds / Question)

| Query Type | Questions | Plain RAG Latency | GraphRAG Latency | Optimized Agent Latency |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 17.40s | 8.24s | **22.69s** |
| **lookup** | 19 | 8.94s | 9.17s | **18.89s** |
| **multi_hop** | 28 | 13.67s | 6.98s | **18.05s** |
| **superlative** | 10 | 11.36s | 11.12s | **20.59s** |
| **temporal** | 22 | 11.95s | 6.64s | **18.63s** |

---

## 4. Key Empirical Findings & Failure Pattern Analysis

1. **Optimization Efficacy at Scale**:
   - Across all 100 questions, the 3 applied optimizations reduced total Agent token consumption from **638,977** down to **527,855** (-17.4% reduction).
   - Total wall-clock runtime dropped from **38.5 minutes** down to **32.6 minutes** (-15.2% faster), while maintaining high accuracy.
   - The fix completely eliminated the runaway essay completions (e.g. `pub-045` dropped from 110s to ~20s) and token budget aborts (`pub-012` now terminates with clean sufficiency).

2. **Multi-Hop Traversal Disparity (Confirmed Unchanged)**:
   - On multi-hop queries (28 total), Plain RAG achieved 82.1%, GraphRAG achieved 75.0%, and Agent achieved 53.6%.
   - **Root Cause Confirmed**: As predicted, token optimizations did not alter this retrieval dynamic. Questions describing events purely via venue names and dates without mentioning the sport (e.g. `pub-022`, `pub-023`, `pub-028`) hit BM25 text chunks immediately in Plain RAG, whereas the SQLite graph schema lacks indexed venue columns in the `events` table.

3. **Verified Ground Truth String Formatting Artifacts (`pub-015` & `pub-099`)**:
   - **Empirically Verified**: In `pub-015`, the dataset ground truth string is `['Dani KingLaura TrottJoanna Rowsell']` (concatenated without spaces or commas). The Agent generated: *'The gold medal in the event held at London Velopark on 3 to 4 August at the 2012 Summer Olympics was won by Dani King, Laura Trott, and Joanna Rowsell from the United Kingdom (GBR).'*, which was penalized solely due to the missing spaces in the evaluation target.
   - **Empirically Verified**: In `pub-099`, the ground truth string is `['Erik LesserDaniel BöhmArnd PeifferSimon Schempp']`. The Agent correctly extracted all 4 athletes (*'Erik Lesser, Daniel Böhm, Arnd Peiffer, and Simon Schempp'*), but normalized string matching flagged a mismatch.

---

## 5. Question-by-Question Comparison Table (All 100 Questions)

| QID | Type | Gold Target | RAG | GraphRAG | Opt Agent | RAG Tok | GR Tok | Opt AG Tok | RAG Lat | GR Lat | Opt AG Lat |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pub-001` | aggregation | `['5']` | ❌ | ✅ | ✅ | 1969 | 2010 | 8652 | 24.045s | 20.426s | 42.499s |
| `pub-002` | temporal | `['Chen Ding']` | ✅ | ✅ | ✅ | 1944 | 1657 | 4134 | 8.51s | 7.753s | 16.02s |
| `pub-003` | aggregation | `['8']` | ❌ | ✅ | ✅ | 2167 | 2659 | 7021 | 26.532s | 14.436s | 22.684s |
| `pub-004` | superlative | `["Athletics at the 2008 Summer Olympi...` | ❌ | ✅ | ✅ | 2644 | 3332 | 5021 | 5.688s | 11.14s | 16.592s |
| `pub-005` | multi_hop | `['Naim Süleymanoğlu']` | ✅ | ✅ | ✅ | 1903 | 1006 | 2698 | 8.122s | 5.746s | 12.076s |
| `pub-006` | temporal | `['Rafaela Silva']` | ❌ | ✅ | ✅ | 2715 | 1565 | 4124 | 9.345s | 5.92s | 15.225s |
| `pub-007` | temporal | `['Renaud Lavillenie']` | ✅ | ✅ | ✅ | 2651 | 2046 | 6261 | 9.907s | 6.425s | 21.897s |
| `pub-008` | superlative | `['Sailing at the 2000 Summer Olympics...` | ✅ | ✅ | ✅ | 1868 | 1980 | 6545 | 8.088s | 8.741s | 21.395s |
| `pub-009` | lookup | `['26']` | ✅ | ✅ | ✅ | 2378 | 3351 | 2901 | 6.944s | 14.877s | 10.374s |
| `pub-010` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1915 | 1709 | 5217 | 19.206s | 5.188s | 17.845s |
| `pub-011` | multi_hop | `['Martina Sáblíková']` | ✅ | ✅ | ✅ | 2101 | 1438 | 2700 | 8.5s | 6.058s | 12.512s |
| `pub-012` | aggregation | `['6']` | ❌ | ❌ | ✅ | 1911 | 2673 | 5524 | 5.26s | 6.158s | 18.513s |
| `pub-013` | temporal | `['Allison Schmitt']` | ✅ | ✅ | ✅ | 2911 | 1612 | 4142 | 9.922s | 5.617s | 15.785s |
| `pub-014` | multi_hop | `['Carolina Marín']` | ✅ | ✅ | ✅ | 2243 | 1175 | 2722 | 10.361s | 5.133s | 12.872s |
| `pub-015` | multi_hop | `['Dani KingLaura TrottJoanna Rowsell']` | ❌ | ❌ | ❌ | 2488 | 1309 | 2706 | 11.778s | 8.341s | 12.821s |
| `pub-016` | temporal | `['Arnd Peiffer']` | ✅ | ✅ | ✅ | 2347 | 2050 | 6141 | 9.307s | 6.079s | 21.374s |
| `pub-017` | multi_hop | `['Yi Siling']` | ✅ | ✅ | ✅ | 1894 | 1045 | 2679 | 7.978s | 4.961s | 11.538s |
| `pub-018` | temporal | `['Kevin Jackson']` | ✅ | ✅ | ✅ | 2793 | 1133 | 4135 | 12.462s | 4.881s | 15.375s |
| `pub-019` | aggregation | `['3']` | ❌ | ✅ | ✅ | 2064 | 2525 | 6909 | 8.609s | 5.985s | 21.608s |
| `pub-020` | aggregation | `['4']` | ❌ | ❌ | ✅ | 2105 | 1812 | 6747 | 15.942s | 5.248s | 22.072s |
| `pub-021` | superlative | `["Alpine skiing at the 1988 Winter Ol...` | ✅ | ✅ | ✅ | 1908 | 2727 | 6529 | 7.818s | 11.107s | 21.012s |
| `pub-022` | multi_hop | `['Ayumi Tanimoto']` | ✅ | ✅ | ❌ | 2697 | 2363 | 4035 | 9.359s | 7.042s | 18.163s |
| `pub-023` | multi_hop | `['Hwang Young-Cho']` | ✅ | ❌ | ❌ | 2150 | 3050 | 7259 | 12.902s | 11.651s | 30.87s |
| `pub-024` | aggregation | `['3']` | ❌ | ❌ | ✅ | 1882 | 2058 | 6716 | 8.924s | 5.518s | 21.719s |
| `pub-025` | lookup | `['23']` | ✅ | ✅ | ✅ | 2230 | 3218 | 4238 | 5.942s | 9.934s | 17.344s |
| `pub-026` | temporal | `['Jaroslav Kulhavý']` | ✅ | ✅ | ✅ | 2153 | 1842 | 6254 | 8.679s | 6.645s | 22.164s |
| `pub-027` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1877 | 2012 | 6904 | 14.037s | 5.242s | 21.718s |
| `pub-028` | multi_hop | `['Michael Phelps']` | ✅ | ❌ | ❌ | 2241 | 3767 | 5510 | 9.663s | 8.505s | 22.35s |
| `pub-029` | lookup | `['28']` | ✅ | ✅ | ✅ | 1773 | 2737 | 2930 | 5.47s | 7.007s | 11.171s |
| `pub-030` | multi_hop | `['Emese Szász']` | ❌ | ✅ | ✅ | 3490 | 2368 | 4109 | 6.576s | 7.689s | 16.822s |
| `pub-031` | multi_hop | `['Dmitry Berestov']` | ✅ | ✅ | ✅ | 1927 | 922 | 2690 | 8.752s | 6.016s | 12.662s |
| `pub-032` | lookup | `['34']` | ✅ | ❌ | ✅ | 2773 | 3291 | 2905 | 7.39s | 9.877s | 10.666s |
| `pub-033` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1998 | 2380 | 6774 | 5.037s | 7.845s | 21.678s |
| `pub-034` | lookup | `['23']` | ✅ | ✅ | ✅ | 2284 | 2046 | 7274 | 6.572s | 8.44s | 27.05s |
| `pub-035` | lookup | `['30']` | ✅ | ✅ | ✅ | 1838 | 2901 | 2935 | 5.591s | 7.129s | 11.093s |
| `pub-036` | temporal | `['Zou Shiming']` | ✅ | ✅ | ✅ | 2308 | 1403 | 4112 | 8.569s | 6.741s | 14.953s |
| `pub-037` | superlative | `["Shooting at the 2008 Summer Olympic...` | ❌ | ✅ | ✅ | 2298 | 3380 | 6613 | 8.861s | 12.862s | 22.189s |
| `pub-038` | multi_hop | `['Pyrros Dimas']` | ❌ | ✅ | ✅ | 1962 | 1215 | 2680 | 7.855s | 5.501s | 11.823s |
| `pub-039` | temporal | `['Sandra Perković']` | ✅ | ✅ | ✅ | 2995 | 1489 | 4118 | 9.68s | 5.711s | 15.038s |
| `pub-040` | temporal | `['Jason Lamy Chappuis']` | ✅ | ✅ | ✅ | 2119 | 2247 | 7626 | 8.581s | 6.653s | 26.952s |
| `pub-041` | multi_hop | `['Nino Schurter']` | ✅ | ✅ | ✅ | 2273 | 797 | 2683 | 11.511s | 4.88s | 11.697s |
| `pub-042` | lookup | `['47']` | ✅ | ✅ | ❌ | 1663 | 2760 | 4236 | 5.222s | 8.798s | 17.235s |
| `pub-043` | multi_hop | `['Kjetil André Aamodt']` | ✅ | ✅ | ✅ | 2392 | 1158 | 4098 | 8.631s | 5.395s | 16.724s |
| `pub-044` | superlative | `["Fencing at the 2008 Summer Olympics...` | ✅ | ✅ | ✅ | 2166 | 2544 | 6745 | 8.199s | 9.805s | 22.573s |
| `pub-045` | aggregation | `['20']` | ❌ | ❌ | ✅ | 1965 | 3107 | 6227 | 11.364s | 7.277s | 19.329s |
| `pub-046` | lookup | `['50']` | ✅ | ✅ | ✅ | 2211 | 2841 | 7418 | 5.749s | 11.629s | 27.776s |
| `pub-047` | lookup | `['24']` | ✅ | ✅ | ✅ | 1935 | 3406 | 7476 | 5.508s | 11.616s | 28.433s |
| `pub-048` | temporal | `['Servet Tazegül']` | ❌ | ✅ | ✅ | 3697 | 1752 | 6119 | 11.187s | 6.813s | 22.523s |
| `pub-049` | temporal | `['Martin Fourcade']` | ✅ | ✅ | ✅ | 2412 | 1942 | 7739 | 8.537s | 10.109s | 27.147s |
| `pub-050` | multi_hop | `['Lee Sang-hwa']` | ✅ | ✅ | ✅ | 2595 | 1147 | 6013 | 28.087s | 5.43s | 22.713s |
| `pub-051` | aggregation | `['6']` | ❌ | ❌ | ✅ | 2057 | 2779 | 7266 | 37.656s | 6.341s | 23.323s |
| `pub-052` | lookup | `['20']` | ✅ | ✅ | ✅ | 2056 | 2880 | 7433 | 5.76s | 6.958s | 27.394s |
| `pub-053` | superlative | `["Shooting at the 2016 Summer Olympic...` | ❌ | ✅ | ✅ | 2272 | 3046 | 6618 | 8.571s | 10.934s | 20.697s |
| `pub-054` | lookup | `['24']` | ✅ | ✅ | ✅ | 2572 | 3243 | 7374 | 6.115s | 7.32s | 26.856s |
| `pub-055` | temporal | `['Sebastián Crismanich']` | ❌ | ✅ | ✅ | 3329 | 1854 | 5781 | 15.838s | 7.072s | 22.079s |
| `pub-056` | temporal | `['Yevgeny Dementyev']` | ✅ | ✅ | ✅ | 2690 | 1609 | 4075 | 9.624s | 9.19s | 16.09s |
| `pub-057` | temporal | `['Allyson Felix']` | ❌ | ✅ | ✅ | 3036 | 1555 | 4126 | 9.487s | 5.566s | 15.174s |
| `pub-058` | aggregation | `['5']` | ❌ | ❌ | ✅ | 1929 | 2509 | 7037 | 11.15s | 6.063s | 22.053s |
| `pub-059` | temporal | `['Laura Dahlmeier']` | ✅ | ✅ | ✅ | 2466 | 1388 | 5550 | 19.539s | 5.527s | 20.173s |
| `pub-060` | multi_hop | `['Yana Shemyakina']` | ✅ | ❌ | ❌ | 2446 | 2375 | 2697 | 8.797s | 9.464s | 12.332s |
| `pub-061` | lookup | `['34']` | ✅ | ✅ | ✅ | 2150 | 2995 | 2902 | 7.338s | 7.079s | 10.15s |
| `pub-062` | temporal | `['Tirunesh Dibaba']` | ✅ | ✅ | ✅ | 2777 | 2868 | 4154 | 9.423s | 7.521s | 15.916s |
| `pub-063` | lookup | `['41']` | ✅ | ❌ | ✅ | 2567 | 3314 | 2930 | 6.343s | 11.276s | 11.339s |
| `pub-064` | multi_hop | `['Gabriela Szabo']` | ✅ | ✅ | ❌ | 2232 | 1769 | 8238 | 10.025s | 6.659s | 38.547s |
| `pub-065` | aggregation | `['5']` | ❌ | ✅ | ❌ | 2005 | 2200 | 9016 | 13.514s | 8.351s | 32.382s |
| `pub-066` | superlative | `["Weightlifting at the 1992 Summer Ol...` | ✅ | ✅ | ✅ | 1956 | 2724 | 6593 | 8.49s | 12.454s | 21.25s |
| `pub-067` | multi_hop | `['Rosannagh MacLennan']` | ✅ | ✅ | ❌ | 3364 | 875 | 2905 | 28.934s | 5.029s | 11.279s |
| `pub-068` | lookup | `['24']` | ✅ | ✅ | ✅ | 1863 | 3253 | 4211 | 22.577s | 9.656s | 16.94s |
| `pub-069` | aggregation | `['3']` | ❌ | ❌ | ✅ | 2088 | 1773 | 6809 | 31.814s | 5.283s | 21.612s |
| `pub-070` | aggregation | `['3']` | ❌ | ✅ | ✅ | 1846 | 1550 | 6779 | 24.107s | 5.513s | 21.615s |
| `pub-071` | lookup | `['24']` | ✅ | ✅ | ✅ | 1909 | 2694 | 7284 | 5.463s | 8.921s | 27.119s |
| `pub-072` | temporal | `['Lee Sang-hwa']` | ✅ | ✅ | ✅ | 2866 | 2357 | 6172 | 9.386s | 6.896s | 22.444s |
| `pub-073` | multi_hop | `['Yang Ling']` | ✅ | ✅ | ❌ | 2130 | 2627 | 6229 | 9.444s | 10.599s | 24.788s |
| `pub-074` | lookup | `['17']` | ✅ | ✅ | ✅ | 2411 | 2817 | 7610 | 6.02s | 9.557s | 28.174s |
| `pub-075` | lookup | `['32']` | ✅ | ✅ | ✅ | 1994 | 3654 | 2961 | 5.547s | 7.77s | 11.625s |
| `pub-076` | multi_hop | `['Julia Mancuso']` | ✅ | ❌ | ❌ | 2205 | 3321 | 3964 | 7.759s | 10.449s | 16.299s |
| `pub-077` | multi_hop | `['Kaillie Humphries']` | ✅ | ✅ | ❌ | 2890 | 1177 | 5651 | 10.381s | 5.508s | 26.321s |
| `pub-078` | aggregation | `['7']` | ❌ | ❌ | ✅ | 2074 | 2496 | 5436 | 4.896s | 5.805s | 18.006s |
| `pub-079` | multi_hop | `['Leontien Zijlaard']` | ✅ | ✅ | ✅ | 2350 | 923 | 2700 | 26.465s | 5.517s | 12.271s |
| `pub-080` | lookup | `['17']` | ✅ | ✅ | ✅ | 2556 | 1673 | 7334 | 24.182s | 8.392s | 26.95s |
| `pub-081` | multi_hop | `['Guo Wenjun']` | ✅ | ✅ | ❌ | 2327 | 2793 | 7242 | 28.867s | 9.393s | 27.346s |
| `pub-082` | aggregation | `['12']` | ❌ | ✅ | ✅ | 1969 | 2993 | 7337 | 32.084s | 22.693s | 22.416s |
| `pub-083` | multi_hop | `['Pernilla Wiberg']` | ✅ | ❌ | ✅ | 1924 | 3341 | 4203 | 5.886s | 8.732s | 19.908s |
| `pub-084` | superlative | `["Fencing at the 1992 Summer Olympics...` | ✅ | ✅ | ✅ | 1963 | 3159 | 6770 | 7.505s | 10.97s | 21.635s |
| `pub-085` | superlative | `["Sailing at the 2008 Summer Olympics...` | ❌ | ✅ | ✅ | 1882 | 3209 | 5034 | 23.191s | 11.713s | 17.368s |
| `pub-086` | multi_hop | `['Shani Davis']` | ✅ | ✅ | ✅ | 2154 | 1232 | 2670 | 23.859s | 4.965s | 11.411s |
| `pub-087` | aggregation | `['17']` | ❌ | ✅ | ✅ | 1966 | 3148 | 7573 | 21.693s | 6.637s | 22.743s |
| `pub-088` | superlative | `["Alpine skiing at the 1992 Winter Ol...` | ✅ | ✅ | ✅ | 1937 | 2831 | 6564 | 27.205s | 11.512s | 21.189s |
| `pub-089` | aggregation | `['5']` | ❌ | ✅ | ✅ | 2004 | 2418 | 6728 | 15.534s | 7.0s | 21.256s |
| `pub-090` | temporal | `['Aslanbek Khushtov']` | ✅ | ✅ | ✅ | 2586 | 1467 | 4161 | 26.167s | 5.841s | 16.465s |
| `pub-091` | lookup | `['18']` | ✅ | ✅ | ✅ | 1818 | 3685 | 2952 | 26.104s | 8.05s | 11.292s |
| `pub-092` | aggregation | `['6']` | ❌ | ❌ | ✅ | 1982 | 1956 | 6902 | 24.128s | 5.776s | 22.401s |
| `pub-093` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1885 | 2055 | 5223 | 9.866s | 10.252s | 19.009s |
| `pub-094` | temporal | `['Oleg Kucherenko']` | ✅ | ✅ | ✅ | 2000 | 1169 | 4159 | 8.522s | 5.632s | 16.285s |
| `pub-095` | multi_hop | `['Valerie Vili']` | ❌ | ✅ | ✅ | 3265 | 1717 | 2656 | 26.661s | 5.798s | 11.526s |
| `pub-096` | multi_hop | `['Fazliddin Gaibnazarov']` | ✅ | ✅ | ✅ | 2895 | 1175 | 2718 | 29.373s | 5.713s | 13.058s |
| `pub-097` | temporal | `['Yana Shemyakina']` | ✅ | ✅ | ✅ | 3061 | 2749 | 4129 | 30.668s | 7.838s | 15.108s |
| `pub-098` | multi_hop | `['Bekzat Sattarkhanov']` | ✅ | ✅ | ❌ | 1856 | 2273 | 8197 | 6.462s | 7.007s | 40.399s |
| `pub-099` | multi_hop | `['Erik LesserDaniel BöhmArnd PeifferS...` | ❌ | ❌ | ❌ | 2375 | 1229 | 2717 | 9.695s | 8.214s | 14.259s |
| `pub-100` | temporal | `['Missy Franklin']` | ✅ | ✅ | ✅ | 3055 | 1670 | 4141 | 9.667s | 5.724s | 15.631s |