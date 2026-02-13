#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${BACKEND_DIR}"

DB_URL="${DATABASE_URL:-postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable}"
CMD="${1:-up}"

echo "Running migrations cmd=${CMD} db=${DB_URL}"
DATABASE_URL="$DB_URL" go run ./cmd/migrate --cmd "$CMD"
