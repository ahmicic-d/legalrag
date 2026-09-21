"""Metrike za evaluaciju retrievala: Precision@k, Recall@k, MRR.

Relevantnost chunka definirana je preko očekivanog dokumenta i (opcionalno)
očekivanog broja članka iz evaluation_questions.
"""


def is_relevant(chunk, expected_source: str | None, expected_article: str | None) -> bool:
    """Chunk je relevantan ako pripada očekivanom dokumentu i članku (ako je zadan)."""
    if expected_source and expected_source.lower() not in chunk.document_title.lower():
        return False
    if expected_article:
        return (chunk.article_number or "").strip() == expected_article.strip()
    return True


def precision_at_k(retrieved: list, expected_source: str | None, expected_article: str | None, k: int) -> float:
    """Udio relevantnih među prvih k dohvaćenih."""
    top = retrieved[:k]
    if not top:
        return 0.0
    relevant = sum(1 for c in top if is_relevant(c, expected_source, expected_article))
    return relevant / len(top)


def recall_at_k(
    retrieved: list,
    expected_source: str | None,
    expected_article: str | None,
    k: int,
    total_relevant: int,
) -> float:
    """Udio pronađenih relevantnih u odnosu na ukupan broj relevantnih u korpusu."""
    if total_relevant <= 0:
        return 0.0
    top = retrieved[:k]
    found = sum(1 for c in top if is_relevant(c, expected_source, expected_article))
    return min(found / total_relevant, 1.0)


def mrr(retrieved: list, expected_source: str | None, expected_article: str | None) -> float:
    """Mean Reciprocal Rank: 1/rang prvog relevantnog rezultata."""
    for rank, c in enumerate(retrieved, start=1):
        if is_relevant(c, expected_source, expected_article):
            return 1.0 / rank
    return 0.0
