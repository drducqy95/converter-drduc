# Phase 08: Desktop UI

Status: ⬜ Pending  
Progress: 0%  
Dependencies: Phase 04 (RBMT Core), Phase 05 (QA), Phase 06 (State/TM)

## Objective

Tạo desktop app dùng Tauri + React để vận hành toàn bộ workflow dịch: quản lý project, từ điển, pre-translation review, translation workspace, QA và candidate approval.

## Start Conditions

Phase này chỉ nên bắt đầu khi:

- RBMT Core có command interface ổn định;
- QA engine có report contract rõ;
- state/TM có persistence schema rõ;
- dictionary metadata đủ giàu để UI hiển thị tooltip, nghĩa phụ và nguồn gốc.

## Deliverables

- Tauri app skeleton
- Python sidecar bridge
- 7 màn hình chính
- command protocol ổn định

## Primary Screens

1. Project Manager
2. Dictionary Manager
3. Translation Workspace
4. Entity & Relationship Viewer
5. Pre-Translation Review
6. QA Report Viewer
7. Settings

## Metadata Requirements for UI

UI phải hiển thị được:

- `target_vi`
- `alternative_meanings`
- `full_explanation`
- `source_dict`
- `priority`
- `status`
- `hit_count`
- fallback level và ambiguity trail

Ngoài ra phải có flow duyệt:

- `candidate -> verified`
- override cho project-specific entries
- review ambiguity từ draft output

## Workstreams

### 1. App Shell

- Init Tauri + React + TypeScript
- sidecar lifecycle management
- IPC/progress events

### 2. Translation Workflow

- import file
- scan entities
- review entities
- translate chapter
- view draft/clean output
- run QA

### 3. Dictionary Workflow

- search/filter
- inspect metadata
- edit priority/source
- approve candidate entries/rules

### 4. Reporting Workflow

- render QA report
- jump to offending segment
- show alternative meanings and explanations

## Detailed Task Breakdown

### UI-001 Command Protocol

- Chốt command contract cho build dictionary, import file, scan entities, translate, run QA, export output.
- Thống nhất progress events, error contract, trace payloads.
- Khóa versioning để backend thay đổi không phá UI âm thầm.

### UI-002 App Shell

- Init Tauri + React + TypeScript.
- Quản lý sidecar lifecycle và long-running tasks.
- Chuẩn bị log viewer tối thiểu cho batch operations.

### UI-003 Project and Pre-Translation Screens

- Project Manager cho create/open/resume/archive.
- Pre-Translation Review cho entity scan, relationship graph, config review.
- Hiển thị cảnh báo ambiguity từ trước khi chạy translate.

### UI-004 Dictionary Manager

- Search/filter/sort theo `source_dict`, `priority`, `status`, `entity_type`.
- Hiển thị hot-path summary và cold-path details như `full_explanation`, `alternative_meanings`.
- Cho phép review `candidate_entries`, `candidate_rules`, project-specific overrides.

### UI-005 Translation Workspace

- Hiển thị clean output, annotated draft và candidate explanations.
- Hiển thị fallback level, ambiguity trail, scoring evidence.
- Cho phép jump từ segment sang dictionary entry hoặc QA issue.

### UI-006 QA Viewer and Review Workflow

- Render `qa_report.md` và JSON QA payload.
- Jump đến offending segment/chapter.
- Hỗ trợ duyệt `candidate -> verified` trực tiếp từ lỗi QA hoặc ambiguity draft.

### UI-007 Packaging and Stability

- Progress streaming cho batch translate.
- Recovery khi sidecar restart hoặc task fail giữa chừng.
- Build Windows dùng được và có smoke test end-to-end.

## Acceptance Criteria

- App khởi động được.
- Python sidecar hoạt động ổn định.
- Có thể chạy end-to-end một project mẫu.
- Có candidate review flow.
- Có build Windows dùng được.
- Người dùng xem được source evidence, fallback level và metadata cần thiết để duyệt từ/rule.

## Immediate Next Slice

1. Chốt command protocol.
2. Init app shell.
3. Build Project Manager + Dictionary Manager.
4. Wire Translation Workspace với backend.

---
Previous Phase: [Phase 07 - EN-VI Engine](./phase-07-en-vi.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
