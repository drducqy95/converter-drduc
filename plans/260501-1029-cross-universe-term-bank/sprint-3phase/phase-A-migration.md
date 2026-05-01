# Phase A: Term Bank Data Migration (Full Import)

Status: ⬜ Pending
Priority: P0
Duration: 1 session
Dependencies: Không

## Objective

Import TOÀN BỘ 23 file MD từ `name_project/` vào `data/term_bank/` JSONL format.
Mỗi bộ truyện = 1 universe riêng.

---

## Tasks

### A1 — Cập nhật FILE_UNIVERSE_HINTS trong md_to_jsonl_converter.py

**File:** `scripts/md_to_jsonl_converter.py`  
**Action:** [MODIFY]

Thêm các entries còn thiếu:

```python
FILE_UNIVERSE_HINTS = {
    # === ChinaWebNovel (12 files) ===
    "Dau_Pha_Thuong_Khung": ("dau_pha_thuong_khung", "Đấu Phá Thương Khung", "Đấu Khí"),
    "Vu_Dong_Can_Khon": ("vu_dong_can_khon", "Vũ Động Càn Khôn", "Đấu Khí"),
    "Dau_La_Dai_Luc": ("dau_la_dai_luc", "Đấu La Đại Lục", "Đấu La"),
    "Phan_Nhan_Tu_Tien": ("pham_nhan_tu_tien", "Phàm Nhân Tu Tiên", "Tu Tiên"),
    "Tien_Nghich": ("tien_nghich", "Tiên Nghịch", "Tu Tiên"),
    "Tru_Tien": ("tru_tien", "Tru Tiên", "Tu Tiên"),
    "Gia_Thien": ("gia_thien", "Già Thiên", "Thần Đông"),
    "Hoan_My_The_Gioi": ("hoan_my_the_gioi", "Hoàn Mỹ Thế Giới", "Thần Đông"),
    "Kiem_Lai": ("kiem_lai", "Kiếm Lai", "Kiếm Lai"),
    "Tuyet_Trung_Han_Dao_Hanh": ("tuyet_trung_han_dao_hanh", "Tuyết Trung Hãn Đao Hành", "Tuyết Trung"),
    "Quy_Bi_Chi_Chu": ("quy_bi_chi_chu", "Quỷ Bí Chi Chủ", "Quỷ Bí"),
    # ★ NEW — Was missing
    "Than_An_Vuong_Toa": ("than_an_vuong_toa", "Thần Ấn Vương Tọa", "Thần Ấn"),

    # === World (1 file) ===
    "Name_Doithuc": ("real_world", "Real World", "Real World"),

    # === Comic (1 file) ===
    "Name_Marvel": ("marvel", "Marvel", "Marvel"),

    # === FilmHollywood (3 files) ===
    "Name_HarryPotter": ("harry_potter", "Harry Potter", "Harry Potter"),
    # ★ NEW
    "Name_Hollywood": ("hollywood", "Hollywood", "Hollywood"),
    # ★ NEW
    "Name_TheOneRing": ("the_one_ring", "The Lord of the Rings", "Middle-earth"),

    # === Manga (6 files) ===
    # ★ NEW — All 6 entries
    "Name_Bleach": ("bleach", "Bleach", "Bleach"),
    "Name_Doremon": ("doremon", "Doraemon", "Doraemon"),
    "Name_Manga": ("manga_shared", "Manga Shared", "Manga"),
    "Name_Naruto": ("naruto", "Naruto", "Naruto"),
    "Name_OnePiece": ("one_piece", "One Piece", "One Piece"),
    "Name_OnePuchman": ("one_punch_man", "One Punch Man", "One Punch Man"),
}
```

**Chi tiết thay đổi:**
- Thêm `Than_An_Vuong_Toa` (universe riêng, KHÔNG gộp vào dau_la)
- Thêm `Name_Hollywood` → universe `hollywood`
- Thêm `Name_TheOneRing` → universe `the_one_ring`
- Thêm 6 entries Manga: `Name_Bleach`, `Name_Doremon`, `Name_Manga`, `Name_Naruto`, `Name_OnePiece`, `Name_OnePuchman`

**Tests cần pass sau thay đổi:**
- [ ] Existing `test_md_to_jsonl_converter.py` tests pass
- [ ] `len(FILE_UNIVERSE_HINTS) == 23`

---

### A2 — Tạo script migration orchestrator

**File:** `scripts/run_term_bank_migration.py`  
**Action:** [NEW]

