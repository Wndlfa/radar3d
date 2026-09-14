import type { Metadata } from "next";
import "./globals.css";
import { getMe, getUsage } from "@/lib/session";
import { Sidebar } from "@/components/Sidebar";

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
        <div className="min-h-screen md:flex">
          <Sidebar
            email={me?.email}
            plan={me?.plan}
            used={usage?.used}
            limit={usage?.limit}
          />
          <main className="min-w-0 flex-1 px-4 py-6 md:px-8 md:py-8">
            <div className="mx-auto max-w-5xl">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
