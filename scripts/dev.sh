#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [ ! -d "$BACKEND_DIR/.venv" ]; then
  echo "Virtual environment not found. Run ./scripts/setup.sh first."
  exit 1
fi

source "$BACKEND_DIR/.venv/bin/activate"
mkdir -p "$BACKEND_DIR/data/uploads" "$BACKEND_DIR/data/outputs"

cleanup() {
  if [ -n "${BACKEND_PID:-}" ]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [ -n "${FRONTEND_PID:-}" ]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "==> Starting backend on http://127.0.0.1:8000"
cd "$BACKEND_DIR"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "==> Starting Streamlit frontend on http://127.0.0.1:8501"
cd "$FRONTEND_DIR"
STREAMLIT_SERVER_HEADLESS=true streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false &
FRONTEND_PID=$!

wait
