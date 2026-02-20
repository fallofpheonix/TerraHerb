# SETUP_GUIDE

## Quick setup
1. `docker compose up -d postgres redis`
2. `cd backend && cp .env.example .env && ./scripts/migrate.sh up`
3. `cd backend && go run ./cmd/api`
4. `flutter pub get && flutter run`

## Android/iOS notes
- Android emulator uses host bridge `10.0.2.2`.
- iOS simulator uses `localhost`.
