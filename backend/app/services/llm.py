"""
Local LLM wrapper via Ollama.

Ollama serves open-source models (Llama 3.1, Mistral, etc.) locally over
a simple HTTP API, so the whole pipeline works fully offline with no
API keys — a deliberate choice to keep this project free to run and
easy for anyone to clone and demo.
"""
from functools import lru_cache
from langchain_ollama import ChatOllama
from app.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.1,
        repeat_penalty=1.3, 
        num_predict=512  # low temperature: favor grounded, factual answers
    )
