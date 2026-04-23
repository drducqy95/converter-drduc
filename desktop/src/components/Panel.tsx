import React from "react";

export function Panel(props: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <section className="panel">
      <header className="panel-head">
        <div>
          <h3>{props.title}</h3>
          <p>{props.subtitle}</p>
        </div>
        {props.actions ? <div className="panel-actions">{props.actions}</div> : null}
      </header>
      {props.children}
    </section>
  );
}

export function MetricCard(props: { label: string; value: number | string; tone?: string }) {
  return (
    <article className={`metric-card ${props.tone ? `metric-${props.tone}` : ""}`}>
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </article>
  );
}

export function InfoLine(props: { label: string; value: string }) {
  return (
    <div className="info-line">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}
