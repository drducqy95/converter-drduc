# Phase 02: POS Auto-Seeding Pipeline

Status: ⬜ Pending
Dependencies: Phase 01 (schema must exist)

## Objective
Tạo pipeline tự động gán POS tag cho 724K entries bằng heuristics, CC-CEDICT cross-reference, và category-based inference. Ưu tiên seed top ~5,000 high-frequency entries trước.

## Chiến Lược Seeding (4 Tầng)

### Tầng 1: Hardcoded Seeds (100% accuracy, ~500 entries)
Danh sách từ đã biết chính xác POS:

```python
HARDCODED_POS = {
    # Particles (PART)
    "的": ("PART", "structural"), "了": ("PART", "aspect"),
    "着": ("PART", "progressive"), "过": ("PART", "experiential"),
    "吗": ("PART", "question"), "吧": ("PART", "suggestion"),
    "呢": ("PART", "question"), "啊": ("INTJ", None),
    
    # Prepositions (PREP)
    "在": ("PREP", "locative"), "从": ("PREP", "source"),
    "向": ("PREP", "directional"), "对": ("PREP", "target"),
    "把": ("PREP", "ba_construction"), "被": ("PREP", "passive"),
    "给": ("PREP", "dative"), "朝": ("PREP", "directional"),
    
    # Auxiliaries (AUX)
    "会": ("AUX", "modal"), "能": ("AUX", "ability"),
    "可以": ("AUX", "permission"), "要": ("AUX", "intention"),
    "应该": ("AUX", "obligation"), "必须": ("AUX", "necessity"),
    
    # Suffixes (SUFFIX)
    "似的": ("SUFFIX", "simulative"), "一样": ("SUFFIX", "simulative"),
    "一般": ("SUFFIX", "simulative"),
    
    # Locatives (LOC)
    "上": ("LOC", "above"), "下": ("LOC", "below"),
    "里": ("LOC", "inside"), "外": ("LOC", "outside"),
    "前": ("LOC", "front"), "后": ("LOC", "back"),
    "面前": ("LOC", "in_front"), "里面": ("LOC", "inside"),
    "上面": ("LOC", "above"), "下面": ("LOC", "below"),
    "旁边": ("LOC", "beside"),
    
    # Complements (COMP)
    "出来": ("COMP", "directional"), "起来": ("COMP", "directional"),
    "下去": ("COMP", "directional"), "过来": ("COMP", "directional"),
    "出去": ("COMP", "directional"),
}
```

### Tầng 2: Category Inference (~20K entries, 95% accuracy)
Gán POS tự động dựa trên `category` đã có:

| Category | Auto POS | Confidence |
|----------|----------|------------|
| `names_person_*` | NOUN + entity_type=person | 99% |
| `names_loc_*` | NOUN + entity_type=location | 99% |
| `names_org_*` | NOUN + entity_type=organization | 99% |
| `trichdan_idioms` | IDIOM | 95% |
| `pronouns` | PRON | 100% |

### Tầng 3: CC-CEDICT Cross-Reference (~50K entries)
Parse CC-CEDICT (open-source Chinese dictionary, 120K+ entries) để lấy POS:

```python
import re

# CC-CEDICT format: 走 走 [zǒu] /to walk/to go/to run/.../
CEDICT_LINE = re.compile(r'^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/(.+)/$')

# POS inference from English definitions:
POS_PATTERNS = [
    # VERB: "to X" or "(V) to X"
    (re.compile(r'^to\s+\w+', re.I), 'VERB'),
    # NOUN: "a/an/the X" or explicit "(N)"
    (re.compile(r'^(a|an|the)\s+\w+', re.I), 'NOUN'),
    # ADJ: standalone adjective-like (no article, no "to")
    (re.compile(r'^(big|small|beautiful|ugly|fast|slow|old|new|good|bad|\w+ful|\w+ous|\w+ive|\w+able|\w+ish)$', re.I), 'ADJ'),
    # CLF: "classifier for X" or "(CL)"
    (re.compile(r'classifier\s+for|^\(CL\)', re.I), 'CLF'),
    # CONJ: "and/but/or/although"
    (re.compile(r'^(and|but|or|although|however|therefore)$', re.I), 'CONJ'),
    # ADV: standalone adverb or ending in -ly
    (re.compile(r'^(very|quite|already|still|also|even|just|only|\w+ly)$', re.I), 'ADV'),
]

def infer_pos_from_cedict(definitions: list[str]) -> str | None:
    for defn in definitions:
        defn_clean = defn.strip()
        for pattern, pos in POS_PATTERNS:
            if pattern.search(defn_clean):
                return pos
    return None
```

**Xử lý conflict**: Khi CC-CEDICT POS khác với Tầng 1 (hardcoded), **Tầng 1 luôn thắng** vì độ chính xác 100%.

