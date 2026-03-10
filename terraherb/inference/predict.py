"""
High-level prediction facade used by the FastAPI layer.
Wraps PlantClassifier and enriches output with parsed metadata.
"""

from __future__ import annotations

import logging
from typing import Optional

from terraherb.inference.classifier import PlantClassifier, get_classifier

logger = logging.getLogger(__name__)


def _parse_class_label(label: str) -> dict:
    """
    Split a PlantVillage class label into its constituent parts.

    Label format: "<Crop>___<Condition>"
    e.g. "Tomato___Early_blight" → {"crop": "Tomato", "condition": "Early blight", "is_healthy": False}
    """
    parts = label.split("___", 1)
    crop = parts[0].replace("_", " ").strip()
    condition_raw = parts[1] if len(parts) > 1 else "Unknown"
    condition = condition_raw.replace("_", " ").strip()
    is_healthy = "healthy" in condition_raw.lower()
    return {"crop": crop, "condition": condition, "is_healthy": is_healthy}


class PlantPredictor:
    """
    Thin facade over PlantClassifier for use in the API layer.

    Provides:
      - predict(image_bytes) → structured result dict
      - Parsed crop/condition metadata
      - Confidence-based warnings (low-confidence flag)
    """

    LOW_CONFIDENCE_THRESHOLD = 0.55

    def __init__(
        self,
        model_path: str = "models/saved/mobilenet_v2.pth",
        classifier: Optional[PlantClassifier] = None,
    ) -> None:
        self._classifier = classifier or get_classifier(model_path=model_path)

    def predict(self, image_bytes: bytes) -> dict:
        """
        Run inference and return a structured prediction result.

        Args:
            image_bytes: Raw image bytes from the upload.

        Returns:
            dict with:
              - "species": Top predicted class label (raw PlantVillage string).
              - "crop": Human-readable crop name.
              - "condition": Human-readable condition / disease name.
              - "is_healthy": bool — True if the plant appears healthy.
              - "confidence": float — model probability for the top class.
              - "low_confidence": bool — True if confidence < threshold.
              - "top_predictions": list of top-3 predictions with label + probability.
        """
        raw = self._classifier.predict(image_bytes, top_k=3)

        parsed = _parse_class_label(raw["top_class"])
        confidence = raw["confidence"]
        low_confidence = confidence < self.LOW_CONFIDENCE_THRESHOLD

        if low_confidence:
            logger.warning(
                "Low-confidence prediction (%.2f) for class '%s'. "
                "Consider requesting a clearer image.",
                confidence,
                raw["top_class"],
            )

        return {
            "species": raw["top_class"],
            "crop": parsed["crop"],
            "condition": parsed["condition"],
            "is_healthy": parsed["is_healthy"],
            "confidence": confidence,
            "low_confidence": low_confidence,
            "top_predictions": raw["top_k"],
        }
