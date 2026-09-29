"""Configuration for Agentic GraphRAG system.
All paths and service connection parameters are defined here or read from environment variables.
"""

import os
from pathlib import Path

# Base Paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = WORKSPACE_ROOT / "drive-download-20260928T175718Z-1-001"

# Corpus and evaluation files (read from env or fallback to workspace relative paths)
CORPUS_PATH = Path(os.getenv("CORPUS_PATH", str(DATASET_DIR / "corpus" / "corpus.jsonl")))
EVAL_PUBLIC_PATH = Path(os.getenv("EVAL_PUBLIC_PATH", str(DATASET_DIR / "questions" / "eval_public.jsonl")))
EVAL_HIDDEN_PATH = Path(os.getenv("EVAL_HIDDEN_PATH", str(DATASET_DIR / "questions" / "eval_hidden.jsonl")))

# Local Graph SQLite DB path
SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(WORKSPACE_ROOT / "local_graph.db")))

# Agentic Runtime Constants
DEFAULT_MAX_AGENT_STEPS: int = int(os.getenv("MAX_AGENT_STEPS", "10"))
DEFAULT_TOKEN_BUDGET: int = int(os.getenv("TOKEN_BUDGET", "6000"))

# Local Ollama LLM Configuration (OpenAI-compatible)
OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1")
DEFAULT_OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")

# TigerGraph Savanna Placeholders (to be connected in Step 7)
TG_HOST: str = os.getenv("TG_HOST", "")
TG_USERNAME: str = os.getenv("TG_USERNAME", "")
TG_PASSWORD: str = os.getenv("TG_PASSWORD", "")
TG_SECRET: str = os.getenv("TG_SECRET", "")
TG_GRAPH_NAME: str = os.getenv("TG_GRAPH_NAME", "TigerGraphRAG")
