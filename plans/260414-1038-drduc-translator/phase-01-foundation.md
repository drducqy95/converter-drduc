# Phase 01: Foundation Closeout

Status: ✅ Done  
Progress: 100%  
Dependencies: Phase 00 (Alignment & Stabilization)

## Objective

Đóng hoàn chỉnh lớp nền tảng từ điển, migration, compiler, Trie và LuatNhan để toàn bộ pipeline phía sau có một nền dữ liệu ổn định, có thể rebuild và benchmark.

## Current Baseline

- Đã có `scripts/migrate_qt_to_md.py`.
- Đã có `src/core/md_dictionary_compiler.py`.
- Đã có `src/core/trie_engine.py`.
- Đã có `src/core/luat_nhan_engine.py`.
- Đã có compiled DB và full test Python xanh.
- Đã nạp `Babylon.txt` và `Mark.txt`.
- Compiler đã tách `reference_entries` và `normalization_rules` khỏi fast-path `entries`.
- Đã rebuild compiled DB theo schema mới.
- Đã migrate `LacViet.txt` và refactor `ThieuChuu.txt` theo hướng metadata-rich reference.
- Đã chạy coverage study cho `PhienAm`.
- Đã materialize `entry_readings` trong compiled DB.
- Đã import `audit_events` từ các file history.
- `TrieEngine` đã có reading fallback từ compiled DB.
- Đã chốt benchmark/rebuild workflow tại [\_phase1_benchmark.json](</D:/Converter by DrDuc/data/dictionaries/_phase1_benchmark.json>).
- Runtime `PhienAm` đã được cắt xuống residual set an toàn, còn `264` entry trong fast path và giữ fallback qua `entry_readings`.

## Deliverables

- Migration pipeline có thể chạy lặp lại.
- Canonical metadata model cho dictionary entries.
- Compiled SQLite DB ổn định.
- Trie load/lookup đúng ưu tiên.
- LuatNhan engine hỗ trợ disambiguation hook cơ bản.
- Benchmark và full test xanh.

## Phase Closeout Summary

- Compiler nhận đúng cả bulk MD split sẵn như `_vietphrase_1char.md`, `_names_person_east.md`.
- `Babylon.txt` được migrate thành [\_bulk_babylon.md](</D:/Converter by DrDuc/data/dictionaries/global/en_vi/_bulk_babylon.md>).
- `Mark.txt` được migrate thành [mark_normalization.md](</D:/Converter by DrDuc/data/dictionaries/global/normalization/mark_normalization.md>).
- `LacViet.txt` được migrate thành [\_bulk_lacviet.md](</D:/Converter by DrDuc/data/dictionaries/global/reference_vi/_bulk_lacviet.md>).
- `ThieuChuu.txt` đã được refactor thành bản metadata-rich reference tại [\_bulk_thieuchuu.md](</D:/Converter by DrDuc/data/dictionaries/global/phien_am/_bulk_thieuchuu.md>).
- SQLite compiled DB có thêm `reference_entries` và `normalization_rules`.
- SQLite compiled DB có thêm `entry_readings`.
- SQLite compiled DB có thêm `audit_events`.
- `reference_entries` hiện có `193,561` rows sau khi thêm `LacViet` và `ThieuChuu`.
- `audit_events` hiện có `6,126` rows imported từ `VietPhraseHistory`, `NamesHistory`, `Names2History`, `ChinesePhienAmWordsHistory`.
- `entry_readings` hiện có `174,999` rows materialized từ `PhienAm`, `ThieuChuu`, `LacViet`, `CEDICT` và metadata hiện có.
- `CEDICT` và `Babylon` không còn đi vào runtime `entries` của Trie.
- `ThieuChuu` không còn đi vào runtime `entries`; `PhienAm` runtime đã giảm từ `1,420` xuống còn `264` residual entries.
- Coverage report cho `PhienAm` nằm tại [\_phienam_coverage_report.json](</D:/Converter by DrDuc/data/dictionaries/_phienam_coverage_report.json>) với kết quả `12,047 / 12,570` khóa được phủ bởi `ThieuChuu + LacViet + CEDICT`, còn lại `523` khóa residual.
- `TrieEngine` hiện đã có fallback từ `entry_readings`, nên việc cắt `PhienAm` về residual set không làm mất single-character fallback.
- Benchmark cuối phase cho thấy compile `43.88s`, SQLite load `4.772s`, `1.225µs/lookup` và `0.297ms` cho sample translation.
- `python -m pytest -q` đạt `91 passed`.

