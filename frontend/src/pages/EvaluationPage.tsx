import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Loader2, Play } from "lucide-react";
import { getEvaluationQuestions, runEvaluation } from "../api/client";
import type { EvaluationRunResponse } from "../types";
import PageHeader from "../components/PageHeader";

const methodLabels: Record<string, string> = {
  keyword: "Keyword",
  vector: "Vector",
  hybrid: "Hybrid",
};

function pct(v: number | null | undefined) {
  return v == null ? "—" : (v * 100).toFixed(1) + " %";
}

export default function EvaluationPage() {
  const [topK, setTopK] = useState(5);

  const { data: questions } = useQuery({
    queryKey: ["evaluation-questions"],
    queryFn: getEvaluationQuestions,
  });

  const runMutation = useMutation<EvaluationRunResponse, Error, void>({
    mutationFn: () => runEvaluation(topK),
  });

  const run = runMutation.data;
  const bestMrr = run ? Math.max(...run.summaries.map((s) => s.avg_mrr)) : 0;

  return (
    <div>
      <PageHeader
        eyebrow="Evaluacija retrievala"
        title="Usporedba metoda pretraživanja"
        description="Precision@k, Recall@k i MRR nad skupom testnih pitanja — usporedba keyword, vector i hybrid pretrage."
        actions={
          <div className="flex items-end gap-3">
            <div>
              <label htmlFor="eval-topk" className="mb-1 block text-xs font-medium text-ink/60">
                Top-k
              </label>
              <select
                id="eval-topk"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none"
              >
                {[3, 5, 10].map((k) => (
                  <option key={k} value={k}>
                    {k}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
              className="btn-primary"
            >
              {runMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
              Pokreni evaluaciju
            </button>
          </div>
        }
      />

      {runMutation.isError && (
        <p className="mb-6 text-sm text-confidence-low">
          Evaluacija nije uspjela. Provjerite je li korpus ingestan i backend dostupan.
        </p>
      )}

      {run && (
        <section className="mb-10" aria-labelledby="summary-heading">
          <h2 id="summary-heading" className="mb-3 font-display text-lg font-semibold">
            Sažetak po metodama <span className="text-sm font-normal text-ink/50">(k = {run.top_k})</span>
          </h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {run.summaries.map((s) => (
              <div
                key={s.method}
                className={`card p-5 ${s.avg_mrr === bestMrr ? "border-bronze/60 ring-1 ring-bronze/30" : ""}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-display text-base font-semibold">{methodLabels[s.method] ?? s.method}</span>
                  {s.avg_mrr === bestMrr && (
                    <span className="article-stamp">najbolji MRR</span>
                  )}
                </div>
                <dl className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-ink/60">Precision@{run.top_k}</dt>
                    <dd className="font-mono font-medium">{pct(s.avg_precision_at_k)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink/60">Recall@{run.top_k}</dt>
                    <dd className="font-mono font-medium">{pct(s.avg_recall_at_k)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-ink/60">MRR</dt>
                    <dd className="font-mono font-medium">{s.avg_mrr.toFixed(3)}</dd>
                  </div>
                  <div className="flex justify-between border-t border-line pt-2">
                    <dt className="text-ink/60">Pitanja</dt>
                    <dd className="font-mono">{s.num_questions}</dd>
                  </div>
                </dl>
              </div>
            ))}
          </div>
        </section>
      )}

      {run && (
        <section className="mb-10" aria-labelledby="detail-heading">
          <h2 id="detail-heading" className="mb-3 font-display text-lg font-semibold">
            Rezultati po pitanjima
          </h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-ink/50">
                  <th className="px-4 py-3 font-medium">Pitanje</th>
                  <th className="px-4 py-3 font-medium">Metoda</th>
                  <th className="px-4 py-3 text-right font-medium">P@k</th>
                  <th className="px-4 py-3 text-right font-medium">R@k</th>
                  <th className="px-4 py-3 text-right font-medium">MRR</th>
                </tr>
              </thead>
              <tbody>
                {run.results.map((r) => (
                  <tr key={r.id} className="border-b border-line last:border-0 hover:bg-paper">
                    <td className="max-w-md px-4 py-2.5">{r.question}</td>
                    <td className="px-4 py-2.5">
                      <span className="rounded bg-primary-light px-2 py-0.5 font-mono text-xs text-primary">
                        {r.method}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono">{pct(r.precision_at_k)}</td>
                    <td className="px-4 py-2.5 text-right font-mono">{pct(r.recall_at_k)}</td>
                    <td className="px-4 py-2.5 text-right font-mono">{r.mrr?.toFixed(3) ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section aria-labelledby="questions-heading">
        <h2 id="questions-heading" className="mb-3 font-display text-lg font-semibold">
          Testna pitanja{" "}
          <span className="text-sm font-normal text-ink/50">({questions?.length ?? 0})</span>
        </h2>
        {!questions?.length ? (
          <p className="text-sm text-ink/60">
            Nema testnih pitanja — pokrenite seed ingestiju na stranici Dokumenti.
          </p>
        ) : (
          <div className="space-y-2">
            {questions.map((q) => (
              <div key={q.id} className="card flex flex-wrap items-center gap-3 px-4 py-3 text-sm">
                <span className="font-mono text-xs text-ink/40">#{q.id}</span>
                <span className="flex-1">{q.question}</span>
                {q.expected_article && <span className="article-stamp">očekivano: čl. {q.expected_article}.</span>}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
