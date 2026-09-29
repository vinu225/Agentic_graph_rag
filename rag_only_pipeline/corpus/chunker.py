"""Document chunker for the independent RAG pipeline.
Preserves the Infobox as its own distinct chunk (chunk_type="infobox")
and splits text sections on paragraph boundaries (~300-500 tokens, ~10-15% overlap)
without breaking table rows or key-value pairs.
"""

import re
from typing import Any, Dict, List


def estimate_tokens(text: str) -> int:
    """Fast approximation of token count (~4 characters per token)."""
    return max(1, len(text) // 4)


def chunk_document(
    doc_id: str,
    title: str,
    text: str,
    min_tokens: int = 250,
    target_tokens: int = 400,
    max_tokens: int = 550,
    overlap_tokens: int = 50
) -> List[Dict[str, Any]]:
    """Chunk an Olympic document into structured retrieval chunks:
    1. Chunk 0: [Infobox Olympic event] metadata preserved intact as chunk_type="infobox".
    2. Subsequent chunks: Narrative sections and results tables split on paragraph
       boundaries (~300-500 tokens), preserving table rows and key-value pairs,
       with ~10-15% overlap.
    """
    chunks: List[Dict[str, Any]] = []
    if not text:
        return chunks

    # 1. Preserve Infobox as its own chunk
    infobox_match = re.search(r"(\[Infobox Olympic event\].*?)(?:\n\n|\Z)", text, re.DOTALL)
    remaining_text = text

    if infobox_match:
        infobox_text = infobox_match.group(1).strip()
        chunks.append({
            "chunk_id": f"{doc_id}#c0",
            "doc_id": doc_id,
            "title": title,
            "chunk_type": "infobox",
            "content": f"Title: {title}\n{infobox_text}"
        })
        remaining_text = text[infobox_match.end():].strip()

    # 2. Split remaining text on paragraph boundaries
    # Keep table rows together within each paragraph block
    raw_paragraphs = re.split(r"\n\s*\n", remaining_text)
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]

    current_paras: List[str] = []
    current_tokens = 0
    chunk_idx = len(chunks)

    for p in paragraphs:
        p_tokens = estimate_tokens(p)

        # If a single paragraph is larger than max_tokens, split on newline boundaries
        # to ensure table rows or key-value lines are never split down the middle
        if p_tokens > max_tokens:
            if current_paras:
                content_str = "\n\n".join(current_paras)
                chunks.append({
                    "chunk_id": f"{doc_id}#c{chunk_idx}",
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_type": "text",
                    "content": f"Title: {title}\n{content_str}"
                })
                chunk_idx += 1
                current_paras = []
                current_tokens = 0

            lines = p.split("\n")
            line_buf: List[str] = []
            line_buf_tokens = 0
            for line in lines:
                l_tokens = estimate_tokens(line)
                if line_buf_tokens + l_tokens > target_tokens and line_buf:
                    chunks.append({
                        "chunk_id": f"{doc_id}#c{chunk_idx}",
                        "doc_id": doc_id,
                        "title": title,
                        "chunk_type": "text",
                        "content": f"Title: {title}\n" + "\n".join(line_buf)
                    })
                    chunk_idx += 1
                    overlap_lines = line_buf[-2:] if len(line_buf) >= 2 else line_buf[-1:]
                    line_buf = list(overlap_lines) + [line]
                    line_buf_tokens = sum(estimate_tokens(l) for l in line_buf)
                else:
                    line_buf.append(line)
                    line_buf_tokens += l_tokens

            if line_buf:
                current_paras = ["\n".join(line_buf)]
                current_tokens = line_buf_tokens
            continue

        # Normal paragraph accumulation
        if current_tokens + p_tokens <= target_tokens:
            current_paras.append(p)
            current_tokens += p_tokens
        else:
            if current_paras:
                content_str = "\n\n".join(current_paras)
                chunks.append({
                    "chunk_id": f"{doc_id}#c{chunk_idx}",
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_type": "text",
                    "content": f"Title: {title}\n{content_str}"
                })
                chunk_idx += 1

                # Apply ~10-15% overlap: carry over the last paragraph if small enough
                if estimate_tokens(current_paras[-1]) <= (overlap_tokens * 2):
                    current_paras = [current_paras[-1], p]
                    current_tokens = estimate_tokens(current_paras[0]) + p_tokens
                else:
                    current_paras = [p]
                    current_tokens = p_tokens
            else:
                current_paras = [p]
                current_tokens = p_tokens

    # Final trailing chunk
    if current_paras:
        content_str = "\n\n".join(current_paras)
        chunks.append({
            "chunk_id": f"{doc_id}#c{chunk_idx}",
            "doc_id": doc_id,
            "title": title,
            "chunk_type": "text",
            "content": f"Title: {title}\n{content_str}"
        })

    return chunks
