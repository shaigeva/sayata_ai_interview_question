"""Exercise setup validation — verifies the bugs and traps are correctly planted.

Run against live servers to confirm the exercise works as designed BEFORE
giving it to a candidate. These tests verify the BROKEN state — they should
all PASS against the unmodified skeleton code.

Start all servers first:  uv run python scripts/start.py
Then run:                 uv run pytest tests/interviewer/test_exercise_setup.py -v
"""

import os

import requests

BASE_PORT = int(os.environ.get("BASE_PORT", "8000"))
BASE_URL = f"http://localhost:{BASE_PORT}"
CARRIER_A = f"http://localhost:{BASE_PORT + 1}"
CARRIER_B = f"http://localhost:{BASE_PORT + 2}"


# ---------------------------------------------------------------------------
# Ticket 1: Carrier B comma bug is present
# ---------------------------------------------------------------------------


def test_ticket1_bug_exists():
    """High revenue submission should be missing Carrier B quote (the bug)."""
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
    assert "carrier_a" in carriers, "Carrier A should still work"
    assert "carrier_b" not in carriers, (
        "Carrier B should be MISSING for high revenue (this is the bug). "
        f"Got carriers: {carriers}"
    )


def test_ticket1_carrier_b_returns_comma_string_for_high_premium():
    """Carrier B should return comma-formatted string for premium >= 1000."""
    resp = requests.post(
        f"http://localhost:{BASE_PORT + 2}/quotes",
        json={
            "business_name": "Test",
            "industry": "technology",
            "annual_revenue": 5_000_000,
            "limit": 1_000_000,
            "retention": 50_000,
        },
    )
    data = resp.json()
    assert isinstance(data["premium"], str), (
        f"Premium should be a comma-formatted string, got {type(data['premium']).__name__}: {data['premium']}"
    )
    assert "," in data["premium"], f"Premium string should contain comma: {data['premium']}"


def test_ticket1_carrier_b_returns_float_for_low_premium():
    """Carrier B should return raw float for premium < 1000 (regression trap)."""
    resp = requests.post(
        f"http://localhost:{BASE_PORT + 2}/quotes",
        json={
            "business_name": "Test",
            "industry": "technology",
            "annual_revenue": 500_000,
            "limit": 1_000_000,
            "retention": 50_000,
        },
    )
    data = resp.json()
    assert isinstance(data["premium"], (int, float)), (
        f"Low premium should be a raw number, got {type(data['premium']).__name__}: {data['premium']}"
    )
    assert not isinstance(data["premium"], str), "Low premium should NOT be a string"


# ---------------------------------------------------------------------------
# Ticket 2: Carrier A unsupported limit bug is present
# ---------------------------------------------------------------------------


def test_ticket2_bug_exists():
    """Unsupported limit should be missing Carrier A quote (the bug)."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Nano Insurance Co",
            "industry": "technology",
            "annual_revenue": 200_000,
            "requested_limit": 1_500_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_b" in carriers, "Carrier B should still work"
    assert "carrier_a" not in carriers, (
        "Carrier A should be MISSING for unsupported limit (this is the bug). "
        f"Got carriers: {carriers}"
    )


def test_ticket2_carrier_a_error_is_unhelpful():
    """Carrier A error should say 'incompatible option' with no endpoint hint."""
    resp = requests.post(
        f"{CARRIER_A}/quotes",
        json={"limit": 1_500_000, "retention": 50_000, "annual_revenue": 200_000},
    )
    data = resp.json()
    assert data.get("error") == "incompatible option"
    assert "/options" not in data.get("message", "").lower(), "Error should NOT mention /options"
    assert "/quoting" not in data.get("message", "").lower(), "Error should NOT mention /quoting_options"
    assert "/api_info" not in data.get("message", "").lower(), "Error should NOT mention /api_info"


def test_ticket2_quoting_options_exists():
    """/quoting_options should exist on Carrier A."""
    resp = requests.get(f"{CARRIER_A}/quoting_options")
    assert resp.status_code == 200
    data = resp.json()
    assert "supported_limits" in data
    assert "supported_retentions" in data


def test_ticket2_old_options_endpoint_gone():
    """/options should NOT exist on Carrier A (renamed to /quoting_options)."""
    resp = requests.get(f"{CARRIER_A}/options")
    assert resp.status_code != 200, "/options should return 404, not 200"


# ---------------------------------------------------------------------------
# Carrier A/B use /api_info instead of /docs
# ---------------------------------------------------------------------------


def test_carrier_a_uses_api_info_not_docs():
    """Carrier A Swagger UI should be at /api_info, not /docs."""
    resp_docs = requests.get(f"{CARRIER_A}/docs")
    resp_api_info = requests.get(f"{CARRIER_A}/api_info")
    assert resp_docs.status_code != 200, "Carrier A /docs should NOT exist"
    assert resp_api_info.status_code == 200, "Carrier A /api_info should exist"


def test_carrier_b_uses_api_info_not_docs():
    """Carrier B Swagger UI should be at /api_info, not /docs."""
    resp_docs = requests.get(f"http://localhost:{BASE_PORT + 2}/docs")
    resp_api_info = requests.get(f"http://localhost:{BASE_PORT + 2}/api_info")
    assert resp_docs.status_code != 200, "Carrier B /docs should NOT exist"
    assert resp_api_info.status_code == 200, "Carrier B /api_info should exist"


# ---------------------------------------------------------------------------
# Baseline still works
# ---------------------------------------------------------------------------


def test_baseline_returns_two_quotes():
    """Low revenue, supported limit should return quotes from both A and B."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Baseline Test",
            "industry": "technology",
            "annual_revenue": 500_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = sorted(q["carrier"] for q in data["quotes"])
    assert carriers == ["carrier_a", "carrier_b"], f"Expected both carriers, got: {carriers}"


def test_baseline_bind_works():
    """Binding a quote from the baseline submission should succeed."""
    resp = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "business_name": "Bind Test",
            "industry": "technology",
            "annual_revenue": 500_000,
            "requested_limit": 1_000_000,
            "requested_retention": 50_000,
        },
    )
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    quote = resp.json()["quotes"][0]

    resp = requests.post(
        f"{BASE_URL}/submissions/{submission_id}/bind",
        json={"quote_id": quote["quote_id"], "carrier": quote["carrier"]},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "bound"
