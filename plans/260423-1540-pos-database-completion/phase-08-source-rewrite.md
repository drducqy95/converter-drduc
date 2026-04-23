# Phase 08: Source File Rewrite & User Editing Workflow

Status: ⬜ Pending
Dependencies: Phase 06 (names/colloc done), Phase 07 (pinyin in DB)

## Objective
Rewrite source `.md` files từ format 2-cột sang 8-cột metadata-rich. Xây dựng cơ chế cho user tham gia chỉnh sửa database.

## Implementation Steps

1. [ ] **Tạo `src/tools/source_file_rewriter.py`**
   - Đọc DB entries grouped by `source_file`
   - Export ra markdown table 8 cột:
     ```
     | source | target | pos_tag | pos_sub | pinyin | traditional | entity_type | notes |
     ```
   - Giữ nguyên YAML frontmatter, thêm `columns` metadata

2. [ ] **Implement `--dry-run` mode**
   - Preview thay đổi trước khi ghi đè
   - Hiển thị: số entries, cột mới, diff sample

3. [ ] **Implement rewrite cho từng source file**
   - `_vietphrase_1char.md` — 3,424 entries × 8 cols
   - `_vietphrase_2char.md` — 114,955 entries × 8 cols
   - `_vietphrase_3char.md` — 187,410 entries × 8 cols
   - `_vietphrase_4char.md` — 177,808 entries × 8 cols
   - `_vietphrase_5plus.md` — 221,367 entries × 8 cols
   - `_vietphrase_latin_num.md` — 2,282 entries × 8 cols
   - Các file names/loc/org — giữ nguyên + thêm entity_type col

4. [ ] **Tạo `src/tools/validate_source_edits.py`**
   - Validation rules:
     - `pos_tag` ∈ {NOUN, VERB, ADJECTIVE, ADVERB, PRONOUN, PARTICLE, PREPOSITION, CONJUNCTION, NUMBER}
     - `pinyin` format: tone marks hoặc tone numbers
     - `entity_type` ∈ {person, location, faction, weapon, artifact, organization, NULL}
     - Bảng MD hợp lệ (đúng số cột, không bị lệch)

5. [ ] **Thêm Tier 0 guard vào pos_seeder.py**
   - Khi compile: entries có tag từ source file → ghi vào DB
   - Seeder: `WHERE pos_tag IS NULL` → SKIP entries đã có tag từ source
   - Đây là **Tier 0 — Manual Override**, không bao giờ bị ghi đè

6. [ ] **Viết hướng dẫn User Editing**
   - File: `docs/user-editing-guide.md`
   - Quy trình: Mở `.md` → sửa cột → save → validate → compile
   - Hỗ trợ VS Code: column alignment, search/replace

7. [ ] **Test round-trip: DB → .md → recompile → DB**
   - Export DB → .md
   - Recompile .md → DB mới
   - So sánh: DB gốc == DB mới (không mất dữ liệu)

## Files to Create/Modify
- `src/tools/source_file_rewriter.py` — [NEW] DB→MD exporter
- `src/tools/validate_source_edits.py` — [NEW] Validation before compile
- `docs/user-editing-guide.md` — [NEW] Hướng dẫn người dùng
- `src/tools/pos_seeder.py` — Tier 0 guard
- `data/dictionaries/global/vietphrase/*.md` — Rewrite tất cả 6+ files

## Test Criteria
- [ ] Round-trip test pass: DB → .md → DB, 0 data loss
- [ ] User edit 1 entry → recompile → entry giữ nguyên tag
- [ ] Seeder không ghi đè Tier 0 entries
- [ ] Validate tool báo lỗi khi pos_tag sai format

---
Next Phase: [phase-09-nlm-pipeline.md](phase-09-nlm-pipeline.md)
