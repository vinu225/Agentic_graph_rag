"""Document chunker for Olympic corpus.
Preserves Infobox as a distinct high-density chunk and splits sections cleanly.
"""

from typing import Any, Dict, List
import re


def chunk_document(
    doc_id: str,
    title: str,
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """Split document into structured chunks:
    1. Chunk 0: [Infobox Olympic event] metadata block intact.
    2. Subsequent chunks: Narrative/results paragraphs with character bounds.
    """
    chunks: List[Dict[str, Any]] = []
    if not text:
        return chunks

    # 1. Extract infobox as chunk 0
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

    # 2. Split remaining sections by paragraphs
    paragraphs = re.split(r"\n\s*\n", remaining_text)
    current_chunk = ""
    chunk_idx = len(chunks)

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        if len(current_chunk) + len(p) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + p
            else:
                current_chunk = p
        else:
            if current_chunk:
                chunks.append({
                    "chunk_id": f"{doc_id}#c{chunk_idx}",
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_type": "text",
                    "content": f"Title: {title}\n{current_chunk}"
                })
                chunk_idx += 1
                # apply overlap if current chunk is long enough
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = (overlap_text + "\n\n" + p).strip() if overlap_text else p
            else:
                # single paragraph exceeds chunk size, split by lines or slice
                chunks.append({
                    "chunk_id": f"{doc_id}#c{chunk_idx}",
                    "doc_id": doc_id,
                    "title": title,
                    "chunk_type": "text",
                    "content": f"Title: {title}\n{p[:chunk_size]}"
                })
                chunk_idx += 1
                current_chunk = p[chunk_size - chunk_overlap:].strip()

    if current_chunk:
        chunks.append({
            "chunk_id": f"{doc_id}#c{chunk_idx}",
            "doc_id": doc_id,
            "title": title,
            "chunk_type": "text",
            "content": f"Title: {title}\n{current_chunk}"
        })

    return chunks
