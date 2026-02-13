#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${BACKEND_DIR}"

DB_URL="${DATABASE_URL:-postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable}"
CMD="${1:-up}"

echo "Running migrations cmd=${CMD} db=${DB_URL}"
if command -v go >/dev/null 2>&1; then
  DATABASE_URL="$DB_URL" go run ./cmd/migrate --cmd "$CMD"
  exit 0
fi

echo "Go runtime unavailable; using fallback psql migration mode"
if [ "$CMD" != "up" ]; then
  echo "Fallback mode supports only 'up'"
  exit 1
fi

for file in ./migrations/*.sql; do
  case "$file" in
    *.up.sql|*.down.sql)
      continue
      ;;
  esac
  echo "Applying $file"
  psql "$DB_URL" -f "$file"
done
