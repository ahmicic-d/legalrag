import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DatabaseZap, ExternalLink, Loader2 } from "lucide-react";
import { getDocuments, postSeed } from "../api/client";
import PageHeader from "../components/PageHeader";

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const { data: documents, isLoading, isError } = useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
  });

  const seedMutation = useMutation({
    mutationFn: postSeed,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  return (
    <div>
      <PageHeader
        eyebrow="Korpus"
        title="Dokumenti u bazi"
        description="Pravni dokumenti nad kojima sustav radi pretraživanje: zakoni iz Narodnih novina, sudske odluke i EU dokumenti."
        actions={
          <button
            onClick={() => seedMutation.mutate()}
            disabled={seedMutation.isPending}
            className="btn-secondary"
          >
            {seedMutation.isPending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <DatabaseZap size={16} />
            )}
            Pokreni seed ingestiju
          </button>
        }
      />

      {seedMutation.isSuccess && (
        <div className="card mb-6 border-confidence-high/40 bg-confidence-high/5 p-4 text-sm">
          <p className="font-medium text-confidence-high">
            Ingestija dovršena — {seedMutation.data.documents_ingested} dokumenata,{" "}
            {seedMutation.data.chunks_created} chunkova.
          </p>
          <ul className="mt-1 list-inside list-disc text-ink/70">
            {seedMutation.data.details.map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        </div>
      )}
      {seedMutation.isError && (
        <div className="card mb-6 border-confidence-low/40 bg-confidence-low/5 p-4 text-sm text-confidence-low">
          Ingestija nije uspjela. Provjerite mrežni pristup backenda prema narodne-novine.nn.hr.
        </div>
      )}

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-ink/60">
          <Loader2 size={16} className="animate-spin" /> Učitavanje dokumenata…
        </div>
      )}
      {isError && (
        <p className="text-sm text-confidence-low">
          Dokumente nije moguće učitati. Provjerite je li backend pokrenut.
        </p>
      )}

      {documents && documents.length === 0 && (
        <div className="card p-8 text-center">
          <p className="font-display text-lg font-semibold">Korpus je prazan</p>
          <p className="mx-auto mt-2 max-w-md text-sm text-ink/60">
            Pokrenite seed ingestiju kako biste dohvatili Zakon o radu iz Narodnih novina,
            chunkirali ga po člancima i generirali embeddinge.
          </p>
        </div>
      )}

      {documents && documents.length > 0 && (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-ink/50">
                <th className="px-4 py-3 font-medium">Naslov</th>
                <th className="px-4 py-3 font-medium">Tip</th>
                <th className="px-4 py-3 font-medium">Izvor</th>
                <th className="px-4 py-3 font-medium">Pravno područje</th>
                <th className="px-4 py-3 text-right font-medium">Chunkova</th>
                <th className="px-4 py-3 font-medium">URL</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-b border-line last:border-0 hover:bg-paper">
                  <td className="px-4 py-3 font-display font-semibold">{doc.title}</td>
                  <td className="px-4 py-3 capitalize text-ink/70">
                    {doc.document_type.replace("_", " ")}
                  </td>
                  <td className="px-4 py-3 text-ink/70">{doc.source}</td>
                  <td className="px-4 py-3 text-ink/70">{doc.legal_area ?? "—"}</td>
                  <td className="px-4 py-3 text-right font-mono">{doc.chunk_count}</td>
                  <td className="px-4 py-3">
                    {doc.source_url ? (
                      <a
                        href={doc.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-primary hover:underline"
                      >
                        Otvori <ExternalLink size={12} />
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
