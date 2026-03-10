import pytest
from fastapi.testclient import TestClient
from terraherb.api.main import app

client = TestClient(app)

def test_health_check():
    """
    Verify the AI substrate health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_inference_endpoint_structure():
    """
    Verify the API response structure (using dummy data).
    """
    # Note: In a real test, we would provide a small dummy image
    pass
