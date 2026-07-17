#!/usr/bin/env bash
#
# run.sh — start the Utility Invoice Extraction app (FastAPI backend + React UI)
#
# Usage: ./run.sh
# Stop:  Ctrl+C (both servers are shut down together)

set -euo pipefail

# Resolve the directory this script lives in, so it works from anywhere.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$ROOT/invoice-extractor-api"
UI_DIR="$ROOT/invoice-extractor-ui"

API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-5173}"

BACK_PID=""
FRONT_PID=""

# Free a TCP port if something is already listening on it (e.g. a previous run
# that didn't shut down cleanly), so we don't hit "Address already in use".
free_port() {
  local port="$1" pids
  pids="$(lsof -ti "tcp:$port" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "Port $port is in use (pid: $pids) — freeing it..."
    kill $pids 2>/dev/null || true
    sleep 1
    pids="$(lsof -ti "tcp:$port" 2>/dev/null || true)"
    [[ -n "$pids" ]] && kill -9 $pids 2>/dev/null || true
  fi
}

cleanup() {
  echo ""
  echo "Shutting down..."
  [[ -n "$BACK_PID" ]]  && kill "$BACK_PID"  2>/dev/null || true
  [[ -n "$FRONT_PID" ]] && kill "$FRONT_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "Stopped."
}
trap cleanup INT TERM EXIT

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
# Pick a compatible Python. The pinned deps (pydantic-core) have no wheels for
# Python 3.14, so prefer 3.13/3.12/3.11/3.10 and fall back to python3.
pick_python() {
  for v in python3.13 python3.12 python3.11 python3.10 python3; do
    command -v "$v" >/dev/null 2>&1 && { echo "$v"; return; }
  done
}

# Rebuild the venv if it's missing OR broken (e.g. copied from another machine,
# where the interpreter shebangs point at a path that no longer exists).
if [[ ! -x "$API_DIR/venv/bin/python" ]] || ! "$API_DIR/venv/bin/python" -c '' 2>/dev/null; then
  PY="$(pick_python)"
  echo "Creating Python virtualenv with $PY ..."
  rm -rf "$API_DIR/venv"
  "$PY" -m venv "$API_DIR/venv"
  "$API_DIR/venv/bin/python" -m pip install -q --upgrade pip
  "$API_DIR/venv/bin/pip" install -q -r "$API_DIR/requirements.txt"
fi

if [[ ! -f "$API_DIR/.env" ]]; then
  echo "WARNING: $API_DIR/.env not found. The backend needs OPENAI_API_KEY set."
fi

free_port "$API_PORT"
echo "Starting backend on http://localhost:$API_PORT ..."
(
  cd "$API_DIR"
  exec ./venv/bin/uvicorn main:app --reload --port "$API_PORT"
) &
BACK_PID=$!

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
if [[ ! -d "$UI_DIR/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  ( cd "$UI_DIR" && npm install )
fi

free_port "$UI_PORT"
echo "Starting frontend on http://localhost:$UI_PORT ..."
(
  cd "$UI_DIR"
  exec npm run dev -- --port "$UI_PORT"
) &
FRONT_PID=$!

echo ""
echo "======================================================"
echo "  Backend : http://localhost:$API_PORT  (docs: /docs)"
echo "  Frontend: http://localhost:$UI_PORT"
echo "  Press Ctrl+C to stop both."
echo "======================================================"

# Wait for either process to exit; cleanup trap handles the rest.
# (Portable to bash 3.2 on macOS, which lacks `wait -n`.)
while kill -0 "$BACK_PID" 2>/dev/null && kill -0 "$FRONT_PID" 2>/dev/null; do
  sleep 1
done