## Canonical Data Model

Mọi nguồn dữ liệu trong Phase 01 phải có khả năng ánh xạ về cùng một model logic:

- `entry_id`
- `core_mapping`
- `reference_data`
- `morphology_and_syntax`
- `eapee_context`
- `system_flags`
- `provenance_and_state`
- `disambiguation_patterns`

Không bắt buộc tất cả trường đều phải được materialize ngay trong SQLite ở vòng đầu, nhưng compiler phải có thiết kế cho phép mở rộng dần mà không phá schema.

## Source-Specific Strategy

### VietPhrase / VietPhrase2

- Phrase-level dictionary.
- `target_vi` mặc định lấy nghĩa đầu.
- Nghĩa phụ đi vào `reference_data.alternative_meanings`.
- Từ đa nghĩa phải tự động bật `luat_nhan_trigger`.

### Names / Project Entity Dictionaries

- Gán `entity_type` rõ.
- Global names dùng `P4`.
- Project-specific names dùng `P5`.
- Từ khóa tên riêng quan trọng nên `is_locked = true`.

### PhienAm

- Không còn là lớp fast-path mặc định.
- Chỉ được giữ như residual fallback nếu các nguồn giàu metadata chưa bao phủ đủ reading.
- Không được ghi đè phrase-level match hoặc candidate đã được ngữ cảnh xác nhận.

### ThieuChuu

- Dùng làm self-contained reference/fallback.
- Ưu tiên rất thấp (`P0` hoặc equivalent fallback tier).
- Phải giữ giải nghĩa đầy đủ trong `reference_data`.
- Có thể parse `han_viet_readings`, `full_explanation`, `parsed_meanings`.

### Babylon

- Nạp như `reference_en`.
- Không được chen vào đường dịch ZH -> VI chính.
- Dùng cho tooltip, QA, đối chiếu nghĩa và EN gloss.

### LacViet

- Nạp như `reference_vi_rich`.
- Ưu tiên giữ `pinyin`, Hán-Việt, giải nghĩa dài và note thay vì chỉ ép về một `target_vi`.
- Dùng để giảm phụ thuộc vào `PhienAm` và tăng dữ liệu cho disambiguation.

### Mark / History Sources

- `Mark.txt` đi vào `normalization_rules`, không đi vào trie dictionary.
- `*History.txt` đi vào `audit_events`, không đi vào lookup runtime.

### LuatNhan / LuatNhanCu

- Giữ như grammar assets riêng.
- Chuẩn bị đường nâng cấp để dùng `semantic_class` và `disambiguation_patterns`.

### CEDICT / Reference Dictionaries

- Dùng làm nguồn tham khảo.
- Không được phép chiếm ưu tiên trước dictionary ZH -> VI chính.

## Workstreams

### 1. Migration Normalization

- Chuẩn hóa parsing `key=value`.
- Bóc BOM, encoding issue, invalid rows.
- Thêm utility sinh `entry_id` ổn định.
- Cho phép migrate từ TXT phẳng sang metadata-rich JSON/MD nếu cần.

### 2. Markdown Dictionary Format

- Chốt format Bulk MD.
- Chốt format Grammar MD.
- Quy định rõ trường nào là canonical, trường nào là transitional.
- Giữ khả năng round-trip từ raw source -> MD -> SQLite.

### 3. Compiler and SQLite

- Chuẩn hóa merge logic theo priority.
- Thiết kế đường chứa metadata mở rộng:
  - inline columns cho hot-path fields;
  - JSON/text column hoặc side tables cho fields ít truy cập.
- Lưu metadata đủ để phục vụ UI, QA và future learning.
- Tách rõ `entries_hot`, `entries_metadata`, `entry_readings`, `grammar_patterns`, `normalization_rules`, `audit_events`.

### 4. Trie Engine

- Longest-prefix match.
- Priority override.
- Single-character fallback.
- Chuẩn bị multi-entry candidate retrieval cho các khóa đa nghĩa.

### 5. LuatNhan Engine

- Load rules từ compiled DB.
- Hỗ trợ pattern-based replacement.
- Chuẩn bị interface cho disambiguation local rules.

### 6. Testing and Benchmark

- Sửa parser escaped pipe `\|`.
- Thêm smoke test rebuild database.
- Thêm benchmark compile/load/lookup.
- Thêm test cho priority `P5`.
- Thêm coverage report để đo overlap và phần còn thiếu giữa `LacViet`, `ThieuChuu`, `PhienAm`.

