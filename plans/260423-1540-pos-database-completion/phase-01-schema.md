# Phase 01: Schema Extension

Status: ⬜ Pending
Dependencies: None

## Objective
Mở rộng DB schema và DictEntry dataclass để hỗ trợ `pinyin`, `traditional`, và chuẩn bị cho format source file mới.

## Implementation Steps

1. [ ] **Thêm cột `pinyin` và `traditional` vào DB schema**
   - File: `src/core/md_dictionary_compiler.py` (DictionaryCompiler._create_tables)
   - SQL: `ALTER TABLE entries ADD COLUMN pinyin TEXT DEFAULT NULL`
   - SQL: `ALTER TABLE entries ADD COLUMN traditional TEXT DEFAULT NULL`

2. [ ] **Cập nhật DictEntry dataclass**
   - File: `src/core/md_dictionary_compiler.py` (class DictEntry)
   - Thêm: `pinyin: str | None = None`
   - Thêm: `traditional: str | None = None`

3. [ ] **Cập nhật parse_bulk_md() để đọc cột pinyin/traditional**
   - File: `src/core/md_dictionary_compiler.py` (parse_bulk_md)
   - Thêm: `pinyin = row.get('pinyin', '').strip() or None`
   - Thêm: `traditional = row.get('traditional', '').strip() or None`

4. [ ] **Cập nhật DictionaryCompiler.compile() để ghi pinyin/traditional vào DB**
   - File: `src/core/md_dictionary_compiler.py` (DictionaryCompiler._write_entries)
   - Thêm 2 cột vào INSERT statement

## Files to Create/Modify
- `src/core/md_dictionary_compiler.py` — Schema + DictEntry + parser + writer

## Test Criteria
- [ ] `PRAGMA table_info(entries)` hiển thị cột `pinyin` và `traditional`
- [ ] Compile lại DB thành công không có lỗi
- [ ] Entry có `pinyin` trong source file → pinyin xuất hiện trong DB

---
Next Phase: [phase-02-quick-wins.md](phase-02-quick-wins.md)
