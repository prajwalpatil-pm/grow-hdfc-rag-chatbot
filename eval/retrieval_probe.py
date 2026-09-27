"""Retrieval prompt-robustness probe (not pass/fail).

Surfaces how retrieval + scheme-resolution behave across paraphrases, synonyms,
misspellings, aliases and indirect phrasings. For each prompt it prints the
resolved scheme, the top-3 retrieved chunks (section=distance), and the final
answer type. Run from repo root:  python -m eval.retrieval_probe
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.pipeline import ask, resolve_scheme  # noqa: E402
from app.retrieve.retriever import search      # noqa: E402

GROUPS = {
    "Paraphrase / synonym (expense ratio, Small Cap)": [
        "What is the expense ratio of HDFC Small Cap Fund?",
        "HDFC Small Cap fund fees?",
        "how much does HDFC Small Cap charge",
        "TER of HDFC Small Cap Fund",
        "what is the cost of HDFC Small Cap Fund",
    ],
    "Misspellings": [
        "expence ratio of HDFC Small Cap Fund",
        "benchmrk of HDFC Large Cap Fund",
        "lock in period for HDFC ELSS Tax Saver",
    ],
    "Alias / short form": [
        "minimum SIP for flexi cap",
        "exit load on BAF",
        "benchmark of top 100 fund",
        "riskometer of tax saver",
    ],
    "Indirect phrasing": [
        "how long is my money locked in the ELSS fund",
        "which index does HDFC Large Cap track",
        "who is the fund manager for HDFC Flexi Cap",
    ],
    "Edge": [
        "expense ratio",
        "AUM of HDFC Mid Cap Fund",
        "portfolio turnover of HDFC Large Cap Fund",
    ],
}


def probe(q: str) -> None:
    sf = resolve_scheme(q)
    top = ""
    if sf:
        hits = search(q, scheme_filter=sf, k=3)
        top = " | ".join(f"{h.metadata['section']}={h.distance:.3f}" for h in hits[:3])
    r = ask(q)
    ans = r.text.split("\n")[0]
    if len(ans) > 88:
        ans = ans[:85] + "..."
    print(f"  Q: {q}")
    print(f"     scheme : {sf.split(' - ')[0] if sf else '—'}")
    if top:
        print(f"     top3   : {top}")
    print(f"     result : [{r.type}] {ans}")
    print()


def main() -> None:
    for group, qs in GROUPS.items():
        print("=" * 72)
        print(group)
        print("=" * 72)
        for q in qs:
            probe(q)


if __name__ == "__main__":
    main()
