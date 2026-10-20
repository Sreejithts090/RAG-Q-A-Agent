"""
The core RAG chain: retrieve relevant chunks, then generate an answer
grounded strictly in that retrieved context.

The prompt explicitly instructs the model to say when it doesn't know,
rather than hallucinate — the whole point of RAG over a plain LLM call.
"""
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import get_llm
from app.services.vectorstore import similarity_search_with_scores
from app.models import SourceChunk

SYSTEM_PROMPT = """You are a precise question-answering assistant.
Answer the user's question using ONLY the context below.
If the context does not contain the answer, say clearly that the
documents don't contain enough information — do not make anything up.
Keep answers concise and cite specific details from the context where relevant.

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def _format_context(results) -> str:
    parts = []
    for doc, score in results:
        parts.append(f"[Source: {doc.metadata.get('source')} | chunk {doc.metadata.get('chunk_index')}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def answer_question(question: str) -> tuple[str, list[SourceChunk]]:
    """Run retrieval + generation, returning (answer_text, cited_sources)."""
    results = similarity_search_with_scores(question)

    if not results:
        return (
            "No documents have been indexed yet, so I don't have any context to answer from. "
            "Please upload a document first.",
            [],
        )

    context = _format_context(results)
    messages = prompt.format_messages(context=context, question=question)
    response = get_llm().invoke(messages)
    # ChatOllama (like other chat models) returns an AIMessage; fall back to
    # str() so this also works if a plain string-returning LLM is swapped in.
    answer = response.content if hasattr(response, "content") else str(response)

    sources = [
        SourceChunk(
            source=doc.metadata.get("source", "unknown"),
            chunk_index=doc.metadata.get("chunk_index", -1),
            excerpt=doc.page_content[:280].strip() + ("..." if len(doc.page_content) > 280 else ""),
            similarity_score=round(score, 4) if score is not None else None,
        )
        for doc, score in results
    ]
    return answer, sources
