# LegalRag

**Inteligentni sustav za pretraživanje hrvatskih pravnih dokumenata temeljen na RAG arhitekturi**

Prototip razvijen u sklopu diplomskog rada *„Inteligentni sustavi za pretraživanje pravnih dokumenata temeljeni na RAG arhitekturi"*. Sustav omogućuje postavljanje pravnih pitanja prirodnim jezikom (fokus: radno pravo, Zakon o radu), dohvaća relevantne članke iz korpusa i generira odgovor s citiranim izvorima.

> ⚖️ **Pravna napomena:** odgovori sustava informativnog su karaktera i ne predstavljaju pravni savjet.

---

## Arhitektura

```
korisnik ──> React frontend ──> FastAPI backend ──┬─> PostgreSQL + pgvector (retrieval)
                                                  └─> LLM (Ollama / OpenAI-kompatibilan API)
```

**Pipeline:** dohvat dokumenta (Narodne novine / EUR-Lex / lokalno) → čišćenje HTML-a → chunkiranje zakona **po člancima** (sudske odluke po odlomcima) → SentenceTransformers embeddinzi → pgvector (HNSW, kosinusna sličnost) → keyword / vector / hybrid (RRF) retrieval → LLM generira odgovor **isključivo iz konteksta**, s citiranim izvorima i confidence oznakom.

## Tehnologije

| Sloj | Tehnologije |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, PostgreSQL + pgvector, SentenceTransformers, httpx |
| LLM | Ollama ili bilo koji OpenAI-kompatibilan API (bez hardkodiranih ključeva) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, TanStack Query, Axios, React Router, Lucide |
| DevOps | Docker Compose, .env konfiguracija |

## Pokretanje (Docker Compose)

```bash
# 1. Konfiguracija
cp .env.example .env         # po potrebi uredite LLM postavke

# 2. Pokretanje svih servisa (db, backend, frontend, ollama)
docker compose up --build -d

# 3. Preuzimanje LLM modela u Ollamu (jednokratno)
docker exec -it legalrag-ollama ollama pull llama3.1

# 4. Ingestija korpusa (Zakon o radu + evaluacijska pitanja)
curl -X POST http://localhost:8000/api/ingest/seed
```

Zatim otvorite:

- **Frontend:** http://localhost:5173
- **API dokumentacija (Swagger):** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

> Prva ingestija traje nešto duže jer se preuzima embedding model (~500 MB).
> Umjesto Ollame možete koristiti vanjski API — u `.env` postavite `LLM_BASE_URL`, `LLM_MODEL` i `LLM_API_KEY`.

## Pokretanje bez Dockera (razvoj)

```bash
# Baza (potrebna pgvector ekstenzija)
docker compose up -d db

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=postgresql+psycopg://legalrag:legalrag@localhost:5432/legalrag \
LLM_BASE_URL=http://localhost:11434/v1 \
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## API endpointi

| Metoda | Putanja | Opis |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/query` | Pretraga: `{question, search_type: keyword\|vector\|hybrid\|rag, top_k}` |
| GET | `/api/documents` | Popis dokumenata s brojem chunkova |
| GET | `/api/documents/{id}` | Detalji dokumenta |
| POST | `/api/ingest/seed` | Pokreće ingestion pipeline (seed korpus + testna pitanja) |
| GET | `/api/evaluation/questions` | Testna pitanja |
| POST | `/api/evaluation/run` | Pokreće evaluaciju (P@k, R@k, MRR za keyword/vector/hybrid) |
| GET | `/api/evaluation/results` | Povijest evaluacijskih rezultata |

Primjer:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Koliko dana godišnjeg odmora ima radnik?", "search_type": "rag", "top_k": 5}'
```

## Struktura projekta

```
backend/app/
  main.py  config.py  database.py  models.py  schemas.py
  api/         query.py  documents.py  ingestion.py  evaluation.py
  rag/         embeddings.py  retriever.py  generator.py  prompts.py  hybrid_search.py
  ingestion/   seed_documents.py  fetch_nn.py  parse_html.py  clean_text.py
               chunk_legal_text.py  embed_documents.py
  evaluation/  metrics.py  test_questions.py
frontend/src/
  api/  components/  pages/  types/  App.tsx  main.tsx  index.css
db/init.sql
docker-compose.yml  .env.example
```

## Baza podataka

- `legal_documents` — metapodaci i sirovi tekst dokumenata
- `legal_chunks` — chunkovi s brojem članka/stavka, JSONB metapodacima i `VECTOR` embeddingom (HNSW indeks)
- `evaluation_questions` — testna pitanja s očekivanim izvorom i člankom
- `evaluation_results` — Precision@k, Recall@k i MRR po metodi

## Evaluacija

Stranica **Evaluacija** (ili `POST /api/evaluation/run`) pokreće 10 testnih pitanja iz radnog prava nad sve tri retrieval metode i prikazuje usporedbu prosječnog Precision@k, Recall@k i MRR-a. Relevantnost chunka definirana je podudaranjem očekivanog dokumenta i broja članka.

## Proširenje korpusa

Novi dokumenti (povezani propisi NN, sudske odluke, odluke Ustavnog suda, EUR-Lex) dodaju se u `backend/app/ingestion/seed_documents.py` u listu `SEED_DOCUMENTS`, nakon čega se ponovno pozove `POST /api/ingest/seed`. Strategija chunkiranja bira se automatski prema `document_type`.
