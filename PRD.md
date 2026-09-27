# PRD — Mutual Fund FAQ Assistant (Facts-Only RAG Chatbot)

| | |
|---|---|
| **Product** | HDFC Mutual Fund FAQ Assistant — a facts-only, citation-backed Q&A chatbot |
| **Owner** | Prajwal Patil |
| **Status** | Draft v1.0 |
| **Date** | 2026-09-27 |
| **Source brief** | `docs/Buildhour-27th-sept-brief.docx` (Build Hour, 27 Sep) |
| **End output** | RAG chatbot (Loading → Chunking → Embedding → Vector store → Retrieval → Grounded answer) |

---

## 1. TL;DR
Build a small, trustworthy FAQ assistant that answers **factual** questions about a fixed set of HDFC mutual-fund schemes — expense ratio, exit load, minimum SIP, ELSS lock-in, riskometer, benchmark, and how to obtain statements — using **only official public pages**. Every answer carries **exactly one source link**, stays **≤3 sentences**, and shows a "Last updated from sources" date. The assistant **refuses advice/opinion and portfolio questions**, never handles PII, and never computes or compares performance. It is powered by a RAG pipeline over a 5-document corpus, embedded with `all-MiniLM-L6-v2` and stored in ChromaDB.

## 2. Problem & context
Retail investors comparing schemes — and the support/content teams who field the same questions repeatedly — have to dig facts out of factsheets, KIM/SID, and fee pages that are scattered and dense. They want a **fast, correct, source-linked** factual answer, not a recommendation. A general chatbot is untrustworthy here: it hallucinates numbers, gives unlicensed advice, and can't cite. The opportunity is a **narrow, grounded, auditable** assistant whose value is precisely that it *only* states verifiable facts and *always* shows the source.

## 3. Goals & non-goals

**Goals (in priority order)**
1. **Grounded factual answers** — respond to in-scope factual queries strictly from the corpus.
2. **Trust via citation** — every factual answer includes one official public source link + a freshness date.
3. **Safe refusals** — decline advice/opinion/portfolio questions politely, with a facts-only message and an educational link.
4. **Compliance by design** — no PII capture/storage, no performance claims, answers ≤3 sentences.

**Non-goals (explicitly out of scope for v1)**
- Buy/sell/hold recommendations or any suitability judgement.
- Computing, projecting, or comparing returns/performance.
- Portfolio construction, goal planning, or tax filing help.
- Transactions, KYC, login, or any personalization.
- Multi-AMC coverage — v1 is **HDFC only**, the 5 listed schemes only.
- Real-time NAV — answers reflect the point-in-time corpus snapshot.

## 4. Target users & jobs-to-be-done
- **Retail comparer** — "When I'm shortlisting HDFC schemes, I want to check a specific fact (fee, lock-in, benchmark) fast and from a source I trust, so I can compare without wading through a factsheet."
- **Support / content agent** — "When a customer asks a routine factual MF question, I want a canned, citation-backed answer, so I reply consistently and correctly without escalation."

## 5. Success metrics & acceptance criteria
Framed for a build-hour eval (run against the sample Q&A set in §14):

| Metric | Target | How measured |
|---|---|---|
| **Citation coverage** | 100% of factual answers carry exactly 1 valid source link | automated check over eval set |
| **Groundedness / factual accuracy** | ≥ 90% of factual answers match the source value | manual check vs corpus |
| **Refusal correctness** | 100% of advice/opinion/portfolio queries refused | eval set of ~5 opinion queries |
| **PII safety** | 100% of PII-bearing inputs refused & not stored | eval set of PAN/phone/email inputs |
| **Answer length** | ≤ 3 sentences | automated check |
| **Freshness stamp** | present on every factual answer | automated check |
| **Latency** | ≤ ~3s per answer (local) | timing |

## 6. Scope — corpus (public sources only)
**AMC:** HDFC Mutual Fund. **Plan:** Direct – Growth. **Snapshot:** collected 2026-09-27, NAV as of 2026-09-25. Full corpus lives in `corpus/`.

