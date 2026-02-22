# VALIDATION

## Backend
- `cd backend && go mod tidy`
- `cd backend && go test ./...`
- `cd backend && go build ./cmd/api`

## Flutter
- `flutter pub get`
- `flutter analyze`
- `flutter test`

## Runtime smoke
- Start services and run health/metrics checks.
- Exercise auth and plant endpoints from Postman collection.
