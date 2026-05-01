# Cross-Project Term Bank

This folder stores proper names and terminology that should be reused before
the heuristic entity scanner guesses a target.

- `global/*.jsonl`: high-coverage names and terms that are safe across many
  projects and contexts.
- `universes/{universe_id}/*.jsonl`: story-specific fingerprints and terms for
  context-aware disambiguation. One concrete book/project is one universe.
- `projects/{project_id}/*.jsonl`: private names and terms for one project.
- `workspace_projects/{project_id}/knowledge/*.jsonl`: optional local private
  overrides that are not shared globally.

Each JSONL row is one term:

```json
{"source":"米迦勒","target":"Michael","entity_type":"person","scope":"global","status":"approved","confidence":0.98,"universe":"Abrahamic religions","work":"Bible / Abrahamic canon","franchise":"religious canon","notes":"High-coverage Latin name."}
```

Private records take priority over global records. Universe records win only
when `detect_universe()` or the local `context_markers` / `co_occurring_entities`
support that story universe. Use `universe`, `work`, `franchise`, `notes`,
`context_markers`, and `version` for names or terms tied to a specific novel,
film, game, or shared-world canon.
