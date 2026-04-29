---
description: Làm việc với NotebookLM (Nghiên cứu, thêm tài liệu, truy vấn) qua CLI
---

# Quy trình làm việc với NotebookLM qua CLI (Global)

Workflow này hướng dẫn Agent các lệnh CLI (`nlm`) để nghiên cứu, cung cấp ngữ cảnh dữ liệu và tương tác với dịch vụ NotebookLM của Google.

### 1. Kiểm tra trạng thái đăng nhập
```bash
// turbo
nlm login --check
```
*Ghi chú: Nếu hệ thống báo mất kết nối, tài khoản sai lệch hoặc cookies hết hạn, người dùng hoặc Agent cần báo để chạy `nlm login` hoặc `nlm login switch <profile>`.*

### 2. Quản lý Notebook
Quản lý Workspace phân tích trên NotebookLM.

- **Liệt kê Notebook:**  
  `nlm notebook list`

- **Tạo Notebook mới:**  
  `nlm notebook create "Tên Project/Nghiên cứu"`

- **Tạo Alias (Xác định ID cho dự án hiện tại):**  
  ```bash
  nlm alias set current_nblm <notebook-id>
  ```
  *(Dùng biến alias như current_nblm thay cho UUID quá phức tạp)*

### 3. Thu thập dữ liệu (Thêm Sources)
Đẩy tài liệu vào NotebookLM để chuẩn bị phân tích hoặc làm base knowledge:

- **Thêm URL web bài viết / YouTube:**  
  `nlm source add current_nblm --url "https://ví dụ.com/bài-viết"`

- **Thêm văn bản tự do (Text / Markdown content):**  
  `nlm source add current_nblm --text "Nội dung phân tích..." --title "Tiêu đề tài liệu"`

- **Thêm Google Drive (Docs, Slides, Sheets, PDF):**  
  `nlm source add current_nblm --drive <google-drive-doc-id>`

### 4. Deep Research (Tính năng nghiên cứu)
Sử dụng NotebookLM để Agent cào nội dung xung quanh web và kéo về sổ tay:

- **Bắt đầu nghiên cứu (thường tốn 3-5 phút cho mode deep):**  
  `nlm research start "Câu hỏi nghiên cứu" --notebook-id current_nblm --mode deep`

- **Kiểm tra tiến độ nghiên cứu:**  
  `nlm research status current_nblm`

- **Tiến hành đưa nội dung về Notebook:**  
  `nlm research import current_nblm <task-id>`

### 5. Khai thác dữ liệu / Truy vấn (QA)
Sau khi có sources, sử dụng NotebookLM như một cỗ máy QA engine có trích dẫn tài liệu tham khảo:

- **Thực hiện truy vấn một lần (One-shot):**
  ```bash
  nlm notebook query current_nblm "Toàn bộ thông tin trọng tâm nằm ở những góc độ nào?"
  ```
  *(Lưu ý: KHÔNG chạy `nlm chat start` trong môi trường tự động Agent vì nó sẽ bị mắc kẹt tại REPL Shell)*

### 6. Tổng hợp Studio (Audio, Báo cáo)
Agent có thể tạo nội dung chuyên sâu từ NotebookLM như tạo Podcast 2 Host, Tài liệu hướng dẫn.

- **Tạo Podcast (Audio Overview) bằng tiếng Việt:**
  `nlm audio create current_nblm --language vi --confirm`
  
- **Tạo Study Guide (Tài liệu nghiên cứu):**
  `nlm report create current_nblm --format "Study Guide" --confirm`
  
- **Kiểm tra trạng thái tạo (Status):**
  `nlm studio status current_nblm`
  
- **Tải tệp nội dung đã hoàn thành:**
  `nlm download audio current_nblm --output podcast_final.mp3`
