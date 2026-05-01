# Phase 02: Segment Typing, Protected Span, Noise Filter

Status: ⬜ Pending
Priority: P0
Duration: 2 tuần
Dependencies: Phase 01

## Objective
Tách đúng loại segment, bảo vệ nội dung thật, lọc rác an toàn. Tuân thủ A8 + A9.

---

## Tasks

### P2-T1 — SegmentType enum
File: `src/pipeline/segment_classifier.py`
```python
class SegmentType(Enum):
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    THOUGHT = "thought"
    SYSTEM_PROMPT = "system_prompt"
    CHAPTER_TITLE = "chapter_title"
    AUTHOR_NOTE = "author_note"
    ADVERTISEMENT = "advertisement"
    FORUM_POST = "forum_post"
    UNKNOWN = "unknown"
```

### P2-T2 — SegmentClassifier
File: `src/pipeline/segment_classifier.py`

Pattern groups:

| Pattern | Type | Ví dụ |
|---------|------|-------|
| `第X章` / `第X节` / `卷X` | CHAPTER_TITLE | 第一百二十三章 |
| `X说/道/喊` + `"..."` | DIALOGUE | 李宇冷声道："你走吧。" |
| `X心中暗道` / `X想` (no quote) | THOUGHT | 他心中暗想 |
| `【面板...】` / `【系统...】` standalone | SYSTEM_PROMPT | 【面板未开启】 |
| `PS:` / `作者有话说` / `本章完` | AUTHOR_NOTE | PS: 今天三更 |
| `求收藏` / `求推荐` / `求月票` | ADVERTISEMENT | 新书上传，求收藏推荐。 |
| `楼主` / `沙发` / `回复` | FORUM_POST | 10楼: 沙发！ |
| Else | NARRATION | 他激活了【蜘蛛感应】技能。 |

Test cases bắt buộc:
```python
def test_system_prompt():
    assert classify("【面板未开启】") == SegmentType.SYSTEM_PROMPT

def test_narration_with_bracket_entity():
    # Bracket entity INSIDE narration — NOT system prompt
    assert classify("他激活了【蜘蛛感应】技能。") == SegmentType.NARRATION

def test_dialogue():
    assert classify('李宇冷声道："你走吧。"') == SegmentType.DIALOGUE

def test_chapter_title():
    assert classify("第一百二十三章 龙吟虎啸") == SegmentType.CHAPTER_TITLE
```

### P2-T3 — ProtectedSpanRegistry
File: `src/pipeline/protected_span_registry.py`

**SpanType enum:**
```python
class SpanType(Enum):
    ENTITY = "entity"
    NUMBER = "number"
    QUOTE = "quote"
    SYSTEM_UI = "system_ui"
    CHAPTER_TITLE = "chapter_title"
    IDIOM = "idiom"
    TIME = "time"
    DATE = "date"
    RANK = "rank"
    TECH_VERSION = "tech_version"
    BRACKET_ITEM = "bracket_item"
```

**ProtectedSpan dataclass:**
```python
@dataclass
class ProtectedSpan:
    start: int
    end: int
    span_type: SpanType
    priority: int
    original_text: str
    replacement: str | None = None
    locked: bool = False  # True = absolutely no modification
```

**Priority system:**
```
100 — system UI / title locked
 90 — approved entity
 80 — quote span
 70 — number / rank / time / date
 60 — idiom literal forbidden
 50 — soft entity candidate
```

Overlap rules: higher priority wins; same priority → longer span wins.

### P2-T4 — NoiseFilterWithSafeWhitelist
File: `src/pipeline/noise_filter.py`

**Algorithm (A9 compliant):**
```
1. hard_keep_patterns match? → KEEP (bypass scoring)
2. stop_phrase_patterns full-line match? → DROP
3. Partial match + real content → strip noise only, KEEP content
4. Score remaining → threshold > 0.8 → DROP
```

**Hard keep patterns** (`data/noise/hard_keep_patterns.yml`):
```yaml
system_brackets:
  - "【系统.*?】"
  - "【面板.*?】"
  - "【任务.*?】"
  - "【技能.*?】"
  - "【奖励.*?】"
entity_action:
  - ".+【.+】.+"    # bracket entity inside narration
  - "获得【.+】"
  - "激活【.+】"
```

**Stop phrase patterns** (`data/noise/stop_phrase_patterns.yml`):
```yaml
author_note: ["PS:", "PS：", "作者有话说", "本章完", "未完待续"]
solicitation: ["求收藏", "求推荐", "求月票", "求订阅", "求打赏", "新书上传", "打赏"]
```

Test cases:
```python
def test_hard_keep_system_panel():
    assert noise_filter.process("【面板未开启】").kept == True

def test_drop_solicitation():
    assert noise_filter.process("新书上传，求收藏推荐。").dropped == True

def test_keep_mixed_content():
    result = noise_filter.process("他转身离去。（求收藏）")
    assert "他转身离去" in result.text
```

## Files to Create/Modify
- `src/pipeline/segment_classifier.py` — [MODIFY] SegmentType enum + classifier
- `src/pipeline/protected_span_registry.py` — [MODIFY] SpanType + priority + overlap
- `src/pipeline/noise_filter.py` — [MODIFY] Whitelist-first + scoring fallback
- `data/noise/hard_keep_patterns.yml` — [NEW]
- `data/noise/soft_keep_patterns.yml` — [NEW]
- `data/noise/stop_phrase_patterns.yml` — [NEW]
- `data/noise/author_note_patterns.yml` — [NEW]
- `data/noise/forum_patterns.yml` — [NEW]
- `data/noise/advertisement_patterns.yml` — [NEW]
- `tests/test_pipeline/test_segment_classifier.py` — [NEW]
- `tests/test_pipeline/test_protected_span_registry.py` — [NEW]
- `tests/test_pipeline/test_noise_filter.py` — [NEW]

## Definition of Done
```
[ ] SegmentType enum 9 types
[ ] SegmentClassifier pattern rules for all types
[ ] Segment typing macro-F1 ≥ 0.93 trên seed gold
[ ] ProtectedSpanRegistry 11 span types + priority system
[ ] Overlap resolution: higher priority → longer span
[ ] Noise false drop ≤ 0.02
[ ] System panel không bị drop (hard keep)
[ ] Ad/author note bị drop/metadata
[ ] Mixed content: strip noise suffix, keep content
[ ] All noise data YML files created
[ ] Full regression pass
```

---
Next Phase: Phase 03 — Grammar Pattern Scanner
