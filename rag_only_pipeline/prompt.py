"""RAG Prompt Template for the independent RAG pipeline.
Instructs the model to answer strictly from the provided context chunks,
cite chunk_id for every claim, and output 'not found in corpus' if evidence is insufficient.
"""

from typing import Any, Dict, List


SYSTEM_PROMPT = """You are a strict, factual Olympic Games research assistant.
Answer questions solely based on the provided context chunks.

RULES:
1. Rely ONLY on the provided context chunks. Do NOT extrapolate, speculate, or use outside knowledge.
2. For EVERY factual claim, statistic, name, date, or number in your answer, you MUST cite the exact chunk_id in square brackets, e.g. [Q1050909#c0] or [Q26233122#c1].
3. If the provided context does NOT contain sufficient evidence to answer the question, output exactly:
   "not found in corpus"
4. Keep your answer direct, concise, and factual. Avoid conversational filler or introductory pleasantries.
"""


def format_context_chunks(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into a clear, numbered context block."""
    if not chunks:
        return "No relevant context found."

    blocks: List[str] = []
    for idx, c in enumerate(chunks, 1):
        chunk_id = c.get("chunk_id", "unknown")
        doc_id = c.get("doc_id", "unknown")
        chunk_type = c.get("chunk_type", "text")
        content = c.get("content", "").strip()

        block = f"--- [CHUNK {idx}: {chunk_id}] (Doc: {doc_id}, Type: {chunk_type}) ---\n{content}"
        blocks.append(block)

    return "\n\n".join(blocks)


def build_rag_prompt(question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Build messages array (system + user) for OpenAI-compatible chat completion."""
    context_text = format_context_chunks(chunks)

    user_content = (
        f"CONTEXT CHUNKS:\n"
        f"{context_text}\n\n"
        f"QUESTION:\n"
        f"{question}\n\n"
        f"ANSWER (grounded strictly in the chunks above, citing [chunk_id] for every claim):"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
