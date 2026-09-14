// O componente mais importante do sistema (design-system.md §3).
// Sempre cor + ícone (forma) + texto. Nunca aparece sozinho sem o link à fonte.
import type { LicenseTier } from "@/lib/types";
import { LicenseIcon, WarnIcon } from "./LicenseIcon";

const TIER = {
  VENDA_PERMITIDA: { label: "Venda permitida", cls: "text-lic-green border-lic-green" },
  EXIGE_LICENCA: { label: "Exige licença", cls: "text-lic-yellow border-lic-yellow" },
  SOMENTE_PESSOAL: { label: "Somente pessoal", cls: "text-lic-red border-lic-red" },
  NAO_IDENTIFICADA: { label: "Não identificada", cls: "text-lic-gray border-lic-gray" },
} as const;

export function LicenseBadge({
  tier,
  protectedIp = false,
  checkedAt,
  raw,
}: {
  tier: LicenseTier;
  protectedIp?: boolean;
  checkedAt?: string | null;
  raw?: string | null;
}) {
  const t = TIER[tier];
  const date = checkedAt ? new Date(checkedAt).toLocaleDateString("pt-BR") : null;
  const tip = [raw, date && `Verificada em ${date} · confira na origem`]
    .filter(Boolean)
    .join(" — ");

  return (
    <span className="inline-flex flex-wrap items-center gap-1.5">
      <span
        title={tip}
        className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium ${t.cls}`}
      >
        <LicenseIcon tier={tier} />
        {t.label}
      </span>
      {protectedIp && (
        <span
          title="Possível marca ou personagem protegido — confira os direitos na origem."
          className="inline-flex items-center gap-1 rounded-full border border-lic-warn px-2 py-0.5 text-xs font-medium text-lic-warn"
        >
          <WarnIcon />
          Possível marca protegida
        </span>
      )}
    </span>
  );
}
