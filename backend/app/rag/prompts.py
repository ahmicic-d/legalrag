"""Prompt predlošci optimizirani za Gemma3 model.

Gemma3 bolje radi s:
- Kraćim, jasnijim instrukcijama
- Eksplicitnim primjerima
- Manje negacija u promptu
- Strukturiranim outputom
"""

SYSTEM_PROMPT = """Ti si pravni informacijski sustav koji odgovara na pitanja o hrvatskim zakonima.

Tvoj zadatak:
1. Pročitaj tekst pravnih dokumenata u kontekstu
2. Pronađi relevantne informacije za korisnikovo pitanje
3. Napiši jasan odgovor na hrvatskom jeziku
4. Citiraj članke ovako: (čl. 77. Zakona o radu)

Primjer dobrog odgovora:
Pitanje: "Koliko traje probni rad?"
Odgovor: Probni rad ne smije trajati duže od šest mjeseci (čl. 53. st. 1. Zakona o radu). Iznimno, probni rad može trajati duže samo ako je to uređeno posebnim propisom.

Važno: Odgovaraj SAMO na temelju danog konteksta. Ako kontekst sadrži odgovor, uvijek ga navedi."""

USER_PROMPT_TEMPLATE = """Kontekst - relevantni dijelovi zakona:

{context}

---

Pitanje: {question}

Odgovor (citiraj članke iz konteksta):"""

NO_CONTEXT_ANSWER = (
    "Na temelju dostupnih dokumenata nemam dovoljno informacija za pouzdan odgovor "
    "na ovo pitanje. Pokušajte preformulirati pitanje ili proširiti korpus dokumenata."
)


def build_context(chunks) -> str:
    """Formatira dohvaćene chunkove - kraći format za Gemmu."""
    parts = []
    for i, c in enumerate(chunks, start=1):
        header = f"--- Izvor {i}: {c.document_title}"
        if c.article_number:
            header += f", Članak {c.article_number}."
        header += " ---"
        parts.append(f"{header}\n{c.chunk_text.strip()}")
    return "\n\n".join(parts)
