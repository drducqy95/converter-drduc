# Phase 06: State Management & Translation Memory

Status: ⬜ Pending  
Progress: 5%  
Dependencies: Phase 04 (RBMT Core), Phase 05 (QA recommended)

## Objective

Xây dựng lớp trạng thái dự án và Translation Memory để hệ thống có thể tiếp tục làm việc qua nhiều phiên, nhiều chapter và nhiều dự án, đồng thời hỗ trợ candidate workflow cho learned entries và learned rules.

## Deliverables

- `project_manager.py`
- `translation_memory.py`
- `obsidian_sync.py`
- SQLite schema cho project/state/TM/candidate rules

## Core State Model

Phase này phải quản lý tối thiểu:

- project metadata
- chapter progress
- segment history
- TM exact/fuzzy entries
- candidate dictionary entries
- candidate rules
- provenance và hit count
- translation trace và fallback evidence

## Suggested Persistence Domains

- `projects`
- `chapters`
- `segments`
- `tm_entries`
- `candidate_entries`
- `candidate_rules`
- `audit_events`
- `entry_reviews`
- `runtime_stats`

## Workstreams

### 1. Project Manager

- Create/open/update/archive project
- Save project config
- Save active chapter state
- Resume đúng vị trí dang dở

### 2. Translation Memory

- Exact match
- Fuzzy match
- scoring / threshold
- provenance and usage history

### 3. Candidate Workflow

- Learned terms/rules không được activate ngay.
- Trạng thái mặc định là `candidate`.
- Chỉ khi người dùng hoặc reviewer duyệt mới chuyển `verified`.

### 4. Provenance Tracking

- `source_dict`
- `project_id`
- `created_at`
- `updated_at`
- `status`
- `hit_count`

### 5. Import and Sync

- Import từ dự án cũ
- Obsidian sync nếu cần
- Watch mode là tùy chọn sau baseline

## Detailed Task Breakdown

### STM-001 Persistence Schema

- Chốt schema cho project, chapter, segment, TM, candidate entries, candidate rules, audit events.
- Tạo khóa nối với `entry_id` của dictionary database.
- Chốt field cho translation trace và fallback evidence.

### STM-002 Project Manager

- Tạo/open/update/archive project.
- Lưu active chapter, config snapshot, runtime version.
- Resume đúng vị trí và đúng dictionary build version.

### STM-003 Translation Memory

- Exact match, fuzzy match, scoring, threshold.
- Ghi provenance, reviewer feedback, usage history.
- Cho phép phân biệt TM verified với TM candidate.

### STM-004 Candidate Workflow

- Mọi learned term/rule mặc định vào trạng thái `candidate`.
- Có vòng duyệt `candidate -> verified -> locked`.
- Lưu reviewer reason và related segments.

### STM-005 History Import

- Import `VietPhraseHistory.txt`, `NamesHistory.txt`, `Names2History.txt`, `ChinesePhienAmWordsHistory.txt`.
- Map sang `audit_events`.
- Giữ raw payload đủ để truy vết khi cần.

### STM-006 Runtime Analytics

- Đo hit rate theo source_dict, priority tier, fallback level.
- Đo tần suất residual `PhienAm`, `P0`, unresolved ambiguity.
- Tạo báo cáo để quyết định tối ưu layer dictionary ở Phase 01/04.

### STM-007 Optional Sync

- Chuẩn bị export/import với Obsidian hoặc project external notes.
- Không để sync contract làm rối schema cốt lõi.
- Chỉ mở khi baseline persistence đã ổn định.

## Acceptance Criteria

- Tạo project mới được.
- Resume project giữa chừng được.
- TM exact/fuzzy hoạt động.
- Candidate entries/rules có lifecycle rõ ràng.
- Có thể import tri thức từ dữ liệu cũ.
- Có analytics đủ để đánh giá hiệu quả thực tế của metadata-first runtime và residual fallback policy.

## Immediate Next Slice

1. Chốt SQLite schema cho projects + tm_entries.
2. Xây `project_manager.py`.
3. Xây `translation_memory.py`.
4. Thêm provenance fields chuẩn + translation trace fields.

---
Previous Phase: [Phase 05 - QA Engine](./phase-05-qa-engine.md)  
Next Phase: [Phase 07 - EN-VI Engine](./phase-07-en-vi.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
