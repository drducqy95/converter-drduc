# Phase 05: Component Decomposition Engine

Status: ⬜ Pending
Dependencies: Phase 04

## Objective
Tạo engine phân tích compound words để gán tag cho khối 3-5+ chars (450K entries, 82% gap).

## Implementation Steps

1. [ ] **Tạo file `src/tools/component_tagger.py`**
   - Class `ComponentTagger`
   - Input: danh sách source entries chưa tag
   - Output: danh sách `(source, pos_tag, pos_sub, confidence)`

2. [ ] **Implement Head-Final decomposition**
   ```
   AB   → head_pos(B) if B tagged, else head_pos(A)
   ABC  → head_pos(BC) if BC tagged, else head_pos(C)
   ABCD → head_pos(CD) if CD tagged, else head_pos(BCD), else head_pos(D)
   ```

3. [ ] **Exception rules**
   - Nếu cuối là classifier/particle → lấy component trước
   - Nếu đầu là verb → giữ VERB (verb phrase)
   - Nếu tất cả components là ADJ → ADJECTIVE

4. [ ] **Confidence scoring**
   - Cả 2 components đều tagged: confidence = HIGH
   - Chỉ 1 component tagged: confidence = MEDIUM
   - Không component nào tagged: SKIP

5. [ ] **Tích hợp vào pos_seeder.py như Tier 6**
   - `WHERE pos_tag IS NULL` guard
   - Chỉ apply entries có confidence >= MEDIUM

## Files to Create/Modify
- `src/tools/component_tagger.py` — [NEW] Component Decomposition Engine
- `src/tools/pos_seeder.py` — Tier 6 integration

## Test Criteria
- [ ] Coverage tăng từ ~48% lên ~70%
- [ ] `穿黑色` decompose thành VERB (head = 穿 = VERB)
- [ ] `黑色风衣` decompose thành NOUN (head = 风衣 = NOUN)

---
Next Phase: [phase-06-names-collocation.md](phase-06-names-collocation.md)
