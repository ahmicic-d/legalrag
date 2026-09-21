"""POST /api/query — glavna pretraga i RAG pipeline."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.rag.generator import compute_confidence, generate_answer
from app.rag.prompts import NO_CONTEXT_ANSWER
from app.rag.retriever import retrieve
from app.schemas import QueryRequest, QueryResponse, RetrievedChunkOut, SourceOut

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    chunks = retrieve(db, payload.question, payload.search_type, payload.top_k)

    if payload.search_type == "rag":
        answer = await generate_answer(payload.question, chunks)
    else:
        answer = (
            "Prikazani su dohvaćeni dijelovi dokumenata bez LLM generiranja. "
            "Odaberite metodu 'RAG' za generirani odgovor."
            if chunks
            else NO_CONTEXT_ANSWER
        )

    confidence = compute_confidence(chunks, payload.search_type)

    # Deduplikacija izvora po (dokument, članak)
    seen: set[tuple[int, str | None]] = set()
    sources: list[SourceOut] = []
    for c in chunks:
        key = (c.document_id, c.article_number)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            SourceOut(
                document_id=c.document_id,
                document_title=c.document_title,
                article_number=c.article_number,
                paragraph_number=c.paragraph_number,
                source=c.source,
                source_url=c.source_url,
                document_type=c.document_type,
                legal_area=c.legal_area,
            )
        )

    return QueryResponse(
        question=payload.question,
        answer=answer,
        confidence=confidence,
        search_type=payload.search_type,
        sources=sources,
        retrieved_chunks=[
            RetrievedChunkOut(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                document_title=c.document_title,
                article_number=c.article_number,
                paragraph_number=c.paragraph_number,
                chunk_text=c.chunk_text,
                score=round(c.score, 4),
                search_type=c.search_type,
            )
            for c in chunks
        ],
    )
