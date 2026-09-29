"""BM25 Index for the independent RAG pipeline.
Uses SQLite FTS5 with BM25 ranking (with title weight boosting)
persisted in rag_storage.db.
"""

import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rag_only_pipeline.config import SQLITE_DB_PATH
from rag_only_pipeline.corpus.loader import load_corpus
from rag_only_pipeline.corpus.chunker import chunk_document


# Standard English / question stop words to filter out from raw questions for cleaner BM25 matching
STOP_WORDS = {
    "according", "to", "the", "provided", "corpus", "how", "many", "at",
    "had", "more", "than", "which", "who", "what", "where", "when", "in",
    "of", "a", "an", "is", "was", "were", "are", "been", "being", "have",
    "has", "do", "does", "did", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "from",
    "up", "down", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "all", "any", "both", "each", "few", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "can", "will", "just", "should", "now"
}


def sanitize_query_for_fts(query: str) -> str:
    """Sanitize and prepare a query for SQLite FTS5 BM25.
    Extracts informative alphanumeric keywords and combines with OR / NEAR.
    """
    clean = re.sub(r"[^\w\s-]", " ", query)
    tokens = clean.split()
    meaningful = [t for t in tokens if t.lower() not in STOP_WORDS and len(t) > 1]

    if not meaningful:
        # Fallback to alphanumeric tokens
        meaningful = [t for t in tokens if len(t) > 1]

    if not meaningful:
        return ""

    # FTS5 query: require or prioritize key phrases, match tokens
    # Escape double quotes just in case
    escaped = [f'"{t}"' for t in meaningful]
    fts_query = " OR ".join(escaped)
    return fts_query


class BM25Index:
    """BM25 Search Index backed by SQLite FTS5."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else SQLITE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables for chunks and FTS5 index if not existing."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    content TEXT NOT NULL
                );
            """)
            cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    doc_id UNINDEXED,
                    title,
                    content,
                    tokenize='porter unicode61'
                );
            """)
            conn.commit()

    def is_indexed(self) -> bool:
        """Check if chunks have already been loaded."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            count = cur.execute("SELECT count(*) FROM chunks").fetchone()[0]
            return count > 0

    def build_index(self, force_rebuild: bool = False, verbose: bool = True) -> int:
        """Populate database from corpus.jsonl and chunk_document()."""
        if self.is_indexed() and not force_rebuild:
            with self._get_connection() as conn:
                count = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
                if verbose:
                    print(f"[BM25Index] Database already contains {count} chunks. Skipping rebuild.")
                return count

        if verbose:
            print("[BM25Index] Building BM25 index from corpus...")
        t0 = time.time()

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM chunks;")
            cur.execute("DELETE FROM chunks_fts;")

            chunk_records = []
            fts_records = []

            doc_count = 0
            for doc in load_corpus():
                doc_count += 1
                doc_chunks = chunk_document(
                    doc_id=doc["doc_id"],
                    title=doc.get("title", ""),
                    text=doc.get("text", "")
                )
                for c in doc_chunks:
                    chunk_records.append((
                        c["chunk_id"], c["doc_id"], c["title"], c["chunk_type"], c["content"]
                    ))
                    fts_records.append((
                        c["chunk_id"], c["doc_id"], c["title"], c["content"]
                    ))

            # Batch insert
            cur.executemany("""
                INSERT INTO chunks (chunk_id, doc_id, title, chunk_type, content)
                VALUES (?, ?, ?, ?, ?)
            """, chunk_records)

            cur.executemany("""
                INSERT INTO chunks_fts (chunk_id, doc_id, title, content)
                VALUES (?, ?, ?, ?)
            """, fts_records)

            conn.commit()

        elapsed = time.time() - t0
        if verbose:
            print(f"[BM25Index] Indexed {len(chunk_records)} chunks across {doc_count} documents in {elapsed:.2f}s.")
        return len(chunk_records)

    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Perform BM25 search over chunks with title boosting.
        Returns top_k chunk dictionaries with score.
        """
        fts_query = sanitize_query_for_fts(query)
        if not fts_query:
            return []

        with self._get_connection() as conn:
            cur = conn.cursor()
            # FTS5 bm25(chunks_fts, title_weight, content_weight)
            # Give title higher weight (5.0) than content (1.0) for entity/event alignment
            try:
                rows = cur.execute("""
                    SELECT c.chunk_id, c.doc_id, c.title, c.chunk_type, c.content,
                           bm25(chunks_fts, 5.0, 1.0) AS bm25_score
                    FROM chunks_fts
                    JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
                    WHERE chunks_fts MATCH ?
                    ORDER BY bm25_score ASC
                    LIMIT ?
                """, (fts_query, top_k)).fetchall()

                results = []
                for r in rows:
                    results.append({
                        "chunk_id": r["chunk_id"],
                        "doc_id": r["doc_id"],
                        "title": r["title"],
                        "chunk_type": r["chunk_type"],
                        "content": r["content"],
                        "score": float(r["bm25_score"])
                    })
                return results

            except sqlite3.OperationalError as e:
                # If complex query syntax fails, fallback to simple title/content LIKE search
                print(f"[BM25Index Warning] FTS match error: {e}. Fallback to LIKE.")
                terms = [t for t in query.split() if len(t) > 3][:3]
                like_clauses = " AND ".join(["content LIKE ?" for _ in terms])
                params = [f"%{t}%" for t in terms] + [top_k]
                rows = cur.execute(f"""
                    SELECT chunk_id, doc_id, title, chunk_type, content, 0.0 as bm25_score
                    FROM chunks
                    WHERE {like_clauses}
                    LIMIT ?
                """, params).fetchall()
                return [dict(r) for r in rows]
