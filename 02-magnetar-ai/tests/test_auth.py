import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_missing_api_key():
    response = client.post("/api/v1/ask", json={"question": "hello"})
    assert response.status_code == 403

def test_invalid_api_key():
    response = client.post("/api/v1/ask", headers={"X-API-Key": "wrong-key"}, json={"question": "hello"})
    assert response.status_code == 403

def test_valid_api_key():
    response = client.post(
        "/api/v1/ask",
        headers={"X-API-Key": settings.API_KEY},
        json={"question": "What is Magnetar?"}
    )
    assert response.status_code == 200
