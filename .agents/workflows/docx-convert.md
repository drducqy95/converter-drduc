---
description: 🔄 Chuyển đổi file sang DOCX và ngược lại (MD/HTML/LaTeX/JSON ↔ DOCX) với bảo toàn công thức, bảng, hình ảnh
---

# WORKFLOW: /docx-convert — Trinity DOCX Converter v1.0

Bạn là **Chuyên gia Chuyển đổi Tài liệu cấp cao**. Khả năng nổi bật: chuyển đổi đa định dạng sang DOCX và ngược lại, bảo toàn công thức toán/hóa (native Word equations), bảng biểu phức tạp (merged cells), và hình ảnh chất lượng cao.

---

## ⚠️ PRIME DIRECTIVE

**Nhiệm vụ cốt lõi:** Chuyển đổi file giữa các định dạng (MD, HTML, LaTeX, JSON ↔ DOCX) với mức độ bảo toàn cao nhất. Công thức toán/hóa phải xuất hiện dưới dạng **Native Word Equation** (chỉnh sửa được), KHÔNG phải hình ảnh.

---

## Giai đoạn 0: Context Detection & Setup

### 0.1. Nhận diện Input

```
User: /docx-convert [file.md] --to docx
→ Chuyển Markdown → DOCX

User: /docx-convert [file.html] --to docx
→ Chuyển HTML → DOCX

User: /docx-convert [file.tex] --to docx
→ Chuyển LaTeX → DOCX

User: /docx-convert [file.docx] --to md
→ Chuyển DOCX → Markdown

User: /docx-convert [file.docx] --to html
→ Chuyển DOCX → HTML

User: /docx-convert [file.docx] --to latex
→ Chuyển DOCX → LaTeX

User: /docx-convert (không đủ tham số)
→ Hỏi: "Bạn muốn convert file nào? Sang định dạng nào?"
```

### 0.2. Load Skill

```
1. Đọc SKILL.md: global_skills/skills/docx-converter/SKILL.md
2. Kiểm tra Pandoc: pandoc --version (cần >= 3.0)
3. Kiểm tra Python deps: python -c "import pypandoc, docx, lxml"
4. Nếu thiếu → cài đặt tự động
```

### 0.3. Xác định Pipeline

| Source → Target | Engine chính | Lua Filter | Post-processing |
|----------------|-------------|------------|-----------------|
| MD → DOCX | Pandoc | mhchem.lua | Fix namespace |
| HTML → DOCX | Pandoc + BS4 | - | Fix tables |
| LaTeX → DOCX | Pandoc | mhchem.lua | - |
| JSON → DOCX | docxtpl | - | - |
| DOCX → MD | Pandoc | - | Clean up |
| DOCX → HTML | Pandoc/mammoth | - | - |
| DOCX → LaTeX | Pandoc | - | Fix encoding |

---

## Giai đoạn 1: Pre-processing

### 1.1. Kiểm tra nội dung nguồn

```
□ File tồn tại và đọc được?
□ Encoding UTF-8?
□ Có chứa công thức toán ($...$, $$...$$)?
□ Có chứa công thức hóa (\ce{...})?
□ Có chứa hình ảnh Base64?
□ Có chứa bảng biểu HTML với merged cells?
□ Kích thước file (cảnh báo nếu > 20MB)?
```

### 1.2. Xử lý trước khi convert

**Nếu có Base64 images:**
```
→ Trích xuất ra thư mục media/
→ Thay thế src Base64 bằng đường dẫn file
→ Tránh Pandoc crash (Exit 251)
```

**Nếu có HTML với merged cells:**
```
→ Parse HTML tables để ghi nhận cấu trúc merge
→ Lưu merge map cho post-processing
```

**Nếu có \ce{} blocks:**
```
→ Đảm bảo mhchem.lua filter được load
→ Path: global_skills/skills/docx-converter/filters/mhchem.lua
```

---

## Giai đoạn 2: Core Conversion

### 2.1. Convert SANG DOCX

```bash
# Markdown → DOCX
python global_skills/skills/docx-converter/scripts/convert_to_docx.py \
    [input.md] --to docx \
    --reference global_skills/skills/docx-converter/templates/reference.docx \
    --lua-filter global_skills/skills/docx-converter/filters/mhchem.lua \
    --dpi 600

# HTML → DOCX (với fix tables)
python global_skills/skills/docx-converter/scripts/convert_to_docx.py \
    [input.html] --to docx --fix-tables --dpi 600

# LaTeX → DOCX
python global_skills/skills/docx-converter/scripts/convert_to_docx.py \
    [input.tex] --to docx --dpi 600
```

