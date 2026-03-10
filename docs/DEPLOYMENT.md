# 📦 DEPLOYMENT.md — Production Orchestration

## 🏛️ Strategy
Terraherb is designed for containerized deployment using **Docker** and **Kubernetes**.

## 🛠️ Docker Orchestration
We use the root `docker-compose.yml` for local production-like environments.

```bash
docker-compose up -d --build
```

## 🏗️ Environment Configuration
Backend secrets are managed via `.env` files in the `backend/` directory.

## 📱 Client Distribution
- **Android/iOS**: CI/CD pipelines generate signed binaries for App Store/Play Store distribution.
- **Web**: Static hosting for the Flutter Web build.

---

*Stability is a function of structure.*
