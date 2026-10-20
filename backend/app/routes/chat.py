"""Endpoint for asking a question against the indexed documents."""
from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.services.rag_chain import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask(request: ChatRequest):
    answer, sources = answer_question(request.question)
    return ChatResponse(answer=answer, sources=sources)