| # | Scheme | Category | Source |
|---|---|---|---|
| 1 | HDFC Large Cap Fund | Large Cap | groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 2 | HDFC Flexi Cap Fund | Flexi Cap | groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 3 | HDFC ELSS Tax Saver Fund | ELSS (3Y lock-in) | groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 4 | HDFC Small Cap Fund | Small Cap | groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 5 | HDFC Balanced Advantage Fund | Hybrid (Dyn. Alloc.) | groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |

> Note on sources: the brief references AMC/SEBI/AMFI public pages. HDFC's own site (hdfcfund.com) blocks automated fetches (HTTP 403), so **Groww's public scheme pages** are used as the accessible public source. See §17 (Risks) and §19 (Open questions) on ToS and on adding an official statement-guide page.

## 7. Functional requirements

**FR1 — Answer in-scope factual queries.** Supported intents: expense ratio · exit load · minimum SIP / lumpsum · ELSS lock-in · riskometer / risk level · benchmark index · NAV & AUM (as-of snapshot) · fund manager(s) · launch date · category. Also: "how to download capital-gains / account statement" *(see coverage gap in §19 — needs an added source doc)*.
*Acceptance:* returns the correct value from the retrieved chunk, scoped to the named scheme.

**FR2 — One citation per answer.** Every factual answer ends with a single `Source:` link taken from the retrieved chunk's `source_url` metadata.
*Acceptance:* exactly one link; the link is one of the 5 official corpus URLs.

**FR3 — Refuse advice/opinion/portfolio queries.** e.g. "Should I buy/sell?", "Which is best?", "Is this good for me?" → polite facts-only refusal + one educational/official link.
*Acceptance:* no numeric/recommendation content; refusal copy shown (§12).

**FR4 — Freshness stamp.** Every factual answer appends `Last updated from sources: 25 Sep 2026`.

**FR5 — Out-of-scope / not-found handling.** If the query is factual but not answerable from the corpus (unknown scheme, missing field), say so plainly and point to the official page — do **not** guess.

**FR6 — PII guard.** Detect PAN, Aadhaar, account numbers, OTPs, emails, phone numbers in input; refuse to process/store; respond with a privacy-safe message. Nothing is persisted.

**FR7 — No performance claims.** Never compute/compare/project returns. If asked, decline and link the official factsheet.

**FR8 — Tiny UI.** Welcome line + 3 example questions + persistent disclaimer: "Facts-only. No investment advice." (§12).

## 8. Guardrails & constraints (from the brief — non-negotiable)
- **Public sources only.** No third-party blogs; no screenshots of app back-end as sources.
- **No PII.** Do not accept or store PAN, Aadhaar, account numbers, OTPs, emails, phone numbers.
- **No performance claims.** Don't compute/compare returns; link the official factsheet instead.
- **Clarity & transparency.** Answers ≤ 3 sentences; always add "Last updated from sources: <date>".
- **Disclaimer** shown in the UI at all times.

## 9. System architecture (RAG)

```
INGESTION (offline, run once / on refresh)
  corpus/*.md ──► Load ──► Chunk (section-aware) ──► Embed (all-MiniLM-L6-v2) ──► ChromaDB
     (5 docs)                 + metadata                                          (persisted)

RETRIEVAL (per query, online)
  user query
     │
     ├─► [Guard: PII filter] ──(PII)──► privacy refusal (FR6)
     ├─► [Guard: intent classifier] ──(advice/opinion)──► facts-only refusal (FR3)
     │                                └─(performance)────► factsheet-link refusal (FR7)
     ▼ (factual, in-scope)
  embed query ──► ChromaDB top-k similarity (+ optional metadata filter: scheme)
     ▼
  retrieved chunks (text + source_url + nav_as_of)
     ▼
  LLM composes answer  ── grounded, ≤3 sentences, 1 citation, freshness stamp
     ▼
  [Post-check: length ≤3 sentences, exactly 1 link, no advice verbs] ──► answer
```

**Tech stack**
- **Language:** Python 3.11
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (brief-mandated; 384-dim, fast, local, CPU-friendly)
- **Vector DB:** ChromaDB (brief-mandated; persistent local client)
- **Generation LLM:** **Mistral** (`mistral-small-latest`, low temperature) for short extractive answers; key in a git-ignored `.env`. A template-only answer mode is the automatic fallback if no LLM/key is available or on any API error.
- **UI:** Streamlit (fastest path to a working prototype) *(alt: static HTML+JS — see §19)*
- **Orchestration:** thin custom pipeline (LangChain optional, not required at this size)

