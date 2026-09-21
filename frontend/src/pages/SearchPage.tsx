import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AlertTriangle, Loader2, Search, Sparkles } from "lucide-react";
import { postQuery } from "../api/client";
import type { QueryResponse, SearchType } from "../types";
import PageHeader from "../components/PageHeader";
import ConfidenceBadge from "../components/ConfidenceBadge";
import SourceCard from "../components/SourceCard";
import ChunkCard from "../components/ChunkCard";

const searchTypes: { value: SearchType; label: string; hint: string }[] = [
  { value: "keyword", label: "Keyword", hint: "Leksička full-text pretraga" },
  { value: "vector", label: "Vector", hint: "Semantička pretraga (embeddings)" },
  { value: "hybrid", label: "Hybrid", hint: "RRF fuzija keyword + vector" },
  { value: "rag", label: "RAG", hint: "Hybrid retrieval + LLM odgovor" },
];

const exampleQuestions = [
  "Koliko dana godišnjeg odmora ima radnik?",
  "Kada poslodavac može dati otkaz?",
  "Kada radnik ima pravo na otpremninu?",
  "Što ako poslodavac ne isplati plaću?",
];

export default function SearchPage() {
  const [question, setQuestion] = useState("");
  const [searchType, setSearchType] = useState<SearchType>("rag");
  const [topK, setTopK] = useState(5);

  const mutation = useMutation<QueryResponse, Error, void>({
    mutationFn: () => postQuery({ question, search_type: searchType, top_k: topK }),
  });

  const submit = () => {
    if (question.trim().length >= 3) mutation.mutate();
  };

  const result = mutation.data;

  return (
    <div>
      <PageHeader
        eyebrow="Pretraživanje korpusa"
        title="Postavite pravno pitanje"
        description="Sustav dohvaća relevantne članke iz korpusa hrvatskih pravnih dokumenata i, u RAG načinu, generira odgovor s citiranim izvorima."
      />

      <div className="card p-5">
        <label htmlFor="question" className="mb-2 block text-sm font-medium">
          Pravno pitanje
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={2}
          placeholder="npr. Koliko dana godišnjeg odmora ima radnik?"
          className="w-full resize-none rounded-md border border-line bg-paper px-3 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />

        <div className="mt-2 flex flex-wrap gap-2">
          {exampleQuestions.map((q) => (
            <button
              key={q}
              onClick={() => setQuestion(q)}
              className="rounded-full border border-line bg-paper px-3 py-1 text-xs text-ink/60 transition-colors hover:border-primary hover:text-primary"
            >
              {q}
            </button>
          ))}
        </div>

        <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
          <fieldset>
            <legend className="mb-2 text-sm font-medium">Metoda pretraživanja</legend>
            <div className="flex flex-wrap gap-2" role="radiogroup">
              {searchTypes.map((t) => (
                <button
                  key={t.value}
                  role="radio"
                  aria-checked={searchType === t.value}
                  title={t.hint}
                  onClick={() => setSearchType(t.value)}
                  className={`rounded-md border px-3.5 py-2 text-sm font-medium transition-colors ${
                    searchType === t.value
                      ? "border-primary bg-primary text-white"
                      : "border-line bg-surface text-ink/70 hover:border-primary/50"
                  }`}
                >
                  {t.value === "rag" && <Sparkles size={13} className="mr-1 inline" />}
                  {t.label}
                </button>
              ))}
            </div>
            <p className="mt-1.5 text-xs text-ink/50">
              {searchTypes.find((t) => t.value === searchType)?.hint}
            </p>
          </fieldset>

          <div className="flex items-end gap-3">
            <div>
              <label htmlFor="topk" className="mb-2 block text-sm font-medium">
                Top-k
              </label>
              <select
                id="topk"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none"
              >
                {[3, 5, 8, 10].map((k) => (
                  <option key={k} value={k}>
                    {k}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={submit}
              disabled={mutation.isPending || question.trim().length < 3}
              className="btn-primary"
            >
              {mutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
              Pretraži
            </button>
          </div>
        </div>
      </div>

      {mutation.isError && (
        <div className="card mt-6 flex items-start gap-3 border-confidence-low/40 bg-confidence-low/5 p-4 text-sm">
          <AlertTriangle size={18} className="mt-0.5 shrink-0 text-confidence-low" />
          <div>
            <p className="font-medium text-confidence-low">Pretraga nije uspjela</p>
            <p className="mt-0.5 text-ink/70">
              Provjerite je li backend pokrenut (http://localhost:8000/health) i je li korpus ingestan
              (stranica Dokumenti → Pokreni seed).
            </p>
          </div>
        </div>
      )}

      {result && (
        <div className="mt-8 space-y-8">
          {/* Odgovor */}
          <section aria-labelledby="answer-heading">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <h2 id="answer-heading" className="font-display text-lg font-semibold">
                Odgovor
              </h2>
              <div className="flex items-center gap-2">
                <span className="rounded-full border border-line bg-surface px-3 py-1 font-mono text-xs text-ink/60">
                  {result.search_type}
                </span>
                <ConfidenceBadge level={result.confidence} />
              </div>
            </div>
            <div className="card border-l-[3px] border-l-primary p-5">
              <p className="whitespace-pre-line text-[15px] leading-relaxed">{result.answer}</p>
              <p className="mt-4 border-t border-line pt-3 text-xs text-ink/50">{result.disclaimer}</p>
            </div>
          </section>

          {/* Izvori */}
          <section aria-labelledby="sources-heading">
            <h2 id="sources-heading" className="mb-3 font-display text-lg font-semibold">
              Citirani izvori <span className="text-sm font-normal text-ink/50">({result.sources.length})</span>
            </h2>
            {result.sources.length === 0 ? (
              <p className="text-sm text-ink/60">Nisu pronađeni relevantni izvori za ovo pitanje.</p>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {result.sources.map((s, i) => (
                  <SourceCard key={`${s.document_id}-${s.article_number}-${i}`} source={s} />
                ))}
              </div>
            )}
          </section>

          {/* Dohvaćeni chunkovi */}
          <section aria-labelledby="chunks-heading">
            <h2 id="chunks-heading" className="mb-3 font-display text-lg font-semibold">
              Dohvaćeni odlomci{" "}
              <span className="text-sm font-normal text-ink/50">({result.retrieved_chunks.length})</span>
            </h2>
            <div className="space-y-3">
              {result.retrieved_chunks.map((c, i) => (
                <ChunkCard key={c.chunk_id} chunk={c} rank={i + 1} />
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
