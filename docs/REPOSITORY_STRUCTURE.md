# 🧪 Professional ML Research Structure

This document defines the high-end structural standards for **Terraherb**, modeled after top-tier AI research laboratories.

## 🏛️ Root Architecture
| Parent | Layer | Responsibility |
| :--- | :--- | :--- |
| `terraherb/` | **Package** | The core library logic (Models, Datasets, Logic). |
| `datasets_substrate/` | **Artifacts** | Unified storage for 3.5GB of raw and processed botanical data. |
| `configs/` | **Governance** | YAML/JSON hyperparameter and experiment configurations. |
| `docs/` | **Knowledge** | Flattened technical specifications and ML reports. |
| `frontend/` | **Interface** | Vite + React Plant Identification Dashboard. |
| `notebooks/` | **Research** | Experiment logs and Strategy 98 implementation reports. |
| `tests/` | **Integrity** | Unit and integration tests for ML pipelines. |

## 🧬 Package Internals (`terraherb/`)
- `api/`: FastAPI model serving layer.
- `datasets/`: PyTorch/TF data loaders and augmentation policies.
- `inference/`: High-performance inference wrappers and predictors.
- `knowledge/`: UCI Taxonomic Client and botanical metadata logic.
- `models/`: Model architecture definitions (MobileNetV2, EfficientNetB0).
- `training/`: Training engines for "Strategy 98" high-accuracy pipelines.

## 🛠️ Design Patterns
1. **Config-Driven Development**: All hyperparameters reside in `configs/`, never hardcoded in scripts.
2. **Stateless Logic**: Training and inference logic are separated from state (weights).
3. **Determinism**: Random seeds are strictly managed in the training entry points.

---
*Precision as a standard. Intelligence as a result.*
