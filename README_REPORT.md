# TerraHerb MVP Implementation Report

## Project
- Name: TerraHerb MVP (India Plant Intelligence Platform)
- Repository path in this environment: `/Users/fallofpheonix/AndroidStudioProjects/terraherb`
- Intended renamed root in docs/runbooks: `/Users/fallofpheonix/AndroidStudioProjects/TerraHerb`

## Epic Goal
Deliver a production-ready MVP with seasonal/location-aware plant discovery, normalized data backbone, and deployable backend/mobile integration.

## Executive Summary
- Flutter seasonal UI is implemented and integrated with backend seasonal API contract, with safe local fallback behavior.
- Go backend scaffold is implemented with layered structure (`cmd`, `internal`, `migrations`, `scripts`), health endpoint, plant endpoints, Redis cache wrapper, JWT helper, and rate-limit middleware.
- PostgreSQL normalized schema, indexes, reference seeds, sample data, and ingestion CLI are implemented.
- Key hardening pass completed:
  - API query validation now returns deterministic `400` validation errors for invalid input.
  - Bearer parsing and client-IP extraction for rate limiting improved.
  - Ingestion validation and species dedup/upsert behavior strengthened.
  - Path hygiene and local defaults updated for TerraHerb naming in operational docs and runtime defaults.
  - CI pipeline added for Flutter + backend checks on push/PR.
  - Local `doctor` script added for prerequisite/debug diagnostics.

## Story-by-Story Status

### Story 1: Backend Foundation
Status: Complete
- Backend module/layout present under `backend/`
- Environment config loading implemented
- HTTP bootstrap and graceful shutdown implemented
- `/health` endpoint implemented

### Story 2: Database Schema and Reference Data
Status: Complete
- `001_init.sql`, `002_indexes.sql`, `003_seed_reference.sql`, `004_seed_sample_plants.sql` present
- Added hardening migration: `005_species_author_default.sql`
- FK/CHECK constraints and indexes are defined in migrations

### Story 3: Plant Query APIs
Status: Complete (with validation hardening)
- Endpoints implemented:
  - `GET /api/v1/plants`
  - `GET /api/v1/plants/by-season`
  - `GET /api/v1/plants/by-climate-zone`
  - `GET /api/v1/plants/{id}`
- Standard error envelope implemented
- Input validation now returns `400` for invalid numeric/enums

### Story 4: Caching and Protection Middleware
Status: Complete (scaffold + functional behavior)
- Redis client abstraction implemented
- List/profile caching wired in service layer
- JWT generate/parse helper implemented
- Rate limit middleware implemented with `429` + `Retry-After`

### Story 5: CSV Ingestion Pipeline (MVP)
Status: Complete (MVP)
- `cmd/ingest` implemented
- CSV parser and validation implemented
- Transactional upsert flow across taxonomy/plant/seasonality/common names implemented
- Accepted/rejected summary logging implemented

### Story 6: Local Dev Infra and Operations
Status: Complete
- `docker-compose.yml` (Postgres + Redis) present
- Migration script present (`backend/scripts/migrate.sh`)
- Dockerfile and Makefile present
- Backend runbook updated

### Story 7: Flutter Seasonal UI and Backend Integration
Status: Complete
- Seasonal selector + animated background implemented
- API model/service implemented
- Seasonal API call on season selection implemented
- Fallback local seasonal data implemented
- `http` dependency added to `pubspec.yaml`

### Story 8: Validation and Stabilization
Status: Partially complete (environment-limited)
- Completed:
  - `flutter pub get`
  - `flutter analyze` (pass)
  - `flutter test` (pass)
- Blocked in current environment:
  - `go` command unavailable on PATH
  - Docker daemon unreachable

### Story 9: Rename and Path Hygiene
Status: Complete for operational docs/config
- Updated runbooks and backend defaults to TerraHerb naming and `terraherb` DB defaults
- Updated compose service/container naming to TerraHerb conventions
- Note: Generated platform metadata may still contain old Flutter project identifiers; these do not block backend/API operation

## Files Added/Updated in Final Hardening Pass
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/.github/workflows/ci.yml`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/internal/http/router.go`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/internal/http/middleware.go`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/internal/http/router_test.go`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/internal/http/middleware_test.go`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/cmd/ingest/main.go`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/migrations/005_species_author_default.sql`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/migrations/004_seed_sample_plants.sql`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/.env.example`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/internal/config/config.go`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/scripts/migrate.sh`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/docker-compose.yml`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/scripts/doctor.sh`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/README.md`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/README.md`
- `/Users/fallofpheonix/AndroidStudioProjects/terraherb/pubspec.yaml`

## Validation Evidence
- Flutter analyze: passed with no issues
- Flutter tests: passed (`test/widget_test.dart`)

## Remaining Blockers
- Docker daemon access required to run local Postgres/Redis stack
- Go toolchain (1.22+) required to run backend build/tests/runtime checks

## Next Commands to Reach Full Epic DoD
1. `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb`
2. `docker compose up -d postgres redis`
3. `cd backend && go mod tidy`
4. `cd backend && ./scripts/migrate.sh`
5. `cd backend && go test ./...`
6. `cd backend && go run ./cmd/api`
7. `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb && flutter run`
8. Verify app seasonal requests against `/api/v1/plants/by-season`

## Definition of Done Assessment
- Local infra/migrations: implemented, pending Docker availability to execute
- Backend endpoints + cache/rate-limit scaffolding: implemented
- Flutter seasonal API + fallback: implemented and validated (analyze/test)
- Ingestion CLI + sample CSV: implemented
- Core checks in renamed path: Flutter checks pass; backend runtime checks pending environment readiness
