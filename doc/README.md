# TerraHerb MVP

India-focused plant intelligence platform MVP with:
- Flutter mobile app (Android + iOS)
- Go backend API
- PostgreSQL normalized schema
- Redis caching and rate limiting
- OTP-dev auth + refresh/logout flow
- Structured logs + Prometheus-style metrics
- Versioned migration runner
- OpenAPI and Postman API docs

## Current Stage
Late MVP / pre-beta.

Implemented:
- Seasonal plant browsing UI with backend integration + fallback data.
- Production-style backend layering (`cmd`, `internal`, `migrations`, `scripts`).
- Core plant APIs, auth APIs, migrations, CI workflows, observability.

Pending for final production confidence:
- Full backend runtime validation on a machine with Go + Docker daemon available.

## Repository Structure
- `lib/`: Flutter application.
- `backend/`: Go API server, migrations, ingestion, docs.
- `backend/internal/`: domain logic (`config`, `http`, `repository`, `service`, `observability`, etc.).
- `backend/migrations/`: SQL schema/data migrations.
- `.github/workflows/`: backend and Flutter CI.

## Prerequisites
- Flutter SDK
- Go 1.22+
- Docker + Docker Compose
- PostgreSQL client (`psql`) for fallback migration path

Optional helper:
- `./scripts/doctor.sh` checks environment readiness.

## Environment Variables
Example file: `backend/.env.example`

Key values:
- `HTTP_ADDR` (default `:8080`)
- `DATABASE_URL` (default `postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable`)
- `REDIS_ADDR` (default `localhost:6379`)
- `REDIS_PASSWORD` (optional)
- `JWT_SIGNING_KEY` (required for secure deployment)
- `AUTH_DEV_OTP` (default `123456`, for dev login only)
- `ACCESS_TOKEN_MINS` (default `15`)
- `REFRESH_TOKEN_HRS` (default `168`)
- `RATE_LIMIT_PER_MIN` (default `120`)

## Local Setup (End-to-End)
1. `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb`
2. `docker compose up -d postgres redis`
3. `cd backend && cp .env.example .env`
4. `cd backend && ./scripts/migrate.sh up`
5. `cd backend && go run ./cmd/api`
6. In another shell: `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb && flutter pub get`
7. Run mobile app: `flutter run`

## Mobile Platform Details
- Android emulator backend default: `http://10.0.2.2:8080`
- iOS simulator backend default: `http://localhost:8080`
- Physical devices: pass explicit host:
  - `flutter run --dart-define=API_BASE_URL=http://<your-lan-ip>:8080`

Platform network setup included:
- Android cleartext local HTTP enabled.
- iOS ATS local exceptions for `localhost` and `127.0.0.1`.

## Backend APIs
### Health and Observability
- `GET /health`
- `GET /metrics` (Prometheus text format)

### Auth
- `POST /api/v1/auth/login` (dev OTP mode)
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

### Plant Intelligence
- `GET /api/v1/plants`
- `GET /api/v1/plants/by-season`
- `GET /api/v1/plants/by-climate-zone`
- `GET /api/v1/plants/{id}`

## Auth Flow (MVP)
1. Client calls `POST /api/v1/auth/login` with `identifier`, `otp`, and optional `device_id`.
2. API issues access token + refresh token.
3. Refresh token hash is stored in DB (`refresh_tokens` table).
4. Client calls `POST /api/v1/auth/refresh` to rotate tokens.
5. Client calls `POST /api/v1/auth/logout` to revoke refresh token.

## Database and Migrations
Primary tool:
- `go run ./cmd/migrate --cmd up`
- `go run ./cmd/migrate --cmd down --steps 1`
- `go run ./cmd/migrate --cmd version`

Wrapper script:
- `./scripts/migrate.sh up`

Auth tables introduced:
- `users`
- `refresh_tokens` (token hash, expiry, revoke state, device id)

## API Documentation
- OpenAPI: `backend/docs/openapi.yaml`
- Postman: `backend/docs/postman_collection.json`
- Docs guide: `backend/docs/README.md`

## CI
- Backend CI: `.github/workflows/backend-ci.yml`
  - `go mod tidy`
  - `go test ./...`
  - `go build ./cmd/api`
- Flutter CI: `.github/workflows/flutter-ci.yml`
  - `flutter pub get`
  - `flutter analyze`
  - `flutter test`

## Validation Commands
- Flutter:
  - `flutter analyze`
  - `flutter test`
- Backend:
  - `cd backend && go test ./...`
  - `cd backend && go build ./...`

## Open Source Governance
- License: `LICENSE`
- Contributing: `CONTRIBUTING.md`
- Code of Conduct: `CODE_OF_CONDUCT.md`
- Security Policy: `SECURITY.md`
- Issue templates and PR template under `.github/`

## Troubleshooting
- `go: command not found`
  - Install Go 1.22+ and ensure it is on PATH.
- `Cannot connect to Docker daemon`
  - Start Docker Desktop/daemon, then rerun compose.
- Flutter app cannot reach backend on Android emulator
  - Verify backend is running and uses `10.0.2.2` mapping.
- Auth login failing
  - Ensure request uses `otp` matching `AUTH_DEV_OTP`.
- Migration failures
  - Check DB URL, ensure PostgreSQL is running, run `cmd/migrate --cmd version`.

## Notes
- Dev auth is OTP-mock mode for MVP speed; replace with production auth provider before launch.
- This repository path is lowercase in current environment:
  - `/Users/fallofpheonix/AndroidStudioProjects/terraherb`
