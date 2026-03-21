"""Internal verification test suite — NOT given to candidates.

This is the full pytest-based test suite used by interviewers to verify that
all tasks have been completed correctly. Run against live servers.

Start all servers first:  uv run python scripts/start.py
Then run:                 uv run pytest tests/test_verification.py -v
"""

import os
import time

import requests

BASE_PORT = int(os.environ.get("BASE_PORT", "8000"))
BASE_URL = f"http://localhost:{BASE_PORT}"


# ---------------------------------------------------------------------------
# Baseline — should pass with the skeleton implementation
# ---------------------------------------------------------------------------


def test_basic_flow():
    """Skeleton flow: low-revenue submit, 2 quotes, bind."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Small Tech Co",
            "industry": "technology",
            "annual_revenue": 500_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["quotes"]) == 2, (
        f"Expected 2 quotes but got {len(data['quotes'])}. "
        f"Carriers returned: {[q['carrier'] for q in data['quotes']]}"
    )

    quote = data["quotes"][0]
    resp = requests.post(
        f"{BASE_URL}/submissions/{submission_id}/bind",
        json={"quote_id": quote["quote_id"], "carrier": quote["carrier"]},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "bound"


def test_submission_not_found():
    """GET for nonexistent submission returns 404."""
    resp = requests.get(f"{BASE_URL}/submissions/nonexistent-id")
    assert resp.status_code == 404


def test_low_revenue_both_carriers():
    """Low revenue produces quotes from both A and B with premiums under $1K."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Tiny Startup",
            "industry": "technology",
            "annual_revenue": 300_000,
            "requested_limit": 500_000,
            "requested_retention": 25_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = sorted(q["carrier"] for q in data["quotes"])
    assert "carrier_a" in carriers
    assert "carrier_b" in carriers


# ---------------------------------------------------------------------------
# Ticket 1 — Carrier B comma-formatted prices
# ---------------------------------------------------------------------------


def test_ticket1_high_value_policy():
    """High revenue ($5M) must still return quotes from both A and B."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Big Tech Corp",
            "industry": "technology",
            "annual_revenue": 5_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_a" in carriers, f"Missing carrier_a. Got: {carriers}"
    assert "carrier_b" in carriers, f"Missing carrier_b. Got: {carriers}"


def test_ticket1_premium_is_numeric():
    """Carrier B premium should be a proper number, not a formatted string."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Revenue Test Co",
            "industry": "manufacturing",
            "annual_revenue": 4_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    for quote in data["quotes"]:
        assert isinstance(quote["premium"], (int, float)), (
            f"Premium from {quote['carrier']} is not numeric: {quote['premium']}"
        )


# ---------------------------------------------------------------------------
# Ticket 2 — Carrier A unsupported limits + business rule
# ---------------------------------------------------------------------------


def test_ticket2_high_limit_request():
    """High limit ($5M) — both carriers should still return quotes."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Large Enterprise",
            "industry": "manufacturing",
            "annual_revenue": 2_000_000,
            "requested_limit": 5_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_a" in carriers, f"Missing carrier_a. Got: {carriers}"
    assert "carrier_b" in carriers, f"Missing carrier_b. Got: {carriers}"


def test_ticket2_uses_closest_limit():
    """When limit is unsupported, Carrier A quote should use closest available."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Limit Fallback Co",
            "industry": "technology",
            "annual_revenue": 1_000_000,
            "requested_limit": 5_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carrier_a_quotes = [q for q in data["quotes"] if q["carrier"] == "carrier_a"]
    assert len(carrier_a_quotes) == 1, "Expected a quote from carrier_a"
    # Closest supported limit to 5M is 3M
    assert carrier_a_quotes[0]["limit"] == 3_000_000, (
        f"Expected carrier_a to fall back to limit 3000000 but got {carrier_a_quotes[0]['limit']}"
    )


def test_ticket2_unsupported_retention():
    """Unsupported retention should also fall back to closest available."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Retention Test Co",
            "industry": "technology",
            "annual_revenue": 1_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 75_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carrier_a_quotes = [q for q in data["quotes"] if q["carrier"] == "carrier_a"]
    assert len(carrier_a_quotes) == 1
    # Closest supported retention to 75K is either 50K or 100K
    assert carrier_a_quotes[0]["retention"] in (50_000, 100_000), (
        f"Expected carrier_a retention to be 50000 or 100000 but got {carrier_a_quotes[0]['retention']}"
    )


# ---------------------------------------------------------------------------
# Ticket 3 — Carrier C polling integration
# ---------------------------------------------------------------------------


def test_ticket3_carrier_c_present():
    """Submission should include a quote from Carrier C after polling completes."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Medium Co",
            "industry": "technology",
            "annual_revenue": 3_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    time.sleep(10)

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_c" in carriers, (
        f"Expected carrier_c but got: {carriers}"
    )


def test_ticket3_carrier_c_quote_fields():
    """Carrier C quote should have all standard fields."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Fields Test Co",
            "industry": "retail",
            "annual_revenue": 2_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    time.sleep(10)

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carrier_c_quotes = [q for q in data["quotes"] if q["carrier"] == "carrier_c"]
    assert len(carrier_c_quotes) == 1
    q = carrier_c_quotes[0]
    assert q["carrier"] == "carrier_c"
    assert isinstance(q["premium"], (int, float)) and q["premium"] > 0
    assert q["limit"] > 0
    assert q["retention"] > 0
    assert q["quote_id"].startswith("cc-")


# ---------------------------------------------------------------------------
# Ticket 4 — Carrier D unfamiliar API
# ---------------------------------------------------------------------------


def test_ticket4_carrier_d_present():
    """Submission should include a quote from Carrier D."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Another Corp",
            "industry": "technology",
            "annual_revenue": 2_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_d" in carriers, (
        f"Expected carrier_d but got: {carriers}"
    )


def test_ticket4_carrier_d_quote_normalized():
    """Carrier D quote should be normalized to standard format."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Normalization Test",
            "industry": "finance",
            "annual_revenue": 3_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carrier_d_quotes = [q for q in data["quotes"] if q["carrier"] == "carrier_d"]
    assert len(carrier_d_quotes) == 1
    q = carrier_d_quotes[0]
    assert q["carrier"] == "carrier_d"
    assert isinstance(q["premium"], (int, float)) and q["premium"] > 0
    assert q["limit"] > 0
    assert q["retention"] > 0
    assert q["quote_id"].startswith("cd-")


def test_ticket4_carrier_d_bind():
    """Binding a Carrier D quote should work."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Bind Test D",
            "industry": "technology",
            "annual_revenue": 1_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    time.sleep(5)

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carrier_d_quotes = [q for q in data["quotes"] if q["carrier"] == "carrier_d"]
    if carrier_d_quotes:
        q = carrier_d_quotes[0]
        resp = requests.post(
            f"{BASE_URL}/submissions/{submission_id}/bind",
            json={"quote_id": q["quote_id"], "carrier": "carrier_d"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "bound"


# ---------------------------------------------------------------------------
# End-to-end — all carriers together
# ---------------------------------------------------------------------------


def test_all_carriers_combined():
    """After all tickets are resolved, a standard submission should return 4 quotes."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Full Integration Corp",
            "industry": "technology",
            "annual_revenue": 2_000_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    time.sleep(10)

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = sorted(q["carrier"] for q in data["quotes"])
    assert carriers == ["carrier_a", "carrier_b", "carrier_c", "carrier_d"], (
        f"Expected all 4 carriers but got: {carriers}"
    )
