import Link from "next/link";
import { listTrending } from "@/lib/api";
import { getToken } from "@/lib/session";
import { LicenseSummary } from "@/components/LicenseSummary";

const PERIODS = [
  { key: "day", label: "Hoje" },
  { key: "week", label: "Semana" },
  { key: "month", label: "Mês" },
] as const;

export default async function Trending({
  searchParams,
}: {
  searchParams: { periodo?: string };
}) {
  const period = (["day", "week", "month"].includes(searchParams.periodo ?? "")
    ? searchParams.periodo
    : "week") as "day" | "week" | "month";

  let rows = [];
  let error: string | null = null;
  try {
    rows = await listTrending(period, getToken());
  } catch {
    error = "Não foi possível carregar as tendências.";
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold tracking-tight">Em alta</h1>
        <p className="mt-1 text-sm text-muted">
          Maior crescimento de vendas no período — ranqueado pelos snapshots diários.
        </p>
      </div>

      <div className="mb-4 flex justify-end">
        <div className="flex gap-1 rounded-full border border-border p-0.5">
          {PERIODS.map((p) => (
            <Link
              key={p.key}
              href={`/em-alta?periodo=${p.key}`}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                period === p.key ? "bg-accent text-[#04222a]" : "text-muted hover:text-text"
              }`}
            >
              {p.label}
            </Link>
          ))}
        </div>
      </div>

      {error && <p className="text-sm text-lic-red">{error}</p>}

      {!error && rows.length === 0 && (
        <p className="rounded-md border border-border bg-surface p-6 text-center text-sm text-muted">
          Sem dados de tendência ainda. As tendências surgem quando há histórico
          de coleta (snapshots) em mais de um momento.
        </p>
      )}

      <div className="space-y-2">
        {rows.map((r, i) => (
          <Link
            key={r.id}
            href={`/produto/${r.id}`}
            className="flex items-center gap-4 rounded-lg border border-border bg-surface p-3 shadow-card transition hover:border-accent hover:shadow-pop"
          >
            <span className="w-7 text-center font-display text-lg font-bold text-faint">
              {i + 1}
            </span>
            <div className="h-12 w-12 flex-shrink-0 overflow-hidden rounded bg-surface-2">
              {r.image_url && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={r.image_url} alt="" className="h-full w-full object-cover" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{r.title}</p>
              <p className="text-xs text-muted">
                {r.last_sales} vendas
                {r.price_brl != null && ` · R$ ${r.price_brl.toFixed(2)}`}
              </p>
              <div className="mt-1">
                <LicenseSummary
                  tier={r.best_license_tier}
                  modelsCount={r.models_count}
                  protectedIp={r.protected_ip}
                />
              </div>
            </div>
            <div className="text-right">
              <p className="font-mono font-semibold text-lic-green">
                ↑ {r.growth_pct != null ? `${(r.growth_pct * 100).toFixed(0)}%` : "—"}
              </p>
              <p className="font-mono text-xs text-faint">+{r.growth_abs} vendas</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
