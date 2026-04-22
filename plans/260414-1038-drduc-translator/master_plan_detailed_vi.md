# Master Plan Chi Tiết: DrDuc Translator

Ngày cập nhật: 2026-04-15  
Trạng thái: Bản kế hoạch thực thi hợp nhất  
Phạm vi: ZH/EN -> VI, non-LLM, ưu tiên triển khai thật trên repo hiện tại

## 1. Mục đích của tài liệu

Tài liệu này thay thế vai trò điều phối của các plan rời rạc hiện có bằng một master plan duy nhất, dùng để:

- phản ánh đúng hiện trạng codebase thay vì chỉ phản ánh ý tưởng;
- gom phạm vi của `plan.md`, `enhanced_plan.md`, các file phase, và tài liệu nghiên cứu kiến trúc;
- xác định rõ stack sản xuất, deliverable, phụ thuộc, tiêu chí nghiệm thu, rủi ro và thứ tự triển khai;
- làm cơ sở cập nhật `project_progress.json` và báo cáo tiến độ sau này.

Các bản plan cũ đã được dọn khỏi bộ tài liệu vận hành để tránh chồng chéo; tài liệu này là nguồn kế hoạch chính để triển khai.

## 2. Tóm tắt điều hành

Mục tiêu của dự án là xây dựng một hệ thống dịch thuật Trung-Việt và Anh-Việt không phụ thuộc LLM, ưu tiên:

- dịch văn bản dài, đặc biệt truyện và tài liệu nhiều chương;
- bảo toàn cấu trúc Markdown, HTML, code block, công thức và dữ liệu phi văn bản;
- sử dụng từ điển, trie, mẫu LuatNhan, quy tắc ngữ pháp và bộ nhớ dịch thuật;
- cho phép cải thiện chất lượng sau mỗi dự án thông qua Translation Memory và học tăng cường có kiểm soát;
- có desktop app để vận hành toàn bộ pipeline.

Tuy nhiên, hiện trạng repo cho thấy dự án chưa ở mức "0%" tuyệt đối. Nền tảng Phase 01 đã có triển khai thật khá sâu bằng Python, trong khi phần nâng cao ở JS mới chủ yếu là prototype/demonstration. Vì vậy kế hoạch mới phải bắt đầu bằng việc chốt lại nguồn sự thật kỹ thuật, đóng phần nền tảng còn dang dở, rồi mới mở rộng lên pipeline hoàn chỉnh.

## 3. Hiện trạng thực tế của repo

### 3.1 Những gì đã có thật

- Đã có script migrate dữ liệu Quick Translator sang Markdown Dictionary Format:
  - `scripts/migrate_qt_to_md.py`
- Đã có dictionary compiler:
  - `src/core/md_dictionary_compiler.py`
- Đã có trie engine:
  - `src/core/trie_engine.py`
- Đã có LuatNhan engine:
  - `src/core/luat_nhan_engine.py`
- Đã có number converter ở mức tương đối hoàn chỉnh:
  - `src/engine/number_converter.py`
- Đã có dữ liệu migrate và DB biên dịch:
  - `data/dictionaries/_migration_report.json`
  - `data/dictionaries/_compiled/trie_cache.db`
  - `data/dictionaries/_compiled/lookup_index.json`
- Đã có test Python cho phần nền tảng:
  - `tests/test_phase1.py`
  - `tests/test_number_converter.py`

### 3.2 Kết quả baseline kiểm tra tại thời điểm lập plan

- Migration report ghi nhận:
  - `895,468` dòng nguồn;
  - `898,116` mục migrated theo tổng hợp từng nguồn;
  - có dedupe và một số dòng bị bỏ qua ở LuatNhan, TrichDan, Pronouns, CEDICT.
- SQLite compiled database hiện có:
  - `784,442` dictionary entries;
  - `16,091` grammar patterns;
  - priority range hiện tại là `1..4`, nghĩa là chưa vận hành thực tế phần project-specific priority `P5`.
- Test Python:
  - `82 passed, 1 failed`;
  - lỗi hiện tại nằm ở parser Markdown table với escaped pipe `\|`.

### 3.3 Những gì mới ở mức prototype

Repo có một nhánh prototype bằng JS:

- `src/preprocessor/*.js`
- `src/parser/*.js`
- `src/rules/*.js`
- `src/learning/*.js`
- `index.js`
- `test_basic.js`
- `test_comprehensive.js`

Các file này hữu ích để mô tả kiến trúc và kiểm thử khái niệm, nhưng chưa thể xem là implementation production vì:

- nhiều module tự ghi rõ là `Mock`, `simplified implementation`, `demo implementation`;
- test JS hiện chủ yếu xác nhận interface tồn tại, không chạy E2E thật;
- stack mục tiêu trong plan gốc xác định backend chính là Python, trong khi nhánh JS chưa đồng bộ với cấu trúc phase Python đã thiết kế.

### 3.4 Kết luận hiện trạng

- Phase 01: đã triển khai thật phần lớn, nhưng chưa đóng phase.
- Phase 04: có một module production-level tương đối rõ là `number_converter.py`.
- Phase 02, 03, phần lớn của 04, 05, 06, 07, 08: chưa có production artifact tương ứng với plan.
- `project_progress.json` và các file phase đang thấp hơn thực tế ở Phase 01, nhưng lại cao hơn thực tế ở các phần enhanced nếu đọc theo ngôn ngữ mô tả.

## 4. Quyết định chiến lược

### 4.1 Nguồn sự thật kỹ thuật

Từ thời điểm plan này có hiệu lực:

- Python là nguồn sự thật cho translation engine, compiler, QA, TM, state management.
- SQLite là persistence layer chính cho compiled dictionaries, translation memory và metadata.
- Tauri + React là lớp desktop UI khi Phase 08 bắt đầu.
- JS prototype được xem là tài liệu nghiên cứu hoặc reference implementation, không phải production core.

### 4.2 Định hướng triển khai

