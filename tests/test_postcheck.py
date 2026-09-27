import re

from app.guardrails.postcheck import finalize

URL = "https://example.com/scheme"


def test_finalize_appends_single_citation_and_stamp():
    out = finalize("The expense ratio is 0.78%.", URL, "25 Sep 2026")
    assert out.count("Source:") == 1
    assert f"Source: {URL}" in out
    assert "Last updated from sources: 25 Sep 2026" in out


def test_finalize_limits_to_three_sentences():
    out = finalize("One. Two. Three. Four. Five.", URL, "25 Sep 2026")
    body = out.split("\n\n")[0]
    assert len(re.findall(r"[.!?]", body)) <= 3


def test_finalize_strips_model_inserted_urls():
    out = finalize("See http://evil.example for details.", URL, "25 Sep 2026")
    assert "evil.example" not in out
    assert f"Source: {URL}" in out
