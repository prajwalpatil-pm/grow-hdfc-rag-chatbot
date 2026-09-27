"""Compose a grounded, <=3-sentence answer from retrieved context.

architecture.md §6 step 8. Two modes:
  - "template" (default): deterministic — extract the asked field straight from
    the retrieved chunk. No LLM, zero hallucination risk. Returns None when it
    can't confidently answer (the pipeline turns that into `not_found`).
  - "llm": Mistral composes from context; falls back to template on error.
The Source link and freshness stamp are attached by the pipeline/post-check,
never here.
"""
from __future__ import annotations

import re

import config
from app.generate.prompts import SYSTEM_PROMPT
from app.retrieve.retriever import RetrievedChunk

# Ordered most-specific-first; first field whose keyword appears (whole-word) in the query wins.
# `label` = regex matched against the left-of-colon label in a corpus line.
# `exclude` = regex; if it matches the label, that line is skipped (e.g. skip AMC-wide "Total AUM").
_FIELDS = [
    {"name": "lock-in", "kw": ["lock-in", "lock in", "lockin", "locked in", "locked"],
     "label": r"lock-?in", "exclude": None,
     "phrase": "{scheme} has a lock-in period of {value}."},
    {"name": "expense ratio", "kw": ["expense ratio", "expense", "expenses", "fee", "fees", "cost", "ter"],
     "label": r"expense ratio", "exclude": None,
     "phrase": "{scheme}'s expense ratio (Direct plan) is {value}."},
    {"name": "exit load", "kw": ["exit load", "exit"],
     "label": r"exit load", "exclude": None,
     "phrase": "The exit load for {scheme} is: {value}"},
    {"name": "minimum sip", "kw": ["sip"],
     "label": r"min.*sip", "exclude": None,
     "phrase": "The minimum SIP for {scheme} is {value}."},
    {"name": "minimum investment", "kw": ["minimum investment", "min investment", "lumpsum", "minimum lumpsum"],
     "label": r"min.*(1st|first|investment)", "exclude": r"sip",
     "phrase": "The minimum investment for {scheme} is {value}."},
    {"name": "benchmark", "kw": ["benchmark", "index"],
     "label": r"benchmark", "exclude": None,
     "phrase": "The benchmark for {scheme} is {value}."},
    {"name": "riskometer", "kw": ["riskometer", "risk level", "risk"],
     "label": r"risk level", "exclude": None,
     "phrase": "The risk level (riskometer) of {scheme} is {value}."},
    {"name": "nav", "kw": ["nav", "net asset value"],
     "label": r"nav", "exclude": None,
     "phrase": "The NAV of {scheme} is {value}."},
    {"name": "aum", "kw": ["aum", "fund size", "fund value", "assets under management"],
     "label": r"aum|fund size", "exclude": r"total",
     "phrase": "The AUM (fund size) of {scheme} is {value}."},
    {"name": "category", "kw": ["category", "type of fund", "what type"],
     "label": r"category", "exclude": None,
     "phrase": "{scheme} is categorised as {value}."},
    {"name": "launch date", "kw": ["launch", "inception", "launched"],
     "label": r"launch date", "exclude": None,
     "phrase": "{scheme} was launched on {value}."},
    {"name": "fund manager", "kw": ["fund manager", "who manages", "managed by", "manager"],
     "label": None, "exclude": None, "phrase": None},  # special-cased
]

_GENERAL_INTENT = ("about", "overview", "tell me", "describe", "summary", "summarise", "summarize", "details", "detail")


def answer(query: str, chunks: list[RetrievedChunk], mode: str | None = None) -> str | None:
    """Return a grounded answer string, or None if not confidently answerable."""
    mode = mode or config.GEN_MODE
    if not chunks:
        return None
    if mode == "llm":
        try:
            out = _answer_llm(query, chunks)
            if out:
                return out
        except Exception:
            pass  # graceful fallback to template
    return _answer_template(query, chunks)


# ---------- template mode ----------

def _short_scheme(scheme: str) -> str:
    return scheme.split(" - ")[0].strip()  # "HDFC Small Cap Fund"


def _detect_field(q: str):
    for f in _FIELDS:
        for k in f["kw"]:
            if re.search(r"\b" + re.escape(k) + r"\b", q):
                return f
    return None


def _extract(chunks, label_regex, exclude=None):
    lab = re.compile(label_regex, re.I)
    exc = re.compile(exclude, re.I) if exclude else None
    for c in chunks:
        for raw in c.text.split("\n"):
            line = raw.strip().lstrip("-*• ").replace("**", "").strip()
            if ":" in line:
                left, right = line.split(":", 1)
                if lab.search(left) and right.strip() and not (exc and exc.search(left)):
                    return right.strip(), c
    return None, None


def _summarize(chunk) -> str | None:
    lines = [ln.strip().lstrip("-*• ").replace("**", "").strip()
             for ln in chunk.text.split("\n")[1:] if ln.strip()]
    body = " ".join(lines)
    parts = re.split(r"(?<=[.!?])\s+", body)
    return " ".join(parts[: config.MAX_SENTENCES]).strip() or None


def _answer_template(query: str, chunks: list[RetrievedChunk]) -> str | None:
    q = query.lower()
    field = _detect_field(q)
    scheme = _short_scheme(chunks[0].metadata.get("scheme", ""))

    if field and field["name"] == "fund manager":
        # Match both "Fund Managers" and "Fund Management" section titles.
        mgr = next((c for c in chunks if "manage" in c.metadata.get("section", "").lower()), None)
        if mgr:
            names = [n.strip() for n in re.findall(r"\*\*([^*]+?)\*\*\s*\(", mgr.text)]
            if names:
                return f"{_short_scheme(mgr.metadata.get('scheme', ''))} is managed by {', '.join(names)}."
        return None

    if field and field["label"]:
        value, _ = _extract(chunks, field["label"], field.get("exclude"))
        if value:
            return field["phrase"].format(scheme=scheme, value=value)
        # Prose fields (e.g. exit load): summarise the section chunk that matches the field name.
        fwords = set(field["name"].replace("-", " ").split())
        for c in chunks:
            sec = set(c.metadata.get("section", "").lower().replace("-", " ").split())
            if fwords & sec:
                return _summarize(c)
        return None

    # No known field: only summarise for explicit "about/overview" style queries; else not answerable.
    if any(g in q for g in _GENERAL_INTENT):
        return _summarize(chunks[0])
    return None


# ---------- llm mode (optional) ----------

def _answer_llm(query: str, chunks: list[RetrievedChunk]) -> str | None:
    from mistralai import Mistral

    context = "\n\n".join(f"[{i + 1}] {c.text}" for i, c in enumerate(chunks))
    client = Mistral(api_key=config.MISTRAL_API_KEY)
    resp = client.chat.complete(
        model=config.MISTRAL_MODEL,
        max_tokens=200,
        temperature=config.LLM_TEMPERATURE,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"Context:\n{context}\n\nQuestion: {query}\n\n"
                        f"Answer in <=3 sentences using ONLY the context above."},
        ],
    )
    return (resp.choices[0].message.content or "").strip() or None
