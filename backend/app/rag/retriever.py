"""Poboljšani retriever s query expansion za hrvatski jezik."""
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.rag.embeddings import embed_query
from app.rag.hybrid_search import reciprocal_rank_fusion


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    document_title: str
    article_number: str | None
    paragraph_number: str | None
    chunk_text: str
    score: float
    search_type: str
    source: str = ""
    source_url: str | None = None
    document_type: str = ""
    legal_area: str | None = None


_BASE_SELECT = """
SELECT c.id AS chunk_id,
       c.document_id,
       d.title AS document_title,
       c.article_number,
       c.paragraph_number,
       c.chunk_text,
       d.source,
       d.source_url,
       d.document_type,
       d.legal_area,
       {score_expr} AS score
FROM legal_chunks c
JOIN legal_documents d ON d.id = c.document_id
"""


def _rows_to_chunks(rows, search_type: str) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk_id=r.chunk_id,
            document_id=r.document_id,
            document_title=r.document_title,
            article_number=r.article_number,
            paragraph_number=r.paragraph_number,
            chunk_text=r.chunk_text,
            score=float(r.score) if r.score is not None else 0.0,
            search_type=search_type,
            source=r.source,
            source_url=r.source_url,
            document_type=r.document_type,
            legal_area=r.legal_area,
        )
        for r in rows
    ]


# Sinonimi i proširenja za česte pravne pojmove na hrvatskom
QUERY_EXPANSIONS: dict[str, list[str]] = {
    "godišnji odmor": ["godišnji odmor", "pravo na odmor", "trajanje odmora", "četiri tjedna"],
    "otkaz": ["otkaz", "prestanak ugovora", "otkazivanje", "redoviti otkaz", "izvanredni otkaz"],
    "otpremnina": ["otpremnina", "pravo na otpremninu", "prestanak radnog odnosa"],
    "plaća": ["plaća", "naknada plaće", "isplata plaće", "neisplata"],
    "radno vrijeme": ["radno vrijeme", "puno radno vrijeme", "nepuno radno vrijeme", "prekovremeni rad"],
    "probni rad": ["probni rad", "trajanje probnog rada"],
    "ugovor o radu": ["ugovor o radu", "sklapanje ugovora", "sadržaj ugovora", "oblik ugovora"],
    "odmor": ["godišnji odmor", "dnevni odmor", "tjedni odmor", "stanka"],
    "trudnica": ["trudnica", "rodiljni dopust", "trudnoća", "zaštita trudnica"],
    "bolovanje": ["bolovanje", "privremena nesposobnost", "naknada za bolovanje"],
}


def expand_query(query: str) -> str:
    """Proširuje upit sinonimima za bolji keyword recall."""
    query_lower = query.lower()
    expansions: list[str] = []
    for key, synonyms in QUERY_EXPANSIONS.items():
        if key in query_lower:
            expansions.extend(synonyms)
    if expansions:
        return query + " " + " ".join(set(expansions))
    return query


def vector_search(db: Session, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    query_embedding = embed_query(query)
    sql = text(
        _BASE_SELECT.format(score_expr="1 - (c.embedding <=> CAST(:qvec AS vector))")
        + """
WHERE c.embedding IS NOT NULL
ORDER BY c.embedding <=> CAST(:qvec AS vector)
LIMIT :top_k
"""
    )
    rows = db.execute(sql, {"qvec": str(query_embedding), "top_k": top_k}).fetchall()
    return _rows_to_chunks(rows, "vector")


def keyword_search(db: Session, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    # Proširi upit sinonimima
    expanded = expand_query(query)
    
    sql = text(
        _BASE_SELECT.format(
            score_expr=(
                "ts_rank(to_tsvector('simple', c.chunk_text), "
                "plainto_tsquery('simple', :q))"
            )
        )
        + """
WHERE to_tsvector('simple', c.chunk_text) @@ plainto_tsquery('simple', :q)
ORDER BY score DESC
LIMIT :top_k
"""
    )
    rows = db.execute(sql, {"q": expanded, "top_k": top_k}).fetchall()
    results = _rows_to_chunks(rows, "keyword")

    if results:
        return results

    # Fallback: ILIKE s grubim stemmingom
    words = [w for w in query.split() if len(w) > 3]
    if not words:
        return []
    like_clauses = " + ".join(
        [f"(CASE WHEN c.chunk_text ILIKE :w{i} THEN 1 ELSE 0 END)" for i in range(len(words))]
    )
    params: dict = {"top_k": top_k}
    for i, w in enumerate(words):
        stem = w[:-2] if len(w) > 5 else w
        params[f"w{i}"] = f"%{stem}%"
    sql2 = text(
        _BASE_SELECT.format(score_expr=like_clauses)
        + f"""
WHERE {like_clauses} > 0
ORDER BY score DESC
LIMIT :top_k
"""
    )
    rows = db.execute(sql2, params).fetchall()
    return _rows_to_chunks(rows, "keyword")


def hybrid_search(db: Session, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    pool = max(top_k * 3, 15)
    vec = vector_search(db, query, top_k=pool)
    kw = keyword_search(db, query, top_k=pool)
    fused = reciprocal_rank_fusion([vec, kw], top_k=top_k)
    for c in fused:
        c.search_type = "hybrid"
    return fused


def retrieve(db: Session, query: str, search_type: str, top_k: int = 5) -> list[RetrievedChunk]:
    if search_type == "vector":
        return vector_search(db, query, top_k)
    if search_type == "keyword":
        return keyword_search(db, query, top_k)
    return hybrid_search(db, query, top_k)
