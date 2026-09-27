"""Retrieval over the ChromaDB index. architecture.md §6 steps 4-6.

Embeds the query with the same MiniLM model used at ingestion, runs a cosine
similarity search (optionally filtered to one scheme), and exposes a relevance
gate so the pipeline can fall back to `not_found`.
"""
from __future__ import annotations

from dataclasses import dataclass

import config
from app.ingest.embedder import get_embedder
from app.ingest.index import get_collection


@dataclass
class RetrievedChunk:
    id: str
    text: str
    distance: float
    metadata: dict


def search(query: str, scheme_filter: str | None = None, k: int | None = None) -> list[RetrievedChunk]:
    k = k or config.TOP_K
    vec = get_embedder().encode([query])[0]
    where = {"scheme": scheme_filter} if scheme_filter else None
    res = get_collection().query(query_embeddings=[vec], n_results=k, where=where)

    ids = res["ids"][0]
    docs = res["documents"][0]
    dists = res["distances"][0]
    metas = res["metadatas"][0]
    return [
        RetrievedChunk(id=ids[i], text=docs[i], distance=dists[i], metadata=metas[i])
        for i in range(len(ids))
    ]


def passes_gate(chunks: list[RetrievedChunk]) -> bool:
    """True if we have at least one chunk within the distance threshold."""
    return bool(chunks) and min(c.distance for c in chunks) <= config.DISTANCE_THRESHOLD
