"""System prompt, refusal copy, and UI strings. Sourced from PRD §12."""
from __future__ import annotations

import config

SYSTEM_PROMPT = (
    "You are a facts-only assistant for HDFC mutual-fund schemes. "
    "Answer ONLY using the provided context. If the answer is not in the context, "
    "say you don't have that fact and point to the official page. "
    "Rules: at most 3 sentences; state facts only; never give investment advice; "
    "never compute, compare, or project returns. Do not add a source link yourself "
    "— it is appended automatically."
)

WELCOME = (
    "Hi! I answer factual questions about 5 HDFC mutual-fund schemes — fees, lock-in, "
    "benchmark, and more — with a source link for every answer. "
    "Facts-only. No investment advice."
)

EXAMPLES = [
    "What is the expense ratio of HDFC Small Cap Fund?",
    "What is the lock-in period for the HDFC ELSS Tax Saver Fund?",
    "What is the minimum SIP for HDFC Flexi Cap Fund?",
]

DISCLAIMER = (
    "Facts-only assistant. Not investment advice. Data is a point-in-time snapshot "
    "from official public pages; verify on the linked source."
)

REFUSAL_ADVICE = (
    "I share facts only and can't advise on whether to buy, sell, or which scheme suits "
    "you. For guidance, please consult a SEBI-registered adviser. "
    f"Learn how mutual funds work here: {config.AMFI_EDU_URL}"
)

REFUSAL_PERFORMANCE = (
    "I don't compute or compare returns. For official performance figures, please see "
    f"the scheme's factsheet on the AMC site: {config.HDFC_AMC_URL}"
)

REFUSAL_PII = (
    "For your privacy, please don't share personal details like PAN, Aadhaar, account "
    "numbers, OTPs, or phone/email. I don't collect any personal data. "
    "Ask me a factual question about a scheme instead."
)

NOT_FOUND_MSG = (
    "I don't have that fact in my sources for this scheme. Please check the official page:"
)

CLARIFY_SCHEME = (
    "I can answer factual questions about these 5 HDFC schemes: Large Cap, Flexi Cap, "
    "ELSS Tax Saver, Small Cap, and Balanced Advantage. Which one do you mean?"
)
