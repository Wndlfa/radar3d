import Link from "next/link";
import type { Product } from "@/lib/types";
import { LicenseSummary, verdictColor } from "./LicenseSummary";

export function ProductCard({ product }: { product: Product }) {
  // A espinha à esquerda codifica o veredito de licença: a lista vira um radar
  // escaneável de "posso vender?".
  const spine = product.models_count ? verdictColor(product.best_license_tier) : "var(--border)";

  return (
    <Link
      href={`/produto/${product.id}`}
      className="group relative block overflow-hidden rounded-lg border border-border bg-surface shadow-card transition hover:border-accent hover:shadow-pop"
    >
      <span
        aria-hidden
        className="absolute inset-y-0 left-0 w-1"
        style={{ background: spine }}
      />
      <div className="flex gap-3 p-4 pl-5">
        <div className="h-20 w-20 flex-shrink-0 overflow-hidden rounded bg-surface-2">
          {product.image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={product.image_url} alt="" className="h-full w-full object-cover" />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-display font-semibold leading-tight tracking-tight">
            {product.title}
          </p>
          <p className="mt-1.5 font-mono text-sm tabular-nums">
            {product.price_brl != null && (
              <span className="font-semibold">R$ {product.price_brl.toFixed(2)}</span>
            )}
            {product.public_sales != null && (
              <span className="text-muted"> · {product.public_sales} vendas</span>
            )}
            {product.trend && <span className="text-lic-green"> · ↑ {product.trend}</span>}
          </p>
          <p className="mt-0.5 text-xs text-muted">
            {product.rating != null && `★ ${product.rating} · `}
            {product.shop_name}
            {product.competitors != null && ` · ${product.competitors} concorrentes`}
          </p>
          <div className="mt-2.5">
            <LicenseSummary
              tier={product.best_license_tier}
              modelsCount={product.models_count}
              protectedIp={product.protected_ip}
            />
          </div>
        </div>
      </div>
    </Link>
  );
}
