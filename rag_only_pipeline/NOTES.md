# Benchmark Findings & Structural Insights for Pipeline 1 (Plain RAG)

This document logs empirical findings, structural failure modes, and retrieval characteristics observed during the development and benchmarking of the standalone RAG pipeline (`rag_only_pipeline`). These insights are preserved for the final hackathon comparison writeup (RAG vs GraphRAG vs Agentic GraphRAG).

---

## 1. Finding 1: Structural Under-Retrieval on Aggregation & Superlative Queries
* **Observation**: In Step 2 BM25 benchmarking across all 100 public questions:
  * **Hit@8** was **100.0%** for both `aggregation` and `superlative` questions.
  * **Frac@8** was only **54.3%** for `aggregation` and **61.3%** for `superlative`.
* **Root Cause**: Many aggregation questions (e.g. *"how many shooting events at the 2004 Summer Olympics had more than 37 competitors?"*) and superlative questions have 10 to 45 gold candidate documents in the corpus.
* **Empirical Confirmation on Eval Sample**:
  * **Manifestation A — Partial / Undercounting (`pub-001`, `pub-003`, `pub-010`)**:
    * **`pub-001`**: Gold answer = 5, got = 4 (under-counted because only 4 relevant candidate documents were retrieved within the $k=8$ budget).
    * **`pub-003`**: Gold answer = 8, got = 3 (under-counted because only 3 relevant candidate documents were retrieved within the $k=8$ budget).
    * **`pub-010`**: Gold answer = 4, got = 2 (under-counted; correctly evaluated the 4 retrieved cycling events but missed the 2 outside top-8).
    * **Mechanism**: The model correctly reasons over what it was given, but cannot synthesize evidence that was truncated by top-$k$ retrieval.
  * **Manifestation B — Honest Refusal / "not found in corpus" (`pub-004`)**:
    * **`pub-004`**: Question asks which 2008 athletics event had the highest number of competitors (Gold: *"Athletics at the 2008 Summer Olympics – Men's marathon"*).
    * **Behavior**: The marathon chunk was entirely ranked outside the top 8 by lexical BM25. Finding no qualifying candidate in the retrieved context, the LLM adhered strictly to grounding instructions and returned `"not found in corpus"` in 2.8s.
    * **Divergence**: Both Manifestation A and B stem from the identical $k=8$ retrieval gap, but manifest differently depending on whether partial evidence allows a plausible (under-counted) answer or leaves the model with zero valid candidates (honest refusal).
* **Architectural Comparison**:
  * **RAG**: Fails to provide complete candidate sets due to fixed context window and top-$k$ chunk truncation.
  * **Agentic GraphRAG**: Uses deterministic tool `get_events(games="2004 Summer", sport="Shooting", limit=1000)` followed by `count_or_rank(metric="competitors", operation="count", threshold=37, threshold_op="gt")` to compute exact counts across all 17 candidate events directly in the graph.

---

## 2. Finding 2: Lexical-Overlap Failure on Temporal Queries (`pub-002`)
* **Observation**:
  * **Question (`pub-002`)**: *"Who won the gold medal in the men's 20 kilometres walk athletics event at the Summer Olympics held immediately before 2016?"*
  * **Gold Target**: 2012 Summer Olympics Men's 20 km walk (`Q1050909`), won by **Chen Ding**.
  * **Plain RAG Retrieval**: Top retrieved chunk was `Q26225938#c1` (the 2016 Summer Olympics event), resulting in the answer **Wang Zhen** (the 2016 winner).
* **Root Cause**: Plain lexical BM25 matching strongly scores on the token `"2016"`, retrieving documents from the 2016 Games rather than resolving the relative temporal relation *"immediately before 2016"* $\to$ 2012.
* **Architectural Comparison**:
  * **RAG**: Vulnerable to distractor years and superficial lexical matches.
  * **Agentic GraphRAG**: Invokes `link_entities("immediately before 2016")` $\to$ resolves to `"2012 Summer Olympics"`, then queries the knowledge graph specifically for `games="2012 Summer"`.

---

