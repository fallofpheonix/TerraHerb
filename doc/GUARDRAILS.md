# GUARDRAILS

## Do not break
- API response envelope shape.
- Migration ordering and reversibility assumptions.
- Mobile fallback behavior when backend is unavailable.

## Mandatory update coupling
- API change => update OpenAPI + Postman + tests.
- Security control change => update `CONTROLS.md` and `CRITICAL_WARNINGS.md`.
- Runtime change => update `OPERATIONS.md` and `SETUP_GUIDE.md`.
