# Changelog

## Unreleased

- Cleaned repository layout by moving runner, debug, migration, planning, and archive artifacts out of the root directory.
- Standardized Python dependencies in `pyproject.toml`.
- Added GitHub Actions for Python tests and the desktop web build.
- Added contributor and security documentation.
- Added dialogue context classification before emotion detection, implicit speaker tracking, CJK-aware fuzzy TM similarity, and non-name phrase filtering for entity scan.
- Added emotion negation handling, TM last-access metadata and machine-entry eviction, document input validation, export checkpoints, CI coverage output, and a Makefile task runner.
- Added dictionary source-manifest hashing/stale detection and EN-VI passive voice plus phrasal-verb handling.
- Added Trie Viterbi segmentation, typed LuatNhan placeholders, and relationship-graph hints for third-person pronoun resolution.
- Fixed editable package installation for CI, added LuatNhan specificity conflict resolution, and made directory pretranslation skip bad source files with an import-error manifest.
- Added CI dictionary-cache compilation before pytest so fresh runners do not depend on ignored `_compiled` artifacts.
- Added deterministic grammar conflict-resolution traces, paired-connective clause segmentation, and TM tiered fuzzy search with snapshot/rollback recovery.

## v24.0 - Production Release Candidate

### Added

- Cross-universe term bank loading for global, universe, and project-private JSONL records.
- Context-aware universe detection and same-name entity resolution without injecting universe tags into translation output.
- Entity enrichment workflow for scan, review, approve, save, and Markdown export.
- Markdown-to-JSONL migration converter for `name_project` glossaries.
- Regression gate, seed performance benchmark, and production readiness validator scripts.
- Release documentation for cross-universe resolution, grammar scanning, grammar transfer, learning loop, regression policy, and promotion policy.

### Changed

- `EntitySuggestion` now carries review metadata, universe/work hints, suggested tags, context markers, and QA flags.
- `TermBankRecord` now carries context markers, co-occurring entities, and version metadata.
- GitHub Actions now runs the production regression gate after the Python test job.

### Security

- Machine output still cannot enter approved TM without review.
- Promotion policy requires human approval and regression success before durable application.
