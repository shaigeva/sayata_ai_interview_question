#!/usr/bin/env bash
# Install exercise dependencies — run this after extracting the exercise zip.
set -euo pipefail

echo "Installing exercise dependencies..."
uv sync
echo ""
echo "Ready! Start the servers with:"
echo "  uv run python scripts/start.py"