**Hoặc dùng Pandoc trực tiếp (nếu script gặp vấn đề):**
```bash
pandoc [input.md] -o [output.docx] \
    --reference-doc=global_skills/skills/docx-converter/templates/reference.docx \
    --lua-filter=global_skills/skills/docx-converter/filters/mhchem.lua \
    --dpi=600
```

### 2.2. Convert TỪ DOCX

```bash
# DOCX → Markdown
python global_skills/skills/docx-converter/scripts/convert_from_docx.py \
    [input.docx] --to md

# DOCX → HTML
python global_skills/skills/docx-converter/scripts/convert_from_docx.py \
    [input.docx] --to html

# DOCX → LaTeX
python global_skills/skills/docx-converter/scripts/convert_from_docx.py \
    [input.docx] --to latex
```

---

## Giai đoạn 3: Post-processing

### 3.1. Fix OMML Namespace (nếu cần)

```bash
python global_skills/skills/docx-converter/scripts/fix_omml_namespace.py [output.docx] --backup
```

### 3.2. Kiểm tra output

```
□ File DOCX mở được trong Word?
□ Công thức hiển thị đúng (native equation, chỉnh sửa được)?
□ Bảng biểu đúng cấu trúc (merged cells đúng)?
□ Hình ảnh chất lượng cao (không vỡ)?
□ Font/style đúng template (Times New Roman 14pt)?
□ Heading hierarchy đúng (H1 > H2 > H3)?
```

### 3.3. Xử lý lỗi

| Lỗi | Chiến lược |
|-----|-----------|
| Pandoc crash (exit 251) | Chia file nhỏ, convert từng phần |
| Equation không hiển thị | Chạy fix_omml_namespace.py |
| Hình ảnh mờ | Tăng --dpi=600 hoặc 1200 |
| Bảng merge sai | Chạy --fix-tables post-processing |
| Lua filter lỗi | Bỏ filter, convert rồi fix thủ công |
| Font sai | Kiểm tra reference.docx template |

---

## Giai đoạn 4: Báo cáo & Delivery

### 4.1. Báo cáo kết quả

```
📋 BÁO CÁO CHUYỂN ĐỔI

📄 Source: [input_file] ([format])
📄 Target: [output_file] (DOCX)
📏 Size: [X] KB → [Y] KB

✅ Kết quả:
  - Paragraphs: [N]
  - Tables: [T] (merged cells fixed: [M])
  - Equations: [E] (native OMML)
  - Images: [I] (DPI: 600)

⚠️ Cảnh báo (nếu có):
  - [Danh sách elements có vấn đề]

📁 Output: [output_path]
```

### 4.2. Gợi ý Next Steps

```
➡️ Next steps:
1️⃣ Mở [output.docx] trong Word để kiểm tra
2️⃣ Cần phân tích DOCX? → /docx-read
3️⃣ Cần OCR hình ảnh? → /ocr
4️⃣ Lưu context? → /save-brain
```

---

## Giai đoạn 5: Update Trinity State

### 5.1. Cập nhật `project_progress.json`

```json
{
  "task": "DOCX Conversion",
  "source": "[input_path]",
  "target": "[output_path]",
  "direction": "MD→DOCX",
  "status": "DONE",
  "equations": E,
  "tables": T,
  "images": I
}
```

### 5.2. Ghi lỗi (nếu có)

```json
{
  "error_id": "ERR_CONV_XXX",
  "timestamp": "...",
  "context": "DOCX Conversion",
  "error_type": "...",
  "message": "...",
  "root_cause": "...",
  "fix_applied": "...",
  "status": "RESOLVED"
}
```

---

## 🛡️ RESILIENCE PATTERNS

### File lớn (> 20MB)
```
1. Cảnh báo thời gian xử lý
2. Trích xuất Base64 images trước
3. Chia thành sections nếu cần
4. Set --dpi=300 thay vì 600 để giảm dung lượng
```

### Round-trip testing
```
Để kiểm tra chất lượng conversion:
1. Convert: MD → DOCX
2. Convert ngược: DOCX → MD
3. So sánh 2 file MD → xem mất mát gì
```

### Template customization
```
User muốn font/style khác:
1. Sửa scripts/create_reference_docx.py
2. Chạy lại để tạo reference.docx mới
3. Hoặc: mở reference.docx trong Word, sửa styles, save
```
