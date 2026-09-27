"""Section-aware chunking: one chunk per H2 section.

architecture.md §4.2 & §5 step 2; PRD §10. Each chunk text is prefixed with a
"scheme › section" breadcrumb so the embedding captures which fund + field it
describes. Metadata values are coerced to Chroma-safe primitives.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from app.ingest.loader import Doc

_slug_re = re.compile(r"[^a-z0-9]+")
_h2_re = re.compile(r"^##\s+(.*)$")

# Metadata keys carried onto each chunk (Chroma requires primitive values).
_CARRY = ("doc_id", "scheme", "category", "source_url", "fetched_at", "nav_as_of")


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict


def slugify(s: str) -> str:
    return _slug_re.sub("-", s.strip().lower()).strip("-")


def _coerce(v):
    """Coerce a frontmatter value into a Chroma-safe primitive.

    YAML parses bare dates (e.g. 2026-09-25) into datetime.date objects, which
    Chroma rejects — convert those (and anything non-primitive) to strings.
    """
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return v
    return str(v)


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split a markdown body on H2 (## ) headings into (title, text) pairs.

    Content before the first H2 (the H1 title, any intro note) is ignored.
    """
    sections: list[tuple[str, str]] = []
    title: str | None = None
    buf: list[str] = []
    for line in body.split("\n"):
        m = _h2_re.match(line)
        if m:
            if title is not None:
                sections.append((title, "\n".join(buf).strip()))
            title = m.group(1).strip()
            buf = []
        elif title is not None:
            buf.append(line)
    if title is not None:
        sections.append((title, "\n".join(buf).strip()))
    return sections


def chunk_doc(doc: Doc) -> list[Chunk]:
    """Turn one Doc into a list of section chunks with metadata."""
    scheme = doc.metadata["scheme"]
    doc_id = doc.metadata["doc_id"]
    base_meta = {k: _coerce(doc.metadata.get(k)) for k in _CARRY}

    chunks: list[Chunk] = []
    for title, text in _split_sections(doc.body):
        if not text:
            continue
        chunk_text = f"{scheme} › {title}\n{text}"
        meta = dict(base_meta, section=title)
        chunks.append(Chunk(id=f"{doc_id}::{slugify(title)}", text=chunk_text, metadata=meta))
    return chunks
