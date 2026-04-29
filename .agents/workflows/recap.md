---
description: Restore project context from Trinity state, wiki, palace, and Obsidian Second Brain.
---

# WORKFLOW: /recap

You are the Trinity Context Loader.

Prime rules:
- Always load context through `trinity_cli.py recap` first.
- Treat recap output as the canonical merged snapshot.
- Do not fabricate state that recap did not show.

## Step 1: Run recap first

Full mode:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" recap
```

Compact mode:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" recap --short
```

## Step 2: Read the recap output before doing anything else

Extract:
- project identity
- current feature and phase
- recent blockers
- wiki coverage
- atlas coverage for active domains
- second brain notes
- palace summary

If recap shows domain grounding, use it:
- Translation: atlas, glossary, pronouns, canon hubs
- Translation databases: project RBMT export and shared language-pair export
- Medical: atlas, drug canon, case coverage, index density
- Debugging: recent failures, fix patterns, reused solutions

## Step 3: Drill down only when needed

For narrower recall:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" check "[module-or-error]"
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" wiki search "[keyword]" --top 8
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" wiki lint
```

## Step 4: Respond with actionable context

Tell the user:
- what the system believes is the current task
- what structured knowledge already exists
- where recall is weak or stale
- what command or action should happen next
- whether translation app-ready exports are already fresh enough or should be rebuilt

## Strict rule

If recap shows missing or weak memory, say so explicitly and suggest rebuilding context with:
- `/save-brain`
- `trinity_cli.py wiki create/update`
- `trinity_cli.py translation-memory ...`
- `trinity_cli.py translation-memory build-database`
- `trinity_cli.py medical ...`
- `trinity_cli.py log-error`
