import Link from "next/link";
import type { Product } from "@/lib/types";
import { LicenseSummary, verdictColor } from "./LicenseSummary";

// Visão em lista (densa): tudo numa linha. Complementa o ProductCard (grid).
export function ProductRow({ product }: { product: Product }) {
  const spine = product.models_count ? verdictColor(product.best_license_tier) : "var(--border)";
  return (
    <Link
      href={`/produto/${product.id}`}
      className="group relative flex items-center gap-4 overflow-hidden rounded-lg border border-border bg-surface p-3 pl-4 shadow-card transition hover:border-accent"
    >
      <span aria-hidden className="absolute inset-y-0 left-0 w-1" style={{ background: spine }} />
      <div className="h-12 w-12 flex-shrink-0 overflow-hidden rounded bg-surface-2">
        {product.image_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={product.image_url} alt="" className="h-full w-full object-cover" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate font-display font-semibold leading-tight">{product.title}</p>
        <p className="font-mono text-xs text-muted tabular-nums">
          {product.price_brl != null && `R$ ${product.price_brl.toFixed(2)}`}
          {product.public_sales != null && ` · ${product.public_sales} vendas`}
        </p>
      </div>
      <div className="hidden flex-shrink-0 sm:block">
        <LicenseSummary
          tier={product.best_license_tier}
          modelsCount={product.models_count}
          protectedIp={product.protected_ip}
        />
      </div>
    </Link>
  );
}
