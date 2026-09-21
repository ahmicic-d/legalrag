"""POST /api/ingest/seed — pokretanje ingestion pipelinea."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.evaluation.test_questions import seed_test_questions
from app.ingestion.seed_documents import run_seed
from app.schemas import SeedResponse

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])


@router.post("/seed", response_model=SeedResponse)
def seed(db: Session = Depends(get_db)) -> SeedResponse:
    docs, chunks, messages = run_seed(db)
    inserted_questions = seed_test_questions(db)
    if inserted_questions:
        messages.append(f"Ubačeno {inserted_questions} evaluacijskih pitanja.")
    return SeedResponse(
        status="ok",
        documents_ingested=docs,
        chunks_created=chunks,
        details=messages,
    )
