# Phân Tích Các Bộ Từ Điển Bổ Sung Trong Quick Translator 2020

Ngày cập nhật: 2026-04-15  
Phạm vi khảo sát: `D:\APP\Quick Translator 2020\Data`

## 1. Mục tiêu

Tài liệu này phân tích các nguồn dữ liệu trong thư mục Quick Translator chưa được dùng trực tiếp hoặc chưa được migrate đúng vai trò trong hệ thống hiện tại, nhằm đánh giá:

- khả năng nạp vào database dictionary;
- giá trị thực tế đối với project DrDuc Translator;
- mức ưu tiên triển khai parser riêng;
- vai trò phù hợp: core dictionary, reference dictionary, normalization resource, audit log hay bỏ qua.

## 2. Kết luận nhanh

Các nguồn bổ sung đáng quan tâm nhất là:

1. `Babylon.txt`
2. `LacViet.txt`
3. `ChinesePhienAmEnglishWords.txt`
4. `Mark.txt`
5. Các file `*History.txt`
6. `Dictionaries.ini`

Đánh giá ngắn:

- `Babylon.txt`: nạp được ngay với parser gần như giống `VietPhrase`, giá trị tốt cho lớp tham chiếu ZH -> EN.
- `LacViet.txt`: rất đáng giá nhưng không nên nạp thô như dictionary dịch trực tiếp; nên nạp dưới dạng metadata/reference với parser riêng.
- `ChinesePhienAmEnglishWords.txt`: nạp được ngay nhưng giá trị thấp, nên để optional.
- `Mark.txt`: không nên vào bảng dictionary chính; nên đưa vào bảng/tập rule normalization.
- `*History.txt`: không phải dictionary lookup data; phù hợp hơn với audit/provenance tables ở Phase 06.
- `Dictionaries.ini`: là manifest/config source, không phải dictionary entries.
- `Bookmarks.txt`: bỏ qua.

## 3. Tình trạng hiện tại của migration script

Script hiện tại `scripts/migrate_qt_to_md.py` đã xử lý:

- `VietPhrase.txt`
- `VietPhrase2.txt`
- `Names.txt`
- `Names2.txt`
- `ChinesePhienAmWords.txt`
- `ThieuChuu.txt`
- `LuatNhan.txt`
- `LuatNhancu.txt`
- `TrichDan.txt`
- `Pronouns.txt`
- `IgnoredChinesePhrases.txt`
- `cedict_ts.u8`

Các nguồn còn lại chưa được migrate hoặc đang bị dùng chưa đúng vai trò:

- `Babylon.txt`
- `LacViet.txt`
- `ChinesePhienAmEnglishWords.txt`
- `ChinesePhienAmWordsHistory.txt`
- `NamesHistory.txt`
- `Names2History.txt`
- `VietPhraseHistory.txt`
- `Mark.txt`
- `Dictionaries.ini`
- `Bookmarks.txt`

## 4. Phân loại theo khả năng nạp

## 4.1 Nạp trực tiếp được với parser đơn giản

### `Babylon.txt`

- Dung lượng: `31,132` dòng
- Định dạng: `zh=en_definitions`
- Mẫu:
  - `丟三落四=forgetful; scatterbrained`
  - `佪徨=oscillate; vacillate; hesitate`

Đánh giá:

- Rất dễ parse bằng `parse_kv_line()`.
- Có thể chuyển thành `_bulk_babylon.md` ngay.
- Phù hợp làm dictionary tham chiếu `ZH -> EN`.

Giá trị với project:

- Hữu ích cho Phase 07 EN-VI.
- Hữu ích cho semantic fallback khi thiếu nghĩa Việt.
- Có thể dùng để hỗ trợ disambiguation hoặc UI glossary.

Khuyến nghị:

- Nạp vào DB dưới category kiểu `babylon_reference`.
- Không dùng làm nguồn dịch trực tiếp cho ZH -> VI.
- Priority nên thấp, tương đương `P0/P1 reference`.

### `ChinesePhienAmEnglishWords.txt`

- Dung lượng: `313` dòng
- Định dạng: `zh=romanized_english_like_forms`
- Mẫu:
  - `一=y`
  - `丁=tin dine`
  - `万=van wann`

Đánh giá:

- Parse rất dễ.
- Toàn bộ `313/313` khóa đã overlap với compiled DB hiện tại.
- Giá trị mới gần như bằng 0 nếu chỉ nhìn theo coverage key.

Giá trị với project:

- Có thể hữu ích rất hẹp cho transliteration sang English-like reading.
- Không đáng ưu tiên cho core translation path.

Khuyến nghị:

- Không cần nạp vào bảng dictionary chính ở giai đoạn này.
- Nếu cần, nạp vào `transliteration_reference` riêng.
- Ưu tiên thấp.

## 4.2 Nạp được nhưng cần parser riêng và phân vai trò đúng

### `LacViet.txt`

