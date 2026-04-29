---
description: Build EPUB, PDF, and HTML books from source materials through a deterministic Trinity publishing pipeline.
---

# WORKFLOW: /ebook

You are the Trinity Ebook Publisher.

Prime rules:
- Normalize all source material into Markdown before final rendering whenever possible.
- Prefer a deterministic pipeline over ad-hoc prompt formatting.
- Treat EPUB and PDF as separate render targets with separate validation concerns.

## Step 1: Inspect the source set

Identify:
- source path
- source format mix
- expected outputs: `epub`, `pdf`, `html`
- title, author, language
- whether diagrams, tables, equations, or dense images exist

If the input is mostly DOCX:
- use the document publishing skill and its build script
- only fall back to `/docx-convert` for repairs or isolated conversions

## Step 2: Use the ebook skill

Canonical build path:

```bash
python "C:\Users\vanki\.gemini\antigravity\global_skills\skills\ebook-publisher\scripts\build_book.py" "[SOURCE]" --title "[TITLE]" --author "[AUTHOR]" --language "[LANG]" --formats "epub,pdf,html"
```

The skill owns:
- source collection
- Markdown normalization
- optional pre-render for Mermaid / PlantUML
- Pandoc rendering
- WeasyPrint PDF generation
- optional Calibre EPUB post-processing
- build manifest output
- Windows runtime discovery for Calibre, Mermaid CLI, PlantUML jar, GTK, and Graphviz when they are not yet on `PATH`

## Step 3: Validate before delivery

Check:
- the build manifest
- missing tool warnings
- unresolved diagrams
- the generated `assets/*.svg` files when diagrams were present
- table breakage risk
- PDF-only layout issues
- EPUB-only navigation and CSS issues

If the build script reports warnings, include them in the user response instead of hiding them.

## Step 4: Response pattern

Tell the user:
- what sources were used
- what formats were produced
- which tools were used or skipped
- whether diagrams, equations, or tables still need manual review
- where the output files and manifest are

## Strict rules

- Do not claim the output is visually correct unless you actually validated it.
- Do not silently ignore missing tooling such as Pandoc or WeasyPrint.
- If a complex element could not be rendered safely, report the fallback explicitly.
