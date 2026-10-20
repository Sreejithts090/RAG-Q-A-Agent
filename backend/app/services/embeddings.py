"""
Local embedding model wrapper.

Using a local HuggingFace sentence-transformers model (instead of an API)
means embedding generation is free, offline, and has no rate limits —
important for a demo/resume project that should run anywhere.
"""
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Cached so the (relatively heavy) sentence-transformer model is
    loaded into memory only once per process.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
