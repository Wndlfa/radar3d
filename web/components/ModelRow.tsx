import type { Match } from "@/lib/types";
import { LicenseBadge } from "./LicenseBadge";
import { MatchScore } from "./MatchScore";

export function ModelRow({ match }: { match: Match }) {
  const m = match.model;
  return (
    <div className="flex gap-3 rounded-md border border-border bg-surface-2 p-3">
      <div className="h-16 w-16 flex-shrink-0 overflow-hidden rounded bg-bg">
        {m.thumbnail_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={m.thumbnail_url} alt="" className="h-full w-full object-cover" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between gap-2">
          <p className="truncate font-medium">{m.title}</p>
          <span className="text-xs text-faint">{m.platform}</span>
        </div>
        <p className="text-xs text-muted">
          {m.creator ? `por ${m.creator}` : "criador desconhecido"} ·{" "}
          {m.is_paid ? (m.price_brl ? `R$ ${m.price_brl}` : "pago") : "grátis"}
          {m.downloads != null && ` · ↓ ${m.downloads.toLocaleString("pt-BR")}`}
        </p>
        <div className="mt-1.5 flex flex-wrap items-center gap-2">
          <MatchScore score={match.final_score} level={match.match_level} />
          <LicenseBadge
            tier={m.license_tier}
            protectedIp={m.possible_protected_ip}
            checkedAt={m.license_checked_at}
            raw={m.license_raw}
          />
        </div>
      </div>
      <a
        href={m.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-shrink-0 self-center rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent-hover"
      >
        Abrir modelo ↗
      </a>
    </div>
  );
}
