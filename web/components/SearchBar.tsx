"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

// Busca por título. Preserva os outros parâmetros da URL (view, sort, etc.).
export function SearchBar() {
  const router = useRouter();
  const params = useSearchParams();
  const [value, setValue] = useState(params.get("q") ?? "");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const next = new URLSearchParams(params.toString());
    if (value.trim()) next.set("q", value.trim());
    else next.delete("q");
    router.push(`/?${next.toString()}`);
  }

  return (
    <form onSubmit={submit} className="relative">
      <svg
        className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-faint"
        width="18" height="18" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" aria-hidden
      >
        <circle cx="11" cy="11" r="7" />
        <line x1="21" y1="21" x2="16.5" y2="16.5" />
      </svg>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Buscar produto, nicho ou palavra-chave…"
        className="w-full rounded-lg border border-border bg-surface py-3 pl-11 pr-24 text-sm shadow-card placeholder:text-faint focus:border-accent focus:outline-none"
      />
      <button
        type="submit"
        className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-md bg-accent px-4 py-1.5 text-sm font-semibold text-[#04222a] transition-colors hover:bg-accent-hover"
      >
        Buscar
      </button>
    </form>
  );
}
