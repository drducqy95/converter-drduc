# Architecture Status

Updated: 2026-04-27

## Verification Baseline

- Python tests: `python -m pytest` -> `151 passed`
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
  - pre-translation emits `working/segments/segments_classified.json`
  - `ProtectedSpan` and priority-aware `ProtectedSpanRegistry`
  - `NoiseFilter` with hard whitelist and weighted DROP/REVIEW/METADATA decisions
- V23 grammar foundation:
  - `ClauseSegmenter`
  - `RelationDetector`
  - `RuleClaim`, `RuleRegistry`, `ConflictResolver`

## Partial

- Protected spans are modeled and tested, but not yet enforced inside every existing rewrite path.
- Entity handling still uses the existing `EntityScanner`; the proposed 7-pass `EntityPipeline`, ranker, promoter, and transliteration decision tree are not complete.
- Context handling exists through current EAPEE/pronoun modules, but `SpeakerTracker`, `EntitySalienceMemory`, and zero-pronoun insertion are not production complete.
- Learning exists through candidate review and project learning, but full promotion gates tied to regression metrics are not complete.
- Regression tests are green, but the v23 metric gate thresholds are not yet implemented as a standalone CI gate.

## Missing From Full V23 Roadmap

- AliasGraph persistence with `entities`, `entity_aliases`, and `entity_occurrences`
- Full grammar P0 transfer planner and Vietnamese surface realizer
- Idiom policy enforcement with `LITERAL_FORBIDDEN` and semantic templates
- Register-aware lexical policy files
- Human review diff/error classifier/candidate miner as a unified learning loop
- `scripts/run_regression_gate.py` with threshold metrics
- GitHub Actions regression workflow

## Verify

```powershell
python -m pytest
cd desktop
npm run build
```

