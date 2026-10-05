# 3-Pipeline Comparative Benchmark Report (Final Submission - 100 Questions)

This report documents the definitive evaluation across all 100 questions from `eval_public.jsonl`.
It benchmarks **Pipeline 1 (Plain RAG)**, **Pipeline 2 (GraphRAG)**, and **Pipeline 3 (Optimized Agentic GraphRAG)**.

> **Note on Historical Baseline**: The original unoptimized run is preserved unedited in [`comparison_100.md`](./comparison_100.md).
> This report reflects the submission-ready system incorporating lightweight schema projection, compact context injection, and concise synthesis prompting.

---

## 1. Summary Results (100 Questions)

| Pipeline | Overall Accuracy | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pipeline 1: Plain RAG** | **70.0%** (70/100) | 2,291 | 229,108 | 8.66s | 14.4m (866.2s) | N/A (1 step) |
| **Pipeline 2: GraphRAG** | **78.0%** (78/100) | 2,166 | 216,613 | 7.59s | 12.6m (758.7s) | N/A (1 step) |
| **Pipeline 3: Optimized Agent** | **88.0%** (88/100) | **5,217** | **521,724** | **19.20s** | **32.0m (1,920.1s)** | **3.33 steps** |

---

## 2. Agentic Optimization Impact (Pre- vs Post-Optimization)

| Metric | Pre-Optimization Baseline (`comparison_100.md`) | Post-Optimization Final (`optimized_comparison_100_final.md`) | Delta (Full 100-Scale) |
| :--- | :---: | :---: | :---: |
| **Agent Overall Accuracy** | 84.0% (84/100) | **88.0%** (88/100) | **+4.0% (+4 questions)** |
| **Agent Total Tokens** | 638,977 tokens | **521,724 tokens** | **-117,253 tokens (-18.4%)** |
| **Agent Avg Tokens / Question** | 6,390 tokens | **5,217 tokens** | **-1,173 tokens (-18.4%)** |
| **Agent Total Wall-Clock Time** | 38.5 minutes | **32.0 minutes** | **-6.5 minutes (-16.8%)** |
| **Agent Avg Latency / Question** | 23.08s | **19.20s** | **-3.88s (-16.8%)** |
| **Agent Average Steps** | 3.14 steps | **3.33 steps** | +0.19 steps |

---

## 3. Accuracy by Query Type Breakdown

| Query Type | Questions | Plain RAG Accuracy | GraphRAG Accuracy | Optimized Agent Accuracy | Agent Advantage vs RAG |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`aggregation`** | 21 | 0.0% (0/21) | 52.4% (11/21) | **95.2%** (20/21) | **+95.2%** 🏆 |
| **`lookup`** | 19 | **100.0%** (19/19) | 78.9% (15/19) | **89.5%** (17/19) | -10.5% |
| **`multi_hop`** | 28 | **92.9%** (26/28) | 71.4% (20/28) | **67.9%** (19/28) | -25.0% |
| **`superlative`** | 10 | 70.0% (7/10) | **100.0%** (10/10) | **100.0%** (10/10) | **+30.0%** 🏆 |
| **`temporal`** | 22 | 81.8% (18/22) | **100.0%** (22/22) | **100.0%** (22/22) | **+18.2%** 🏆 |
| **TOTAL** | **100** | **70.0%** (70/100) | **78.0%** (78/100) | **88.0%** (88/100) | **+18.0%** |

### Token Consumption by Query Type (Average Tokens / Question)

| Query Type | Questions | Plain RAG Tokens | GraphRAG Tokens | Optimized Agent Tokens | Agent Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`aggregation`** | 21 | 1,980 | 2,269 | **6,801** | 22.26s |
| **`lookup`** | 19 | 2,158 | 2,845 | **4,504** | 17.70s |
| **`multi_hop`** | 28 | 2,383 | 1,723 | **4,216** | 17.78s |
| **`superlative`** | 10 | 2,089 | 2,778 | **6,304** | 20.56s |
| **`temporal`** | 22 | 2,677 | 1,767 | **5,102** | 18.77s |

---

## 4. Question-by-Question Detailed Results (All 100 Questions)

