# TerraHerb Backend

## Local runbook
From project root (`/Users/fallofpheonix/AndroidStudioProjects/TerraHerb`):

1. Start infra:
   - `docker compose up -d postgres redis`
2. Apply migrations:
   - `cd backend && ./scripts/migrate.sh`
3. Start API:
   - `cd backend && go run ./cmd/api`
4. Optional env bootstrap:
   - `cd backend && cp .env.example .env`

Default local database URL:
- `postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable`

## API endpoints
- `GET /health`
- `GET /api/v1/plants`
- `GET /api/v1/plants/by-season?season=monsoon&region_code=IN-KA&month=7`
- `GET /api/v1/plants/by-climate-zone?climate_zone=tropical_wet`
- `GET /api/v1/plants/{id}`

## Validation behavior
- Invalid query params return `400` with `VALIDATION_ERROR`.
- `/api/v1/plants/by-season` requires `season`.
- `/api/v1/plants/by-climate-zone` requires `climate_zone`.
- Missing records return `404` with `NOT_FOUND`.
- Invalid bearer tokens return `401` with `UNAUTHORIZED`.
- Rate-limited requests return `429` and `Retry-After: 60`.

## Ingestion
CSV columns:
- `scientific_name,common_name,plant_type,lifecycle,state_code,season_code,start_month,end_month`

Run:
- `cd backend && go run ./cmd/ingest --file ./scripts/sample_plants.csv`

Output:
- Logs rejected rows with reason.
- Logs summary counts as `accepted=<n> rejected=<n>`.
