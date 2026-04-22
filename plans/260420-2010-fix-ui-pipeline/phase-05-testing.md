# Phase 05: Testing & Verification

Status: ⬜ Pending
Dependencies: Phase 01, 02, 03, 04

## Objective
Đảm bảo cả hai hướng sửa hoạt động đúng, không break code hiện tại, và ghi nhận kết quả vào Trinity state.

## Requirements

### Functional
- [ ] Tất cả 99+ pytest tests PASS
- [ ] TypeScript build PASS (no errors)
- [ ] HTTP bridge test mới PASS
- [ ] Tauri build PASS (nếu toolchain available)
- [ ] End-to-end pipeline hoạt động qua browser + HTTP bridge

### Non-Functional
- [ ] Test coverage cho HTTP bridge: health, sidecar, CORS, error cases
- [ ] No regression trên existing sidecar tests

## Implementation Steps

1. [ ] **Thêm HTTP bridge test vào `tests/test_phase7_and_ui.py`**
   ```python
   def test_http_bridge_health_and_sidecar_endpoint():
       """Start HTTP bridge in background, test endpoints, shut down."""
       import subprocess, time, urllib.request, json

       # Start bridge
       proc = subprocess.Popen(
           [sys.executable, "-m", "src.ui.http_bridge", "--port", "19721"],
           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
       )
       time.sleep(1.5)

       try:
           # Health check
           health = urllib.request.urlopen("http://localhost:19721/api/health")
           data = json.loads(health.read())
           assert data["ok"] is True

           # Sidecar call
           payload = json.dumps({
               "command": "list_projects",
               "payload": {"base_dir": "workspace_projects"},
               "request_id": "test-http",
               "protocol_version": "2026-04-16.phase10",
           }).encode()
           req = urllib.request.Request(
               "http://localhost:19721/api/sidecar",
               data=payload,
               headers={"Content-Type": "application/json"},
           )
           resp = urllib.request.urlopen(req)
           result = json.loads(resp.read())
           assert result["ok"] is True
           assert "projects" in result["data"]
       finally:
           proc.terminate()
           proc.wait(timeout=5)
   ```

2. [ ] **Chạy full pytest suite**
   ```bash
   cd d:\Converter by DrDuc
   python -m pytest tests/ -q
   ```
   Expected: 100+ passed (99 existing + 1 new HTTP bridge test)

3. [ ] **Chạy TypeScript build**
   ```bash
   cd d:\Converter by DrDuc\desktop
   npm run build
   ```
   Expected: exit code 0, no type errors

4. [ ] **Manual verification: HTTP bridge mode**
   - Terminal 1: `python -m src.ui.http_bridge --port 9721`
   - Terminal 2: `cd desktop && npm run dev`
   - Browser `localhost:5173`:
     - [ ] Status bar: "HTTP bridge detected"
     - [ ] Project Manager: project-002 visible
     - [ ] Chọn project → 1672 chapters loaded
     - [ ] Set active chapter → text appears
     - [ ] Translate → Vietnamese output
     - [ ] Dictionary search → results

5. [ ] **Update Trinity state**
   - Cập nhật `project_progress.json` với milestone mới
   - Ghi nhận completion vào `all_global_errors.jsonl` (status: RESOLVED)
   - `/save-brain` checkpoint

## Files to Create/Modify
- `tests/test_phase7_and_ui.py` — **MODIFY** (+ 1 test function)

## Test Criteria
- [ ] `python -m pytest tests/ -q` → all passed
- [ ] `npm run build` → exit code 0
- [ ] HTTP bridge manual test → all 6 checkpoints pass
- [ ] Tauri:dev manual test → all 4 checkpoints pass (Phase 01)

---
Plan complete! Return to: [plan.md](./plan.md)
