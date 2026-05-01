# Phase 05: Term Bank Schema Expansion

Status: ⬜ Pending
Priority: P1
Duration: 1 tuần
Dependencies: Phase 04

## Objective
Mở rộng TermBankRecord để hỗ trợ universe/context/versioning. Implement context-scoring và lazy-load.

## Tasks

### P5-T1 — TermBankRecord fields expansion
```python
@dataclass(slots=True)
class TermBankRecord:
    source: str
    target: str
    entity_type: str = "term"
    universe: str = ""
    work: str = ""
    scope: str = "global"
    aliases_source: list[str] = field(default_factory=list)   # 中文 aliases
    aliases_target: list[str] = field(default_factory=list)   # Hán Việt aliases
    context_markers: list[str] = field(default_factory=list)   # Fingerprint terms
    co_occurring_entities: list[str] = field(default_factory=list)
    confidence: float = 1.0
    status: str = "active"
    version: int = 1
    notes: str = ""
    tags: list[str] = field(default_factory=list)
```

### P5-T2 — score_against_context()
Scoring weights:
```
universe match weight = 0.5
context markers weight = 0.3
co-occurrence weight = 0.2
multiply by confidence
```

### P5-T3 — Lazy-load universe data
```python
TermBank._universe_cache: dict[str, list[TermBankRecord]]
TermBank._load_universe(universe_id: str)
TermBank.reload_universe(universe_id: str)
TermBank.get_universe_glossary(universe: str) -> list[TermBankRecord]
```

### P5-T4 — lookup_with_context()
```python
def lookup_with_context(
    self, source: str, *,
    context_window: str = "",
    entity_type: str | None = None,
    detected_universes: list[str] | None = None,
) -> list[TermBankRecord]:
    """Return sorted candidates; caller decides ambiguity."""
```

### P5-T5 — Universe loader expansion
Mở rộng `_iter_record_files()` load từ `data/term_bank/universes/{id}/*.jsonl`

## Files to Create/Modify
- `src/pipeline/term_bank.py` — [MODIFY] Schema + scoring + loader
- `tests/test_entities/test_term_bank_universe.py` — [NEW]

## Definition of Done
```
[ ] 5 required fields exist: universe, scope, confidence, status, version
[ ] lookup_with_context sorted by score
[ ] deprecated records (status != active/approved) ignored
[ ] reload_universe works (hot reload)
[ ] Backward compatible with existing JSONL
[ ] Tests pass
```

---
Next Phase: Phase 06 — Universe Detector
