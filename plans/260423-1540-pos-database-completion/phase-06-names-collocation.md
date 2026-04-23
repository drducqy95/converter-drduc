# Phase 06: Name Entity Taxonomy & COLLOCATION Tag

Status: ⬜ Pending
Dependencies: Phase 05

## Objective
Mở rộng entity_type taxonomy (6 loại) với LuatNhan alignment và gán COLLOCATION cho long vietphrase.

## Implementation Steps — Names

1. [ ] **Extend Tier 2: category → entity_type mapping**
   - File: `src/tools/pos_seeder.py`
   - `names_loc_east/west` → `entity_type='location'`
   - `names_org_east/west` → `entity_type='organization'`
   - `names_person_east/west` → `entity_type='person'` (đã có)

2. [ ] **Auto-classify `names_misc_*` bằng suffix**
   ```python
   WEAPON_SUFFIX = {"剑","刀","枪","戟","斧","弓","鞭","锤","矛","弩"}
   FACTION_SUFFIX = {"宗","派","门","阁","殿","堂","盟","会","教","帮"}
   ARTIFACT_SUFFIX = {"丹","珠","玉","印","镜","鼎","符","塔","令","旗"}
   ```

3. [ ] **Đặt `luat_nhan_trigger=1` cho ALL name entities**
   ```sql
   UPDATE entries SET luat_nhan_trigger=1 
   WHERE entity_type IS NOT NULL
   ```

4. [ ] **Đặt `reorder_role='head'` cho ALL name entities**
   ```sql
   UPDATE entries SET reorder_role='head'
   WHERE entity_type IS NOT NULL AND reorder_role IS NULL
   ```

## Implementation Steps — COLLOCATION

5. [ ] **Tag long vietphrase còn lại**
   - `vietphrase_5plus` + `vietphrase_4char` chưa tag → `NOUN`, `pos_sub='collocation'`
   - Guard: `WHERE pos_tag IS NULL AND category IN ('vietphrase_5plus','vietphrase_4char')`

6. [ ] **Detect 4-char idioms**
   - Pattern: source = 4 ký tự CJK thuần → `pos_sub='idiom'`
   - Ví dụ: `坐以待毙`, `一飞冲天`

7. [ ] **Detect mixed entries**
   - Entries chứa số, latin, hỗn hợp → `pos_sub='mixed'`

## Files to Create/Modify
- `src/tools/pos_seeder.py` — Name taxonomy + COLLOCATION logic

## Test Criteria
- [ ] `SELECT DISTINCT entity_type FROM entries WHERE entity_type IS NOT NULL` có ≥4 loại
- [ ] `SELECT COUNT(*) FROM entries WHERE luat_nhan_trigger=1` > 2,000
- [ ] `SELECT COUNT(*) FROM entries WHERE pos_sub='collocation'` > 100,000
- [ ] Coverage tăng từ ~70% lên ~85%

---
Next Phase: [phase-07-pinyin-traditional.md](phase-07-pinyin-traditional.md)
