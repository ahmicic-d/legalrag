"""LegalRag — FastAPI aplikacija.

Inteligentni sustav za pretraživanje hrvatskih pravnih dokumenata
temeljen na RAG arhitekturi. Diplomski rad.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, evaluation, ingestion, query
from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicijalizacija baze podataka…")
    init_db()
    logger.info("LegalRag backend spreman.")
    yield


app = FastAPI(
    title="LegalRag",
    description="Inteligentni sustav za pretraživanje hrvatskih pravnih dokumenata (RAG)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(documents.router)
app.include_router(ingestion.router)
app.include_router(evaluation.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "legalrag-backend"}
