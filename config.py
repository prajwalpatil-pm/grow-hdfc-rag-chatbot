"""Central configuration for the MF FAQ RAG chatbot.

See architecture.md §7. All tunables live here so the pipeline stages stay
config-driven. Nothing in this module imports heavy deps, so it is safe to
import anywhere (including before the venv deps are installed).
"""
import os

from dotenv import load_dotenv

# --- Paths (anchored to this file's dir so the app runs from ANY working dir) ---
_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_ROOT, ".env"))  # load secrets/config from the git-ignored .env
CORPUS_DIR = os.path.join(_ROOT, "corpus")
CHROMA_PATH = os.path.join(_ROOT, "data", "chroma")

# --- Vector store ---
COLLECTION_NAME = "hdfc_mf_faq"
DISTANCE_METRIC = "cosine"          # ChromaDB hnsw:space

# --- Embeddings (brief-mandated model) ---
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384

# --- Retrieval ---
TOP_K = 4
# Once the query is resolved to ONE scheme, retrieve up to this many of that scheme's
# chunks (a scheme has ~10 sections) so field extraction always sees the right section.
# No cross-scheme risk because results are already filtered to the resolved scheme.
SCHEME_K = 12
# Loose backstop only: the scheme is already resolved and field-extraction returns
# not_found when a fact is absent, so this just rejects total-nonsense queries.
DISTANCE_THRESHOLD = 0.85          # cosine distance; > threshold => not_found.

# --- Answer constraints (brief) ---
MAX_SENTENCES = 3

# --- Generation (Mistral) ---
# GEN_MODE=llm uses Mistral (key in .env); otherwise deterministic template mode.
# The answerer falls back to template automatically on any API error/missing key.
GEN_MODE = os.getenv("GEN_MODE", "llm")             # "llm" | "template"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
LLM_TEMPERATURE = 0.0

# --- Scheme resolution: query alias -> exact `scheme` metadata value in the corpus frontmatter ---
SCHEME_LARGE_CAP = "HDFC Large Cap Fund - Direct Plan - Growth"
SCHEME_FLEXI_CAP = "HDFC Flexi Cap Fund - Direct Plan - Growth"
SCHEME_ELSS = "HDFC ELSS Tax Saver Fund - Direct Plan - Growth"
SCHEME_SMALL_CAP = "HDFC Small Cap Fund - Direct Plan - Growth"
SCHEME_BAF = "HDFC Balanced Advantage Fund - Direct Plan - Growth"

# Keys are lowercase substrings matched against the query (longest match wins in the resolver).
SCHEME_ALIASES = {
    "large cap": SCHEME_LARGE_CAP,
    "largecap": SCHEME_LARGE_CAP,
    "top 100": SCHEME_LARGE_CAP,
    "flexi cap": SCHEME_FLEXI_CAP,
    "flexicap": SCHEME_FLEXI_CAP,
    "flexi": SCHEME_FLEXI_CAP,
    "elss": SCHEME_ELSS,
    "tax saver": SCHEME_ELSS,
    "taxsaver": SCHEME_ELSS,
    "small cap": SCHEME_SMALL_CAP,
    "smallcap": SCHEME_SMALL_CAP,
    "balanced advantage": SCHEME_BAF,
    "baf": SCHEME_BAF,
    "dynamic asset allocation": SCHEME_BAF,
}

# Fallback educational / official links used by refusals & not_found (public sources only).
AMFI_EDU_URL = "https://www.amfiindia.com/investor-corner"
HDFC_AMC_URL = "https://www.hdfcfund.com"
