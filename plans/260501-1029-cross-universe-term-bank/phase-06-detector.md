# Phase 06: Universe Detector

Status: ⬜ Pending
Priority: P1
Duration: 1 tuần
Dependencies: Phase 05

## Objective
Triển khai module riêng `UniverseDetector` — phát hiện universe từ text bằng fingerprint, canonical characters, co-occurrence.

## Tasks

### P6-T1 — fingerprints.json
File: `data/term_bank/universes/fingerprints.json`
```json
{
  "version": 1,
  "universes": {
    "tu_tien": {
      "fingerprint_terms": [
        {"term": "灵根", "weight": 1.5},
        {"term": "筑基", "weight": 1.2},
        {"term": "结丹", "weight": 1.2},
        {"term": "元婴", "weight": 1.3},
        {"term": "化神", "weight": 1.0},
        {"term": "飞升", "weight": 0.8}
      ],
      "canonical_chars": ["韩立", "王林", "张小凡"],
      "co_occurrence_seeds": [
        {"pair": ["韩立", "南宫婉"], "confidence": 0.99},
        {"pair": ["王林", "李慕婉"], "confidence": 0.99}
      ],
      "exclusion_terms": []
    },
    "dau_khi": {
      "fingerprint_terms": [{"term": "斗气", "weight": 1.5}, {"term": "异火", "weight": 1.5}],
      "canonical_chars": ["萧炎", "药尘"],
      "co_occurrence_seeds": [{"pair": ["萧炎", "药尘"], "confidence": 0.99}]
    }
  },
  "multi_universe_threshold": 0.65,
  "min_confidence_for_active": 0.4
}
```

### P6-T2 — UniverseDetector module
File: `src/pipeline/universe_detector.py`
```python
@dataclass(frozen=True)
class UniverseSignal:
    universe_id: str
    confidence: float
    matched_fingerprints: list[str]
    matched_characters: list[str]

@dataclass
class UniverseContext:
    active_universes: list[str]
    signals: list[UniverseSignal]
    is_multi_universe: bool
    is_unknown: bool
```

Algorithm:
```
1. Weighted fingerprint scan
2. Canonical character scan
3. Co-occurrence pair scan
4. Normalize scores
5. Filter by threshold (min_confidence_for_active: 0.4)
6. If ≥2 universes > multi_universe_threshold (0.65): is_multi_universe = True
7. Return UniverseContext
```

### P6-T3 — detect_sentence_level()
Use sentence ±1 context radius for per-sentence universe detection.

### P6-T4 — expand_cooccurrence_from_term_bank()
Auto-learn co-occurrence pairs from `co_occurring_entities` field in TermBankRecords.

## Files to Create/Modify
- `src/pipeline/universe_detector.py` — [NEW]
- `data/term_bank/universes/fingerprints.json` — [NEW]
- `tests/test_entities/test_universe_detector.py` — [NEW]

## Definition of Done
```
[ ] detect() accuracy ≥ 90% trên benchmark
[ ] detect_sentence_level() hoạt động
[ ] multi_universe detection works (Chư Thiên scenario)
[ ] oc_fanfic fallback cho unknown universe
[ ] Tests pass
```

---
Next Phase: Phase 07 — Context-Aware Entity Resolution
