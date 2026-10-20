"""
Tests for document loading + chunking.

Uses real TextLoader / text splitter (no mocking needed here — these
are lightweight, pure-Python and require no model downloads).
"""
import pytest
from app.services.ingestion import load_and_chunk


def test_load_and_chunk_txt_returns_chunks(sample_txt_file):
    chunks = load_and_chunk(str(sample_txt_file), original_filename="sample.txt")

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.page_content.strip() != ""


def test_chunks_are_tagged_with_source_metadata(sample_txt_file):
    chunks = load_and_chunk(str(sample_txt_file), original_filename="sample.txt")

    for chunk in chunks:
        assert chunk.metadata["source"] == "sample.txt"
        assert isinstance(chunk.metadata["chunk_index"], int)


def test_chunk_indices_are_sequential(sample_txt_file):
    chunks = load_and_chunk(str(sample_txt_file), original_filename="sample.txt")
    indices = [c.metadata["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))


def test_unsupported_file_type_raises_value_error(tmp_path):
    bad_file = tmp_path / "notes.md"
    bad_file.write_text("hello")

    with pytest.raises(ValueError, match="Unsupported file type"):
        load_and_chunk(str(bad_file), original_filename="notes.md")


def test_chunk_size_respects_config(sample_txt_file):
    """Chunks should not wildly exceed the configured chunk_size + overlap slack."""
    from app.config import settings
    chunks = load_and_chunk(str(sample_txt_file), original_filename="sample.txt")
    # Recursive splitter can slightly exceed chunk_size on hard-to-split text;
    # allow generous slack rather than asserting an exact bound.
    for chunk in chunks:
        assert len(chunk.page_content) <= settings.chunk_size + 200
