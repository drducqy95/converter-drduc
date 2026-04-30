# Báo cáo thay đổi 2026-04-30

## Phạm vi

Thực hiện hardening theo `plans/PHAN_TICH_KY_THUAT_converter-drduc.md`, ưu tiên các hạng mục còn thiếu trong repo hiện tại. Một số mục Sprint 0/P1 trong báo cáo đã có sẵn trước khi sửa: artifact root không còn được Git theo dõi, `name_project/` đã dùng tên chuẩn, JS plan cũ đã nằm trong `docs/archive/`, CI Python/Vite đã tồn tại, `pyproject.toml` đã khai báo dependencies, và Emotion Detector đã có negation guard cơ bản.

## Thay đổi chính

- Thêm `src/pipeline/robust_batch_runner.py` với fault isolation theo chapter, checkpoint JSON, circuit breaker, timeout mềm, output writer, và reset context theo chapter.
- Bổ sung `ContextManager.reset_for_chapter()` để tránh kéo sentence/entity/emotion window qua ranh giới chương.
- Hardening `TrieEngine`:
  - gom xử lý `one_mean` vào resolver có context lookahead;
  - thêm context hint cho các trường hợp như `打电话` và `打折`;
  - normalize chuỗi biểu cảm lặp dài trước Viterbi;
  - giới hạn candidate Viterbi mỗi vị trí;
  - chuyển Viterbi sang backpointer để giảm copy path.
- Bổ sung semantic polarity guard cho Translation Memory fuzzy search để tránh reuse bản dịch gần giống nhưng đảo nghĩa bởi phủ định.
- Bổ sung pretend/feigned emotion guard cho EAPEE để không coi `假装高兴`, `故作愤怒` là emotion thật.
- Bổ sung fallback-chain trace cho Pronoun Resolver khi genre cụ thể thiếu entry và phải rơi về `general`.
- Điều chỉnh RBMT handoff: emotion/dialogue context được detect trên câu nguồn trước grammar transfer, grammar trace mang metadata handoff, pronoun vẫn resolve sau grammar transfer.
- Mở rộng GitHub Actions với job native Tauri build chạy theo `workflow_dispatch` hoặc weekly schedule.

## Test và build

- `python -m py_compile ...`: pass.
- Targeted tests: `107 passed`.
- Full suite: `202 passed`.
- Desktop web build: `npm run build` pass.
- Native Tauri build: `npm run tauri:build` pass.
- Native artifact local: `desktop/src-tauri/target/release/drduc-translator-desktop.exe`.

## Còn lại

- Golden benchmark từ các dự án cũ chưa được xây dựng.
- Unified CLI (`drduc ...`) chưa gom các runner cũ.
- Hot-reload dictionary race condition mới được giảm rủi ro qua batch checkpoint/context reset, chưa có watcher-level deferred reload.
- Scope-limited P5 entity override cần thêm metadata dictionary trước khi bật đầy đủ.
