"""Hybrid Retriever combining BM25 (sparse) and FAISS (dense semantic) search.

Uses Reciprocal Rank Fusion (RRF) to merge candidate lists from BM25 and Vector search:
RRF_score(doc) = 1 / (60 + rank_bm25) + 1 / (60 + rank_vector)
"""

from typing import Any, Dict, List, Optional
from collections import defaultdict

from rag_only_pipeline.retrieval.bm25_index import BM25Index
from rag_only_pipeline.retrieval.vector_index import VectorIndex


class HybridRetriever:
    """Hybrid Retriever fusing BM25 and Vector search results using Reciprocal Rank Fusion."""

    def __init__(
        self,
        bm25_index: Optional[BM25Index] = None,
        vector_index: Optional[VectorIndex] = None,
        rrf_k: int = 60
    ):
        self.bm25 = bm25_index or BM25Index()
        self.vector = vector_index or VectorIndex()
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 8,
        candidate_k: int = 25
    ) -> List[Dict[str, Any]]:
        """Perform hybrid retrieval using RRF over top candidate_k from each source."""
        # 1. Retrieve sparse candidates (BM25)
        bm25_hits = self.bm25.search(query, top_k=candidate_k)

        # 2. Retrieve dense candidates (Vector)
        vector_hits = self.vector.search(query, top_k=candidate_k)

        # 3. Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = defaultdict(float)
        chunk_map: Dict[str, Dict[str, Any]] = {}
        bm25_ranks: Dict[str, int] = {}
        vector_ranks: Dict[str, int] = {}

        for rank, hit in enumerate(bm25_hits, 1):
            cid = hit["chunk_id"]
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank)
            bm25_ranks[cid] = rank
            if cid not in chunk_map:
                chunk_map[cid] = hit

        for rank, hit in enumerate(vector_hits, 1):
            cid = hit["chunk_id"]
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank)
            vector_ranks[cid] = rank
            if cid not in chunk_map:
                chunk_map[cid] = hit

        # 4. Sort by descending RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        results = []
        for cid in sorted_cids[:top_k]:
            item = dict(chunk_map[cid])
            item["rrf_score"] = rrf_scores[cid]
            item["bm25_rank"] = bm25_ranks.get(cid, None)
            item["vector_rank"] = vector_ranks.get(cid, None)
            results.append(item)

        return results
