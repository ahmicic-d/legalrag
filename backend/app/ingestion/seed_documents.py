"""Seed pipeline: dohvat -> čišćenje -> chunkiranje -> embedding -> baza.

Početni korpus sadrži Zakon o radu (NN 93/2014). Dodatni dokumenti se
jednostavno dodaju u SEED_DOCUMENTS listu.
"""
import logging

from sqlalchemy.orm import Session

from app.ingestion.chunk_legal_text import chunk_document
from app.ingestion.clean_text import clean_text
from app.ingestion.embed_documents import embed_pending_chunks
from app.ingestion.fetch_nn import fetch_document
from app.ingestion.parse_html import html_to_text
from app.models import LegalChunk, LegalDocument

logger = logging.getLogger(__name__)

SEED_DOCUMENTS = [
    {
        "title": "Zakon o radu",
        "url": "https://narodne-novine.nn.hr/clanci/sluzbeni/2014_07_93_1872.html",
        "source": "Narodne novine",
        "document_type": "zakon",
        "legal_area": "radno pravo",
    },
    # Dodatni izvori (povezani propisi, sudske odluke, EUR-Lex) dodaju se ovdje, npr.:
    # {
    #     "title": "Direktiva (EU) 2019/1152 o transparentnim i predvidivim radnim uvjetima",
    #     "url": "https://eur-lex.europa.eu/legal-content/HR/TXT/HTML/?uri=CELEX:32019L1152",
    #     "source": "EUR-Lex",
    #     "document_type": "eu_direktiva",
    #     "legal_area": "radno pravo",
    # },
]


def ingest_document(db: Session, spec: dict) -> tuple[LegalDocument | None, int, str]:
    """Ingesta jednog dokumenta. Vraća (dokument, broj chunkova, poruka)."""
    existing = db.query(LegalDocument).filter(LegalDocument.title == spec["title"]).first()
    if existing:
        return None, 0, f"Preskočeno (već postoji): {spec['title']}"

    try:
        raw = fetch_document(spec["url"])
    except Exception as exc:  # noqa: BLE001
        logger.error("Dohvat nije uspio za %s: %s", spec["url"], exc)
        return None, 0, f"Dohvat nije uspio: {spec['title']} ({exc})"

    text = clean_text(html_to_text(raw)) if "<" in raw[:200] else clean_text(raw)

    doc = LegalDocument(
        title=spec["title"],
        source=spec["source"],
        source_url=spec["url"],
        document_type=spec["document_type"],
        legal_area=spec.get("legal_area"),
        raw_text=text,
    )
    db.add(doc)
    db.flush()

    chunks = chunk_document(text, spec["document_type"])
    for c in chunks:
        db.add(
            LegalChunk(
                document_id=doc.id,
                chunk_text=c.text,
                article_number=c.article_number,
                paragraph_number=c.paragraph_number,
                chunk_index=c.chunk_index,
                meta=c.metadata,
            )
        )
    db.commit()

    embedded = embed_pending_chunks(db, document_id=doc.id)
    return doc, len(chunks), f"Ingestano: {spec['title']} ({len(chunks)} chunkova, {embedded} embeddinga)"


def run_seed(db: Session) -> tuple[int, int, list[str]]:
    """Pokreće seed za sve dokumente. Vraća (br. dokumenata, br. chunkova, poruke)."""
    docs, chunks, messages = 0, 0, []
    for spec in SEED_DOCUMENTS:
        doc, n_chunks, msg = ingest_document(db, spec)
        messages.append(msg)
        if doc is not None:
            docs += 1
            chunks += n_chunks
    return docs, chunks, messages
