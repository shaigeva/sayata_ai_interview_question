#!/usr/bin/env bash
# Install exercise dependencies — run this after extracting the exercise zip.
set -euo pipefail

echo "Installing exercise dependencies..."
uv sync
echo ""
echo "Ready! Start the servers (each in its own terminal):"
echo "  uv run python scripts/start_server.py"
echo "  uv run python scripts/start_carrier.py carrier_a"
echo "  uv run python scripts/start_carrier.py carrier_b"
echo "  uv run python scripts/start_carrier.py carrier_c"
echo "  uv run python scripts/start_carrier.py carrier_d"
