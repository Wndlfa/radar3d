"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { RadarMark } from "./RadarMark";
import { useFavorites } from "@/lib/favorites";

// --- Ícones (traço, herdam currentColor) ------------------------------------
const iconProps = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.9,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

function SearchIcon() {
  return (
    <svg {...iconProps}>
      <circle cx="11" cy="11" r="7" />
      <line x1="21" y1="21" x2="16.5" y2="16.5" />
    </svg>
  );
}
function HeartIcon() {
  return (
    <svg {...iconProps}>
      <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1Z" />
    </svg>
  );
}
function TrendIcon() {
  return (
    <svg {...iconProps}>
      <polyline points="3 17 9 11 13 15 21 7" />
      <polyline points="15 7 21 7 21 13" />
    </svg>
  );
}
function GearIcon() {
  return (
    <svg {...iconProps}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z" />
    </svg>
  );
}
function PlusIcon() {
  return (
    <svg {...iconProps}>
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}
function LogoutIcon() {
  return (
    <svg {...iconProps}>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}
function ChevronIcon() {
  return (
    <svg {...iconProps} width={16} height={16}>
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

// --- Item de navegação ------------------------------------------------------
function NavItem({
  href,
  label,
  icon,
  active,
  badge,
}: {
  href: string;
  label: string;
  icon: React.ReactNode;
  active: boolean;
  badge?: number;
}) {
  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={`group relative flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
        active
          ? "bg-surface-2 text-text"
          : "text-muted hover:bg-surface-2/60 hover:text-text"
      }`}
    >
      {/* Espinha de acento — mesmo motivo dos cards de produto. */}
      <span
        aria-hidden
        className={`absolute inset-y-1.5 left-0 w-0.5 rounded-full bg-accent transition-opacity ${
          active ? "opacity-100" : "opacity-0"
        }`}
      />
      <span className={active ? "text-accent" : ""}>{icon}</span>
      <span className="flex-1">{label}</span>
      {badge != null && badge > 0 && (
        <span className="rounded-full bg-surface px-1.5 text-xs font-mono text-faint">
          {badge}
        </span>
      )}
    </Link>
  );
}

// --- Bloco de perfil + dropdown --------------------------------------------
function ProfileMenu({
  email,
  plan,
  used,
  limit,
  direction = "up",
}: {
  email?: string;
  plan?: string;
  used?: number;
  limit?: number | null;
  direction?: "up" | "down";
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onClick);
    };
  }, [open]);

  if (!email) {
    return (
      <Link
        href="/login"
        className="flex items-center justify-center gap-2 rounded-md border border-border px-3 py-2.5 text-sm font-medium text-muted transition-colors hover:border-accent hover:text-text"
      >
        Entrar / criar conta
      </Link>
    );
  }

  const initials = email.slice(0, 2).toUpperCase();

  async function logout() {
    await fetch("/api/session", { method: "DELETE" });
    setOpen(false);
    router.push("/");
    router.refresh();
  }

  return (
    <div ref={ref} className="relative">
      {open && (
        <div
          role="menu"
          className={`absolute left-0 z-30 w-full overflow-hidden rounded-lg border border-border bg-surface shadow-pop ${
            direction === "up" ? "bottom-full mb-2" : "top-full mt-2"
          }`}
        >
          <div className="border-b border-border px-3 py-2.5">
            <p className="truncate text-sm font-medium">{email}</p>
            {limit != null ? (
              <p className="mt-0.5 font-mono text-xs text-faint">
                {used}/{limit} consultas este mês
              </p>
            ) : (
              <p className="mt-0.5 font-mono text-xs text-faint">consultas ilimitadas</p>
            )}
          </div>
          <Link
            href="/configuracoes"
            role="menuitem"
            onClick={() => setOpen(false)}
            className="flex items-center gap-2.5 px-3 py-2.5 text-sm text-muted transition-colors hover:bg-surface-2 hover:text-text"
          >
            <GearIcon />
            Configurações
          </Link>
          <button
            role="menuitem"
            onClick={logout}
            className="flex w-full items-center gap-2.5 px-3 py-2.5 text-sm text-muted transition-colors hover:bg-surface-2 hover:text-lic-red"
          >
            <LogoutIcon />
            Sair
          </button>
        </div>
      )}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-haspopup="menu"
        className="flex w-full items-center gap-2.5 rounded-md border border-border p-2 text-left transition-colors hover:border-accent/60"
      >
        <span className="grid h-8 w-8 flex-shrink-0 place-items-center rounded-md bg-accent/15 font-display text-xs font-bold text-accent">
          {initials}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-medium leading-tight">{email}</span>
          <span className="block text-xs capitalize text-muted">plano {plan}</span>
        </span>
        <span className={`text-faint transition-transform ${open ? "rotate-180" : ""}`}>
          <ChevronIcon />
        </span>
      </button>
    </div>
  );
}

// --- Sidebar ----------------------------------------------------------------
export function Sidebar(props: {
  email?: string;
  plan?: string;
  used?: number;
  limit?: number | null;
}) {
  const pathname = usePathname();
  const favorites = useFavorites();
  const favCount = favorites.length;

  const isBusca = pathname === "/" || pathname.startsWith("/produto");
  const isFav = pathname.startsWith("/favoritos");
  const isAlta = pathname.startsWith("/em-alta");

  const nav = (
    <>
      <NavItem href="/" label="Busca" icon={<SearchIcon />} active={isBusca} />
      <NavItem
        href="/favoritos"
        label="Favoritos"
        icon={<HeartIcon />}
        active={isFav}
        badge={favCount}
      />
    </>
  );

  const wordmark = (
    <Link href="/" className="flex items-center gap-2">
      <RadarMark />
      <span className="font-display text-lg font-bold tracking-tight">
        Radar<span className="text-accent">3D</span>
      </span>
    </Link>
  );

  return (
    <>
      {/* Desktop: rail à esquerda -------------------------------------------- */}
      <aside className="sticky top-0 hidden h-screen w-60 flex-shrink-0 flex-col border-r border-border bg-surface md:flex">
        <div className="px-4 pb-3 pt-5">{wordmark}</div>
        <div className="layerlines h-px w-full opacity-60" aria-hidden />

        <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-3">
          {nav}
          <div className="my-2 border-t border-border" />
          <NavItem href="/em-alta" label="Em alta" icon={<TrendIcon />} active={isAlta} />
          <Link
            href="/adicionar"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-faint transition-colors hover:bg-surface-2/60 hover:text-text"
          >
            <PlusIcon />
            <span className="flex-1">Adicionar</span>
            <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-faint">
              teste
            </span>
          </Link>
        </nav>

        <div className="border-t border-border p-3">
          <ProfileMenu {...props} />
        </div>
      </aside>

      {/* Mobile: barra no topo ----------------------------------------------- */}
      <header className="sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur md:hidden">
        <div className="flex items-center justify-between gap-3 px-4 py-2.5">
          {wordmark}
          <div className="w-44">
            <ProfileMenu {...props} direction="down" />
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-2">
          <NavItem href="/" label="Busca" icon={<SearchIcon />} active={isBusca} />
          <NavItem
            href="/favoritos"
            label="Favoritos"
            icon={<HeartIcon />}
            active={isFav}
            badge={favCount}
          />
          <NavItem href="/em-alta" label="Em alta" icon={<TrendIcon />} active={isAlta} />
        </nav>
      </header>
    </>
  );
}
