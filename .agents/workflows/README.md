# Global Workflows - Trinity System

For the full current-system guide, read [`../README.md`](../README.md) first.

This directory contains the human-facing workflow contracts for Trinity.

They are not free-form prompts. They define the canonical order of operations so the agent writes through the same memory system every time.

## Core workflows

| Command | File | Purpose |
|---|---|---|
| `/init` | `init.md` | Initialize Trinity files and project state |
| `/plan` | `plan.md` | Planning and decomposition |
| `/code` | `code.md` | Implementation |
| `/debug` | `debug.md` | Structured debugging and fix capture |
| `/test` | `test.md` | Test execution |

## Memory workflows

| Command | File | Purpose |
|---|---|---|
| `/save-brain` | `save-brain.md` | Save session checkpoints across all memory layers |
| `/recap` | `recap.md` | Restore merged context from Trinity |
| `/next` | `next.md` | Show the next task |
| `/medical` | `medical.md` | Ingest medical knowledge, pharmacology, and clinical cases |
| `/legal` | `legal.md` | Ingest legal authorities, contracts, and IRAC analyses |
| `/finance` | `finance.md` | Ingest finance metrics, forecasts, tax rules, and controls |

## Translation workflows

| Command | File | Purpose |
|---|---|---|
| `/translate` | `translate.md` | Translation execution contract with glossary, pronouns, world grounding, deterministic batch runtime, and standalone runtime handoff |
| `/translate-setup` | `translate-setup.md` | Initialize translation project state and canon files |

## Document workflows

| Command | File | Purpose |
|---|---|---|
| `/docx-convert` | `docx-convert.md` | High-fidelity DOCX conversion |
| `/docx-read` | `docx-read.md` | Read and analyze DOCX files |
| `/ocr` | `ocr.md` | OCR and raw document extraction |
| `/ebook` | `ebook.md` | Build EPUB, PDF, and HTML books from source materials |

## Operating rules

- `save-brain` is a checkpoint workflow, not a replacement for domain ingestion.
- Translation checkpoints still refresh shared glossary sync and app-ready databases if structured translation state already exists.
- Legal and finance imports should go through `/legal` or `/finance` so the resulting pages keep schema, lineage, and hub updates.
- `recap` must run before context-sensitive work when state is uncertain.
- Broad imports should end with atlas refresh or linting.
- High-stakes domains must preserve lineage, auditability, and human review boundaries.
