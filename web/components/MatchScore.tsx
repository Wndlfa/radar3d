// Medidor de correspondência (design-system.md §4). Distinto da licença.
const LEVEL_LABEL: Record<number, string> = {
  1: "Correspondência exata",
  2: "Muito semelhante",
  3: "Alternativa semelhante",
  4: "Conceito relacionado",
};

const LEVEL_COLOR: Record<number, string> = {
  1: "#2563eb",
  2: "#4f82e0",
  3: "#6b7280",
  4: "#8a94a0",
};

export function MatchScore({ score, level }: { score: number; level: number }) {
  const pct = Math.round(score * 100);
  const color = LEVEL_COLOR[level] ?? LEVEL_COLOR[4];
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-2">
        <div style={{ width: `${pct}%`, background: color }} className="h-full" />
      </div>
      <span className="font-mono text-xs text-muted">
        {pct}% · {LEVEL_LABEL[level] ?? "—"}
      </span>
    </div>
  );
}
