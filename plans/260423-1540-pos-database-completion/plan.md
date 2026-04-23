# Plan: POS Database Completion — Full Tagging & Metadata Pipeline

Created: 2026-04-23T15:40:00+07:00
Status: 🟡 In Progress

## Overview

Hoàn thiện hệ thống POS tagging cho database từ điển ZH-VI (710K entries).
Nâng coverage từ 26.3% lên ≥85%, bổ sung Name Entity taxonomy, gắn Pinyin/Phồn thể,
rewrite source files theo format metadata-rich, và xây dựng NLM pipeline lâu dài.

## Tech Stack
- Database: SQLite (`trie_cache.db`)
- Source Files: Markdown tables (`.md`)
- Compiler: `md_dictionary_compiler.py`
- Seeder: `pos_seeder.py`
- External: CC-CEDICT, NotebookLM ZH-VI Trans
- Language: Python 3.14

## Phases

| Phase | Name | Tasks | Status | Progress |
|-------|------|-------|--------|----------|
| 01 | Schema Extension | 4 | ⬜ Pending | 0% |
| 02 | Quick Wins Tagging | 5 | ⬜ Pending | 0% |
| 03 | CEDICT Enhancement | 6 | ⬜ Pending | 0% |
| 04 | Vietnamese Heuristic | 5 | ⬜ Pending | 0% |
| 05 | Component Decomposition | 5 | ⬜ Pending | 0% |
| 06 | Name Entity & COLLOCATION | 7 | ⬜ Pending | 0% |
| 07 | Pinyin & Traditional Pipeline | 6 | ⬜ Pending | 0% |
| 08 | Source File Rewrite & User Editing | 7 | ⬜ Pending | 0% |
| 09 | NLM Dictionary Research Pipeline | 5 | ⬜ Pending | 0% |

**Tổng:** 50 tasks | Ước tính: 5–7 sessions

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
