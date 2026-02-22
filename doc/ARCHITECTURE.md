# ARCHITECTURE

## Topology
- Flutter client
- Go API service
- PostgreSQL primary store
- Redis for rate limit + cache

## Backend layers
- `cmd/` entrypoints
- `internal/http` transport
- `internal/service` business logic
- `internal/repository` persistence
- `internal/models` contracts
- `internal/observability` telemetry

## Data flow
1. Request enters `http` router.
2. Middleware enforces request ID, logging, metrics, rate limit, auth.
3. Service validates rules and coordinates repository/cache.
4. Repository executes SQL with context deadlines.
5. Response emitted in deterministic JSON.
