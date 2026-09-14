"use client";

import Link from "next/link";
import { useState } from "react";
import { useFavorites } from "@/lib/favorites";
import { ProductCard } from "@/components/ProductCard";
import { ProductRow } from "@/components/ProductRow";

export default function Favoritos() {
  const products = useFavorites();
  const [view, setView] = useState<"grid" | "list">("grid");

  return (
    <div>
      <div className="mb-6">
        <p className="text-sm text-muted">Sua lista</p>
        <h1 className="font-display text-2xl font-bold tracking-tight">Favoritos</h1>
        <p className="mt-1 text-sm text-muted">
          Produtos que você salvou para acompanhar. Ficam guardados neste
          navegador.
        </p>
      </div>

      {products.length > 0 && (
        <div className="mb-4 flex items-center justify-between">
          <span className="text-xs uppercase tracking-wider text-faint">
            {products.length} salvo{products.length === 1 ? "" : "s"}
          </span>
          <div className="flex items-center gap-0.5 rounded-md border border-border p-0.5">
            <button onClick={() => setView("grid")} aria-label="Grade"
              className={`rounded p-1.5 ${view === "grid" ? "bg-surface-2 text-text" : "text-muted"}`}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                <rect x="3" y="3" width="8" height="8" rx="1" /><rect x="13" y="3" width="8" height="8" rx="1" />
                <rect x="3" y="13" width="8" height="8" rx="1" /><rect x="13" y="13" width="8" height="8" rx="1" />
              </svg>
            </button>
            <button onClick={() => setView("list")} aria-label="Lista"
              className={`rounded p-1.5 ${view === "list" ? "bg-surface-2 text-text" : "text-muted"}`}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                <rect x="3" y="4" width="18" height="3" rx="1" /><rect x="3" y="10.5" width="18" height="3" rx="1" />
                <rect x="3" y="17" width="18" height="3" rx="1" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {products.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface p-10 text-center">
          <p className="font-display text-lg font-semibold">Nada salvo ainda</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted">
            Toque no marcador dos produtos na busca para guardá-los aqui e
            acompanhar as oportunidades.
          </p>
          <Link
            href="/"
            className="mt-4 inline-block rounded-md bg-accent px-4 py-2 text-sm font-semibold text-[#04222a] hover:bg-accent-hover"
          >
            Ir para a busca
          </Link>
        </div>
      ) : view === "grid" ? (
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
