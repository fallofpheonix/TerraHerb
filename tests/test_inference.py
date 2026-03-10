from __future__ import annotations

import io

import pytest
from PIL import Image

from terraherb.inference.classifier import preprocess_image
from terraherb.inference.predict import PlantPredictor


def _png_bytes() -> bytes:
    img = Image.new("RGB", (256, 256), (10, 180, 10))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_preprocess_image_returns_expected_shape() -> None:
    tensor = preprocess_image(_png_bytes())
    assert tuple(tensor.shape) == (1, 3, 224, 224)


def test_preprocess_image_invalid_bytes_raises() -> None:
    with pytest.raises(ValueError):
        preprocess_image(b"not-an-image")


class _FakeClassifier:
    def __init__(self, confidence: float) -> None:
        self.confidence = confidence

    def predict(self, image_bytes: bytes, top_k: int = 3) -> dict:
        return {
            "top_class": "Tomato___Early_blight",
            "confidence": self.confidence,
            "top_k": [
                {"label": "Tomato___Early_blight", "probability": self.confidence},
                {"label": "Tomato___Late_blight", "probability": 0.05},
                {"label": "Tomato___healthy", "probability": 0.03},
            ],
        }


def test_predictor_parses_class_label() -> None:
    predictor = PlantPredictor(classifier=_FakeClassifier(0.9))
    result = predictor.predict(_png_bytes())
    assert result["species"] == "Tomato___Early_blight"
    assert result["crop"] == "Tomato"
    assert result["condition"] == "Early blight"
    assert result["is_healthy"] is False


def test_predictor_low_confidence_flag() -> None:
    predictor = PlantPredictor(classifier=_FakeClassifier(0.30))
    result = predictor.predict(_png_bytes())
    assert result["low_confidence"] is True
