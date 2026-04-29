# Báo cáo thay thế JavaScript bằng Python và kiểm tra pipeline

Ngày tạo: 2026-04-28

## Phạm vi

Báo cáo này ghi lại lần audit và triển khai hiện tại cho các hạng mục:

- Thay thế các module JavaScript legacy bằng Python.
- Bổ sung bộ lọc cụm từ rác do user tự thêm trong quá trình dịch.
- Quét ngữ pháp trên thư mục `Template Book` và cải thiện thuật toán chuyển đổi ngữ pháp.
- Gia cố thuật toán phân tích tên riêng để giảm nhận diện sai.
- Việt hóa các đầu mục UI và build lại native app.

## Audit JavaScript legacy

Lệnh `rg --files -g "*.js" -g "*.mjs" -g "*.cjs"` không còn trả về file JavaScript source trong cây source pipeline đang hoạt động. Các file JS legacy ở root và trong pipeline đã được loại bỏ:

- `index.js`, `test_basic.js`, `test_comprehensive.js`, root `package.json`
- `src/parser/morphological_analyzer.js`
- `src/parser/dependency_parser.js`
- `src/rules/syntax_transfer_rules.js`
- `src/learning/translation_memory.js`
- `src/learning/rule_induction_engine.js`
- `src/learning/sliding_context_manager.js`
- `src/preprocessor/structure_preserver.js`
- `src/preprocessor/traditional_to_simplified.js`
- `src/preprocessor/pinyin_processor.js`

Các module Python thay thế hiện tại:

| Khu vực legacy | Module Python thay thế | Cách hoạt động trong pipeline |
|---|---|---|
| Morphological analyzer | `src/parser/morphological_analyzer.py` | Được gọi trong `PreTranslationPipeline._build_syntax_analysis()` |
| Dependency parser | `src/parser/dependency_parser.py` | Ghi artifact `working/segments/syntax_analysis.json` |
| Syntax transfer rules | `src/rules/syntax_transfer_rules.py` | Tạo artifact kiểm tra syntax-transfer, nằm ngoài bước decode RBMT cuối |
| Learning TM compatibility | `src/learning/translation_memory.py` | Dùng cho test compatibility và `src/drduc_translator.py` |
| Rule induction | `src/learning/rule_induction_engine.py` | Hỗ trợ feedback của Translator Learning Coach |
| Sliding context | `src/learning/sliding_context_manager.py` | Dùng cho test context/learning compatibility |
| Structure preserve | `src/preprocessor/structure_preserver.py` | Wrapper tới `src/engine/structure_preserver.py` |
| Traditional conversion | `src/preprocessor/traditional_to_simplified.py` | Wrapper tới `src/engine/traditional_to_simplified.py` |
| Pinyin processor | `src/preprocessor/pinyin_processor.py` | Wrapper tới `src/engine/pinyin_processor.py` |

Kiểm chứng:

- `tests/test_python_js_replacements.py`: pass.
- `tests/test_phase2_pipeline.py`: pass.
- Bước import Phase 02 ghi `working/segments/syntax_analysis.json`, xác nhận đường parser/syntax Python đang hoạt động trong pre-translation pipeline.

## Lọc cụm từ rác

Đã thêm `src/engine/junk_phrase_filter.py` và tích hợp vào `RBMTTranslator`.

Cách chạy trong pipeline:

- Bộ lọc phía source chạy sau bước preserve structure, chuyển giản thể và resolve pinyin, trước khi tách câu và lookup Translation Memory.
- Bộ lọc phía target chạy sau bước normalize tiếng Việt để loại bỏ phần rác đã lọt sang output.
- Trace dùng `fallback_level="junk_phrase_filter"` và stage `junk_filter`.
- Các key config được hỗ trợ: `ignored_phrases`, `junk_phrases`, `user_noise_phrases`, cùng các key tương ứng bên trong `translation_filters`.

Workflow cho user:

- UI hỗ trợ entity type `junk_phrase`.
- `upsert_project_entity` lưu `junk_phrase` vào `ignored_phrases` trong `translation_config.json`.
- `junk_phrase` không sync vào `locked_entities`.
- Xóa một entity hoặc xóa nhiều entity cũng xóa các entry junk phrase tương ứng trong config.

Kiểm chứng:

- `tests/test_junk_phrase_filter.py`: pass.
- Nhóm regression Python liên quan: 52 test pass.

## Quét ngữ pháp

