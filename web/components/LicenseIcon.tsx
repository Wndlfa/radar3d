// Ícones de licença diferenciados por FORMA (não só cor) — herdam currentColor.
import type { LicenseTier } from "@/lib/types";

const base = {
  width: 14,
  height: 14,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2.2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

export function LicenseIcon({ tier }: { tier: LicenseTier }) {
  switch (tier) {
    case "VENDA_PERMITIDA": // ✓ pode vender
      return (
        <svg {...base}>
          <polyline points="20 6 9 17 4 12" />
        </svg>
      );
    case "EXIGE_LICENCA": // cadeado — precisa comprar licença
      return (
        <svg {...base}>
          <rect x="5" y="11" width="14" height="9" rx="2" />
          <path d="M8 11V8a4 4 0 0 1 8 0v3" />
        </svg>
      );
    case "SOMENTE_PESSOAL": // proibido vender
      return (
        <svg {...base}>
          <circle cx="12" cy="12" r="9" />
          <line x1="6.2" y1="6.2" x2="17.8" y2="17.8" />
        </svg>
      );
    default: // NAO_IDENTIFICADA — interrogação
      return (
        <svg {...base}>
          <circle cx="12" cy="12" r="9" />
          <path d="M9.2 9.3a2.8 2.8 0 0 1 5.4 1c0 1.8-2.6 2.2-2.6 3.9" />
          <line x1="12" y1="17.4" x2="12" y2="17.5" />
        </svg>
      );
  }
}

export function WarnIcon() {
  return (
    <svg {...base}>
      <path d="M12 3 22 20 2 20Z" />
      <line x1="12" y1="9.5" x2="12" y2="14" />
      <line x1="12" y1="17" x2="12" y2="17.1" />
    </svg>
  );
}
