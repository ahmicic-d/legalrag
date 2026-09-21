import { ExternalLink, FileText } from "lucide-react";
import type { Source } from "../types";

/**
 * Kartica izvora — vizualno stilizirana poput unosa u službenom glasilu:
 * brončana lijeva linija, mono "žig" s brojem članka, serifni naslov.
 */
export default function SourceCard({ source }: { source: Source }) {
  return (
    <div className="card flex items-start gap-3 border-l-[3px] border-l-bronze p-4">
      <div className="mt-0.5 text-primary">
        <FileText size={18} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-display text-sm font-semibold">{source.document_title}</span>
          {source.article_number && (
            <span className="article-stamp">
              čl. {source.article_number}.
              {source.paragraph_number ? ` st. ${source.paragraph_number}.` : ""}
            </span>
          )}
        </div>
        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink/55">
          <span>{source.source}</span>
          <span className="capitalize">{source.document_type.replace("_", " ")}</span>
          {source.legal_area && <span>{source.legal_area}</span>}
        </div>
        {source.source_url && (
          <a
            href={source.source_url}
            target="_blank"
            rel="noreferrer"
            className="mt-1.5 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
          >
            Otvori izvorni dokument <ExternalLink size={12} />
          </a>
        )}
      </div>
    </div>
  );
}
