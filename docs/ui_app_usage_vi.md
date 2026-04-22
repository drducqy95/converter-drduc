# Quy trình sử dụng ứng dụng qua UI

Tài liệu này mô tả quy trình thao tác bằng giao diện cho bản `desktop` hiện tại của DrDuc Translator.

## 1. Điều kiện sử dụng

- Dùng bản native Windows:
  `desktop/src-tauri/target/release/drduc-translator-desktop.exe`
- Không dùng browser preview để xử lý dữ liệu thật.
- Chuẩn bị sẵn đường dẫn tới file nguồn cần import:
  `.txt`, `.md`, `.html`, `.docx`, `.pdf`
- Hiện tại chưa cần installer. Chạy trực tiếp file `.exe`.

## 2. Tổng quan giao diện

App có 2 khu vực chính:

- Sidebar bên trái:
  - danh sách màn hình
  - danh sách project
  - trạng thái `transport`
- Khu vực làm việc bên phải:
  - tên project đang mở
  - trạng thái command
  - `metrics`
  - màn hình nghiệp vụ
  - `Command Timeline`
  - `Runtime Snapshot`

7 màn hình chính:

1. `Project Manager`
2. `Dictionary Manager`
3. `Translation Workspace`
4. `Entity & Relationship Viewer`
5. `Pre-Translation Review`
6. `QA Report Viewer`
7. `Settings`

## 3. Quy trình thao tác chuẩn

### Bước 1. Mở app và kiểm tra runtime

Khi mở app:

- Ở thẻ `TAURI TRANSPORT`, phải thấy thông báo native runtime.
- Nếu không phải `tauri`, dừng lại và mở đúng file `.exe`.

### Bước 2. Tạo project

Vào màn `Project Manager`.

Nhập:

- `Project Id`: mã dự án, ví dụ `novel-001`
- `Workspace Base Dir`: thư mục chứa tất cả dự án, ví dụ `workspace_projects`

Nhấn:

- `Create Project`

Kết quả mong đợi:

- Project mới xuất hiện trong sidebar
- Khu `Project Control` hiển thị:
  - `Project`
  - `Directory`
  - `Languages`
  - `Active chapter`

## 4. Nạp dữ liệu nguồn

Sau khi tạo project, vào `Pre-Translation Review`.

Tại ô:

- `Source Path`

Nhập đường dẫn file nguồn thật, ví dụ:

```text
D:\Converter by DrDuc\Name project\ChinaWebNovel\Phan_Nhan_Tu_Tien.md
```

Nhấn:

- `Import and Prepare`

Kết quả mong đợi:

- App import file vào project
- Tự động tạo artifact trong:
  - `source/raw/`
  - `source/chapters/`
  - `working/entities/`
  - `working/relationships/`
  - `working/config/`
- Màn hình hiển thị:
  - `locked entities`
  - `Terminology Suggestions`
  - `Config Snapshot`

## 5. Kiểm tra chapter và chọn chapter đang làm việc

Quay lại `Project Manager`.

Tại khu `Chapters`:

- Nhấn vào 1 chapter để đặt `active chapter`
- Khi click chapter, app đồng bộ chapter đang chọn vào backend
- Nội dung chapter được nạp sang workspace dịch

Kết quả mong đợi:

- `Active chapter` thay đổi
- `Translation Workspace` sẽ dịch đúng chapter đã chọn
- `QA` sẽ chạy trên đúng chapter đã chọn

## 6. Rà soát entities và relationships

Vào `Entity & Relationship Viewer`.

Tại đây kiểm tra:

- `Entities`: tên riêng, khóa thuật ngữ, lock term
- `Relationships`: quan hệ sinh ra từ phân tích pre-translation

Mục đích:

- xác nhận term quan trọng đã được nhận diện
- nhìn nhanh graph quan hệ trước khi dịch

## 7. Dịch chapter

Vào `Translation Workspace`.

Kiểm tra:

- ô `Source Text` đã có nội dung chapter
- nếu cần có thể sửa tạm text đầu vào trong ô này

Nhấn:

- `Translate Active Slice`

Kết quả mong đợi:

- `Clean Output`: bản dịch sạch để đọc
- `Annotated Draft`: bản dịch có đánh dấu ambiguity/unresolved
- `Trace Evidence`: bằng chứng chọn nghĩa, fallback level, lý do

Cần quan sát kỹ:

- term nào bị `ambiguous`
- term nào bị `unresolved`
- segment nào fallback về `tm`, `number`, `project_entity`, `runtime`

## 8. Tra từ điển khi gặp cụm từ khó

Vào `Dictionary Manager`.

Tại khu `Dictionary Explorer`:

- nhập từ/cụm từ vào ô `Dictionary Query`
- nhấn `Search Dictionary`

App sẽ hiển thị:

- `source`
- `target_vi`
- `alternative_meanings`
- `full_explanation`
- `source_dict`
- `priority`
- `status`
- `hit_count`
- `pinyin`
- `han_viet_readings`

Đây là màn hình dùng để:

- đối chiếu từ điển gốc
- xem nghĩa phụ
- kiểm tra vì sao app chọn một nghĩa nào đó

## 9. Duyệt candidate sau khi dịch

Vẫn trong `Dictionary Manager`, xuống khu `Candidate Review`.

Nếu bản dịch có ambiguity hoặc unresolved:

- app sẽ đẩy candidate vào đây

Bạn có thể:

- lọc theo `Status`
- tìm theo `Search`
- nhấn `Verify`
- nhấn `Reject`

Ý nghĩa:

