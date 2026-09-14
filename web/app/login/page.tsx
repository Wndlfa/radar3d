"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function Login() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const f = new FormData(e.currentTarget);
    const res = await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode,
        email: f.get("email"),
        password: f.get("password"),
      }),
    });
    if (res.ok) {
      router.push("/");
      router.refresh();
    } else {
      const d = await res.json().catch(() => ({}));
      setError(d?.error || "Falha na autenticação");
      setBusy(false);
    }
  }

  const field =
    "w-full rounded-md border border-border bg-bg px-3 py-2 text-sm focus:border-accent focus:outline-none";

  return (
    <div className="mx-auto max-w-sm">
      <Link href="/" className="text-sm text-accent hover:underline">
        ← Voltar
      </Link>
      <h1 className="mt-3 text-xl font-semibold">
        {mode === "login" ? "Entrar" : "Criar conta"}
      </h1>

      <form onSubmit={onSubmit} className="mt-5 space-y-3">
        <input name="email" type="email" required placeholder="e-mail" className={field} />
        <input name="password" type="password" required placeholder="senha" className={field} />
        {error && <p className="text-sm text-lic-red">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {busy ? "..." : mode === "login" ? "Entrar" : "Criar conta"}
        </button>
      </form>

      <button
        onClick={() => {
          setMode(mode === "login" ? "register" : "login");
          setError(null);
        }}
        className="mt-4 text-xs text-muted hover:text-text"
      >
        {mode === "login"
          ? "Não tem conta? Criar uma"
          : "Já tem conta? Entrar"}
      </button>
    </div>
  );
}
