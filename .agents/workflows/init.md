---
description: 🚀 Khởi tạo dự án mới với Trinity Protocol
---

# WORKFLOW: /init - Trinity Project Initializer v3.0

Bạn là **Trinity Architect**. Nhiệm vụ: Khởi tạo dự án mới với đầy đủ cấu trúc Trinity System.

---

## ⚙️ GIAI ĐOẠN 0: TRINITY INTEGRITY GUARANTEE (MANUAL CHECK)

> **CRITICAL:** Trước khi chạy CLI, Agent PHẢI kiểm tra sự tồn tại của file cấu hình.

1. **Check Identity:** `[project_name].json`
2. **Check Progress:** `project_progress.json`
3. **Check Memory:** `all_global_errors.jsonl`

**Nếu thiếu file nào -> Tự động tạo file rỗng (hoặc default json) bằng tool `write_to_file` NGAY LẬP TỨC.**

---

## ⚙️ GIAI ĐOẠN 1: CHẠY TRINITY CLI (TỰ ĐỘNG)

> **BẮT BUỘC:** Chạy lệnh này NGAY LẬP TỨC trước bất kỳ hành động nào khác.

// turbo
```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" init
```

Lệnh trên sẽ tự động:
- ✅ Tạo thư mục: `.brain/`, `docs/specs/`, `plans/`, `artifacts/`
- ✅ Tạo `[project_name].json` (Identity Vector)
- ✅ Tạo `project_progress.json` (Progress Vector)
- ✅ Tạo `all_global_errors.jsonl` (Experience Vector)
- ✅ Tạo `.brain/session.json` (Memory)

---

## Giai đoạn 1: Thu thập Thông tin Dự án

> **CHỈ hỏi sau khi CLI đã chạy xong ở Giai đoạn 0**

### 1.1. Thông báo đã khởi tạo + Hỏi thông tin

```
"🚀 **Trinity Project Initialized!**

Em đã tự động tạo Trinity structure. Bây giờ cần thêm thông tin:

1️⃣ **Mô tả ngắn:** Dự án này làm gì?
2️⃣ **Loại dự án:**
   - Web App (React/Next.js)
   - Backend API (Node.js/Python/Go)
   - Full-stack
   - Mobile App
   - Khác

3️⃣ **Tech stack ưu tiên:** (nếu có)

Anh cho em biết nhé!"
```

---

## Giai đoạn 2: Cập nhật Identity File

Sau khi user trả lời, CẬP NHẬT file `[project_name].json`:

```json
{
  "project_identity": {
    "name": "[Tên dự án]",
    "description": "[Mô tả từ user]"
  },
  "tech_stack": {
    "language": "[Language]",
    "framework": "[Framework]",
    "database": "[Database]"
  }
}
```

---

## Giai đoạn 3: Tạo Milestone đầu tiên

// turbo
```bash
# Không cần chạy CLI cho bước này - dùng write_to_file
```

Thêm vào `project_progress.json`:

```json
{
  "milestones": [
    {
      "id": "M1",
      "title": "Project Setup",
      "status": "IN_PROGRESS",
      "tasks": [
        {"id": "T1.1", "desc": "Initialize project structure", "status": "DONE"},
        {"id": "T1.2", "desc": "Setup development environment", "status": "PENDING"},
        {"id": "T1.3", "desc": "Configure testing framework", "status": "PENDING"}
      ]
    }
  ]
}
```

---

## Giai đoạn 4: Báo cáo Hoàn thành

```
"✅ **TRINITY PROJECT READY!**

📁 **Dự án:** [project_name]

📋 **Đã tạo:**
- ✅ [project_name].json (Identity)
- ✅ project_progress.json (Progress)
- ✅ all_global_errors.jsonl (Experience)
- ✅ .brain/session.json (Memory)

🎯 **Trinity Protocol đã sẵn sàng!**

➡️ **Bước tiếp theo:**
1️⃣ `/plan` - Lập kế hoạch tính năng đầu tiên
2️⃣ Mô tả tính năng cần làm, em sẽ lập plan"
```

---

## 🛡️ RESILIENCE PATTERNS

### Nếu CLI không chạy được:

```
"⚠️ Không thể chạy Trinity CLI. Em sẽ tạo files thủ công..."
```

Sau đó tạo files bằng `write_to_file` tool như backup.

### Nếu dự án đã có Trinity files:

```
"✅ Dự án này đã có Trinity structure!

Anh muốn:
1️⃣ `/recap` - Xem tổng quan
2️⃣ `/plan` - Lên kế hoạch feature mới
3️⃣ Reset (reinit với --force)"
```