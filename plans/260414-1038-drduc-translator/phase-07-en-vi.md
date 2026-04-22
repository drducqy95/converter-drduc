# Phase 07: EN-VI Engine

Status: ⬜ Pending  
Progress: 0%  
Dependencies: Phase 01 (Foundation), Phase 04 (RBMT patterns reusable)

## Objective

Mở rộng nền tảng phrase matching và rule-based translation sang Anh-Việt với phạm vi nhỏ hơn và ít phức tạp hơn ZH-VI, nhưng vẫn dùng chung tư duy priority, phrase-first và QA.

## Deliverables

- `en_vi_translator.py`
- tokenizer + phrase matcher
- rule set cơ bản cho adjective order, possessive, tense markers
- test corpus EN-VI

## Workstreams

### 1. Data Preparation

- Chuẩn hóa nguồn EN-VI hiện có.
- Tách phrase-level và word-level entries.
- Chốt priority giữa phrase dictionary và single-word fallback.
- Dùng cùng metadata model để sau này UI, QA và TM không phải tách hai nhánh dữ liệu.

### 2. Tokenization and Matching

- English tokenization
- multi-word phrase priority
- punctuation-aware segmentation

### 3. Grammar Rules

- adjective + noun
- possessive
- article removal
- plural handling
- tense marker hints

### 4. QA Reuse

- Tận dụng QA framework từ Phase 05.
- Tận dụng state/TM nếu phù hợp.

## Detailed Task Breakdown

### ENVI-001 Data Normalization

- Chuẩn hóa EN-VI entries theo metadata model đang dùng cho ZH-VI.
- Gắn source role và priority tier rõ ràng.
- Tách hot-path và cold-path fields để không phình runtime DB.

### ENVI-002 Tokenization and Phrase Matching

- Xây tokenizer English ổn định cho phrase-first matching.
- Ưu tiên multi-word units trước single-word fallback.
- Giữ punctuation-aware segmentation để không phá cấu trúc.

### ENVI-003 Grammar Transfer Baseline

- Rule cho adjective order, possessive, article removal, plural, tense hints.
- Tránh mở rộng phrase hardcode vô hạn cho các pattern ngữ pháp thông dụng.
- Ghi trace cho QA giải thích được rule nào đã chạy.

### ENVI-004 Shared Infrastructure Reuse

- Tái dùng TM, QA, reporting, state management khi phù hợp.
- Không tạo nhánh schema riêng nếu chưa thật sự cần.
- Giữ contract chung để UI chỉ cần một viewer logic.

### ENVI-005 Test Corpus and Regression

- Tạo corpus EN-VI baseline cho câu ngắn và đoạn ngắn.
- Đo phrase priority, grammar transfer, residual ambiguity.
- Bảo đảm không làm ảnh hưởng core ZH-VI.

## Acceptance Criteria

- Dịch được câu và đoạn ngắn EN-VI bằng baseline rule-based.
- Phrase priority hoạt động đúng.
- Không ảnh hưởng core ZH-VI.

## Immediate Next Slice

1. Chuẩn hóa dictionary EN-VI.
2. Tokenizer + phrase matcher.
3. 3-5 rule grammar đầu tiên.
4. Test corpus nội bộ + trace format cho QA.

---
Previous Phase: [Phase 06 - State Management & Translation Memory](./phase-06-state-tm.md)  
Next Phase: [Phase 08 - Desktop UI](./phase-08-desktop-ui.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