## 10. Chunking strategy (recommendation)
The brief says "ask Cursor to decide the chunking strategy based on the data." The data is **short, highly structured fact-sheet markdown** — one file per fund, with stable H2 sections (Fund Overview, Trailing Returns, Holdings, Exit Load & Tax, Fund Managers, About) and small tables.

**Recommendation: structure-aware (header-based) chunking, one chunk per H2 section.**
- Target ~150–350 tokens/chunk; overlap ~40–50 tokens between adjacent sections to preserve context.
- **Attach metadata to every chunk:** `doc_id, scheme, category, section, source_url, fetched_at, nav_as_of`.
- Prepend a header breadcrumb to each chunk's text (e.g. "HDFC Small Cap Fund › Exit Load & Tax") so the embedding captures which fund + field it describes.

**Why not naive fixed-size splitting:** a fee/lock-in value can get separated from its label, and facts from two funds could land in one chunk — both cause wrong retrievals. Section chunks keep each fact with its label and scheme. The `scheme` metadata also enables a **filtered query** ("expense ratio of HDFC Small Cap" → filter `scheme = HDFC Small Cap Fund` before similarity), which sharply improves precision on a small, near-duplicate corpus (all 5 funds share very similar text).

## 11. Data model — chunk record
```
{
  "id": "hdfc-small-cap-fund::exit-load-tax",
  "text": "HDFC Small Cap Fund › Exit Load & Tax\nExit load of 1% if redeemed within 1 year...",
  "embedding": [384 floats],
  "metadata": {
    "doc_id": "hdfc-small-cap-fund",
    "scheme": "HDFC Small Cap Fund - Direct Plan - Growth",
    "category": "Equity - Small Cap",
    "section": "Exit Load & Tax",
    "source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "fetched_at": "2026-09-27",
    "nav_as_of": "2026-09-25"
  }
}
```

## 12. UX copy (draft, ready to use)
**Welcome line:** "Hi! I answer factual questions about 5 HDFC mutual-fund schemes — fees, lock-in, benchmark, and more — with a source link for every answer. **Facts-only. No investment advice.**"

**3 example questions:**
1. "What is the expense ratio of HDFC Small Cap Fund?"
2. "What is the lock-in period for the HDFC ELSS Tax Saver Fund?"
3. "What is the minimum SIP for HDFC Flexi Cap Fund?"

**Factual answer format:**
> HDFC Small Cap Fund's expense ratio (Direct plan) is 0.78%.
> Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
> Last updated from sources: 25 Sep 2026

**Advice/opinion refusal (FR3):**
> I share facts only and can't advise on whether to buy, sell, or which scheme suits you. For guidance, please consult a SEBI-registered adviser. You can learn how mutual funds work here: https://www.amfiindia.com/investor-corner

**Performance-claim refusal (FR7):**
> I don't compute or compare returns. You can see the official performance in the scheme factsheet: <source_url>.

**PII refusal (FR6):**
> For your privacy, please don't share personal details like PAN, Aadhaar, account numbers, or phone/email. I don't collect any personal data. Ask me a factual question about a scheme instead.

**Persistent disclaimer (footer):** "Facts-only assistant. Not investment advice. Data is a point-in-time snapshot from official public pages; verify on the linked source."

## 13. Answer & refusal decision logic
1. **PII scan** (regex: PAN `[A-Z]{5}[0-9]{4}[A-Z]`, Aadhaar 12-digit, phone, email, long digit runs) → PII refusal.
2. **Intent classification** → `advice/opinion` (buy, sell, should I, best, worth it, recommend, suitable) → FR3 refusal; `performance` (compare returns, will it grow, projected) → FR7 refusal.
3. **Factual & in-scope** → retrieve → grounded answer + citation + stamp.
4. **Factual but not found** → FR5 not-found message + official link.

