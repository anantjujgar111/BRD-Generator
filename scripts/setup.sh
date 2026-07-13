#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up BRD Generator development environment"

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "python3-venv is required. On Debian/Ubuntu: sudo apt install python3-venv"
  exit 1
fi

BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating Python virtual environment"
  python3 -m venv "$VENV_DIR"
fi

echo "==> Installing backend dependencies"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

echo "==> Installing Streamlit frontend dependencies"
pip install -r "$FRONTEND_DIR/requirements.txt"

mkdir -p "$BACKEND_DIR/data/uploads" "$BACKEND_DIR/data/outputs"

echo "==> Setup complete"
echo "Run ./scripts/dev.sh to start backend and Streamlit frontend"
