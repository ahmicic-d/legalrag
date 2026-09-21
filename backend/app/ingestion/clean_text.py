"""Čišćenje teksta prije chunkiranja."""
import re


def clean_text(text: str) -> str:
    """Normalizira whitespace, uklanja artefakte HTML/PDF ekstrakcije."""
    # Normaliziraj razne vrste razmaka
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    # Ukloni višestruke razmake unutar redaka
    text = re.sub(r"[ \t]+", " ", text)
    # Ukloni razmake na počecima/krajevima redaka
    text = "\n".join(line.strip() for line in text.splitlines())
    # Sažmi 3+ praznih redova u dva
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