Thứ tự ưu tiên triển khai:

1. Đóng phần nền tảng hiện có.
2. Tạo được một RBMT pipeline tối thiểu chạy thật trên dữ liệu thật.
3. Chỉ thêm mô-đun nâng cao khi có đường ống cơ bản đã ổn định.
4. Chỉ mở UI desktop khi backend đã có command contract ổn định.

### 4.3 Nguyên tắc thực thi

- Không đưa thêm module mô hình nặng nếu chưa có baseline heuristic chạy được.
- Mỗi phase phải có artifact chạy được, test được, benchmark được.
- Ưu tiên vertical slice hơn là mở rộng đồng loạt nhiều mô-đun chưa tích hợp.
- Mọi yêu cầu nâng cao phải có fallback heuristic trước khi triển khai statistical model phức tạp.

## 5. Kiến trúc đích

### 5.1 Các lớp chính

- `data/`
  - dữ liệu từ điển nguồn, dữ liệu đã migrate, compiled DB, assets kiểm thử
- `src/core/`
  - compiler, trie, LuatNhan, các primitive xử lý từ điển
- `src/pipeline/`
  - import, split chapter, scan entity, suggest thuật ngữ, sinh config
- `src/engine/`
  - preservation, segmentation, RBMT orchestrator, number conversion, pronoun resolution, context
- `src/qa/`
  - checker và report generator
- `src/state/`
  - project manager, translation memory, sync, checkpoint
- `src/en_vi/` hoặc `src/engine/en_vi_*.py`
  - EN-VI engine
- `src-tauri/` và `src/`
  - desktop app

### 5.2 Luồng dữ liệu chuẩn

1. Input file import
2. Normalize encoding và format
3. Tách chương
4. Bảo toàn cấu trúc phi dịch
5. Traditional -> Simplified
6. Pinyin -> Simplified
7. Scan entity và thuật ngữ
8. Sentence segmentation
9. Translation Memory lookup
10. Trie + LuatNhan + rule-based translation
11. Pronoun/EAPEE resolution
12. Number conversion
13. QA checks
14. Output clean + draft annotated
15. Save TM + state + feedback loop

### 5.3 Giao ước đầu ra

Mỗi project dịch phải có tối thiểu:

- `source/raw/`
- `source/chapters/`
- `working/entities/`
- `working/relationships/`
- `working/config/translation_config.json`
- `drafts/`
- `output/`
- `reports/qa_report.md`
- `state/project_state.json`

### 5.4 Mô hình metadata chuẩn cho dictionary entries

Từ thời điểm này, mọi nguồn từ điển migrate mới phải quy về một mô hình metadata logic thống nhất, dù cách lưu vật lý vẫn có thể là Markdown, JSON hoặc SQLite.

Schema logic tối thiểu:

```json
{
  "entry_id": "stable_unique_id",
  "core_mapping": {
    "source_zh": "本座",
    "source_zh_trad": "本座",
    "target_vi": "bổn tọa",
    "pinyin": "běn zuò"
  },
  "reference_data": {},
  "morphology_and_syntax": {
    "pos_tag": "PRONOUN",
    "semantic_class": null,
    "entity_type": null,
    "luat_nhan_trigger": false
  },
  "eapee_context": {
    "genre": [],
    "speaker_identity": [],
    "listener_identity": [],
    "emotion_state": []
  },
  "system_flags": {
    "priority": 4,
    "is_one_mean": true,
    "is_locked": true,
    "cultural_origin": "han_viet"
  },
  "provenance_and_state": {
    "source_dict": "Pronouns",
    "project_id": null,
    "status": "verified",
    "created_at": "2026-04-15T00:00:00Z",
    "updated_at": "2026-04-15T00:00:00Z",
    "hit_count": 0
  },
  "disambiguation_patterns": []
}
```

Ý nghĩa các khối:

- `entry_id`: định danh ổn định để hỗ trợ upsert, provenance và TM/rule promotion.
- `core_mapping`: cặp dịch cốt lõi, bao gồm cả giản thể, phồn thể và pinyin khi có.
- `reference_data`: vùng chứa thông tin giải thích, nghĩa phụ, raw target, tooltip data.
- `morphology_and_syntax`: phục vụ POS, semantic class, entity typing và trigger logic.
- `eapee_context`: phục vụ xưng hô, vai giao tiếp, thể loại, cảm xúc.
- `system_flags`: điều khiển priority, locked, one-mean, cultural origin.
- `provenance_and_state`: theo dõi nguồn gốc, project scope, trạng thái candidate/verified và hit count.
- `disambiguation_patterns`: danh sách luật cục bộ để ưu tiên ứng viên phù hợp khi đa nghĩa.

### 5.5 Chiến lược multiple entries và disambiguation

Hệ thống không được ép các từ đa nghĩa hoặc đa từ loại vào một bản ghi duy nhất. Cách làm chuẩn là:

- tách mỗi nghĩa hoặc vai trò cú pháp thành một entry riêng;
- dùng `priority` để giải quyết xung đột giữa từ điển chung, tên riêng và project-specific data;
- dùng `entity_type`, `genre`, `semantic_class`, `luat_nhan_trigger` để sàng tiếp ở tầng ngữ cảnh;
- dùng `disambiguation_patterns` để tăng điểm hoặc loại bỏ ứng viên trong RBMT Core.

Quy trình chọn nghĩa chuẩn:

1. Trie trả về tập ứng viên theo khóa nguồn.
2. Lọc theo `priority`.
3. Lọc tiếp theo `project_id`, `genre`, `entity_type`, context chapter.
4. Nếu còn nhập nhằng và `luat_nhan_trigger = true`, chuyển sang LuatNhan/RBMT local rules.
5. Nếu vẫn chưa đủ chắc chắn, fallback về nghĩa mặc định và ghi cờ ambiguity vào draft/QA.

Ví dụ điển hình:

