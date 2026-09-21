"""Poboljšani generator s retry logikom i post-procesiranjem za Gemma3."""
import logging
import re

import httpx

from app.config import settings
from app.rag.prompts import NO_CONTEXT_ANSWER, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, build_context

logger = logging.getLogger(__name__)


def compute_confidence(chunks, search_type: str) -> str:
    if not chunks:
        return "low"

    if search_type in ("vector",):
        top = chunks[0].score
        if top >= settings.confidence_high_threshold:
            return "high"
        if top >= settings.confidence_medium_threshold:
            return "medium"
        return "low"

    doc_ids = {c.document_id for c in chunks}
    if len(chunks) >= 3 and len(doc_ids) <= 2:
        return "high"
    if len(chunks) >= 2:
        return "medium"
    return "low"


def _clean_gemma_response(text: str) -> str:
    """Čisti Gemma-specifične artefakte iz odgovora."""
    # Ukloni thinking tagove ako ih ima
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Ukloni prazne redove na početku
    text = text.strip()
    # Ukloni markdown bold oko cijelih rečenica (Gemma to često radi)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    return text


async def generate_answer(question: str, chunks) -> str:
    if not chunks:
        return NO_CONTEXT_ANSWER

    context = build_context(chunks)
    
    payload = {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(context=context, question=question)},
        ],
    }
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    
    # Retry logika - Ollama ponekad treba zagrijavanje
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                answer = data["choices"][0]["message"]["content"].strip()
                answer = _clean_gemma_response(answer)
                
                # Ako Gemma kaže "nemam info" ali kontekst postoji, 
                # probaj s direktnijim promptom
                if attempt == 0 and _is_refusal(answer) and len(chunks) >= 3:
                    logger.info("Model odbio odgovoriti, pokušavam s direktnijim promptom...")
                    payload["messages"][1]["content"] = (
                        f"Kontekst:\n\n{context}\n\n---\n\n"
                        f"Pitanje: {question}\n\n"
                        f"Gornji kontekst SADRŽI odgovor na ovo pitanje. "
                        f"Pažljivo pročitaj svaki članak i napiši odgovor. "
                        f"Citiraj brojeve članaka."
                    )
                    continue
                
                return answer
        except httpx.HTTPError as exc:
            logger.error("LLM poziv nije uspio (pokušaj %d): %s", attempt + 1, exc)
            if attempt == max_retries:
                return (
                    "LLM servis trenutno nije dostupan pa odgovor nije generiran. "
                    "U nastavku su prikazani dohvaćeni relevantni dijelovi dokumenata — "
                    "provjerite konfiguraciju LLM_BASE_URL / LLM_MODEL."
                )
    
    return NO_CONTEXT_ANSWER


def _is_refusal(answer: str) -> bool:
    """Detektira li Gemma odbija odgovoriti unatoč kontekstu."""
    refusal_markers = [
        "nemam dovoljno informacija",
        "nije navedeno u kontekstu",
        "ne mogu pronaći",
        "kontekst ne sadrži",
        "nije moguće odgovoriti",
        "nema podataka",
        "nije specificirano",
    ]
    lower = answer.lower()
    return any(m in lower for m in refusal_markers)
