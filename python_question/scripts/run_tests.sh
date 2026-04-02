#!/usr/bin/env bash
# INTERVIEWER ONLY — not shipped to candidates.
#
# Start all servers, run the interviewer test suites, then stop servers.
# Runs both exercise setup validation (bugs are present) and baseline tests.
#
# Usage:
#   bash scripts/run_tests.sh                    # setup + baseline tests
#   bash scripts/run_tests.sh --all              # ALL interviewer tests (requires solved code)
#   bash scripts/run_tests.sh -k "ticket1"       # specific test filter
#   BASE_PORT=9000 bash scripts/run_tests.sh     # custom port range

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

export BASE_PORT="${BASE_PORT:-8000}"
PORT_END=$((BASE_PORT + 4))

# Parse args
PYTEST_ARGS=""
RUN_ALL=false
for arg in "$@"; do
    if [ "$arg" = "--all" ]; then
        RUN_ALL=true
    else
        PYTEST_ARGS="$PYTEST_ARGS $arg"
    fi
done

# Kill any existing servers on our ports
lsof -ti :${BASE_PORT}-${PORT_END} 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1

# Clear pycache to use latest simulator source
find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Start servers
cd "$PROJECT_DIR"
uv run python scripts/start.py > /dev/null 2>&1 &
SERVER_PID=$!

cleanup() {
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    lsof -ti :${BASE_PORT}-${PORT_END} 2>/dev/null | xargs kill 2>/dev/null || true
}
trap cleanup EXIT

# Wait for ports
echo "Starting servers on ports ${BASE_PORT}-${PORT_END}..."
for i in $(seq 1 15); do
    ALL_UP=true
    for offset in 0 1 2 3 4; do
        port=$((BASE_PORT + offset))
        if ! curl -s --max-time 1 "http://localhost:$port/" > /dev/null 2>&1; then
            ALL_UP=false
            break
        fi
    done
    if $ALL_UP; then break; fi
    sleep 1
done

if ! $ALL_UP; then
    echo "ERROR: Servers did not start within 15 seconds"
    exit 1
fi
echo "Servers ready."
echo ""

# Run tests
if [ -n "$PYTEST_ARGS" ]; then
    echo "=== Running filtered tests ==="
    uv run pytest tests/interviewer/ -v $PYTEST_ARGS
elif $RUN_ALL; then
    echo "=== Running ALL interviewer tests ==="
    uv run pytest tests/interviewer/ -v
else
    echo "=== Exercise setup validation ==="
    uv run pytest tests/interviewer/test_exercise_setup.py -v
    echo ""
    echo "=== Baseline verification ==="
    uv run pytest tests/interviewer/test_verification.py -v -k "basic_flow or submission_not_found or low_revenue"
fi
