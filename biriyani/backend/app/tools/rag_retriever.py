from __future__ import annotations
import re
from typing import Any
from app.core.config import settings
from app.models.document import Document


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping chunks of specified size using recursive paragraph/sentence boundaries where possible."""
    cs = chunk_size or settings.chunk_size
    ol = overlap or settings.chunk_overlap

    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= cs:
        return [cleaned]

    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + cs
        chunk = cleaned[start:end]

        # Try to break at paragraph or sentence boundaries if near end
        if end < len(cleaned):
            break_idx = max(chunk.rfind("\n\n"), chunk.rfind(". "), chunk.rfind("\n"))
            if break_idx > cs // 2:
                chunk = chunk[: break_idx + 1]
                end = start + len(chunk)

        chunks.append(chunk.strip())
        start = max(start + 1, end - ol)

    return [c for c in chunks if c]


def _score_chunk(query: str, query_terms: set[str], chunk: str) -> float:
    """Calculate relevance score between query terms and chunk text with exact phrase bonuses."""
    chunk_lower = chunk.lower()
    score = 0.0

    # Exact full query match bonus
    query_lower = query.lower().strip()
    if query_lower and len(query_lower) > 4 and query_lower in chunk_lower:
        score += 5.0

    for term in query_terms:
        if not term:
            continue
        occurrences = chunk_lower.count(term)
        if occurrences > 0:
            weight = 2.0 if len(term) > 4 else 1.0
            score += occurrences * weight

    return score


def retrieve_document_chunks(
    query: str,
    documents: list[Document],
    top_k: int | None = None,
    relevance_threshold: float | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve Top-K relevant document chunks across all attached user documents.
    Filters out chunks with score below relevance_threshold to prevent hallucinated context.
    """
    k = top_k if top_k is not None else settings.rag_top_k
    threshold = relevance_threshold if relevance_threshold is not None else settings.rag_relevance_threshold

    if not query or not documents:
        return []

    # Clean query into unique keyword terms
    query_terms = set(re.findall(r"\w+", query.lower()))
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "what", "which", "how", "where",
        "when", "who", "why", "and", "or", "to", "in", "of", "for", "on", "with", "this",
        "that", "it", "from", "at", "by", "as", "be", "do", "does", "did"
    }
    query_terms = query_terms - stop_words

    all_scored_chunks: list[dict[str, Any]] = []

    for doc in documents:
        if not doc.extracted_text:
            continue

        chunks = chunk_text(doc.extracted_text)
        for idx, chunk in enumerate(chunks, start=1):
            score = _score_chunk(query, query_terms, chunk)
            if score >= threshold:
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

    return all_scored_chunks[:k]


def format_sources(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Format RAG chunks into clean source citation dictionaries for frontend display."""
    sources = []
    seen = set()
    for c in chunks:
        key = (c.get("filename"), c.get("chunk_index"))
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "document_id": c.get("document_id"),
                "filename": c.get("filename"),
                "chunk_index": c.get("chunk_index"),
                "total_chunks": c.get("total_chunks"),
                "citation": f"{c.get('filename')}, Chunk {c.get('chunk_index')}/{c.get('total_chunks')}",
            }
        )
    return sources

