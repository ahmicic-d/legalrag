import type { Confidence } from "../types";

const config: Record<Confidence, { label: string; classes: string }> = {
  high: { label: "Visoka pouzdanost", classes: "bg-confidence-high/10 text-confidence-high border-confidence-high/30" },
  medium: { label: "Srednja pouzdanost", classes: "bg-confidence-medium/10 text-confidence-medium border-confidence-medium/30" },
  low: { label: "Niska pouzdanost", classes: "bg-confidence-low/10 text-confidence-low border-confidence-low/30" },
};

export default function ConfidenceBadge({ level }: { level: Confidence }) {
  const { label, classes } = config[level];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${classes}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden />
      {label}
    </span>
  );
}
