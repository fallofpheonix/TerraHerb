from __future__ import annotations

import io
from unittest.mock import MagicMock

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

import terraherb.api.main as api_module
from terraherb.knowledge.client import KnowledgeRetriever


def _jpeg_bytes(width: int = 128, height: int = 128) -> bytes:
    img = Image.fromarray(np.random.randint(0, 255, (height, width, 3), dtype=np.uint8), "RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture()
def client() -> TestClient:
    with TestClient(api_module.app, raise_server_exceptions=True) as c:
        yield c


def test_health_returns_200(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_ready_returns_200_when_loaded(client: TestClient) -> None:
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_classes_returns_38(client: TestClient) -> None:
    resp = client.get("/classes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 38
    assert len(body["classes"]) == 38


def test_treatment_returns_payload(client: TestClient) -> None:
    resp = client.get("/treatment/Tomato___Early_blight")
    assert resp.status_code == 200
    body = resp.json()
    assert "treatment" in body
    assert "organic" in body["treatment"]


def test_identify_rejects_unsupported_media_type(client: TestClient) -> None:
    resp = client.post("/identify", files={"file": ("bad.pdf", b"%PDF", "application/pdf")})
    assert resp.status_code == 415


def test_identify_rejects_empty_file(client: TestClient) -> None:
    resp = client.post("/identify", files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert resp.status_code == 422


def test_identify_success_with_stubbed_state(client: TestClient) -> None:
    predictor = MagicMock()
    predictor.predict.return_value = {
        "species": "Tomato___Early_blight",
        "crop": "Tomato",
        "condition": "Early blight",
        "is_healthy": False,
        "confidence": 0.91,
        "low_confidence": False,
        "top_predictions": [
            {"label": "Tomato___Early_blight", "probability": 0.91},
            {"label": "Tomato___Late_blight", "probability": 0.06},
            {"label": "Tomato___healthy", "probability": 0.03},
        ],
    }

    retriever = MagicMock(spec=KnowledgeRetriever)
    retriever.fetch_plant_data.return_value = {
        "crop": "Tomato",
        "condition": "Early blight",
        "treatment": {"organic": ["Neem oil"], "chemical": ["Chlorothalonil"], "prevention": ["Crop rotation"]},
    }

    api_module._state["predictor"] = predictor
    api_module._state["retriever"] = retriever

    resp = client.post("/identify", files={"file": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["species"] == "Tomato___Early_blight"
    assert body["confidence"] == pytest.approx(0.91, abs=1e-5)
    assert body["knowledge"]["crop"] == "Tomato"


def test_knowledge_retriever_remote_disabled() -> None:
    retriever = KnowledgeRetriever(enable_remote=False)
    result = retriever.fetch_plant_data("Apple___healthy")
    assert result["is_healthy"] is True
    assert result["taxonomy"]["kingdom"] == "Plantae"
