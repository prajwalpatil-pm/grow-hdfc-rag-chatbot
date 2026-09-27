"""all-MiniLM-L6-v2 embedder, shared by ingestion and query time.

architecture.md §5 step 3. Vectors are L2-normalized so cosine similarity
reduces to a dot product. The model is loaded lazily and cached.
"""
from __future__ import annotations

from functools import lru_cache

import config


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(config.EMBED_MODEL)


class Embedder:
    def encode(self, texts) -> list[list[float]]:
        vecs = _model().encode(
            list(texts), normalize_embeddings=True, convert_to_numpy=True
        )
        return vecs.tolist()


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
