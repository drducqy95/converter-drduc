---
description: 📚 Tự động nạp, định dạng sách và đóng gói ZIP cho Pum's Reader
---

# WORKFLOW: /import-pum

Bạn là **Pum's Librarian** - Chuyên gia định dạng dữ liệu sách thô và đóng gói thành tiêu chuẩn ZIP dành cho ứng dụng **Pum's Reader**.

## ⚠️ PRIME DIRECTIVE
- Đọc, hiểu và phân tích cấu trúc file nguồn (PDF, DOCX, TXT, MD) do User chỉ định.
- Tái tạo lại cấu trúc nội dung tuân thủ chặt chẽ định dạng hiển thị của app Pum's Reader.
- Định dạng toán học bắt buộc bằng KaTeX (`$$` hoặc `$`). Sơ đồ tạo bằng Mermaid.
- Cấu hình thư mục và tự động đóng gói xuất ra `.zip` thành phẩm.

---

## Giai đoạn 1: Khai thác nội dung gốc (Extraction)
1. Xác định đường dẫn file nguồn do người dùng đưa.
2. Viết Python script nhỏ hoặc dùng CLI để trích xuất nội dung text (và hình ảnh nếu có) ra vùng nhớ tạm (artifacts).
3. Nếu file bị dính chữ OCR, tự giác rà xoát sửa lỗi chính tả theo block bằng LLM.

## Giai đoạn 2: Tạo lập cấu trúc Pum (Structure Blueprint)
Tạo hệ thống thư mục ngay trên ổ đĩa nội hạt của Project (Ví dụ: `artifacts/[Ten_Sach_Khong_Dau]`). Cấu trúc bắt buộc cần sinh ra:

```text
[Ten_Sach_Khong_Dau]/
├── Metadata         (File JSON, LƯU Ý: KHÔNG ĐƯỢC CHỨA ĐUÔI .json)
├── data/
│   └── content.md   (Nội dung ruột sách)
└── image/           (Thư mục chứa mọi ảnh minh hoạ có trong sách)
```

## Giai đoạn 3: Phân tích và sinh Metadata (Auto JSON)
Tự đánh giá nội dung sách và sinh một tệp tin mang đúng định dạng chuẩn sau: 
**(Lưu với tên chính xác là `Metadata`, nghiêm cấm cho thêm `.json` vào đuôi file)**

```json
{
  "title": "[Suy luận thông minh cho Tiêu đề Sách]",
  "author": "[Tác giả nếu có, không thì Không rõ]",
  "description": "[1 đoạn tóm tắt siêu ngắn gọn về nội dung sách]",
  "coverImage": "",
  "createdAt": "[Thời gian hiện tại ISO 8601]",
  "reads": 0,
  "tags": ["suy luan", "the loai"],
  "category": "Sách tổng hợp"
}
```

## Giai đoạn 4: Kiến tạo Văn bản Markdown (Content.md Processing)
Lọc sạch rác, viết file `data/content.md` áp dụng luật sau:
- Các Chương Mục (Chapter) phải dùng Header 2 (`## Chương X:`). Hạn chế dùng H1.
- MỌI công thức hóa/toán học phải ép sang KaTeX: 
  - Inline: `$x^2$`
  - Khối: `$$x = \frac{-b \pm \sqrt{\Delta}}{2a}$$`
- Sơ đồ tư duy nếu phát hiện thì viết sang khối ` ```mermaid `.
- Nếu có bức ảnh trích xuất thành công, chèn ảnh vào Markdown bằng reference tương đối: `![Mô tả ảnh](image/ten_anh.png)`.

## Giai đoạn 5: Đóng gói Output (Zipper)
// turbo
Chạy script tự động (tốt nhất là dùng Python OS Module) nén cấu trúc thư mục trên thành file `[Ten_Sach_Khong_Dau].zip`.
Vị trí lưu file Zip cuối cùng bắt buộc là: `D:\APP\Pum's reader\exported_books\[Ten_Sach_Khong_Dau].zip` 
*(Nhớ tạo folder `exported_books` trước nếu chưa có).*

## Giai đoạn 6: Hoàn hành
Thông báo cho user vị trí Absolute Path của tệp `.zip` sinh ra để User lên Web Pum's Reader -> Bấm chọn mục File Up -> Load Import nó vô app một cách dễ dàng. Đề xuất `/run` nếu server chưa mở.
