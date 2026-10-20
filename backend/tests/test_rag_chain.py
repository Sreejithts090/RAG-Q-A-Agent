"""
Tests for the retrieval + generation chain.

The retriever (`similarity_search_with_scores`) and the LLM are both
mocked here — this tests the RAG *logic* (grounding, source formatting,
the "no documents indexed" fallback) rather than actual model output,
so it runs without a real Ollama server or downloaded embedding model.
"""
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from app.services.rag_chain import answer_question


def test_answer_question_with_no_indexed_documents_returns_fallback():
    with patch("app.services.rag_chain.similarity_search_with_scores", return_value=[]):
        answer, sources = answer_question("What is RAG?")

    assert "don't have any context" in answer.lower() or "no documents" in answer.lower()
    assert sources == []


def test_answer_question_returns_llm_answer_and_cited_sources():
    fake_doc = Document(
        page_content="RAG grounds LLM answers in retrieved context.",
        metadata={"source": "sample.txt", "chunk_index": 0},
    )
    fake_results = [(fake_doc, 0.91)]

    # Mimic a LangChain chat model: .invoke(messages) -> object with .content
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="RAG grounds answers in retrieved context.")

    with patch("app.services.rag_chain.similarity_search_with_scores", return_value=fake_results), \
         patch("app.services.rag_chain.get_llm", return_value=mock_llm):
        answer, sources = answer_question("How does RAG work?")

    assert answer == "RAG grounds answers in retrieved context."
    mock_llm.invoke.assert_called_once()

    assert len(sources) == 1
    assert sources[0].source == "sample.txt"
    assert sources[0].chunk_index == 0
    assert sources[0].similarity_score == 0.91


def test_context_passed_to_llm_includes_retrieved_chunk_text():
    """The prompt sent to the LLM should actually contain the retrieved content."""
    fake_doc = Document(
        page_content="UNIQUE_MARKER_TEXT_12345",
        metadata={"source": "sample.txt", "chunk_index": 0},
    )
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="answer")

    with patch("app.services.rag_chain.similarity_search_with_scores", return_value=[(fake_doc, 0.5)]), \
         patch("app.services.rag_chain.get_llm", return_value=mock_llm):
        answer_question("question")

    sent_messages = mock_llm.invoke.call_args[0][0]
    rendered = "\n".join(m.content for m in sent_messages)
    assert "UNIQUE_MARKER_TEXT_12345" in rendered


def test_source_excerpt_is_truncated_for_long_chunks():
    long_text = "x" * 500
    fake_doc = Document(page_content=long_text, metadata={"source": "big.pdf", "chunk_index": 3})
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="answer")

    with patch("app.services.rag_chain.similarity_search_with_scores", return_value=[(fake_doc, 0.5)]), \
         patch("app.services.rag_chain.get_llm", return_value=mock_llm):
        _, sources = answer_question("question")

    assert len(sources[0].excerpt) <= 284  # 280 chars + "..."
    assert sources[0].excerpt.endswith("...")
