import pytest

from app.guardrails.pii import contains_pii


@pytest.mark.parametrize(
    "text,kind",
    [
        ("My PAN is ABCDE1234F", "PAN"),
        ("Aadhaar 1234 5678 9012", "Aadhaar"),
        ("email me at a.b@test.com", "email"),
        ("call 9876543210", "phone"),
        ("please share the OTP now", "OTP"),
        ("account 123456789012345", "account number"),
    ],
)
def test_pii_positive(text, kind):
    hit, k = contains_pii(text)
    assert hit is True
    assert k == kind


@pytest.mark.parametrize(
    "text",
    [
        "What is the expense ratio of HDFC Small Cap Fund?",
        "Lock-in for HDFC ELSS Tax Saver?",
        "Who manages HDFC Flexi Cap Fund?",
    ],
)
def test_pii_negative(text):
    hit, _ = contains_pii(text)
    assert hit is False
