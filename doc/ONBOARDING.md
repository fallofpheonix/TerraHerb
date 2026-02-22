# ONBOARDING

## 30-minute bootstrap
1. Install Flutter, Go, Docker.
2. `docker compose up -d postgres redis`
3. `cd backend && cp .env.example .env && ./scripts/migrate.sh up`
4. `cd backend && go run ./cmd/api`
5. `flutter pub get && flutter run`

## First tasks for new contributors
- Run full validation matrix in `VALIDATION.md`.
- Read `ARCHITECTURE.md` and `CONTROLS.md`.
- Pick top item from `TASKS.md`.
