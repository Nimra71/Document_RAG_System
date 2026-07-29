"""
Core retrieval engine: embeds chunks, builds a FAISS index, retrieves candidates,
and re-ranks them with a cross-encoder for higher-precision context selection.

This two-stage retrieve-then-rerank approach is the key upgrade over the original
project's single-stage FAISS-only retrieval.
"""
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder

# Loaded once at startup and reused across requests — avoids reloading per call.
_embedder = SentenceTransformer("all-MiniLM-L6-v2")
_reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def build_index(chunks: list[str]):
    """Embed chunks and build a FAISS index for semantic search."""
    embeddings = _embedder.encode(chunks, convert_to_numpy=True).astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def retrieve_and_rerank(
    question: str,
    chunks: list[str],
    index,
    initial_k: int = 15,
    final_k: int = 5,
) -> list[dict]:
    """
    Stage 1: FAISS retrieves a wide net of candidates (initial_k).
    Stage 2: Cross-encoder re-scores each (question, chunk) pair and keeps the
             best final_k — this catches cases where FAISS's vector similarity
             picks a chunk that's topically close but not actually the best answer.

    Returns a list of dicts with chunk text, original index, and relevance score,
    so the API can cite exactly which chunk each answer came from.
    """
    query_embedding = _embedder.encode([question]).astype("float32")
    search_k = min(initial_k, len(chunks))
    _, candidate_indices = index.search(query_embedding, search_k)
    candidate_indices = candidate_indices[0]

    candidates = [chunks[i] for i in candidate_indices]
    pairs = [[question, c] for c in candidates]
    scores = _reranker.predict(pairs)

    ranked = sorted(
        zip(candidate_indices, candidates, scores),
        key=lambda x: x[2],
        reverse=True,
    )[:final_k]

    return [
        {"chunk_id": int(idx), "text": text, "relevance_score": float(score)}
        for idx, text, score in ranked
    ]
