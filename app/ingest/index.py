"""ChromaDB persistence for the chunk index.

architecture.md §4.2 & §5 step 4. Uses a persistent client + cosine space.
Embeddings are supplied explicitly on upsert/query, so the collection's default
embedding function is never invoked.
"""
from __future__ import annotations

from functools import lru_cache

import config
from app.ingest.chunker import Chunk
from app.ingest.embedder import get_embedder


@lru_cache(maxsize=1)
def get_collection():
    import chromadb

    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": config.DISTANCE_METRIC},
    )


def build_collection(chunks: list[Chunk]) -> int:
    """Embed chunk texts and upsert them (idempotent by id). Returns row count."""
    col = get_collection()
    ids = [c.id for c in chunks]
    docs = [c.text for c in chunks]
    metas = [c.metadata for c in chunks]
    embeddings = get_embedder().encode(docs)
    col.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
    return col.count()
