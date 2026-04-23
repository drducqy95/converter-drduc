# Phase 03: CEDICT Enhancement

Status: ⬜ Pending
Dependencies: Phase 02

## Objective
Tăng yield từ CEDICT cross-reference bằng fuzzy matching, ADV detection, và mở rộng ADJ list.

## Implementation Steps

1. [ ] **Thêm ADV detection từ CEDICT**
   - File: `src/tools/pos_seeder.py`
   - Pattern: CEDICT meaning chứa `(adv)`, `immediately`, `suddenly`, `already`, `very`, `truly`, `gradually`
   - Tag: `ADVERB`

2. [ ] **Cải thiện VERB detection**
   - Hiện tại chỉ check meaning[0]. Fix: check `"to "` ở đầu BẤT KỲ meaning nào
   - Pattern: `to write`, `to run` → VERB

3. [ ] **Extend `_CEDICT_ADJ_HINTS`**
   - Thêm ~200 adjectives phổ biến (beautiful, cold, hot, big, small, dark, bright...)

4. [ ] **Fuzzy decomposition cho multi-char**
   - Entry `ABC` không match CEDICT → tách `AB+C` hoặc `A+BC`
   - Lấy tag từ component đã biết trong CEDICT

5. [ ] **Extract pinyin từ CEDICT → UPDATE DB**
   - CEDICT format: `繁體 简体 [pin1 yin1] /meaning/`
   - `UPDATE entries SET pinyin=? WHERE source=? AND pinyin IS NULL`

6. [ ] **Extract traditional từ CEDICT → UPDATE DB**
   - Cột 1 CEDICT = phồn thể
   - `UPDATE entries SET traditional=? WHERE source=? AND traditional IS NULL`

## Files to Create/Modify
- `src/tools/pos_seeder.py` — ADV/VERB/ADJ detection + pinyin/traditional extract

## Test Criteria
- [ ] `SELECT COUNT(*) FROM entries WHERE pos_tag='ADVERB'` > 0
- [ ] `SELECT COUNT(*) FROM entries WHERE pinyin IS NOT NULL` > 50,000
- [ ] `SELECT COUNT(*) FROM entries WHERE traditional IS NOT NULL` > 50,000
- [ ] Coverage tăng từ 26% lên ~35%

---
Next Phase: [phase-04-vi-heuristic.md](phase-04-vi-heuristic.md)
