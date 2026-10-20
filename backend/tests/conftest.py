"""
Shared pytest fixtures.

Design note: unit/route tests never touch the real embedding model,
Chroma DB, or Ollama server. Those are mocked at the service-function
boundary (e.g. `app.services.vectorstore.add_documents`) so the test
suite runs fast, deterministically, and without any GPU/network/model
download — important for CI.
"""
import sys
from pathlib import Path

# Make `app` importable when pytest is run from the backend/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_txt_file(tmp_path) -> Path:
    """A small text file with enough content to produce multiple chunks."""
    content = (
        "Retrieval-Augmented Generation combines a retriever with a generator.\n\n"
        "The retriever finds relevant chunks of text from a knowledge base using "
        "semantic similarity search over vector embeddings.\n\n"
        "The generator, typically a large language model, then produces an answer "
        "conditioned on the retrieved context, which reduces hallucination compared "
        "to asking the model with no supporting context at all.\n\n"
        "This project demonstrates the full pipeline: ingestion, chunking, embedding, "
        "storage in a vector database, retrieval, and grounded generation."
    )
    file_path = tmp_path / "sample.txt"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def client():
    """FastAPI TestClient built from the real app, routes included."""
    from app.main import app
    return TestClient(app)
