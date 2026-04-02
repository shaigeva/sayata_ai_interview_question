#!/usr/bin/env bash
# End-to-end test of the full delivery pipeline.
#
# Simulates the candidate experience:
#   1. Build delivery artifacts (skeleton.zip + exercise.zip + docs.zip)
#   2. Set up skeleton in a temp dir, run tests
#   3. Extract exercise zip, run setup
#   4. Start all servers
#   5. Run verify_setup.py
#   6. Run interviewer test suite
#   7. Check nothing leaked (no simulator source, no interviewer content)
#   8. Verify docs are separate (not in exercise)
#
# Uses BASE_PORT (default 9100) to avoid colliding with dev sessions.
#
# Usage:
#   bash scripts/test_delivery.sh
#   BASE_PORT=9200 bash scripts/test_delivery.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$(mktemp -d)"
PIDS=""
PASS=0
FAIL=0

export BASE_PORT="${BASE_PORT:-9100}"
PORT_END=$((BASE_PORT + 4))

cleanup() {
    echo ""
    echo "Cleaning up..."
    for pid in $PIDS; do
        kill "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
    done
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

wait_for_ports() {
    local max_wait=15
    local waited=0
    while [ $waited -lt $max_wait ]; do
        local all_up=true
        for offset in 0 1 2 3 4; do
            local port=$((BASE_PORT + offset))
            if ! curl -s --max-time 1 "http://localhost:$port/" > /dev/null 2>&1; then
                all_up=false
                break
            fi
        done
        if $all_up; then
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done
    return 1
}

echo "=== End-to-end delivery test ==="
echo "  Project: $PROJECT_DIR"
echo "  Test dir: $TEST_DIR"
echo "  Ports: ${BASE_PORT}-${PORT_END}"
echo ""

# --- Pre-run: kill any leftover processes on our ports ---
echo "--- Pre-run: clearing ports ${BASE_PORT}-${PORT_END} ---"
lsof -ti :${BASE_PORT}-${PORT_END} 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1

# ------------------------------------------------------------------
# Step 1: Build delivery artifacts
# ------------------------------------------------------------------
echo "--- Step 1: Build delivery artifacts ---"
cd "$PROJECT_DIR"
bash scripts/prepare_delivery.sh > /dev/null 2>&1
if [ -f delivery/skeleton.zip ] && [ -f delivery/skeleton-docs.zip ] && [ -f delivery/exercise.zip ] && [ -f delivery/docs.zip ]; then
    pass "delivery artifacts created (4 zips)"
else
    fail "delivery artifacts missing"
    exit 1
fi

# ------------------------------------------------------------------
# Step 2: Skeleton setup
# ------------------------------------------------------------------
echo "--- Step 2: Skeleton setup ---"
unzip -o delivery/skeleton.zip -d "$TEST_DIR" > /dev/null
cd "$TEST_DIR"

uv sync > /dev/null 2>&1
if [ $? -eq 0 ]; then pass "uv sync"; else fail "uv sync"; fi

uv run pytest -v 2>&1 | tail -5
if uv run pytest -q 2>/dev/null; then
    pass "skeleton tests"
else
    fail "skeleton tests"
fi

# ------------------------------------------------------------------
# Step 3: Extract exercise zip
# ------------------------------------------------------------------
echo "--- Step 3: Extract exercise zip ---"
unzip -o "$PROJECT_DIR/delivery/exercise.zip" -d "$TEST_DIR" > /dev/null

bash setup.sh > /dev/null 2>&1
if [ $? -eq 0 ]; then pass "setup.sh"; else fail "setup.sh"; fi

# Verify simulator wheel is installed
if uv run python -c "import sayata_simulators" 2>/dev/null; then
    pass "sayata_simulators importable"
else
    fail "sayata_simulators importable"
fi

# ------------------------------------------------------------------
# Step 4: Start servers (using candidate scripts)
# ------------------------------------------------------------------
echo "--- Step 4: Start servers ---"
PIDS=""
uv run python scripts/start_carrier.py carrier_a --port $((BASE_PORT + 1)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_carrier.py carrier_b --port $((BASE_PORT + 2)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_carrier.py carrier_c --port $((BASE_PORT + 3)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_carrier.py carrier_d --port $((BASE_PORT + 4)) > /dev/null 2>&1 &
PIDS="$PIDS $!"
uv run python scripts/start_server.py --port $BASE_PORT > /dev/null 2>&1 &
SERVER_PID=$!
PIDS="$PIDS $SERVER_PID"

if wait_for_ports; then
    pass "servers started (ports ${BASE_PORT}-${PORT_END})"
else
    fail "servers did not start within 15s"
    exit 1
fi

# ------------------------------------------------------------------
# Step 5: Candidate verification script
# ------------------------------------------------------------------
echo "--- Step 5: Candidate verify_setup.py ---"
if uv run python scripts/verify_setup.py > /dev/null 2>&1; then
    pass "verify_setup.py runs"
else
    fail "verify_setup.py runs"
fi

# ------------------------------------------------------------------
# Step 6: Interviewer test suite (baseline only)
# ------------------------------------------------------------------
echo "--- Step 6: Interviewer baseline tests ---"
cd "$PROJECT_DIR"
if uv run pytest tests/interviewer/test_verification.py -v -k "basic_flow or submission_not_found or low_revenue" 2>&1 | tail -5; then
    pass "baseline verification tests"
else
    fail "baseline verification tests"
fi

echo "--- Step 6b: Exercise setup validation ---"
if uv run pytest tests/interviewer/test_exercise_setup.py -v 2>&1 | tail -5; then
    pass "exercise setup validated (bugs present, traps working)"
else
    fail "exercise setup validation"
fi
cd "$TEST_DIR"

# ------------------------------------------------------------------
# Step 7: Check for leaks
# ------------------------------------------------------------------
echo "--- Step 7: Check for leaks ---"

# No simulator .py source
if find "$TEST_DIR" -name "*.py" -path "*/simulators/*" 2>/dev/null | grep -q .; then
    fail "simulator .py source found"
else
    pass "no simulator source leaked"
fi

# No interviewer tickets
if find "$TEST_DIR" -path "*/interviewer/*" 2>/dev/null | grep -q .; then
    fail "interviewer content found"
else
    pass "no interviewer content leaked"
fi

# No test_verification.py
if find "$TEST_DIR" -name "test_verification*" 2>/dev/null | grep -q .; then
    fail "test_verification.py found"
else
    pass "no verification tests leaked"
fi

# Docs NOT in exercise directory (delivered separately)
if find "$TEST_DIR/docs" -name "architecture.md" 2>/dev/null | grep -q .; then
    fail "docs found in exercise (should be separate)"
else
    pass "docs not in exercise directory"
fi

# Confirm key exercise files are present
for f in README.md src/sayata/server.py src/sayata/carriers/carrier_a.py tickets/ticket-1.md scripts/start_server.py scripts/start_carrier.py; do
    if [ ! -f "$TEST_DIR/$f" ]; then
        fail "missing exercise file: $f"
    fi
done
pass "all exercise files present"

# Confirm skeleton files coexist
for f in README_PREP.md src/sayata/server_stub.py tests/test_setup.py; do
    if [ ! -f "$TEST_DIR/$f" ]; then
        fail "missing skeleton file: $f"
    fi
done
pass "skeleton files still present (no overwrites)"

# Confirm skeleton-docs.zip has about.md
SKEL_DOCS_DIR="$(mktemp -d)"
unzip -o "$PROJECT_DIR/delivery/skeleton-docs.zip" -d "$SKEL_DOCS_DIR" > /dev/null
if [ -f "$SKEL_DOCS_DIR/docs/about.md" ]; then
    pass "skeleton-docs.zip contains docs/about.md"
else
    fail "skeleton-docs.zip missing docs/about.md"
fi
rm -rf "$SKEL_DOCS_DIR"

# Confirm docs.zip has the right content
DOCS_DIR="$(mktemp -d)"
unzip -o "$PROJECT_DIR/delivery/docs.zip" -d "$DOCS_DIR" > /dev/null
for doc in business-rules.md glossary.md frontend-guidelines.md; do
    if [ ! -f "$DOCS_DIR/docs/$doc" ]; then
        fail "missing doc in docs.zip: $doc"
    fi
done
pass "docs.zip contains all reference docs"
rm -rf "$DOCS_DIR"

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
