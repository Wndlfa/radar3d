"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

// Enquanto a busca de modelos roda no worker, a tela de detalhe recarrega
// sozinha até aparecerem resultados (ou atingir o limite de tentativas).
export function AutoRefresh({
  active,
  intervalMs = 4000,
  maxTries = 30,
}: {
  active: boolean;
  intervalMs?: number;
  maxTries?: number;
}) {
  const router = useRouter();
  const [tries, setTries] = useState(0);

  useEffect(() => {
    if (!active || tries >= maxTries) return;
    const t = setTimeout(() => {
      setTries((n) => n + 1);
      router.refresh();
    }, intervalMs);
    return () => clearTimeout(t);
  }, [active, tries, maxTries, intervalMs, router]);

  if (!active) return null;

  return (
    <div className="flex items-center gap-2 rounded-md border border-border bg-surface p-3 text-sm text-muted">
      <span className="inline-block h-3 w-3 animate-pulse rounded-full bg-accent" />
      {tries >= maxTries
        ? "Ainda sem resultados. Verifique se o worker está rodando."
        : "Buscando modelos semelhantes nas bibliotecas… atualizando sozinho."}
    </div>
  );
}
