# Benchmark Findings & Structural Insights for Pipeline 1 (Plain RAG)

This document logs empirical findings, structural failure modes, and retrieval characteristics observed during the development and benchmarking of the standalone RAG pipeline (`rag_only_pipeline`). These insights are preserved for the final hackathon comparison writeup (RAG vs GraphRAG vs Agentic GraphRAG).

---

## 1. Finding 1: Structural Under-Retrieval on Aggregation & Superlative Queries
* **Observation**: In Step 2 BM25 benchmarking across all 100 public questions:
  * **Hit@8** was **100.0%** for both `aggregation` and `superlative` questions.
  * **Frac@8** was only **54.3%** for `aggregation` and **61.3%** for `superlative`.
* **Root Cause**: Many aggregation questions (e.g. *"how many shooting events at the 2004 Summer Olympics had more than 37 competitors?"*) and superlative questions have 10 to 45 gold candidate documents in the corpus.
* **Empirical Confirmation on Eval Sample (`pub-001`, `pub-003`)**:
  * **`pub-001`**: Gold answer = 5, got = 4 (under-counted because only 4 relevant candidate documents were retrieved within the $k=8$ budget).
  * **`pub-003`**: Gold answer = 8, got = 3 (under-counted because only 3 relevant candidate documents were retrieved within the $k=8$ budget).
  * **Key Takeaway**: Directly confirms the Frac@8 retrieval gap predicted from the Step 2 recall benchmark. The model correctly reasons over what it was given, but cannot synthesize evidence that was truncated by top-$k$ retrieval.
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
