// Marca do Radar3D: um disco de radar com sweep girando (a "varredura" do
// mercado) sobre um alvo. Assinatura sutil da identidade.
export function RadarMark() {
  return (
    <span className="radar-sweep relative flex h-7 w-7 items-center justify-center overflow-hidden rounded-full border border-border bg-surface-2">
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
        <circle cx="12" cy="12" r="9" fill="none" stroke="var(--accent)" strokeWidth="1" opacity="0.55" />
        <circle cx="12" cy="12" r="5" fill="none" stroke="var(--accent)" strokeWidth="1" opacity="0.4" />
        <circle cx="12" cy="12" r="1.6" fill="var(--accent)" />
      </svg>
    </span>
  );
}