### Tầng 4: Vietnamese Target Heuristics (~100K entries)
Phân tích `target` text để suy luận POS dựa trên các pattern tiếng Việt:

```python
# ========== VERB indicators ==========
VIET_VERB_PREFIXES = (
    "mặc", "ăn", "uống", "đi", "chạy", "nói", "viết", "nhìn", "xem",
    "nghe", "cầm", "lấy", "đánh", "giết", "bắn", "ném", "kéo", "đẩy",
    "mở", "đóng", "cắt", "rửa", "giặt", "nấu", "chiên", "nướng",
    "quỳ", "ngồi", "nằm", "đứng", "bay", "bơi", "nhảy", "leo",
    "trèo", "lái", "dẫn", "mang", "vác", "gánh", "bưng", "xách",
    "hỏi", "đáp", "kêu", "gọi", "hét", "la", "khóc", "cười",
    "tìm", "kiếm", "chọn", "lựa", "bỏ", "nhặt", "lượm", "thu",
)

# ========== ADJ indicators ==========
VIET_ADJ_WORDS = (
    "xinh", "đẹp", "lớn", "nhỏ", "trắng", "đen", "đỏ", "xanh",
    "vàng", "tím", "nâu", "hồng", "tốt", "xấu", "nhanh", "chậm",
    "cao", "thấp", "dài", "ngắn", "rộng", "hẹp", "dày", "mỏng",
    "nặng", "nhẹ", "cứng", "mềm", "nóng", "lạnh", "ẩm", "khô",
    "sạch", "bẩn", "mới", "cũ", "trẻ", "già", "giàu", "nghèo",
    "vui", "buồn", "giận", "sợ", "lo", "sống", "chết",
)

# ========== NOUN indicators ==========
VIET_NOUN_SUFFIXES = (
    "viên", "sư", "gia", "sĩ", "phủ", "thầy", "cô", "chủ",
    "thuật", "pháp", "kiếm", "cung", "đao", "thương",
)

def infer_pos_from_target(target: str) -> str | None:
    first_meaning = target.split('/')[0].split(';')[0].strip().lower()
    
    # Check verb patterns
    for prefix in VIET_VERB_PREFIXES:
        if first_meaning.startswith(prefix):
            return 'VERB'
    
    # Check adj patterns
    for adj in VIET_ADJ_WORDS:
        if first_meaning == adj or first_meaning.endswith(adj):
            return 'ADJ'
    
    # Check noun suffix patterns (Sino-Vietnamese)
    for suffix in VIET_NOUN_SUFFIXES:
        if first_meaning.endswith(suffix):
            return 'NOUN'
    
    return None
```

### Thứ Tự Ưu Tiên Seeding (Conflict Resolution)

```
Tầng 1 (Hardcoded)  >  Tầng 2 (Category)  >  Tầng 3 (CC-CEDICT)  >  Tầng 4 (Heuristics)
    100% accuracy          99% accuracy           ~85% accuracy           ~70% accuracy
```

Khi có conflict giữa các tầng: **tầng số nhỏ luôn thắng**. Tầng sau chỉ được ghi nếu entry chưa có POS.

## Implementation Steps

1. [ ] Create `src/tools/pos_seeder.py` — orchestration script
2. [ ] Implement Tầng 1: hardcoded seed loading
3. [ ] Implement Tầng 2: category inference engine
4. [ ] Download & parse CC-CEDICT for Tầng 3
5. [ ] Implement Tầng 4: Vietnamese target heuristics
6. [ ] Create validation report: POS coverage statistics
7. [ ] Manual review & correction for top 500 high-frequency entries
8. [ ] Recompile dictionary with POS data → `trie_cache.db`

## Files to Create/Modify
- `src/tools/pos_seeder.py` — **[NEW]** POS seeding orchestrator
- `src/tools/cedict_parser.py` — **[NEW]** CC-CEDICT parser
- `data/external/cedict_ts.u8` — **[NEW]** CC-CEDICT data file
- `data/dictionaries/_compiled/trie_cache.db` — Updated with POS

## Test Criteria
- [ ] ≥ 90% coverage for 1-char entries (3,424 total)
- [ ] ≥ 80% coverage for 2-char entries (114,955 total)
- [ ] ≥ 50% overall coverage for all entries
- [ ] Coverage report generated: `reports/pos_coverage.json`

## Xử Lý Đa Nghĩa (Polysemy)

> [!WARNING]
> Từ đa nghĩa như `好` (ADJ/ADV/VERB), `在` (PREP/VERB/ADV) cần xử lý đặc biệt.

**Chiến lược**: Gán POS **chủ đạo** (dominant POS) + liệt kê alternatives trong `pos_sub`:
```json
{"source": "好", "pos_tag": "ADJ", "pos_sub": "evaluative|ADV:degree|VERB:like"}
```

---
Next Phase: [phase-03-trie-enhancement.md](phase-03-trie-enhancement.md)
