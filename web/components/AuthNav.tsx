"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

// Mostra plano + logout quando logado; link de entrar quando anônimo.
// Recebe os dados já resolvidos pelo layout (server component).
export function AuthNav({
  email,
  plan,
  used,
  limit,
}: {
  email?: string;
  plan?: string;
  used?: number;
  limit?: number | null;
}) {
  const router = useRouter();

  if (!email) {
    return (
      <Link
        href="/login"
        className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-muted hover:text-text"
      >
        Entrar
      </Link>
    );
  }

  async function logout() {
    await fetch("/api/session", { method: "DELETE" });
    router.push("/");
    router.refresh();
  }

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="rounded-full border border-accent px-2 py-0.5 font-medium capitalize text-accent">
        {plan}
      </span>
      {limit != null && (
        <span className="text-faint" title="Consultas usadas este mês">
          {used}/{limit}
        </span>
      )}
      <span className="hidden text-muted sm:inline">{email}</span>
      <button onClick={logout} className="text-muted hover:text-text">
        sair
      </button>
    </div>
  );
}