- Dung lượng: `66,450` dòng
- Định dạng: `zh=rich_explanation`
- Mẫu:
  - `阿=✚[ā] Hán Việt: A ...`
  - có pinyin, Hán Việt, nhiều lớp nghĩa và giải thích chi tiết

Đánh giá:

- Không phù hợp với parser `key=value` kiểu phẳng nếu mục tiêu là giữ tri thức.
- Rất phù hợp nếu migrate sang metadata-rich model:
  - `core_mapping.pinyin`
  - `reference_data.full_explanation`
  - `reference_data.han_viet_readings`
  - `morphology_and_syntax.pos_tag` nếu trích được
- Chỉ có khoảng `1,345` khóa mới so với compiled DB hiện tại, nhưng giá trị chính nằm ở enrichment chứ không nằm ở coverage.

Giá trị với project:

- Rất có giá trị cho:
  - tooltip/UI tra cứu;
  - fallback reference;
  - enrich pinyin/Hán Việt;
  - gợi ý semantic class hoặc parsed meanings;
  - QA và biên tập viên tra cứu.

Rủi ro:

- Nếu nạp thô vào bảng dictionary chính, output dịch sẽ bị “nát câu” vì đây là dạng tự điển giải nghĩa chứ không phải phrase translation dictionary.

Khuyến nghị:

- Nạp như `reference dictionary`, không nạp như direct translation dictionary.
- Cần parser riêng kiểu:
  - tách `pinyin`
  - tách `Hán Việt`
  - giữ `full_explanation`
  - tùy chọn parse danh sách nghĩa
- Priority rất thấp hoặc route vào bảng reference riêng.

### `ThieuChuu.txt`

Mặc dù đã được migrate, bản chất dữ liệu của `ThieuChuu.txt` gần với `LacViet.txt` hơn là với `PhienAm` thuần. Vì vậy đánh giá lại:

- không nên chỉ lưu như `target=text cleaned`;
- nên có parser riêng metadata-rich giống mô hình đã chốt trong master plan;
- nên xem đây là `reference/fallback layer`, không phải phrase translation layer.

Khuyến nghị:

- refactor migration hiện tại của `ThieuChuu` theo hướng parser riêng tương tự `LacViet`.

## 4.3 Không nên nạp vào bảng dictionary chính, nhưng nên dùng ở subsystem khác

### `Mark.txt`

- Dung lượng: `20` dòng
- Định dạng: map dấu câu / ký hiệu
- Mẫu:
  - `，=,`
  - `。=.`
  - `“="`

Đánh giá:

- Đây là normalization table, không phải lexical dictionary.
- Có ích cho preprocessing và output normalization.
- Có `15` key mới chưa nằm trong compiled DB, nhưng không nên đưa vào trie translation entries vì sẽ làm lẫn logic dấu câu với logic từ vựng.

Khuyến nghị:

- Nạp vào `normalization_marks` hoặc file config `mark_rules.json`.
- Dùng trong Phase 02 hoặc Phase 04 ở bước normalize/preserve/restore.

### `VietPhraseHistory.txt`

- Dung lượng: `5,144` dòng
- Định dạng: TSV audit log
- Cột:
  - `Entry`
  - `Action`
  - `User Name`
  - `Updated Date`

Đánh giá:

- Không phải dictionary content.
- Rất hữu ích làm provenance / audit trail.

Khuyến nghị:

- Không nạp vào `entries`.
- Có thể nạp vào `audit_events` hoặc `dictionary_history`.
- Dùng ở Phase 06 cho provenance tracking.

### `NamesHistory.txt`

- Dung lượng: `311` dòng
- Format: TSV audit log

Khuyến nghị:

- Cùng vai trò như `VietPhraseHistory.txt`.

### `Names2History.txt`

- Dung lượng: `655` dòng
- Format: TSV audit log

Khuyến nghị:

- Cùng vai trò như `VietPhraseHistory.txt`.

### `ChinesePhienAmWordsHistory.txt`

- Dung lượng: `20` record thực
- Format: TSV audit log

Khuyến nghị:

- Cùng vai trò như history files khác.

### `Dictionaries.ini`

- Dung lượng: `20` dòng
- Vai trò: manifest/config file cho Quick Translator
- Ví dụ:
  - `Names=Names.txt`
  - `Babylon=Babylon.txt`
  - `LacViet=LacViet.txt`
  - `Mark=Mark.txt`
  - `PanGuDict=PanguDict\Dict.dct`

Đánh giá:

- Không phải dictionary entries.
- Hữu ích để:
  - auto-discover sources trong migration script;
  - xác nhận source inventory;
  - phát hiện nguồn thiếu.

Lưu ý:

- `PanguDict\Dict.dct` được khai báo nhưng hiện không thấy file/folder tương ứng trong thư mục khảo sát.

Khuyến nghị:

- Dùng như manifest config, không nạp vào dictionary DB.

## 4.4 Có thể bỏ qua

### `Bookmarks.txt`

- Gần như rỗng.
- Không có giá trị cho dictionary DB hay pipeline hiện tại.