Lần quét full-corpus không giới hạn ban đầu timeout sau 3600 giây. Scanner đã được tối ưu để khi dùng `max_bytes_per_file`, chương trình chỉ đọc đúng byte window cần thiết thay vì đọc toàn bộ các file nhiều MB trước rồi mới cắt.

Lần quét bounded trên toàn bộ sách đã hoàn tất:

- Thư mục nguồn: `D:\Converter by DrDuc\Template Book`
- Số file: 90
- Giới hạn đọc: `--max-bytes-per-file 750000`
- Output: `reports/grammar_learning/template_book_all_books_sampled_after_rules/grammar_learning_report.json`

Sau khi bổ sung rule:

- Sources: 90
- Chapters: 2403
- Sentences: 192664
- Clauses: 473737
- Source chars sampled: 30657078
- Nhóm rule đã biết match được: 47
- Tổng known matches: 37016
- Chênh lệch so với trước khi bổ sung: +18 nhóm rule, +6194 matches

Top known matches sau khi bổ sung:

- `jiang_construction`: 8680
- `passive_bei`: 7725
- `ba_construction`: 3387
- `concession_suiran_danshi`: 2669
- `marker_shenzhi`: 1753
- `marker_guanyu_duiyu`: 1073
- `condition_ruguo_jiu`: 803
- `marker_zhiyu`: 775
- `progressive_yue_yue`: 743

Các candidate tần suất cao còn cần review:

- `竟然`: marker bất ngờ.
- `毕竟`: marker lập luận/nguyên do.
- `倒也`, `竟是`, `反倒`.
- Các candidate marker/clause còn lại cho `由于`, `甚至`, `否则`, `至于`, `与其`, `对于`, `反而`, `未必`.

Các mục còn lại được giữ trong hàng đợi review của Translation Coach vì chúng cần quyết định theo ngữ cảnh và style, không nên ép vào một rule chuyển đổi cố định.

## Cải thiện grammar transfer

Đã cập nhật `src/grammar/transfer_engine.py` và known patterns của scanner cho các cấu trúc:

- `与其...不如...`
- `宁可/宁愿...也不/也要...`
- `既...又...`
- `越...越...`
- `再怎么...也/都...`
- `之所以...是因为...`
- `只有...才...`
- `倘若/假如/若是...`
- `免得/以免...`
- `由于...因此/因而/所以...`
- Marker transfer: `何况`, `更何况`, `反而`, `乃至`, `甚至`, `并非`, `未必`, `何尝`, `与此同时`, `不至于`, `否则`, `因此`, `因而`, `由于`

Kiểm chứng:

- `tests/test_grammar_learning_scanner.py`: pass.
- `tests/test_grammar_transfer_pack.py`: pass.

## Gia cố thuật toán tên riêng

Đã cập nhật `src/pipeline/entity_scanner.py` để loại bỏ các cụm thông dụng không phải tên người nhưng có hình thái giống tên, ví dụ `王道`, `天道`, `系统`, `任务`, `灵气`, `天下`. Đồng thời vẫn giữ khả năng phát hiện tên thật lặp lại như `林动` và tên có ngữ cảnh mạnh như `夏天骐`.

Kiểm chứng:

- Các regression hiện có của entity scanner đều pass.
- Đã thêm regression mới: cụm yếu lặp lại `王道` bị loại, trong khi `夏天骐` vẫn được nhận diện.

## UI và native app

Đã cập nhật các đầu mục và menu cấp cao sang tiếng Việt:

- Label top bar: `Tổng quan`, `Từ điển`, `Workspace dịch`, `Coach dịch`, `Pipeline`, `Cài đặt`.
- Các heading chính trong Dashboard, Workspace, Coach, Pipeline, Settings và Dictionary đã được Việt hóa.
- Top bar luôn fixed khi scroll và đã được thu gọn để tránh overflow ngang.
- `junk_phrase` đã có trong danh sách entity type.
- Python sidecar được chạy ẩn trên Windows qua Tauri `CREATE_NO_WINDOW`.

Kiểm chứng:

- `npm run build`: pass.
- `npm run tauri:build`: pass.
- File app đã build: `D:\Converter by DrDuc\desktop\src-tauri\target\release\drduc-translator-desktop.exe`

## Tổng kết test

Đã pass:

- `python -m pytest tests\test_python_js_replacements.py tests\test_phase2_pipeline.py tests\test_grammar_learning_scanner.py tests\test_junk_phrase_filter.py tests\test_grammar_transfer_pack.py tests\test_translation_regressions.py -q`
- Kết quả: 52 test pass.

Build:

- `npm run build`: pass.
- `npm run tauri:build`: pass.
