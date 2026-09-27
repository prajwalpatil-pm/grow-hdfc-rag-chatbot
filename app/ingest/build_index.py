"""Ingestion CLI: Load -> Chunk -> Embed -> Store.

Run from the repo root:  python -m app.ingest.build_index
Idempotent — safe to re-run after editing the corpus (upserts by id).
"""
from __future__ import annotations

from app.ingest.chunker import chunk_doc
from app.ingest.index import build_collection, get_collection
from app.ingest.loader import load_corpus


def main() -> None:
    docs = load_corpus()
    chunks = [c for doc in docs for c in chunk_doc(doc)]
    print(f"#docs   = {len(docs)}")
    print(f"#chunks = {len(chunks)}")

    count = build_collection(chunks)
    col = get_collection()
    print(f"collection '{col.name}' now holds {count} chunks")
    print("sample ids:", col.peek(3).get("ids"))


if __name__ == "__main__":
    main()
