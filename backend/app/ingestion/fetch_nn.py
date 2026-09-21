"""Dohvaćanje dokumenata s Narodnih novina (ili općenito s URL-a / lokalne datoteke)."""
import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "LegalRag/1.0 (diplomski rad; akademska svrha)",
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_url(url: str, timeout: float = 60.0) -> str:
    """Dohvaća HTML sadržaj s URL-a."""
    logger.info("Dohvaćam: %s", url)
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=HEADERS) as client:
        resp = client.get(url)
        resp.raise_for_status()
        resp.encoding = resp.encoding or "utf-8"
        return resp.text


def fetch_local(path: str | Path) -> str:
    """Učitava sadržaj iz lokalne datoteke (HTML ili TXT)."""
    p = Path(path)
    logger.info("Učitavam lokalnu datoteku: %s", p)
    return p.read_text(encoding="utf-8")


def fetch_document(url_or_path: str) -> str:
    """Dohvaća dokument s URL-a ili lokalne putanje."""
    if url_or_path.startswith(("http://", "https://")):
        return fetch_url(url_or_path)
    return fetch_local(url_or_path)
