#!/usr/bin/env bash
# INTERVIEWER ONLY — not shipped to candidates.
#
# Start all servers (candidate server + all carrier simulators) in one command.
# Uses the unified start.py which is kept for interviewer convenience.
#
# Usage:
#   bash scripts/run_servers.sh              # default ports (8000-8004)
#   BASE_PORT=9000 bash scripts/run_servers.sh   # custom port range
#
# Output is sent to a log file. Servers run in background.
# Use scripts/stop_servers.sh to stop them.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BASE_PORT="${BASE_PORT:-8000}"
PORT_END=$((BASE_PORT + 4))
LOG_FILE="$PROJECT_DIR/.server.log"

# Kill any existing servers on our ports
lsof -ti :${BASE_PORT}-${PORT_END} 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1

cd "$PROJECT_DIR"
export BASE_PORT
uv run python scripts/start.py > "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PROJECT_DIR/.server.pid"

# Wait for all ports
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
    if $ALL_UP; then
        echo "All servers running (pid $PID). Log: $LOG_FILE"
        echo "Stop with: bash scripts/stop_servers.sh"
        exit 0
    fi
    sleep 1
done

echo "ERROR: Servers did not start within 15 seconds. Check $LOG_FILE"
exit 1
