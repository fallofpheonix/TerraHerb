# EVALUATION_HARNESS

## Functional checks
- Health: `curl localhost:8080/health`
- Metrics: `curl localhost:8080/metrics`
- Auth login/refresh/logout flows via Postman collection
- Plant query endpoints with valid and invalid params

## Build checks
- Flutter: analyze + test
- Backend: tidy + test + build

## Failure checks
- Invalid token => `401`
- Invalid query => `400`
- Missing entity => `404`
- Rate limit breach => `429`
