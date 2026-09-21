"""Generiranje i spremanje embeddinga za chunkove."""
import logging

from sqlalchemy.orm import Session

from app.models import LegalChunk
from app.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)

BATCH_SIZE = 32


def embed_pending_chunks(db: Session, document_id: int | None = None) -> int:
    """Embedda sve chunkove koji još nemaju embedding. Vraća broj obrađenih."""
    query = db.query(LegalChunk).filter(LegalChunk.embedding.is_(None))
    if document_id is not None:
        query = query.filter(LegalChunk.document_id == document_id)
    chunks = query.order_by(LegalChunk.id).all()

    total = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        vectors = embed_texts([c.chunk_text for c in batch])
        for chunk, vec in zip(batch, vectors):
            chunk.embedding = vec
        db.commit()
        total += len(batch)
        logger.info("Embeddano %d/%d chunkova", total, len(chunks))
    return total
