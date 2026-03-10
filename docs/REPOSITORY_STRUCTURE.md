# 🧪 Professional ML Research Structure

This document defines the high-end structural standards for **Terraherb**, modeled after top-tier AI research laboratories.

## 🏛️ Root Architecture
| Parent | Layer | Responsibility |
| :--- | :--- | :--- |
| `terraherb/` | **Package** | The core library logic (Models, Datasets, Logic). |
| `configs/` | **Governance** | YAML/JSON hyperparameter and experiment configurations. |
| `docs/` | **Knowledge** | Flattened technical specifications and ML reports. |
| `scripts/` | **CLI** | Entry points for training, evaluation, and deployment. |
| `tests/` | **Integrity** | Unit and integration tests for ML pipelines. |
| `data/` | **Artifacts** | Raw and processed botanical image data (Gitignored). |
| `models/` | **Storage** | Serialized model checkpoints and weights (Gitignored). |

## 🧬 Package Internals (`terraherb/`)
- `datasets/`: PyTorch Dataset class and data augmentation policies.
- `models/`: Model architecture definitions (MobileNetV2, etc.).
- `training/`: Training engine (loops, loss functions, optimizers).
- `inference/`: High-performance inference wrappers.
- `knowledge/`: Biological API connectors (GBIF, Wikipedia).
- `api/`: FastAPI model serving layer.

## 🛠️ Design Patterns
1. **Config-Driven Development**: All hyperparameters reside in `configs/`, never hardcoded in scripts.
2. **Stateless Logic**: Training and inference logic are separated from state (weights).
3. **Determinism**: Random seeds are strictly managed in the training entry points.

---
*Precision as a standard. Intelligence as a result.*
