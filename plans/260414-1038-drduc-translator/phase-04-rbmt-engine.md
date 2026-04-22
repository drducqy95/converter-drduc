# Phase 04: RBMT Core

Status: 🟨 In Progress  
Progress: 15%  
Dependencies: Phase 01, Phase 02, Phase 03

## Objective

Tạo translation orchestrator chạy thật từ input chapter đến output chapter, tích hợp preserve, segment, TM lookup, Trie, LuatNhan, disambiguation, EAPEE, number conversion và context update.

## Current Baseline

- `src/engine/number_converter.py` đã có nền tảng tốt.
- Chưa có `rbmt_translator.py` production.
- Chưa có candidate ranking theo metadata.
- Chưa có draft/clean output flow hoàn chỉnh.

## Deliverables

- `sentence_segmenter.py`
- `structure_preserver.py`
- `context_manager.py`
- `cultural_origin_detector.py`
- `rbmt_translator.py`
- output clean + draft annotated

## Translation Strategy

Phase 04 không được dịch kiểu 1 entry -> 1 output duy nhất cho mọi tình huống. Thay vào đó:

1. Trie trả về ứng viên.
2. Bộ lọc theo `priority`, `project_id`, `entity_type`, `genre`, `cultural_origin`.
3. Nếu từ có `luat_nhan_trigger`, chuyển cho LuatNhan/RBMT local rules.
4. Nếu có `semantic_class` và `disambiguation_patterns`, dùng lookahead/lookbehind để tăng hoặc giảm điểm.
5. Nếu vẫn chưa chắc, dùng fallback mặc định và đánh cờ ambiguity.

Mục tiêu của phase này là tăng xử lý bằng thuật toán thay vì tiếp tục mở rộng vô hạn phrase data cứng:

- phrase dictionary vẫn là lớp quan trọng, nhưng không được là công cụ duy nhất để xử lý đa nghĩa;
- measure-word resolution, entity-aware ranking, noun phrase assembly và cultural-origin policy phải nằm ở runtime logic;
- residual reading fallback chỉ được dùng sau khi phrase-level và metadata-rich candidates thất bại.

## Workstreams

### 1. Sentence Segmentation

- Split câu ZH.
- Preserve quote boundary.
- Chuẩn bị cho batch chapter translation.

### 2. Structure Preservation

- Wrap/unwrap invariant structures.
- Giữ placeholder registry.
- Không làm hỏng tables, formulas, code.

### 3. Candidate Retrieval

- Exact trie match.
- Longest-prefix match.
- Support multiple entries for same key.
- Support low-priority fallback.

### 4. Disambiguation

- LuatNhan for local rules.
- Lookahead/lookbehind.
- `semantic_class`-based choice.
- `high_ambiguity_terms` awareness từ `translation_config.json`.
- Candidate trace để QA/UI giải thích được quyết định.

### 5. EAPEE Integration

- Dialogue detection.
- Speaker/listener context.
- Pronoun replacement.
- Expression insertion khi phù hợp.

### 6. Number and Formatting

- Number conversion.
- Date/time/unit patterns.
- Final restore of preserved structures.

### 7. Context Update

- active entities
- scene context
- TM save
- ambiguity markers

## Detailed Task Breakdown

### RBM-001 Sentence Segmentation

- Tách câu ZH an toàn cho thoại, ngoặc, dấu lửng, các câu ngắn liên hoàn.
- Gắn sentence ids ổn định cho trace và TM.
- Cho phép batch translation theo chapter.

### RBM-002 Runtime Lookup Contract

- Kết nối TM, trie, grammar patterns, normalization rules theo một API runtime thống nhất.
- Trả multi-entry candidates kèm metadata tối thiểu cho scoring.
- Không collapse candidate quá sớm ở lớp lookup.

### RBM-003 Candidate Scoring

- Xếp hạng theo `priority`, `project_id`, `entity_type`, `semantic_class`, `genre`, `cultural_origin`, `context_window`.
- Tăng/giảm điểm theo `disambiguation_patterns` và `luat_nhan_trigger`.
- Ghi trace điểm số để QA và UI xem lại.

### RBM-004 Local Rule Execution

- Chạy `LuatNhan` và rule templates trên đoạn context ngắn.
- Tạo lớp measure-word/classifier resolution.
- Tạo hook cho syntax transfer heuristic mà không khóa cứng toàn bộ phrase.

### RBM-005 Phrase Assembly

- Lắp noun phrase dựa trên classifier, entity type, modifiers và order rules.
- Tách phrase assembly khỏi dictionary compile để giảm hardcoded data growth.
- Có fallback an toàn khi rule chưa đủ chắc.

### RBM-006 EAPEE Integration

- Nối speaker/listener context, pronoun matrix, expression bank vào translation pass.
- Chỉ apply expression khi confidence đủ và không phá nghĩa gốc.
- Ghi lại các override do EAPEE gây ra.

### RBM-007 Ambiguity Management

- Nếu chưa chắc, giữ draft annotation thay vì chọn cứng.
- Lưu top candidates, rule hits, fallback level.
- Tạo output cho Phase 05 và UI review.

### RBM-008 Output Restore and Context Update

- Restore placeholder, chạy number/date/unit conversion.
- Cập nhật active entity set, scene memory, TM checkpoints.
- Sinh đồng thời clean output và annotated draft.

## Output Contract

### Clean Output

- văn bản đã dịch dùng để đọc
- tối thiểu chú thích

### Draft Output

- có annotation
- có unresolved ambiguity markers
- có source mapping hoặc explanation khi cần

## Acceptance Criteria

- Dịch được ít nhất một chapter end-to-end.
- Không phá placeholder.
- Candidate ranking không bỏ qua priority.
- `number_converter.py` hoạt động đúng khi tích hợp với Trie.
- Batch mode chạy ổn định nhiều chapter.
- Có clean output và draft annotated.
- Có trace đủ để giải thích vì sao engine chọn candidate và khi nào rơi xuống low-priority fallback.

## Immediate Next Slice

1. Tạo `rbmt_translator.py` skeleton.
2. Tạo sentence segmenter.
3. Tạo structure preservation production Python.
4. Tạo candidate ranking theo metadata + `luat_nhan_trigger` + trace scoring.

---
Previous Phase: [Phase 03 - EAPEE](./phase-03-eapee.md)  
Next Phase: [Phase 05 - QA Engine](./phase-05-qa-engine.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