- một khóa có thể vừa là danh từ chung vừa là tên nhân vật;
- một lượng từ như `道` có thể ra `đạo`, `luồng`, `món`, tùy `semantic_class` của danh từ phía sau;
- một từ đa nghĩa trong VietPhrase phải được giữ `alternative_meanings` trong `reference_data` để hậu kiểm và UI sử dụng.

### 5.6 Chiến lược migration chuẩn hóa theo nguồn

Mỗi nguồn từ điển cần có chiến lược migrate riêng, nhưng đổ về cùng mô hình metadata ở trên.

`VietPhrase` và `VietPhrase2`:

- ưu tiên phrase-level;
- `target_vi` mặc định lấy nghĩa đầu;
- các nghĩa phụ được giữ trong `reference_data.alternative_meanings`;
- nếu có nhiều nghĩa, tự động bật `luat_nhan_trigger = true` và `is_one_mean = false`.

`Names`, project names và entity dictionaries:

- gán `entity_type` rõ ràng;
- ưu tiên `P4` cho global names và `P5` cho project-specific names;
- thường `is_locked = true`.

`PhienAm`:

- không còn được xem là lớp dịch cốt lõi mặc định;
- chỉ nên tồn tại như residual fallback cho các ký tự hoặc biến thể chưa được bao phủ bởi metadata-rich dictionaries;
- nếu `LacViet`, `ThieuChuu`, `CEDICT` hoặc source metadata khác đã cung cấp đủ `pinyin`, `han_viet_readings` hoặc `target_vi` cho khóa đó, standalone `PhienAm` có thể bị loại khỏi fast path compile;
- mục tiêu dài hạn là co hẹp `PhienAm` thành sparse fallback set thay vì full-layer bắt buộc.

`ThieuChuu`:

- không dùng làm phrase translation mặc định;
- ưu tiên rất thấp (`P0` hoặc fallback tương đương);
- phải giữ `reference_data.full_explanation`, `han_viet_readings`, và nếu parse được thì `parsed_meanings`;
- mục tiêu chính là tra cứu, fallback Hán Việt và hỗ trợ UI/tooltip.

`LuatNhan` và rule templates:

- giữ riêng như grammar/disambiguation assets;
- về lâu dài có thể tham chiếu trực tiếp các trường `semantic_class`, `entity_type`, `disambiguation_patterns`.

`CEDICT` và từ điển tham chiếu:

- chỉ dùng làm nguồn hỗ trợ giải nghĩa hoặc EN meaning;
- không được chiếm ưu tiên trực tiếp trước VietPhrase/Names trong ZH -> VI pipeline.

### 5.7 Tối ưu database dictionary theo metadata-first

Dictionary database không nên tiếp tục phát triển như một kho `source -> target` phẳng. Với metadata model mới, DB phải được tối ưu theo hai lớp truy cập:

- hot path: phục vụ lookup rất nhanh cho translation runtime;
- cold path: phục vụ giải nghĩa sâu, UI, QA, provenance, candidate review.

Thiết kế logic khuyến nghị:

- `entries_hot`
  - `entry_id`
  - `source_zh`
  - `normalized_source`
  - `target_vi_primary`
  - `priority`
  - `source_dict`
  - `entity_type`
  - `semantic_class`
  - `flags_bitmask`
- `entries_metadata`
  - JSON hoặc side-table cho `reference_data`, `eapee_context`, `disambiguation_patterns`
- `entry_readings`
  - `pinyin`
  - `han_viet_readings`
  - `source_zh_trad`
- `grammar_patterns`
  - LuatNhan, disambiguation templates, pattern weights
- `normalization_rules`
  - punctuation marks, ignored phrases, normalization maps
- `audit_events`
  - history import, created/updated metadata, reviewer actions

Nguyên tắc tối ưu:

- chỉ giữ field cần cho runtime scoring trên hot path;
- đưa giải nghĩa dài, tooltip data, note, parsed meanings sang cold path;
- dùng bitmask hoặc enum cho các flag nóng như `is_locked`, `is_one_mean`, `luat_nhan_trigger`;
- materialize `normalized_source` để giảm chi phí normalize tại lookup time;
- chuẩn bị khả năng compile nhiều layer riêng: `core`, `reference`, `normalization`, `audit`.

### 5.8 Chiến lược giảm phụ thuộc vào dữ liệu cứng

Mục tiêu của kiến trúc mới không phải là mở rộng vô hạn số lượng cụm phrase hardcoded, mà là tăng tỷ trọng xử lý bằng thuật toán và metadata-aware ranking.

Các hướng chính:

- thay vì thêm vô hạn phrase cố định, ưu tiên `semantic_class` + luật lượng từ + disambiguation patterns;
- thay vì dựa vào `PhienAm` nguyên khối, ưu tiên trích `pinyin`, `han_viet_readings`, `full_explanation` từ `LacViet`/`ThieuChuu`;
- thay vì lưu một bản dịch duy nhất cho từ đa nghĩa, lưu nhiều ứng viên và xếp hạng theo:
  - `priority`
  - `entity_type`
  - `genre`
  - `semantic_class`
  - context window
  - local rules
- chuẩn hóa các lớp thuật toán có thể thay phrase data:
  - number/date/time/unit conversion
  - punctuation normalization
  - measure-word resolution
  - capitalization/entity rendering
  - classifier-driven noun phrase assembly

### 5.9 Chiến lược nạp thêm nguồn dictionary

Theo đánh giá hiện tại, thứ tự nạp thêm nguồn nên là:

1. `Babylon.txt`
2. `Mark.txt`
3. `LacViet.txt`
4. refactor `ThieuChuu.txt`
5. `*History.txt`
6. `ChinesePhienAmEnglishWords.txt` nếu còn nhu cầu

Vai trò mong muốn sau khi nạp:

- `Babylon`: `reference_en`
- `LacViet`: `reference_vi_rich`
- `ThieuChuu`: `reference_vi_rich` / fallback Hán-Việt
- `Mark`: `normalization_rules`
- `History files`: `audit_events`
- `PhienAm`: `residual_readings_fallback`

