# 3-Pipeline Comparative Benchmark Report (Final Submission - 100 Questions)

This report documents the definitive evaluation across all 100 questions from `eval_public.jsonl`.
It benchmarks **Pipeline 1 (Plain RAG)**, **Pipeline 2 (GraphRAG)**, and **Pipeline 3 (Optimized Agentic GraphRAG)**.

> **Note on Historical Baseline**: The original unoptimized run is preserved unedited in `comparison_100.md`.
> This report (`comparison_100_final.md`) reflects the submission-ready system incorporating lightweight schema projection, compact context injection, and concise synthesis prompting.

---

## 1. Summary Results (100 Questions)

| Pipeline | Overall Accuracy | Avg Tokens / Q | Total Tokens | Avg Latency (s) | Total Wall-Clock | Agent Avg Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pipeline 1: Plain RAG** | **70.0%** (70/100) | 2291 | 229,108 | 8.66s | 14.4m (866.2s) | N/A (1 step) |
| **Pipeline 2: GraphRAG** | **78.0%** (78/100) | 2166 | 216,613 | 7.59s | 12.6m (758.7s) | N/A (1 step) |
| **Pipeline 3: Optimized Agent** | **88.0%** (88/100) | **5217** | **521,724** | **19.20s** | **32.0m (1920.1s)** | **3.33 steps** |

---

## 2. Accuracy by Query Type Breakdown

| Query Type | Questions | Plain RAG Accuracy | GraphRAG Accuracy | Optimized Agent Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 0.0% | 52.4% | **95.2%** |
| **lookup** | 19 | 100.0% | 78.9% | **89.5%** |
| **multi_hop** | 28 | 92.9% | 71.4% | **67.9%** |
| **superlative** | 10 | 70.0% | 100.0% | **100.0%** |
| **temporal** | 22 | 81.8% | 100.0% | **100.0%** |

### Token Consumption by Query Type (Average Tokens / Question)

| Query Type | Questions | Plain RAG Tokens | GraphRAG Tokens | Optimized Agent Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **aggregation** | 21 | 1980 | 2269 | **6801** |
| **lookup** | 19 | 2158 | 2845 | **4504** |
| **multi_hop** | 28 | 2383 | 1723 | **4216** |
| **superlative** | 10 | 2089 | 2778 | **6304** |
| **temporal** | 22 | 2677 | 1767 | **5102** |

---

## 3. Question-by-Question Detailed Results (All 100 Questions)

