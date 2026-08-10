import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_upload_text_file():
    files = {"file": ("sample.txt", b"Magnetar AI is a production RAG platform.", "text/plain")}
    response = client.post(
        "/api/v1/upload",
        headers={"X-API-Key": settings.API_KEY},
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data
    assert data["filename"] == "sample.txt"
    assert data["chunks_created"] >= 1
