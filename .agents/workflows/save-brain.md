---
description: Save long-term context into Trinity local state, compiled wiki, palace, and Obsidian Second Brain.
---

# WORKFLOW: /save-brain

You are the Trinity Memory Manager.

Prime rules:
- Use `trinity_cli.py save` as the canonical checkpoint path.
- Do not use `/save-brain` as a replacement for structured domain ingestion.
- If the user is adding durable medical, translation, legal, finance, or research knowledge, route that through the domain command first, then checkpoint.
- If a translation project already has structured JSON state, `/save-brain` should still refresh the translation atlas, shared glossary sync, and app-ready translation databases automatically.

## Step 1: Ensure Trinity exists

Run:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" init
```

If Trinity is already initialized, continue.

## Step 2: Resolve the checkpoint payload

Before saving, determine:
- `feature`
- `phase`
- `notes`

Use project state and recent conversation context first.

If the user just completed a structured ingest, mention that in `notes` instead of recreating the domain pages manually.

## Step 3: Canonical save

Run:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" save --feature "[FEATURE]" --phase "[PHASE]" --notes "[NOTES]"
```

If one or more fields are unknown, pass empty strings and let Trinity save the snapshot anyway.

## Step 4: Trust the CLI side effects

After success, assume Trinity updated:
- project state files
- session snapshot and recovery prompt
- local `.brain/wiki`
- palace
- Obsidian dashboards and mirrors
- translation wiki hubs and atlas when translation state exists
- `artifacts/translation-db/` plus shared language-pair database when translation state exists

For chapter-level deterministic QA after the checkpoint, use:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" translate next --deterministic
```

or batch pending chapters:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" translate all --deterministic
```

or batch arbitrary source folders for a non-LLM app runtime:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" translation-memory batch-apply --input-dir source
```

or call the standalone runtime directly for machine-to-machine integrations:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_translation_runtime.py" --project "[PROJECT_ROOT]" batch-apply --input-dir source --json
```

Do not recreate those artifacts manually unless the CLI explicitly failed.

## Step 5: Confirm the checkpoint

Report:
- feature and phase used
- whether the save reached wiki, palace, and second brain
- whether translation database refresh ran
- what structured domains were already updated before the checkpoint

Suggested next commands:
- `/recap`
- `/debug`
- `/medical`
- `/translate`

## Recovery rule

If the CLI reports that the Obsidian vault is missing:
- mention that the Second Brain mirror failed
- continue saving local state, wiki, and palace
- recommend checking `obsidian.json` or `TRINITY_OBSIDIAN_VAULT`