### 5.10 Chính sách với PhienAm

Chính sách mới:

- không mặc định compile toàn bộ `ChinesePhienAmWords.txt` vào fast path nếu coverage đã được thay thế bởi source giàu metadata hơn;
- trước khi giữ `PhienAm` như một lớp riêng, phải đo:
  - coverage không trùng với `LacViet`/`ThieuChuu`
  - số ký tự còn thiếu reading sau khi hợp nhất nguồn rich metadata
  - ảnh hưởng tốc độ và RAM khi giữ full layer
- đầu ra mong muốn là một `residual fallback dictionary` nhỏ, chỉ chứa:
  - ký tự hiếm
  - glyph đặc biệt
  - ký tự không có trong các nguồn khác

Điều này giúp:

- giảm dung lượng trie;
- giảm nhiễu khi fallback từng chữ;
- giảm phụ thuộc vào lớp từ điển cứng ít ngữ cảnh;
- tăng cơ hội ưu tiên phrase-level và metadata-driven disambiguation.

## 6. Phạm vi và ngoài phạm vi

### 6.1 Trong phạm vi

- ZH -> VI là trọng tâm ưu tiên số 1.
- EN -> VI là nhánh mở rộng sau khi core ZH -> VI ổn định.
- Bộ từ điển Quick Translator migrate.
- Pinyin, Traditional/Simplified normalization.
- Pronoun/EAPEE, LuatNhan, QA, TM, desktop app.

### 6.2 Ngoài phạm vi giai đoạn đầu

- Neural MT.
- Huấn luyện model lớn hoặc pipeline ML nặng.
- Cloud service bắt buộc.
- Real-time collaboration đa người.
- Tự động học quy tắc không kiểm soát rồi áp trực tiếp lên production output.

## 7. Lộ trình tổng thể

Kế hoạch mới gồm 9 phase thực thi:

- Phase 00: Alignment & Stabilization
- Phase 01: Foundation Closeout
- Phase 02: Pre-Translation Pipeline
- Phase 03: EAPEE
- Phase 04: RBMT Core
- Phase 05: QA Engine
- Phase 06: State Management & Translation Memory
- Phase 07: EN-VI Engine
- Phase 08: Desktop UI

## 8. Phase 00: Alignment & Stabilization

### 8.1 Mục tiêu

Chốt lại baseline kỹ thuật, phân định production code với prototype, và sửa các lỗi cản trở việc đóng nền tảng.

### 8.2 Hiện trạng

- Cần thiết ngay.
- Chưa có trong plan cũ nhưng bắt buộc để tránh kéo dài lệch hướng.

### 8.3 Deliverable

- Một baseline sạch, test Python xanh, đường hướng stack rõ ràng.
- Tài liệu cập nhật tiến độ và vai trò từng thư mục.

### 8.4 Công việc chi tiết

- Sửa lỗi `_parse_md_table()` để hỗ trợ escaped pipe `\|`.
- Chạy lại full test Python.
- Chuẩn hóa vai trò của thư mục JS:
  - hoặc chuyển về `prototype_js/`;
  - hoặc đánh dấu rõ là reference only.
- Đồng bộ `project_progress.json` với trạng thái thật.
- Thêm tài liệu `ARCHITECTURE_DECISIONS.md` hoặc gộp vào README để chốt:
  - production core = Python;
  - JS modules = experimental/reference.
- Kiểm tra lại `requirements.txt`, `pyproject.toml`, đường dẫn runtime.

### 8.5 Tiêu chí nghiệm thu

- `python -m pytest -q` pass 100%.
- Không còn mơ hồ về stack chính.
- Tracker phản ánh đúng baseline.

### 8.6 Ước lượng

- 1 đến 2 session.

## 9. Phase 01: Foundation Closeout

### 9.1 Mục tiêu

Đóng hoàn chỉnh lớp nền tảng từ điển, compiler, trie và LuatNhan để làm input ổn định cho toàn bộ hệ thống.

### 9.2 Trạng thái hiện tại

- Đã hoàn tất và có thể đóng phase.
- Benchmark/rebuild workflow đã chốt với baseline reproducible.
- `PhienAm` đã được co về residual runtime, phần reading còn lại đi qua `entry_readings`.

### 9.3 Deliverable

- Migration pipeline ổn định.
- Compiled dictionary DB có thể rebuild lặp lại.
- Trie lookup production-ready.
- LuatNhan engine chạy được trên entity pairs thật.

### 9.4 Hạng mục chuyển tiếp sau khi đóng phase

- Multi-entry candidate retrieval theo `entry_id` chuyển sang Phase 04.
- Runtime scorer dùng sâu `entity_type`, `semantic_class`, `flags_bitmask` chuyển sang Phase 04/05.
- Incremental rebuild tiếp tục là tối ưu hóa hậu Phase 01, không còn là blocker nghiệm thu.

### 9.4.1 Gói task thực thi chi tiết

- `FND-001`: kiểm kê source từ `Dictionaries.ini`, đối chiếu với source đang migrate và gán vai trò runtime. Completed.
- `FND-002`: chốt schema logic cho `core_mapping`, `reference_data`, `morphology_and_syntax`, `provenance_and_state`. Completed ở mức cần cho Phase 01.
- `FND-003`: tách thiết kế compiled DB thành hot path và cold path. Completed.
- `FND-004`: viết parser `Babylon.txt` vào lớp `reference_en`. Completed.
- `FND-005`: viết parser `Mark.txt` vào lớp `normalization_rules`. Completed.
- `FND-006`: viết parser metadata-rich cho `LacViet.txt`. Completed.
- `FND-007`: refactor parser `ThieuChuu.txt` để sinh `han_viet_readings`, `parsed_meanings`, `full_explanation`. Completed.
- `FND-008`: import `*History.txt` vào `audit_events` thay vì lookup dictionary. Completed.
- `FND-009`: đo coverage thực tế của `PhienAm` sau khi hợp nhất `LacViet` và `ThieuChuu`. Completed.
- `FND-010`: quyết định compile `PhienAm` theo residual fallback set thay cho full fast-path layer nếu đủ điều kiện. Completed.
- `FND-011`: materialize các field nóng phục vụ trie scoring và runtime ranking. Completed ở mức lookup nền; candidate scoring nâng cao được chuyển sang Phase 04/05.
- `FND-012`: thêm benchmark và coverage report cho từng dictionary layer. Completed.

