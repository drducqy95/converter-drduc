# Phase 04: POS-Driven Rewrite Engine

Status: ⬜ Pending
Dependencies: Phase 03 (TrieMatch with POS data)

## Objective
Tạo `POSRewriteEngine` — hệ thống rule-based thay thế 23 regex categories cứng trong `zh_structure_rewriter.py`. Rules được kích hoạt bởi POS tags thay vì pattern matching cứng.

## Kiến Trúc

```
┌──────────────────────────────────────────┐
│  POSRewriteEngine                        │
├──────────────────────────────────────────┤
│  Input: list[TrieMatch] (with POS)       │
│                                          │
│  ┌─ Rule Registry ─────────────────────┐ │
│  │  R01: VERB+PART(的)+NOUN → swap     │ │
│  │  R02: PRON+PART(的)+NOUN → insert 的│ │
│  │  R03: ADJ+NOUN → swap              │ │
│  │  R04: PREP(把)+NOUN+VERB → SVO     │ │
│  │  R05: PREP(被)+NOUN+VERB → bị      │ │
│  │  R06: VERB+COMP → complement       │ │
│  │  R07: NUM+CLF+NOUN → classifier    │ │
│  │  R08: DEM+NUM+CLF+NOUN → reorder   │ │
│  │  R09: X+SUFFIX(似的) → invert      │ │
│  │  R10: NOUN+LOC → swap              │ │
│  │  R11: PREP+NOUN+VERB → swap        │ │
│  │  ...                               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Output: list[TrieMatch] (reordered)     │
└──────────────────────────────────────────┘
```

## Complete Cat → Rule Mapping (23 Categories)

> [!IMPORTANT]
> Bảng này là contract giữa legacy `zh_structure_rewriter.py` và POS engine mới. Mỗi Cat PHẢI có rule tương đương.

| Cat | Tên | POS Pattern | Rule | Priority |
|-----|-----|-------------|------|----------|
| 1A | Verb+Color+Item+的+Person | VERB+ADJ(color)+NOUN+PART(的)+NOUN | R01a: swap modifier block | 100 |
| 1B | Adj+的+Noun | ADJ+PART(的)+NOUN | R01b: swap adj | 100 |
| 1C | Relative Clause+的+Person | VERB+...+PART(的)+NOUN | R01c: swap clause | 100 |
| 2 | Possessive+的+BodyNoun | PRON/NOUN+PART(的)+NOUN(body) | R02: insert `của` | 90 |
| 3 | Color+Noun | ADJ(color)+NOUN | R03: swap color after | 80 |
| 4 | 把+O+V | PREP(把)+NOUN+VERB | R04: SVO restore | 110 |
| 5 | 被+Agent+V | PREP(被)+NOUN+VERB | R05: insert `bị` | 110 |
| 6 | Result Complement | VERB+COMP | R06: rewrite complement | 70 |
| 7 | Classifier Map | NUM+CLF+NOUN | R07: map CLF | 60 |
| 8 | Demonstrative | PRON(dem)+NUM+CLF+NOUN | R08: move dem to end | 85 |
| 9 | Multi-level Possessive | X+PART(的)+Y+PART(的)+Z | R09: chain reverse | 75 |
| 10 | Generic Adj+Noun | ADJ+NOUN (no 的) | R10: swap | 78 |
| 11 | Postposition | NOUN+LOC | R11: swap LOC before | 75 |
| 12 | Nested Locative | PREP(在)+...+NOUN+LOC | R12: complex swap | 72 |
| 13 | Temporal Post | VERB+X+LOC(后) | R13: insert `sau khi` | 70 |
| 14 | Spatial Hierarchy | NOUN(large)+NOUN(small) | R14: reverse order | 65 |
| 15 | Correlative Conj | CONJ(除了)+X+CONJ(还)+Y | R15: restructure | 60 |
| 16 | Prep Action | PREP(向/对/朝)+NOUN+VERB | R16: swap verb before | 80 |
| 17 | Locative Action | PREP(在)+NOUN+VERB | R17: swap verb before | 78 |
| 18 | Kinship Inversion | Name+Title | R18: title before name | 85 |
| 19 | Approx Quantity | NUM+多+CLF | R19: insert `hơn` | 55 |
| 20 | Chapter Marker | 第+NUM+章 | R20: rewrite to `Chương N` | 50 |
| 21 | Prep Verb Inv. | PREP(从)+...+VERB | R21: verb before prep | 78 |
| 22 | Temporal Clf | NUM+年/月/日 | R22: unit after number | 55 |
| 23 | Simulative | X+SUFFIX(似的/一样) | R23: `như X` | 95 |

## Implementation Steps

### 1. [ ] Create `src/engine/pos_rewrite_engine.py`

```python
@dataclass
class RewriteRule:
    name: str               # e.g. "modifier_de_noun_swap"
    condition: Callable      # func(tokens, i) -> bool
    action: Callable         # func(tokens, i) -> list[TrieMatch]
    priority: int            # higher = applied first
    description: str

class POSRewriteEngine:
    def __init__(self):
        self.rules: list[RewriteRule] = []
        self._register_builtin_rules()
    
    def rewrite(self, tokens: list[TrieMatch]) -> list[TrieMatch]:
        for rule in sorted(self.rules, key=lambda r: -r.priority):
            tokens = self._apply_rule(tokens, rule)
        return tokens
```

### 2. [ ] Implement R01: VERB+的+NOUN → NOUN+VERB (Cat.1A/1B/1C)

```python
def is_modifier_de_noun(tokens, i):
    """Detect [VERB/ADJ...] + 的 + [NOUN]"""
    if tokens[i].source != '的' or tokens[i].pos_tag != 'PART':
        return False
    has_modifier = any(t.pos_tag in ('VERB','ADJ') for t in tokens[max(0,i-5):i])
    has_head = i+1 < len(tokens) and tokens[i+1].pos_tag == 'NOUN'
    return has_modifier and has_head
```

