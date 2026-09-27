import pytest

from app.guardrails.intent import classify


@pytest.mark.parametrize(
    "query,expected",
    [
        ("Should I buy HDFC Small Cap Fund?", "advice"),
        ("Which HDFC fund is best?", "advice"),
        ("Which HDFC fund gave the best returns?", "performance"),
        ("What are the 3 year returns of HDFC Small Cap?", "performance"),
        ("What is the expense ratio of HDFC Small Cap Fund?", "factual"),
        # 'growth' in the plan name must NOT be read as a performance query
        ("HDFC Small Cap Fund Direct Growth expense ratio", "factual"),
        # 'riskometer' contains 'ter' but must stay factual (not expense/advice)
        ("What is the riskometer of HDFC ELSS Tax Saver Fund?", "factual"),
        ("What is the benchmark of HDFC Large Cap Fund?", "factual"),
    ],
)
def test_classify(query, expected):
    assert classify(query) == expected
