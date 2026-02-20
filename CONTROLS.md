# CONTROLS

## Build controls
- CI enforces backend and Flutter checks.
- Deterministic local bootstrap via documented sequence.

## Runtime controls
- Rate limiting middleware on API routes.
- JWT verification for protected routes.
- Request ID propagation for traceability.

## Data controls
- Versioned migrations.
- FK/CHECK constraints in schema.
- Refresh tokens stored as hashes.
