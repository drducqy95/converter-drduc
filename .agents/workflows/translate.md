---
description: 🌐 Dịch thuật chuyên sâu đa thể loại với Translation Engine
---

# WORKFLOW: /translate — Trinity Translation Engine v2.0

Bạn là **Nhóm Tác Tử Dịch Thuật Đa Nhiệm (MATT)**. Vai trò: Phân tích → Dịch thô → Phản tỉnh → Hiệu đính.

## ⚠️ PRIME DIRECTIVE (BẮT BUỘC TRƯỚC KHI DỊCH)
1. Đọc: `global_skills/skills/translation/SKILL.md`, `translation_config.json`
2. Load: `glossary.json`, `pronouns.json`, `characters.json`, `context.json`, `worldbuilding.json`, `progress.json`, `~/.gemini/antigravity/translation/global_pronouns.json`
3. Nếu đã có compiled wiki: load `Translation Atlas`, `Translation Reference`, `Translation Pronouns`, rồi mới rơi xuống raw JSON khi cần xác minh chi tiết.
*Lưu ý: Nếu chưa có project, chạy `/translate-setup` trước.*

Chuẩn bị deterministic từ terminal khi cần batch QA hoặc app non-LLM:
- `python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" translate next --deterministic`
- `python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" translate all --deterministic`
- `python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" translation-memory batch-apply --input-dir source`
- `python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_translation_runtime.py" --project [PROJECT] batch-apply --input-dir source --json`
- Artifact mặc định: `artifacts/translation-db/chapters/chapter_XXX.rbmt.md` và `chapter_XXX.report.json`

## GĐ 0: Context Detection
- `/translate [chapter]` → Dịch chương cụ thể
- `/translate next` → Lấy chương tiếp theo từ progress
- `/translate all` → Batch mode (Loop tất cả)
- `/translate [text/file]` → Dịch text/file
- `/translate` → Hỏi: "Anh muốn dịch gì?"
*Chưa có config:* Đọc `genre-profiles.md` → Auto-detect từ 500 từ đầu → Hỏi xác nhận → Tạo config tạm.

## GĐ 1: PHÂN TÍCH (Tác Tử Phân Tích)
> Sub-skills: glossary-manager, pronoun-resolver, context-analyzer, worldbuilding-tracker
**1.1 NER:** Quét text, kiểm tra thuật ngữ trong `glossary.json`. Thuật ngữ mới: Định danh cố định, ghi nhận (pending_sync=true), báo user.
**1.2 Nhân vật & Xưng hô:** Quét nhân vật (`characters.json`). Người mới: tạo node. Check mood. Tính xưng hô theo thứ tự: `Translation Pronouns` wiki page → `pronouns.json` (project overrides) → `~/.gemini/antigravity/translation/global_pronouns.json` (shared common groups / Shared Pronoun Registry) → `pronoun-matrix.json` (fallback rules). Nếu đổi xưng hô quá lớn (>20 điểm) thì dừng lại TRƯỚC KHI dịch gốc và hỏi user.
**1.3 Macro Context:** Đọc `context.json` (overview + 3-5 sub-chapters gần nhất, ≤600 tokens).
**1.4 Worldbuilding:** Quét entity mới theo Quy Trình 1 (thế lực, vũ khí, công pháp, location, đột phá, gia phả). Update `worldbuilding.json` và tóm tắt entity mới.

## GĐ 2: DỊCH THÔ (Tác Tử Dịch Thuật)
> Dùng prompt template: `resources/prompt-templates/[genre].md`
Lắp 5 block XML:
- `<SYSTEM_PERSONA>` (genre)
- `<MACRO_CONTEXT>` (từ GĐ 1.3)
- `<DYNAMIC_GLOSSARY>` (từ glossary, ⚡ BẮT BUỘC tuân thủ)
- `<RELATIONSHIP_GRAPH>` (xưng hô, 🔒 BẮT BUỘC tuân thủ)
- `<SOURCE_TEXT>` (Văn bản gốc)
Thực hiện dịch giữ nguyên tone/style. Lưu nháp vào: `drafts/draft_chapter_XXX.md`.

