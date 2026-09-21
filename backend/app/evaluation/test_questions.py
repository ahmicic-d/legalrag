"""Skup testnih pitanja za evaluaciju retrievala (30 pitanja).

Pitanja su razvrstana u pet tipova prema zahtjevima koje postavljaju pred
dohvaćanje (v. potpoglavlje 3.3):

  A — točno pravno nazivlje    (7)   očekivano: leksička pretraga jaka
  B — svakodnevni jezik         (7)   očekivano: semantička pretraga jaka
  C — morfološki zahtjevna      (8)   očekivano: leksička slaba zbog padeža
  D — višedijelna pitanja       (6)   očekivano: hibridna jaka
  E — izvan opsega korpusa      (2)   kontrolna: sustav treba priznati neznanje

Pitanja tipa E nemaju očekivani članak i izuzimaju se iz izračuna metrika.

NAPOMENA: brojevi članaka označeni s PROVJERITI nisu potvrđeni; provjeriti
skriptom verify_questions.py prije uporabe u mjerenju.
"""
from sqlalchemy.orm import Session

from app.models import EvaluationQuestion

TEST_QUESTIONS = [
    # ═══════════ A: točno pravno nazivlje (7) ═══════════
    {
        "question": "Što je otpremnina i kada radnik na nju ima pravo?",
        "expected_source": "Zakon o radu",
        "expected_article": "126",
        "notes": "Tip A. Pravo na otpremninu nakon dvije godine neprekidnog rada.",
    },
    {
        "question": "Što je probni rad i koliko najduže može trajati?",
        "expected_source": "Zakon o radu",
        "expected_article": "53",
        "notes": "Tip A. Probni rad ne smije trajati duže od šest mjeseci.",
    },
    {
        "question": "Što je izvanredni otkaz ugovora o radu?",
        "expected_source": "Zakon o radu",
        "expected_article": "116",
        "notes": "Tip A. Izvanredni otkaz zbog osobito teške povrede obveze.",
    },
    {
        "question": "Što je kolektivni ugovor?",
        "expected_source": "Zakon o radu",
        "expected_article": "192",
        "notes": "Tip A. PROVJERITI — definicija i sadržaj kolektivnog ugovora.",
    },
    {
        "question": "Što je poslovno uvjetovani otkaz?",
        "expected_source": "Zakon o radu",
        "expected_article": "115",
        "notes": "Tip A. Opravdani razlozi za redoviti otkaz.",
    },
    {
        "question": "Što se smatra noćnim radom?",
        "expected_source": "Zakon o radu",
        "expected_article": "69",
        "notes": "Tip A. Noćni rad između 22 i 6 sati.",
    },
    {
        "question": "Što je nepuno radno vrijeme?",
        "expected_source": "Zakon o radu",
        "expected_article": "62",
        "notes": "Tip A. Svako radno vrijeme kraće od punog radnog vremena.",
    },

    # ═══════════ B: svakodnevni jezik (7) ═══════════
    {
        "question": "Kada mi poslodavac mora isplatiti plaću?",
        "expected_source": "Zakon o radu",
        "expected_article": "92",
        "notes": "Tip B. Plaća se isplaćuje nakon obavljenog rada.",
    },
    {
        "question": "Mora li radnik obavijestiti poslodavca da je na bolovanju?",
        "expected_source": "Zakon o radu",
        "expected_article": "37",
        "notes": "Tip B. Obveza obavještavanja o privremenoj nesposobnosti za rad.",
    },
    {
        "question": "Moram li raditi duže ako mi to poslodavac naredi?",
        "expected_source": "Zakon o radu",
        "expected_article": "65",
        "notes": "Tip B. Prekovremeni rad na pisani zahtjev poslodavca.",
    },
    {
        "question": "Smije li me poslodavac ne zaposliti zato što sam trudna?",
        "expected_source": "Zakon o radu",
        "expected_article": "30",
        "notes": "Tip B. Zabrana odbijanja zapošljavanja zbog trudnoće.",
    },
    {
        "question": "Što se događa ako sud utvrdi da mi otkaz nije bio zakonit?",
        "expected_source": "Zakon o radu",
        "expected_article": "125",
        "notes": "Tip B. PROVJERITI — sudski raskid ugovora i naknada.",
    },
    {
        "question": "Mogu li se vratiti na posao nakon duže ozljede?",
        "expected_source": "Zakon o radu",
        "expected_article": "40",
        "notes": "Tip B. PROVJERITI — povratak na rad nakon privremene nesposobnosti.",
    },
    {
        "question": "Što ako me poslodavac pošalje raditi u drugu državu?",
        "expected_source": "Zakon o radu",
        "expected_article": "18",
        "notes": "Tip B. PROVJERITI — privremeno upućivanje na rad u inozemstvo.",
    },

    # ═══════════ C: morfološki zahtjevna (8) ═══════════
    {
        "question": "Koliko dana godišnjeg odmora ima radnik?",
        "expected_source": "Zakon o radu",
        "expected_article": "77",
        "notes": "Tip C. Genitiv 'odmora'; najmanje četiri tjedna.",
    },
    {
        "question": "Koliko traje otkazni rok?",
        "expected_source": "Zakon o radu",
        "expected_article": "122",
        "notes": "Tip C. Trajanje otkaznog roka ovisno o stažu.",
    },
    {
        "question": "Koliko iznosi puno radno vrijeme radnika?",
        "expected_source": "Zakon o radu",
        "expected_article": "61",
        "notes": "Tip C. Najviše 40 sati tjedno.",
    },
    {
        "question": "Ima li radnik pravo na stanku tijekom radnog dana?",
        "expected_source": "Zakon o radu",
        "expected_article": "73",
        "notes": "Tip C. Stanka od najmanje 30 minuta.",
    },
    {
        "question": "Koliko najduže može trajati ugovor o radu na određeno vrijeme?",
        "expected_source": "Zakon o radu",
        "expected_article": "12",
        "notes": "Tip C. Ograničenja ugovora na određeno vrijeme.",
    },
    {
        "question": "Kolika je naknada plaće za vrijeme godišnjeg odmora?",
        "expected_source": "Zakon o radu",
        "expected_article": "81",
        "notes": "Tip C. Naknada u visini prosječne mjesečne plaće.",
    },
    {
        "question": "Kako se utvrđuje broj dana godišnjeg odmora?",
        "expected_source": "Zakon o radu",
        "expected_article": "79",
        "notes": "Tip C. PROVJERITI — utvrđivanje brojem radnih dana.",
    },
    {
        "question": "Kada poslodavac mora dostaviti obračun plaće?",
        "expected_source": "Zakon o radu",
        "expected_article": "93",
        "notes": "Tip C. PROVJERITI — najkasnije petnaest dana od isplate.",
    },

    # ═══════════ D: višedijelna pitanja (6) ═══════════
    {
        "question": "Koje obveze ima poslodavac prije donošenja odluke o poslovno uvjetovanom otkazu?",
        "expected_source": "Zakon o radu",
        "expected_article": "115",
        "notes": "Tip D. Obuhvaća i čl. 127. o savjetovanju s radničkim vijećem.",
    },
    {
        "question": "Što mora sadržavati ugovor o radu i u kojem obliku se sklapa?",
        "expected_source": "Zakon o radu",
        "expected_article": "15",
        "notes": "Tip D. Obvezni sadržaj ugovora o radu.",
    },
    {
        "question": "Kako se utvrđuje raspored korištenja godišnjeg odmora i mora li radnik biti obaviješten?",
        "expected_source": "Zakon o radu",
        "expected_article": "85",
        "notes": "Tip D. Raspored korištenja i obveza obavještavanja.",
    },
    {
        "question": "Koja prava ima radnik kada mu prestane ugovor o radu?",
        "expected_source": "Zakon o radu",
        "expected_article": "126",
        "notes": "Tip D. Široko pitanje; obuhvaća otpremninu, otkazni rok i potvrdu.",
    },
    {
        "question": "Koje obveze ima poslodavac pri zapošljavanju maloljetnika?",
        "expected_source": "Zakon o radu",
        "expected_article": "21",
        "notes": "Tip D. PROVJERITI — ograničenja zapošljavanja maloljetnika.",
    },
    {
        "question": "Kada se poslodavac mora savjetovati s radničkim vijećem prije otkaza?",
        "expected_source": "Zakon o radu",
        "expected_article": "127",
        "notes": "Tip D. PROVJERITI — savjetovanje pri kolektivnom zbrinjavanju viška.",
    },

    # ═══════════ E: izvan opsega korpusa (2, kontrolna) ═══════════
    {
        "question": "Kada radnica ima pravo na rodiljni dopust?",
        "expected_source": None,
        "expected_article": None,
        "notes": (
            "Tip E — kontrolno. Čl. 33. upućuje na poseban propis; Zakon o radu "
            "sam ne uređuje uvjete stjecanja rodiljnih prava. Sustav bi trebao "
            "priznati da nema dovoljno informacija."
        ),
    },
    {
        "question": "Koliko iznosi minimalna plaća u Republici Hrvatskoj?",
        "expected_source": None,
        "expected_article": None,
        "notes": (
            "Tip E — kontrolno. Iznos minimalne plaće uređuje se posebnim "
            "propisom i uredbom Vlade, ne Zakonom o radu."
        ),
    },
]


def seed_test_questions(db: Session) -> int:
    """Ubacuje testna pitanja ako ih nema. Vraća broj ubačenih."""
    inserted = 0
    for q in TEST_QUESTIONS:
        exists = (
            db.query(EvaluationQuestion)
            .filter(EvaluationQuestion.question == q["question"])
            .first()
        )
        if not exists:
            db.add(EvaluationQuestion(**q))
            inserted += 1
    db.commit()
    return inserted