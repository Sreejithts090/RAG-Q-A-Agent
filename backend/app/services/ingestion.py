"""
Document ingestion: load a file from disk, split it into overlapping
chunks suitable for embedding, and tag each chunk with source metadata
(filename + chunk index) so answers can later be cited.
"""
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
}


def load_and_chunk(file_path: str, original_filename: str) -> list:
    """
    Load a document by extension and split it into chunks.
    Raises ValueError for unsupported file types.
    """
    ext = Path(file_path).suffix.lower()
    loader_cls = LOADER_MAP.get(ext)
    if loader_cls is None:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(LOADER_MAP)}")

    loader = loader_cls(file_path)
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    # Normalize metadata: always tag with the original filename and a
    # stable chunk index, regardless of loader-specific metadata quirks.
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = original_filename
        chunk.metadata["chunk_index"] = i

    return chunks
