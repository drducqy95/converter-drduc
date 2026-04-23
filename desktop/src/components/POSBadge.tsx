const POS_TONE: Record<string, string> = {
  NOUN: "pos-noun",
  VERB: "pos-verb",
  ADJECTIVE: "pos-adjective",
  ADVERB: "pos-adverb",
  PARTICLE: "pos-particle",
  PREPOSITION: "pos-preposition",
  PRONOUN: "pos-pronoun",
  CONJUNCTION: "pos-conjunction",
  NUMBER: "pos-number",
};

export function POSBadge(props: { tag?: string | null; sub?: string | null }) {
  if (!props.tag) {
    return <span className="pill subtle">No POS</span>;
  }
  return (
    <span className={`pill pos-badge ${POS_TONE[props.tag] ?? "subtle"}`}>
      {props.tag}
      {props.sub ? `:${props.sub}` : ""}
    </span>
  );
}
