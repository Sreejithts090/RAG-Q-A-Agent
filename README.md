# RAG Q&A Agent

A full-stack **Retrieval-Augmented Generation (RAG)** question-answering agent. Upload documents (PDF/TXT/DOCX), and ask natural-language questions grounded in their content — answers are generated **only from retrieved context**, with source citations, using a **fully local, open-source LLM stack** (no API keys required).

## Why this project

Most "chatbot" demos just call an LLM API. This project implements the full RAG pipeline end-to-end:

- Document ingestion → chunking → embedding → vector storage
- Semantic retrieval (top-k similarity search) at query time
- Context-grounded generation with a local LLM (via Ollama)
- Source-attributed answers (shows which chunk/page an answer came from)
- A real client/server architecture (FastAPI backend, React frontend) rather than a single Streamlit script

## Architecture

```
┌─────────────┐      HTTP/REST       ┌──────────────────┐
│   React     │  ───────────────────▶│    FastAPI        │
│  (Vite +    │◀───────────────────  │    Backend         │
│  Tailwind)  │      JSON             └─────────┬────────┘
└─────────────┘                                 │
                                                 ▼
                          ┌──────────────────────────────────────┐
                          │           RAG Pipeline                │
                          │                                        │
                          │  1. Ingestion (PyPDF/docx loaders)     │
                          │  2. Chunking (recursive text splitter) │
                          │  3. Embeddings (HuggingFace            │
                          │     sentence-transformers, local)      │
                          │  4. Vector Store (ChromaDB, persisted) │
                          │  5. Retriever (top-k cosine similarity)│
                          │  6. LLM (Ollama — Llama 3.1 / Mistral) │
                          │  7. Answer + cited source chunks       │
                          └──────────────────────────────────────┘
```

## Tech stack

| Layer | Technology |
|---|---|
| LLM | [Ollama](https://ollama.com) (Llama 3.1 / Mistral, runs locally) |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (local, no API key) |
| Vector DB | [ChromaDB](https://www.trychroma.com/) (persisted on disk) |
| Orchestration | LangChain (LCEL RAG chain) |
| Backend | FastAPI + Uvicorn, Pydantic v2 |
| Frontend | React 18 + Vite + TailwindCSS |
| Deployment | Docker + docker-compose |

## Features

- 📄 Multi-format ingestion: PDF, TXT, DOCX
- ✂️ Configurable chunking (size/overlap)
- 🔍 Semantic retrieval with similarity scores
- 💬 Chat interface with streaming-style responses
- 📚 Source citations under every answer (filename + chunk excerpt)
- 🧠 100% local inference — no OpenAI/Gemini API key needed, runs offline
- 🐳 One-command startup via Docker Compose

## Project structure

```
rag-qa-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── config.py            # settings (env-driven)
│   │   ├── models.py            # Pydantic schemas
│   │   ├── services/
│   │   │   ├── embeddings.py    # HuggingFace embedding model
│   │   │   ├── vectorstore.py   # Chroma init/query
│   │   │   ├── llm.py           # Ollama wrapper
│   │   │   ├── ingestion.py     # load + chunk documents
│   │   │   └── rag_chain.py     # LCEL retrieval-augmented chain
│   │   └── routes/
│   │       ├── documents.py     # upload/ingest endpoints
│   │       └── chat.py          # ask-question endpoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   └── FileUpload.jsx
│   │   └── api/client.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting started

### Prerequisites
- [Ollama](https://ollama.com/download) installed locally, with a model pulled:
  ```bash
  ollama pull llama3.1
  ```
- Python 3.11+, Node 18+ (or just Docker)

### Option A — Docker (recommended)
```bash
docker-compose up --build
```
Backend: http://localhost:8000  Frontend: http://localhost:5173

### Option B — Manual

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## How it works (RAG pipeline)

1. **Upload** — a document is uploaded via `/documents/upload`.
2. **Ingest** — `ingestion.py` loads the file and splits it into overlapping chunks (`RecursiveCharacterTextSplitter`).
3. **Embed** — each chunk is embedded locally with `all-MiniLM-L6-v2` (no network call).
4. **Store** — embeddings + metadata (source, chunk index) are persisted in ChromaDB.
5. **Ask** — a question hits `/chat/ask`; it's embedded and used to retrieve the top-k most similar chunks.
6. **Generate** — the retrieved chunks are inserted into a prompt template and sent to the local Ollama model, which is instructed to answer **only** from the provided context and say so if the answer isn't present.
7. **Respond** — the answer is returned along with the source chunks used, so the user can verify it.

## Testing

The backend has a pytest suite covering ingestion/chunking, Pydantic
schema validation, the RAG chain's grounding logic, and the API routes
(document upload + chat). Heavy dependencies (the embedding model,
Chroma, Ollama) are mocked at the service boundary, so the suite runs
fast with no GPU, network access, or running Ollama server required.

```bash
cd backend
python -m venv venv && source venv/bin/activate   # if not already set up
pip install -r requirements-dev.txt
pytest
```

This also runs automatically on every push/PR via GitHub Actions
(`.github/workflows/ci.yml`), alongside a frontend build check.

## Resume bullet points (suggested)

- Built a full-stack RAG (Retrieval-Augmented Generation) Q&A system with a FastAPI backend and React frontend, using LangChain, ChromaDB, and locally-hosted LLMs via Ollama.
- Implemented a document ingestion pipeline (chunking + embedding with HuggingFace sentence-transformers) and a semantic retrieval layer with source-cited, context-grounded answer generation.
- Containerized the application with Docker Compose for reproducible, one-command deployment.
- Wrote a pytest suite (ingestion, schema validation, RAG grounding logic, API routes) with mocked model/vector-store boundaries, wired into a GitHub Actions CI pipeline.

## License
MIT
