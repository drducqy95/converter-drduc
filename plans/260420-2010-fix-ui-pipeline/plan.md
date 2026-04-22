# Plan: Fix UI Pipeline — Tauri:dev + HTTP Bridge

Created: 2026-04-20T20:10:42+07:00
Status: 🟡 In Progress

## Overview

Sửa lỗi UI pipeline không hoạt động trong browser mode do transport layer fallback sang `browserTransport` (block all commands). Hai hướng sửa song song:
- **Phase A**: Khôi phục Tauri native build (production path)
- **Phase B**: Thêm HTTP bridge transport (development path)

## Tech Stack
- Frontend: React 18 + TypeScript + Vite 5
- Backend: Python 3.14 (sidecar bridge) + Rust (Tauri 2)
- Database: SQLite (project_state.db)
- New: Python stdlib `http.server` (HTTP bridge)

## Phases

| Phase | Name | Tasks | Status | Progress |
|-------|------|-------|--------|----------|
| 01 | Tauri Toolchain Verify | 4 | ⬜ Pending | 0% |
| 02 | HTTP Bridge Backend | 5 | ⬜ Pending | 0% |
| 03 | HTTP Transport Frontend | 4 | ⬜ Pending | 0% |
| 04 | Integration & Scripts | 3 | ⬜ Pending | 0% |
| 05 | Testing & Verification | 5 | ⬜ Pending | 0% |

**Total:** 21 tasks | Ước tính: 2 sessions

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
