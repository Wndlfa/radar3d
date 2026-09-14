// Resumo compacto da licença para listas (responde "posso vender?" num relance).
import type { LicenseTier } from "@/lib/types";
import { LicenseIcon, WarnIcon } from "./LicenseIcon";

const SUMMARY = {
  VENDA_PERMITIDA: { label: "Vendável", cls: "text-lic-green border-lic-green", color: "var(--lic-green)" },
  EXIGE_LICENCA: { label: "Licença paga", cls: "text-lic-yellow border-lic-yellow", color: "var(--lic-yellow)" },
  SOMENTE_PESSOAL: { label: "Uso pessoal", cls: "text-lic-red border-lic-red", color: "var(--lic-red)" },
  NAO_IDENTIFICADA: { label: "Licença ?", cls: "text-lic-gray border-lic-gray", color: "var(--lic-gray)" },
} as const;

export function verdictColor(tier?: LicenseTier | null): string {
  return tier ? SUMMARY[tier].color : "var(--lic-gray)";
}

export function LicenseSummary({
  tier,
  modelsCount = 0,
  protectedIp = false,
}: {
  tier?: LicenseTier | null;
  modelsCount?: number;
  protectedIp?: boolean;
}) {
  if (!modelsCount || !tier) {
    return <span className="text-xs text-faint">nenhum modelo encontrado</span>;
  }
  const s = SUMMARY[tier];
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5">
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium ${s.cls}`}
      >
        <LicenseIcon tier={tier} />
        {s.label}
      </span>
      <span className="font-mono text-xs text-faint">
        {modelsCount} modelo{modelsCount > 1 ? "s" : ""}
      </span>
      {protectedIp && (
        <span
          title="Algum modelo pode citar marca/personagem protegido — confira os direitos."
          className="inline-flex items-center gap-1 rounded-full border border-lic-warn px-2 py-0.5 text-xs font-medium text-lic-warn"
        >
          <WarnIcon />
          IP protegido?
        </span>
      )}
    </span>
  );
}