### 9.5 Tiêu chí nghiệm thu

- Migration lặp lại được.
- Build DB không lỗi.
- Lookup đúng top terms và đúng ưu tiên.
- LuatNhan đúng trên tập entity pair mẫu.
- Có benchmark reproducible.
- Test phase pass hoàn toàn.

### 9.6 Rủi ro

- Dữ liệu nguồn Quick Translator không đồng nhất.
- Một số file có format lẫn lộn, dễ gây mismatch count.
- Priority `P5` hiện chưa được thử thực chiến.

### 9.7 Ước lượng

- 2 đến 3 session sau Phase 00.

## 10. Phase 02: Pre-Translation Pipeline

### 10.1 Mục tiêu

Xây dựng pipeline đầu vào chuẩn hóa tài liệu trước dịch, gồm import, split chương, preserve cấu trúc, Traditional/Simplified, Pinyin, entity scan và config generation.

### 10.2 Trạng thái hiện tại

- Chưa có artifact Python theo plan.
- Một phần ý tưởng đã có prototype JS.
- Đánh giá thực tế: `0-10%`.

### 10.3 Deliverable

- `document_importer.py`
- `chapter_splitter.py`
- `structure_preserver.py`
- `traditional_to_simplified.py`
- `pinyin_processor.py`
- `entity_scanner.py`
- `relationship_builder.py`
- `terminology_suggester.py`
- `config_generator.py`

### 10.4 Thứ tự triển khai

1. Importer và chapter splitter.
2. Structure preservation.
3. Traditional -> Simplified.
4. Pinyin -> Simplified.
5. Entity scan và relationship builder.
6. Terminology suggestion và config generation.

### 10.5 Công việc chi tiết

- Import HTML, TXT, MD, DOCX, PDF.
- Normalize encoding:
  - UTF-8
  - GB2312
  - GBK
  - Big5
  - UTF-16
- Split chapter theo regex ZH/VI/EN và fallback theo word count.
- Preserve:
  - code block
  - inline code
  - HTML tag
  - image/link
  - LaTeX
  - table placeholders
- Traditional/Simplified:
  - phrase-level trước
  - char-level fallback
  - regional mapping nếu có
- Pinyin:
  - heuristic version trước;
  - model-based disambiguation sau;
  - chỉ convert khi confidence đủ cao
- Entity scanning:
  - character
  - location
  - faction
  - weapon/item
  - technique
  - realm
- Relationship builder:
  - kinship
  - dialogue pair
  - faction membership
  - power hints
- Suggester:
  - Han-Viet
  - cultural origin
  - naming policy
  - genre hints
- Tạo danh sách `high_ambiguity_terms` cho project khi một khóa có nhiều vai trò hoặc nhiều nghĩa mạnh.
- Chuẩn hóa output entity scan để feed trực tiếp cho RBMT và EAPEE.
- Sinh `translation_config.json`.

### 10.5.1 Gói task thực thi chi tiết

- `PRE-001`: xây importer đa định dạng với output contract thống nhất cho mọi project.
- `PRE-002`: xây chapter splitter có thể review và override boundary.
- `PRE-003`: compile `Mark.txt` thành normalization map dùng chung cho import và runtime.
- `PRE-004`: tạo structure-preserver có registry placeholder ổn định.
- `PRE-005`: xây T2S phrase-first, char-fallback với provenance rõ ràng.
- `PRE-006`: thiết kế reading resolver ưu tiên `pinyin` và `han_viet_readings` lấy từ metadata-rich dictionaries trước khi dùng residual `PhienAm`.
- `PRE-007`: entity scanner phải tận dụng `entity_type`, `semantic_class`, `source_dict`, `priority`.
- `PRE-008`: relationship builder phải sinh graph tối thiểu cho kinship, affiliation, dialogue adjacency.
- `PRE-009`: terminology suggester phải phát hiện term cần khóa cứng, term cần LuatNhan và term nên để machine-ranking.
- `PRE-010`: config generator phải sinh `high_ambiguity_terms`, naming policy, genre hints, cultural-origin hints.

### 10.6 Tiêu chí nghiệm thu

- Import và split được trên tập mẫu đa định dạng.
- Preserve/restore không làm hỏng cấu trúc.
- T2S hoạt động đúng trên tập mẫu Phồn thể.
- Pinyin processor có fallback an toàn.
- Entity detection đủ tốt để hỗ trợ workflow biên tập.
- Sinh config tự động cho project mới.

### 10.7 Ước lượng

- 5 đến 7 session.

## 11. Phase 03: EAPEE

### 11.1 Mục tiêu

Xây dựng engine xưng hô và biểu đạt theo ngữ cảnh, là lớp tạo khác biệt chất lượng cho bản dịch truyện.

### 11.2 Trạng thái hiện tại

- Chưa có engine Python.
- Thư mục expressions hiện chưa có data file thật.
- Đánh giá thực tế: `0-5%`.

### 11.3 Deliverable

- `emotion_detector.py`
- `emotion_state.py`
- `pronoun_resolver.py`
- `expression_bank.py`
- bộ dữ liệu expressions ở dạng MD/JSON

### 11.4 Công việc chi tiết

- Thiết kế schema cho 4 chiều:
  - genre
  - relationship
  - emotion
  - gender/identity
- Xây emotion detector heuristic trước:
  - keyword
  - dialogue verbs
  - punctuation
