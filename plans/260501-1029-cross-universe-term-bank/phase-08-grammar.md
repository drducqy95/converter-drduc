# Phase 08: Grammar Transfer Planner

Status: ⬜ Pending
Priority: P1
Duration: 3 tuần
Dependencies: Phase 03 + Phase 07

## Objective
Nâng grammar transfer từ rewrite chuỗi lên clause/relation/rule-claim planner. Tuân thủ A7 (trace mọi decision) + A8 (protected spans thắng mọi rewrite).

---

## Tasks

### P8-T1 — ClauseSegmenter
File: `src/grammar/clause_segmenter.py`

**BoundaryType enum:**
```python
class BoundaryType(Enum):
    SENTENCE_END = "sentence_end"       # 。！？
    CLAUSE_SOFT = "clause_soft"         # ，、
    CLAUSE_HARD = "clause_hard"         # ；
    CONDITIONAL = "conditional"         # 如果/只要/一旦/除非 boundary
    CONCESSIVE = "concessive"           # 虽然/即便/哪怕/就算 boundary
    CAUSE = "cause"                     # 因为/由于/既然 boundary
    RESULT = "result"                   # 所以/因此/故 boundary
    TEMPORAL = "temporal"               # 当/在...时 boundary
    CONJUNCTION = "conjunction"         # 而/且/并 boundary
```

**Clause dataclass:**
```python
@dataclass
class Clause:
    text: str
    start: int
    end: int
    boundary_before: BoundaryType | None
    boundary_after: BoundaryType | None
    role: str = ""  # "condition", "main", "concession", "result"
```

### P8-T2 — RelationDetector
File: `src/grammar/relation_detector.py`

**RelationType enum:**
```python
class RelationType(Enum):
    CONDITION = "condition"
    CONCESSION = "concession"
    CAUSE_EFFECT = "cause_effect"
    CONTRAST = "contrast"
    TEMPORAL = "temporal"
    PURPOSE = "purpose"
    VIEWPOINT = "viewpoint"
    PASSIVE = "passive"
    DISPOSAL = "disposal"
    PARALLEL_ACTION = "parallel_action"
    DEFINITION = "definition"
    EVIDENTIAL = "evidential"
    COMPARISON = "comparison"
    PRECAUTION = "precaution"
    EMPHATIC_EVEN = "emphatic_even"
    NECESSITY = "necessity"
```

**Relation dataclass:**
```python
@dataclass
class Relation:
    relation_type: RelationType
    source_span: tuple[int, int]
    marker_positions: list[int]
    clause_a: Clause
    clause_b: Clause | None
    confidence: float
```

### P8-T3 — RuleClaim
File: `src/grammar/rule_claim.py`
```python
@dataclass
class RuleClaim:
    rule_id: str                    # e.g. "rule_condition_001"
    relation_type: str
    source_span: tuple[int, int]
    priority: int                   # from grammar_rule_priority.yml
    confidence: float
    replacement_plan: dict          # {"template": "Nếu {a} thì {b}", ...}
    protected: bool                 # A8: if True, this span is untouchable
    trace: TraceEvent               # A7: mandatory trace
```

### P8-T4 — RuleRegistry + ConflictResolver
Files: `src/grammar/rule_registry.py`, `src/grammar/conflict_resolver.py`

**Priority system** (`data/grammar/grammar_rule_priority.yml`):
```yaml
priority_table:
  protected_span_guard: 100
  entity_guard: 95
  number_quote_system_guard: 90
  idiom_literal_forbidden: 85
  viewpoint: 80
  condition_concession: 78
  passive_disposal: 76
  parallel: 74
  evidential_definition: 72
  de_modifier_possessive: 60
  classifier_complement_aspect: 55
  vi_surface_cleanup: 20
```

**ConflictResolver algorithm:**
```
1. Collect all RuleClaims for current segment
2. Sort by priority DESC
3. For each claim (highest first):
   a. Check if source_span overlaps with any already-applied claim
   b. If overlap with higher priority → SKIP this claim (trace: "skipped_lower_priority")
   c. If no overlap → APPLY this claim
   d. If claim.protected → mark span as locked, no further rules can touch it
4. Return applied claims list + skipped claims list (for trace)
```

### P8-T5 — Grammar P0 rules (15 rule modules)
Directory: `src/grammar/rules/`

| # | File | Pattern | Ví dụ | Vietnamese template |
|---|------|---------|-------|---------------------|
| 1 | `rule_viewpoint.py` | 作为X而言 | 作为朋友而言 | Với tư cách là {X} mà nói |
| 2 | `rule_condition.py` | 只要X就Y | 只要努力就能成功 | Chỉ cần {X} thì {Y} |
| 3 | `rule_condition.py` | 一旦X就Y | 一旦发现就报告 | Một khi {X} thì {Y} |
| 4 | `rule_condition.py` | 除非X否则Y | 除非投降否则格杀 | Trừ phi {X} nếu không {Y} |
| 5 | `rule_concession.py` | 哪怕X也Y | 哪怕失败也要尝试 | Cho dù {X} cũng {Y} |
| 6 | `rule_concession.py` | 就算X也Y | 就算下雨也要去 | Dù cho {X} cũng {Y} |
| 7 | `rule_concession.py` | 虽然X但是Y | 虽然累但是开心 | Tuy {X} nhưng {Y} |
| 8 | `rule_ba_construction.py` | 把X...V | 把书放下 | {V} {X} |
| 9 | `rule_passive.py` | 被X...V | 被打伤了 | Bị {X} {V} |
| 10 | `rule_passive.py` | 为X所V | 为人所知 | Được {X} {V} |
| 11 | `rule_passive.py` | 被X所V | 被敌人所困 | Bị {X} {V} |
| 12 | `rule_parallel_action.py` | 一边X一边Y | 一边走一边说 | Vừa {X} vừa {Y} |
| 13 | `rule_definition.py` | 所谓X | 所谓英雄 | Cái gọi là {X} |
| 14 | `rule_minimizing_suffix.py` | X罢了 / X而已 | 小事罢了 | {X} mà thôi |
| 15 | `rule_evidential.py` | 据说 / 据X称 | 据说他很强 | Nghe nói / Theo {X} |
| 16 | `rule_emphatic_even.py` | 就连X也Y | 就连他也害怕 | Ngay cả {X} cũng {Y} |

