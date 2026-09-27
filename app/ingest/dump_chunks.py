"""Dump all corpus chunks to a human-readable text file for inspection.

Run from the repo root:  python -m app.ingest.dump_chunks
Writes eval/chunks_dump.txt (id + metadata + breadcrumbed text per chunk).
"""
from __future__ import annotations

import os

from app.ingest.chunker import chunk_doc
from app.ingest.loader import load_corpus

OUT_PATH = os.path.join("eval", "chunks_dump.txt")


def main() -> None:
    docs = load_corpus()
    chunks = [c for doc in docs for c in chunk_doc(doc)]

    lines: list[str] = [
        "MF FAQ RAG — Corpus Chunks Dump",
        f"Total chunks: {len(chunks)}  (from {len(docs)} scheme docs)",
        "Chunking: section-aware (one chunk per H2). See architecture.md §5/§10.",
        "=" * 72,
    ]
    for i, c in enumerate(chunks, 1):
        m = c.metadata
        lines += [
            "",
            f"### CHUNK {i}/{len(chunks)}",
            f"id         : {c.id}",
            f"scheme     : {m['scheme']}",
            f"section    : {m['section']}",
            f"category   : {m['category']}",
            f"source_url : {m['source_url']}",
            f"nav_as_of  : {m['nav_as_of']}",
            "-" * 72,
            c.text,
        ]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {OUT_PATH} with {len(chunks)} chunks")


if __name__ == "__main__":
    main()
