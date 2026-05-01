# Phase C: Context Package

Status: ⬜ Pending
Priority: P1
Duration: 1-2 sessions
Dependencies: Phase B

## Objective
Tạo `src/context/` package: tách SpeakerTracker, tạo EntitySalienceMemory, ZeroPronounDetector, VietnamesePronounSelector, RegisterPolicy, MentionMemory.

---

## Tasks

### C1 — Tạo src/context/__init__.py [NEW]

### C2 — Tách SpeakerTracker [NEW]
**File:** `src/context/speaker_tracker.py`

Tách class `SpeakerTracker` từ `src/eapee/pronoun_resolver.py` L27-88.
Mở rộng SPEECH_VERBS từ 11 → 25+:
```python
SPEECH_VERBS = [
    "说道", "说", "道", "问道", "问", "喊道", "叫道", "笑道", "怒道", "喝道", "答道",
    "冷声道", "低声道", "大声道", "沉声道", "轻声道", "厉声道", "淡淡道",
    "心中暗道", "心想", "暗想", "开口道", "接口道", "回答道",
]
```

### C3 — EntitySalienceMemory [NEW]
**File:** `src/context/entity_salience.py`

```python
@dataclass
class EntitySalience:
    entity_id: str
    last_seen_segment: str
    last_role: str        # "subject"|"object"|"possessive"|"vocative"
    salience_score: float # 1.0 = most salient, decay 0.85 per segment
    gender: str | None
    register: str | None
    mention_count: int = 0

class EntitySalienceMemory:
    def update(self, entity_id, role, segment_id) -> None
    def decay(self, segment_id) -> None    # score *= 0.85
    def get_most_salient(self, *, gender=None) -> EntitySalience | None
    def reset_chapter(self) -> None
```

### C4 — ZeroPronounDetector [NEW]
**File:** `src/context/zero_pronoun_detector.py`

30+ subject-taking verbs. Insertion conditions (ALL must be true):
1. Subject position empty before verb
2. Salient entity exists (score > 0.6)
3. Not inside dialogue/quote span
4. Ambiguity level low

### C5 — VietnamesePronounSelector + RegisterPolicy [NEW]
**Files:** `src/context/vi_pronoun_selector.py`, `src/context/register_policy.py`

14-entry register matrix (xianxia/modern/formal/casual × gender × role).
Config: `data/grammar/register_policy.yml`

### C6 — MentionMemory [NEW]
**File:** `src/context/mention_memory.py`

Refactor `_recent_mentions` từ PronounResolver.

### C7 — Wire vào PronounResolver [MODIFY]
**File:** `src/eapee/pronoun_resolver.py`

```python
from src.context.speaker_tracker import SpeakerTracker
# Remove inline SpeakerTracker class (L27-88)
# Keep all method signatures unchanged
```

### C8 — Tests [NEW]
**File:** `tests/test_context_package.py`

12+ tests covering SpeakerTracker, EntitySalience, ZeroPronoun, PronounSelector.

## Files Summary

| # | File | Action |
|---|------|--------|
| 1 | `src/context/__init__.py` | [NEW] |
| 2 | `src/context/speaker_tracker.py` | [NEW] Extract from pronoun_resolver |
| 3 | `src/context/entity_salience.py` | [NEW] |
| 4 | `src/context/zero_pronoun_detector.py` | [NEW] |
| 5 | `src/context/vi_pronoun_selector.py` | [NEW] |
| 6 | `src/context/register_policy.py` | [NEW] |
| 7 | `src/context/mention_memory.py` | [NEW] |
| 8 | `data/grammar/register_policy.yml` | [NEW] |
| 9 | `src/eapee/pronoun_resolver.py` | [MODIFY] Import from context |
| 10 | `tests/test_context_package.py` | [NEW] 12+ tests |

## Definition of Done
```
[ ] src/context/ package with 6 modules
[ ] SpeakerTracker extracted + 25+ verbs
[ ] EntitySalienceMemory with decay
[ ] ZeroPronounDetector with 30+ verbs + 4 conditions
[ ] VietnamesePronounSelector 14+ entries
[ ] RegisterPolicy + YAML config
[ ] MentionMemory refactored
[ ] PronounResolver imports from context
[ ] 223 existing tests PASS (backward compatible)
[ ] 12+ new tests pass
```

---
Previous: [Phase B](phase-B-universe-detector.md)
