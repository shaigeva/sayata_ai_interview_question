"""Verification test suite — run against live servers.

Start all servers first:  python scripts/start.py
Then run:                 uv run pytest tests/test_verification.py -v
"""

import time

import requests

BASE_URL = "http://localhost:8000"


def test_basic_flow():
    """Skeleton flow: submit with low revenue, get quotes from both carriers, bind one.

    This should PASS with the skeleton implementation.
    """
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

    # Bind the first quote
    quote = data["quotes"][0]
    resp = requests.post(
        f"{BASE_URL}/submissions/{submission_id}/bind",
        json={"quote_id": quote["quote_id"], "carrier": quote["carrier"]},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "bound"


def test_task1_high_value_policy():
    """Task 1: High revenue submission should still return 2 quotes.

    Currently FAILS — Carrier B returns comma-formatted prices for
    premiums >= $1,000, and parsing breaks silently.
    """
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
    assert len(data["quotes"]) == 2, (
        f"Expected 2 quotes but got {len(data['quotes'])}. "
        f"Check carrier responses for parsing issues."
    )


def test_task2_high_limit_request():
    """Task 2: High limit request should still return 2 quotes.

    Currently FAILS — Carrier A returns 200 with error body for
    unsupported limits, and the server doesn't handle it.
    """
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
    assert len(data["quotes"]) == 2, (
        f"Expected 2 quotes but got {len(data['quotes'])}. "
        f"Check if all carriers are responding correctly."
    )


def test_task3_polling_carrier():
    """Task 3: Submission should include a quote from Carrier C.

    Requires integrating Carrier C, which uses a polling-based API.
    The candidate must add this integration.
    """
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

    # Wait for polling to complete
    time.sleep(10)

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_c" in carriers, (
        f"Expected a quote from carrier_c but got quotes from: {carriers}"
    )


def test_task4_unfamiliar_carrier():
    """Task 4: Submission should include a quote from Carrier D.

    Requires integrating Carrier D, which uses a completely different
    API shape. The candidate must explore and add this integration.
    """
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
        f"Expected a quote from carrier_d but got quotes from: {carriers}"
    )
