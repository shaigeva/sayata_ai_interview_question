"""Candidate results test suite.

Run this with all servers running to see which tickets are working:

    uv run pytest tests/interviewer/test_candidate_results.py -v

Tests are grouped by ticket. A passing group means that ticket is solved.
"""

import os
import time

import requests

BASE_PORT = int(os.environ.get("BASE_PORT", "8000"))
BASE_URL = f"http://localhost:{BASE_PORT}"


def submit(data: dict) -> str:
    """Helper: create a submission and return its ID."""
    resp = requests.post(f"{BASE_URL}/submissions", json=data)
    assert resp.status_code == 201, f"POST /submissions failed: {resp.status_code}"
    return resp.json()["id"]


def get_submission(submission_id: str) -> dict:
    """Helper: retrieve a submission by ID."""
    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    assert resp.status_code == 200
    return resp.json()


def get_carriers(submission_id: str) -> list[str]:
    """Helper: return sorted list of carrier names for a submission."""
    data = get_submission(submission_id)
    return sorted(q["carrier"] for q in data["quotes"])


def get_quotes_by_carrier(submission_id: str, carrier: str) -> list[dict]:
    """Helper: return quotes from a specific carrier."""
    data = get_submission(submission_id)
    return [q for q in data["quotes"] if q["carrier"] == carrier]


# ---------------------------------------------------------------------------
# Baseline — these should always pass (no ticket work required)
# ---------------------------------------------------------------------------