- Xây state machine để duy trì cảm xúc theo scene.
- Xây speaker/listener resolver từ pattern hội thoại.
- Thiết kế pronoun matrix cho:
  - cổ trang
  - hiện đại
  - tiên hiệp
- Xây identity override:
  - trẫm
  - bổn tọa
  - bần tăng
  - bổn cung
- Tạo expression bank:
  - curses
  - endearments
  - interjections
  - tone markers
- Tạo test set hội thoại mẫu.

### 11.5 Tiêu chí nghiệm thu

- Pronoun resolver chạy được trong pipeline câu thoại.
- Có dataset expressions tối thiểu.
- Độ chính xác baseline trên test set nội bộ chấp nhận được.
- Có fallback an toàn khi không xác định được quan hệ.

### 11.6 Ước lượng

- 6 đến 8 session.

## 12. Phase 04: RBMT Core

### 12.1 Mục tiêu

Tạo translation orchestrator chạy thật từ câu nguồn đến câu đích, tích hợp trie, LuatNhan, preserve, number conversion, TM lookup, context và EAPEE.

### 12.2 Trạng thái hiện tại

- `number_converter.py` đã có nền tảng tốt.
- Chưa có orchestrator và các engine còn lại theo Python plan.
- Đánh giá thực tế: `10-15%`.

### 12.3 Deliverable

- `sentence_segmenter.py`
- `structure_preserver.py`
- `context_manager.py`
- `cultural_origin_detector.py`
- `rbmt_translator.py`
- output clean + draft annotated

### 12.4 Công việc chi tiết

- Tạo sentence segmenter cho ZH.
- Tạo structure preservation phiên bản production Python.
- Tạo TM lookup interface.
- Tạo pipeline apply theo thứ tự:
  - preserve
  - normalize
  - segment
  - TM exact/fuzzy
  - trie candidate retrieval
  - priority/entity/genre filtering
  - LuatNhan/disambiguation rule application
  - syntax transfer rules
  - EAPEE
  - number conversion
  - restore
  - context update
- Hỗ trợ `semantic_class` và `disambiguation_patterns` trong candidate ranking.
- Đánh dấu ambiguity unresolved trong draft output thay vì âm thầm chọn nghĩa.
- Tạo context manager 5+5 câu.
- Tạo cultural origin hints cho naming/output policy.
- Hỗ trợ batch mode theo chapter.
- Sinh hai loại output:
  - clean output
  - annotated draft

### 12.4.1 Gói task thực thi chi tiết

- `RBM-001`: sentence segmenter cho ZH với boundary an toàn cho thoại, dấu ngoặc và chấm lửng.
- `RBM-002`: candidate retrieval phải trả multi-entry thay vì một đáp án duy nhất.
- `RBM-003`: runtime scorer phải dùng `priority`, `project_id`, `entity_type`, `semantic_class`, `genre`, `context_window`.
- `RBM-004`: local rule executor phải áp `LuatNhan`, `disambiguation_patterns`, measure-word rules.
- `RBM-005`: noun phrase assembly phải ưu tiên thuật toán classifier-driven hơn là phình phrase dictionary vô hạn.
- `RBM-006`: reading fallback chỉ được dùng sau khi phrase-level và metadata-rich candidates thất bại.
- `RBM-007`: ambiguity manager phải giữ candidate trail để QA/UI giải thích được vì sao engine chọn nghĩa.
- `RBM-008`: context manager phải cập nhật entity hoạt động, scene state, TM save points.
- `RBM-009`: output builder phải sinh clean output và annotated draft từ cùng một translation trace.

### 12.5 Chiến lược triển khai

- Vertical slice đầu tiên không cần parser/dependency đầy đủ.
- Dùng heuristic syntax transfer đủ dùng trước.
- Chỉ sau khi E2E chạy ổn định mới mở rộng rule grammar nâng cao.

### 12.6 Tiêu chí nghiệm thu

- Dịch được một chapter đầy đủ bằng pipeline Python.
- Không làm hỏng cấu trúc placeholder.
- Number conversion và trie interplay đúng.
- Batch mode chạy được nhiều chapter liên tiếp.
- Có output clean và draft.

### 12.7 Ước lượng

- 6 đến 8 session.

## 13. Phase 05: QA Engine

### 13.1 Mục tiêu

Xây hệ thống kiểm tra hậu dịch để phát hiện lỗi thuật ngữ, xưng hô, cấu trúc, untranslated text và độ lệch chiều dài.

### 13.2 Trạng thái hiện tại

- Chưa có implementation thật.
- Đánh giá thực tế: `0%`.

### 13.3 Deliverable

- `terminology_checker.py`
- `pronoun_checker.py`
- `emotion_consistency_checker.py`
- `structure_checker.py`
- `untranslated_detector.py`
- `length_checker.py`
- `report_generator.py`

### 13.4 Công việc chi tiết

- So sánh output với glossary và name rules.
- Kiểm tra các vị trí mà engine đã dùng fallback low-priority hoặc unresolved ambiguity.
- Kiểm tra xưng hô theo cặp nhân vật.
- Kiểm tra consistency cảm xúc giữa các câu thoại liền kề.
- Kiểm tra placeholder restoration, số đoạn, table integrity.
- Detect Hán tự còn sót.
- Kiểm tra tỷ lệ source/target bất thường.
- Hiển thị `alternative_meanings` hoặc tooltip từ `reference_data` khi sinh report.
- Sinh Markdown report có severity.

### 13.4.1 Gói task thực thi chi tiết

- `QA-001`: terminology checker phải kiểm tra drift giữa các source có priority khác nhau.
- `QA-002`: fallback auditor phải báo riêng trường hợp engine rơi xuống `P0` hoặc residual `PhienAm`.
- `QA-003`: ambiguity auditor phải hiển thị top candidates và pattern/rule đã dùng.
- `QA-004`: structure checker phải xác nhận placeholder restore, table integrity, chapter order.
- `QA-005`: untranslated detector phải phân biệt Hán tự sót, pinyin sót và placeholder lỗi.
- `QA-006`: report generator phải đọc được metadata cold path như `full_explanation`, `alternative_meanings`, `source_dict`.

