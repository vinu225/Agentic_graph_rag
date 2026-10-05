"""Vector Index implementation for RAG pipeline using SentenceTransformers and FAISS.

Embeds chunks from rag_storage.db and provides fast cosine-similarity search.
Persists FAISS index to rag_only_pipeline/faiss_index.bin and metadata to
rag_only_pipeline/vector_metadata.json.
"""

import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None

INDEX_DIR = Path(__file__).resolve().parent.parent
DB_PATH = INDEX_DIR / "rag_storage.db"
FAISS_PATH = INDEX_DIR / "faiss_index.bin"
METADATA_PATH = INDEX_DIR / "vector_metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"


class VectorIndex:
    """FAISS-based vector index for semantic chunk retrieval."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ):
        if faiss is None or SentenceTransformer is None:
            raise ImportError("faiss and sentence-transformers must be installed to use VectorIndex.")

        self.model_name = model_name
        self.index_path = index_path or FAISS_PATH
        self.metadata_path = metadata_path or METADATA_PATH
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []

    def _load_model(self) -> SentenceTransformer:
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def build(self, batch_size: int = 128) -> None:
        """Build FAISS index over all 20,100 chunks from SQLite."""
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found at {DB_PATH}")

        print(f"[VectorIndex] Loading chunks from {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        rows = c.execute(
            "SELECT chunk_id, doc_id, title, chunk_type, content FROM chunks ORDER BY rowid ASC"
        ).fetchall()
        conn.close()

        total_chunks = len(rows)
        print(f"[VectorIndex] Total chunks to index: {total_chunks}")

        self.metadata = []
        texts = []
        for r in rows:
            self.metadata.append({
                "chunk_id": r[0],
                "doc_id": r[1],
                "title": r[2],
                "chunk_type": r[3],
                "content": r[4],
            })
            # Combine title and content for richer semantic representation
            text = f"{r[2]}\n{r[4]}" if r[2] else r[4]
            texts.append(text)

        model = self._load_model()
        dim = model.get_sentence_embedding_dimension()
        print(f"[VectorIndex] Model {self.model_name} initialized (dim={dim}).")

        index = faiss.IndexFlatIP(dim)
        t_start = time.time()

        for i in range(0, total_chunks, batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_embs = model.encode(
                batch_texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            ).astype(np.float32)

            index.add(batch_embs)
            done = min(i + batch_size, total_chunks)
            if done % 2000 == 0 or done == total_chunks:
                elapsed = time.time() - t_start
                rate = done / max(0.1, elapsed)
                rem = (total_chunks - done) / max(0.1, rate)
                print(f"  [VectorIndex Progress] {done}/{total_chunks} chunks embedded ({rate:.1f} chunks/sec, est. {rem/60:.1f}m remaining)")

        self.index = index
        print(f"[VectorIndex] Finished embedding {total_chunks} chunks in {time.time() - t_start:.2f}s.")

        # Persist index and metadata
        self.save()

    def save(self) -> None:
        """Save FAISS index and metadata to disk."""
        if self.index is None or not self.metadata:
            raise ValueError("Index or metadata is empty. Cannot save.")

        print(f"[VectorIndex] Saving FAISS index to {self.index_path}...")
        faiss.write_index(self.index, str(self.index_path))

        print(f"[VectorIndex] Saving metadata to {self.metadata_path}...")
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f)

        print("[VectorIndex] Index and metadata successfully saved.")

    def load(self) -> bool:
        """Load FAISS index and metadata from disk if present."""
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False

        print(f"[VectorIndex] Loading FAISS index from {self.index_path}...")
        self.index = faiss.read_index(str(self.index_path))

        print(f"[VectorIndex] Loading metadata from {self.metadata_path}...")
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        print(f"[VectorIndex] Loaded {self.index.ntotal} vectors into index.")
        return True

    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Search top-k most semantically similar chunks for a query."""
        if self.index is None:
            if not self.load():
                raise RuntimeError("VectorIndex is not loaded or built.")

        model = self._load_model()
        q_emb = model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)

        scores, indices = self.index.search(q_emb, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)

        return results


if __name__ == "__main__":
    v_idx = VectorIndex()
    if not v_idx.load():
        print("Vector index not found on disk. Building from scratch...")
        v_idx.build(batch_size=128)
    else:
        print("Vector index already exists.")

    test_q = "Who won the gold medal in tennis at the 2012 Summer Olympics?"
    print(f"\nTest Search: '{test_q}'")
    hits = v_idx.search(test_q, top_k=3)
    for i, h in enumerate(hits, 1):
        print(f"  {i}. [{h['chunk_id']}] (Doc: {h['doc_id']}) Score: {h['score']:.4f} | Title: {h['title']}")
