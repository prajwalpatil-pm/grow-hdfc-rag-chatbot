"""Answer post-check / finalizer. architecture.md §6 step 9, §8; PRD FR2/FR4.

Enforces the brief's answer constraints on a factual draft: <=3 sentences, no
model-inserted URLs, then appends EXACTLY ONE citation + freshness stamp (both
sourced from chunk metadata, never from the model).
"""
from __future__ import annotations

import re

import config

_URL_RE = re.compile(r"https?://\S+")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _limit_sentences(text: str, n: int) -> str:
    parts = _SENTENCE_RE.split(text.strip())
    return " ".join(parts[:n]).strip()


def finalize(draft: str, source_url: str, last_updated: str) -> str:
    """Return the display-ready answer: clean body + one Source + freshness stamp."""
    body = _URL_RE.sub("", draft).strip()          # strip any URLs the model added
    body = _limit_sentences(body, config.MAX_SENTENCES)
    return (
        f"{body}\n\n"
        f"Source: {source_url}\n"
        f"Last updated from sources: {last_updated}"
    )
