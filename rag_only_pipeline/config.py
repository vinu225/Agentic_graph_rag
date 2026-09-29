"""Configuration for the independent RAG pipeline.
All paths and service connection parameters are read from environment variables
with sensible defaults. Nothing is hardcoded.
"""

import os
from pathlib import Path

# Project root
PROJECT_DIR = Path(__file__).resolve().parent

# Default dataset locations (fallback to parent workspace or env vars)
DEFAULT_DATASET_DIR = PROJECT_DIR.parent / "drive-download-20260928T175718Z-1-001"

CORPUS_PATH = Path(os.getenv("CORPUS_PATH", str(DEFAULT_DATASET_DIR / "corpus" / "corpus.jsonl")))
EVAL_PUBLIC_PATH = Path(os.getenv("EVAL_PUBLIC_PATH", str(DEFAULT_DATASET_DIR / "questions" / "eval_public.jsonl")))
EVAL_HIDDEN_PATH = Path(os.getenv("EVAL_HIDDEN_PATH", str(DEFAULT_DATASET_DIR / "questions" / "eval_hidden.jsonl")))

# Local SQLite storage for chunks and BM25 index
SQLITE_DB_PATH = Path(os.getenv("RAG_SQLITE_PATH", str(PROJECT_DIR / "rag_storage.db")))

# Default RAG settings
DEFAULT_K: int = int(os.getenv("RAG_K", "8"))
DEFAULT_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1")
DEFAULT_OUTPUT_PATH = Path(os.getenv("RAG_OUTPUT_PATH", str(PROJECT_DIR / "results_rag.jsonl")))
