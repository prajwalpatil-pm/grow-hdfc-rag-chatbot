# 💬 HDFC Mutual Fund — Facts-Only FAQ Assistant (RAG)

A small, **trustworthy** question-answering chatbot over a fixed corpus of **HDFC mutual-fund
scheme pages**. It answers **factual** questions only — expense ratio, exit load, minimum SIP,
ELSS lock-in, riskometer, benchmark, fund manager, AUM — and **every answer carries exactly one
official source link** and a freshness date. It **refuses** advice/opinion and
returns/performance questions, and it **never accepts or stores PII**.

Built as a Retrieval-Augmented Generation (RAG) pipeline:
**Load → Chunk → Embed → ChromaDB → Retrieve → Guardrails → Grounded answer.**

> ⚠️ **Not investment advice.** Data is a point-in-time snapshot of public pages; always verify on
> the linked source.

---

## ✨ What it does

**Example**

```
Q: What is the expense ratio of HDFC Small Cap Fund?

HDFC Small Cap Fund's expense ratio (Direct plan) is 0.78%.
🔗 Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
Last updated from sources: 25 Sep 2026
```

```
Q: Should I buy HDFC Small Cap Fund?
🚫 I share facts only and can't advise on whether to buy, sell, or which scheme suits you.
   For guidance, please consult a SEBI-registered adviser…
```

**Answers** factual queries with one citation · **Refuses** advice, performance/returns, and PII ·
**Clarifies** when no in-scope scheme is named · Says **"not found"** (with the official link) rather
than guessing.

---

## 🧠 How it works

```
INGESTION (offline)                         QUERY (per prompt)
corpus/*.md                                 user prompt
   │ load frontmatter + body                   │
   │ chunk by H2 section (+ metadata)          ├─ PII guard ───────► refuse (nothing stored)
   │ embed (all-MiniLM-L6-v2, 384-d)           ├─ intent guard ────► refuse advice / performance
   ▼                                           │        (guards run BEFORE retrieval)
ChromaDB (cosine, persisted)  ◄───────────  resolve scheme → embed query → retrieve scheme chunks
                                               │ relevance gate → not_found + link
                                               │ answer (Mistral, else deterministic template)
                                               │ post-check: ≤3 sentences · 1 citation · freshness
                                               ▼
                                            grounded answer
```

- **Scheme-scoped retrieval.** The query is resolved to one of 5 schemes, then all of that scheme's
  ~10 section-chunks are retrieved so field extraction always sees the right section (the 5 pages
  are near-duplicate, so a scheme filter matters more than raw similarity).
- **Two generation modes.** `template` (default-safe, deterministic, zero hallucination — extracts
  the fact straight from the retrieved chunk) and `llm` (Mistral composes from context). The app
  **falls back to template automatically** on any LLM error (missing key, rate-limit, etc.).
- **Citations can't be hallucinated** — they're attached from chunk metadata in the post-check.

See [`architecture.md`](architecture.md) for the full data flow, [`PRD.md`](PRD.md) for
requirements, and [`implementation.md`](implementation.md) for the phased build plan.

---

## 🛠️ Tech stack

| Layer | Choice |
|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim, local, CPU) |
| Vector store | **ChromaDB** (persistent, cosine) |
| Generation | **Mistral** (`mistral-small-latest`) — optional; template fallback |
| UI | **Streamlit** |
| Language | Python 3.11 |
| Quality | `pytest` (37 tests) · `ruff` |

---

## 📁 Project structure

```
rag-agent/
├── README.md · PRD.md · architecture.md · implementation.md   # docs
├── config.py                       # all tunables (paths, model, k, thresholds, aliases)
├── requirements.txt · pyproject.toml · .env.example
├── corpus/                         # 5 HDFC scheme docs (markdown + frontmatter) + sources.csv/json
├── app/
│   ├── ingest/    loader · chunker · embedder · index · build_index · dump_chunks
│   ├── retrieve/  retriever            # embed query → Chroma search → relevance gate
│   ├── guardrails/ pii · intent · postcheck
│   ├── generate/  answerer · prompts   # template + Mistral, refusal/UI copy
│   └── pipeline.py                     # ask() orchestrator
├── ui/streamlit_app.py             # the chat UI
├── tests/                          # pytest suite
├── eval/retrieval_probe.py         # retrieval prompt-robustness probe
└── data/chroma/                    # persisted vector index (generated, git-ignored)
```

---

## 🚀 Getting started

**Prerequisites:** Python 3.11.

```bash
# 1. Clone
git clone https://github.com/prajwalpatil-pm/grow-hdfc-rag-chatbot.git
cd grow-hdfc-rag-chatbot

# 2. Virtual env + deps
python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash);  use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

# 3. (Optional) enable LLM generation via Mistral
cp .env.example .env                 # then put your MISTRAL_API_KEY in .env
# Leave GEN_MODE=template to run fully offline with no key.

# 4. Build the vector index (Load → Chunk → Embed → Store)
python -m app.ingest.build_index     # ~5 docs → ~47 chunks in data/chroma/

# 5a. Run the UI
streamlit run ui/streamlit_app.py    # http://localhost:8501

# 5b. …or the CLI
python -m app.pipeline "What is the expense ratio of HDFC Small Cap Fund?"
```

> First run downloads the MiniLM model (~90 MB) once.

---

## ✅ Testing & quality

```bash
python -m pytest            # 37 tests: loader, chunker, PII, intent, post-check, pipeline
python -m ruff check .      # lint
python -m eval.retrieval_probe   # prompt-robustness probe across paraphrases/synonyms/aliases
```

Tests force `template` mode for deterministic assertions.

---

## 🛡️ Guardrails & constraints (by design)

- **One citation per answer** + `Last updated from sources: <date>` (from chunk metadata).
- **≤ 3 sentences.**
- **No advice / opinion / suitability** — refused with an educational link.
- **No performance/returns** — refused with a factsheet link (per the brief).
- **No PII** — PAN / Aadhaar / phone / email / OTP / account numbers are refused and never stored.
- **Public sources only.** Never guesses — says "not found" with the official link when a fact is absent.

---

## 📚 Data & sources

Corpus = 5 HDFC schemes (Direct–Growth), collected from public Groww scheme pages
(snapshot 25 Sep 2026). Full manifest in [`corpus/sources.csv`](corpus/sources.csv).

| Scheme | Category |
|---|---|
| HDFC Large Cap Fund | Large Cap |
| HDFC Flexi Cap Fund | Flexi Cap |
| HDFC ELSS Tax Saver Fund | ELSS (3Y lock-in) |
| HDFC Small Cap Fund | Small Cap |
| HDFC Balanced Advantage Fund | Hybrid (Dynamic Asset Allocation) |

---

## ⚠️ Known limitations

- **Point-in-time data** — NAV/AUM/returns change daily; answers surface the snapshot date.
- **Template mode is phrasing-sensitive** — retrieval is robust to typos/synonyms, but deterministic
  extraction can miss misspellings (e.g. "expence"); LLM mode handles these.
- **Statement-download intent** ("how to get a capital-gains statement") isn't covered by the 5
  scheme pages — would need an official AMFI/CAMS/AMC statement-guide page added to the corpus.
- Scope is **HDFC-only, 5 schemes**; other funds return an out-of-scope clarification.

---

*This project is a learning/portfolio build. It is not affiliated with HDFC AMC or Groww, and it is
not investment advice.*
