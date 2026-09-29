"""Corpus loader for the independent RAG pipeline.
Loads corpus documents from JSONL line-by-line.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, Union, Optional
from rag_only_pipeline.config import CORPUS_PATH


def load_corpus(corpus_path: Optional[Union[str, Path]] = None) -> Iterator[Dict[str, Any]]:
    """Yield document dictionaries from corpus.jsonl.
    Each item contains: doc_id, title, url, text, etc.
    """
    path = Path(corpus_path) if corpus_path else CORPUS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
                yield doc
            except json.JSONDecodeError as e:
                print(f"[Warning] Failed to parse line {line_num}: {e}")