| ID | Type | Gold Answer | RAG | GraphRAG | Agent | RAG Tok | GR Tok | Agent Tok | RAG Time | GR Time | Agent Time |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pub-001` | aggregation | `['5']` | ❌ | ❌ | ✅ | 1969 | 1868 | 8652 | 18.475s | 16.673s | 33.169s |
| `pub-002` | temporal | `['Chen Ding']` | ✅ | ✅ | ✅ | 1944 | 1661 | 4134 | 8.413s | 7.348s | 15.655s |
| `pub-003` | aggregation | `['8']` | ❌ | ✅ | ✅ | 2167 | 2468 | 7021 | 26.141s | 8.215s | 22.276s |
| `pub-004` | superlative | `["Athletics at the 200...` | ❌ | ✅ | ✅ | 2644 | 3251 | 5021 | 5.483s | 10.963s | 16.255s |
| `pub-005` | multi_hop | `['Naim Süleymanoğlu']` | ✅ | ✅ | ✅ | 1903 | 988 | 2698 | 7.793s | 4.743s | 11.847s |
| `pub-006` | temporal | `['Rafaela Silva']` | ❌ | ✅ | ✅ | 2715 | 1548 | 4124 | 8.979s | 5.231s | 14.985s |
| `pub-007` | temporal | `['Renaud Lavillenie']` | ✅ | ✅ | ✅ | 2651 | 2025 | 6261 | 8.962s | 5.865s | 21.684s |
| `pub-008` | superlative | `['Sailing at the 2000 ...` | ✅ | ✅ | ✅ | 1868 | 1930 | 6545 | 7.620s | 8.230s | 21.126s |
| `pub-009` | lookup | `['26']` | ✅ | ✅ | ✅ | 2378 | 3311 | 2901 | 5.973s | 9.267s | 10.404s |
| `pub-010` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1915 | 1679 | 5217 | 17.601s | 4.921s | 17.485s |
| `pub-011` | multi_hop | `['Martina Sáblíková']` | ✅ | ✅ | ✅ | 2101 | 1423 | 4095 | 7.848s | 5.246s | 16.784s |
| `pub-012` | aggregation | `['6']` | ❌ | ❌ | ✅ | 1911 | 2649 | 5524 | 4.651s | 5.904s | 18.047s |
| `pub-013` | temporal | `['Allison Schmitt']` | ✅ | ✅ | ✅ | 2911 | 1576 | 5771 | 9.369s | 5.219s | 22.039s |
| `pub-014` | multi_hop | `['Carolina Marín']` | ✅ | ✅ | ✅ | 2243 | 1159 | 2712 | 9.158s | 4.735s | 12.276s |
| `pub-015` | multi_hop | `['Dani KingLaura Trott...` | ✅ | ✅ | ✅ | 2488 | 1296 | 2706 | 10.220s | 7.388s | 12.494s |
| `pub-016` | temporal | `['Arnd Peiffer']` | ✅ | ✅ | ✅ | 2347 | 2005 | 7781 | 8.315s | 5.784s | 25.831s |
| `pub-017` | multi_hop | `['Yi Siling']` | ✅ | ✅ | ✅ | 1894 | 1028 | 2679 | 7.522s | 4.486s | 11.451s |
| `pub-018` | temporal | `['Kevin Jackson']` | ✅ | ✅ | ✅ | 2793 | 1118 | 4135 | 9.145s | 4.393s | 15.285s |
| `pub-019` | aggregation | `['3']` | ❌ | ✅ | ✅ | 2064 | 2494 | 6909 | 8.312s | 5.786s | 21.294s |
| `pub-020` | aggregation | `['4']` | ❌ | ❌ | ✅ | 2105 | 1747 | 6747 | 14.647s | 4.892s | 21.592s |
| `pub-021` | superlative | `["Alpine skiing at the...` | ✅ | ✅ | ✅ | 1908 | 2599 | 6529 | 8.011s | 9.714s | 20.516s |
| `pub-022` | multi_hop | `['Ayumi Tanimoto']` | ✅ | ❌ | ❌ | 2697 | 2335 | 6580 | 8.944s | 10.624s | 25.506s |
| `pub-023` | multi_hop | `['Hwang Young-Cho']` | ✅ | ❌ | ✅ | 2112 | 2915 | 4587 | 6.013s | 10.135s | 18.524s |
| `pub-024` | aggregation | `['3']` | ❌ | ❌ | ✅ | 1882 | 2052 | 6725 | 8.186s | 5.350s | 22.624s |
| `pub-025` | lookup | `['23']` | ✅ | ❌ | ✅ | 2230 | 3006 | 4238 | 5.768s | 6.763s | 17.394s |
| `pub-026` | temporal | `['Jaroslav Kulhavý']` | ✅ | ✅ | ✅ | 2153 | 1821 | 6254 | 8.603s | 6.231s | 22.068s |
| `pub-027` | aggregation | `['4']` | ❌ | ❌ | ✅ | 1873 | 1968 | 6904 | 13.195s | 5.826s | 21.820s |
| `pub-028` | multi_hop | `['Michael Phelps']` | ✅ | ❌ | ❌ | 2241 | 3573 | 9398 | 9.438s | 14.621s | 34.265s |
| `pub-029` | lookup | `['28']` | ✅ | ✅ | ✅ | 1773 | 2597 | 2930 | 5.345s | 6.320s | 11.842s |
| `pub-030` | multi_hop | `['Emese Szász']` | ❌ | ❌ | ✅ | 3490 | 2363 | 4109 | 6.320s | 16.134s | 17.998s |
| `pub-031` | multi_hop | `['Dmitry Berestov']` | ✅ | ✅ | ✅ | 1927 | 903 | 2700 | 7.885s | 4.641s | 17.033s |
| `pub-032` | lookup | `['34']` | ✅ | ❌ | ✅ | 2773 | 3144 | 2905 | 6.852s | 9.923s | 11.382s |
| `pub-033` | aggregation | `['4']` | ❌ | ✅ | ✅ | 1998 | 2349 | 6774 | 4.957s | 6.546s | 21.847s |
| `pub-034` | lookup | `['23']` | ✅ | ✅ | ✅ | 2296 | 2020 | 5714 | 7.603s | 7.589s | 22.432s |
| `pub-035` | lookup | `['30']` | ✅ | ✅ | ✅ | 1838 | 2748 | 2935 | 5.637s | 6.314s | 11.498s |
| `pub-036` | temporal | `['Zou Shiming']` | ✅ | ✅ | ✅ | 2308 | 1381 | 4112 | 8.249s | 5.106s | 15.214s |
| `pub-037` | superlative | `["Shooting at the 2008...` | ❌ | ✅ | ✅ | 2298 | 3173 | 6613 | 8.352s | 10.618s | 22.153s |
| `pub-038` | multi_hop | `['Pyrros Dimas']` | ✅ | ✅ | ✅ | 1962 | 1200 | 2680 | 7.657s | 5.128s | 12.028s |
| `pub-039` | temporal | `['Sandra Perković']` | ✅ | ✅ | ✅ | 2995 | 1479 | 4118 | 9.505s | 6.211s | 15.413s |
| `pub-040` | temporal | `['Jason Lamy Chappuis']` | ✅ | ✅ | ✅ | 2119 | 2230 | 5594 | 8.362s | 6.304s | 20.998s |
| `pub-041` | multi_hop | `['Nino Schurter']` | ✅ | ✅ | ✅ | 2273 | 787 | 4516 | 8.504s | 4.646s | 17.742s |
| `pub-042` | lookup | `['47']` | ✅ | ✅ | ❌ | 1663 | 2631 | 4236 | 5.078s | 8.320s | 17.098s |
| `pub-043` | multi_hop | `['Kjetil André Aamodt']` | ✅ | ✅ | ✅ | 2392 | 1141 | 4116 | 8.412s | 4.964s | 17.791s |
| `pub-044` | superlative | `["Fencing at the 2008 ...` | ✅ | ✅ | ✅ | 2166 | 2435 | 6745 | 8.043s | 9.776s | 22.913s |
| `pub-045` | aggregation | `['20']` | ❌ | ❌ | ✅ | 1965 | 3059 | 6228 | 10.987s | 6.844s | 19.736s |
| `pub-046` | lookup | `['50']` | ✅ | ✅ | ✅ | 2211 | 2793 | 7396 | 5.763s | 9.362s | 29.265s |
| `pub-047` | lookup | `['24']` | ✅ | ✅ | ✅ | 1935 | 3263 | 7476 | 5.484s | 10.475s | 28.273s |
| `pub-048` | temporal | `['Servet Tazegül']` | ❌ | ✅ | ✅ | 3697 | 1741 | 4147 | 10.729s | 5.809s | 15.767s |
| `pub-049` | temporal | `['Martin Fourcade']` | ✅ | ✅ | ✅ | 2413 | 1895 | 7741 | 8.563s | 6.605s | 26.758s |
| `pub-050` | multi_hop | `['Lee Sang-hwa']` | ✅ | ✅ | ✅ | 2596 | 1130 | 6013 | 8.546s | 4.672s | 22.820s |
| `pub-051` | aggregation | `['6']` | ❌ | ✅ | ✅ | 2000 | 2879 | 7266 | 16.921s | 22.306s | 23.589s |
| `pub-052` | lookup | `['20']` | ✅ | ✅ | ✅ | 2056 | 2754 | 7433 | 5.777s | 8.926s | 27.684s |
| `pub-053` | superlative | `["Shooting at the 2016...` | ✅ | ✅ | ✅ | 2272 | 2910 | 6625 | 8.337s | 10.380s | 21.040s |
| `pub-054` | lookup | `['24']` | ✅ | ✅ | ✅ | 2572 | 3163 | 7375 | 6.238s | 7.256s | 27.253s |
| `pub-055` | temporal | `['Sebastián Crismanich']` | ❌ | ✅ | ✅ | 3319 | 1844 | 5781 | 14.238s | 5.950s | 22.050s |
| `pub-056` | temporal | `['Yevgeny Dementyev']` | ✅ | ✅ | ✅ | 2690 | 1601 | 4075 | 9.734s | 5.473s | 16.232s |
| `pub-057` | temporal | `['Allyson Felix']` | ❌ | ✅ | ✅ | 3036 | 1547 | 4126 | 9.698s | 5.112s | 15.221s |
| `pub-058` | aggregation | `['5']` | ❌ | ❌ | ✅ | 1931 | 2448 | 7038 | 11.019s | 5.829s | 21.837s |
| `pub-059` | temporal | `['Laura Dahlmeier']` | ✅ | ✅ | ✅ | 2466 | 1363 | 5546 | 8.432s | 5.087s | 19.722s |
| `pub-060` | multi_hop | `['Yana Shemyakina']` | ✅ | ❌ | ❌ | 2446 | 2273 | 2697 | 8.812s | 5.990s | 12.257s |
| `pub-061` | lookup | `['34']` | ✅ | ✅ | ✅ | 2150 | 2907 | 2903 | 7.435s | 6.746s | 10.061s |
| `pub-062` | temporal | `['Tirunesh Dibaba']` | ✅ | ✅ | ✅ | 2777 | 2767 | 5791 | 9.320s | 6.846s | 22.566s |
| `pub-063` | lookup | `['41']` | ✅ | ❌ | ❌ | 2567 | 2974 | 4330 | 6.218s | 9.485s | 23.074s |
| `pub-064` | multi_hop | `['Gabriela Szabo']` | ✅ | ✅ | ❌ | 2232 | 1726 | 5605 | 10.074s | 5.539s | 24.205s |
| `pub-065` | aggregation | `['5']` | ❌ | ❌ | ❌ | 2002 | 2105 | 9021 | 13.025s | 5.270s | 32.351s |
| `pub-066` | superlative | `["Weightlifting at the...` | ✅ | ✅ | ✅ | 1956 | 2549 | 6594 | 8.230s | 9.788s | 21.695s |
| `pub-067` | multi_hop | `['Rosannagh MacLennan']` | ✅ | ✅ | ❌ | 3364 | 868 | 2905 | 9.985s | 4.635s | 11.131s |
| `pub-068` | lookup | `['24']` | ✅ | ❌ | ✅ | 1863 | 3085 | 4211 | 5.480s | 7.082s | 16.889s |
| `pub-069` | aggregation | `['3']` | ❌ | ✅ | ✅ | 2080 | 1757 | 6809 | 9.474s | 5.363s | 21.586s |
| `pub-070` | aggregation | `['3']` | ❌ | ✅ | ✅ | 1846 | 1533 | 6779 | 4.680s | 7.152s | 21.644s |
| `pub-071` | lookup | `['24']` | ✅ | ✅ | ✅ | 1909 | 2444 | 7284 | 5.518s | 8.948s | 26.855s |
| `pub-072` | temporal | `['Lee Sang-hwa']` | ✅ | ✅ | ✅ | 2866 | 2339 | 6172 | 9.251s | 6.379s | 22.616s |
| `pub-073` | multi_hop | `['Yang Ling']` | ✅ | ✅ | ❌ | 2130 | 2556 | 6242 | 9.380s | 9.964s | 25.780s |
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
| `pub-084` | superlative | `["Fencing at the 1992 ...` | ✅ | ✅ | ✅ | 1963 | 3106 | 6770 | 7.362s | 10.836s | 21.333s |
| `pub-085` | superlative | `["Sailing at the 2008 ...` | ❌ | ✅ | ✅ | 1881 | 3136 | 5033 | 7.470s | 10.916s | 17.305s |
| `pub-086` | multi_hop | `['Shani Davis']` | ✅ | ✅ | ✅ | 2154 | 1219 | 4074 | 7.515s | 4.957s | 16.674s |
| `pub-087` | aggregation | `['17']` | ❌ | ✅ | ✅ | 1966 | 3008 | 7573 | 4.702s | 6.768s | 22.869s |
| `pub-088` | superlative | `["Alpine skiing at the...` | ✅ | ✅ | ✅ | 1937 | 2692 | 6564 | 8.173s | 10.326s | 21.217s |
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
| `pub-099` | multi_hop | `['Erik LesserDaniel Bö...` | ✅ | ✅ | ✅ | 2375 | 1213 | 4670 | 9.542s | 7.933s | 20.641s |
| `pub-100` | temporal | `['Missy Franklin']` | ✅ | ✅ | ✅ | 3055 | 1664 | 4141 | 9.663s | 5.365s | 15.382s |
