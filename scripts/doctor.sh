#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "TerraHerb environment doctor"
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

check_cmd docker "Docker"
check_cmd go "Go"
check_cmd flutter "Flutter"
check_cmd psql "PostgreSQL client (psql)"
echo

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    echo "[OK] Docker daemon is reachable"
  else
    echo "[MISSING] Docker daemon is not reachable"
  fi
fi

if command -v go >/dev/null 2>&1; then
  echo "[INFO] Go version: $(go version)"
fi

if command -v flutter >/dev/null 2>&1; then
  echo "[INFO] Flutter version:"
  flutter --version || echo "[WARN] Unable to read flutter version in current environment"
fi

echo
echo "Suggested next steps:"
echo "1. docker compose up -d postgres redis"
echo "2. cd backend && ./scripts/migrate.sh"
echo "3. cd backend && go test ./..."
echo "4. cd ${ROOT_DIR} && flutter analyze && flutter test"
