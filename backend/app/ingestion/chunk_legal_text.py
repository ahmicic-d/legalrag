"""Chunkiranje pravnih tekstova.

Zakoni se chunkiraju po člancima ("Članak N."), jer je članak prirodna
semantička jedinica pravnog teksta. Sudske odluke i ostali dokumenti
chunkiraju se po odlomcima s preklapanjem.
"""
import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    article_number: str | None = None
    paragraph_number: str | None = None
    chunk_index: int = 0
    metadata: dict = field(default_factory=dict)


# "Članak 79." na početku retka (razne varijante pisanja)
ARTICLE_RE = re.compile(r"(?m)^\s*Članak\s+(\d+[a-z]?)\.?\s*$", re.IGNORECASE)

MAX_CHUNK_CHARS = 2500  # sigurnosna granica za jako duge članke


def chunk_law_by_articles(text: str) -> list[Chunk]:
    """Dijeli tekst zakona na chunkove po člancima."""
    matches = list(ARTICLE_RE.finditer(text))
    chunks: list[Chunk] = []

    if not matches:
        return chunk_by_paragraphs(text)

    # Preambula prije prvog članka (naslov zakona, uvod)
    preamble = text[: matches[0].start()].strip()
    if len(preamble) > 100:
        chunks.append(Chunk(text=preamble[:MAX_CHUNK_CHARS], metadata={"section": "preambula"}))

    for i, m in enumerate(matches):
        article_no = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if not body:
            continue
        # Predugi članci: podijeli po stavcima "(1) ... (2) ..."
        if len(body) > MAX_CHUNK_CHARS:
            for sub in _split_long_article(body):
                chunks.append(Chunk(text=sub, article_number=article_no))
        else:
            chunks.append(Chunk(text=body, article_number=article_no))

    for idx, c in enumerate(chunks):
        c.chunk_index = idx
    return chunks


def _split_long_article(body: str) -> list[str]:
    parts: list[str] = []
    current = ""
    for line in body.splitlines():
        if len(current) + len(line) > MAX_CHUNK_CHARS and current:
            parts.append(current.strip())
            current = ""
        current += line + "\n"
    if current.strip():
        parts.append(current.strip())
    return parts


def chunk_by_paragraphs(text: str, target_chars: int = 1200, overlap_chars: int = 200) -> list[Chunk]:
    """Chunkiranje po odlomcima s preklapanjem — za sudske odluke i sl."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    chunks: list[Chunk] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 1 > target_chars and current:
            chunks.append(Chunk(text=current.strip()))
            # preklapanje: zadrži rep prethodnog chunka
            current = current[-overlap_chars:] if overlap_chars else ""
        current += para + "\n"

    if current.strip():
        chunks.append(Chunk(text=current.strip()))

    for idx, c in enumerate(chunks):
        c.chunk_index = idx
    return chunks


def chunk_document(text: str, document_type: str) -> list[Chunk]:
    """Odabire strategiju chunkiranja prema tipu dokumenta."""
    if document_type in ("zakon", "pravilnik", "uredba"):
        return chunk_law_by_articles(text)
    return chunk_by_paragraphs(text)
