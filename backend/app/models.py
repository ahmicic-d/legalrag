"""SQLAlchemy modeli baze podataka."""
from datetime import datetime, date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database import Base


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)  # npr. "Narodne novine"
    source_url: Mapped[str | None] = mapped_column(String(1000))
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)  # zakon, sudska_odluka, ...
    legal_area: Mapped[str | None] = mapped_column(String(255))  # npr. "radno pravo"
    publication_date: Mapped[date | None] = mapped_column(Date)
    raw_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["LegalChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class LegalChunk(Base):
    __tablename__ = "legal_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    article_number: Mapped[str | None] = mapped_column(String(50))  # npr. "79"
    paragraph_number: Mapped[str | None] = mapped_column(String(50))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.embedding_dim))

    document: Mapped[LegalDocument] = relationship(back_populates="chunks")

    __table_args__ = (
        Index(
            "ix_legal_chunks_embedding_cosine",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class EvaluationQuestion(Base):
    __tablename__ = "evaluation_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_source: Mapped[str | None] = mapped_column(String(500))  # naslov očekivanog dokumenta
    expected_article: Mapped[str | None] = mapped_column(String(50))  # npr. "77"
    notes: Mapped[str | None] = mapped_column(Text)

    results: Mapped[list["EvaluationResult"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    method: Mapped[str] = mapped_column(String(50), nullable=False)  # keyword | vector | hybrid
    retrieved_chunk_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    precision_at_k: Mapped[float | None] = mapped_column(Float)
    recall_at_k: Mapped[float | None] = mapped_column(Float)
    mrr: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    question: Mapped[EvaluationQuestion] = relationship(back_populates="results")
