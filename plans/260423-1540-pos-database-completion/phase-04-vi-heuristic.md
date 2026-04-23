# Phase 04: Vietnamese Heuristic Enhancement

Status: ⬜ Pending
Dependencies: Phase 03

## Objective
Mở rộng Tier 4 Vietnamese heuristic để tag thêm ~80K entries dựa trên target text.

## Implementation Steps

1. [ ] **Mở rộng VI_VERB_PREFIXES**
   - File: `src/tools/pos_seeder.py`
   - Thêm: `đánh`, `bắt`, `giết`, `chém`, `phá`, `kéo`, `đẩy`, `ném`, `cắt`, `đấm`, `xé`, `bóp`

2. [ ] **Thêm VI_ADV_MARKERS**
   - Markers: `đã`, `đang`, `sẽ`, `vẫn`, `cũng`, `lại`, `chỉ`, `mới`, `còn`, `từng`, `luôn`, `thường`
   - Tag: `ADVERB`

3. [ ] **Multi-meaning POS voting (Tier 5)**
   - 52,668 entries có `/` trong target
   - Tách mỗi meaning → chạy heuristic riêng → tag = majority vote
   - Ví dụ: `lãng mạn/trữ tình/mơ mộng` → 3/3 ADJ → ADJECTIVE

4. [ ] **Mở rộng VI_ADJ_MARKERS**
   - Cuối: `lắm`, `quá`, `thay`, `nhất`, `nhỉ`
   - Đầu: `thật`, `cực kỳ`, `vô cùng`, `hết sức`

5. [ ] **Intensifier-at-end pattern**
   - Entry "XYZ nhất" → ADJECTIVE (superlative)
   - Entry "XYZ lắm" → ADJECTIVE (intensifier)

## Files to Create/Modify
- `src/tools/pos_seeder.py` — Tier 4 + Tier 5 heuristics

## Test Criteria
- [ ] Coverage tăng từ ~35% lên ~48%
- [ ] `SELECT COUNT(*) FROM entries WHERE pos_tag='ADVERB'` > 5,000

---
Next Phase: [phase-05-component.md](phase-05-component.md)
