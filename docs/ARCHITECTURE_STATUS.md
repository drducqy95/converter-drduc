# Architecture Status

Updated: 2026-05-01

## Verification Baseline

- Python tests before v24 additions: `python -m pytest` -> `215 passed`
- v24 focused tests added for term bank, entity context, enrichment, and markdown migration
- Runtime observed in this workspace: Python 3.14.2 on Windows
- Primary runtime boundary: Python under `src/core`, `src/engine`, `src/pipeline`, `src/state`, `src/qa`
- Desktop shell remains the workflow surface under `desktop/`

## Implemented

- Dictionary compiler, Trie runtime, LuatNhan rules, number conversion, RBMT orchestration, QA reports, project state, candidate review workflow, EN-VI baseline, and desktop sidecar.
- V23 TM governance:
  - `tm_machine`, `tm_approved`, `tm_reviewed`
  - machine RBMT output is stored only in `tm_machine`
  - approved TM promotion requires human review via `promote_to_approved()`
  - lookup order is approved exact -> approved fuzzy -> machine suggestion
- V23 trace foundation:
  - shared `TraceEvent`
  - stable per-segment `trace_id`
  - RBMT trace events enriched with stage/action/confidence
  - QA JSON/Markdown includes decision paths
- V23 segment and safety foundation:
  - `SegmentType`, `SegmentPacket`
  - `SegmentClassifier`
  - `ProtectedSpan` and priority-aware `ProtectedSpanRegistry`
  - `NoiseFilter` with hard whitelist and weighted DROP/REVIEW/METADATA decisions
- V23 grammar foundation:
  - `ClauseSegmenter`, `RelationDetector`, `RuleClaim`, `RuleRegistry`, `ConflictResolver`
  - `GrammarTransferEngine` source-side P0/P1 marker transfer with RBMT trace integration
- V24 cross-universe term bank:
  - `TermBankRecord` supports `universe`, `scope`, `confidence`, `status`, `version`, `context_markers`, and `co_occurring_entities`
  - global, universe-specific, and project-private JSONL loaders
  - `detect_universe()`, `lookup_with_context()`, `get_universe_glossary()`, and hot reload
  - seed universe folders for concrete works such as `pham_nhan_tu_tien`, `dau_pha_thuong_khung`, `dau_la_dai_luc`, `gia_thien`, `kiem_lai`, `quy_bi_chi_chu`, and `marvel`
- V24 entity enrichment:
  - `EntitySuggestion` review metadata
  - `EntityEnrichmentManager` scan -> review -> approve -> save workflow
  - sidecar commands: `entity_scan_review`, `entity_approve`, `entity_reject`, `entity_save_to_term_bank`, `entity_export_report`
- V24 release hardening:
  - `scripts/run_regression_gate.py`
  - `scripts/benchmark_chapter.py`
  - `scripts/validate_production_ready.py`
  - release docs for cross-universe, grammar, learning, regression, and promotion policy

## Partial

- Protected spans are modeled and tested, but every legacy rewrite path is not yet fully span-aware.
- Grammar transfer has a conservative source-side P0/P1 pack; the full clause-plan object model and Vietnamese surface realizer from the long roadmap remain partial.
- Entity handling still uses the existing `EntityScanner`; context-aware term-bank ranking is implemented, but the proposed 7-pass `EntityPipeline` and full transliteration decision tree are not complete.
- Context handling exists through current EAPEE/pronoun modules, but `SpeakerTracker`, `EntitySalienceMemory`, and zero-pronoun insertion are not production complete.
- Learning exists through candidate review, project learning, natural feedback, and entity enrichment; a unified diff/error classifier/candidate miner still needs expansion.
- v24 has a standalone regression gate with seed metrics. Large full-chapter gold-corpus metrics still need expansion as real gold data grows.

## Missing From Full Roadmap

- AliasGraph persistence with `entities`, `entity_aliases`, and `entity_occurrences`
- Full grammar transfer plan object model and Vietnamese surface realizer
- Idiom policy enforcement with `LITERAL_FORBIDDEN` and semantic templates
- Register-aware lexical policy files
- Unified review diff/error classifier/candidate miner beyond current learning surfaces
- Large full-chapter gold regression corpus for every target universe

## Verify

```powershell
python -m pytest
python scripts/run_regression_gate.py --strict
python scripts/validate_production_ready.py
cd desktop
npm run build
```
