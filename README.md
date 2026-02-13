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

## Mobile API base URL
- Android emulator default is auto-mapped to `http://10.0.2.2:8080`.
- iOS simulator default is `http://localhost:8080`.
- Physical devices should use LAN host via:
  - `flutter run --dart-define=API_BASE_URL=http://<your-lan-ip>:8080`

## Validation commands
- Backend: `cd backend && go test ./...`
- Flutter: `flutter analyze && flutter test`
- Environment check: `./scripts/doctor.sh`

## CI
- Backend workflow: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/.github/workflows/backend-ci.yml`
- Flutter workflow: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/.github/workflows/flutter-ci.yml`
- Runs Flutter analyze/test and backend tidy/test/build on push/PR.

## API docs
- OpenAPI spec: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/docs/openapi.yaml`
- Postman collection: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/backend/docs/postman_collection.json`

## Open source
- License: MIT (`/Users/fallofpheonix/AndroidStudioProjects/terraherb/LICENSE`)
- Contributing guide: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/CONTRIBUTING.md`
- Code of conduct: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/CODE_OF_CONDUCT.md`
- Security policy: `/Users/fallofpheonix/AndroidStudioProjects/terraherb/SECURITY.md`
