// Sparkline em SVG puro (sem lib). Escala os valores no viewBox e mantém o
// traço nítido com vector-effect. Um ponto = só a bolinha; nenhum = nada.
const W = 100;
const H = 28;
const PAD = 3;

export function Sparkline({
  values,
  color = "var(--accent)",
  className = "",
}: {
  values: number[];
  color?: string;
  className?: string;
}) {
  const pts = values.filter((v) => Number.isFinite(v));
  if (pts.length === 0) return null;

  const min = Math.min(...pts);
  const max = Math.max(...pts);
  const flat = max === min; // um ponto ou valores iguais → linha no meio
  const span = max - min || 1;
  const n = pts.length;

  const x = (i: number) => (n === 1 ? W / 2 : PAD + (i / (n - 1)) * (W - PAD * 2));
  const y = (v: number) => (flat ? H / 2 : H - PAD - ((v - min) / span) * (H - PAD * 2));

  const line = pts.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  const area = `${PAD},${H} ${line} ${W - PAD},${H}`;
  const lastX = x(n - 1);
  const lastY = y(pts[n - 1]);

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      className={className}
      style={{ color }}
      aria-hidden
    >
      {n > 1 && (
        <polygon points={area} fill="currentColor" opacity={0.12} />
      )}
      {n > 1 && (
        <polyline
          points={line}
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          strokeLinejoin="round"
          strokeLinecap="round"
          vectorEffect="non-scaling-stroke"
        />
      )}
      <circle cx={lastX} cy={lastY} r={2} fill="currentColor" />
    </svg>
  );
}
