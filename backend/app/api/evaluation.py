"""Evaluacijski endpointi: pitanja, pokretanje i rezultati.

Kontrolna pitanja (bez očekivanog dokumenta i članka) izuzimaju se iz
izračuna prosječnih metrika, budući da za njih pojam relevantnosti nije
definiran. Broje se zasebno, kao mjera sposobnosti sustava da prizna
nedostatak informacija.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.database import get_db
from app.evaluation.metrics import mrr, precision_at_k, recall_at_k
from app.models import EvaluationQuestion, EvaluationResult
from app.rag.retriever import retrieve
from app.schemas import (
    EvaluationQuestionOut,
    EvaluationResultOut,
    EvaluationRunRequest,
    EvaluationRunResponse,
    MethodSummary,
)

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


def _is_control(q: EvaluationQuestion) -> bool:
    """Kontrolno pitanje: korpus ne sadrži odgovor, pa relevantnost nije definirana."""
    return not q.expected_source and not q.expected_article


@router.get("/questions", response_model=list[EvaluationQuestionOut])
def list_questions(db: Session = Depends(get_db)):
    return db.query(EvaluationQuestion).order_by(EvaluationQuestion.id).all()


def _total_relevant(db: Session, expected_source: str | None, expected_article: str | None) -> int:
    """Ukupan broj relevantnih chunkova u korpusu (za Recall@k)."""
    sql = """
        SELECT COUNT(*) FROM legal_chunks c
        JOIN legal_documents d ON d.id = c.document_id
        WHERE (CAST(:src AS text) IS NULL OR d.title ILIKE '%' || CAST(:src AS text) || '%')
          AND (CAST(:art AS text) IS NULL OR c.article_number = CAST(:art AS text))
    """
    return db.execute(sql_text(sql), {"src": expected_source, "art": expected_article}).scalar() or 0


@router.post("/run", response_model=EvaluationRunResponse)
def run_evaluation(payload: EvaluationRunRequest, db: Session = Depends(get_db)) -> EvaluationRunResponse:
    questions = db.query(EvaluationQuestion).order_by(EvaluationQuestion.id).all()
    results_out: list[EvaluationResultOut] = []

    # Rezultati se skupljaju odvojeno: samo pitanja s definiranom relevantnošću
    # ulaze u izračun prosjeka.
    scored: dict[str, list[EvaluationResult]] = {m: [] for m in payload.methods}

    for q in questions:
        control = _is_control(q)
        total_rel = 0 if control else _total_relevant(db, q.expected_source, q.expected_article)

        for method in payload.methods:
            chunks = retrieve(db, q.question, method, payload.top_k)

            if control:
                # Relevantnost nije definirana; metrike se ne računaju.
                result = EvaluationResult(
                    question_id=q.id,
                    method=method,
                    retrieved_chunk_ids=[c.chunk_id for c in chunks],
                    precision_at_k=None,
                    recall_at_k=None,
                    mrr=None,
                )
            else:
                result = EvaluationResult(
                    question_id=q.id,
                    method=method,
                    retrieved_chunk_ids=[c.chunk_id for c in chunks],
                    precision_at_k=precision_at_k(
                        chunks, q.expected_source, q.expected_article, payload.top_k
                    ),
                    recall_at_k=recall_at_k(
                        chunks, q.expected_source, q.expected_article, payload.top_k, total_rel
                    ),
                    mrr=mrr(chunks, q.expected_source, q.expected_article),
                )

            db.add(result)
            db.flush()

            if not control:
                scored[method].append(result)

            results_out.append(
                EvaluationResultOut(
                    id=result.id,
                    question_id=q.id,
                    question=q.question,
                    method=method,
                    retrieved_chunk_ids=result.retrieved_chunk_ids,
                    precision_at_k=result.precision_at_k,
                    recall_at_k=result.recall_at_k,
                    mrr=result.mrr,
                    created_at=result.created_at or datetime.now(timezone.utc),
                )
            )
    db.commit()

    summaries = []
    for method, results in scored.items():
        n = len(results)
        if n == 0:
            continue
        summaries.append(
            MethodSummary(
                method=method,
                avg_precision_at_k=round(sum(r.precision_at_k or 0 for r in results) / n, 4),
                avg_recall_at_k=round(sum(r.recall_at_k or 0 for r in results) / n, 4),
                avg_mrr=round(sum(r.mrr or 0 for r in results) / n, 4),
                num_questions=n,
            )
        )

    return EvaluationRunResponse(top_k=payload.top_k, summaries=summaries, results=results_out)


@router.get("/results", response_model=list[EvaluationResultOut])
def list_results(limit: int = 100, db: Session = Depends(get_db)):
    rows = (
        db.query(EvaluationResult, EvaluationQuestion.question)
        .join(EvaluationQuestion, EvaluationQuestion.id == EvaluationResult.question_id)
        .order_by(EvaluationResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        EvaluationResultOut(
            id=r.id,
            question_id=r.question_id,
            question=question,
            method=r.method,
            retrieved_chunk_ids=r.retrieved_chunk_ids,
            precision_at_k=r.precision_at_k,
            recall_at_k=r.recall_at_k,
            mrr=r.mrr,
            created_at=r.created_at,
        )
        for r, question in rows
    ]