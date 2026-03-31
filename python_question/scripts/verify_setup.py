#!/usr/bin/env python3
"""Setup verification — starts each carrier individually and checks it responds.

Usage:
    uv run python scripts/verify_setup.py

Starts each carrier simulator one at a time on its default port, verifies it
responds, then stops it. Also checks the candidate server. This confirms the
environment is correctly set up without needing all servers running at once.
"""

import os
import signal
import subprocess
import sys
import time

import requests

BASE_PORT = int(os.environ.get("BASE_PORT", "8000"))

CARRIERS = [
    {"name": "Carrier A", "args": ["carrier_a"], "port": BASE_PORT + 1, "check": "/status"},
    {"name": "Carrier B", "args": ["carrier_b"], "port": BASE_PORT + 2, "check": "/status"},
    {"name": "Carrier C", "args": ["carrier_c"], "port": BASE_PORT + 3, "check": "/status"},
    {"name": "Carrier D", "args": ["carrier_d"], "port": BASE_PORT + 4, "check": "/api/v1/info"},
]


def wait_for_port(port, timeout=10):
    """Wait until a port is responding."""
    for _ in range(timeout * 5):
        try:
            requests.get(f"http://localhost:{port}/", timeout=0.5)
            return True
        except requests.ConnectionError:
            time.sleep(0.2)
    return False


def check_carrier(carrier):
    """Start a carrier, verify it responds, stop it."""
    port = carrier["port"]
    name = carrier["name"]

    print(f"  {name} (:{port})...", end=" ", flush=True)

    proc = subprocess.Popen(
        ["uv", "run", "python", "scripts/start.py"] + carrier["args"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "BASE_PORT": str(BASE_PORT)},
    )

    try:
        if not wait_for_port(port):
            print("FAIL (timeout)")
            return False

        resp = requests.get(f"http://localhost:{port}{carrier['check']}", timeout=2)
        if resp.status_code == 200:
            print("OK")
            return True
        else:
            print(f"FAIL (status {resp.status_code})")
            return False
    except Exception as e:
        print(f"FAIL ({e})")
        return False
    finally:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)


def check_server():
    """Start the candidate server, verify it responds, stop it."""
    port = BASE_PORT
    print(f"  Candidate server (:{port})...", end=" ", flush=True)

    proc = subprocess.Popen(
        ["uv", "run", "python", "scripts/start.py", "server"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "BASE_PORT": str(BASE_PORT)},
    )

    try:
        if not wait_for_port(port):
            print("FAIL (timeout)")
            return False

        resp = requests.get(f"http://localhost:{port}/health", timeout=2)
        if resp.status_code == 200:
            print("OK")
            return True
        else:
            print(f"FAIL (status {resp.status_code})")
            return False
    except Exception as e:
        print(f"FAIL ({e})")
        return False
    finally:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)


def main():
    print("=" * 60)
    print("Sayata Quoting Platform — Setup Verification")
    print("=" * 60)
    print()
    print("Checking each service individually...")
    print()

    results = []

    for carrier in CARRIERS:
        results.append(check_carrier(carrier))

    results.append(check_server())

    print()
    passed = sum(results)
    total = len(results)
    print(f"{passed}/{total} services OK")

    if passed < total:
        print("\nSome services failed. Check your Python version (must be 3.12)")
        print("and that dependencies are installed: uv sync")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Setup verified. All services start and respond correctly.")
    print()
    print("To start all servers at once:")
    print("  uv run python scripts/start.py")
    print()
    print("To start individual services:")
    print("  uv run python scripts/start.py carrier_a")
    print("  uv run python scripts/start.py server carrier_b")
    print("=" * 60)


if __name__ == "__main__":
    main()
