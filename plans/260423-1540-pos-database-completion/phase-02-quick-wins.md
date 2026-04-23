# Phase 02: Quick Wins Tagging

Status: ⬜ Pending
Dependencies: Phase 01

## Objective
Gán tag cho các categories nhỏ đã xác định rõ: pronouns, misc_vocabulary, latin_num.

## Implementation Steps

1. [ ] **Gán tag 11 pronouns còn lại**
   - File: `src/tools/pos_seeder.py` (Tier 1 SEEDS)
   - Entries: `我们`→PRONOUN, `你`→PRONOUN, `他`→PRONOUN, `自己`→PRONOUN, `别人`→PRONOUN, `您`→PRONOUN, `咱们`→PRONOUN, `您们`→PRONOUN, `大伙儿`→PRONOUN, `自个儿`→PRONOUN, `你娘亲`→PRONOUN

2. [ ] **Gán tag misc_vocabulary (5 entries)**
   - `老师们`→NOUN, `同学们`→NOUN, `少爷`→NOUN, `伤天`→NOUN, `别人`→NOUN

3. [ ] **Gán tag latin_num pattern `X月`**
   - SQL: `UPDATE entries SET pos_tag='NOUN', pos_sub='time' WHERE category='vietphrase_latin_num' AND source LIKE '%月' AND pos_tag IS NULL`

4. [ ] **Gán tag latin_num pattern `X市`**
   - SQL: `UPDATE entries SET pos_tag='NOUN', pos_sub='location' WHERE category='vietphrase_latin_num' AND source LIKE '%市' AND pos_tag IS NULL`

5. [ ] **Gán tag latin_num số thuần**
   - Regex: entries thuần số/latin → `NUMBER` hoặc `NOUN/misc`

## Files to Create/Modify
- `src/tools/pos_seeder.py` — Extended Tier 1 seeds + latin_num logic

## Test Criteria
- [ ] `SELECT COUNT(*) FROM entries WHERE category='pronouns' AND pos_tag IS NULL` = 0
- [ ] `SELECT COUNT(*) FROM entries WHERE category='vietphrase_latin_num' AND pos_tag IS NULL` giảm >50%

---
Next Phase: [phase-03-cedict.md](phase-03-cedict.md)
