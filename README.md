# TerraHerb MVP

India-focused plant intelligence MVP with:
- Flutter seasonal discovery UI
- Go API backend
- PostgreSQL normalized schema
- Redis cache and rate-limit scaffolding
- JWT auth + refresh flow
- Structured API logs and request metrics
- CSV ingestion CLI

## Project layout
- `/Users/fallofpheonix/AndroidStudioProjects/TerraHerb/lib` Flutter app
- `/Users/fallofpheonix/AndroidStudioProjects/TerraHerb/backend` Go backend
- `/Users/fallofpheonix/AndroidStudioProjects/TerraHerb/backend/migrations` SQL migrations/seeds
- `/Users/fallofpheonix/AndroidStudioProjects/TerraHerb/docker-compose.yml` Local Postgres + Redis

## Local quick start
1. `cd /Users/fallofpheonix/AndroidStudioProjects/TerraHerb`
2. `docker compose up -d postgres redis`
3. `cd backend && ./scripts/migrate.sh`
4. `cd backend && go run ./cmd/api`
5. `cd /Users/fallofpheonix/AndroidStudioProjects/TerraHerb && flutter pub get`
6. `cd /Users/fallofpheonix/AndroidStudioProjects/TerraHerb && flutter run`

## Validation commands
- Backend: `cd backend && go test ./...`
- Flutter: `flutter analyze && flutter test`
- Environment check: `./scripts/doctor.sh`

## CI
- GitHub Actions workflow: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/.github/workflows/ci.yml`
- Runs Flutter analyze/test and backend `go test` on push/PR.

## API docs
- OpenAPI spec: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/docs/api/openapi.yaml`
- Postman collection: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/docs/api/TerraHerb.postman_collection.json`

## Open source
- License: MIT (`/Users/fallofpheonix/AndroidStudioProjects/terraherb/LICENSE`)
- Contributing guide: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/CONTRIBUTING.md`
- Code of conduct: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/CODE_OF_CONDUCT.md`
- Security policy: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/SECURITY.md`