### 13.5 Tiêu chí nghiệm thu

- Bắt được lỗi injected trong test corpus.
- Report đọc được và trỏ được vị trí vi phạm.
- Có thể chạy như bước độc lập sau translate.

### 13.6 Ước lượng

- 3 đến 4 session.

## 14. Phase 06: State Management & Translation Memory

### 14.1 Mục tiêu

Tạo lớp lưu trạng thái project và bộ nhớ dịch thuật để hệ thống có thể tiếp tục làm việc qua nhiều chương, nhiều dự án.

### 14.2 Trạng thái hiện tại

- Có ý tưởng và prototype JS cho TM.
- Chưa có implementation Python theo plan.
- Đánh giá thực tế: `0-10%`.

### 14.3 Deliverable

- `project_manager.py`
- `translation_memory.py`
- `obsidian_sync.py`
- schema SQLite cho TM và state

### 14.4 Công việc chi tiết

- Tạo project CRUD.
- Tạo state file cho project.
- Tạo TM exact match.
- Tạo TM fuzzy match bằng Levenshtein hoặc scoring tương đương.
- Tạo import từ các dự án dịch cũ.
- Tạo watch/sync mode nếu cần.
- Thiết kế provenance tracking cho learned rules/TM entry.
- Theo dõi `hit_count`, `status`, `created_at`, `updated_at` cho từ mới, rule mới, TM segments.
- Chỉ cho phép learned rule ở trạng thái `candidate` cho đến khi được duyệt.

### 14.4.1 Gói task thực thi chi tiết

- `STM-001`: chốt schema cho `projects`, `chapters`, `segments`, `tm_entries`, `candidate_entries`, `candidate_rules`, `audit_events`.
- `STM-002`: import `*History.txt` vào `audit_events` và mapping lại theo `entry_id`.
- `STM-003`: lưu translation trace đủ để truy vết candidate nào đã được chọn và candidate nào bị loại.
- `STM-004`: TM exact/fuzzy phải lưu provenance, confidence và reviewer feedback.
- `STM-005`: candidate workflow phải hỗ trợ `candidate -> verified -> locked`.
- `STM-006`: tạo analytics cho source coverage, hit distribution, low-priority fallback rate.
- `STM-007`: tạo báo cáo riêng để đo giá trị còn lại của full `PhienAm` layer theo dữ liệu runtime.

### 14.5 Tiêu chí nghiệm thu

- Tạo project mới được.
- Resume project giữa chừng được.
- TM exact/fuzzy hoạt động.
- Có thể import tri thức từ dữ liệu cũ.

### 14.6 Ước lượng

- 4 đến 5 session.

## 15. Phase 07: EN-VI Engine

### 15.1 Mục tiêu

Mở rộng nền tảng trie/rule sang Anh-Việt với phạm vi gọn hơn ZH-VI.

### 15.2 Trạng thái hiện tại

- Chưa có implementation Python đúng plan.
- Có dữ liệu `en_vi` ở dictionary layer.
- Đánh giá thực tế: `0-5%`.

### 15.3 Deliverable

- `en_vi_translator.py`
- tokenizer + phrase matcher
- rule set cơ bản cho adjective order, possessive, tense markers

### 15.4 Công việc chi tiết

- Migrate và chuẩn hóa dữ liệu EN-VI thật sự dùng được.
- Tokenize English.
- Ưu tiên phrase match dài hơn word match.
- Rule chuyển:
  - adjective + noun
  - possessive
  - article removal
  - plural handling
  - tense marker hints
- Tạo test corpus EN-VI.

### 15.4.1 Gói task thực thi chi tiết

- `ENVI-001`: chuẩn hóa EN-VI entries theo cùng metadata model với ZH-VI.
- `ENVI-002`: tách phrase entries và word entries cho hot-path matching.
- `ENVI-003`: xây tokenizer và matcher ưu tiên multi-word units.
- `ENVI-004`: grammar transfer baseline cho adjective order, possessive, plural, tense hints.
- `ENVI-005`: nối QA và TM để tái dùng hạ tầng đã có thay vì dựng nhánh độc lập.

### 15.5 Tiêu chí nghiệm thu

- Dịch câu và đoạn ngắn EN-VI theo rule-based baseline.
- Đúng phrase priority.
- Không ảnh hưởng core ZH-VI.

### 15.6 Ước lượng

- 3 đến 4 session.

## 16. Phase 08: Desktop UI

### 16.1 Mục tiêu

Tạo desktop app để vận hành toàn bộ workflow project, dictionary, pre-translation, translation và QA.

### 16.2 Trạng thái hiện tại

- Chưa có Tauri app.
- Đánh giá thực tế: `0%`.

### 16.3 Điều kiện mở phase

Chỉ bắt đầu khi:

- RBMT core có CLI hoặc IPC contract ổn định;
- QA và state management đã có command interface;
- format output/input của engine đã cố định tương đối.

### 16.4 Deliverable

- Tauri app skeleton
- Python sidecar bridge
- 7 màn hình chính
- command protocol ổn định

### 16.5 Công việc chi tiết

- Init Tauri + React + TypeScript.
- Tạo IPC contract:
  - build dictionary
  - create project
  - import file
  - scan entities
  - translate
  - run QA
  - export output
- Tạo các màn hình:
  - Project Manager
  - Dictionary Manager
  - Translation Workspace
  - Entity & Relationship Viewer
  - Pre-Translation Review
  - QA Report Viewer
  - Settings
- Dictionary Manager và Translation Workspace phải hiển thị được:
  - `reference_data.full_explanation`
  - `alternative_meanings`
  - `source_dict`
  - `status`
  - `priority`
