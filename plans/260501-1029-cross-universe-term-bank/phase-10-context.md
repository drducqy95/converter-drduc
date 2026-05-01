# Phase 10: Context Resolver, Zero-Pronoun, EAPEE

Status: ⬜ Pending
Priority: P1
Duration: 2 tuần
Dependencies: Phase 07 + Phase 09

## Objective
Ổn định đại từ, speaker tracking, zero-pronoun, liên kết EAPEE với UniverseContext.

---

## Tasks

### P10-T1 — EntitySalienceMemory
File: `src/context/entity_salience.py`

```python
@dataclass
class EntitySalience:
    entity_id: str
    last_seen_segment: str          # segment_id
    last_role: str                  # "subject" | "object" | "possessive" | "vocative"
    salience_score: float           # 1.0 = most salient, decays over segments
    gender: str | None              # "male" | "female" | None
    number: str | None              # "singular" | "plural" | None
    register: str | None            # "xianxia" | "modern" | "formal" | "casual"
    mention_count: int = 0          # Total mentions in current chapter
    first_seen_segment: str = ""    # First appearance

class EntitySalienceMemory:
    """Tracks entity salience across segments in a chapter."""

    def update(self, entity_id: str, role: str, segment_id: str) -> None:
        """Update salience when entity is mentioned."""

    def decay(self, segment_id: str) -> None:
        """Decay all salience scores after processing a segment."""

    def get_most_salient(self, *, gender: str | None = None) -> EntitySalience | None:
        """Return most salient entity, optionally filtered by gender."""

    def reset_chapter(self) -> None:
        """Clear memory for new chapter."""
```

Decay formula: `score *= 0.85` per segment gap (configurable).

### P10-T2 — SpeakerTracker
File: `src/context/speaker_tracker.py`

**Speech verb patterns (full list):**
```python
SPEECH_VERBS = [
    # Standard
    "说", "道", "问", "答", "叫", "喊", "吼",
    # Manner
    "冷声道", "低声道", "大声道", "笑道", "怒道",
    "淡淡道", "沉声道", "轻声道", "厉声道",
    # Internal
    "心中暗道", "心想", "暗想", "心中暗想",
    # Formal
    "开口道", "接口道", "插嘴道", "回答道",
]
```

**SpeakerAttribution dataclass:**
```python
@dataclass
class SpeakerAttribution:
    speaker_entity: str             # Entity ID of speaker
    speech_verb: str                # The verb used
    dialogue_text: str              # Content of dialogue
    segment_id: str
    confidence: float
    is_thought: bool = False        # True for 心中暗道/心想
```

**Algorithm:**
```
1. Find dialogue spans (text in "..." or 「...」)
2. Look for speech verb BEFORE or AFTER dialogue
3. Extract speaker entity from verb context (X道, X说)
4. If no explicit speaker: use most salient entity from EntitySalienceMemory
5. If alternating dialogue: infer speaker from turn-taking pattern
```

### P10-T3 — ZeroPronounDetector
File: `src/context/zero_pronoun_detector.py`

**Subject-taking verbs (complete list):**
```python
SUBJECT_VERBS = [
    # Motion
    "站", "坐", "走", "跑", "飞", "落", "停",
    # Action
    "看", "听", "拿", "放", "打", "踢", "砍", "刺",
    # Mental
    "想", "知", "觉得", "认为", "明白", "理解",
    # Speech
    "说", "叫", "喊", "问",
    # Body
    "转身", "回头", "低头", "抬头", "皱眉", "点头", "摇头",
    "伸手", "挥手", "握拳", "闭眼", "睁眼",
    # Combat (xianxia)
    "出手", "出剑", "施展", "催动", "运转", "凝聚",
]
```

**Insertion conditions (ALL must be true):**
```
1. Subject position is empty (no explicit subject before verb)
2. Salient entity exists in EntitySalienceMemory
3. Sentence needs subject clarity in Vietnamese
4. Ambiguity level is low (salient score > 0.6)
5. Not inside a quote/dialogue span
```

