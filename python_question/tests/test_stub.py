"""Stub test — verifies the test infrastructure works."""

from sayata.models import Quote, Submission


def test_models_importable():
    """Verify test infrastructure is working."""
    sub = Submission(
        id="test-id",
        business_name="Test Corp",
        industry="technology",
        annual_revenue=1_000_000,
        requested_limit=1_000_000,
        requested_retention=50_000,
    )
    assert sub.business_name == "Test Corp"


def test_quote_model():
    """Verify Quote model works."""
    quote = Quote(
        carrier="carrier_a",
        premium=15000,
        limit=1_000_000,
        retention=50_000,
        quote_id="test-quote",
    )
    assert quote.carrier == "carrier_a"
    assert quote.premium == 15000
