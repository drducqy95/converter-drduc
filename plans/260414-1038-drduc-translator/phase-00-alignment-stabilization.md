# Phase 00: Alignment & Stabilization

Status: ✅ Done  
Progress: 100%  
Dependencies: None

## Objective

Chốt baseline kỹ thuật của repo, sửa blocker ngắn hạn và thống nhất lại nguồn sự thật giữa production Python, prototype JS và hệ thống tài liệu kế hoạch.

## Why This Phase Exists

Phase này không có trong kế hoạch cũ nhưng bắt buộc phải có vì repo hiện đang có:

- production code và prototype song song;
- tracker không phản ánh đúng tiến độ thật;
- plan cũ trùng lặp và dễ gây hiểu nhầm;
- một lỗi test đang chặn việc đóng nền tảng.

## Deliverables

- Baseline test rõ ràng.
- Production boundary được chốt bằng tài liệu.
- Tracker và phase docs đồng bộ với master plan.
- Xóa hoặc hợp nhất các bản plan cũ gây chồng chéo.

## Outcome

- Blocker `_parse_md_table()` đã được sửa.
- Full Python test suite đã xanh.
- README đã được đồng bộ theo boundary `Python = production`, `JS = prototype/reference`.
- `project_progress.json` đã phản ánh Phase 00 là `DONE`.

## Workstreams

### 1. Baseline Validation

- Chạy full test Python.
- Xác định blocker thực tế.
- Ghi lại số liệu baseline cho compile DB, load Trie, lookup, số test pass/fail.

### 2. Production Boundary

- Chốt Python là production engine.
- Chốt JS là prototype/reference, không dùng làm nguồn sự thật vận hành.
- Ghi rõ boundary này trong plan và README/tài liệu kiến trúc.

### 3. Documentation Cleanup

- Gộp logic từ plan cũ về master plan mới.
- Tạo phase docs tương thích với master plan.
- Xóa các file plan cũ không còn là authoritative source.

### 4. Immediate Fixes

- Sửa lỗi parser Markdown table đang làm fail test.
- Kiểm tra lại `requirements.txt`, `pyproject.toml`, entry points.
- Bảo đảm repo có một baseline sạch để mở tiếp Phase 01.

## Detailed Task Breakdown

### ALN-001 Baseline Audit

- Chạy baseline test Python.
- Ghi nhận số test pass/fail.
- Ghi lại DB stats hiện có.

### ALN-002 Plan Consolidation

- Xác nhận master plan là nguồn kế hoạch duy nhất.
- Xác nhận phase docs là execution docs chính thức.
- Loại bỏ plan cũ gây chồng chéo.

### ALN-003 Stack Boundary

- Chốt Python là production engine.
- Chốt JS là prototype/reference.
- Ghi quyết định vào tài liệu.

### ALN-004 Source Inventory

- Đồng bộ inventory nguồn từ `Dictionaries.ini`.
- Đối chiếu với migration script hiện tại.
- Gắn vai trò logic cho từng source.

### ALN-005 Short-Term Fixes

- Sửa `_parse_md_table()`.
- Kiểm tra requirements và runtime assumptions.
- Chuẩn bị repo cho Phase 01 execution.

## Files in Scope

- `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`
- `plans/260414-1038-drduc-translator/phase-*.md`
- `project_progress.json`
- `src/core/md_dictionary_compiler.py`
- `tests/test_phase1.py`

## Acceptance Criteria

- Full test baseline đã được xác nhận và ghi lại.
- Không còn mơ hồ về production stack.
- Bộ plan trong `plans/` chỉ còn 1 master plan + phase docs đang dùng.
- Đã sẵn sàng mở execution của Phase 01 mà không còn xung đột tài liệu.

## Estimated Effort

- 1 đến 2 session.

---
Next Phase: [Phase 01 - Foundation Closeout](./phase-01-foundation.md)  
Master Plan: [Master Plan Detailed VI](./master_plan_detailed_vi.md)
