# RISK_REGISTER

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---:|---:|---|
| R1 | Dev OTP config leaking to prod | Medium | High | Enforce prod guardrails and env checks |
| R2 | Query slowdown at scale | Medium | High | Index tuning + load tests + query plans |
| R3 | Refresh token misuse | Medium | High | Rotation + strict revocation + metadata checks |
| R4 | Migration drift | Low | High | Versioned runner + CI migration checks |
| R5 | Redis unavailability | Medium | Medium | Graceful fallback + alerts |