```python
"""
Orchestrator: parse ALL 23 MD files and write to correct term_bank locations.

Usage:
    python scripts/run_term_bank_migration.py [--dry-run] [--verbose]

Output structure:
    data/term_bank/
    ├── global/
    │   ├── real_world.jsonl          # từ Name_Doithuc.md
    │   ├── proper_names.jsonl        # KEEP existing (manual curated)
    │   ├── shared_cultivation.jsonl  # MERGE: keep existing + add shared terms
    │   └── shared_titles.jsonl       # MERGE: keep existing + add shared terms
    ├── universes/
    │   ├── dau_la_dai_luc/terms.jsonl
    │   ├── dau_pha_thuong_khung/terms.jsonl
    │   ├── gia_thien/terms.jsonl
    │   ├── hoan_my_the_gioi/terms.jsonl
    │   ├── kiem_lai/terms.jsonl
    │   ├── pham_nhan_tu_tien/terms.jsonl
    │   ├── quy_bi_chi_chu/terms.jsonl
    │   ├── than_an_vuong_toa/terms.jsonl       # ★ NEW
    │   ├── tien_nghich/terms.jsonl             # ★ NEW
    │   ├── tru_tien/terms.jsonl                # ★ NEW
    │   ├── tuyet_trung_han_dao_hanh/terms.jsonl # ★ NEW
    │   ├── vu_dong_can_khon/terms.jsonl
    │   ├── marvel/terms.jsonl
    │   ├── harry_potter/terms.jsonl            # ★ NEW
    │   ├── hollywood/terms.jsonl               # ★ NEW
    │   ├── the_one_ring/terms.jsonl            # ★ NEW
    │   ├── bleach/terms.jsonl                  # ★ NEW
    │   ├── doremon/terms.jsonl                 # ★ NEW
    │   ├── manga_shared/terms.jsonl            # ★ NEW
    │   ├── naruto/terms.jsonl                  # ★ NEW
    │   ├── one_piece/terms.jsonl               # ★ NEW
    │   └── one_punch_man/terms.jsonl           # ★ NEW
    └── projects/
"""

Steps:
  1. Scan name_project/ for ALL .md files recursively
  2. Parse each file → list[MigratedTerm]
  3. Route records:
     - scope=="global" → global/{category}.jsonl
     - scope=="universe" → universes/{universe_id}/terms.jsonl
  4. MERGE with existing data (don't overwrite manual curated)
     - Load existing records
     - Dedup by (source, universe)
     - Prefer existing manual records over newly parsed
  5. Write JSONL
  6. Print summary report:
     - Per-file record count
     - Total records
     - New vs existing
     - Warnings (parsing failures)
```

**Merge strategy (QUAN TRỌNG):**
```python
def merge_records(existing: list, new: list) -> list:
    """
    1. Build index from existing by (source, universe) → record
    2. For each new record:
       a. If (source, universe) exists in index:
          - Keep existing (manual curated is authoritative)
          - UNLESS existing.confidence < new.confidence
       b. If NOT exists: add new
    3. Return merged list
    """
```

---

### A3 — Chạy migration

```bash
python scripts/run_term_bank_migration.py --verbose
```

**Expected output:**
```
=== Term Bank Migration Report ===
Source files scanned: 23
Total records parsed: ~1200-1500

Per-universe breakdown:
  pham_nhan_tu_tien:    ~150 records (14.6 KB source)
  bleach:               ~200 records (35.8 KB source)
  doremon:              ~100 records (17.5 KB source)
  one_piece:            ~80 records (14.3 KB source)
  marvel:               ~70 records (13.0 KB source)
  naruto:               ~60 records (11.5 KB source)
  harry_potter:         ~50 records (9.2 KB source)
  the_one_ring:         ~40 records (7.4 KB source)
  ...
  real_world (global):  ~100 records (6.2 KB source)

New universe folders created: 11
Existing records preserved: ~49
Records added: ~1100+
```

---

### A4 — Tạo validate_jsonl.py

**File:** `scripts/validate_jsonl.py`  
**Action:** [NEW]

