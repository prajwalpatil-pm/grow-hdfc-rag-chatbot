from app.ingest.loader import REQUIRED_KEYS, load_corpus, parse_frontmatter


def test_parse_frontmatter_basic():
    text = "---\ndoc_id: x\nscheme: S\n---\n# Title\nbody line\n"
    meta, body = parse_frontmatter(text)
    assert meta["doc_id"] == "x"
    assert meta["scheme"] == "S"
    assert "body line" in body
    assert not body.startswith("---")


def test_parse_frontmatter_no_frontmatter():
    meta, body = parse_frontmatter("no frontmatter here")
    assert meta == {}
    assert body == "no frontmatter here"


def test_load_corpus_has_five_valid_docs():
    docs = load_corpus()
    assert len(docs) == 5
    for d in docs:
        for k in REQUIRED_KEYS:
            assert d.metadata.get(k), f"missing {k}"
