"use client";

import type { Product } from "@/lib/types";
import { toggleFavorite, useIsFavorite } from "@/lib/favorites";

// Botão de salvar (bookmark). Fica sobre um card que é um <Link>, então
// preventDefault/stopPropagation impedem a navegação ao clicar.
export function SaveButton({
  product,
  variant = "icon",
}: {
  product: Product;
  variant?: "icon" | "full";
}) {
  const saved = useIsFavorite(product.id);

  function onClick(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    toggleFavorite(product);
  }

  const icon = (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill={saved ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1Z" />
    </svg>
  );

  if (variant === "full") {
    return (
      <button
        onClick={onClick}
        aria-pressed={saved}
        className={`inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
          saved
            ? "border-accent text-accent"
            : "border-border text-muted hover:text-text"
        }`}
      >
        {icon}
        {saved ? "Salvo" : "Salvar"}
      </button>
    );
  }

  return (
    <button
      onClick={onClick}
      aria-pressed={saved}
      aria-label={saved ? "Remover dos favoritos" : "Salvar nos favoritos"}
      title={saved ? "Remover dos favoritos" : "Salvar"}
      className={`grid h-8 w-8 place-items-center rounded-md border backdrop-blur transition-colors ${
        saved
          ? "border-accent bg-surface/80 text-accent"
          : "border-border bg-surface/70 text-muted hover:text-text"
      }`}
    >
      {icon}
    </button>
  );
}
