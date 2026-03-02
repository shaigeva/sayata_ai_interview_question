#!/usr/bin/env python3
"""Quick verification script — run against live servers.

Usage:
    uv run python scripts/verify.py

This script sends a few requests to the running server and prints the results.
Use it to quickly check that the basic flow works. It does NOT use pytest.
"""

import sys

import requests

BASE_URL = "http://localhost:8000"


def main():
    print("=" * 60)
    print("Sayata Quoting Platform — Quick Verification")
    print("=" * 60)
    print()

    # --- Check server is up ---
    try:
        requests.get(f"{BASE_URL}/submissions/health-check", timeout=3)
    except requests.ConnectionError:
        print("ERROR: Cannot connect to server at", BASE_URL)
        print("Make sure you've started the servers:")
        print("  uv run python scripts/start.py")
        sys.exit(1)

    # --- Basic submission ---
    print("1. Creating a basic submission (low revenue)...")
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
    if resp.status_code != 201:
        print(f"   FAIL — expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
    else:
        submission_id = resp.json()["id"]
        print(f"   OK — submission created: {submission_id}")

        resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
        data = resp.json()
        print(f"   Quotes received: {len(data['quotes'])}")
        for q in data["quotes"]:
            print(f"     - {q['carrier']}: premium=${q['premium']}, "
                  f"limit=${q['limit']}, retention=${q['retention']}")

    print()

    # --- High revenue submission ---
    print("2. Creating a high-revenue submission ($5M)...")
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
    if resp.status_code == 201:
        submission_id = resp.json()["id"]
        resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
        data = resp.json()
        print(f"   Quotes received: {len(data['quotes'])}")
        for q in data["quotes"]:
            print(f"     - {q['carrier']}: premium=${q['premium']}")
    else:
        print(f"   Got status {resp.status_code}: {resp.text}")

    print()

    # --- High limit submission ---
    print("3. Creating a high-limit submission ($5M limit)...")
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
    if resp.status_code == 201:
        submission_id = resp.json()["id"]
        resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
        data = resp.json()
        print(f"   Quotes received: {len(data['quotes'])}")
        for q in data["quotes"]:
            print(f"     - {q['carrier']}: premium=${q['premium']}, limit=${q['limit']}")
    else:
        print(f"   Got status {resp.status_code}: {resp.text}")

    print()

    # --- Check carrier simulators ---
    print("4. Carrier simulator status:")
    for port, name in [(8001, "Carrier A"), (8002, "Carrier B"), (8003, "Carrier C"), (8004, "Carrier D")]:
        try:
            if port == 8004:
                resp = requests.get(f"http://localhost:{port}/api/v1/info", timeout=2)
            else:
                resp = requests.get(f"http://localhost:{port}/status", timeout=2)
            print(f"   {name} (:{port}): UP")
        except requests.ConnectionError:
            print(f"   {name} (:{port}): DOWN")

    print()
    print("=" * 60)
    print("Done. Review the output above to check your progress.")
    print("=" * 60)


if __name__ == "__main__":
    main()
