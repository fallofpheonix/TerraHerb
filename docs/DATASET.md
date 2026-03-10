# 📊 DATASET.md — Plant Disease Classification (Merged)

Terraherb utilizes a **Merged Plant Disease Classification Dataset**, which combines multiple high-fidelity botanical image sources for robust species and disease identification.

## 📈 Dataset Statistics
- **Source**: Kaggle (alinedobrovsky/plant-disease-classification-merged-dataset)
- **Content**: Comprehensive collection of healthy and diseased plant leaves.
- **Ingestion**: Managed via `kagglehub` for versioned data provenance.

## 🌽 Species Coverage
The dataset covers 14 crop species including:
- Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, and Tomato.

## 🛠️ Data Processing Pipeline
1. **Splitting**: 75% Training, 15% Validation, 10% Testing.
2. **Augmentation**:
   - Random Horizontal Flip
   - Random Color Jitter (Brightness/Contrast)
   - Random Affine (Rotation/Translation)
3. **Normalization**: Scaling pixel values to [0, 1] followed by ImageNet mean/std normalization.

## 📂 Implementation
Refer to [`terraherb/datasets/plantvillage_loader.py`](../terraherb/datasets/plantvillage_loader.py) for the PyTorch `Dataset` implementation.
