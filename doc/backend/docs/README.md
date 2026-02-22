# Backend API Docs

## Files
- `openapi.yaml`: OpenAPI spec for backend endpoints.
- `postman_collection.json`: Postman collection for quick endpoint testing.

## Import OpenAPI
1. Open Swagger Editor or any OpenAPI-compatible tool.
2. Load `backend/docs/openapi.yaml`.
3. Set server URL to `http://localhost:8080`.

## Import Postman Collection
1. Open Postman.
2. Click **Import**.
3. Select `backend/docs/postman_collection.json`.
4. Ensure `baseUrl` variable is `http://localhost:8080`.

## Endpoint Coverage
- `GET /health`
- `GET /api/v1/plants`
- `GET /api/v1/plants/by-season`
- `GET /api/v1/plants/by-climate-zone`
- `GET /api/v1/plants/{id}`
