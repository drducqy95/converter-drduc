const ENTITY_META: Record<string, { icon: string; label: string }> = {
  person: { icon: "NN", label: "Person" },
  location: { icon: "DD", label: "Location" },
  organization: { icon: "TC", label: "Organization" },
  artifact: { icon: "VP", label: "Artifact" },
  project_term: { icon: "DA", label: "Project" },
};

export function EntityBadge(props: { entityType?: string | null }) {
  if (!props.entityType) {
    return null;
  }
  const meta = ENTITY_META[props.entityType] ?? { icon: "ET", label: props.entityType };
  return (
    <span className="pill subtle entity-badge">
      <strong>{meta.icon}</strong>
      {meta.label}
    </span>
  );
}
