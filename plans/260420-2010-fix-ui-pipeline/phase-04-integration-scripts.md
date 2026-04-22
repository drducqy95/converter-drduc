# Phase 04: Integration & Scripts

Status: ⬜ Pending
Dependencies: Phase 02, Phase 03

## Objective
Tạo npm scripts tiện ích để user chạy cả HTTP bridge + Vite dev server bằng 1 lệnh, và đảm bảo cả hai hướng (Tauri + HTTP) tích hợp mượt mà.

## Requirements

### Functional
- [ ] `npm run bridge` chạy Python HTTP bridge standalone
- [ ] `npm run dev:bridge` chạy cả bridge + Vite dev server
- [ ] Khi dừng `dev:bridge`, cả 2 process đều bị kill

### Non-Functional
- [ ] Cross-platform awareness (Windows primary, document Linux variant)

## Implementation Steps

1. [ ] **Thêm npm scripts vào `desktop/package.json`**
   ```json
   {
     "scripts": {
       "dev": "vite",
       "build": "vite build",
       "tauri:dev": "tauri dev",
       "tauri:build": "tauri build",
       "bridge": "cd .. && python -m src.ui.http_bridge --port 9721",
       "dev:bridge": "start /B npm run bridge && timeout /t 2 /nobreak >nul && vite"
     }
   }
   ```

2. [ ] **Thêm `.env.development` cho bridge URL mặc định**
   ```env
   VITE_BRIDGE_URL=http://localhost:9721
   ```

3. [ ] **Tạo `desktop/README-dev.md` hướng dẫn chạy**
   - Hướng dẫn 3 chế độ: Tauri:dev, HTTP bridge, Browser-only
   - Troubleshooting: port conflict, Python not found
   - Environment variables reference

## Files to Create/Modify
- `desktop/package.json` — **MODIFY** (+ 2 scripts)
- `desktop/.env.development` — **NEW** (1 line)
- `desktop/README-dev.md` — **NEW** (hướng dẫn)

## Test Criteria
- [ ] `npm run bridge` starts Python HTTP server on port 9721
- [ ] `npm run dev:bridge` starts both processes
- [ ] Ctrl+C kills both processes cleanly
- [ ] Bridge URL from `.env.development` is used by httpTransport

---
Next Phase: [phase-05-testing.md](./phase-05-testing.md)
