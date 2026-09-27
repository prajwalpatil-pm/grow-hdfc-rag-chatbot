"""Intent classification. architecture.md §6 step 2, §8; PRD FR3/FR7.

Rule-based (keyword) classifier -> "factual" | "advice" | "performance".
Performance is checked before advice so "which fund gave the best returns?" is
treated as a performance query (per the brief: no computing/comparing returns).
"""
from __future__ import annotations

import re

# Return/performance cues. NOTE: bare "grow"/"growth" is deliberately excluded —
# it appears in plan names ("Direct - Growth") and would false-trigger.
_PERFORMANCE = [
    "returns", "return", "cagr", "performance", "perform", "performed", "outperform",
    "compare returns", "compare performance", "projected", "forecast", "future return",
    "expected return", "annualised return", "annual return", "how much will",
    "how much would", "gave more", "grow my money", "best returns",
]

# Advice / opinion / suitability cues.
_ADVICE = [
    "should i", "shall i", "should you", "buy", "sell", "recommend", "recommendation",
    "recommended", "suitable", "worth", "best", "which is best",
    "which fund", "which scheme", "better", "invest in", "good investment",
    "is it good", "is this good",
]


def _hit(q: str, words: list[str]) -> bool:
    return any(re.search(r"\b" + re.escape(w) + r"\b", q) for w in words)


def classify(query: str) -> str:
    q = query.lower()
    if _hit(q, _PERFORMANCE):
        return "performance"
    if _hit(q, _ADVICE):
        return "advice"
    return "factual"
