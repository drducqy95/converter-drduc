---
description: Làm việc với NotebookLM (Nghiên cứu, thêm tài liệu, truy vấn) qua CLI
---

# Quy trình làm việc với NotebookLM qua CLI

Workflow này hướng dẫn Agent các lệnh CLI (`nlm`) để nghiên cứu, thêm dữ liệu và tương tác với NotebookLM.

### 1. Kiểm tra trạng thái đăng nhập
```bash
// turbo
nlm login --check
```
*Ghi chú: Nếu hệ thống báo mất kết nối hoặc cookies hết hạn, người dùng cần chạy `nlm login` trong terminal cá nhân để đăng nhập lại thông qua trình duyệt.*

### 2. Quản lý Notebook
Bạn có thể liệt kê, tạo mới và thiết lập alias để không phải gõ ID dài dòng:

- **Liệt kê Notebook:**  
  `nlm notebook list`

- **Tạo Notebook mới:**  
  `nlm notebook create "Tên Project/Nghiên cứu"`

- **Tạo Alias (Khuyên dùng):**  
  ```bash
  nlm alias set nblm <notebook-id>
  ```
  *(Từ giờ về sau, có thể dùng chữ `nblm` thay cho `<notebook-id>`)*

### 3. Thu thập dữ liệu (Thêm Sources)
Đẩy tài liệu, trang web vào Notebook để phân tích:

- **Thêm từ URL / Website / YouTube:**  
  `nlm source add nblm --url "https://ví dụ.com/bài-viết"`

- **Thêm đoạn văn bản (Text):**  
  `nlm source add nblm --text "Nội dung văn bản dài..." --title "Tiêu đề tài liệu"`

- **Thêm Google Drive (Docs, Slides, Sheets, PDF):**  
  `nlm source add nblm --drive <google-drive-doc-id>`

### 4. Tính năng Deep Research (Tìm kiếm & tự động tổng hợp Web)
Sử dụng NotebookLM để tự động lên mạng cào dữ liệu và tổng hợp thành các sources hữu ích:

- **Kích hoạt Deep Research (Mất 3-5 phút):**  
  `nlm research start "Câu truy vấn nghiên cứu chi tiết" --notebook-id nblm --mode deep`

- **Kiểm tra tiến độ:**  
  `nlm research status nblm`
  *(Nên chờ tới lúc hoàn thành rồi mới import)*

- **Đưa nội dung kiếm được vào Notebook:**  
  `nlm research import nblm <task-id>`

### 5. Truy vấn / Hỏi đáp (QA)
Sau khi có dữ liệu, hãy đặt câu hỏi để AI phân tích và trả về thông tin kèm theo trích dẫn.

- **Thực hiện câu hỏi One-shot:**
  ```bash
  nlm notebook query nblm "Hãy tóm tắt phương pháp chính được nhắc đến trong các tài liệu?"
  ```
  *(Tuyệt đối KHÔNG chạy lệnh `nlm chat start` vì nó sẽ mở màn hình trả lời REPL không tự động hóa được)*

### 6. Sinh nội dung Studio
Bạn có thể ra lệnh cho NotebookLM xuất file Audio (Podcast), Báo cáo (Report), v.v.

- **Tạo Podcast Tổng hợp Âm thanh (Audio Overview):**
  `nlm audio create nblm --language vi --confirm`
  
- **Tạo Study Guide (Tài liệu báo cáo):**
  `nlm report create nblm --format "Study Guide" --confirm`
  
- **Kiểm tra trạng thái tạo nội dung:**
  `nlm studio status nblm`
  
- **Tải tệp nội dung:**
  `nlm download audio nblm --output podcast.mp3`
