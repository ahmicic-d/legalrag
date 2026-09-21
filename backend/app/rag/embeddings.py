"""Generiranje embeddinga pomoću SentenceTransformers.

Model se učitava lijeno (lazy) i kešira, jer je učitavanje skupo.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Vraća listu embedding vektora za listu tekstova."""
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> list[float]:
    """Embedding za korisničko pitanje."""
    return embed_texts([query])[0]
