#!/usr/bin/env bash
# Test the reference solution by deploying it temporarily and running all tests.
#
# What this does:
#   1. Copies solution files over the exercise files (backs up originals)
#   2. Starts all servers
#   3. Runs test_candidate_results.py
#   4. Restores originals
#
# Usage:
#   bash scripts/test_solution.sh
#   BASE_PORT=9300 bash scripts/test_solution.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

export BASE_PORT="${BASE_PORT:-9300}"
LOGFILE="/tmp/claude/solution_test.log"
mkdir -p /tmp/claude

PIDS=""
BACKED_UP=false

cleanup() {
    echo "Cleaning up..."
    for pid in $PIDS; do kill "$pid" 2>/dev/null || true; done
    wait 2>/dev/null || true

    # Restore originals
    if $BACKED_UP; then
        echo "Restoring original files..."
        mv src/sayata/server.py.bak src/sayata/server.py
        mv src/sayata/models.py.bak src/sayata/models.py
        mv src/sayata/carriers/carrier_a.py.bak src/sayata/carriers/carrier_a.py
        mv src/sayata/carriers/carrier_b.py.bak src/sayata/carriers/carrier_b.py
        rm -f src/sayata/carriers/carrier_c.py
        rm -f src/sayata/carriers/carrier_d.py
        echo "Originals restored."
    fi

    lsof -ti :$((BASE_PORT))-$((BASE_PORT+4)) 2>/dev/null | xargs kill 2>/dev/null || true
}
trap cleanup EXIT

# Kill any leftover processes
lsof -ti :$((BASE_PORT))-$((BASE_PORT+4)) 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1

# Check solution files exist
if [ ! -d solutions/src/sayata ]; then
    echo "ERROR: solutions/ directory not found. Run from python_question/."
    exit 1
fi

echo "=== Testing reference solution ==="
echo "  Port range: ${BASE_PORT}-$((BASE_PORT+4))"
echo ""

# Back up originals and deploy solution
echo "--- Deploying solution files ---"
cp src/sayata/server.py src/sayata/server.py.bak
cp src/sayata/models.py src/sayata/models.py.bak
cp src/sayata/carriers/carrier_a.py src/sayata/carriers/carrier_a.py.bak
cp src/sayata/carriers/carrier_b.py src/sayata/carriers/carrier_b.py.bak
BACKED_UP=true

cp solutions/src/sayata/server.py src/sayata/server.py
cp solutions/src/sayata/models.py src/sayata/models.py
cp solutions/src/sayata/carriers/carrier_a.py src/sayata/carriers/carrier_a.py
cp solutions/src/sayata/carriers/carrier_b.py src/sayata/carriers/carrier_b.py
cp solutions/src/sayata/carriers/carrier_c.py src/sayata/carriers/carrier_c.py
cp solutions/src/sayata/carriers/carrier_d.py src/sayata/carriers/carrier_d.py
echo "  Solution deployed."

# Start servers
echo ""
echo "--- Starting servers ---"
uv run python scripts/start_carrier.py carrier_a --port $((BASE_PORT+1)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_carrier.py carrier_b --port $((BASE_PORT+2)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_carrier.py carrier_c --port $((BASE_PORT+3)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_carrier.py carrier_d --port $((BASE_PORT+4)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_server.py --port $BASE_PORT > /dev/null 2>&1 &
PIDS="$PIDS $!"

echo "  Waiting for servers..."
sleep 5

# Verify servers are up
for port in $BASE_PORT $((BASE_PORT+1)) $((BASE_PORT+2)) $((BASE_PORT+3)) $((BASE_PORT+4)); do
    if ! curl -s --max-time 2 "http://localhost:$port/" > /dev/null 2>&1; then
        echo "  WARNING: port $port not responding"
    fi
done
echo "  Servers started."

# Run candidate results tests
echo ""
echo "=== Candidate results tests ==="
uv run pytest tests/interviewer/test_candidate_results.py -v 2>&1 | tee "$LOGFILE"
TEST_EXIT=${PIPESTATUS[0]}

echo ""
echo "=== Results ==="
if [ $TEST_EXIT -eq 0 ]; then
    echo "  ALL TESTS PASSED"
else
    echo "  SOME TESTS FAILED"
    echo "  Full log: $LOGFILE"
fi
