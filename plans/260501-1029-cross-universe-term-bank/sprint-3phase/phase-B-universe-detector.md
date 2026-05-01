# Phase B: Universe Detector Module

Status: ⬜ Pending
Priority: P1
Duration: 1 session
Dependencies: Phase A (term bank phải có ≥800 records)

## Objective

Tách logic `detect_universe()` phân tán trong `term_bank.py` + `entity_scanner.py` thành module riêng `UniverseDetector`. Tạo `fingerprints.json` cho tất cả universes.

---

## Tasks

### B1 — Tạo fingerprints.json

**File:** `data/term_bank/universes/fingerprints.json`  
**Action:** [NEW]

Sau khi Phase A hoàn thành, mỗi universe có `terms.jsonl`. Script sẽ auto-generate fingerprints từ data:

```python
# scripts/generate_fingerprints.py  [NEW]
"""
Auto-generate fingerprints.json from term_bank data.

Logic cho mỗi universe:
1. Load terms.jsonl
2. fingerprint_terms = top 8 terms by entity_type priority:
   - realm/technique terms → weight 1.2 (domain fingerprints)
   - unique person names (not in any other universe) → weight 2.0
   - item/weapon → weight 1.0
3. canonical_chars = person entities with confidence ≥ 0.9, max 5
4. co_occurrence_seeds = pairs of canonical_chars that ALWAYS co-occur
   (from context_markers + co_occurring_entities)
5. exclusion_terms = terms that appear in THIS universe but are
   commonly confused with another universe
"""
```

**Output format:**
```json
{
  "version": 1,
  "generated_at": "2026-05-01T20:00:00+07:00",
  "universes": {
    "pham_nhan_tu_tien": {
      "work": "Phàm Nhân Tu Tiên",
      "franchise": "Tu Tiên",
      "fingerprint_terms": [
        {"term": "韩立", "weight": 2.5, "type": "person"},
        {"term": "灵根", "weight": 1.5, "type": "realm"},
        {"term": "筑基", "weight": 1.2, "type": "realm"},
        {"term": "元婴", "weight": 1.3, "type": "realm"},
        {"term": "黄枫谷", "weight": 2.0, "type": "location"},
        {"term": "掌天瓶", "weight": 2.0, "type": "item"}
      ],
      "canonical_chars": ["韩立", "南宫婉", "厉飞雨"],
      "co_occurrence_seeds": [
        {"pair": ["韩立", "南宫婉"], "confidence": 0.99},
        {"pair": ["韩立", "掌天瓶"], "confidence": 0.95}
      ],
      "exclusion_terms": []
    },
    "dau_pha_thuong_khung": {
      "work": "Đấu Phá Thương Khung",
      "franchise": "Đấu Khí",
      "fingerprint_terms": [
        {"term": "萧炎", "weight": 2.5, "type": "person"},
        {"term": "斗气", "weight": 1.5, "type": "realm"},
        {"term": "异火", "weight": 1.5, "type": "item"},
        {"term": "斗帝", "weight": 1.3, "type": "realm"}
      ],
      "canonical_chars": ["萧炎", "药尘", "萧薰儿"],
      "co_occurrence_seeds": [
        {"pair": ["萧炎", "药尘"], "confidence": 0.99}
      ]
    },
    "bleach": {
      "work": "Bleach",
      "franchise": "Bleach",
      "fingerprint_terms": [],
      "canonical_chars": [],
      "co_occurrence_seeds": []
    }
    // ... tất cả 18+ universes
  },
  "config": {
    "multi_universe_threshold": 0.65,
    "min_confidence_for_active": 0.4,
    "fingerprint_base_divisor": 2.0,
    "canonical_char_boost": 3.0,
    "co_occurrence_pair_boost": 5.0
  }
}
```

**Universes cần fingerprints:**
1. `pham_nhan_tu_tien` — có data tốt nhất (14.6 KB source)
2. `dau_pha_thuong_khung`
3. `dau_la_dai_luc`
4. `gia_thien`
5. `hoan_my_the_gioi`
6. `kiem_lai`
7. `quy_bi_chi_chu`
8. `than_an_vuong_toa`
9. `tien_nghich`
10. `tru_tien`
11. `tuyet_trung_han_dao_hanh`
12. `vu_dong_can_khon`
13. `marvel`
14. `harry_potter`
15. `the_one_ring`
16. `bleach`
17. `naruto`
18. `one_piece`
19. `one_punch_man`
20. `doremon`
21. `hollywood`
22. `manga_shared`

