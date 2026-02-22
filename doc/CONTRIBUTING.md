# CONTRIBUTING

## Branching
- Use short-lived feature branches.
- Keep PRs scoped and atomic.

## Required checks
- `flutter analyze`
- `flutter test`
- `cd backend && go test ./...`
- `cd backend && go build ./cmd/api`

## Change discipline
- Migration changes must include rollback consideration.
- API contract changes must update OpenAPI + Postman.
- Security-impacting changes must update `CRITICAL_WARNINGS.md` and `RISK_REGISTER.md`.
