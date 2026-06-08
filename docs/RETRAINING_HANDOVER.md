# TerraHerb Pre-Flight & Retraining Handover

As verified by the final adversarial review, the TerraHerb project is currently in an **Engineering-Complete, Unvalidated-Model** state. 

The data pipeline has been recovered, structured, and tested. The API and Frontend are fully functional. However, the model weights (`mobilenet_v2.pth`) do not exist for the new 88-class architecture.

## 1. Verified Project State
*   **Dataset:** Recovered and sanitized. Contains 88 classes (including Wheat, Rice, Sugarcane) and 79,087 images.
*   **Architecture:** `inference/classifier.py` is fully synchronized with `training/train_model.py`.
*   **Taxonomy:** Tested and confirmed. The knowledge retrieval layer successfully parses all 88 modified Kaggle class names without breaking.
*   **OOD Logic:** Basic low-confidence rejection (<0.30) is implemented in the API and visualized with warnings in the React frontend.
*   **OpenMP Root Cause:** Identified. The crash is caused by a namespace collision between `torch/lib/libomp.dylib` and `sklearn/.dylibs/libomp.dylib`. The `KMP_DUPLICATE_LIB_OK=TRUE` flag remains embedded to suppress this environmental conflict.

## 2. Immediate Next Action: Full Training Run
The system cannot classify anything until the model is trained. You must run the full training pipeline. **This requires a GPU and significant compute time.**

Execute the following command from the project root:
```bash
python -m terraherb.training.train_model
```
*Note: This will execute the default configuration (25 epochs head-only, 10 epochs fine-tuning) on the 79,000 images.*

## 3. Post-Training Validation (The True Milestone)
Once `models/saved/mobilenet_v2.pth` is generated, you must validate the actual machine learning outcomes:

1.  **Generate Confusion Matrix:**
    ```bash
    python scripts/generate_confusion_matrix.py
    ```
2.  **Review Metrics:**
    *   Verify the Macro F1-Score is acceptable.
    *   Specifically review the precision/recall for the new classes (`Wheat___*`, `Rice___*`).
3.  **Field Testing:**
    *   Upload real, un-cropped photos of wheat and rice taken from a mobile phone to the frontend UI to ensure the model isn't just memorizing laboratory lighting conditions.

## 4. Future Architecture Recommendations
If the model achieves acceptable accuracy, the next priorities should be:
*   **True OOD Detection:** Replace the basic `<0.30` confidence heuristic with Energy-based scoring or Mahalanobis distance to strictly reject unknown crops.
*   **Dataset Balancing:** Address the massive imbalance (e.g., 97 `Wheat___septoria` vs 1225 `Wheat___healthy`) by acquiring targeted data or implementing severe focal loss weighting, beyond what `WeightedRandomSampler` can handle.
