# 📖 Hướng Dẫn Chạy Pipeline Dịch Thuật Qua UI

> Tài liệu này mô tả chi tiết từng bước sử dụng giao diện **DrDuc Translator Desktop** để thực hiện toàn bộ quy trình dịch thuật, từ tạo project đến kiểm tra chất lượng (QA).

---

## 🚀 Bước 0: Khởi Động Ứng Dụng

### Cách A — Chạy qua HTTP Bridge (Browser, khuyên dùng khi dev)
```powershell
cd "d:\Converter by DrDuc\desktop"
npm run dev:bridge
```
- Mở trình duyệt tại: **http://localhost:5173**
- Thanh sidebar sẽ hiện badge **HTTP TRANSPORT** và thông báo:
  *"HTTP bridge connected. The Python backend is executing your workflow requests."*

### Cách B — Chạy Native Tauri App (Production)
```powershell
cd "d:\Converter by DrDuc\desktop"
npm run tauri:dev
```
- Ứng dụng native mở trực tiếp, sidebar hiện badge **TAURI TRANSPORT**.

> ⚠️ Nếu gặp lỗi **Port 5173 already in use**: chạy `Stop-Process -Name node -Force` rồi thử lại.

---

## 📋 Bước 1: Tạo / Mở Project — Màn hình `Project Manager`

Đây là màn hình mặc định khi mở app.

### 1a. Tạo project mới
| Trường | Giá trị mẫu | Ý nghĩa |
|--------|-------------|----------|
| **Project Id** | `hong-hoang-lich` | Tên định danh duy nhất cho project |
| **Workspace Project Root** | `workspace_projects` | Thư mục gốc chứa tất cả project (tương đối với `d:\Converter by DrDuc`) |

→ Bấm nút **Create Project**.

### 1b. Mở project đã có
- Danh sách project hiện ở panel **Existing Projects** phía dưới.
- Click vào tên project để mở. UI sẽ tự động load **overview, chapters, dictionary, QA report**.

**Kết quả mong đợi:** Panel Project Control hiện đầy đủ thông tin:
- Project ID, Directory, Languages (`zh -> vi`), Active Chapter.

---

## 📥 Bước 2: Import Tài Liệu Nguồn — Màn hình `Pre-Translation Review`

Click **Pre-Translation Review** trên sidebar.

### Import file / folder
| Trường | Giá trị mẫu |
|--------|-------------|
| **Source File Or Source Directory** | `D:\Novel\source\chapter-001.md` hoặc thư mục `D:\Novel\source` |

- Bấm **Choose File** / **Choose Folder** (chỉ hoạt động trong Tauri native).
- Hoặc gõ đường dẫn trực tiếp vào ô input.
- Bấm **Import and Prepare**.

**Kết quả mong đợi:**
- Panel **Terminology Suggestions** hiện danh sách thuật ngữ cần review trước khi dịch.
- Panel **Config Snapshot** hiện JSON cấu hình dịch (locked entities, style, v.v.).
- Quay lại **Project Manager** → Danh sách **Chapters** đã được load đầy đủ.

---

## 📑 Bước 3: Chọn Chapter — Màn hình `Project Manager`

Quay về **Project Manager** (sidebar).

- Panel **Chapters** liệt kê tất cả chapter đã import.
- Click vào chapter muốn dịch (ví dụ: `chapter-001`).
- Chapter được chọn sẽ highlight xanh và trở thành **Active Chapter**.

**Kết quả mong đợi:**
- Ô **Active chapter** trong info panel cập nhật thành chapter vừa chọn.
- Nội dung source text tự động load vào **Translation Workspace**.

---

## ✍️ Bước 4: Dịch Chapter — Màn hình `Translation Workspace`

Click **Translation Workspace** trên sidebar.

### Thao tác
1. Kiểm tra ô **Source Text** — nội dung gốc (tiếng Trung) đã được tự động điền từ Active Chapter.
2. Bấm nút **Translate Active Slice**.
3. Đợi processing (thanh status bar ở dưới cùng sẽ cập nhật tiến trình).

**Kết quả mong đợi:**
- Panel **Clean Output**: Bản dịch sạch, không annotation — đây là bản reader-facing.
- Panel **Annotated Draft**: Bản dịch có đánh dấu các chỗ mơ hồ/chưa giải quyết.
- Panel **Trace Evidence**: Từng segment hiện chi tiết:
  - `sentence_id`, `source_text`
  - Fallback level (runtime, dictionary, fuzzy, v.v.)
  - Các candidate đã xem xét → candidate được chọn.

---

## 🔍 Bước 5: Kiểm Tra Chất Lượng (QA) — Màn hình `QA Report Viewer`

### Cách 1: Từ Translation Workspace
- Bấm nút **Run QA** (nằm cạnh nút Translate).
- UI tự chuyển sang **QA Report Viewer**.

### Cách 2: Từ sidebar
- Click **QA Report Viewer** trên sidebar.