class TestBaseline:
    """Basic platform functionality that works out of the box."""

    def test_health(self):
        """Server health endpoint responds."""
        resp = requests.get(f"{BASE_URL}/health")
        assert resp.status_code == 200

    def test_submit_and_get(self):
        """Can create and retrieve a submission."""
        sid = submit({
            "business_name": "Test Co",
            "industry": "technology",
            "annual_revenue": 500_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        data = get_submission(sid)
        assert data["business_name"] == "Test Co"

    def test_low_revenue_returns_two_quotes(self):
        """Low-revenue submission returns quotes from both Carrier A and B."""
        sid = submit({
            "business_name": "Small Startup",
            "industry": "technology",
            "annual_revenue": 300_000,
            "requested_limit": 500_000,
            "requested_retention": 25_000,
        })
        carriers = get_carriers(sid)
        assert "carrier_a" in carriers
        assert "carrier_b" in carriers

    def test_bind_quote(self):
        """Can bind a quote from a submission."""
        sid = submit({
            "business_name": "Bind Test Co",
            "industry": "technology",
            "annual_revenue": 500_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        data = get_submission(sid)
        quote = data["quotes"][0]
        resp = requests.post(
            f"{BASE_URL}/submissions/{sid}/bind",
            json={"quote_id": quote["quote_id"], "carrier": quote["carrier"]},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "bound"

    def test_submission_not_found(self):
        """Nonexistent submission returns 404."""
        resp = requests.get(f"{BASE_URL}/submissions/does-not-exist")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Ticket 1 — Carrier B high-revenue quotes
# ---------------------------------------------------------------------------


class TestTicket1:
    """Ticket 1: Carrier B's quote should appear for high-revenue submissions."""

    def test_high_revenue_both_carriers(self):
        """$5M revenue submission returns quotes from both Carrier A and B."""
        sid = submit({
            "business_name": "Big Tech Corp",
            "industry": "technology",
            "annual_revenue": 5_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        carriers = get_carriers(sid)
        assert "carrier_a" in carriers, f"Missing carrier_a. Got: {carriers}"
        assert "carrier_b" in carriers, f"Missing carrier_b. Got: {carriers}"

    def test_premium_is_integer(self):
        """All premiums should be whole dollar amounts (integers)."""
        sid = submit({
            "business_name": "Premium Check Co",
            "industry": "manufacturing",
            "annual_revenue": 4_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        data = get_submission(sid)
        for quote in data["quotes"]:
            assert isinstance(quote["premium"], int), (
                f"Premium from {quote['carrier']} should be an integer, "
                f"got: {quote['premium']} ({type(quote['premium']).__name__})"
            )

    def test_low_revenue_still_works(self):
        """Low-revenue submissions should still work (regression check)."""
        sid = submit({
            "business_name": "Small Co Regression",
            "industry": "retail",
            "annual_revenue": 400_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        carriers = get_carriers(sid)
        assert "carrier_b" in carriers, "Carrier B should work for low revenue too"


# ---------------------------------------------------------------------------
# Ticket 2 — Carrier A unsupported limit/retention fallback
# ---------------------------------------------------------------------------


class TestTicket2:
    """Ticket 2: Carrier A should return quotes even for unsupported limits."""

    def test_unsupported_limit_returns_quote(self):
        """Unsupported limit ($1.5M) should still return a Carrier A quote."""
        sid = submit({
            "business_name": "Nano Insurance Co",
            "industry": "technology",
            "annual_revenue": 200_000,
            "requested_limit": 1_500_000,
            "requested_retention": 50_000,
        })
        carriers = get_carriers(sid)
        assert "carrier_a" in carriers, f"Missing carrier_a. Got: {carriers}"

    def test_limit_fallback_rounds_up(self):
        """Limit $1.5M should fall back to $2M (next available >= requested)."""
        sid = submit({
            "business_name": "Limit Fallback Co",
            "industry": "technology",
            "annual_revenue": 200_000,
            "requested_limit": 1_500_000,
            "requested_retention": 50_000,
        })
        quotes = get_quotes_by_carrier(sid, "carrier_a")
        assert len(quotes) == 1, "Expected a quote from carrier_a"
        assert quotes[0]["limit"] == 2_000_000, (
            f"Expected limit 2000000 (nearest >=) but got {quotes[0]['limit']}"
        )

    def test_limit_above_max_uses_highest(self):
        """Limit $5M (above all options) should fall back to highest available."""
        sid = submit({
            "business_name": "High Limit Co",
            "industry": "technology",
            "annual_revenue": 200_000,
            "requested_limit": 5_000_000,
            "requested_retention": 50_000,
        })
        quotes = get_quotes_by_carrier(sid, "carrier_a")
        assert len(quotes) == 1, "Expected a quote from carrier_a"
        assert quotes[0]["limit"] == 3_000_000, (
            f"Expected limit 3000000 (highest available) but got {quotes[0]['limit']}"
        )

    def test_retention_fallback_rounds_down(self):
        """Retention $75K should fall back to $50K (nearest <= requested)."""
        sid = submit({
            "business_name": "Retention Test Co",
            "industry": "technology",
            "annual_revenue": 200_000,
            "requested_limit": 1_000_000,
            "requested_retention": 75_000,
        })
        quotes = get_quotes_by_carrier(sid, "carrier_a")
        assert len(quotes) == 1
        assert quotes[0]["retention"] == 50_000, (
            f"Expected retention 50000 (nearest <=) but got {quotes[0]['retention']}"
        )

    def test_high_limit_both_carriers(self):
        """$5M limit should return quotes from both carriers."""
        sid = submit({
            "business_name": "Large Enterprise",
            "industry": "manufacturing",
            "annual_revenue": 2_000_000,
            "requested_limit": 5_000_000,
            "requested_retention": 50_000,
        })
        carriers = get_carriers(sid)
        assert "carrier_a" in carriers, f"Missing carrier_a. Got: {carriers}"
        assert "carrier_b" in carriers, f"Missing carrier_b. Got: {carriers}"


# ---------------------------------------------------------------------------
# Ticket 3 — Carrier C integration
# ---------------------------------------------------------------------------


class TestTicket3:
    """Ticket 3: Carrier C should be integrated and return quotes."""

    def test_carrier_c_returns_quote(self):
        """Submission should include a quote from Carrier C."""
        sid = submit({
            "business_name": "Carrier C Test",
            "industry": "technology",
            "annual_revenue": 3_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        time.sleep(10)
        carriers = get_carriers(sid)
        assert "carrier_c" in carriers, f"Expected carrier_c but got: {carriers}"

    def test_carrier_c_quote_has_standard_fields(self):
        """Carrier C quote should have all standard fields."""
        sid = submit({
            "business_name": "Fields Test C",
            "industry": "retail",
            "annual_revenue": 2_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        time.sleep(10)
        quotes = get_quotes_by_carrier(sid, "carrier_c")
        assert len(quotes) == 1, "Expected one quote from carrier_c"
        q = quotes[0]
        assert q["carrier"] == "carrier_c"
        assert isinstance(q["premium"], (int, float)) and q["premium"] > 0
        assert q["limit"] > 0
        assert q["retention"] > 0
        assert q["quote_id"].startswith("cc-")


# ---------------------------------------------------------------------------
# Ticket 4 — Carrier D integration
# ---------------------------------------------------------------------------


class TestTicket4:
    """Ticket 4: Carrier D should be integrated and return normalized quotes."""

    def test_carrier_d_returns_quote(self):
        """Submission should include a quote from Carrier D."""
        sid = submit({
            "business_name": "Carrier D Test",
            "industry": "technology",
            "annual_revenue": 2_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        carriers = get_carriers(sid)
        assert "carrier_d" in carriers, f"Expected carrier_d but got: {carriers}"

    def test_carrier_d_quote_normalized(self):
        """Carrier D quote should be normalized to standard format."""
        sid = submit({
            "business_name": "Normalization Test D",
            "industry": "finance",
            "annual_revenue": 3_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        quotes = get_quotes_by_carrier(sid, "carrier_d")
        assert len(quotes) == 1, "Expected one quote from carrier_d"
        q = quotes[0]
        assert q["carrier"] == "carrier_d"
        assert isinstance(q["premium"], (int, float)) and q["premium"] > 0
        assert q["limit"] > 0
        assert q["retention"] > 0
        assert q["quote_id"].startswith("cd-")

    def test_carrier_d_bind(self):
        """Binding a Carrier D quote should work."""
        sid = submit({
            "business_name": "Bind Test D",
            "industry": "technology",
            "annual_revenue": 1_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        time.sleep(5)
        quotes = get_quotes_by_carrier(sid, "carrier_d")
        assert len(quotes) >= 1, "Expected a quote from carrier_d"
        q = quotes[0]
        resp = requests.post(
            f"{BASE_URL}/submissions/{sid}/bind",
            json={"quote_id": q["quote_id"], "carrier": "carrier_d"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "bound"


# ---------------------------------------------------------------------------
# Full integration — all tickets together
# ---------------------------------------------------------------------------


class TestAllTickets:
    """All tickets solved: a single submission should return all 4 carriers."""

    def test_all_four_carriers(self):
        """Standard submission returns quotes from all 4 carriers."""
        sid = submit({
            "business_name": "Full Integration Corp",
            "industry": "technology",
            "annual_revenue": 2_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        })
        time.sleep(10)
        carriers = get_carriers(sid)
        assert carriers == ["carrier_a", "carrier_b", "carrier_c", "carrier_d"], (
            f"Expected all 4 carriers but got: {carriers}"
        )