Each rule module implements:
```python
class RuleXxx:
    rule_id: str
    relation_type: RelationType
    priority: int

    def match(self, text: str, clauses: list[Clause]) -> list[RuleClaim]:
        """Return claims if pattern matches."""

    def apply(self, claim: RuleClaim, context: dict) -> str:
        """Apply transformation, return Vietnamese output."""
```

### P8-T6 — TransferPlanner
File: `src/grammar/transfer_planner.py`

Orchestrator that:
1. Receives SegmentPacket
2. Calls ClauseSegmenter → clauses
3. Calls RelationDetector → relations
4. For each relation → load appropriate rule → generate RuleClaim
5. Calls ConflictResolver → resolved claims
6. Applies claims in priority order → output Vietnamese
7. Calls SurfaceRealizer for final cleanup

### P8-T7 — SurfaceRealizer
File: `src/grammar/surface_realizer.py`

Vietnamese surface cleanup:
- Remove double spaces
- Fix punctuation spacing
- Normalize Vietnamese diacritics
- Handle classifier/measure word placement

### P8-T8 — LexicalDecodePolicy
File: `src/grammar/lexical_decode_policy.py`

Policy for when word-by-word Hán Việt vs semantic decode:
```python
@dataclass
class DecodeDecision:
    source: str
    strategy: str  # "hanviet", "semantic", "transliterate", "keep_original"
    confidence: float
    reason: str
```

### P8-T9 — IdiomPolicy
File: `src/grammar/idiom_policy.py`

Chengyu / idiom handling:
- If in `idiom_lexicon.tsv` → use pre-defined Vietnamese equivalent
- If unknown chengyu → decompose or transliterate
- Protected span type IDIOM blocks word-by-word decode

## Files to Create/Modify
- `src/grammar/__init__.py` — [NEW]
- `src/grammar/clause_segmenter.py` — [NEW]
- `src/grammar/relation_detector.py` — [NEW]
- `src/grammar/rule_claim.py` — [NEW]
- `src/grammar/rule_registry.py` — [NEW]
- `src/grammar/conflict_resolver.py` — [NEW]
- `src/grammar/transfer_planner.py` — [NEW]
- `src/grammar/surface_realizer.py` — [NEW]
- `src/grammar/lexical_decode_policy.py` — [NEW]
- `src/grammar/idiom_policy.py` — [NEW]
- `src/grammar/rules/__init__.py` — [NEW]
- `src/grammar/rules/rule_viewpoint.py` — [NEW]
- `src/grammar/rules/rule_condition.py` — [NEW]
- `src/grammar/rules/rule_concession.py` — [NEW]
- `src/grammar/rules/rule_passive.py` — [NEW]
- `src/grammar/rules/rule_ba_construction.py` — [NEW]
- `src/grammar/rules/rule_parallel_action.py` — [NEW]
- `src/grammar/rules/rule_definition.py` — [NEW]
- `src/grammar/rules/rule_evidential.py` — [NEW]
- `src/grammar/rules/rule_minimizing_suffix.py` — [NEW]
- `src/grammar/rules/rule_emphatic_even.py` — [NEW]
- `data/grammar/grammar_rule_priority.yml` — [NEW]
- `data/grammar/relation_templates.yml` — [NEW]
- `data/grammar/idiom_lexicon.tsv` — [NEW]
- `tests/test_grammar/test_clause_segmenter.py` — [NEW]
- `tests/test_grammar/test_relation_detector.py` — [NEW]
- `tests/test_grammar/test_rule_registry.py` — [NEW]
- `tests/test_grammar/test_transfer_planner.py` — [NEW]

## Definition of Done
```
[ ] ClauseSegmenter splits Chinese text into clause list
[ ] RelationDetector identifies 16 relation types
[ ] 15+ rule modules implemented with match() + apply()
[ ] RuleRegistry loads rules + ConflictResolver resolves by priority
[ ] TransferPlanner orchestrates full grammar transfer
[ ] Grammar P0 pass rate ≥ 0.92
[ ] Rule conflict resolved by priority (higher wins)
[ ] Protected span NOT modified (A8)
[ ] Trace available for every rule decision (A7)
[ ] LexicalDecodePolicy + IdiomPolicy functional
[ ] SurfaceRealizer cleans Vietnamese output
[ ] Tests pass
```

---
Next Phase: Phase 09 — Entity Enrichment & User Review
