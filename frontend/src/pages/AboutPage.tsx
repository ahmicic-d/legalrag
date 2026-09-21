import { BookOpen, Cpu, Database, Scale, Workflow } from "lucide-react";
import PageHeader from "../components/PageHeader";

export default function AboutPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Diplomski rad"
        title="Inteligentni sustavi za pretraživanje pravnih dokumenata temeljeni na RAG arhitekturi"
        description="LegalRag je prototip sustava razvijen u sklopu diplomskog rada, s fokusom na hrvatsko radno pravo."
      />

      <div className="space-y-8">
        <section className="card p-6" aria-labelledby="about-work">
          <h2 id="about-work" className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
            <BookOpen size={18} className="text-primary" /> O radu
          </h2>
          <p className="text-sm leading-relaxed text-ink/80">
            Cilj rada je istražiti primjenu arhitekture Retrieval-Augmented Generation (RAG) na
            domenu hrvatskih pravnih dokumenata. Klasične metode pretraživanja pravnih tekstova
            oslanjaju se na podudaranje ključnih riječi, što slabo funkcionira kada korisnik
            postavlja pitanje prirodnim jezikom. RAG pristup kombinira semantičko dohvaćanje
            relevantnih dijelova dokumenata s generiranjem odgovora velikim jezičnim modelom,
            pri čemu je model strogo ograničen na dohvaćeni kontekst — čime se smanjuje rizik
            halucinacija, a svaki odgovor prati citirane izvore.
          </p>
        </section>

        <section className="card p-6" aria-labelledby="about-rag">
          <h2 id="about-rag" className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
            <Workflow size={18} className="text-primary" /> RAG arhitektura sustava
          </h2>
          <ol className="space-y-3 text-sm leading-relaxed text-ink/80">
            <li>
              <strong>1. Ingestija.</strong> Dokument se dohvaća s izvora (URL ili lokalna
              datoteka), HTML se čisti, a tekst zakona chunkira po člancima jer je članak
              prirodna semantička jedinica pravnog teksta. Sudske odluke chunkiraju se po
              odlomcima s preklapanjem.
            </li>
            <li>
              <strong>2. Embeddings.</strong> Svaki chunk pretvara se u vektor pomoću
              višejezičnog SentenceTransformers modela i sprema u PostgreSQL s pgvector
              ekstenzijom (HNSW indeks, kosinusna sličnost).
            </li>
            <li>
              <strong>3. Retrieval.</strong> Podržane su tri metode: <em>keyword</em>{" "}
              (PostgreSQL full-text pretraga), <em>vector</em> (semantička sličnost) i{" "}
              <em>hybrid</em> (Reciprocal Rank Fusion obiju lista rezultata).
            </li>
            <li>
              <strong>4. Generiranje.</strong> Dohvaćeni chunkovi ulaze u prompt LLM-a
              (Ollama ili OpenAI-kompatibilan API). Model smije odgovarati isključivo na
              temelju konteksta; ako kontekst nije dovoljan, eksplicitno kaže da nema dovoljno
              informacija.
            </li>
            <li>
              <strong>5. Evaluacija.</strong> Kvaliteta retrievala mjeri se metrikama
              Precision@k, Recall@k i MRR nad skupom testnih pitanja s poznatim očekivanim
              člancima.
            </li>
          </ol>
        </section>

        <section className="card p-6" aria-labelledby="about-sources">
          <h2 id="about-sources" className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
            <Database size={18} className="text-primary" /> Izvori podataka
          </h2>
          <ul className="list-inside list-disc space-y-1.5 text-sm text-ink/80">
            <li>
              <strong>Zakon o radu</strong> (NN 93/2014) — glavni dokument korpusa, Narodne novine
            </li>
            <li>Povezani propisi iz Narodnih novina (pravilnici, uredbe)</li>
            <li>Odabrane sudske odluke i odluke Ustavnog suda Republike Hrvatske</li>
            <li>EU dokumenti s EUR-Lex portala (direktive iz područja radnog prava)</li>
          </ul>
        </section>

        <section className="card p-6" aria-labelledby="about-tech">
          <h2 id="about-tech" className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
            <Cpu size={18} className="text-primary" /> Tehnologije
          </h2>
          <div className="grid gap-6 text-sm text-ink/80 sm:grid-cols-3">
            <div>
              <h3 className="mb-1.5 font-semibold text-ink">Backend</h3>
              <ul className="space-y-1">
                <li>Python + FastAPI</li>
                <li>PostgreSQL + pgvector</li>
                <li>SQLAlchemy, Pydantic</li>
                <li>SentenceTransformers</li>
                <li>Ollama / OpenAI-kompatibilan LLM</li>
              </ul>
            </div>
            <div>
              <h3 className="mb-1.5 font-semibold text-ink">Frontend</h3>
              <ul className="space-y-1">
                <li>React + TypeScript</li>
                <li>Vite</li>
                <li>Tailwind CSS</li>
                <li>TanStack Query, Axios</li>
                <li>React Router, Lucide</li>
              </ul>
            </div>
            <div>
              <h3 className="mb-1.5 font-semibold text-ink">DevOps</h3>
              <ul className="space-y-1">
                <li>Docker Compose</li>
                <li>.env konfiguracija</li>
                <li>HNSW vektorski indeks</li>
              </ul>
            </div>
          </div>
        </section>

        <section
          className="card border-l-[3px] border-l-bronze p-6"
          aria-labelledby="about-legal"
        >
          <h2 id="about-legal" className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
            <Scale size={18} className="text-bronze" /> Pravna napomena
          </h2>
          <p className="text-sm leading-relaxed text-ink/80">
            LegalRag je istraživački prototip izrađen u akademske svrhe. Odgovori sustava
            informativnog su karaktera i <strong>ne predstavljaju pravni savjet</strong>.
            Sustav može sadržavati pogreške, a propisi se mijenjaju — za konkretne pravne
            situacije uvijek se obratite odvjetniku ili nadležnom tijelu i provjerite važeći
            pročišćeni tekst propisa.
          </p>
        </section>
      </div>
    </div>
  );
}