## GĐ 3: PHẢN TỈNH (Tác Tử Phản Tỉnh)
> Sub-skill: reflection-evaluator.md
Đổi persona thành Biên tập viên. Đánh giá Draft ↔ Source + Glossary + Characters.
**4 Trục đánh giá:** Accuracy (30%), Terminology (25%), Pronouns (25%), Fluency (20%).
**Trừ điểm khi lỗi:** Critical(-10), Major(-5), Minor(-2).
- Vòng 1: >=85(PASS), <85(REVISE)
- Vòng 2: >=80(PASS), <80(REVISE)
- Vòng 3: >=70(ACCEPT), <70(FLAG)

## GĐ 4: HIỆU ĐÍNH (Tác Tử Hiệu Đính)
Nhận feedback GĐ3 → Áp dụng sửa lỗi vào file nháp → Đưa lại về GĐ3 re-evaluate.

## GĐ 5: OUTPUT & STATE UPDATE
**5.1 Lưu bản cuối:** Markdown sạch ra `output/chapter_XXX.md`
**5.2 Cập nhật States:**
- `glossary.json`: Thêm thuật ngữ.
- `pronouns.json`: Thêm/cập nhật project-specific pronoun groups nếu xuất hiện cách xưng hô riêng chỉ đúng cho project hiện tại.
- `characters.json`: Nhân vật mới, tu vi (realms, systems, resources), faction, weapon, status (alive/dead), gia phả, timeline, tính lại `readiness_score`.
- `context.json`: Chapter summary (≤50 từ), key events, active characters.
- `worldbuilding.json`: Cập nhật chi tiết thế lực, location, cultivation_systems (realms, đột phá), tài nguyên, items, power ranking.
- `progress.json`: Đánh dấu xong, update current_chapter.
 - `Translation Atlas` / `Translation Reference` / `Translation Pronouns`: refresh compiled wiki hubs để recap và Obsidian dùng lại ngay.
**5.3 Integrity Check (Quy Trình 2):** Cross-check Faction/Weapon/System/Alive giữa các file. Tự sửa lỗi + log warning.
**5.4 Sync Global:** Thêm glossary có pending_sync vào master glossary và merge pronoun common mới vào `~/.gemini/antigravity/translation/global_pronouns.json` nếu đủ tính tái sử dụng liên project.
**5.4b Build Database:** Rebuild `artifacts/translation-db/` và shared database theo cặp ngôn ngữ để batch app không-LLM có thể dùng lại ngay.
**5.4c Deterministic Runtime QA:** Dùng `translation-memory lookup`, `translation-memory apply`, và `translation-memory resolve-pronoun` để kiểm tra DB vừa build có thể tra thuật ngữ, thay thế cụm từ, và chọn xưng hô đúng trước khi đẩy sang app batch.
**5.4d Chapter Prep:** Dùng `trinity translate next --deterministic` hoặc `trinity translate all --deterministic` để sinh RBMT output/report theo chapter mà không ghi đè `output/chapter_XXX.md` mặc định.
**5.4e Folder Batch Runtime:** Dùng `trinity translation-memory batch-apply --input-dir [DIR]` khi cần batch-translate cả thư mục cho app non-LLM hoặc pipeline hậu xử lý.
**5.4f Standalone Runtime:** Dùng `trinity_translation_runtime.py` khi app ngoài Trinity cần gọi runtime trực tiếp và lấy JSON ổn định thay vì parse output của CLI checkpoint.
**5.5 Illustrations (Quy Trình 3):** Generate image nếu đủ readiness score (chân dung >=5, map >=5, diagram count >=8) vào thư mục tương ứng.
**5.6 Log:** Ghi log vào `logs/reflection_log.jsonl`.

**5.7 🔒 State Verification Gate (BẮT BUỘC SAU MỖI CHƯƠNG/BÀI):**
Đây là bước KHÔNG ĐƯỢC BỎ QUA, áp dụng cho TẤT CẢ quy trình dịch (single, next, all, batch, text/file).

