"""Input-side PII detection. architecture.md §6 step 1, §8; PRD FR6.

Detects common Indian PII in the user's query so the pipeline can refuse BEFORE
any retrieval/LLM call. This function never logs or stores the raw input.
"""
from __future__ import annotations

import re

# Order matters: more specific / longer patterns first (Aadhaar & phone before the
# generic long-digit "account number" run).
_PATTERNS = [
    ("PAN", re.compile(r"\b[A-Za-z]{5}[0-9]{4}[A-Za-z]\b")),
    ("Aadhaar", re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("phone", re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)")),
    ("OTP", re.compile(r"\botp\b", re.I)),
    ("account number", re.compile(r"(?<!\d)\d{9,18}(?!\d)")),
]


def contains_pii(text: str) -> tuple[bool, str | None]:
    """Return (True, kind) on the first PII match, else (False, None)."""
    for kind, pat in _PATTERNS:
        if pat.search(text):
            return True, kind
    return False, None
