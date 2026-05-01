# Phase 01: Core Governance — SegmentPacket, TraceEvent, TM Split

Status: ⬜ Pending
Priority: P0
Duration: 1-2 tuần
Dependencies: Phase 00

## Objective
Khóa governance nền trước khi thêm entity/grammar/learning. Phase quan trọng nhất để tránh hệ thống tự học sai.

## Tasks

### P1-T1 — Tạo TraceEvent
File: `src/core/trace.py`
```python
@dataclass
class TraceEvent:
    segment_id: str
    stage: str                        # "entity_scan", "grammar_rule", "noise_filter"...
    rule_id: str | None
    input_span: tuple[int, int] | None
    output_span: tuple[int, int] | None
    action: str                       # "replace", "protect", "skip", "flag"
    confidence: float
    metadata: dict
```

### P1-T2 — Tạo SegmentPacket
File: `src/pipeline/packet.py`
```python
@dataclass
class SegmentPacket:
    segment_id: str
    chapter_id: str
    position: int
    raw_text: str
    normalized_text: str
    seg_type: str                     # SegmentType enum value
    confidence: float
    protected_spans: list
    metadata: dict
    trace: list[TraceEvent]
```

### P1-T3 — Tách Translation Memory
Migration: `src/state/migrations/001_tm_split.sql`
- [ ] `tm_machine` — raw RBMT output
- [ ] `tm_reviewed` — human đã xem/sửa
- [ ] `tm_approved` — verified, canonical

### P1-T4 — Sửa TM lookup order
```
1. tm_approved exact
2. tm_approved fuzzy
3. tm_machine suggestion only
4. fallback RBMT
```

### P1-T5 — Chặn machine output vào approved TM
Test bắt buộc:
```python
def test_rbmt_output_never_goes_to_approved_tm():
    result = translator.translate("他走了。")
    assert tm_machine.exists("他走了。")
    assert not tm_approved.exists("他走了。")
```

## Files to Create/Modify
- `src/core/trace.py` — [NEW]
- `src/pipeline/packet.py` — [MODIFY] Add SegmentPacket
- `src/state/migrations/001_tm_split.sql` — [NEW]
- `src/state/translation_memory.py` — [MODIFY] Split TM

## Definition of Done
```
[ ] TraceEvent attach được vào mọi stage
[ ] SegmentPacket dùng được trong pipeline
[ ] TM tách machine/reviewed/approved
[ ] Machine output không bao giờ status verified
[ ] Test tm governance pass
```

---
Next Phase: Phase 02 — Segment/Protected/Noise
