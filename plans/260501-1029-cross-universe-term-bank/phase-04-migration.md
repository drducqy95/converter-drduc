# Phase 04: Cross-Universe Term Bank Data Migration

Status: ⬜ Pending
Priority: P1
Duration: 1 tuần
Dependencies: Phase 02

## Objective
Chuyển 12 file MD entity bank + Name_Doithuc.md sang JSONL universe-aware. Backfill proper_names.jsonl.

## Tasks

### P4-T1 — Tạo term_bank directory structure
```
data/term_bank/
  global/
    proper_names.jsonl     (existing)
    shared_cultivation.jsonl
    shared_titles.jsonl
    real_world.jsonl
  universes/
    fingerprints.json
    tu_tien/   (Phàm Nhân, Tiên Nghịch, Tru Tiên)
    dau_khi/   (Đấu Phá, Vũ Động)
    dau_la/    (Đấu La, Thần Ấn)
    than_dong/ (Già Thiên, Hoàn Mỹ)
    kiem_lai/  (Kiếm Lai, Tuyết Trung)
    quy_bi/    (Quỷ Bí Chi Chủ)
    oc_fanfic/ (Cho OC/fanfic characters)
```

### P4-T2 — md_to_jsonl_converter.py
File: `scripts/md_to_jsonl_converter.py`
Requirements:
- [ ] Parse `*`, `-`, `•` bullet formats
- [ ] Parse `中文 = Hán Việt` và `中文 = Hán Việt (notes)`
- [ ] Parse slash aliases: `中文 / 别名 = Target`
- [ ] Map section header → entity_type
- [ ] Map file path → universe/work
- [ ] Primary key = `source|universe`
- [ ] Idempotent (chạy lại không duplicate)

Section → entity_type mapping:
```
### Nhân vật → person
### Bản đồ / Địa danh → location
### Tổ chức / Thế lực → organization
### Hệ thống tu luyện / Cấp bậc → realm
### Công pháp / Chiêu thức → technique
### Vũ khí → weapon
### Vật phẩm / Đan dược → item
### Linh thú → creature
### Trận pháp → technique
### Dị Hỏa / Võ Hồn → item
### Thuật ngữ khác → term
```

### P4-T3 — validate_jsonl.py
File: `scripts/validate_jsonl.py`
Checks:
- [ ] Valid JSON per line
- [ ] Required fields: source, target, entity_type
- [ ] No duplicate primary keys (source|universe)
- [ ] entity_type in allowed list
- [ ] confidence in [0,1]

### P4-T4 — Backfill proper_names.jsonl
Thêm fields mới vào existing records:
```
universe, scope, confidence, status, version,
context_markers, co_occurring_entities, aliases_source, aliases_target, tags
```

## Input Files
| Source File | Universe | Work |
|------------|----------|------|
| Phan_Nhan_Tu_Tien.md (302 lines) | tu_tien | 凡人修仙传 |
| Tien_Nghich.md (130 lines) | tu_tien | 仙逆 |
| Tru_Tien.md (109 lines) | tu_tien | 诛仙 |
| Dau_Pha_Thuong_Khung.md (144 lines) | dau_khi | 斗破苍穹 |
| Vu_Dong_Can_Khon.md (123 lines) | dau_khi | 武动乾坤 |
| Dau_La_Dai_Luc.md (128 lines) | dau_la | 斗罗大陆 |
| Than_An_Vuong_Toa.md (115 lines) | dau_la | 神印王座 |
| Gia_Thien.md (128 lines) | than_dong | 遮天 |
| Hoan_My_The_Gioi.md (132 lines) | than_dong | 完美世界 |
| Kiem_Lai.md (104 lines) | kiem_lai | 剑来 |
| Tuyet_Trung_Han_Dao_Hanh.md (101 lines) | kiem_lai | 雪中悍刀行 |
| Quy_Bi_Chi_Chu.md (112 lines) | quy_bi | 诡秘之主 |
| Name_Doithuc.md (221 lines) | real_world | — |

## Files to Create/Modify
- `scripts/md_to_jsonl_converter.py` — [NEW]
- `scripts/validate_jsonl.py` — [NEW]
- `scripts/backfill_proper_names.py` — [NEW]
- `data/term_bank/global/shared_cultivation.jsonl` — [NEW]
- `data/term_bank/global/shared_titles.jsonl` — [NEW]
- `data/term_bank/global/real_world.jsonl` — [NEW]
- `data/term_bank/universes/*/` — [NEW] 7 universe folders

## Definition of Done
```
[ ] JSONL valid (validate_jsonl.py pass)
[ ] No duplicate primary keys
[ ] proper_names.jsonl backfilled
[ ] shared_cultivation / shared_titles / real_world tồn tại
[ ] Tất cả 7 universe folders có data
[ ] Unit tests pass
```

---
Next Phase: Phase 05 — Term Bank Schema Expansion
