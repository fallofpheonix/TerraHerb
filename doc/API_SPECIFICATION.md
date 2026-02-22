# API_SPECIFICATION

## Base
- Base URL: `http://localhost:8080`
- Version prefix: `/api/v1`
- Content type: `application/json`

## Endpoints
- `GET /health`
- `GET /metrics`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/plants`
- `GET /api/v1/plants/by-season`
- `GET /api/v1/plants/by-climate-zone`
- `GET /api/v1/plants/{id}`

## Error Envelope
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "request_id": "..."
  }
}
```

## Source of truth
- `backend/docs/openapi.yaml`
- `backend/docs/postman_collection.json`
