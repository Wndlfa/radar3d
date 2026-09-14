import Link from "next/link";
import { Suspense } from "react";
import { listProducts, listKpis, type ListParams } from "@/lib/api";
import type { KpiPoint, Product } from "@/lib/types";
import { getToken } from "@/lib/session";
import { ProductCard } from "@/components/ProductCard";
import { ProductRow } from "@/components/ProductRow";
import { SearchBar } from "@/components/SearchBar";
import { Sparkline } from "@/components/Sparkline";

const SORTS = [
  { key: "sales", label: "Mais vendidos" },
  { key: "price_asc", label: "Menor preço" },
  { key: "price_desc", label: "Maior preço" },
] as const;

// 84.7k → "84,7 mil"; 1.2M → "1,2 mi"
function compact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(".", ",")} mi`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(".", ",")} mil`;
  return String(n);
}

function Stat({
  label,
  value,
  hint,
  series,
  color,
}: {
  label: string;
  value: string;
  hint?: string;
  series: number[];
  color: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4 shadow-card">
      <p className="text-xs uppercase tracking-wider text-faint">{label}</p>
      <div className="mt-1 flex items-end justify-between gap-3">
        <div>
          <p className="font-display text-2xl font-bold tracking-tight tabular-nums">{value}</p>
          {hint && <p className="mt-0.5 text-xs text-muted">{hint}</p>}
        </div>
        {series.length >= 1 && (
          <Sparkline values={series} color={color} className="h-8 w-24 flex-shrink-0" />
        )}
      </div>
      {series.length < 2 && (
        <p className="mt-1 text-[11px] text-faint">coletando histórico…</p>
      )}
    </div>
  );
}

export default async function Home({
  searchParams,
}: {
  searchParams: { comercial?: string; q?: string; sort?: string; view?: string };
}) {
  const commercialOnly = searchParams.comercial === "1";
  const q = searchParams.q ?? "";
  const sort = (["sales", "price_asc", "price_desc"].includes(searchParams.sort ?? "")
    ? searchParams.sort
    : "sales") as ListParams["sort"];
  const view = searchParams.view === "list" ? "list" : "grid";

  // Mantém os parâmetros ao alternar um controle.
  const withParam = (patch: Record<string, string | null>) => {
    const p = new URLSearchParams();
    if (commercialOnly) p.set("comercial", "1");
    if (q) p.set("q", q);
    if (sort && sort !== "sales") p.set("sort", sort);
    if (view !== "grid") p.set("view", view);
    for (const [k, v] of Object.entries(patch)) v === null ? p.delete(k) : p.set(k, v);
    const s = p.toString();
    return s ? `/?${s}` : "/";
  };

  const token = getToken();
  let products: Product[] = [];
  let error: string | null = null;
  let kpis: KpiPoint[] = [];
  try {
    [products, kpis] = await Promise.all([
      listProducts({ commercialOnly, q, sort }, token),
      listKpis(30, token),
    ]);
  } catch (e) {
    error = e instanceof Error ? e.message : "Não foi possível carregar os produtos.";
  }

  // Métricas honestas, calculadas do que está monitorado agora.
  const totalSales = products.reduce((s, p) => s + (p.public_sales ?? 0), 0);
  const vendaveis = products.filter((p) => p.commercial_available).length;

  return (
    <div>
      <div className="mb-6">
        <p className="text-sm text-muted">Radar de oportunidades</p>
        <h1 className="font-display text-2xl font-bold tracking-tight">
          Produtos 3D em alta na Shopee
        </h1>
      </div>

      {/* Hero de busca */}
      <div className="mb-4">
        <Suspense fallback={<div className="h-11 rounded-md border border-border bg-surface" />}>
          <SearchBar />
        </Suspense>
      </div>

      {/* Faixa de métricas — dados reais do que está monitorado */}
      {!error && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
          <Stat
            label="Produtos monitorados"
            value={compact(products.length)}
            series={kpis.map((k) => k.monitored)}
            color="var(--accent)"
          />
          <Stat
            label="Vendas públicas"
            value={compact(totalSales)}
            hint="somadas no radar"
            series={kpis.map((k) => k.sales)}
            color="var(--accent)"
          />
          <Stat
            label="Vendáveis"
            value={compact(vendaveis)}
            hint="com modelo comercializável"
            series={kpis.map((k) => k.sellable)}
            color="var(--lic-green)"
          />
        </div>
      )}

      {/* Controles: ordenação + filtro + view */}
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="mr-auto text-xs uppercase tracking-wider text-faint">
          {products.length} produto{products.length === 1 ? "" : "s"}
          {q && <> · busca “{q}”</>}
        </span>
        <div className="flex items-center gap-1 rounded-md border border-border p-0.5 text-xs">
          {SORTS.map((s) => (
            <Link
              key={s.key}
              href={withParam({ sort: s.key === "sales" ? null : s.key })}
              className={`rounded px-2 py-1 font-medium transition-colors ${
                sort === s.key ? "bg-surface-2 text-text" : "text-muted hover:text-text"
              }`}
            >
              {s.label}
            </Link>
          ))}
        </div>
        <Link
          href={withParam({ comercial: commercialOnly ? null : "1" })}
          className={`rounded-md border px-3 py-1.5 text-xs font-medium transition-colors ${
            commercialOnly ? "border-lic-green text-lic-green" : "border-border text-muted hover:text-text"
          }`}
        >
          {commercialOnly ? "✓ " : ""}Só vendáveis
        </Link>
        {/* Toggle grid / lista */}
        <div className="flex items-center gap-0.5 rounded-md border border-border p-0.5">
          <Link href={withParam({ view: null })} aria-label="Grade"
            className={`rounded p-1.5 ${view === "grid" ? "bg-surface-2 text-text" : "text-muted"}`}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <rect x="3" y="3" width="8" height="8" rx="1" /><rect x="13" y="3" width="8" height="8" rx="1" />
              <rect x="3" y="13" width="8" height="8" rx="1" /><rect x="13" y="13" width="8" height="8" rx="1" />
            </svg>
          </Link>
          <Link href={withParam({ view: "list" })} aria-label="Lista"
            className={`rounded p-1.5 ${view === "list" ? "bg-surface-2 text-text" : "text-muted"}`}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <rect x="3" y="4" width="18" height="3" rx="1" /><rect x="3" y="10.5" width="18" height="3" rx="1" />
              <rect x="3" y="17" width="18" height="3" rx="1" />
            </svg>
          </Link>
        </div>
      </div>

      {error && (
        <p className="rounded-md border border-border bg-surface p-4 text-sm text-lic-yellow">{error}</p>
      )}

      {!error && products.length === 0 && (
        <p className="rounded-md border border-border bg-surface p-6 text-center text-sm text-muted">
          Nenhum produto encontrado{q ? ` para “${q}”` : ""}.
        </p>
      )}

      {view === "grid" ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {products.map((p) => (
            <ProductRow key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}