**Quy trình quét:**
1. **Scan State Files:** Đọc lại 6 file state sau khi ghi:
   - `progress.json` → Xác nhận `current_chapter` đã tăng, chapter vừa dịch có `status: "done"`.
   - `context.json` → Xác nhận có entry summary cho chapter vừa dịch.
   - `characters.json` → Xác nhận nhân vật mới (nếu có) đã được thêm, status đúng.
   - `worldbuilding.json` → Xác nhận entity mới (nếu có) đã được thêm.
   - `glossary.json` → Xác nhận thuật ngữ mới (nếu có) đã được ghi.
   - `pronouns.json` → Xác nhận xưng hô mới (nếu có) đã được cập nhật.
2. **Validation Rules:**
   - ✅ Tất cả file phải là JSON hợp lệ (parse không lỗi).
   - ✅ `progress.json.current_chapter` phải khớp chapter vừa dịch xong.
   - ✅ Không có nhân vật trùng ID trong `characters.json`.
   - ✅ Không có thuật ngữ trùng key trong `glossary.json`.
   - ✅ Output file `output/chapter_XXX.md` phải tồn tại và không rỗng.
3. **Kết quả:**
   - ✅ **PASS:** Báo `"🔍 State verified for Chapter [X] — All [N] files consistent."` → Cho phép tiếp tục.
   - ✖️ **FAIL:** Lập tức **DỪNG TOÀN BỘ QUY TRÌNH**. Báo chi tiết lỗi:
     ```
     ⛔ STATE VERIFICATION FAILED — Chapter [X]
     File: [tên file lỗi]
     Issue: [mô tả cụ thể]
     Expected: [giá trị kỳ vọng]
     Actual: [giá trị thực tế]
     ```
     TUYỆT ĐỐI KHÔNG dịch tiếp, KHÔNG save-brain, KHÔNG recap cho đến khi user xác nhận fix xong.

## GĐ 6: BÁO CÁO & TIẾP TỤC
**6.1 Report ngắn sau từng chương/bài:**
"✅ CHƯƠNG [X] XONG! Score: [Y]"
Tóm tắt ngắn gọn thay đổi: Thuật ngữ, Nhân vật, Worldbuilding (thế lực, đột phá...).
Hướng dẫn Next Steps (ví dụ view wiki, save-brain).

**6.2 Batch Mode (Long Tasks):**
Dành cho task dài (>10 chương truyện hoặc >10 bài viết thể loại khác) chế độ `all`:
1. Tự động sang chương/bài tiếp. Báo tiến độ: "📊 [X]/[Total] items ([%]%)".
2. **SAU MỖI CHƯƠNG/BÀI (BẮT BUỘC):**
   - Chạy **GĐ 5.7 State Verification Gate** — quét và xác minh toàn bộ state files.
   - ✖️ **FAIL:** Lập tức DỪNG batch. Báo lỗi chi tiết cho user. TUYỆT ĐỐI KHÔNG dịch tiếp, KHÔNG save-brain.
   - ✅ **PASS:** Tiếp tục sang chương/bài kế tiếp.
3. **CHECKPOINT LỚN MỖI 10 CHƯƠNG/BÀI:**
   - Sau khi 10 chương PASS liên tiếp qua State Verification Gate:
   - Chạy tuần tự workflow `@[/save-brain]`, xong chạy `@[/recap]`.
   - Sau khi hoàn thành recap: TỰ TRỰC TIẾP CHẠY BATCH TIẾP mà không hỏi user cho đến khi hết task.
4. **EMERGENCY STOP:** Nếu 2 chương liên tiếp FAIL State Verification → Dừng vĩnh viễn, yêu cầu user can thiệp thủ công.

## 🛡️ RESILIENCE PATTERNS
- **Overlength (>3000 từ):** Chia ra segment 1000-1500 từ → dịch nối liền mạch → merge.
- **Gender unclear:** Dùng đại từ trung tính, note `[⚠️ gender unclear]` để update sau.
- **Term ambiguous:** Theo ngữ cảnh tối ưu, lock=false vào glossary.
- **Context overflow (>600 tokens):** Cắt bớt relevant context, chỉ giữ 100 token overview và 2 chương gần nhất.

## ⚠️ NEXT STEPS
⌨️ `/translate next` | `/translate-setup`
⌨️ `/translate-wiki` (character/faction/weapon/technique/map/worldview/cultivation)
⌨️ `/save-brain` | `/recap`
