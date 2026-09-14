import type { Metadata } from "next";
import "./globals.css";
import { getMe, getUsage } from "@/lib/session";
import { AuthNav } from "@/components/AuthNav";
import { RadarMark } from "@/components/RadarMark";

export const metadata: Metadata = {
  title: "Radar3D",
  description:
    "Descubra produtos impressos em 3D vendendo na Shopee, encontre modelos semelhantes e confira a licença para comercializar.",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const me = await getMe();
  const usage = me ? await getUsage() : null;
  return (
    <html lang="pt-BR">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <header className="border-b border-border bg-surface">
          <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-3">
            <div className="flex items-center gap-5">
              <a href="/" className="group flex items-center gap-2">
                <RadarMark />
                <span className="font-display text-lg font-bold tracking-tight">
                  Radar<span className="text-accent">3D</span>
                </span>
              </a>
              <nav className="hidden items-center gap-4 text-sm sm:flex">
                <a href="/" className="text-muted transition-colors hover:text-text">
                  Produtos
                </a>
                <a href="/em-alta" className="text-muted transition-colors hover:text-text">
                  Em alta
                </a>
              </nav>
            </div>
            <div className="flex items-center gap-3">
              <a
                href="/adicionar"
                className="rounded-md bg-accent px-3 py-1.5 text-xs font-semibold text-[#04222a] transition-colors hover:bg-accent-hover"
              >
                + Adicionar
              </a>
              <AuthNav
                email={me?.email}
                plan={me?.plan}
                used={usage?.used}
                limit={usage?.limit}
              />
            </div>
          </div>
          <div className="layerlines h-1 w-full opacity-70" aria-hidden />
        </header>
        <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
