"""GET /api/documents — pregled korpusa."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LegalChunk, LegalDocument
from app.schemas import DocumentDetailOut, DocumentOut

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentOut]:
    rows = (
        db.query(LegalDocument, func.count(LegalChunk.id).label("chunk_count"))
        .outerjoin(LegalChunk, LegalChunk.document_id == LegalDocument.id)
        .group_by(LegalDocument.id)
        .order_by(LegalDocument.id)
        .all()
    )
    return [
        DocumentOut(
            id=doc.id,
            title=doc.title,
            source=doc.source,
            source_url=doc.source_url,
            document_type=doc.document_type,
            legal_area=doc.legal_area,
            publication_date=doc.publication_date,
            created_at=doc.created_at,
            chunk_count=chunk_count,
        )
        for doc, chunk_count in rows
    ]


@router.get("/documents/{document_id}", response_model=DocumentDetailOut)
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentDetailOut:
    doc = db.get(LegalDocument, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Dokument nije pronađen")
    chunk_count = db.query(func.count(LegalChunk.id)).filter(LegalChunk.document_id == doc.id).scalar()
    return DocumentDetailOut(
        id=doc.id,
        title=doc.title,
        source=doc.source,
        source_url=doc.source_url,
        document_type=doc.document_type,
        legal_area=doc.legal_area,
        publication_date=doc.publication_date,
        created_at=doc.created_at,
        chunk_count=chunk_count or 0,
        raw_text_preview=(doc.raw_text[:2000] + "…") if doc.raw_text and len(doc.raw_text) > 2000 else doc.raw_text,
    )
