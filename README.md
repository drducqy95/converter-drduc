# Converter by DrDuc

Non-LLM translation workspace focused on `ZH -> VI` with a baseline `EN -> VI` path, using dictionary migration, Trie lookup, LuatNhan rules, RBMT orchestration, QA, translation memory, and a desktop workflow scaffold.

## Current Status

- Production core: Python.
- Primary execution plan: `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`.
- Current baseline: Phase 00-07 implemented and tested; Phase 08 has a verified React shell plus Python sidecar/Tauri scaffold.
- Test command: `python -m pytest`
- Desktop shell build: `cd desktop && npm run build`

## Production Boundary

The repo currently contains two different implementation layers:

- Python under `src/core/`, `src/engine/`, and related scripts is the production path.
- JavaScript modules under `src/preprocessor/`, `src/parser/`, `src/rules/`, and `src/learning/` are prototype/reference material and are not the authoritative runtime.

This boundary is intentional. New execution work should follow the Python plan and SQLite-backed dictionary pipeline.

## Implemented Baseline

- `scripts/migrate_qt_to_md.py`: migrate Quick Translator dictionaries into Markdown-based sources.
- `src/core/md_dictionary_compiler.py`: compile Markdown dictionaries into SQLite.
- `src/core/trie_engine.py`: runtime Trie lookup with priority handling.
- `src/core/luat_nhan_engine.py`: grammar/disambiguation rule loading and application.
- `src/engine/number_converter.py`: number/date/unit conversion baseline.
- `src/pipeline/`: document import, chapter split, structure preservation, entity scan, relationship build, config generation.
- `src/eapee/`: emotion detector, emotion state machine, pronoun resolver, expression bank.
- `src/engine/rbmt_translator.py`: clean + draft RBMT output with ambiguity trace and TM integration.
- `src/qa/`: terminology, pronoun, emotion, structure, untranslated, length checks, and QA reports.
- `src/state/`: project manager, SQLite TM, candidate workflow, runtime stats, Obsidian export.
- `src/en_vi/en_vi_translator.py`: phrase-first EN-VI baseline with small grammar transfer rules.
- `src/ui/`: sidecar command protocol for the desktop app.
- `desktop/`: React shell, Tauri scaffold, and verified web build.

## Verification

- `python -m pytest` -> `98 passed`
- `cd desktop && npm run build` -> Vite production build succeeds
- Native Tauri packaging has not been validated in this environment because Rust tooling is not installed

## Project References

- Master plan: `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`
- Progress tracker: `project_progress.json`
- Desktop scaffold notes: `desktop/README.md`

## Principles

- Deterministic core behavior.
- Phrase-first lookup, but not phrase-only reasoning.
- Hot/cold dictionary storage separation for runtime speed and richer metadata.
- Explicit provenance, fallback visibility, and reviewable ambiguity.
