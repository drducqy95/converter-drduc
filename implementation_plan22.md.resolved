# Cải thiện ngữ pháp tiếng Việt trong bản dịch RBMT

## Vấn đề

Phân tích so sánh source chương 1 và output cho thấy **6 loại lỗi hệ thống** chính:

### 1. 🔴 Thứ tự Tính từ - Danh từ chưa đảo (Critical)

Tiếng Trung: `Adj + Noun` → Tiếng Việt phải là: `Noun + Adj`

| Source | Output hiện tại (sai) | Đúng |
|---|---|---|
| 黑色风衣 | màu đen áo gió | áo gió màu đen |
| 白色寿衣 | màu trắng áo liệm | áo liệm màu trắng |
| 黑色高跟鞋 | màu đen giày cao gót | giày cao gót màu đen |
| 惨白腐烂的双手 | trắng ởn hư thối hai tay | hai bàn tay trắng ởn hư thối |

### 2. 🔴 False-positive tên riêng từ Terminology Suggestions (Critical)

Nhiều từ phổ thông bị nhận nhầm là tên riêng và dịch Hán Việt:

| Source | Sai | Đúng | Ghi chú |
|---|---|---|---|
| 连忙 | Liên Mang | vội vàng | Từ phổ thông, không phải tên |
| 相信 | Tướng Tín | tin tưởng | Từ phổ thông |
| 有发现 | Hữu Phát Hiện | có phát hiện | 有+V không phải tên |
| 有对/有办法/有死 | Hữu Đối/Hữu Bạn Pháp/Hữu Tử | có đối/có cách/có chết | 有+X patterns |
| 和他/和我/和你 | Hòa Tha/Hòa Ngã/Hòa Nhĩ | và hắn/và ta/và ngươi | 和+pronoun |
| 能性/能出 | Năng Tính/Năng Xuất | khả năng/có thể ra | 能+X patterns |
| 张陈面/张陈身/... | Trương Trần Diện/Thân/... | Trương Trần + verb | 张陈+verb goom nhầm |

### 3. 🟡 Lượng từ dịch literal (Medium)

| Source | Output (sai) | Đúng |
|---|---|---|
| 一座小山 | một tòa núi nhỏ | một ngọn núi nhỏ |
| 一根笔 | một cái một nguyên tiền trung tính bút | một cây bút |

### 4. 🟡 `我` dịch thành `bản tọa` trong ngữ cảnh nội tâm (Medium)

`我` trong suy nghĩ nội tâm → nên là "ta" hoặc "tôi", không phải "bản tọa" (= tại hạ, dùng khi nói với người khác).

### 5. 🟢 Hậu cấu trúc "的" bị bỏ mất ngữ nghĩa (Low)

`的` hiện tại bị map thành `""` (xóa), nhưng trong cấu trúc `N1 的 N2` cần giữ lại "của".

### 6. 🟢 Heading chưa dịch đúng (Low)

`# 第一篇 浸水的婴儿 第一章 自杀的男子` → thiếu regex cho `第X篇`.

---

## Proposed Changes

### Post-translation Grammar Rewriter

#### [NEW] [vi_grammar_rewriter.py](file:///d:/Converter%20by%20DrDuc/src/engine/vi_grammar_rewriter.py)

Module mới chứa các regex pattern đảo ngữ pháp Việt:
- **Adj-Noun reorder**: Đảo `màu X + Noun` → `Noun + màu X`
- **「的」handler**: Chèn "của" khi cần giữa N1 và N2
- **Measure word mapping**: `一座山` → "một ngọn núi" (tra bảng lượng từ)

---

#### [MODIFY] [rbmt_translator.py](file:///d:/Converter%20by%20DrDuc/src/engine/rbmt_translator.py)

- Import `vi_grammar_rewriter` và gọi nó trong [_normalize_output](file:///d:/Converter%20by%20DrDuc/src/engine/rbmt_translator.py#573-611) sau bước regex cleanup hiện có.

---

### Terminology Suggestion Cleanup

#### [MODIFY] [terminology_suggester.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/terminology_suggester.py)

- Thêm blacklist cho các từ phổ thông không được gợi ý: `连忙`, `相信`, `有X`, `和X`, `能X`.
- Lọc bỏ các suggestion có [source](file:///d:/Converter%20by%20DrDuc/scripts/run_batch_project_eval.py#165-171) bắt đầu bằng `有`/`和`/`能` + pronoun/verb.

---

### Entity Scanner Improvement

#### [MODIFY] [entity_scanner.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/entity_scanner.py)

- Mở rộng `INVALID_NAME_CHARS` thêm: `面`, `身`, `点`, `回`, `现`, `正`, `转`, `皱`, `背`, `松`, `接`, `摇`, `倒`, `便` (các động từ/danh từ thường đi sau tên)
- Thêm blacklist patterns: `有X`, `和X`, `能X`, `连X`, `相X` (ngăn [_fallback_name_mining](file:///d:/Converter%20by%20DrDuc/src/pipeline/entity_scanner.py#147-214) bắt)

---

## Verification Plan

### Automated Tests

```powershell
# Chạy test regression hiện có
cd "D:\Converter by DrDuc"
python -m pytest tests/test_translation_regressions.py -v

# Chạy dịch lại chapter-001 và kiểm tra output
python run_full_pipeline.py --chapter chapter-001 --skip-pretranslation
```

### Manual Verification

Sau khi chạy lại pipeline:
1. Mở [output/chapter-001.txt](file:///d:/Converter%20by%20DrDuc/workspace_projects/New%20folder/output/chapter-001.txt)
2. Kiểm tra:
   - Dòng 3: `áo gió màu đen` (không còn `màu đen áo gió`)
   - Dòng 63: `vội vàng` (không còn `Liên Mang`)
   - Dòng 123: `tin tưởng` (không còn `Tướng Tín`)
   - Các dòng chứa `Hữu X` phải biến mất