- `Verify`: xác nhận candidate hợp lệ
- `Reject`: đánh dấu candidate cần viết lại / không dùng

Sau khi duyệt:

- app cập nhật project state
- các candidate đã duyệt có thể được dùng để tham khảo cho các lần dịch sau

## 10. Chạy QA

Vào `Translation Workspace` hoặc `QA Report Viewer`.

Cách 1:

- từ `Translation Workspace`, nhấn `Run QA`

Cách 2:

- vào `QA Report Viewer`, nhấn `Refresh QA`

Kết quả mong đợi:

- hiển thị tổng số `Issues`
- danh sách lỗi theo từng checker

Mỗi issue hiển thị:

- `checker`
- `severity`
- `message`
- `segment_id`

Cần đọc kỹ các nhóm lỗi:

- `untranslated`
- `structure`
- `terminology`
- `pronoun`
- `emotion_consistency`
- `length`

## 11. Đọc timeline và artifact sau mỗi bước

Ở cuối màn hình có 2 khu cần theo dõi thường xuyên:

### `Command Timeline`

Dùng để xem:

- command nào vừa chạy
- đang ở stage nào
- có lỗi hay không
- message backend trả về

### `Runtime Snapshot`

Dùng để xem nhanh đường dẫn artifact:

- `Output`
- `Draft`
- `Trace`
- `QA`

Đây là nơi để mở file kết quả sau khi app đã xử lý.

## 12. Chu kỳ sử dụng đề xuất

Quy trình thực tế nên đi theo thứ tự sau:

1. Mở app
2. `Project Manager` -> tạo project
3. `Pre-Translation Review` -> import file
4. `Project Manager` -> chọn chapter
5. `Entity & Relationship Viewer` -> xem entities/relationships
6. `Translation Workspace` -> dịch
7. `Dictionary Manager` -> tra từ và duyệt candidate
8. `QA Report Viewer` -> chạy QA
9. Quay lại `Translation Workspace` nếu cần dịch lại sau khi sửa

## 13. Cách dùng cho trường hợp nhiều chapter

Nếu project có nhiều chapter:

1. Vào `Project Manager`
2. Trong khu `Chapters`, click chapter cần làm
3. Xác nhận `Active chapter` đã đổi
4. Vào `Translation Workspace` và nhấn `Translate Active Slice`
5. Chạy `Run QA`
6. Lặp lại cho chapter tiếp theo

Không nên dịch lung tung mà không chọn lại chapter, vì output/QA sẽ bám theo `active chapter`.

## 14. Đầu ra sau khi xử lý

Sau một vòng import -> dịch -> QA, project sẽ có ít nhất:

- `source/raw/`
- `source/chapters/`
- `working/entities/entities_suggested.json`
- `working/relationships/relationships_suggested.json`
- `working/config/translation_config.json`
- `drafts/`
- `output/`
- `reports/qa_report*.json`
- `reports/qa_report*.md`
- `state/project_state.json`
- `state/project_state.db`
- `state/tm.sqlite`

## 15. Lỗi thường gặp và cách xử lý

### App mở lên nhưng không thao tác được

- Kiểm tra đang mở đúng file `.exe` native
- Kiểm tra `transport` phải là `tauri`

### Import không chạy

- Kiểm tra `Source Path` có tồn tại thật
- Kiểm tra định dạng file có được hỗ trợ hay không

### Dịch không ra kết quả

- Kiểm tra đã chọn project chưa
- Kiểm tra đã import file chưa
- Kiểm tra `Active chapter` đã được chọn chưa

### QA không có dữ liệu

- Kiểm tra đã chạy dịch trước chưa
- Kiểm tra chapter đang active có đúng chapter vừa dịch không

### Dictionary search không ra kết quả

- Thử tìm một token ngắn hơn
- Thử tìm từng Hán tự / từ khóa chính

## 16. Khuyến nghị vận hành

- Luôn bắt đầu từ `Project Manager`
- Mỗi file nguồn nên tạo 1 project rõ ràng
- Sau khi import, nên kiểm tra `Terminology Suggestions` trước khi dịch
- Sau mỗi lần dịch, nên xem `Trace Evidence`
- Chỉ xem `Clean Output` là kết quả tạm; luôn đối chiếu thêm với `Annotated Draft` và `QA Report`

## 17. Mục đích từng màn hình

- `Project Manager`: tạo project, chọn chapter, quan sát tổng quan
- `Pre-Translation Review`: nạp file, tạo config, xem term gợi ý
- `Entity & Relationship Viewer`: xem tên riêng và quan hệ
- `Translation Workspace`: dịch và xem trace
- `Dictionary Manager`: tra cứu metadata và duyệt candidate
- `QA Report Viewer`: kiểm tra lỗi chất lượng
- `Settings`: xem protocol, transport, artifact path

## 18. Quy trình tối thiểu để chạy 1 file thật

Nếu cần chạy nhanh 1 file thật bằng UI:

1. Mở `.exe`
2. `Project Manager` -> `Create Project`
3. `Pre-Translation Review` -> nhập `Source Path` -> `Import and Prepare`
4. `Project Manager` -> click chapter đầu tiên
5. `Translation Workspace` -> `Translate Active Slice`
6. `QA Report Viewer` -> `Refresh QA`
7. `Runtime Snapshot` -> mở file output/qa nếu cần

---

Tài liệu này bám theo UI hiện tại của app desktop trong repo. Nếu label nút, tên màn hình hoặc flow thay đổi, cần cập nhật lại tài liệu này đồng bộ với `desktop/src/App.tsx`.
