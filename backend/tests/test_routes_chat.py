"""API-level tests for POST /chat/ask, hitting the app through TestClient."""
from unittest.mock import patch
from app.models import SourceChunk


def test_ask_returns_200_and_expected_shape(client):
    fake_answer = "RAG stands for Retrieval-Augmented Generation."
    fake_sources = [SourceChunk(source="doc.pdf", chunk_index=0, excerpt="...", similarity_score=0.9)]

    with patch("app.routes.chat.answer_question", return_value=(fake_answer, fake_sources)):
        response = client.post("/chat/ask", json={"question": "What is RAG?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == fake_answer
    assert body["sources"][0]["source"] == "doc.pdf"


def test_ask_rejects_empty_question(client):
    response = client.post("/chat/ask", json={"question": ""})
    assert response.status_code == 422  # FastAPI/Pydantic validation error


def test_ask_rejects_missing_question_field(client):
    response = client.post("/chat/ask", json={})
    assert response.status_code == 422
