"""Parsiranje HTML dokumenata (Narodne novine, EUR-Lex, sudske odluke)."""
from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """Pretvara HTML u čisti tekst, čuvajući strukturu odlomaka."""
    soup = BeautifulSoup(html, "lxml")

    # Ukloni nepotrebne elemente
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()

    # Narodne novine: glavni sadržaj je često u <div> s klasom koja sadrži 'clanak'
    # ili u <body>; pokušaj pronaći najrelevantniji kontejner.
    main = (
        soup.find("div", class_=lambda c: c and "clanak" in c.lower())
        or soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    # Odlomci odvojeni novim redovima
    lines: list[str] = []
    for element in main.find_all(["p", "h1", "h2", "h3", "h4", "li", "td"]):
        text = element.get_text(separator=" ", strip=True)
        if text:
            lines.append(text)

    if not lines:
        return main.get_text(separator="\n", strip=True)
    return "\n".join(lines)
