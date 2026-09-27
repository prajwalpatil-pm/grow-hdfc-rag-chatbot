"""End-to-end pipeline tests (require the ChromaDB index; built by conftest)."""
import re

from app.pipeline import ask


def _sentences(body: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", body.strip()) if s]


def test_factual_small_cap_expense():
    r = ask("What is the expense ratio of HDFC Small Cap Fund?")
    assert r.type == "answer"
    assert "0.78%" in r.text
    assert len(r.citations) == 1
    assert r.text.count("Source:") == 1


def test_factual_elss_lockin():
    r = ask("What is the lock-in period for HDFC ELSS Tax Saver Fund?")
    assert r.type == "answer"
    assert "3 years" in r.text.lower()


def test_refusal_advice():
    assert ask("Should I buy HDFC Small Cap Fund?").type == "refusal_advice"


def test_refusal_performance():
    assert ask("Which HDFC fund gave the best returns?").type == "refusal_performance"


def test_refusal_pii_stores_no_citation():
    r = ask("My PAN is ABCDE1234F please open an account")
    assert r.type == "refusal_pii"
    assert len(r.citations) == 0


def test_not_found_missing_field():
    assert ask("What is the portfolio turnover ratio of HDFC Large Cap Fund?").type == "not_found"


def test_out_of_scope_unknown_scheme():
    assert ask("What is the AUM of HDFC Mid Cap Fund?").type == "out_of_scope"


def test_synonym_fees_maps_to_expense_ratio():
    r = ask("HDFC Small Cap fund fees?")
    assert r.type == "answer"
    assert "0.78%" in r.text


def test_synonym_index_maps_to_benchmark():
    r = ask("which index does HDFC Large Cap track")
    assert r.type == "answer"
    assert "NIFTY 100" in r.text


def test_terse_alias_exit_load_baf():
    r = ask("exit load on BAF")
    assert r.type == "answer"
    assert "1%" in r.text


def test_fund_manager_for_management_section_title():
    # HDFC Large Cap / ELSS title this section "Fund Management" (not "Fund Managers").
    r = ask("who is the fund manager of hdfc large cap fund?")
    assert r.type == "answer"
    assert "Rahul Baijal" in r.text


def test_answers_stay_within_three_sentences():
    for q in [
        "What is the expense ratio of HDFC Small Cap Fund?",
        "What is the benchmark of HDFC Large Cap Fund?",
        "Who manages HDFC Flexi Cap Fund?",
    ]:
        body = ask(q).text.split("\n\n")[0]
        assert len(_sentences(body)) <= 3