```python
"""
Usage: python scripts/validate_jsonl.py data/term_bank/ [--fix]

Validation checks:
  1. Valid JSON per line (skip empty/comment lines)
  2. Required fields present: source, target, entity_type
  3. source not empty, target not empty
  4. entity_type in ALLOWED_TYPES
  5. confidence in [0.0, 1.0] (default 0.86 if missing)
  6. No duplicate primary keys (source|universe) per file
  7. Cross-file: warn on duplicate (source|universe) across files
  8. universe field present for scope=universe
  9. No trailing whitespace in source/target

Output:
  ✅ file.jsonl: 150 records, 0 errors
  ⚠️ file.jsonl: 148 records, 2 warnings (duplicate keys)
  ❌ file.jsonl: 140 records, 5 errors (invalid JSON on lines 12, 45, ...)

Summary:
  Total files: 20
  Total records: 1200
  Valid: 1195
  Warnings: 5
  Errors: 0

  --fix mode:
  - Auto-fix trailing whitespace
  - Remove duplicate lines (keep first)
  - Add missing confidence field
  - Remove empty lines
"""
```

---

### A5 — Chạy validate + fix

```bash
python scripts/validate_jsonl.py data/term_bank/ --fix
```

- [ ] 0 errors
- [ ] ≤ 5 warnings (expected duplicates from shared cultivation terms)

---

### A6 — Cập nhật tests

**File:** `tests/test_md_to_jsonl_converter.py`  
**Action:** [MODIFY]

```python
# Thêm test cases:

def test_parse_all_23_source_files():
    """Parse ALL 23 files, assert total records >= 800."""
    source_dir = Path("name_project")
    all_records = []
    for md_file in source_dir.rglob("*.md"):
        all_records.extend(parse_markdown_file(md_file))
    assert len(all_records) >= 800, f"Only {len(all_records)} records"

def test_real_world_count():
    """Name_Doithuc.md should produce >= 80 records."""
    records = parse_markdown_file("name_project/World/Name_Doithuc.md")
    assert len(records) >= 80

def test_bleach_is_largest():
    """Bleach (35.8 KB) should produce the most records."""
    records = parse_markdown_file("name_project/Manga/Name_Bleach.md")
    assert len(records) >= 100

def test_no_duplicate_primary_keys():
    """No (source, universe) duplicates within a single file."""
    for md_file in Path("name_project").rglob("*.md"):
        records = parse_markdown_file(md_file)
        keys = [(r.source, r.universe) for r in records]
        assert len(keys) == len(set(keys)), f"Duplicates in {md_file.name}"

def test_file_universe_hints_complete():
    """All 23 source files should have matching hints."""
    assert len(FILE_UNIVERSE_HINTS) >= 23

def test_than_an_vuong_toa_separate_universe():
    """Than_An_Vuong_Toa must be its own universe, not dau_la_dai_luc."""
    records = parse_markdown_file("name_project/ChinaWebNovel/Than_An_Vuong_Toa.md")
    assert all(r.universe == "than_an_vuong_toa" for r in records)
```

---

## Files to Create/Modify

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `scripts/md_to_jsonl_converter.py` | [MODIFY] | Add 10 missing FILE_UNIVERSE_HINTS |
| 2 | `scripts/run_term_bank_migration.py` | [NEW] | Orchestrator: parse → route → merge → write |
| 3 | `scripts/validate_jsonl.py` | [NEW] | Validate all JSONL files |
| 4 | `data/term_bank/global/real_world.jsonl` | [OVERWRITE] | ~100+ records from Name_Doithuc |
| 5 | `data/term_bank/global/shared_cultivation.jsonl` | [MERGE] | Add shared cultivation terms |
| 6 | `data/term_bank/global/shared_titles.jsonl` | [MERGE] | Add shared title terms |
| 7-17 | `data/term_bank/universes/{new_id}/terms.jsonl` | [NEW] | 11 new universe folders |
| 18-24 | `data/term_bank/universes/{existing_id}/terms.jsonl` | [MERGE] | 7 existing folders updated |
| 25 | `tests/test_md_to_jsonl_converter.py` | [MODIFY] | 6 new test cases |

## Definition of Done

```
[ ] FILE_UNIVERSE_HINTS has 23 entries
[ ] run_term_bank_migration.py runs without error
[ ] 23 source MD files parsed
[ ] ≥ 18 universe folders exist
[ ] global/real_world.jsonl ≥ 80 records
[ ] Total term bank records ≥ 800
[ ] validate_jsonl.py reports 0 errors
[ ] Existing manual curated records preserved (merge, not overwrite)
[ ] No duplicate primary keys (source|universe)
[ ] 6 new tests pass
[ ] All 223+ existing tests pass
```

---
Next Phase: [Phase B — Universe Detector](phase-B-universe-detector.md)
