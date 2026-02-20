# CRITICAL_WARNINGS

## High risk defaults
- `AUTH_DEV_OTP` is development-only and must not ship to production.
- Local HTTP allowances (Android cleartext / iOS ATS exceptions) are for local development.

## Operational blockers
- Without Docker daemon, backend integration checks cannot run.
- Without Go toolchain, backend build/test/migrate cannot run.

## Security gaps for production
- No external OTP provider integration yet.
- No refresh token family replay-detection implementation yet.
