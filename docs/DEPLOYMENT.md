# Deployment

## Runtime Components
- FastAPI service (`terraherb.api.main:app`)
- React frontend (`frontend/` static build)

## Local Deployment
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn terraherb.api.main:app --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm install
npm run build
```

## Production Notes
- Run FastAPI behind a reverse proxy.
- Configure request size limits and CORS origins.
- Keep model weights outside image layers where possible.
