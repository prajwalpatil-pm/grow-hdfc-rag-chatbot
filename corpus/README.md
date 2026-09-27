# RAG Corpus — HDFC Mutual Fund (5 public pages)

Knowledge base for the facts-only MF FAQ chatbot. **AMC:** HDFC Mutual Fund. **Source:** public scheme pages on Groww (groww.in), Direct–Growth plans. **Collected:** 2026-09-27 (NAV as of 2026-09-25). Matches the Build Hour 27-Sep brief's scheme list exactly.

## Documents

| # | File | Scheme | Category |
|---|------|--------|----------|
| 1 | `01-hdfc-large-cap-fund.md` | HDFC Large Cap Fund | Equity — Large Cap |
| 2 | `02-hdfc-flexi-cap-fund.md` | HDFC Flexi Cap Fund | Equity — Flexi Cap |
| 3 | `03-hdfc-elss-tax-saver-fund.md` | HDFC ELSS Tax Saver Fund | Equity — ELSS (3Y lock-in) |
| 4 | `04-hdfc-small-cap-fund.md` | HDFC Small Cap Fund | Equity — Small Cap |
| 5 | `05-hdfc-balanced-advantage-fund.md` | HDFC Balanced Advantage Fund | Hybrid — Dynamic Asset Allocation |

## Structure
- Each `.md` file has YAML frontmatter (`doc_id`, `scheme`, `category`, `source_url`, `fetched_at`, `nav_as_of`) — usable as chunk metadata for retrieval and citation.
- `sources.json` / `sources.csv` are the machine-readable manifest / submission source list (id → file → url).

## Caveats for the RAG agent
- Values are **point-in-time** (NAV, AUM, returns change daily) — surface the `fetched_at` / `nav_as_of` dates when answering ("Last updated from sources: 25 Sep 2026").
- Each page's free-text "about" section repeats the **AMC-wide** AUM (~₹9,86,237 Cr); the fund-specific AUM is in the "Fund Overview" section. Prefer the overview figure.
- Groww slugs are not predictable from fund names (Flexi Cap → `hdfc-equity-fund`, ELSS → `hdfc-taxsaver`).
- **Coverage gap:** these 5 scheme pages do NOT cover "how to download a capital-gains/account statement." That intent needs an AMC/CAMS/AMFI statement-guide page — see the PRD open questions.
- This is not investment advice — data reproduced from public pages for a retrieval demo.
