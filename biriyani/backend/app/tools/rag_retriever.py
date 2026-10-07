import re
from typing import Any
from app.models.document import Document

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks of specified size."""
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + chunk_size
        chunk = cleaned[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def _score_chunk(query_terms: set[str], chunk: str) -> float:
    """Calculate keyword relevance score between query terms and chunk text."""
    chunk_lower = chunk.lower()
    score = 0.0
    for term in query_terms:
        if not term:
            continue
        # Count frequency of query terms in chunk
        occurrences = len(re.findall(re.escape(term), chunk_lower))
        score += occurrences * (1.5 if len(term) > 4 else 1.0)
    return score


def retrieve_document_chunks(
    query: str, documents: list[Document], top_k: int = 4
) -> list[dict[str, Any]]:
    """
    Retrieve Top-K relevant document chunks across all attached documents for a given query.
    Returns structured chunk references with source citations.
    """
    if not query or not documents:
        return []

    # Clean query into unique keyword terms
    query_terms = set(re.findall(r"\w+", query.lower()))
    # Remove ultra-common stop words
    stop_words = {"the", "a", "an", "is", "are", "what", "which", "how", "and", "or", "to", "in", "of", "for", "on", "with"}
    query_terms = query_terms - stop_words

    all_scored_chunks: list[dict[str, Any]] = []

    for doc in documents:
        if not doc.extracted_text:
            continue

        chunks = chunk_text(doc.extracted_text)
        for idx, chunk in enumerate(chunks, start=1):
            score = _score_chunk(query_terms, chunk)
            all_scored_chunks.append(
                {
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "text": chunk,
                    "score": score,
                }
            )

    # Sort chunks by relevance score descending
    all_scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    # Return top K items (if score > 0 or if all scores are 0, return initial chunks)
    selected = all_scored_chunks[:top_k]
    return selected