**ZeroPronounInsertion dataclass:**
```python
@dataclass
class ZeroPronounInsertion:
    position: int                   # Insert position in Vietnamese text
    pronoun: str                    # Vietnamese pronoun to insert
    referent_entity: str            # Entity ID being referenced
    confidence: float
    reason: str                     # "subject_omitted_verb_X"
```

### P10-T4 — VietnamesePronounSelector
File: `src/context/vi_pronoun_selector.py`

**Full register matrix:**

| Register | Gender | Role | Vietnamese |
|----------|--------|------|------------|
| xianxia | male | third person | hắn |
| xianxia | female | third person | nàng |
| xianxia | male | elder/senior | lão |
| xianxia | female | elder/senior | lão bà |
| xianxia | — | master relation | sư phụ |
| xianxia | — | disciple | đồ đệ |
| modern | male | third person | anh ta |
| modern | female | third person | cô ấy |
| modern | male | elder | ông ta |
| modern | female | elder | bà ta |
| formal | — | first person | ta / bần đạo / bổn tọa |
| casual | male | first person | tao |
| casual | — | second person | ngươi / mi |
| neutral | — | it/they | nó / chúng |

**RegisterPolicy:**
File: `src/context/register_policy.py`
```python
class RegisterPolicy:
    def select_pronoun(
        self,
        entity: EntitySalience,
        universe_context: UniverseContext | None,
        relation_to_speaker: str | None,
    ) -> str:
        """Select Vietnamese pronoun based on register + context."""
```

Config: `data/grammar/register_policy.yml`

### P10-T5 — EAPEE Integration
File: `src/eapee/pronoun_resolver.py` — [MODIFY]

```python
class PronounResolver:
    def resolve(
        self,
        segment: SegmentPacket,
        *,
        universe_context: UniverseContext | None = None,
        salience_memory: EntitySalienceMemory | None = None,
    ) -> SegmentPacket:
        """
        Resolve pronouns using:
        1. SpeakerTracker → attribute dialogue
        2. ZeroPronounDetector → find omitted subjects
        3. VietnamesePronounSelector → pick correct pronoun
        4. RegisterPolicy → adjust for universe register
        """
```

### P10-T6 — MentionMemory
File: `src/context/mention_memory.py`

Track cross-segment entity mentions for coreference:
```python
class MentionMemory:
    def add_mention(self, entity_id: str, segment_id: str, role: str) -> None:
    def get_chain(self, entity_id: str) -> list[Mention]:
    def get_active_entities(self, *, window: int = 5) -> list[str]:
```

## Files to Create/Modify
- `src/context/__init__.py` — [NEW]
- `src/context/speaker_tracker.py` — [NEW]
- `src/context/entity_salience.py` — [NEW]
- `src/context/zero_pronoun_detector.py` — [NEW]
- `src/context/vi_pronoun_selector.py` — [NEW]
- `src/context/register_policy.py` — [NEW]
- `src/context/mention_memory.py` — [NEW]
- `src/eapee/pronoun_resolver.py` — [MODIFY] Accept UniverseContext
- `data/grammar/register_policy.yml` — [NEW]
- `tests/test_context/test_speaker_tracker.py` — [NEW]
- `tests/test_context/test_zero_pronoun_detector.py` — [NEW]
- `tests/test_context/test_vi_pronoun_selector.py` — [NEW]

## Definition of Done
```
[ ] EntitySalienceMemory tracks salience with decay
[ ] SpeakerTracker detects speaker from 20+ speech verbs
[ ] Speaker attribution accuracy ≥ 0.90
[ ] ZeroPronounDetector with 30+ subject-taking verbs
[ ] Insertion only when ALL 5 conditions met
[ ] Zero-pronoun false insertion ≤ 0.08
[ ] VietnamesePronounSelector full register matrix (14+ entries)
[ ] RegisterPolicy configurable via YAML
[ ] Pronoun consistency ≥ 0.85
[ ] EAPEE PronounResolver receives UniverseContext
[ ] MentionMemory tracks cross-segment chains
[ ] Tests pass
```

---
Next Phase: Phase 11 — Metadata DB & Learning Loop
