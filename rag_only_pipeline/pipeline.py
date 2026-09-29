"""Execution pipeline for the independent RAG pipeline.
Orchestrates:
1. Retrieval of top-k chunks via BM25Index
2. Context preparation & prompt formatting
3. Generation via llm_client.generate()
4. Parsing of answer, citations, and token metrics
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from rag_only_pipeline.config import DEFAULT_K
from rag_only_pipeline.llm.llm_client import generate
from rag_only_pipeline.prompt import build_rag_prompt
from rag_only_pipeline.retrieval.bm25_index import BM25Index


@dataclass
class RAGResult:
    question_id: str
    question: str
    answer: str
    citations: List[str]
    retrieved_chunks: List[Dict[str, Any]]
    context_tokens: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    elapsed_time_s: float

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to the exact JSONL evaluation schema."""
        return {
            "question_id": self.question_id,
            "answer": self.answer,
            "citations": self.citations,
            "context_tokens": self.context_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "elapsed_time_s": round(self.elapsed_time_s, 3),
        }


def extract_citations(answer: str, candidate_chunks: List[Dict[str, Any]]) -> List[str]:
    """Parse out cited chunk_ids or doc_ids from the generated answer."""
    # Match patterns like [Q1050909#c0] or [Q1050909]
    found = re.findall(r"\[([A-Za-z0-9_#\-]+)\]", answer)
    candidate_chunk_ids = {c["chunk_id"] for c in candidate_chunks}
    candidate_doc_ids = {c["doc_id"] for c in candidate_chunks}

    valid_citations = []
    for item in found:
        if item in candidate_chunk_ids or item in candidate_doc_ids:
            if item not in valid_citations:
                valid_citations.append(item)

    # If no explicit citation in text, fallback to top retrieved chunk_ids
    if not valid_citations and candidate_chunks:
        valid_citations = [candidate_chunks[0]["chunk_id"]]

    return valid_citations


class RAGPipeline:
    """Retrieval-Augmented Generation Pipeline."""

    def __init__(self, index: Optional[BM25Index] = None):
        self.index = index or BM25Index()

    def run(
        self,
        question: str,
        question_id: Optional[str] = None,
        k: int = DEFAULT_K,
        temperature: float = 0.0,
    ) -> RAGResult:
        """Execute full RAG pipeline on a question."""
        start_time = time.time()
        qid = question_id or "adhoc"

        # 1. Retrieve top-k chunks
        chunks = self.index.search(question, top_k=k)

        # 2. Count context tokens (~4 chars per token)
        context_str = "".join(c.get("content", "") for c in chunks)
        context_tokens = max(1, len(context_str) // 4) if context_str else 0

        # 3. Build prompt messages
        messages = build_rag_prompt(question, chunks)

        # 4. Generate LLM response
        llm_resp = generate(messages, temperature=temperature)

        # 5. Extract citations
        citations = extract_citations(llm_resp.content, chunks)

        elapsed = time.time() - start_time

        return RAGResult(
            question_id=qid,
            question=question,
            answer=llm_resp.content,
            citations=citations,
            retrieved_chunks=chunks,
            context_tokens=context_tokens,
            input_tokens=llm_resp.prompt_tokens,
            output_tokens=llm_resp.completion_tokens,
            total_tokens=llm_resp.total_tokens,
            elapsed_time_s=elapsed,
        )