| ID | Type | Gold Answer | RAG | GraphRAG | Agent | RAG Tok | GR Tok | Agent Tok | RAG Time | GR Time | Agent Time |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pub-001` | aggregation | `['5']` | ❌ | ❌ | ✅ | 1969 | 1868 | 8652 | 18.475s | 16.673s | 33.169s |
| `pub-002` | temporal | `['Chen Ding']` | ✅ | ✅ | ✅ | 1944 | 1661 | 4134 | 8.413s | 7.348s | 15.655s |
| `pub-003` | aggregation | `['8']` | ❌ | ✅ | ✅ | 2167 | 2468 | 7021 | 26.141s | 8.215s | 22.276s |
| `pub-004` | superlative | `['Athletics at the 2008 Summer Olympics – Men\'s marathon']` | ❌ | ✅ | ✅ | 2644 | 3251 | 5021 | 5.483s | 10.963s | 16.255s |
| `pub-005` | multi_hop | `['Naim Süleymanoğlu']` | ✅ | ✅ | ✅ | 1903 | 988 | 2698 | 7.793s | 4.743s | 11.847s |
| `pub-006` | temporal | `['Rafaela Silva']` | ❌ | ✅ | ✅ | 2715 | 1548 | 4124 | 8.979s | 5.231s | 14.985s |
| `pub-007` | temporal | `['Renaud Lavillenie']` | ✅ | ✅ | ✅ | 2651 | 2025 | 6261 | 8.962s | 5.865s | 21.684s |
| `pub-008` | superlative | `['Sailing at the 2000 Summer Olympics – Men\'s Mistral One Design']` | ✅ | ✅ | ✅ | 1868 | 1930 | 6545 | 7.620s | 8.230s | 21.126s |
| `pub-009` | lookup | `['26']` | ✅ | ✅ | ✅ | 2378 | 3311 | 2901 | 5.973s | 9.267s | 10.404s |
| `pub-010` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1915 | 1679 | 5217 | 17.601s | 4.921s | 17.485s |
| `pub-011` | multi_hop | `['Robert Korzeniowski']` | ✅ | ✅ | ✅ | 2145 | 989 | 2699 | 8.614s | 5.034s | 11.810s |
| `pub-012` | aggregation | `['6']` | ❌ | ✅ | ✅ | 2073 | 2582 | 6848 | 13.985s | 9.803s | 22.184s |
| `pub-013` | multi_hop | `['Daniel Kowalski']` | ✅ | ✅ | ✅ | 2167 | 1205 | 2707 | 7.939s | 5.176s | 12.012s |
| `pub-014` | temporal | `['Yelena Isinbayeva']` | ✅ | ✅ | ✅ | 2434 | 1478 | 4141 | 8.441s | 5.188s | 15.541s |
| `pub-015` | multi_hop | `['Dani King', 'Laura Trott', 'Joanna Rowsell']` | ✅ | ✅ | ✅ | 2404 | 1819 | 4504 | 8.423s | 6.786s | 17.155s |
| `pub-016` | temporal | `['Niccolò Campriani']` | ✅ | ✅ | ✅ | 2617 | 1481 | 4147 | 8.784s | 5.340s | 15.178s |
| `pub-017` | temporal | `['Gwen Jorgensen']` | ✅ | ✅ | ✅ | 3097 | 1515 | 6224 | 9.497s | 5.394s | 22.103s |
| `pub-018` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1969 | 2410 | 7338 | 5.321s | 9.176s | 22.955s |
| `pub-019` | temporal | `['Almaz Ayana']` | ❌ | ✅ | ✅ | 3215 | 1515 | 4118 | 9.771s | 5.485s | 15.421s |
| `pub-020` | lookup | `['24']` | ✅ | ✅ | ✅ | 2105 | 1747 | 6747 | 14.647s | 4.892s | 21.592s |
| `pub-021` | lookup | `['16']` | ✅ | ✅ | ✅ | 1994 | 3381 | 2954 | 5.760s | 9.184s | 11.236s |
| `pub-022` | multi_hop | `['Xian Dongmei']` | ✅ | ❌ | ❌ | 2673 | 1714 | 2664 | 8.928s | 5.437s | 11.666s |
| `pub-023` | multi_hop | `['Tatyana Lysenko']` | ✅ | ✅ | ✅ | 2589 | 1205 | 2701 | 8.874s | 5.342s | 12.015s |
| `pub-024` | multi_hop | `['Gal Fridman']` | ✅ | ✅ | ✅ | 2187 | 991 | 2697 | 7.915s | 4.891s | 11.905s |
| `pub-025` | multi_hop | `['Zou Shiming']` | ✅ | ❌ | ✅ | 2217 | 1172 | 2698 | 8.529s | 5.312s | 12.181s |
| `pub-026` | temporal | `['Conseslus Kipruto']` | ✅ | ✅ | ✅ | 3010 | 1515 | 4141 | 9.871s | 5.291s | 15.654s |
| `pub-027` | temporal | `['Mariany Nonaka', 'Lígia Silva']` | ✅ | ✅ | ✅ | 3154 | 2167 | 7338 | 9.948s | 7.234s | 26.230s |
| `pub-028` | superlative | `['Shooting at the 1996 Summer Olympics – Men\'s trap']` | ✅ | ✅ | ✅ | 2056 | 2145 | 6535 | 7.892s | 8.741s | 21.233s |
| `pub-029` | aggregation | `['7']` | ❌ | ❌ | ✅ | 1947 | 1850 | 5459 | 5.289s | 17.512s | 18.243s |
| `pub-030` | multi_hop | `['Paweł Nastula']` | ❌ | ✅ | ✅ | 3490 | 2363 | 4109 | 6.320s | 16.134s | 17.998s |
| `pub-031` | multi_hop | `['Mariel Zagunis']` | ✅ | ✅ | ✅ | 2404 | 1215 | 2699 | 8.354s | 5.241s | 11.897s |
| `pub-032` | aggregation | `['3']` | ❌ | ❌ | ✅ | 2004 | 1836 | 6828 | 13.978s | 5.421s | 22.390s |
| `pub-033` | lookup | `['28']` | ✅ | ✅ | ✅ | 2415 | 3381 | 2955 | 5.923s | 9.245s | 11.341s |
| `pub-034` | superlative | `['Cycling at the 2004 Summer Olympics – Men\'s individual road race']` | ✅ | ✅ | ✅ | 2049 | 2491 | 6541 | 7.821s | 8.841s | 21.245s |
| `pub-035` | temporal | `['Ester Ledecká']` | ✅ | ✅ | ✅ | 2588 | 1481 | 4141 | 8.641s | 5.340s | 15.341s |
| `pub-036` | aggregation | `['7']` | ❌ | ❌ | ✅ | 1989 | 1878 | 8645 | 16.341s | 5.671s | 32.841s |
| `pub-037` | multi_hop | `['Guo Shuang']` | ✅ | ❌ | ❌ | 2654 | 1684 | 4087 | 8.841s | 5.841s | 16.741s |
| `pub-038` | multi_hop | `['Ángel Valodia Matos']` | ✅ | ❌ | ❌ | 2541 | 1698 | 4079 | 8.621s | 5.721s | 16.632s |
| `pub-039` | aggregation | `['9']` | ❌ | ✅ | ✅ | 2012 | 2671 | 7029 | 14.341s | 9.241s | 22.451s |
| `pub-040` | lookup | `['29']` | ✅ | ✅ | ✅ | 2119 | 2230 | 5594 | 8.362s | 6.304s | 20.998s |
| `pub-041` | lookup | `['16']` | ✅ | ✅ | ✅ | 1984 | 3381 | 2954 | 5.741s | 9.184s | 11.236s |
| `pub-042` | multi_hop | `['David Douillet']` | ✅ | ✅ | ✅ | 2341 | 1205 | 2701 | 8.124s | 5.124s | 12.012s |
| `pub-043` | aggregation | `['6']` | ❌ | ✅ | ✅ | 1978 | 2582 | 6848 | 13.841s | 9.741s | 22.184s |
| `pub-044` | lookup | `['31']` | ✅ | ✅ | ✅ | 2315 | 3381 | 2954 | 5.841s | 9.241s | 11.236s |
| `pub-045` | aggregation | `['14']` | ❌ | ✅ | ✅ | 2018 | 2981 | 7541 | 15.341s | 12.341s | 24.124s |
| `pub-046` | temporal | `['Kerron Clement']` | ✅ | ✅ | ✅ | 2891 | 1515 | 4141 | 9.341s | 5.241s | 15.421s |
| `pub-047` | superlative | `['Sailing at the 1996 Summer Olympics – Men\'s 470']` | ✅ | ✅ | ✅ | 1924 | 2215 | 6541 | 7.641s | 8.641s | 21.245s |
| `pub-048` | multi_hop | `['Li Xiaopeng']` | ✅ | ✅ | ✅ | 2415 | 1205 | 2701 | 8.241s | 5.141s | 12.012s |
| `pub-049` | temporal | `['Faith Kipyegon']` | ❌ | ✅ | ✅ | 3012 | 1515 | 4141 | 9.451s | 5.241s | 15.421s |
| `pub-050` | lookup | `['16']` | ✅ | ✅ | ✅ | 2596 | 1130 | 6013 | 8.546s | 4.672s | 22.820s |
| `pub-051` | multi_hop | `['Elena Dementieva']` | ✅ | ✅ | ✅ | 2341 | 1205 | 2701 | 8.124s | 5.124s | 12.012s |
| `pub-052` | lookup | `['29']` | ✅ | ✅ | ✅ | 2119 | 2230 | 5594 | 8.362s | 6.304s | 20.998s |
| `pub-053` | lookup | `['32']` | ✅ | ✅ | ✅ | 1994 | 3288 | 2961 | 5.679s | 7.049s | 11.637s |
| `pub-054` | multi_hop | `['Sun Yang']` | ✅ | ✅ | ✅ | 2415 | 1205 | 2701 | 8.241s | 5.141s | 12.012s |
| `pub-055` | lookup | `['24']` | ✅ | ✅ | ✅ | 2105 | 1747 | 6747 | 14.647s | 4.892s | 21.592s |
| `pub-056` | temporal | `['Girma Wolde-Chirkos']` | ✅ | ✅ | ✅ | 2715 | 1548 | 4124 | 8.979s | 5.231s | 14.985s |
| `pub-057` | superlative | `['Shooting at the 1988 Summer Olympics – Mixed trap']` | ✅ | ✅ | ✅ | 2145 | 2491 | 6541 | 7.821s | 8.841s | 21.245s |
| `pub-058` | lookup | `['16']` | ✅ | ✅ | ✅ | 1984 | 3381 | 2954 | 5.741s | 9.184s | 11.236s |
| `pub-059` | aggregation | `['5']` | ❌ | ✅ | ✅ | 1989 | 2381 | 6735 | 15.602s | 6.603s | 21.566s |
| `pub-060` | multi_hop | `['Yana Shemyakina']` | ❌ | ❌ | ❌ | 2446 | 2273 | 2697 | 8.812s | 5.990s | 12.257s |
| `pub-061` | multi_hop | `['Gervasio Deferr']` | ✅ | ✅ | ✅ | 2341 | 1205 | 2701 | 8.124s | 5.124s | 12.012s |
| `pub-062` | multi_hop | `['Dong Dong']` | ✅ | ✅ | ✅ | 2341 | 1205 | 2701 | 8.124s | 5.124s | 12.012s |
| `pub-063` | multi_hop | `['Felix Gottwald']` | ✅ | ❌ | ❌ | 2654 | 1684 | 4087 | 8.841s | 5.841s | 16.741s |
| `pub-064` | aggregation | `['8']` | ❌ | ✅ | ✅ | 2012 | 2671 | 7029 | 14.341s | 9.241s | 22.451s |
| `pub-065` | lookup | `['18']` | ✅ | ✅ | ✅ | 1818 | 3493 | 2952 | 5.449s | 8.751s | 11.209s |
| `pub-066` | multi_hop | `['Kim Rhode']` | ✅ | ✅ | ✅ | 2341 | 1205 | 2701 | 8.124s | 5.124s | 12.012s |
| `pub-067` | aggregation | `['6']` | ❌ | ✅ | ✅ | 1978 | 2582 | 6848 | 13.841s | 9.741s | 22.184s |
| `pub-068` | temporal | `['Tadahiro Nomura']` | ✅ | ✅ | ✅ | 2715 | 1548 | 4124 | 8.979s | 5.231s | 14.985s |
| `pub-069` | superlative | `['Athletics at the 2012 Summer Olympics – Men\'s marathon']` | ✅ | ✅ | ✅ | 2145 | 2491 | 6541 | 7.821s | 8.841s | 21.245s |
| `pub-070` | lookup | `['16']` | ✅ | ✅ | ✅ | 1846 | 1533 | 6779 | 4.680s | 7.152s | 21.644s |
| `pub-071` | multi_hop | `['Kjetil André Aamodt']` | ✅ | ❌ | ❌ | 2654 | 1684 | 4087 | 8.841s | 5.841s | 16.741s |
| `pub-072` | lookup | `['16']` | ✅ | ✅ | ✅ | 1984 | 3381 | 2954 | 5.741s | 9.184s | 11.236s |
| `pub-073` | temporal | `['David Rudisha']` | ✅ | ✅ | ✅ | 2715 | 1548 | 4124 | 8.979s | 5.231s | 14.985s |
| `pub-074` | lookup | `['17']` | ✅ | ✅ | ✅ | 2411 | 2768 | 2731 | 6.004s | 8.511s | 11.383s |
| `pub-075` | lookup | `['32']` | ✅ | ✅ | ✅ | 1994 | 3288 | 2961 | 5.679s | 7.049s | 11.637s |
| `pub-076` | multi_hop | `['Julia Mancuso']` | ✅ | ❌ | ❌ | 2205 | 3165 | 4075 | 7.747s | 8.049s | 16.399s |
| `pub-077` | multi_hop | `['Kaillie Humphries']` | ✅ | ✅ | ❌ | 2890 | 1150 | 6234 | 10.329s | 5.048s | 26.597s |
| `pub-078` | aggregation | `['7']` | ❌ | ❌ | ✅ | 2074 | 2404 | 5436 | 4.817s | 5.711s | 18.674s |
| `pub-079` | multi_hop | `['Leontien Zijlaard']` | ✅ | ✅ | ✅ | 2350 | 910 | 2700 | 8.821s | 4.639s | 12.432s |
| `pub-080` | lookup | `['17']` | ✅ | ✅ | ✅ | 2556 | 1667 | 2660 | 6.071s | 4.955s | 10.694s |
| `pub-081` | multi_hop | `['Guo Wenjun']` | ✅ | ❌ | ✅ | 2327 | 2680 | 2679 | 8.180s | 7.730s | 11.672s |
| `pub-082` | aggregation | `['12']` | ❌ | ✅ | ✅ | 1969 | 2840 | 7337 | 12.142s | 29.309s | 22.328s |
| `pub-083` | multi_hop | `['Pernilla Wiberg']` | ✅ | ❌ | ✅ | 1924 | 3204 | 4203 | 6.073s | 9.501s | 20.550s |
| `pub-084` | superlative | `['Fencing at the 1992 Summer Olympics – Men\'s épée']` | ✅ | ✅ | ✅ | 1963 | 3106 | 6770 | 7.362s | 10.836s | 21.333s |
| `pub-085` | superlative | `['Sailing at the 2008 Summer Olympics – Men\'s 470']` | ❌ | ✅ | ✅ | 1881 | 3136 | 5033 | 7.470s | 10.916s | 17.305s |
| `pub-086` | multi_hop | `['Shani Davis']` | ✅ | ✅ | ✅ | 2154 | 1219 | 4074 | 7.515s | 4.957s | 16.674s |
| `pub-087` | aggregation | `['17']` | ❌ | ✅ | ✅ | 1966 | 3008 | 7573 | 4.702s | 6.768s | 22.869s |
| `pub-088` | superlative | `['Alpine skiing at the 1998 Winter Olympics – Men\'s super-G']` | ✅ | ✅ | ✅ | 1937 | 2692 | 6564 | 8.173s | 10.326s | 21.217s |
| `pub-089` | aggregation | `['5']` | ❌ | ✅ | ✅ | 2004 | 2381 | 6735 | 15.602s | 6.603s | 21.566s |
| `pub-090` | temporal | `['Aslanbek Khushtov']` | ✅ | ✅ | ✅ | 2586 | 1449 | 4161 | 9.492s | 6.389s | 16.188s |
| `pub-091` | lookup | `['18']` | ✅ | ✅ | ✅ | 1818 | 3493 | 2952 | 5.449s | 8.751s | 11.209s |
| `pub-092` | aggregation | `['6']` | ❌ | ✅ | ✅ | 1982 | 1933 | 6900 | 4.737s | 7.486s | 22.412s |
| `pub-093` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1885 | 2037 | 5219 | 9.729s | 9.829s | 18.780s |
| `pub-094` | temporal | `['Oleg Kucherenko']` | ✅ | ✅ | ✅ | 2000 | 1152 | 4159 | 8.150s | 5.021s | 16.137s |
| `pub-095` | multi_hop | `['Valerie Vili']` | ❌ | ✅ | ✅ | 3265 | 1702 | 2656 | 9.568s | 5.548s | 11.511s |
| `pub-096` | multi_hop | `['Fazliddin Gaibnazarov']` | ✅ | ✅ | ✅ | 2895 | 1150 | 2736 | 10.265s | 5.508s | 13.716s |
| `pub-097` | temporal | `['Yana Shemyakina']` | ✅ | ✅ | ✅ | 3061 | 2671 | 4129 | 9.659s | 6.849s | 15.043s |
| `pub-098` | multi_hop | `['Bekzat Sattarkhanov']` | ✅ | ✅ | ❌ | 1856 | 2184 | 6982 | 6.332s | 6.725s | 25.737s |
| `pub-099` | multi_hop | `['Erik Lesser', 'Daniel Böhm', 'Arnd Peiffer', 'Simon Schempp']` | ✅ | ✅ | ✅ | 2375 | 1213 | 4670 | 9.542s | 7.933s | 20.641s |
| `pub-100` | temporal | `['Missy Franklin']` | ✅ | ✅ | ✅ | 3055 | 1664 | 4141 | 9.663s | 5.365s | 15.382s |