### 3. [ ] Implement R02-R05: Possessive, Color, 把, 被

| Rule | POS Pattern | Action | Maps to Category |
|------|-------------|--------|------------------|
| R02 | PRON+PART(的)+NOUN(body) | insert `của` | Cat.2 |
| R03 | ADJ(color)+NOUN | swap → NOUN+ADJ | Cat.3 |
| R04 | PREP(把)+NOUN+VERB | → VERB+NOUN (SVO) | Cat.4 |
| R05 | PREP(被)+NOUN+VERB | insert `bị` | Cat.5 |

### 4. [ ] Implement R06-R08: Complements, Classifiers, Demonstratives

| Rule | POS Pattern | Action | Maps to Category |
|------|-------------|--------|------------------|
| R06 | VERB+COMP | rewrite complement | Cat.6 |
| R07 | NUM+CLF+NOUN | map classifier | Cat.7 |
| R08 | PRON(dem)+NUM+CLF+NOUN | reorder to end | Cat.8 |

### 5. [ ] Implement R09-R11: Suffixes, Locatives, Prepositions

| Rule | POS Pattern | Action | Maps to Category |
|------|-------------|--------|------------------|
| R09 | X+SUFFIX(似的) | invert → `như X` | Cat.23 |
| R10 | NOUN+LOC | swap → LOC+NOUN | Cat.11 |
| R11 | PREP+NOUN+VERB | swap → VERB+PREP+NOUN | Cat.16/17 |

### 6. [ ] Implement separable verb handling (离合词)
NotebookLM research: 生气, 毕业, 离婚 có `pos_sub=separable`:

```python
# DANH SÁCH ĐỘNG TỪ LY HỢP THƯỜNG GẶP
SEPARABLE_VERBS = {
    "生气": ("生", "气"),     # tức giận
    "毕业": ("毕", "业"),     # tốt nghiệp
    "离婚": ("离", "婚"),     # ly hôn
    "道歉": ("道", "歉"),     # xin lỗi
    "帮忙": ("帮", "忙"),     # giúp đỡ
    "见面": ("见", "面"),     # gặp mặt
    "睡觉": ("睡", "觉"),     # ngủ
    "吃饭": ("吃", "饭"),     # ăn cơm
    "唱歌": ("唱", "歌"),     # ca hát
    "跳舞": ("跳", "舞"),     # nhảy múa
}

def handle_separable_verb(tokens: list[TrieMatch], i: int) -> list[TrieMatch] | None:
    """Detect split separable verbs and recombine.
    
    Patterns:
    (1) V + Duration + O: 毕业三年了 → tokens: [毕, 业, 三年, 了]
        → Recombine: [毕业, 三年, 了]
    (2) V + Poss + 的 + O: 生了你的气 → tokens: [生, 了, 你, 的, 气]
        → Reorder: [生气, 你] (tức giận bạn)
    (3) Prep + O + VO: 向他道歉 → tokens: [向, 他, 道歉]
        → Keep as-is (道歉 not split)
    """
    token = tokens[i]
    if token.pos_tag != 'VERB' or 'separable' not in (token.pos_sub or ''):
        return None
    
    # Check if verb_char (first char) is at current position
    # and obj_char (second char) appears within next 5 tokens
    verb_source = token.source
    if verb_source in SEPARABLE_VERBS:
        verb_part, obj_part = SEPARABLE_VERBS[verb_source]
        # Already combined → no action needed
        return None
    
    # Check if only first char matched (split state)
    for sv_full, (v, o) in SEPARABLE_VERBS.items():
        if token.source == v:
            # Look forward for the object part
            for j in range(i+1, min(i+6, len(tokens))):
                if tokens[j].source == o:
                    # Found split → recombine
                    infix = tokens[i+1:j]  # duration/pronoun between
                    combined = TrieMatch(
                        source=sv_full, target=tokens[i].target,
                        priority=token.priority, length=len(sv_full),
                        one_mean=False, pos_tag='VERB',
                        is_function_word=False, reorder_role='modifier',
                    )
                    return [combined] + list(infix) + list(tokens[j+1:])
    return None
```

## Rule Conflict Resolution

Khi nhiều rules match cùng một chuỗi tokens:

```
1. Sort rules by priority (cao → thấp)
2. Apply rule với priority cao nhất TRƯỚC
3. Sau khi áp dụng rule, tokens ĐÃ THAY ĐỔI → re-check từ đầu
4. Mỗi token chỉ được modified BỞI MỘT rule (no double-swap)
5. Track modified indices để tránh vòng lặp vô tận
```

```python
def _apply_rule(self, tokens, rule):
    modified = set()  # indices that have been modified
    i = 0
    while i < len(tokens):
        if i not in modified and rule.condition(tokens, i):
            new_tokens, affected = rule.action(tokens, i)
            tokens = new_tokens
            modified.update(affected)  # mark as modified
        i += 1
    return tokens
```

### 7. [ ] Create rule documentation & test matrix
Document mỗi rule với input/expected output table.

## Files to Create
- `src/engine/pos_rewrite_engine.py` — **[NEW]** Main engine
- `tests/test_pos_rewrite_engine.py` — **[NEW]** Rule tests

## Test Criteria
- [ ] Each rule has ≥ 3 test cases (positive + negative)
- [ ] All 23 existing regex categories mapped to POS rules
- [ ] No regression on Chapter 1-5 translations
- [ ] Performance: rewrite ≤ 50ms per chapter

---
Next Phase: [phase-05-integration.md](phase-05-integration.md)
