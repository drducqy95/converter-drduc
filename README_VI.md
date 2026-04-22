# Converter by DrDuc

Workspace dịch thuật không dùng LLM, tập trung `ZH -> VI` và có baseline `EN -> VI`, dùng migrate từ điển, Trie, LuatNhan, RBMT, QA, translation memory và desktop workflow.

## Trạng Thái Hiện Tại

- Production core: Python.
- Kế hoạch thực thi chính: `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`.
- Phase 00-07 đã có artifact chạy được và test.
- Phase 08 đã có React shell, sidecar protocol Python và Tauri scaffold; build web đã xác thực, native Tauri build còn phụ thuộc Rust toolchain.
- Lệnh test chuẩn: `python -m pytest`

## Những Gì Đang Chạy Được

- `src/pipeline/`: import tài liệu, tách chapter, preserve structure, scan entity, build relationship, sinh `translation_config.json`.
- `src/eapee/`: emotion detector, emotion state, pronoun resolver, expression bank.
- `src/engine/rbmt_translator.py`: RBMT orchestrator sinh đồng thời clean output và draft annotated.
- `src/qa/`: terminology/pronoun/emotion/structure/untranslated/length checks và QA report.
- `src/state/`: project manager, SQLite translation memory, candidate workflow, runtime stats, Obsidian export.
- `src/en_vi/en_vi_translator.py`: baseline EN-VI phrase-first với grammar rules cơ bản.
- `src/ui/`: command protocol và sidecar bridge cho desktop app.
- `desktop/`: React shell build được bằng `npm run build`; `src-tauri/` đã có skeleton tối thiểu.

## Ranh Giới Production

- Python trong `src/core/`, `src/engine/`, `src/pipeline/`, `src/state/`, `src/qa/`, `src/eapee/`, `src/en_vi/`, `src/ui/` là đường chạy production.
- JavaScript trong `src/preprocessor/`, `src/parser/`, `src/rules/`, `src/learning/` vẫn được giữ như prototype/reference, không phải core authoritative.

## Kiểm Chứng Gần Nhất

- `python -m pytest`: `98 passed`
- `desktop/npm run build`: build web shell thành công

## Tài Liệu Chính

- Master plan: `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`
- Tracker: `project_progress.json`
- Desktop scaffold: `desktop/README.md`
