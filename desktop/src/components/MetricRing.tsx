export function MetricRing(props: {
  label: string;
  value: number;
  suffix?: string;
  tone?: "accent" | "warm";
}) {
  const bounded = Math.max(0, Math.min(100, props.value));
  const angle = `${bounded * 3.6}deg`;
  return (
    <article className="metric-ring-card">
      <div
        className={`metric-ring ${props.tone === "warm" ? "warm" : ""}`}
        style={{ background: `conic-gradient(var(--ring-fill) ${angle}, rgba(32, 48, 61, 0.08) 0deg)` }}
      >
        <div className="metric-ring-inner">
          <strong>{bounded.toFixed(1)}</strong>
          <span>{props.suffix ?? "%"}</span>
        </div>
      </div>
      <small>{props.label}</small>
    </article>
  );
}
