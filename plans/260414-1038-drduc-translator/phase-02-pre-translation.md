# Phase 02: Pre-Translation Pipeline

Status: ⬜ Pending  
Progress: 5%  
Dependencies: Phase 01 (Foundation Closeout)

## Objective

Xây dựng pipeline tiền dịch chuẩn hóa đầu vào trước khi RBMT Core chạy: import tài liệu, chuẩn hóa encoding, tách chương, preserve cấu trúc, Traditional -> Simplified, Pinyin resolution, entity scan, relationship build và sinh `translation_config.json`.

## Role in Overall Architecture

Phase 02 là cầu nối giữa nền từ điển của Phase 01 và translation orchestration ở Phase 04. Nếu Phase này làm không tốt, RBMT Core sẽ phải xử lý dữ liệu bẩn, chapter boundary sai, entity chưa xác nhận và ambiguity không được gắn cờ.

Ngoài chuẩn hóa input, Phase này còn có vai trò chuyển dịch hệ thống từ kiểu xử lý dựa nhiều vào phrase cứng sang kiểu metadata-aware:

- reading phải ưu tiên lấy từ dictionary metadata thay vì lệ thuộc vào một lớp `PhienAm` riêng;
- normalization phải được quản lý như rules có nguồn gốc rõ, không trộn vào translation entries;
- entity scan và config generation phải tạo ra ngữ cảnh để runtime ranking xử lý linh hoạt hơn.

## Deliverables

- `document_importer.py`
- `chapter_splitter.py`
- `structure_preserver.py`
- `traditional_to_simplified.py`
- `pinyin_processor.py`
- `entity_scanner.py`
- `relationship_builder.py`
- `terminology_suggester.py`
- `config_generator.py`

## Input / Output Contract

### Input

- file `TXT`, `MD`, `HTML`, `DOCX`, `PDF`
- source text raw theo project
- compiled dictionaries từ Phase 01

### Output

- `source/raw/`
- `source/chapters/`
- `working/entities/entities_suggested.json`
- `working/relationships/relationships_suggested.json`
- `working/config/translation_config.json`
- logs và report scan sơ bộ

## Workstreams

### 1. Document Importer

- Import đa định dạng.
- Auto-detect encoding:
  - UTF-8
  - GB2312
  - GBK
  - Big5
  - UTF-16
- Normalize whitespace và lỗi ký tự thường gặp.

### 2. Chapter Splitter

- Regex cho ZH/VI/EN headings.
- Fallback theo word count.
- Sinh `chapters_index.json`.
- Hỗ trợ split lại khi người dùng chỉnh boundary.

### 3. Structure Preservation

- Bảo toàn:
  - code block
  - inline code
  - HTML/XML
  - links/images
  - LaTeX
  - table-like blocks
- Placeholder phải khôi phục được 100%.

### 4. Traditional -> Simplified

- Phrase-first, char-fallback.
- Có hook tích hợp OpenCC hoặc equivalent.
- Ghi nhận provenance nếu có biến thể regional.

### 5. Pinyin Resolution

- Baseline heuristic trước.
- Chuẩn bị hook cho model-based disambiguation sau.
- Chỉ convert khi confidence đủ cao.
- Không được làm hỏng tên riêng đã xác thực.
- Ưu tiên `pinyin` và `han_viet_readings` lấy từ `LacViet`, `ThieuChuu`, `CEDICT` hoặc metadata-rich entries trước khi dùng residual `PhienAm`.

### 6. Entity Scanning

- Character
- Location
- Faction
- Weapon / Item
- Technique
- Realm

Mỗi entity nên có:

- source text
- normalized form
- entity type
- confidence
- source_dict hit nếu có
- ambiguity flag nếu trùng danh từ chung

### 7. Relationship Builder

- Kinship patterns
- Dialogue pairs
- Faction membership
- Power hierarchy hints
- Scene-local co-occurrence

### 8. Terminology Suggester & Config Generator

- Han-Viet suggestion
- cultural origin hints
- name casing rules
- genre hints
- `high_ambiguity_terms`
- default translation mode cho project

## Detailed Task Breakdown

### PRE-001 Document Import Contract

- Xây importer đa định dạng với output chuẩn vào `source/raw/`.
- Ghi provenance về encoding, source format, conversion notes.
- Chuẩn bị đường mở rộng cho batch import nhiều file.

### PRE-002 Chapter Boundary Engine

- Split theo heading regex cho ZH/VI/EN.
- Fallback theo độ dài và dấu ngắt chương.
- Sinh `chapters_index.json` và cho phép override boundary.

### PRE-003 Normalization Rule Layer

- Parse `Mark.txt` thành normalization map.
- Tách rule punctuation/spacing khỏi dictionary translation layer.
- Áp normalization có log để QA truy được.

### PRE-004 Structure Preservation

- Bảo toàn code block, inline code, HTML/XML, links, LaTeX, tables.
- Dùng placeholder registry ổn định để Phase 04 chỉ làm việc trên text dịch được.
- Thêm test cho placeholder collision và nested structures.

### PRE-005 T2S and Reading Resolution

- Xây T2S phrase-first, char-fallback.
- Gắn provenance cho mỗi conversion.
- Thiết kế reading resolver ưu tiên metadata-rich dictionaries trước residual `PhienAm`.

### PRE-006 Entity and Semantic Scan

- Gắn `entity_type`, `semantic_class`, `source_dict`, `confidence`, `ambiguity_flag`.
- Đánh dấu term có thể là danh từ chung lẫn tên riêng.
- Tạo danh sách term cần reviewer khóa cứng.

### PRE-007 Relationship Builder

- Sinh graph tối thiểu cho kinship, faction membership, dialogue adjacency, scene co-occurrence.
- Tạo input dùng chung cho EAPEE và RBMT context manager.
- Lưu confidence và source evidence cho từng cạnh.

### PRE-008 Terminology and Config Generation

- Sinh `translation_config.json` với `high_ambiguity_terms`, naming policy, genre hints, cultural-origin hints.
- Phân loại term nào nên ưu tiên rule-based, term nào nên để runtime ranking.
- Ghi output reviewable để editor có thể xác nhận trước khi dịch hàng loạt.

## Alignment with Metadata Model

Phase 02 phải sinh đủ dữ liệu để Phase 04 lọc ứng viên theo:

- `entity_type`
- `genre`
- `cultural_origin`
- danh sách `high_ambiguity_terms`
- context entities theo chapter/scene

## Acceptance Criteria

- Import được trên tập mẫu đa định dạng.
- Split chapter ổn định và có fallback.
- Preserve/restore không làm hỏng cấu trúc.
- T2S có thể chạy trên văn bản Phồn thể mẫu.
- Pinyin resolution có cơ chế an toàn.
- Entity scan và relationship output đủ dùng cho biên tập viên duyệt.
- `translation_config.json` được sinh tự động cho project mới.
- Có cơ chế reading resolution không phụ thuộc mặc định vào full-layer `PhienAm`.

## Immediate Next Slice

1. `document_importer.py`
2. `chapter_splitter.py`
3. `structure_preserver.py`
4. `Mark.txt` -> `normalization_rules` và output contract cho `translation_config.json`

---
Previous Phase: [Phase 01 - Foundation Closeout](./phase-01-foundation.md)  
Next Phase: [Phase 03 - EAPEE](./phase-03-eapee.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
