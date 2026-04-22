# Phase 01: Tauri Toolchain Verify & Rebuild

Status: ⬜ Pending
Dependencies: None

## Objective
Đảm bảo Rust toolchain hoạt động, rebuild Tauri binary, và xác nhận native app có thể chạy Python sidecar.

## Requirements

### Functional
- [ ] Tauri native window mở được
- [ ] Python sidecar được gọi thành công từ Rust backend
- [ ] `list_projects` trả về danh sách project qua native bridge

### Non-Functional
- [ ] Build time < 10 phút (cold build), < 30s (incremental)
- [ ] Binary size hợp lý (< 30MB)

## Implementation Steps

1. [x] **Verify Rust toolchain**
   - Chạy `rustup show`, `rustc --version`, `cargo --version`
   - Xác nhận target `x86_64-pc-windows-msvc` có sẵn
   - Kiểm tra VS Build Tools tại `D:\App\BuildTools\VS2022`
   - Kiểm tra Windows SDK tại `C:\Program Files (x86)\Windows Kits\10`
   - Nếu thiếu: `rustup update stable && rustup target add x86_64-pc-windows-msvc`

2. [x] **Rebuild Tauri binary**
   - `cd d:\Converter by DrDuc\desktop`
   - `npm run tauri:build`
   - Verify output: `src-tauri/target/release/drduc-translator-desktop.exe`
   - Ghi lại build time và binary size

3. [ ] **Smoke test native build**
   - Launch `drduc-translator-desktop.exe`
   - Verify status bar: "Native Tauri bridge detected"
   - Verify `list_projects` trả về project-001, project-002

4. [ ] **Full pipeline test qua Tauri UI**
   - Chọn project-002 → phải hiện 1672 chapters
   - Set active chapter → chapter xuất hiện trong Translation Workspace
   - Bấm Translate → phải ra kết quả tiếng Việt
   - Bấm Run QA → phải ra QA report

## Files to Create/Modify
- Không sửa file nào — chỉ verify và rebuild

## Test Criteria
- [ ] `rustc --version` >= 1.70
- [ ] `npm run tauri:build` exit code 0
- [ ] Binary exists at `src-tauri/target/release/drduc-translator-desktop.exe`
- [ ] Native app mở và gọi sidecar thành công

---
Next Phase: [phase-02-http-bridge-backend.md](./phase-02-http-bridge-backend.md)
