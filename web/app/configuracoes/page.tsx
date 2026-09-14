import Link from "next/link";
import { getMe, getUsage } from "@/lib/session";

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-border py-3 last:border-0">
      <span className="text-sm text-muted">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  );
}

export default async function Configuracoes() {
  const me = await getMe();
  const usage = me ? await getUsage() : null;

  if (!me) {
    return (
      <div className="mx-auto max-w-md text-center">
        <h1 className="font-display text-2xl font-bold tracking-tight">Configurações</h1>
        <p className="mt-2 text-sm text-muted">Entre para ver e ajustar sua conta.</p>
        <Link
          href="/login"
          className="mt-4 inline-block rounded-md bg-accent px-4 py-2 text-sm font-semibold text-[#04222a] hover:bg-accent-hover"
        >
          Entrar / criar conta
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl">
      <div className="mb-6">
        <p className="text-sm text-muted">Sua conta</p>
        <h1 className="font-display text-2xl font-bold tracking-tight">Configurações</h1>
      </div>

      <section className="rounded-lg border border-border bg-surface p-4 shadow-card">
        <h2 className="mb-1 font-display font-semibold">Conta</h2>
        <Field label="E-mail" value={me.email} />
        <Field
          label="Plano"
          value={
            <span className="rounded-full border border-accent px-2 py-0.5 text-xs capitalize text-accent">
              {me.plan}
            </span>
          }
        />
        <Field
          label="Consultas este mês"
          value={
            usage?.limit != null ? `${usage.used}/${usage.limit}` : "ilimitadas"
          }
        />
      </section>

      <p className="mt-4 text-xs text-faint">
        Cobrança e planos pagos, tema claro/escuro e alertas chegam em breve.
      </p>
    </div>
  );
}
