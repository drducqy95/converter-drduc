# Phase 05: QA Engine

Status: ⬜ Pending  
Progress: 0%  
Dependencies: Phase 04 (RBMT Core)

## Objective

Xây dựng hệ thống hậu kiểm để phát hiện lỗi thuật ngữ, xưng hô, cấu trúc, untranslated text, fallback nguy hiểm và ambiguity chưa được giải quyết.

## Deliverables

- `terminology_checker.py`
- `pronoun_checker.py`
- `emotion_consistency_checker.py`
- `structure_checker.py`
- `untranslated_detector.py`
- `length_checker.py`
- `report_generator.py`

## QA Philosophy

QA không chỉ kiểm tra “có lỗi hay không”, mà còn phải giải thích vì sao engine đã chọn một nghĩa, fallback nào đã được dùng, và chỗ nào cần biên dịch viên can thiệp.

QA cũng là nơi xác nhận chiến lược metadata-first có thực sự giảm phụ thuộc vào dữ liệu cứng hay không. Nếu runtime vẫn thường xuyên rơi xuống phrase fallback quá thấp hoặc residual `PhienAm`, đó là tín hiệu phải quay lại tối ưu dictionary/model thay vì chỉ vá thêm phrase mới.

## Workstreams

### 1. Terminology Consistency

- So output với glossary/name rules.
- Kiểm tra entity consistency giữa các chương.
- Cảnh báo khi một key có nhiều bản dịch thực tế.

### 2. Pronoun & Dialogue Consistency

- Kiểm tra xưng hô theo cặp nhân vật.
- Kiểm tra drift cảm xúc/hierarchy không hợp lý.
- Kiểm tra speaker continuity trong dialogue runs.

### 3. Structure Integrity

- Paragraph count
- placeholder restore
- table / code / LaTeX integrity
- chapter order

### 4. Residual Source Detection

- Detect Hán tự còn sót
- Detect source fragments chưa dịch
- Detect transliteration fallback bất thường

### 5. Ambiguity & Fallback Audit

- Đánh dấu nơi engine đã dùng low-priority fallback.
- Đánh dấu nơi unresolved ambiguity vẫn còn trong draft.
- Đưa `alternative_meanings` hoặc `reference_data` vào report khi hữu ích.

### 6. Length and Sanity Checks

- Source/target ratio
- sentence loss/duplication
- suspicious short or long outputs

## Detailed Task Breakdown

### QA-001 Terminology Checker

- So output với glossary/name rules và project overrides.
- Phát hiện drift giữa entries đến từ nguồn khác nhau.
- Báo riêng trường hợp runtime bỏ qua candidate ưu tiên cao bất thường.

### QA-002 Pronoun and Dialogue Checker

- Kiểm tra xưng hô theo cặp speaker/listener.
- Kiểm tra continuity trong dialogue runs.
- Dùng emotion trace để phát hiện override không hợp lý.

### QA-003 Structure Checker

- Kiểm tra paragraph count, placeholder restore, table/code/LaTeX integrity.
- Phát hiện rơi placeholder hoặc restore sai vị trí.
- Báo severity theo mức phá hỏng output.

### QA-004 Residual Source Checker

- Detect Hán tự còn sót, pinyin còn sót, transliteration fallback bất thường.
- Báo riêng trường hợp engine dùng residual `PhienAm` hoặc `P0` fallback quá nhiều.
- Tạo thống kê theo chapter để quay lại tối ưu dictionary layer.

### QA-005 Ambiguity and Candidate Audit

- Hiển thị unresolved ambiguity.
- Hiển thị top candidates, scoring trace, matched rules, source_dict.
- Lấy `alternative_meanings`, `full_explanation` từ cold path khi cần giải thích.

### QA-006 Report Generator

- Xuất `reports/qa_report.md` với severity, chapter summary, actionable fix list.
- Link violation về segment id và candidate trace.
- Chuẩn bị JSON output để UI viewer tái sử dụng.

## Output Contract

- `reports/qa_report.md`
- severity levels
- per-chapter summary
- actionable violations

## Acceptance Criteria

- Bắt được lỗi injected trong test corpus.
- Report đọc được và trỏ được vị trí vi phạm.
- Có thể chạy độc lập sau translation.
- Có mục riêng cho fallback và ambiguity.

## Immediate Next Slice

1. Terminology checker
2. Untranslated detector
3. Structure checker
4. Markdown report generator kèm fallback/ambiguity audit

---
Previous Phase: [Phase 04 - RBMT Core](./phase-04-rbmt-engine.md)  
Next Phase: [Phase 06 - State Management & Translation Memory](./phase-06-state-tm.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