---

### B2 — Tạo UniverseDetector module

**File:** `src/pipeline/universe_detector.py`  
**Action:** [NEW]

```python
"""Standalone universe detection with fingerprint-based scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_FINGERPRINTS_PATH = Path(__file__).resolve().parents[2] / "data" / "term_bank" / "universes" / "fingerprints.json"


@dataclass(frozen=True)
class UniverseSignal:
    """Detection result for one universe."""
    universe_id: str
    confidence: float
    matched_fingerprints: list[str] = field(default_factory=list)
    matched_characters: list[str] = field(default_factory=list)
    work: str = ""
    franchise: str = ""


@dataclass
class UniverseContext:
    """Aggregated detection result."""
    active_universes: list[str]         # universe_ids with confidence ≥ threshold
    signals: list[UniverseSignal]       # sorted by confidence desc
    primary_universe: str | None        # highest confidence, None if unknown
    is_multi_universe: bool             # ≥ 2 universes above threshold
    is_unknown: bool                    # no universe detected


class UniverseDetector:
    """Detect active universes from text using fingerprints + term bank."""

    def __init__(
        self,
        fingerprints_path: Path | str | None = None,
        *,
        term_bank: "TermBank | None" = None,
    ):
        self._fp_path = Path(fingerprints_path or DEFAULT_FINGERPRINTS_PATH)
        self._fingerprints: dict | None = None
        self._config: dict = {}
        self._term_bank = term_bank

    @property
    def fingerprints(self) -> dict:
        if self._fingerprints is None:
            self._fingerprints, self._config = self._load_fingerprints()
        return self._fingerprints

    def detect(self, text: str) -> UniverseContext:
        """
        Full-text universe detection.

        Algorithm (3-pass):
        1. Weighted fingerprint scan — each term hit → +weight
        2. Canonical character scan — char present → +canonical_char_boost (3.0)
        3. Co-occurrence pair scan — both chars present → +pair_confidence * co_occurrence_pair_boost (5.0)
        4. Normalize: confidence = score / (score + base_divisor)
        5. Filter by min_confidence_for_active
        6. If ≥2 universes > multi_universe_threshold → is_multi_universe
        """

    def detect_sentence_level(
        self,
        sentences: list[str],
        *,
        context_radius: int = 1,
    ) -> list[UniverseContext]:
        """
        Per-sentence detection with ±context_radius sentence window.

        For sentence[i], context = sentences[max(0,i-radius):i+radius+1]
        """

    def get_universe_info(self, universe_id: str) -> dict | None:
        """Return fingerprint data for a universe."""

    def _score_universe(self, text: str, universe_id: str, fp_data: dict) -> UniverseSignal:
        """Score one universe against text."""

    def _load_fingerprints(self) -> tuple[dict, dict]:
        """Load fingerprints.json, return (universes, config)."""
```

**Backward compatibility:**
- `detect()` output can be converted to `list[tuple[str, float]]` for existing callers:
  ```python
  [(sig.universe_id, sig.confidence) for sig in ctx.signals]
  ```

---

### B3 — Wire UniverseDetector vào EntityScanner

**File:** `src/pipeline/entity_scanner.py`  
**Action:** [MODIFY]

Thay đổi tối thiểu:

```python
# Line ~303: Add import
from src.pipeline.universe_detector import UniverseDetector

# Line ~307: In __init__, add:
self._universe_detector = UniverseDetector(term_bank=self.term_bank)

# Line 479-480: Replace detect_universe
def detect_universe(self, text: str) -> list[tuple[str, float]]:
    ctx = self._universe_detector.detect(text)
    return [(sig.universe_id, sig.confidence) for sig in ctx.signals]

# NEW method:
def detect_universe_context(self, text: str) -> UniverseContext:
    """Return full UniverseContext (new API)."""
    return self._universe_detector.detect(text)
```

**Giữ nguyên:**
- `scan()` method vẫn gọi `self.term_bank.detect_universe()` trong L333-336
  → Cập nhật L333-336 để gọi `self._universe_detector.detect()` thay vì `self.term_bank.detect_universe()`

```python
# BEFORE (L332-337):
active_universes = [
    universe
    for universe, confidence in self.term_bank.detect_universe(text)
    if confidence >= 0.5
]

# AFTER:
ctx = self._universe_detector.detect(text)
active_universes = ctx.active_universes
```

---

### B4 — Tạo tests

**File:** `tests/test_universe_detector.py`  
**Action:** [NEW]

