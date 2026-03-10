# Changelog

All notable changes to the Terraherb project will be documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.3.0] - 2026-03-10

### Added
- Inference completions: `PlantClassifier.predict()` and `PlantPredictor.predict()` fully implemented with MobileNetV2 forward pass and top-k confidence scoring.
- Preprocessing pipeline: `preprocess_image()` with OpenCV blur detection, PIL decode, ImageNet normalization.
- KnowledgeRetriever: GBIF REST + Wikipedia API integration with in-process response cache, plus local UCI Plants CSV lookup.
- Disease treatment database: Built-in curated treatment guide (organic, chemical, prevention) for major PlantVillage disease classes.
- FastAPI enhancements: `/ready`, `/classes`, `/treatment/{label}`, CORS middleware, request size/MIME validation, structured logging, lifespan startup.
- Go API: `internal/handler` package and endpoints `/health`, `/api/v1/plants`, `/api/v1/plants/{id}`, `/api/v1/seasonal`, `/api/v1/identify`.
- Flutter UI: `lib/main.dart` implementing `TerraHerbariumApp` with Marketplace, Identify, and Seasonal pages.
- Test suites: `tests/test_inference.py`, `tests/test_model.py`, `tests/test_api.py`, `backend/internal/handler/handler_test.go`.
- Weighted dataset sampler: `PlantVillageDataset.class_weights()` + `WeightedRandomSampler` in `get_dataloader()`.
- Two-phase training loop: head-only training then partial fine-tuning with `CosineAnnealingLR` and early stopping.

### Fixed
- `requirements.txt`: duplicate entries removed and missing test/runtime dependencies added.
- `scripts/check-health.sh`: directory checks fixed and non-zero exit on failures.
- `MobileNetClassifier`: deprecated pretrained init replaced with explicit `weights=MobileNet_V2_Weights.IMAGENET1K_V1`; forward pass fixed with `AdaptiveAvgPool2d`.
- Changelog inconsistency: removed incorrect statement claiming Flutter/Go decommissioning.
- `backend/internal/handler`: removed placeholder proxy scaffold and implemented multipart forwarding.

### Changed
- `MobileNetClassifier.forward()` now uses explicit `AdaptiveAvgPool2d` + flatten for deterministic output shape.
- `get_dataloader()` includes `use_weighted_sampler` and `pin_memory` flags.
- `PlantPredictor` accepts optional classifier dependency injection for testability.

## [0.2.0] - 2026-02-18

### Added
- MVP backend + Flutter seasonal client integration.
- Auth/refresh/logout endpoints and migration runner.
- Observability (`/metrics`, structured logs) and CI workflows.

## [0.1.0] - 2026-02-01

### Added
- Initial repository structure.
- Python ML substrate scaffold (PyTorch + TensorFlow paths).
- Go API scaffold with Postgres/Redis via Docker Compose.
- Flutter app scaffold with bottom navigation.
