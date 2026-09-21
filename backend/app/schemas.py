"""Pydantic sheme (request/response modeli)."""
from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SearchType = Literal["keyword", "vector", "hybrid", "rag"]
Confidence = Literal["high", "medium", "low"]


# ---------- Query ----------

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    search_type: SearchType = "hybrid"
    top_k: int = Field(5, ge=1, le=20)


class SourceOut(BaseModel):
    document_id: int
    document_title: str
    article_number: str | None = None
    paragraph_number: str | None = None
    source: str
    source_url: str | None = None
    document_type: str
    legal_area: str | None = None


class RetrievedChunkOut(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    article_number: str | None = None
    paragraph_number: str | None = None
    chunk_text: str
    score: float
    search_type: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    confidence: Confidence
    search_type: SearchType
    sources: list[SourceOut]
    retrieved_chunks: list[RetrievedChunkOut]
    disclaimer: str = (
        "Ovaj odgovor je informativnog karaktera i ne predstavlja pravni savjet. "
        "Za konkretne pravne situacije obratite se odvjetniku ili nadležnom tijelu."
    )


# ---------- Documents ----------

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    source_url: str | None
    document_type: str
    legal_area: str | None
    publication_date: date | None
    created_at: datetime
    chunk_count: int = 0


class DocumentDetailOut(DocumentOut):
    raw_text_preview: str | None = None


# ---------- Ingestion ----------

class SeedResponse(BaseModel):
    status: str
    documents_ingested: int
    chunks_created: int
    details: list[str] = []


# ---------- Evaluation ----------

class EvaluationQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    expected_source: str | None
    expected_article: str | None
    notes: str | None


class EvaluationRunRequest(BaseModel):
    top_k: int = Field(5, ge=1, le=20)
    methods: list[Literal["keyword", "vector", "hybrid"]] = ["keyword", "vector", "hybrid"]


class EvaluationResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    question: str | None = None
    method: str
    retrieved_chunk_ids: list[int] | None
    precision_at_k: float | None
    recall_at_k: float | None
    mrr: float | None
    created_at: datetime


class MethodSummary(BaseModel):
    method: str
    avg_precision_at_k: float
    avg_recall_at_k: float
    avg_mrr: float
    num_questions: int


class EvaluationRunResponse(BaseModel):
    top_k: int
    summaries: list[MethodSummary]
    results: list[EvaluationResultOut]
