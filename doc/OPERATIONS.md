# OPERATIONS

## Local runtime
- Backend on `:8080`
- PostgreSQL on `:5432`
- Redis on `:6379`

## Health and telemetry
- `GET /health`
- `GET /metrics`

## Incident triage order
1. Health endpoint.
2. DB connectivity and migration version.
3. Redis availability.
4. Auth and rate-limit logs.
