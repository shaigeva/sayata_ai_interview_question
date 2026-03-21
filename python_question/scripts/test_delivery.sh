#!/usr/bin/env bash
# End-to-end test of the full delivery pipeline.
#
# Simulates the candidate experience:
#   1. Build delivery artifacts (skeleton + exercise.zip)
#   2. Set up skeleton in a temp dir, run tests
#   3. Extract exercise zip, run setup
#   4. Start all servers
#   5. Run verify.py
#   6. Run interviewer test suite
#   7. Check nothing leaked (no simulator source, no interviewer content)
#
# Usage:
#   bash scripts/test_delivery.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$(mktemp -d)"
SERVER_PID=""
PASS=0
FAIL=0

cleanup() {
    echo ""
    echo "Cleaning up..."
    # Kill any servers we started
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
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
        for port in 8000 8001 8002 8003 8004; do
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
echo ""

# --- Pre-run: kill any leftover processes on our ports ---
echo "--- Pre-run: clearing ports 8000-8004 ---"
lsof -ti :8000-8004 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1

# ------------------------------------------------------------------
# Step 1: Build delivery artifacts
# ------------------------------------------------------------------
echo "--- Step 1: Build delivery artifacts ---"
cd "$PROJECT_DIR"
bash scripts/prepare_delivery.sh > /dev/null 2>&1
if [ -f delivery/skeleton.zip ] && [ -f delivery/exercise.zip ]; then
    pass "delivery artifacts created"
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
# Step 4: Start servers
# ------------------------------------------------------------------
echo "--- Step 4: Start servers ---"
uv run python scripts/start.py > /dev/null 2>&1 &
SERVER_PID=$!

if wait_for_ports; then
    pass "servers started (pid $SERVER_PID)"
else
    fail "servers did not start within 15s"
    exit 1
fi

# ------------------------------------------------------------------
# Step 5: Candidate verification script
# ------------------------------------------------------------------
echo "--- Step 5: Candidate verify.py ---"
if uv run python scripts/verify.py > /dev/null 2>&1; then
    pass "verify.py runs"
else
    fail "verify.py runs"
fi

# ------------------------------------------------------------------
# Step 6: Interviewer test suite (baseline only)
# ------------------------------------------------------------------
echo "--- Step 6: Interviewer baseline tests ---"
# Run only baseline tests (these should pass with unmodified skeleton)
cd "$PROJECT_DIR"
if uv run pytest tests/interviewer/test_verification.py -v -k "basic_flow or submission_not_found or low_revenue" 2>&1 | tail -5; then
    pass "baseline verification tests"
else
    fail "baseline verification tests"
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

# Confirm key exercise files are present
for f in README.md src/sayata/server.py src/sayata/carriers/carrier_a.py docs/business-rules.md tickets/ticket-1.md scripts/start.py; do
    if [ ! -f "$TEST_DIR/$f" ]; then
        fail "missing exercise file: $f"
    fi
done
pass "all exercise files present"

# Confirm skeleton files coexist
for f in README_PREP.md src/sayata/server_stub.py tests/test_setup.py docs/about.md; do
    if [ ! -f "$TEST_DIR/$f" ]; then
        fail "missing skeleton file: $f"
    fi
done
pass "skeleton files still present (no overwrites)"

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