- Tạo luồng duyệt `candidate -> verified` cho từ/rule mới.
- Tạo progress streaming cho batch translate.
- Tạo package build Windows.

### 16.5.1 Gói task thực thi chi tiết

- `UI-001`: chốt command protocol giữa Tauri và Python sidecar.
- `UI-002`: dựng Project Manager, Dictionary Manager, Translation Workspace theo cùng dữ liệu state.
- `UI-003`: Dictionary Manager phải tách được hot-path summary và cold-path details.
- `UI-004`: Translation Workspace phải hiển thị ambiguity trail, fallback level và candidate explanations.
- `UI-005`: QA Viewer phải mở được violation theo chapter/segment và link ngược về draft.
- `UI-006`: Candidate Review phải duyệt được `candidate_entries`, `candidate_rules`, low-confidence TM suggestions.

### 16.6 Tiêu chí nghiệm thu

- App khởi động được.
- Sidecar gọi được Python engine.
- Chạy được end-to-end một project mẫu.
- Có build Windows dùng được.

### 16.7 Ước lượng

- 8 đến 10 session.

## 17. Parser, syntax transfer và learning nâng cao

Phần nghiên cứu trong tài liệu cũ về:

- CRF morphological analyzer
- dependency parser
- graph-based syntax transfer
- HMM-Viterbi Pinyin disambiguation
- automatic transfer rule induction
- dynamic suffix array

vẫn là hướng phát triển hợp lệ, nhưng không nên chặn tiến độ của pipeline cơ bản. Cách triển khai hợp lý:

- giai đoạn 1: heuristic và deterministic baseline;
- giai đoạn 2: statistical enhancement trên mô-đun đã chạy thật;
- giai đoạn 3: chỉ nâng cấp mô-đun nào chứng minh được lợi ích trên corpus thực.

## 18. Mốc nghiệm thu cấp dự án

### Milestone A: Baseline ổn định

- Phase 00 hoàn tất
- Phase 01 đóng phase
- full test Python pass

### Milestone B: Pipeline tiền dịch chạy thật

- Phase 02 hoàn tất
- có thể import, split, scan, generate config cho project mới

### Milestone C: Dịch chapter đầu tiên end-to-end

- Phase 03 và Phase 04 đạt baseline
- dịch được một chapter thật bằng pipeline Python

### Milestone D: Hậu kiểm và ghi nhớ dự án

- Phase 05 và Phase 06 hoàn tất
- có QA report và resume project

### Milestone E: Mở rộng hệ và UI

- Phase 07 baseline xong
- Phase 08 có desktop workflow dùng được

## 19. Ma trận tiến độ đề xuất

| Phase | Tên | Trạng thái đề xuất | Tiến độ ước lượng |
| --- | --- | --- | --- |
| 00 | Alignment & Stabilization | Done | 100% |
| 01 | Foundation Closeout | Done | 100% |
| 02 | Pre-Translation Pipeline | Pending | 5% |
| 03 | EAPEE | Pending | 0% |
| 04 | RBMT Core | In Progress | 15% |
| 05 | QA Engine | Pending | 0% |
| 06 | State Management & TM | Pending | 5% |
| 07 | EN-VI Engine | Pending | 0% |
| 08 | Desktop UI | Pending | 0% |

## 20. Rủi ro chính

- Repo đang có hai hướng implementation song song, dễ gây phân tán công sức.
- Enhanced plan cũ dùng ngôn ngữ dễ bị hiểu là đã triển khai xong phần nâng cao.
- Một số yêu cầu nâng cao đang ở mức nghiên cứu, chưa có corpus và benchmark để xác thực.
- Dữ liệu nguồn từ Quick Translator có thể chứa bất nhất, ảnh hưởng migration và compile.
- Nếu mở UI quá sớm, backend contract sẽ thay đổi nhiều lần.

## 21. Backlog ưu tiên ngay sau khi ban hành plan

1. Sửa lỗi parser Markdown table và xanh toàn bộ test Python.
2. Cập nhật `project_progress.json` theo bảng tiến độ đề xuất.
3. Tách production core và prototype JS về mặt tài liệu.
4. Hoàn tất benchmark + rebuild flow cho Phase 01.
5. Nạp thêm `Babylon.txt` và `Mark.txt` theo đúng vai trò `reference_en` và `normalization_rules`.
6. Thiết kế parser metadata-rich cho `LacViet.txt` và refactor `ThieuChuu.txt`.
7. Chạy phân tích coverage để quyết định thu gọn hoặc loại khỏi fast path lớp `PhienAm`.
8. Bắt đầu Phase 02 với `document_importer.py`, `chapter_splitter.py`, `structure_preserver.py`.
9. Sau khi Phase 02 có baseline, mở `rbmt_translator.py` cho vertical slice đầu tiên.

## 22. Tiêu chuẩn cập nhật tiến độ từ nay

Mỗi phase chỉ được chuyển sang `Done` khi đáp ứng đủ 4 điều kiện:

- có artifact thật trong repo;
- có test hoặc benchmark tương ứng;
- có input/output sample kiểm chứng được;
- đã cập nhật tracker và tài liệu.

Mỗi khi kết thúc một session phát triển, cần cập nhật tối thiểu:

- trạng thái phase;
- % tiến độ;
- blockers;
- file chính đã thêm/sửa;
- kết quả test.

## 23. Kết luận

Kế hoạch mới chuyển trọng tâm từ "mô tả hệ thống lý tưởng" sang "lộ trình triển khai thực tế". Dự án hiện không ở mức bắt đầu từ số 0, nhưng cũng chưa sẵn sàng để tuyên bố đã có enhanced translation system hoàn chỉnh. Cách làm đúng là:

- đóng phần nền móng đang có;
- dựng vertical slice ZH-VI chạy thật;
- sau đó mới mở rộng sang cú pháp nâng cao, học tăng cường và desktop UI.

Đây là tài liệu kế hoạch chính để tiếp tục phát triển từ thời điểm 2026-04-15.
