#!/usr/bin/env bash
set -euo pipefail

DB_URL="${DATABASE_URL:-postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable}"

for file in ./migrations/*.sql; do
  echo "Applying $file"
  psql "$DB_URL" -f "$file"
done
