# Phase 09: Entity Enrichment & User Review

Status: ⬜ Pending
Priority: P1
Duration: 1 tuần
Dependencies: Phase 07

## Objective
Scan → enrich metadata → user review → save approved only. Không tự động promote (A5, A12).

---

## Tasks

### P9-T1 — EntitySuggestion extended fields
Extend existing `EntitySuggestion` dataclass:
```python
@dataclass(slots=True)
class EntitySuggestion:
    # Existing fields
    source: str
    target: str
    entity_type: str
    start: int
    end: int
    confidence: float

    # NEW: Universe context
    universe: str = ""                          # Detected universe ID
    work: str = ""                              # Detected work (e.g. "凡人修仙传")
    sentence_index: int = -1                    # Which sentence in chapter

    # NEW: Review workflow
    review_status: str = "pending"              # pending|approved|rejected|saved
    enrichment_ready: bool = False              # True = đủ info để save vào term bank
    resolution_source: str = ""                 # "term_bank"|"trie"|"heuristic"|"user"

    # NEW: Suggestions for user
    suggested_tags: list[str] = field(default_factory=list)
    suggested_context_markers: list[str] = field(default_factory=list)
    suggested_co_occurring: list[str] = field(default_factory=list)

    # NEW: Disambiguation
    ambiguous: bool = False
    ambiguous_candidates: list[str] = field(default_factory=list)
    needs_qa_review: bool = False
```

### P9-T2 — EntityEnrichmentManager
File: `src/pipeline/entity_enrichment.py`

```python
class EntityEnrichmentManager:
    """User-controlled flow: scan → review → approve → save (A5, A12)."""

    def prepare_for_review(
        self,
        entities: list[EntitySuggestion],
        *,
        detected_universes: list[str],
        context_text: str,
    ) -> list[EntitySuggestion]:
        """
        Auto-fill universe (if single active), suggest tags,
        suggest context_markers from fingerprints, suggest co_occurring
        from nearby entities. Set enrichment_ready=True when sufficient.
        """

    def approve_entity(self, entity: EntitySuggestion) -> EntitySuggestion:
        """User approves → review_status='approved'."""

    def reject_entity(self, entity: EntitySuggestion) -> EntitySuggestion:
        """User rejects → review_status='rejected'."""

    def save_to_term_bank(
        self,
        entities: list[EntitySuggestion],
        *,
        target_scope: str = "global",
    ) -> int:
        """
        User chọn lưu → atomic write to JSONL.
        Only saves entities with review_status='approved'.
        Returns count saved.
        """

    def export_review_report(
        self,
        entities: list[EntitySuggestion],
    ) -> str:
        """Export Markdown report for user review."""
```

### P9-T3 — Atomic write flow
```
1. Write to temp file (same directory, .tmp suffix)
2. Validate temp file (valid JSONL, required fields)
3. Deduplicate against existing records (source|universe key)
4. Append new records to target JSONL file
5. Remove temp file
6. Call TermBank.reload_universe() for hot reload
```

Error handling:
- If validation fails → delete temp, raise error, no data corrupted
- If dedup finds existing → skip duplicate, log warning
- If write fails → temp file preserved for recovery

### P9-T4 — Sidecar commands
Add to `src/ui/sidecar_bridge.py`:

| Command | Input | Output |
|---------|-------|--------|
| `entity_scan_review` | `{chapter_text, options}` | `{entities: EntitySuggestion[]}` |
| `entity_approve` | `{entity_id}` | `{status: "approved"}` |
| `entity_reject` | `{entity_id, reason?}` | `{status: "rejected"}` |
| `entity_save_to_term_bank` | `{entity_ids[], scope}` | `{saved_count, skipped_count}` |
| `entity_export_report` | `{entity_ids[]}` | `{markdown: string}` |

Sidecar JSON schema per command:
```json
{
  "command": "entity_scan_review",
  "payload": {
    "chapter_text": "string",
    "options": {
      "auto_detect_universe": true,
      "include_ambiguous": true,
      "min_confidence": 0.5
    }
  }
}
```

### P9-T5 — Review report format
Markdown export format:
```markdown
# Entity Review Report
Generated: {timestamp}
Chapter: {chapter_id}
Detected Universe(s): {universes}

## Entities for Review ({count})

### ✅ Approved ({approved_count})
| Source | Target | Type | Universe | Confidence |
|--------|--------|------|----------|------------|
| 萧炎 | Tiêu Viêm | person | dau_khi | 0.99 |

### ⚠️ Ambiguous ({ambiguous_count})
| Source | Candidates | Context |
|--------|-----------|---------|
| 长老 | Trưởng Lão (global), Trưởng Lão (dau_khi) | ... |

### ❌ Rejected ({rejected_count})
| Source | Reason |
|--------|--------|
```

## Files to Create/Modify
- `src/pipeline/entity_scanner.py` — [MODIFY] Extend EntitySuggestion
- `src/pipeline/entity_enrichment.py` — [NEW] EntityEnrichmentManager
- `src/ui/sidecar_bridge.py` — [MODIFY] Add 5 commands
- `tests/test_entities/test_entity_enrichment.py` — [NEW]

## Definition of Done
```
[ ] EntitySuggestion has all 12 new fields
[ ] prepare_for_review auto-fills universe if single active
[ ] approve_entity/reject_entity update status correctly
[ ] save_to_term_bank: atomic, deduped, valid JSONL
[ ] Hot reload after save (reload_universe)
[ ] No auto-save without user approve (A5)
[ ] Sidecar 5 commands documented with JSON schemas
[ ] export_review_report outputs valid Markdown
[ ] Tests pass
```

---
Next Phase: Phase 10 — Context Resolver + EAPEE
