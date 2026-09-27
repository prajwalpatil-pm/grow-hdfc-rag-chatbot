from datetime import date

from app.ingest.chunker import _coerce, chunk_doc, slugify
from app.ingest.loader import Doc


def _make_doc() -> Doc:
    body = (
        "# HDFC Test Fund\n\n"
        "## Fund Overview\n- **Expense Ratio:** 0.50%\n\n"
        "## Exit Load\n1% within 1 year.\n"
    )
    meta = {
        "doc_id": "hdfc-test",
        "scheme": "HDFC Test Fund - Direct Plan - Growth",
        "category": "Equity",
        "source_url": "http://example.com",
        "fetched_at": date(2026, 9, 27),
        "nav_as_of": date(2026, 9, 25),
    }
    return Doc(metadata=meta, body=body)


def test_slugify():
    assert slugify("Exit Load & Tax") == "exit-load-tax"


def test_coerce_date_and_none():
    assert _coerce(date(2026, 9, 25)) == "2026-09-25"
    assert _coerce(None) == ""
    assert _coerce("x") == "x"


def test_chunk_doc_sections_metadata_and_breadcrumb():
    chunks = chunk_doc(_make_doc())
    ids = {c.id for c in chunks}
    assert "hdfc-test::fund-overview" in ids
    assert "hdfc-test::exit-load" in ids

    fo = next(c for c in chunks if c.id.endswith("fund-overview"))
    assert fo.text.startswith("HDFC Test Fund - Direct Plan - Growth › Fund Overview")
    assert fo.metadata["section"] == "Fund Overview"
    # YAML dates must be coerced to Chroma-safe strings
    assert isinstance(fo.metadata["nav_as_of"], str)
    assert fo.metadata["nav_as_of"] == "2026-09-25"
