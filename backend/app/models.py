"""Pydantic request/response schemas shared across routes."""
from typing import Optional 
from pydantic import BaseModel, Field

class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's natural-language question")


class SourceChunk(BaseModel):
    source: str
    chunk_index: int
    excerpt: str
    similarity_score: Optional[float] = None



class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class DocumentInfo(BaseModel):
    filename: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
