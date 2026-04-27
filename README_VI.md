# Converter by DrDuc

Workspace dịch thuật không dùng LLM, tập trung `ZH -> VI` và có baseline `EN -> VI`, dùng migrate từ điển, Trie, LuatNhan, RBMT, QA, translation memory và desktop workflow.

## Trạng Thái Hiện Tại

- Production core: Python.
- Kế hoạch thực thi chính: `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`.
- Phase 00-08 đã có artifact chạy được và test.
- v23.0 đã có nền tảng hardening cho TM governance, trace, segment typing, protected span, noise filter và grammar relation detection.
- Lệnh test chuẩn: `python -m pytest`

## Những Gì Đang Chạy Được

- `src/pipeline/`: import tài liệu, tách chapter, preserve structure, scan entity, build relationship, sinh `translation_config.json`.
- `src/eapee/`: emotion detector, emotion state, pronoun resolver, expression bank.
- `src/engine/rbmt_translator.py`: RBMT orchestrator sinh đồng thời clean output và draft annotated.
- `src/qa/`: terminology/pronoun/emotion/structure/untranslated/length checks và QA report.
- `src/state/`: project manager, SQLite translation memory đã tách `tm_machine`/`tm_approved`/`tm_reviewed`, candidate workflow, runtime stats, Obsidian export.
- `src/pipeline/segment_classifier.py`, `packet.py`, `protected_span_registry.py`, `noise_filter.py`: nền tảng v23 cho segment typing và an toàn noise/protected span.
- `src/grammar/`: ClauseSegmenter, RelationDetector, RuleClaim/RuleRegistry/ConflictResolver.
- `src/en_vi/en_vi_translator.py`: baseline EN-VI phrase-first với grammar rules cơ bản.
- `src/ui/`: command protocol và sidecar bridge cho desktop app.
- `desktop/`: React shell build được bằng `npm run build`; `src-tauri/` đã có skeleton tối thiểu.

## Ranh Giới Production

- Python trong `src/core/`, `src/engine/`, `src/pipeline/`, `src/state/`, `src/qa/`, `src/eapee/`, `src/en_vi/`, `src/ui/` là đường chạy production.
- JavaScript trong `src/preprocessor/`, `src/parser/`, `src/rules/`, `src/learning/` vẫn được giữ như prototype/reference, không phải core authoritative.

## Kiểm Chứng Gần Nhất

- `python -m pytest`: `151 passed`
- `desktop/npm run build`: build web shell thành công

## Tài Liệu Chính

- Master plan: `plans/260414-1038-drduc-translator/master_plan_detailed_vi.md`
- V23 hardening plan: `plans/CONVERTER_DRDUC_V23_CORE_HARDENING_PLAN.md`
- Architecture status: `docs/ARCHITECTURE_STATUS.md`
- Tracker: `project_progress.json`
- Desktop scaffold: `desktop/README.md`
