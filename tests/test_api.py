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


def test_classes_returns_88(client: TestClient) -> None:
    resp = client.get("/classes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 88
    assert len(body["classes"]) == 88


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


def test_identify_low_confidence_skips_retrieval(client: TestClient) -> None:
    predictor = MagicMock()
    # Threshold is 0.70, so 0.65 is low confidence
    predictor.predict.return_value = {
        "species": "Apple___healthy",
        "crop": "Apple",
        "condition": "healthy",
        "is_healthy": True,
        "confidence": 0.65,
        "low_confidence": True,
        "top_predictions": [{"label": "Apple___healthy", "probability": 0.65}],
    }
    predictor.LOW_CONFIDENCE_THRESHOLD = 0.70

    retriever = MagicMock(spec=KnowledgeRetriever)

    api_module._state["predictor"] = predictor
    api_module._state["retriever"] = retriever

    resp = client.post("/identify", files={"file": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")})
    assert resp.status_code == 200
    body = resp.json()

    assert body["low_confidence"] is True
    assert body["knowledge"]["status"] == "uncertain"
    # Ensure retriever was NEVER called
    retriever.fetch_plant_data.assert_not_called()


def test_knowledge_retriever_remote_disabled() -> None:
    retriever = KnowledgeRetriever(enable_remote=False)
    result = retriever.fetch_plant_data("Apple___healthy")
    assert result["is_healthy"] is True
    assert result["taxonomy"]["kingdom"] == "Plantae"


def test_knowledge_retriever_orange_canonical_lookup() -> None:
    # This tests the logic added to avoid "Nesothele Orange"
    retriever = KnowledgeRetriever(enable_remote=True)

    # Mock GBIF client to return a lichen if we search for "Orange"
    # and a plant if we search for "Citrus sinensis"
    retriever._gbif = MagicMock()

    def side_effect(q):
        if q == "Citrus sinensis":
            return {"kingdom": "Plantae", "scientificName": "Citrus sinensis", "family": "Rutaceae"}
        return {"kingdom": "Fungi", "scientificName": "Nesothele Orange", "family": "Verrucariaceae"}

    retriever._gbif.search_species.side_effect = side_effect

    # This should use the map and search for "Citrus sinensis"
    result = retriever.fetch_plant_data("Orange___Haunglongbing_(Citrus_greening)")

    assert result["taxonomy"]["kingdom"] == "Plantae"
    assert result["taxonomy"]["scientific_name"] == "Citrus sinensis"
    # Ensure it searched for the scientific name
    retriever._gbif.search_species.assert_called_with("Citrus sinensis")


def test_knowledge_retriever_rejects_non_plantae() -> None:
    retriever = KnowledgeRetriever(enable_remote=True)
    retriever._gbif = MagicMock()
    # Mock GBIF returning a Fungus
    retriever._gbif.search_species.return_value = {"kingdom": "Fungi", "scientificName": "Some Fungus"}

    result = retriever.fetch_plant_data("Apple___healthy")

    # Should fall back to basic taxonomy and not include the Fungus data
    assert result["taxonomy"]["kingdom"] == "Plantae"
    assert "Some Fungus" not in str(result["taxonomy"])
    assert result["taxonomy"]["scientific_name"] == "Apple"
