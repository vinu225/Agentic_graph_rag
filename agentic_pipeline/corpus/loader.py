"""Corpus document loader.
Reads corpus.jsonl dynamically from config.CORPUS_PATH.
"""

import json
from pathlib import Path
from typing import Generator, Dict, Any, Optional
from agentic_pipeline.config import CORPUS_PATH


def stream_corpus(corpus_file: Optional[Path] = None) -> Generator[Dict[str, Any], None, None]:
    """Stream documents from corpus JSONL line by line."""
    target_path = Path(corpus_file) if corpus_file else CORPUS_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Corpus file not found at: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def count_corpus_documents(corpus_file: Optional[Path] = None) -> int:
    """Return total number of documents in corpus."""
    count = 0
    for _ in stream_corpus(corpus_file):
        count += 1
    return count
