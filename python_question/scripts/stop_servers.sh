#!/usr/bin/env bash
# INTERVIEWER ONLY — not shipped to candidates.
#
# Stop servers started by run_servers.sh.
#
# Usage:
#   bash scripts/stop_servers.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/.server.pid"
BASE_PORT="${BASE_PORT:-8000}"
PORT_END=$((BASE_PORT + 4))

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    kill "$PID" 2>/dev/null && echo "Stopped server process $PID" || true
    rm -f "$PID_FILE"
fi

# Also kill anything on our ports (in case of stale processes)
lsof -ti :${BASE_PORT}-${PORT_END} 2>/dev/null | xargs kill 2>/dev/null || true
echo "Ports ${BASE_PORT}-${PORT_END} cleared."
