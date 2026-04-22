# Phase 03: EAPEE

Status: ⬜ Pending  
Progress: 0%  
Dependencies: Phase 01 (Foundation), Phase 02 (Pre-Translation Pipeline)

## Objective

Xây dựng engine xưng hô và biểu đạt cảm xúc theo ngữ cảnh nhằm xử lý hội thoại truyện theo 4 chiều: thể loại, quan hệ, cảm xúc, thân phận.

## Why This Phase Matters

Đây là phase quyết định chất lượng “giọng văn” bản dịch. Nếu không có EAPEE, hệ thống chỉ dừng ở mức thay từ và sắp câu, không đủ khác biệt cho truyện dài.

## Deliverables

- `emotion_detector.py`
- `emotion_state.py`
- `pronoun_resolver.py`
- `expression_bank.py`
- dataset expressions / pronoun matrices

## Core Data Model

EAPEE cần tương thích trực tiếp với metadata fields:

- `eapee_context.genre`
- `eapee_context.speaker_identity`
- `eapee_context.listener_identity`
- `eapee_context.emotion_state`

Ngoài ra phải đọc được context từ:

- entity scan
- relationship graph
- scene boundary
- translation config
- metadata dictionary như `entity_type`, `semantic_class`, `cultural_origin`

## Workstreams

### 1. Emotion Detector

- Keyword-based markers
- Dialogue verb markers
- Punctuation markers
- Intensity scoring

### 2. Emotion State Machine

- Carry-over theo scene
- Decay rule theo loại cảm xúc
- Reset khi scene change

### 3. Speaker / Listener Resolution

- Pattern `X nói`, `X đạo`, `đối X`, `với X`
- Context fallback nếu không có speaker rõ
- Liên kết với active entity list từ Phase 02

### 4. Pronoun Matrix

- Cổ trang
- Hiện đại
- Tiên hiệp / huyền huyễn

Mỗi matrix phải xét:

- self
- other
- relationship
- hierarchy
- emotion
- identity override

### 5. Expression Bank

- curses
- endearments
- interjections
- tone markers

## Detailed Task Breakdown

### EAP-001 Context Schema

- Chốt schema cho `genre`, `relationship`, `emotion`, `identity_override`.
- Xác định field nào đến từ Phase 02, field nào đến từ dictionary metadata.
- Chuẩn hóa cách serialize context để Phase 04 dùng trực tiếp.

### EAP-002 Emotion Detector Baseline

- Tạo detector heuristic từ keyword, dialogue verbs, punctuation, intensity markers.
- Cho phép nhiều nhãn cảm xúc đồng thời với confidence score.
- Chuẩn bị hook cho learning-based refinement sau này.

### EAP-003 Emotion State Machine

- Duy trì state theo scene.
- Có decay rule và reset rule.
- Ghi trace để QA kiểm tra drift cảm xúc.

### EAP-004 Speaker and Listener Resolver

- Dò speaker/listener từ pattern hội thoại.
- Liên kết với entity graph từ Phase 02.
- Có fallback an toàn khi câu thoại thiếu speaker rõ ràng.

### EAP-005 Pronoun Matrix

- Xây matrix theo `genre`, `relationship`, `hierarchy`, `emotion`, `identity_override`.
- Tạo lớp override cho trường hợp như `trẫm`, `bổn tọa`, `bần tăng`, `bổn cung`.
- Tách rule mặc định và rule project-specific.

### EAP-006 Expression Bank

- Tạo dataset expressions theo ít nhất 3 genre.
- Gắn metadata về emotion, intensity, speaker identity, safety level.
- Chuẩn bị cơ chế reviewer duyệt và khóa expression.

### EAP-007 Dialogue Test Corpus

- Tạo corpus hội thoại mẫu cho regression test.
- Bao phủ cổ trang, hiện đại, tiên hiệp.
- Đo baseline cho pronoun resolution và tone consistency.

## Acceptance Criteria

- Pronoun resolver xử lý được câu thoại mẫu.
- Có dataset expressions tối thiểu cho ít nhất 3 genre.
- Có fallback an toàn khi không đủ context.
- Có test corpus hội thoại mẫu để benchmark nội bộ.

## Immediate Next Slice

1. Chốt schema pronoun matrix.
2. Tạo dataset expressions tối thiểu.
3. Xây emotion detector heuristic.
4. Tạo speaker/listener resolver baseline và trace format cho QA.

---
Previous Phase: [Phase 02 - Pre-Translation Pipeline](./phase-02-pre-translation.md)  
Next Phase: [Phase 04 - RBMT Core](./phase-04-rbmt-engine.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
