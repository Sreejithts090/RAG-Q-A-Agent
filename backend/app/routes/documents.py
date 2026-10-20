"""Endpoints for uploading and listing indexed documents."""
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.models import UploadResponse, DocumentListResponse, DocumentInfo
from app.services.ingestion import load_and_chunk
from app.services.vectorstore import add_documents, list_indexed_sources

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest_path = upload_dir / file.filename

    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        chunks = load_and_chunk(str(dest_path), original_filename=file.filename)
        count = add_documents(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

    return UploadResponse(
        filename=file.filename,
        chunks_indexed=count,
        message=f"Indexed {count} chunks from {file.filename}",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    counts = list_indexed_sources()
    docs = [DocumentInfo(filename=name, chunk_count=c) for name, c in counts.items()]
    return DocumentListResponse(documents=docs)
