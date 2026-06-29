#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"

if [[ ! -d "$ROOT/.venv" ]]; then
  echo "Virtualenv not found at $ROOT/.venv"
  echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements/development.txt"
  exit 1
fi

# Avoid macOS soft file-descriptor limit issues during long dev sessions
ulimit -n 4096 2>/dev/null || true

source "$ROOT/.venv/bin/activate"

echo "Starting VoteBridge backend on http://127.0.0.1:8000"
exec python manage.py runserver 127.0.0.1:8000