## 14. Sample Q&A coverage (maps to deliverable `sample-qa.md`)
Factual (should answer w/ citation): (1) Expense ratio of HDFC Small Cap Fund? (2) ELSS Tax Saver lock-in period? (3) Minimum SIP for HDFC Flexi Cap Fund? (4) Exit load on HDFC Balanced Advantage Fund? (5) Benchmark of HDFC Large Cap Fund? (6) Riskometer of HDFC ELSS Tax Saver Fund? (7) Who manages HDFC Flexi Cap Fund?
Refusals (should decline): (8) "Should I buy HDFC Small Cap?" (9) "Which HDFC fund gives the best returns?" (10) "My PAN is ABCDE1234F, open an account" (PII).

## 15. Hypotheses (to validate)
- **I think** users trust a short answer *more* when it shows one clean source link than when it shows several — one citation reads as authoritative, many read as hedging.
- **I think** filtering retrieval by `scheme` metadata will matter more than the embedding model here, because all 5 fund pages are near-duplicate in wording and pure similarity will confuse them.
- **I think** most real queries will be about fees, lock-in, and minimum SIP — so getting those three intents airtight covers the majority of value.
- **I think** the biggest trust risk is *stale* numbers, not *wrong* ones — so the freshness stamp is a feature, not fine print.

## 16. Milestones / build plan
- **M0 — Corpus (DONE):** 5 HDFC pages collected in `corpus/` + `sources.json`/`sources.csv`.
- **M1 — Ingestion & index:** loader → section-aware chunker (§10) → embed (`all-MiniLM-L6-v2`) → persist to ChromaDB with metadata.
- **M2 — Retrieval & grounded answer:** query embed → top-k (+ scheme filter) → LLM composes ≤3-sentence answer with 1 citation + stamp; not-found handling (FR5).
- **M3 — Guardrails:** PII filter (FR6), advice/opinion classifier (FR3), performance refusal (FR7), post-checks.
- **M4 — UI:** Streamlit app — welcome + 3 examples + disclaimer + chat.
- **M5 — Eval & deliverables:** run §14 eval; produce sample-qa, README, disclaimer snippet; record demo if not hosted.

## 17. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Stale point-in-time data | Freshness stamp on every answer; a `refresh_corpus` script to re-fetch; state snapshot date in UI |
| Hallucinated numbers | Retrieval-grounded generation, low temperature, "answer only from context, else say not found", cite the chunk |
| Wrong scheme retrieved (near-duplicate pages) | `scheme` metadata filter before similarity; disambiguate if scheme not named |
| Advice leakage | Intent classifier + strict system prompt + post-check for recommendation verbs |
| PII captured | Input regex filter, refuse + do not persist, no logging of raw inputs |
| Source ToS / scraping | Store only extracted facts + link back; prefer official AMC/AMFI/SEBI pages where fetchable; see §19 |
| "Download statement" intent unanswerable | Coverage gap — add an official statement-guide page or scope the intent out (see §19) |

## 18. Deliverables checklist (from brief)
- [ ] Working prototype (Streamlit app) **or** ≤3-min demo video.
- [x] **Source list** of the 5 URLs → `corpus/sources.csv` + `corpus/sources.json`.
- [ ] **README** with setup steps, scope (AMC + schemes), known limits → `README.md` (root, at M5).
- [ ] **Sample Q&A file** (5–10 queries + answers + links) → `sample-qa.md` (at M5).
- [x] **Disclaimer snippet** used in the UI → §12 (persistent disclaimer + refusals).
- [x] **Corpus** (5 public pages) → `corpus/`.

## 19. Open questions / decisions for you
1. **Statement-guide coverage gap.** The brief lists "how to download the capital-gains statement" as a sample query, but the 5 scheme pages don't contain it. **Recommend:** add one official page (HDFC/CAMS/AMFI statement-guide) as a 6th source, or explicitly scope that intent out of v1. Which do you want?
2. **UI framework.** Recommend **Streamlit** (fastest working prototype for the build hour). Alternative: a static HTML+JS page calling a small local API. OK to go Streamlit?
3. **Generation LLM.** DECIDED: **Mistral** (`mistral-small-latest`), key in `.env`. Template mode remains the deterministic, zero-hallucination fallback and is used automatically whenever the LLM is unavailable (e.g. rate-limited).
4. **Answer style.** Numeric-first one-liner (as in §12) vs. a short sentence — confirm §12 format is what you want.
```
