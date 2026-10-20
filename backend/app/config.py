"""
Centralized, env-driven configuration.
Keeping every tunable in one place makes the RAG pipeline easy to
experiment with (chunk size, top_k, model names) without touching code.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ollama (local LLM server)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"

    # Embeddings (local, HuggingFace)
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 4

    # Storage
    chroma_persist_dir: str = "./data/chroma_db"
    upload_dir: str = "./data/uploads"


settings = Settings()
