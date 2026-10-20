"""Tests for Pydantic request/response schema validation."""
import pytest
from pydantic import ValidationError
from app.models import ChatRequest, SourceChunk, ChatResponse, UploadResponse


def test_chat_request_accepts_valid_question():
    req = ChatRequest(question="What is RAG?")
    assert req.question == "What is RAG?"


def test_chat_request_rejects_empty_question():
    with pytest.raises(ValidationError):
        ChatRequest(question="")


def test_chat_request_requires_question_field():
    with pytest.raises(ValidationError):
        ChatRequest()


def test_source_chunk_allows_missing_similarity_score():
    chunk = SourceChunk(source="doc.pdf", chunk_index=0, excerpt="some text")
    assert chunk.similarity_score is None


def test_chat_response_serializes_sources_list():
    resp = ChatResponse(
        answer="RAG combines retrieval and generation.",
        sources=[SourceChunk(source="doc.pdf", chunk_index=0, excerpt="...", similarity_score=0.87)],
    )
    dumped = resp.model_dump()
    assert dumped["sources"][0]["similarity_score"] == 0.87


def test_upload_response_requires_all_fields():
    with pytest.raises(ValidationError):
        UploadResponse(filename="a.pdf")
