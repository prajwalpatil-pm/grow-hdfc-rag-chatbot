"""all-MiniLM-L6-v2 embedder via ChromaDB's built-in ONNX runtime (NO PyTorch).

We run the SAME all-MiniLM-L6-v2 model (384-dim) through onnxruntime instead of
sentence-transformers/PyTorch. This cuts resident memory from ~1 GB (torch) to a
few hundred MB, so the app fits comfortably on a 512 MB instance. onnxruntime
ships with chromadb, so there is no extra dependency and no torch to install.

architecture.md §5 step 3. The same embedder is used at ingestion and query time,
so index and query vectors always come from the identical model.
"""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def _ef():
    # ChromaDB's default embedding function IS all-MiniLM-L6-v2 (quantized, ONNX).
    try:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
    except ImportError:  # layout differs across chromadb versions
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import (
            ONNXMiniLM_L6_V2,
        )
    return ONNXMiniLM_L6_V2()


class Embedder:
    def encode(self, texts) -> list[list[float]]:
        vecs = _ef()(list(texts))
        return [[float(x) for x in v] for v in vecs]


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
