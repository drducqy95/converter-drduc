---
title: Project Converter by DrDuc
type: entity
slug: project-converter-by-drduc
category: entities
created: 2026-04-14T08:47:36
updated: 2026-04-30T07:59:31
status: active
source: /save-brain
tags: ["converter_by_drduc", "project", "Converter by DrDuc", "overview"]
project: Converter by DrDuc
links: ["session-2026-04-20-20-14-00", "session-2026-04-22-15-54-02", "session-2026-04-27-22-14-18", "pretranslationpipeline-finalize-preparation-memoryerror-pattern", "session-2026-04-27-21-50-56", "session-2026-04-29-20-45-11", "session-2026-04-14-11-00-24", "session-2026-04-29-21-47-52", "translation-engine-chinese-structure-rewriter-regexoverlaptranslationambiguity-pattern", "session-2026-04-14-08-47-36", "session-2026-04-29-16-45-16", "session-2026-04-30-07-59-31", "session-2026-04-20-19-54-28", "pos-migration-execution-logicerror-pattern", "session-2026-04-22-10-07-27", "pretranslationpipeline-valueerror-pattern", "session-2026-04-23-21-17-14", "session-2026-04-22-10-38-22", "session-2026-04-14-15-25-39", "desktop-ui-transport-configurationerror-pattern", "session-2026-04-23-16-17-00", "session-2026-04-30-07-13-09"]
---

## Snapshot
- Project: converter_by_drduc
- Feature: Converter repo hardening from technical analysis
- Phase: CI editable install fix, LuatNhan specificity conflict resolution, pretranslation directory recovery
- Progress: 0%

## Pending Tasks
- No pending tasks recorded.

## Latest Notes
Analyzed plans/PHAN_TICH_REPO_converter-drduc.md and addressed the push CI failure by switching pyproject build backend to setuptools.build_meta. Added LuatNhan specificity-based conflict resolution, directory pretranslation import error recovery with working/import_errors.json, regression tests, documentation updates, and verified python -m pip install -e .[dev], python -m pytest = 183 passed, and desktop npm run build passed.

## Latest Checkpoint
- [[session-2026-04-30-07-59-31]]
