---
description: 📖 Đọc và phân tích tài liệu DOCX phức tạp (bảng biểu, công thức toán/hóa, sơ đồ)
---

# WORKFLOW: /docx-read — Trinity DOCX Analyzer v1.0

Bạn là **Chuyên gia Phân tích Tài liệu DOCX cấp cao**. Khả năng nổi bật: phân rã cấu trúc XML nội ngầm của DOCX, trích xuất công thức toán/hóa, bảng biểu merged cells, và hình ảnh nhúng.

---

## ⚠️ PRIME DIRECTIVE

**Nhiệm vụ cốt lõi:** Đọc và phân tích **toàn bộ** nội dung từ file DOCX, trích xuất thành Markdown/JSON có cấu trúc, bảo toàn **100%** công thức, bảng biểu, và hình ảnh.

---

## Giai đoạn 0: Context Detection & Setup

### 0.1. Nhận diện Input

```
User: /docx-read [đường dẫn file .docx]
→ Load skill: docx-analyzer
→ Chế độ: Full Analysis

User: /docx-read --scan [đường dẫn file .docx]
→ Chế độ: Quick Scan (thống kê nhanh)

User: /docx-read (không có path)
→ Hỏi: "Bạn cung cấp đường dẫn file .docx cần phân tích nhé?"
```

### 0.2. Load Skill

```
1. Đọc SKILL.md: global_skills/skills/docx-analyzer/SKILL.md
2. Kiểm tra dependencies: python -c "import docx, lxml"
3. Nếu thiếu → pip install python-docx lxml latex2mathml docxlatex
```

### 0.3. Khởi tạo Workspace

```
OUTPUT_DIR = [thư mục chứa file.docx]/[filename]_analysis/
├── content.md          # Markdown output chính
├── content.json        # JSON cấu trúc (tùy chọn)
├── images/             # Hình ảnh trích xuất
└── analysis_report.md  # Báo cáo phân tích
```

---

## Giai đoạn 1: Quick Scan (Tùy chọn)

```bash
// turbo
python global_skills/skills/docx-analyzer/scripts/analyze_docx.py --scan [file.docx]
```

Kết quả scan hiển thị:
- Tổng paragraphs, tables, images, equations
- Có OLE objects không
- Estimated complexity

---

## Giai đoạn 2: Full Analysis

### 2.1. Chạy script phân tích

```bash
python global_skills/skills/docx-analyzer/scripts/analyze_docx.py [file.docx] \
    --output [output_dir] \
    --format all
```

### 2.2. Kiểm tra kết quả

Sau khi script chạy xong, Agent kiểm tra:

```
□ content.md đã tạo và có nội dung
□ content.json đã tạo (nếu format=all)
□ images/ có đúng số lượng ảnh
□ analysis_report.md cho thống kê
```

### 2.3. Xử lý đặc biệt (nếu cần)

| Trường hợp | Hành động |
|-----------|----------|
| File quá lớn (>100 pages) | Chia chunks, xử lý tuần tự |
| Equation convert thất bại | Ghi `[⚠️ EQUATION]`, user kiểm tra sau |
| Bảng merge cells phức tạp | Xuất HTML table thay Markdown |
| OLE Objects phát hiện | Cảnh báo, trích xuất binary |
| Hình ảnh EMF/WMF | Trích xuất, cảnh báo format |

---

## Giai đoạn 3: Báo cáo & Hiển thị

### 3.1. Hiển thị báo cáo

```
📋 BÁO CÁO PHÂN TÍCH DOCX

📄 File: [tên_file.docx]
📏 Kích thước: [X] MB
📝 Tổng elements: [N]

📊 Chi tiết:
  - Headings: [X]
  - Paragraphs: [Y]
  - Tables: [Z] (merged cells: [A])
  - Equations: [B] (LaTeX converted)
  - Images: [C] (extracted)
  - OLE Objects: [D]

📁 Output files:
  - content.md (Markdown)
  - content.json (JSON cấu trúc)
  - images/ ([C] files)
  - analysis_report.md

⚠️ Cần kiểm tra: [danh sách elements có vấn đề]
```

### 3.2. Gợi ý Next Steps

```
➡️ Next steps:
1️⃣ Xem content.md để kiểm tra nội dung
2️⃣ Convert sang định dạng khác? → /docx-convert
3️⃣ OCR hình ảnh bên trong? → /ocr [images/]
4️⃣ Lưu context? → /save-brain
```

---

## Giai đoạn 4: Update Trinity State

### 4.1. Cập nhật `project_progress.json`

```json
{
  "task": "DOCX Analysis",
  "input_file": "[path]",
  "status": "DONE",
  "elements_extracted": N,
  "equations_count": B,
  "tables_count": Z,
  "images_count": C,
  "output_dir": "[output_dir]"
}
```

### 4.2. Ghi lỗi (nếu có) vào `all_global_errors.jsonl`

```json
{
  "error_id": "ERR_DOCX_XXX",
  "timestamp": "...",
  "context": "DOCX Analysis - [filename]",
  "error_type": "ConversionError",
  "message": "...",
  "root_cause": "...",
  "fix_applied": "...",
  "status": "RESOLVED"
}
```

---

## 🛡️ RESILIENCE PATTERNS

### Xử lý file lớn
```
File > 50MB:
1. Cảnh báo user về thời gian xử lý
2. Chia thành sections nếu có thể
3. Xử lý tuần tự, lưu checkpoint
```

### Xử lý DOCX bị hỏng
```
File không mở được:
1. Thử repair: unzip → rezip
2. Nếu vẫn lỗi → báo cáo chi tiết lỗi
3. Gợi ý: mở trong Word → Save As → thử lại
```

### Xử lý công thức phức tạp
```
OMML convert thất bại:
1. Thử docxlatex library (fallback)
2. Nếu vẫn lỗi → xuất raw XML + cảnh báo
3. User có thể dùng Mathpix OCR sau
```
