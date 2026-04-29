# Changelog

## Unreleased

- Cleaned repository layout by moving runner, debug, migration, planning, and archive artifacts out of the root directory.
- Standardized Python dependencies in `pyproject.toml`.
- Added GitHub Actions for Python tests and the desktop web build.
- Added contributor and security documentation.
- Added dialogue context classification before emotion detection, implicit speaker tracking, CJK-aware fuzzy TM similarity, and non-name phrase filtering for entity scan.
- Added emotion negation handling, TM last-access metadata and machine-entry eviction, document input validation, export checkpoints, CI coverage output, and a Makefile task runner.
- Added dictionary source-manifest hashing/stale detection and EN-VI passive voice plus phrasal-verb handling.
