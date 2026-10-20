"""API-level tests for the document upload/list endpoints."""
import io
from unittest.mock import patch


def test_upload_rejects_unsupported_extension(client):
    file_content = b"hello world"
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.md", io.BytesIO(file_content), "text/markdown")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_txt_indexes_and_returns_chunk_count(client):
    file_content = b"RAG combines retrieval with generation for grounded answers."

    # Mock the vector-store write so this test never touches the real
    # embedding model or Chroma DB.
    with patch("app.routes.documents.add_documents", return_value=1) as mock_add:
        response = client.post(
            "/documents/upload",
            files={"file": ("sample.txt", io.BytesIO(file_content), "text/plain")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "sample.txt"
    assert body["chunks_indexed"] == 1
    mock_add.assert_called_once()


def test_list_documents_returns_indexed_sources(client):
    with patch("app.routes.documents.list_indexed_sources", return_value={"sample.txt": 3}):
        response = client.get("/documents")

    assert response.status_code == 200
    body = response.json()
    assert body["documents"] == [{"filename": "sample.txt", "chunk_count": 3}]


def test_root_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
