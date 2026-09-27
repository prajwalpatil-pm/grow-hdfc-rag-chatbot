"""Query pipeline orchestrator. architecture.md §6.

Phase 2 scope = the happy path: resolve scheme -> retrieve -> relevance gate ->
grounded answer with a single citation + freshness stamp. The PII/advice/
performance guardrails and the answer post-check are added in Phase 3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import config
from app.generate.answerer import answer as generate_answer
from app.generate.prompts import (
    CLARIFY_SCHEME,
    NOT_FOUND_MSG,
    REFUSAL_ADVICE,
    REFUSAL_PERFORMANCE,
    REFUSAL_PII,
)
from app.guardrails.intent import classify
from app.guardrails.pii import contains_pii
from app.guardrails.postcheck import finalize
from app.retrieve.retriever import passes_gate, search


@dataclass
class AskResponse:
    type: str                       # answer | not_found | refusal_* (Phase 3)
    text: str
    source_url: str | None = None
    last_updated: str | None = None
    citations: list = field(default_factory=list)
    debug: dict = field(default_factory=dict)


def resolve_scheme(query: str) -> str | None:
    """Map the query to one scheme via config.SCHEME_ALIASES (longest alias wins)."""
    q = query.lower()
    best_alias, best_scheme = "", None
    for alias, scheme in config.SCHEME_ALIASES.items():
        if alias in q and len(alias) > len(best_alias):
            best_alias, best_scheme = alias, scheme
    return best_scheme


def _fmt_date(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%d %b %Y").lstrip("0")
    except Exception:
        return iso


def ask(query: str) -> AskResponse:
    # --- Guard-first ordering (architecture.md §6/§8). Deterministic guards run
    # before any embedding/retrieval, so unsafe/out-of-scope inputs short-circuit. ---

    # 1. PII guard — refuse and store nothing (do not echo the raw query anywhere).
    is_pii, kind = contains_pii(query)
    if is_pii:
        return AskResponse(type="refusal_pii", text=REFUSAL_PII,
                           debug={"intent": "pii", "pii_kind": kind, "retrieved": False})

    # 2. Intent guard — performance checked before advice.
    intent = classify(query)
    if intent == "performance":
        return AskResponse(type="refusal_performance", text=REFUSAL_PERFORMANCE,
                           debug={"intent": "performance", "retrieved": False})
    if intent == "advice":
        return AskResponse(type="refusal_advice", text=REFUSAL_ADVICE,
                           debug={"intent": "advice", "retrieved": False})

    # 3. Factual path. This corpus has 5 near-duplicate scheme pages, so we require
    # the query to name one of them (else clarify). Stricter than architecture.md §9's
    # "search all", which caused cross-scheme mismatches on lookalike text.
    scheme_filter = resolve_scheme(query)
    if scheme_filter is None:
        return AskResponse(
            type="out_of_scope",
            text=CLARIFY_SCHEME,
            debug={"intent": "factual", "scheme_filter": None, "retrieved_ids": [], "top_distance": None},
        )

    chunks = search(query, scheme_filter=scheme_filter, k=config.SCHEME_K)
    debug = {
        "intent": "factual",
        "scheme_filter": scheme_filter,
        "retrieved_ids": [c.id for c in chunks],
        "top_distance": round(min((c.distance for c in chunks), default=1.0), 4),
    }

    if not passes_gate(chunks):
        url = chunks[0].metadata["source_url"] if chunks else config.HDFC_AMC_URL
        return AskResponse(type="not_found", text=f"{NOT_FOUND_MSG} {url}", debug=debug)

    top = chunks[0]
    text = generate_answer(query, chunks)
    if not text:  # known scheme, but the specific fact isn't in our sources
        return AskResponse(type="not_found", text=f"{NOT_FOUND_MSG} {top.metadata['source_url']}", debug=debug)

    source_url = top.metadata["source_url"]
    last_updated = _fmt_date(top.metadata["nav_as_of"])
    return AskResponse(
        type="answer",
        text=finalize(text, source_url, last_updated),  # <=3 sentences + one citation + stamp
        source_url=source_url,
        last_updated=last_updated,
        citations=[source_url],
        debug=debug,
    )


if __name__ == "__main__":
    import json
    import sys

    try:  # Windows consoles default to cp1252 and choke on ₹ (U+20B9)
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    q = " ".join(sys.argv[1:]) or "What is the expense ratio of HDFC Small Cap Fund?"
    r = ask(q)
    print("Q:", q)
    print("type:", r.type)
    print(r.text)  # for `answer`, this already includes the Source + freshness lines
    print("debug:", json.dumps(r.debug, ensure_ascii=False))
