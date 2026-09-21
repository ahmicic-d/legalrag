"""Konfiguracija aplikacije.

Sve postavke se čitaju iz environment varijabli (ili .env datoteke).
API ključevi se NIKADA ne hardkodiraju.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Baza podataka ---
    database_url: str = "postgresql+psycopg://legalrag:legalrag@localhost:5432/legalrag"

    # --- Embeddings ---
    # Višejezični model koji dobro radi za hrvatski jezik.
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384

    # --- LLM (Ollama ili bilo koji OpenAI-kompatibilan API) ---
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "llama3.1"
    llm_api_key: str = ""  # prazno za Ollama; postavite za OpenAI-kompatibilne servise
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024
    llm_timeout_seconds: float = 120.0

    # --- Retrieval ---
    default_top_k: int = 5
    max_top_k: int = 20
    # Pragovi kosinusne sličnosti za confidence oznaku
    confidence_high_threshold: float = 0.60
    confidence_medium_threshold: float = 0.40

    # --- CORS ---
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