**Kết quả mong đợi:**
- Bảng **QA Issues** hiện danh sách lỗi với các cột:
  - **Severity** (error / warning / info)
  - **Checker** (tên bộ kiểm tra đã phát hiện lỗi)
  - **Segment** (câu bị ảnh hưởng)
  - **Message** (mô tả lỗi cụ thể)
- Thống kê tổng: số issues / số segments.

---

## 📚 Bước 6: Tra Từ Điển — Màn hình `Dictionary Manager`

Click **Dictionary Manager** trên sidebar.

- Gõ từ Hán ngữ vào ô **Dictionary Query** (ví dụ: `林动` hoặc `一`).
- Bấm **Search Dictionary**.

**Kết quả mong đợi:**
- Danh sách entry hiện ra gồm: source, target_vi, pinyin, Hán Việt readings, priority, hit count, explanations.
- Panel **Candidate Review** ở dưới hiện danh sách ambiguity entries đang chờ duyệt.
  - Bấm **Verify** để chấp nhận candidate → cập nhật từ điển runtime.
  - Bấm **Reject** để loại bỏ.

---

## 🎓 Bước 7: Huấn Luyện Bản Dịch — Màn hình `Translation Coach`

Click **Translation Coach** trên sidebar. Đây là tính năng **human-in-the-loop** mạnh nhất.

### Điền feedback
| Trường | Ý nghĩa | Ví dụ |
|--------|---------|-------|
| **Scope** | Chapter hoặc Project | `Chapter` |
| **Hint** | Loại quy tắc gợi ý | `Auto` (để hệ thống tự phân loại) |
| **Feedback** | Nhận xét bằng ngôn ngữ tự nhiên | *"Hội thoại chương này cần tự nhiên hơn, xưng hô bớt cứng"* |
| **Source Snippet** | Đoạn gốc liên quan | *(tự động điền từ Active Chapter)* |
| **Current Translation** | Bản dịch hiện tại | *(tự động điền từ kết quả dịch)* |
| **Preferred Translation** | Bản dịch mong muốn | *(gõ tay bản sửa)* |

### LLM Assist (Tùy chọn)
Nếu muốn AI phân tích feedback sâu hơn, điền cấu hình LLM:
- **Endpoint**: URL API (ví dụ: `https://api.openai.com/v1/chat/completions`)
- **Model**: `gpt-4.1-mini`
- **API Key**: Token xác thực (lưu cục bộ trên máy)

→ Bấm **Analyze and Propose**.

**Kết quả mong đợi:**
- Panel **Analysis Suggestions**: Danh sách gợi ý quy tắc mới (rule type, confidence %, payload).
- Panel **Learning Snapshot**: Báo cáo learning (QA total, word similarity, runtime metrics).
- Panel **Candidate Rules**: Danh sách rules được tạo ra.
  - Bấm **Verify and Apply** → rule được áp dụng vào config project.
  - Bấm **Reject** → rule bị loại.

---

## 🔗 Bước 8: Xem Thực Thể — Màn hình `Entity & Relationship Viewer`

Click **Entity & Relationship Viewer** trên sidebar.

- Panel **Entities**: Danh sách tên nhân vật, thuật ngữ đã khóa (source → target, entity type).
- Panel **Relationships**: Đồ thị quan hệ (source → relation → target).

---

## ⚙️ Bước 9: Kiểm Tra Cấu Hình — Màn hình `Settings`

Click **Settings** trên sidebar.

- **Protocol version**: Phiên bản giao thức hiện tại (ví dụ: `2026-04-16.phase10`).
- **Transport mode**: `http` / `tauri` / `demo` / `browser`.
- **Supported commands**: Danh sách 18 lệnh backend hỗ trợ.

---

## 🔄 Quy Trình Tổng Hợp (Workflow Chính)

```
┌─────────────────┐
│ 1. Project Mgr  │ ── Tạo / Mở project
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Pre-Trans    │ ── Import source files
│    Review       │    Kiểm tra terminology
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Project Mgr  │ ── Chọn Active Chapter
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. Translation  │ ── Dịch → Clean + Draft + Trace
│    Workspace    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. QA Report    │ ── Kiểm tra chất lượng
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. Dictionary   │ ── Tra từ + Duyệt candidate
│    Manager      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 7. Translation  │ ── Feedback → Candidate Rules
│    Coach        │    → Verify/Reject → Re-translate
└────────┬────────┘
         ▼
    🔁 Lặp lại từ Bước 4 nếu cần
```

---

## ❓ Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| Port 5173 bị chiếm | `Stop-Process -Name node -Force` rồi chạy lại |
| Port 9721 bị chiếm | `Stop-Process -Name python -Force` rồi chạy lại |
| Nút bấm bị disable (xám) | Kiểm tra sidebar badge: phải là `HTTP TRANSPORT` hoặc `TAURI TRANSPORT`, không phải `BROWSER TRANSPORT` |
| Import không nhận file | Gõ đường dẫn tuyệt đối (ví dụ: `D:\Novel\source\ch01.md`) vào ô input |
| Translate trả về rỗng | Kiểm tra Active Chapter đã được chọn chưa (Project Manager → click chapter) |
