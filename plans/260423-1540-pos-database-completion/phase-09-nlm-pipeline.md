# Phase 09: NotebookLM Dictionary Research Pipeline

Status: ⬜ Pending
Dependencies: Phase 08 (source file format ready)

## Objective
Xây dựng pipeline tự động hóa tra cứu từ điển qua NotebookLM, parse output, gắn vào source files.

## Implementation Steps

1. [ ] **Tạo `src/tools/nlm_batch_exporter.py`**
   - Export batch untagged entries (mặc định 50/batch)
   - Format thành NLM query:
     ```
     Cho các chữ Hán sau, cung cấp:
     1. POS (danh từ/động từ/tính từ/phó từ)
     2. Pinyin (có dấu thanh)
     3. Phồn thể
     4. Nghĩa Hán Việt ngắn gọn

     | # | Giản thể | Pinyin | Phồn thể | POS | Hán Việt |
     |---|----------|--------|----------|-----|----------|
     | 1 | 男子     |        |          |     |          |
     ```
   - CLI: `python src/tools/nlm_batch_exporter.py --category vietphrase_2char --batch-size 50`

2. [ ] **Tạo `src/tools/nlm_response_parser.py`**
   - Parse NLM markdown table response
   - Map POS Vietnamese → English tag:
     - danh từ→NOUN, động từ→VERB, tính từ→ADJECTIVE, phó từ→ADVERB
   - Output: list of `{source, pos_tag, pinyin, traditional}` dicts

3. [ ] **Tạo `src/tools/nlm_enrich_pipeline.py`**
   - Orchestrator: export → query NLM → parse → insert vào source .md
   - CLI modes:
     - `--single-batch`: 1 batch
     - `--auto --max-batches 20`: chạy liên tục
   - Insert vào đúng cột trong source file (không ghi đè cột đã có giá trị)

4. [ ] **Tạo alias NLM và test kết nối**
   ```bash
   nlm login
   nlm alias set zhvi 77682187-4934-431c-b392-42d4a22d5aa4
   nlm notebook query zhvi "Kiểm tra từ 不 trong từ điển"
   ```

5. [ ] **Chạy batch test với 50 entries thật**
   - Export 50 entries `vietphrase_2char` chưa tag
   - Query NLM
   - Parse + insert vào `_vietphrase_2char.md`
   - Recompile + verify DB

## Files to Create/Modify
- `src/tools/nlm_batch_exporter.py` — [NEW]
- `src/tools/nlm_response_parser.py` — [NEW]
- `src/tools/nlm_enrich_pipeline.py` — [NEW]

## Test Criteria
- [ ] Export format đúng markdown table
- [ ] Parse NLM response chính xác ≥90%
- [ ] Round-trip: export → NLM → parse → insert → compile → DB có data mới
- [ ] Source file giữ nguyên entries cũ, chỉ thêm metadata mới

## Lưu ý
> ⚠️ Cần chạy `nlm login` trong terminal riêng trước khi sử dụng pipeline này.
> NLM notebook: ZH-VI Trans (ID: 77682187-4934-431c-b392-42d4a22d5aa4)
