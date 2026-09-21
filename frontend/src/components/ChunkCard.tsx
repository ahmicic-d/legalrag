import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { RetrievedChunk } from "../types";

export default function ChunkCard({ chunk, rank }: { chunk: RetrievedChunk; rank: number }) {
  const [expanded, setExpanded] = useState(false);
  const preview = chunk.chunk_text.length > 320 && !expanded;

  return (
    <div className="card p-4">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="font-mono font-semibold text-ink/40">#{rank}</span>
        <span className="font-medium text-ink">{chunk.document_title}</span>
        {chunk.article_number && <span className="article-stamp">čl. {chunk.article_number}.</span>}
        <span className="ml-auto font-mono text-ink/50">
          score {chunk.score.toFixed(4)}
        </span>
      </div>
      <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink/80">
        {preview ? chunk.chunk_text.slice(0, 320) + "…" : chunk.chunk_text}
      </p>
      {chunk.chunk_text.length > 320 && (
        <button
          onClick={() => setExpanded((e) => !e)}
          className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
        >
          {expanded ? (
            <>
              Prikaži manje <ChevronUp size={13} />
            </>
          ) : (
            <>
              Prikaži cijeli odlomak <ChevronDown size={13} />
            </>
          )}
        </button>
      )}
    </div>
  );
}
