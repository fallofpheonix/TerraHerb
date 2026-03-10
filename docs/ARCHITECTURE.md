# Architecture

## Scope
Python/ML-only system for image classification + botanical knowledge retrieval.

## Data Flow
1. User uploads image from React UI.
2. FastAPI validates MIME/size and forwards bytes to `PlantPredictor`.
3. `PlantClassifier` preprocesses and performs MobileNetV2 inference.
4. `KnowledgeRetriever` enriches prediction with UCI local data + GBIF/Wikipedia.
5. API returns structured JSON (prediction + confidence + treatment + taxonomy).

## Training Flow
1. Dataset ingestion into `datasets_substrate/raw/plant_disease_merged`.
2. `PlantVillageDataset` builds stratified train/val/test splits.
3. Phase 1: train head with backbone frozen.
4. Phase 2: unfreeze top layers, fine-tune with reduced LR.
5. Save checkpoints in `models/saved/`.

## Evaluation Flow
- Top-1 / Top-5 accuracy during validation.
- Loss tracked per epoch.
- Optional TensorFlow Strategy 98 run for higher top-1 accuracy.

## Invariants
- Model input shape: `(B, 3, 224, 224)`.
- Output classes: 38 PlantVillage labels.
- API response includes `species`, `confidence`, `top_predictions`, `knowledge`.
- Local knowledge path must exist for UCI enrichment.

## Constraints
- Inference path must be CPU-safe.
- External API failures must degrade gracefully.
- Training scripts must be deterministic with fixed seed.
