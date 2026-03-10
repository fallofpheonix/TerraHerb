# Dataset

## Primary Dataset: PlantVillage
- Classes: 38
- Images: ~54,000
- Task: Multi-class crop disease/health classification

## Canonical Storage
- `datasets_substrate/raw/plant_disease_merged/`
- `datasets_substrate/processed/`
- `datasets_substrate/external/`

## Ingestion
- Script: `terraherb/scripts/ingest_data.py`
- Provider: KaggleHub dataset `alinedobrovsky/plant-disease-classification-merged-dataset`

## Split Strategy
- Train: 75%
- Validation: 15%
- Test: 10%
- Stratified by label

## Augmentation
- Random crop/flip/rotation/affine
- Color jitter
- ImageNet normalization

## Local Knowledge Dataset (UCI Plants)
- Path: `datasets_substrate/external/uci_plants/plants.data`
- Usage: distribution metadata enrichment in `KnowledgeRetriever`