## Detailed Task Breakdown

### FND-001 Source Role Mapping

- Đồng bộ inventory từ `Dictionaries.ini`.
- Gắn vai trò logic cho từng source: `core_translation`, `reference_vi_rich`, `reference_en`, `normalization_rules`, `audit_events`.
- Khóa rõ source nào được vào fast path, source nào chỉ ở cold path.

### FND-002 Metadata Schema Freeze

- Chốt schema logic cho `core_mapping`, `reference_data`, `morphology_and_syntax`, `eapee_context`, `provenance_and_state`.
- Chốt mapping field tối thiểu cho các source mới.
- Tạo guideline để thêm parser mới mà không phá compiler.

### FND-003 Additional Source Parsers

- Viết parser `Babylon.txt` sang `reference_en`. Completed.
- Viết parser `Mark.txt` sang `normalization_rules`. Completed.
- Viết parser metadata-rich cho `LacViet.txt`. Completed.
- Refactor `ThieuChuu.txt` để tách reading, meanings và explanation. Completed.
- Import `*History.txt` vào `audit_events`. Completed.

### FND-004 PhienAm Reduction Study

- Đo overlap giữa `PhienAm` với `LacViet`, `ThieuChuu`, `CEDICT`. Completed.
- Đo coverage reading còn thiếu sau khi hợp nhất nguồn giàu metadata. Completed.
- Quyết định giữ full layer hay chỉ compile residual fallback set. Completed: runtime chỉ giữ `264` residual entries, còn fallback đọc chuyển sang `entry_readings`.

### FND-005 Hot/Cold DB Layout

- Materialize fields nóng cho runtime lookup.
- Tách reference và normalization khỏi runtime `entries`.
- Tách metadata nặng sang cold path hoặc JSON side table.
- Chuẩn hóa `entry_readings` để reading không còn phụ thuộc vào một source đơn lẻ. Completed.
- Materialize `audit_events` để giữ provenance thay vì bỏ history files. Completed.

### FND-006 Trie and Ranking Contract

- Cập nhật trie để trả multi-entry candidates theo `entry_id`. Deferred sang Phase 04 vì không còn là blocker của Phase 01.
- Giữ đủ metadata cho runtime scorer dùng `priority`, `entity_type`, `semantic_class`, `flags_bitmask`. Deferred sang Phase 04/05.
- Không collapse entry đa nghĩa quá sớm ở compile time. Deferred và sẽ thực hiện cùng candidate orchestrator ở Phase 04.

### FND-007 Validation and Benchmark

- Sửa `_parse_md_table()` và xanh full test. Completed.
- Thêm benchmark compile/load/lookup. Completed.
- Thêm smoke test rebuild DB và coverage report theo dictionary layer. Completed.

## Files in Scope

- `scripts/migrate_qt_to_md.py`
- `scripts/migrate_txt_to_metadata.py` hoặc utility tương đương
- `src/core/md_dictionary_compiler.py`
- `src/core/trie_engine.py`
- `src/core/luat_nhan_engine.py`
- `data/dictionaries/`
- `tests/test_phase1.py`

## Acceptance Criteria

- `python -m pytest -q` pass 100%. Satisfied (`91 passed`).
- Rebuild compiled DB từ nguồn MD không lỗi. Satisfied.
- Lookup đúng với priority override. Satisfied trên Phase 01 test suite.
- LuatNhan chạy được trên entity pairs mẫu. Satisfied trên Phase 01 test suite.
- Benchmark reproducible và có số liệu baseline. Satisfied tại [\_phase1_benchmark.json](</D:/Converter by DrDuc/data/dictionaries/_phase1_benchmark.json>).
- Có chiến lược rõ ràng cho VietPhrase, Names, Babylon, LacViet, Mark, PhienAm, ThieuChuu, LuatNhan. Satisfied.
- Có số liệu đủ để quyết định thu gọn hoặc bỏ full fast-path layer của `PhienAm`. Satisfied.

## Immediate Next Slice

1. Mở Phase 02 với vertical slice đầu tiên: importer, chapter split và structure preservation.
2. Giữ `entry_readings`, `reference_entries` và `audit_events` làm nền cho pre-translation pipeline.
3. Chuyển các hạng mục candidate retrieval và runtime scorer nâng cao sang Phase 04/05.

---
Previous Phase: [Phase 00 - Alignment & Stabilization](./phase-00-alignment-stabilization.md)  
Next Phase: [Phase 02 - Pre-Translation Pipeline](./phase-02-pre-translation.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
