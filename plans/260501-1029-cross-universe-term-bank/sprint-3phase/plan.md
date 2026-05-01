# Sprint: 3-Phase Priority — Data Migration + Universe Detector + Context Package

Created: 2026-05-01T19:51+07:00
Status: 🟡 In Progress

## Overview
Hoàn thành 3 phase ưu tiên cao nhất còn thiếu trong roadmap v24:
- **Phase A:** Import toàn bộ 23 file MD → term bank JSONL
- **Phase B:** Tách UniverseDetector + fingerprints.json
- **Phase C:** Tạo src/context/ package

## Design Decisions
- **Q1:** Mỗi bộ truyện = 1 universe riêng (KHÔNG gộp)
- **Q2:** Import TOÀN BỘ 23 files (ChinaWebNovel + Comic + FilmHollywood + Manga + World)

## Source Files (23 files, ~195 KB)

| # | Folder | File | Size | Universe ID |
|---|--------|------|-----:|-------------|
| 1 | ChinaWebNovel | Dau_La_Dai_Luc.md | 4.1 KB | `dau_la_dai_luc` |
| 2 | ChinaWebNovel | Dau_Pha_Thuong_Khung.md | 3.9 KB | `dau_pha_thuong_khung` |
| 3 | ChinaWebNovel | Gia_Thien.md | 3.8 KB | `gia_thien` |
| 4 | ChinaWebNovel | Hoan_My_The_Gioi.md | 3.6 KB | `hoan_my_the_gioi` |
| 5 | ChinaWebNovel | Kiem_Lai.md | 3.1 KB | `kiem_lai` |
| 6 | ChinaWebNovel | Phan_Nhan_Tu_Tien.md | 14.6 KB | `pham_nhan_tu_tien` |
| 7 | ChinaWebNovel | Quy_Bi_Chi_Chu.md | 3.6 KB | `quy_bi_chi_chu` |
| 8 | ChinaWebNovel | Than_An_Vuong_Toa.md | 3.6 KB | `than_an_vuong_toa` |
| 9 | ChinaWebNovel | Tien_Nghich.md | 3.4 KB | `tien_nghich` |
| 10 | ChinaWebNovel | Tru_Tien.md | 2.9 KB | `tru_tien` |
| 11 | ChinaWebNovel | Tuyet_Trung_Han_Dao_Hanh.md | 2.9 KB | `tuyet_trung_han_dao_hanh` |
| 12 | ChinaWebNovel | Vu_Dong_Can_Khon.md | 3.6 KB | `vu_dong_can_khon` |
| 13 | Comic/Marvel | Name_Marvel.md | 13.0 KB | `marvel` |
| 14 | FilmHollywood | Name_HarryPotter.md | 9.2 KB | `harry_potter` |
| 15 | FilmHollywood | Name_Hollywood.md | 6.7 KB | `hollywood` |
| 16 | FilmHollywood | Name_TheOneRing.md | 7.4 KB | `the_one_ring` |
| 17 | Manga | Name_Bleach.md | 35.8 KB | `bleach` |
| 18 | Manga | Name_Doremon.md | 17.5 KB | `doremon` |
| 19 | Manga | Name_Manga.md | 5.4 KB | `manga_shared` |
| 20 | Manga | Name_Naruto.md | 11.5 KB | `naruto` |
| 21 | Manga | Name_OnePiece.md | 14.3 KB | `one_piece` |
| 22 | Manga | Name_OnePuchman.md | 6.8 KB | `one_punch_man` |
| 23 | World | Name_Doithuc.md | 6.2 KB | `real_world` (global) |

## Phases

| Phase | Name | Duration | Dep | Status | File |
|-------|------|----------|-----|--------|------|
| A | Term Bank Data Migration | 1 session | — | ⬜ Pending | [phase-A-migration.md](phase-A-migration.md) |
| B | Universe Detector Module | 1 session | A | ⬜ Pending | [phase-B-universe-detector.md](phase-B-universe-detector.md) |
| C | Context Package | 1-2 sessions | B | ⬜ Pending | [phase-C-context-package.md](phase-C-context-package.md) |

## Target Metrics

| Metric | Before | After |
|--------|--------|-------|
| Term bank records | ~49 | ≥ 1000 |
| Universe folders | 7 | ≥ 18 |
| UniverseDetector module | ❌ | ✅ |
| Context modules | 0/6 | 6/6 |
| Total tests | 223 | ≥ 250 |

## Quick Commands
- Start Phase A: `/code phase-A`
- Check next: `/next`
- Save context: `/save-brain`