Khuyến nghị:

- Bỏ qua.

## 5. Đề xuất phân tầng dữ liệu trong database

Để dùng các nguồn bổ sung hiệu quả mà không làm bẩn core dictionary, nên chia DB thành 4 lớp:

### Lớp A: Core translation entries

- `VietPhrase`
- `VietPhrase2`
- `Names`
- `Names2`
- project-specific entries
- `LuatNhan` / `LuatNhanCu` dưới dạng rules

### Lớp B: Fallback lexical/reference

- `ChinesePhienAmWords`
- `ThieuChuu` metadata-rich
- `LacViet` metadata-rich
- `Babylon` reference
- `CEDICT` reference

### Lớp C: Normalization and preprocessing resources

- `IgnoredChinesePhrases`
- `Mark.txt`
- Traditional/Simplified resources ngoài QT nếu có

### Lớp D: Audit / provenance / operational metadata

- `VietPhraseHistory.txt`
- `NamesHistory.txt`
- `Names2History.txt`
- `ChinesePhienAmWordsHistory.txt`
- `Dictionaries.ini`

## 6. Đánh giá theo khả năng phục vụ project

| Nguồn | Khả năng parse | Nên nạp DB | Vai trò phù hợp | Mức ưu tiên |
| --- | --- | --- | --- | --- |
| `Babylon.txt` | Rất dễ | Có | `reference_en` | Cao |
| `LacViet.txt` | Trung bình, cần parser riêng | Có | `reference_vi_rich` | Rất cao |
| `ChinesePhienAmEnglishWords.txt` | Rất dễ | Tùy chọn | `transliteration_reference` | Thấp |
| `Mark.txt` | Rất dễ | Có, nhưng không vào `entries` | `normalization_marks` | Trung bình |
| `VietPhraseHistory.txt` | Dễ | Có, nhưng không vào `entries` | `audit_events` | Trung bình |
| `NamesHistory.txt` | Dễ | Có, nhưng không vào `entries` | `audit_events` | Thấp |
| `Names2History.txt` | Dễ | Có, nhưng không vào `entries` | `audit_events` | Thấp |
| `ChinesePhienAmWordsHistory.txt` | Dễ | Có, nhưng không vào `entries` | `audit_events` | Thấp |
| `Dictionaries.ini` | Rất dễ | Không cần nạp DB lookup | source manifest | Trung bình |
| `Bookmarks.txt` | Không đáng kể | Không | bỏ qua | Không |

## 7. Thứ tự triển khai khuyến nghị

### Ưu tiên 1

- `Babylon.txt`
- `Mark.txt`

Lý do:

- parse dễ;
- ít rủi ro;
- giá trị thực tế rõ;
- có thể mở rộng nhanh migration script.

### Ưu tiên 2

- `LacViet.txt`
- refactor `ThieuChuu.txt`

Lý do:

- giá trị tri thức rất cao;
- hỗ trợ tốt cho metadata model mới;
- hữu ích cho UI, QA, fallback, semantic enrichment.

### Ưu tiên 3

- `*History.txt`
- `Dictionaries.ini`

Lý do:

- không ảnh hưởng trực tiếp chất lượng dịch;
- hữu ích hơn ở Phase 06 khi làm provenance và audit.

### Ưu tiên 4

- `ChinesePhienAmEnglishWords.txt`

Lý do:

- giá trị thấp;
- overlap hoàn toàn với key hiện có;
- use case hẹp.

## 8. Đề xuất cập nhật migration script

Nên mở rộng `scripts/migrate_qt_to_md.py` theo các hướng:

1. thêm `migrate_babylon()`;
2. thêm `migrate_mark_rules()`;
3. tách parser riêng cho `LacViet`;
4. refactor `migrate_thieuchuu()` theo metadata-rich strategy;
5. thêm bước optional ingest history files vào report/audit dataset;
6. dùng `Dictionaries.ini` làm source manifest để script tự phát hiện nguồn hiện diện.

## 9. Kết luận

Nếu mục tiêu là phục vụ project DrDuc Translator một cách thực dụng:

- `Babylon.txt` nên được nạp sớm như nguồn tham chiếu ZH -> EN.
- `LacViet.txt` là nguồn giàu tri thức nhất trong các file chưa khai thác đúng mức và rất đáng để parser riêng.
- `Mark.txt` nên được đưa vào normalization subsystem thay vì trie dictionary.
- Các file `History` nên dành cho provenance/audit, không dành cho lookup.
- `ChinesePhienAmEnglishWords.txt` có thể để sau hoặc bỏ qua nếu không mở rộng nhánh transliteration.

Tóm lại, trong các “bộ từ điển khác”, hai nguồn đáng đầu tư nhất là:

1. `LacViet.txt`
2. `Babylon.txt`

vì chúng bổ sung tốt nhất cho định hướng metadata-rich dictionary DB và các phase Phase 04, Phase 06, Phase 07, Phase 08.