## 3. Finding 3: Document Dilution on Venue + Date Collisions (`pub-030`, `pub-095`)
* **Observation**: Multi-hop queries `pub-030` (*"Who won the gold medal in the event held at Carioca Arena 3 on 6 August 2016?"*) and `pub-095` (*"event held at Beijing National Stadium on 16 August 2008"*) had 0 gold hits in top-$k$.
* **Root Cause**: Major Olympic venues (such as Carioca Arena 3 or Beijing National Stadium) host dozens of events across multiple sports over a single two-week period. Standard unstructured keyword search ranks general venue overviews and adjacent events higher than the single specific event that took place on that exact calendar date.
* **Architectural Comparison**:
  * **RAG**: High noise-to-signal ratio when querying by common spatial/temporal anchors.
  * **Agentic GraphRAG**: Directly filters structured attributes via `get_events(venue="Carioca Arena 3", date="6 August 2016")`.

---

## 4. Note on Offline MockLLM Validation
* **Implementation Details**: The `MockLLM` in `rag_only_pipeline/llm/llm_client.py` uses heuristic pattern matching over the *retrieved prompt context* (scanning for Infobox fields like `gold:` and `competitors:` within the retrieved chunks and extracting chunk IDs).
* **Purpose**: It validates end-to-end retrieval grounding, chunk extraction, prompt construction, token tracking, citation parsing, and JSONL output schema compliance without external LLM dependencies.
* **Limitation**: MockLLM does NOT perform genuine reasoning or semantic comprehension. Full question answering capabilities will be evaluated once the real model (`qwen3:8b`) is connected.

---

## 5. Finding 5: Semantic Vector Search & Hybrid RRF Empirical Evaluation

To test whether dense semantic search could enhance sparse BM25 retrieval, we constructed a dense vector index over all **20,100 narrative chunks** using `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) and FAISS (`IndexFlatIP` with L2-normalized cosine similarity). We then evaluated **BM25-only**, **Vector-only**, and **Hybrid RRF** (Reciprocal Rank Fusion with $k_{rrf}=60$) across all 100 questions from `eval_public.jsonl`.

### Empirical Results across 100 Evaluation Questions:

| Metric | BM25-Only | Vector-Only | Hybrid (RRF) | Hybrid vs BM25 Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Hit@5** | **98.0%** (98/100) | 79.0% (79/100) | 93.0% (93/100) | -5.0% |
| **Hit@8** | **98.0%** (98/100) | 86.0% (86/100) | 97.0% (97/100) | **-1.0%** |
| **Hit@10** | 98.0% (98/100) | 87.0% (87/100) | **99.0%** (99/100) | +1.0% |
| **Frac@5 (All Gold Docs)** | **73.3%** | 50.5% | 69.1% | -4.2% |
| **Frac@8 (All Gold Docs)** | **82.5%** | 64.1% | 82.2% | -0.3% |
| **Frac@10 (All Gold Docs)** | 87.8% | 67.5% | **88.8%** | +1.0% |

### Recall@8 Breakdown by Query Type:

| Query Type | Questions | BM25 Hit@8 | Vector Hit@8 | Hybrid Hit@8 | Delta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`aggregation`** | 21 | **100.0%** (21/21) | 100.0% (21/21) | 100.0% (21/21) | 0.0% |
| **`lookup`** | 19 | **100.0%** (19/19) | 100.0% (19/19) | 100.0% (19/19) | 0.0% |
| **`multi_hop`** | 28 | **92.9%** (26/28) | 50.0% (14/28) | 89.3% (25/28) | **-3.6%** |
| **`superlative`** | 10 | **100.0%** (10/10) | 100.0% (10/10) | 100.0% (10/10) | 0.0% |
| **`temporal`** | 22 | **100.0%** (22/22) | 100.0% (22/22) | 100.0% (22/22) | 0.0% |

### Key Analysis & Architectural Takeaway:
1. **Semantic Vector Search Alone Suffers on Named Entity & Date Constraints (50.0% on `multi_hop`)**: Dense embeddings capture broad topical similarity (e.g., cycling or sailing at the Olympics), but fail to distinguish between specific dates (e.g., "3 to 4 August" vs "7 August") or specific sub-arenas.
2. **Hybrid RRF Slightly Regressed Hit@8 (-1.0%)**: Fusing vector rankings diluted the precise lexical signal of BM25 on multi-hop questions (`pub-015`, `pub-038`), pushing exact match chunks from top-8 down to rank 9–10.
3. **Decision: Retain BM25-Only as Production Retriever**: Because Hybrid RRF does not improve Hit@8 recall and introduces unnecessary embedding overhead, BM25-only is retained as the authoritative, optimal retriever for the RAG baseline. The vector index and hybrid retriever are preserved in `rag_only_pipeline/retrieval/` as verified research artifacts.

