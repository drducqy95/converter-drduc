# Phase 07: Pinyin & Traditional Pipeline

Status: ⬜ Pending
Dependencies: Phase 01 (schema), Phase 03 (CEDICT extract)

## Objective
Xây dựng pre-processing tools để chuyển phồn thể → giản thể và quét pinyin trong text trước khi dịch.

## Implementation Steps

1. [ ] **Tạo `src/tools/traditional_converter.py`**
   - Class `TraditionalConverter`
   - Load bảng `traditional → source` từ DB
   - Method: `convert(text) → simplified_text`
   - Scan từng char, tra bảng, replace

2. [ ] **Tạo `src/tools/pinyin_scanner.py`**
   - Class `PinyinScanner`
   - Load bảng `pinyin → source` từ DB
   - Method: `scan(text) → [(start, end, pinyin, hanzi)]`
   - Detect patterns: tone marks (`nǐ hǎo`) hoặc tone numbers (`ni3 hao3`)

3. [ ] **Tích hợp vào RBMTTranslator pre-processing**
   - File: `src/engine/rbmt_translator.py`
   - Trước segmentation: `text = TraditionalConverter().convert(text)`
   - Trước segmentation: `text = PinyinScanner().replace_pinyin(text)`

4. [ ] **Build pinyin index từ DB**
   - Index: `pinyin → [source1, source2, ...]` (nhiều chữ cùng pinyin)
   - Disambiguation: chọn entry có priority cao nhất

5. [ ] **Build traditional index từ DB**
   - Index: `traditional_char → simplified_char`
   - Char-level mapping cho các ký tự không có trong DB

6. [ ] **Test với input phồn thể + pinyin lẫn**
   - Input: `這張美麗的臉` → `这张美丽的脸` → dịch
   - Input: `Anh ấy nói nǐ hǎo` → `Anh ấy nói 你好` → dịch

## Files to Create/Modify
- `src/tools/traditional_converter.py` — [NEW]
- `src/tools/pinyin_scanner.py` — [NEW]
- `src/engine/rbmt_translator.py` — Pre-processing integration

## Test Criteria
- [ ] `TraditionalConverter().convert("這張美麗的臉")` == `"这张美丽的脸"`
- [ ] `PinyinScanner().scan("nǐ hǎo")` trả về `[(0, 7, "nǐ hǎo", "你好")]`
- [ ] Regression tests vẫn pass

---
Next Phase: [phase-08-source-rewrite.md](phase-08-source-rewrite.md)
