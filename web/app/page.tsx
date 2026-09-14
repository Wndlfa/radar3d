import Link from "next/link";
import { Suspense } from "react";
import { listProducts, type ListParams } from "@/lib/api";
import { getToken } from "@/lib/session";
import { ProductCard } from "@/components/ProductCard";
import { ProductRow } from "@/components/ProductRow";
import { SearchBar } from "@/components/SearchBar";

const SORTS = [
  { key: "sales", label: "Mais vendidos" },
  { key: "price_asc", label: "Menor preço" },
  { key: "price_desc", label: "Maior preço" },
] as const;

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

  let products = [];
  let error: string | null = null;
  try {
    products = await listProducts({ commercialOnly, q, sort }, getToken());
  } catch (e) {
    error = e instanceof Error ? e.message : "Não foi possível carregar os produtos.";
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold tracking-tight">
          Produtos 3D em alta na Shopee
        </h1>
        <p className="mt-1 max-w-xl text-sm text-muted">
          O que está vendendo — e se você pode imprimir e vender. Cada faixa
          colorida mostra a licença do modelo encontrado.
        </p>
      </div>

      {/* Barra de controles: busca + ordenação + filtro + view */}
      <div className="mb-5 flex flex-wrap items-center gap-2">
        <Suspense fallback={<div className="h-9 flex-1 rounded-md border border-border bg-surface" />}>
          <SearchBar />
        </Suspense>
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

      <div className="mb-3 text-xs uppercase tracking-wider text-faint">
        {products.length} produto{products.length === 1 ? "" : "s"}
        {q && <> · busca “{q}”</>}
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