```python
"""Tests for UniverseDetector module."""

import pytest
from src.pipeline.universe_detector import UniverseDetector, UniverseContext, UniverseSignal


class TestUniverseDetector:

    @pytest.fixture
    def detector(self):
        return UniverseDetector()

    # --- Single universe detection ---

    def test_detect_xianxia_by_character(self, detector):
        """韩立 alone → pham_nhan_tu_tien."""
        ctx = detector.detect("韩立拿出掌天瓶")
        assert ctx.primary_universe == "pham_nhan_tu_tien"
        assert not ctx.is_multi_universe

    def test_detect_dau_khi_by_fingerprint(self, detector):
        """斗气 + 异火 → dau_pha_thuong_khung."""
        ctx = detector.detect("萧炎催动斗气，异火出现")
        assert ctx.primary_universe == "dau_pha_thuong_khung"

    def test_detect_bleach(self, detector):
        """Bleach characters → bleach universe."""
        ctx = detector.detect("黒崎一護使出斩魄刀")
        assert ctx.primary_universe == "bleach"

    def test_detect_naruto(self, detector):
        """Naruto characters → naruto universe."""
        ctx = detector.detect("漩涡鸣人使用影分身")
        assert ctx.primary_universe == "naruto"

    # --- Multi-universe ---

    def test_multi_universe(self, detector):
        """Multiple universe chars → is_multi_universe."""
        ctx = detector.detect("韩立和萧炎在一起")
        assert ctx.is_multi_universe
        assert len(ctx.active_universes) >= 2

    # --- Unknown ---

    def test_unknown_fallback(self, detector):
        """No fingerprint → is_unknown."""
        ctx = detector.detect("今天天气不错")
        assert ctx.is_unknown
        assert ctx.primary_universe is None

    # --- Co-occurrence boost ---

    def test_co_occurrence_boost(self, detector):
        """韩立+南宫婉 → higher confidence than 韩立 alone."""
        ctx_single = detector.detect("韩立走了过来")
        ctx_pair = detector.detect("韩立和南宫婉走了过来")
        sig_single = next(s for s in ctx_single.signals if s.universe_id == "pham_nhan_tu_tien")
        sig_pair = next(s for s in ctx_pair.signals if s.universe_id == "pham_nhan_tu_tien")
        assert sig_pair.confidence > sig_single.confidence

    # --- Sentence-level ---

    def test_sentence_level_detection(self, detector):
        """Per-sentence detection."""
        sentences = [
            "韩立走进了黄枫谷",
            "他坐下来修炼灵气",
            "这时南宫婉走了过来",
        ]
        results = detector.detect_sentence_level(sentences)
        assert len(results) == 3
        for r in results:
            assert r.primary_universe == "pham_nhan_tu_tien"

    # --- Backward compat ---

    def test_backward_compat_tuple_format(self, detector):
        """Can convert to list[tuple[str,float]] for existing callers."""
        ctx = detector.detect("萧炎催动斗气")
        tuples = [(s.universe_id, s.confidence) for s in ctx.signals]
        assert len(tuples) >= 1
        assert isinstance(tuples[0][0], str)
        assert isinstance(tuples[0][1], float)
```

---

## Files to Create/Modify

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `scripts/generate_fingerprints.py` | [NEW] | Auto-generate fingerprints from term bank |
| 2 | `data/term_bank/universes/fingerprints.json` | [NEW] | 22 universe fingerprints + config |
| 3 | `src/pipeline/universe_detector.py` | [NEW] | UniverseDetector class |
| 4 | `src/pipeline/entity_scanner.py` | [MODIFY] | Wire detector, replace detect_universe |
| 5 | `tests/test_universe_detector.py` | [NEW] | 9 test cases |

## Definition of Done

```
[ ] fingerprints.json exists with ≥ 18 universes
[ ] generate_fingerprints.py can regenerate from term bank data
[ ] UniverseDetector class implemented:
    [ ] detect() — full-text, 3-pass algorithm
    [ ] detect_sentence_level() — per-sentence + context radius
    [ ] UniverseSignal dataclass
    [ ] UniverseContext dataclass
[ ] EntityScanner wired to use UniverseDetector
[ ] Backward compatible: existing detect_universe() returns same format
[ ] 9 new tests pass
[ ] All 223+ existing tests pass (no regressions)
```

---
Previous Phase: [Phase A — Data Migration](phase-A-migration.md)  
Next Phase: [Phase C — Context Package](phase-C-context-package.md)
