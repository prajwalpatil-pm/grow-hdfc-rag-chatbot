"""Pytest session setup: make sure the ChromaDB index exists before tests run."""
import pytest

import config
from app.ingest.build_index import main as build_index_main
from app.ingest.index import get_collection

# Tests exercise retrieval/extraction/guardrail logic deterministically — never a
# live LLM. Force template mode regardless of .env so assertions are stable.
config.GEN_MODE = "template"


@pytest.fixture(scope="session", autouse=True)
def _ensure_index():
    if get_collection().count() == 0:
        build_index_main()
    yield
