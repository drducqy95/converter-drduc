# Phase 00: Baseline Audit & Repo Housekeeping

Status: ⬜ Pending
Priority: P0
Duration: 3-5 ngày
Dependencies: Không có

## Objective
Xác nhận trạng thái thật của repo, đồng bộ tài liệu, dọn root directory, fix pyproject.

## Tasks

### P0-T1 — Clone và verify repo
- [ ] Chạy `python -m pytest --tb=short`
- [ ] Ghi lại: Python version, OS, tests passed/failed, warnings, runtime

### P0-T2 — Đồng bộ README / tracker / Plan
- [ ] Kiểm tra README.md
- [ ] Kiểm tra project_progress.json
- [ ] Đồng bộ test count thật
- [ ] Tạo `docs/ARCHITECTURE_STATUS.md`

### P0-T3 — Dọn root directory
```bash
mkdir -p scripts/debug scripts/run
git mv debug_*.py scripts/debug/ 2>/dev/null || true
git mv run_*.py scripts/run/ 2>/dev/null || true
git mv patch_*.py scripts/debug/ 2>/dev/null || true
```

### P0-T4 — Fix pyproject/dependencies
```toml
[project]
dependencies = [
    "pytest>=7.4",
    "python-rapidjson>=1.10",
    "PyYAML>=6.0",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

## Files to Create/Modify
- `docs/ARCHITECTURE_STATUS.md` — [NEW] Trạng thái kiến trúc hiện tại
- `pyproject.toml` — [MODIFY] Fix dependencies
- `README.md` — [MODIFY] Đồng bộ test count

## Definition of Done
```
[ ] Repo cài được bằng pip install -e .
[ ] pytest chạy được
[ ] README không lệch test count
[ ] Root directory sạch
[ ] docs/ARCHITECTURE_STATUS.md tồn tại
```

---
Next Phase: Phase 01 — Core Governance
