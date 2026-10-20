"""
ChromaDB vector store: initialization, document indexing, and retrieval.

Chroma persists to disk (backend/data/chroma_db) so ingested documents
survive server restarts — no need to re-embed everything each run.
"""
from functools import lru_cache
from typing import Optional
from langchain_chroma import Chroma
from app.config import settings
from app.services.embeddings import get_embeddings

COLLECTION_NAME = "rag_documents"


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def add_documents(chunks: list) -> int:
    """Embed and persist a list of LangChain Document chunks. Returns count added."""
    store = get_vectorstore()
    store.add_documents(chunks)
    return len(chunks)


def similarity_search_with_scores(query: str, k: Optional[int] = None):
    """Return top-k (Document, similarity_score) pairs for a query."""
    store = get_vectorstore()
    k = k or settings.top_k
    return store.similarity_search_with_relevance_scores(query, k=k)


def list_indexed_sources() -> dict[str, int]:
    """Return {filename: chunk_count} for everything currently indexed."""
    store = get_vectorstore()
    raw = store.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for meta in raw.get("metadatas", []):
        source = meta.get("source", "unknown")
        counts[source] = counts.get(source, 0) + 1
    return counts
