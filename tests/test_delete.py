import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_delete_document():
    # First upload a doc
    files = {"file": ("to_delete.txt", b"Content to be deleted.", "text/plain")}
    up_resp = client.post(
        "/api/v1/upload",
        headers={"X-API-Key": settings.API_KEY},
        files=files
    )
    doc_id = up_resp.json()["doc_id"]

    # Delete doc
    del_resp = client.delete(
        f"/api/v1/delete/{doc_id}",
        headers={"X-API-Key": settings.API_KEY}
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["doc_id"] == doc_id
