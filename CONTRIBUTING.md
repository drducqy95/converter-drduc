# Contributing

## Setup

Use Python 3.11+ from the repository root:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

For the desktop shell:

```bash
cd desktop
npm ci
npm run build
```

## Project Boundary

The production runtime is Python under `src/`. The desktop shell lives under `desktop/`. Historical design notes and resolved planning artifacts are archived under `docs/archive/`.

Runner scripts live in `scripts/runners/`; development and migration utilities live in `scripts/dev/` and `scripts/migration/`.

## Change Rules

- Keep generated diagnostics, local state, compiled databases, media captures, and workspace projects out of git.
- Prefer focused tests near the behavior being changed.
- Do not add LLM or cloud translation dependencies to the deterministic RBMT core.
- Keep dictionary changes reviewable and preserve source/provenance metadata when available.

## Pull Requests

Before opening a PR, run:

```bash
python -m pytest
cd desktop && npm run build
```

Mention any test you could not run and why.
