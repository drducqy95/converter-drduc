# Phase 07: Context-Aware Entity Resolution

Status: ⬜ Pending
Priority: P1
Duration: 2 tuần
Dependencies: Phase 06

## Objective
Nâng cấp EntityScanner dùng UniverseContext, TermBank context scoring, mixed-script detection, expanded entity types.

## Resolution Chain (A4 compliant)
```
1. Project-private TermBank
2. Universe-specific TermBank
3. Global TermBank
4. Trie P5 project-specific names
5. Trie P4 global proper names
6. Trie P3 project VietPhrase
7. Trie P2 global VietPhrase
8. Trie P1 PhienAm
9. Heuristic name mining
```

## Tasks

### P7-T1 — Pre-scan universe
```python
universe_ctx = self._universe_detector.detect(text)
sentence_ctxs = self._universe_detector.detect_sentence_level(sentences)
```

### P7-T2 — Resolve entity with context
```python
candidates = self._term_bank.lookup_with_context(
    entity.source,
    context_window=context_window,
    entity_type=entity.entity_type,
    detected_universes=active_universes,
)
```
Disambiguation rule (A11):
- If score gap < 0.15 between top 2 candidates:
  - `entity.ambiguous = True`
  - `entity.needs_qa_review = True`
  - `entity.ambiguous_candidates = top 3`
  - **Do NOT inject [universe_tag] into translation**

### P7-T3 — Mixed-script detection
Patterns to detect:
```
克莱恩·莫雷蒂 (Full CJK transliteration)
Klein (Pure Latin in CJK text)
Sequence 9 (Latin+Number in CJK text)
M829A3, AL2O3 (Technical codes)
```

### P7-T4 — Expanded entity types
```python
ENTITY_TYPES = {
    "person", "location", "organization",
    "realm", "technique", "weapon", "item",
    "title", "creature", "faction", "term",
    "tech_product", "ship", "planet", "race",
    "artifact", "skill", "cultivation_realm",
}
```

### P7-T5 — Same-name cross-universe disambiguation
```
For each entity occurrence:
  1. context_window = text[pos-200 : pos+200]
  2. local_universe = detect_sentence_level(context_window)
  3. candidates = term_bank.lookup_with_context(source, context_window)
  4. IF len(candidates) == 1: use it
  5. IF len(candidates) > 1:
     - Score each by: universe match(+3), co_occurrence(+2), context_markers(+1)
     - Pick highest score
     - IF tie: flag as ambiguous (QA review, NOT tag injection)
```

## Files to Create/Modify
- `src/pipeline/entity_scanner.py` — [MODIFY] Context-aware scan + resolution chain
- `src/entities/entity_types.py` — [NEW] Entity type enum
- `tests/test_entities/test_entity_context.py` — [NEW]

## Definition of Done
```
[ ] Same-name disambiguation works
[ ] Mixed-script entity detected
[ ] TermBank lookup before Trie (A4)
[ ] Ambiguity becomes QA flag, NOT output tag (A11)
[ ] No [universe_tag] in translation output
[ ] Tests pass
```

---
Next Phase: Phase 08 — Grammar Transfer Planner
