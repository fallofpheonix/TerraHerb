#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "TerraHerb Python/ML environment doctor"
echo "Repository: ${ROOT_DIR}"
echo

check_cmd() {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] ${label}: $(command -v "$cmd")"
  else
    echo "[MISSING] ${label}: command '$cmd' not found"
  fi
}

check_cmd python3 "Python"
check_cmd pip "pip"
check_cmd node "Node.js"
check_cmd npm "npm"

echo
if command -v python3 >/dev/null 2>&1; then
  echo "[INFO] Python version: $(python3 --version)"
fi
if command -v node >/dev/null 2>&1; then
  echo "[INFO] Node version: $(node --version)"
fi

echo
echo "Suggested next steps:"
echo "1. python3 -m venv venv && source venv/bin/activate"
echo "2. pip install -r requirements.txt && pip install -e ."
echo "3. python -m pytest tests -v"
echo "4. uvicorn terraherb.api.main:app --reload"
echo "5. cd frontend && npm install && npm run dev"
