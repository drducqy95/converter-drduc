# Báo Cáo Phân Tích: drducqy95/converter-drduc

> **Ngày phân tích:** 29/04/2026
> **Nguồn:** https://github.com/drducqy95/converter-drduc
> **Mục tiêu:** Phần mềm dịch thuật Non-LLM: ZH → VI, EN → VI
> **Công nghệ chính:** Python (RBMT, Trie, SQLite), Tauri + React (Desktop UI)

---

## 1. Tổng Quan Dự Án

Converter by DrDuc là một workspace dịch thuật quy mô lớn với mục tiêu tham vọng: xây dựng hệ thống dịch Trung–Việt và Anh–Việt **hoàn toàn không dùng LLM**, dựa trên:

- Trie đa trọng số (5 tầng ưu tiên)
- Rule-Based Machine Translation (RBMT)
- LuatNhan grammar rules
- Emotion-Aware Pronoun & Expression Engine (EAPEE)
- SQLite Translation Memory
- Desktop App: Tauri + React

Theo README, tính đến thời điểm phân tích:
- **170 test cases passed** (`python -m pytest`)
- **Vite production build thành công** (`cd desktop && npm run build`)
- Triển khai từ Phase 00 đến Phase 08, đang ở giai đoạn "v23.0 core hardening"

---

## 2. Phân Tích Cấu Trúc Project

### 2.1 Cấu Trúc Thư Mục (Nhận Diện Được)

```
converter-drduc/
├── .agents/workflows/         ← Workflow agent definitions
├── src/
│   ├── core/                  ← Trie engine, dictionary compiler, LuatNhan
│   ├── engine/                ← RBMT, number converter, pronoun resolver
│   ├── pipeline/              ← Document import, chapter split, entity scan
│   ├── eapee/                 ← Emotion detector, pronoun engine, expression bank
│   ├── qa/                    ← QA checks, report generator
│   ├── state/                 ← Project manager, TM, Obsidian sync
│   ├── grammar/               ← v23 clause segmentation, relation detection
│   ├── en_vi/                 ← EN→VI translator
│   └── ui/                    ← Sidecar command protocol
├── desktop/                   ← Tauri + React shell
├── scripts/
│   ├── runners/               ← Entry points
│   ├── dev/                   ← Dev utilities
│   └── migration/             ← Migration utilities
├── data/                      ← Dictionaries, compiled assets
├── tests/                     ← Test suite
├── plans/                     ← Planning documents
├── docs/                      ← Documentation, architecture status
├── Name project/              ← Name dictionaries
└── [root level files]         ← Rất nhiều file debug, patch, script lẻ
```

### 2.2 Thiếu Sót Cấu Trúc Project

#### 🔴 Vấn đề Nghiêm Trọng

**1. Root level ô nhiễm (Root Pollution)**

Có hàng chục file không thuộc về root:
```
clean_dict.py, debug_regex.py, debug_rewriter.py, debug_zh_rewriter.py,
patch_nc2.py, patch_nc5.py, run_coach_feedback.py, run_full_pipeline.py,
run_prepare.py, run_pretranslation.py, run_translate_ch01.py,
run_translate_ch02.py, test_basic.js, test_comprehensive.js, test_import.py,
all_global_errors.jsonl, cedict_seeding_debug.txt, diagnose_results.json,
pos_db_audit.json, pos_diagnostic_results.json, pos_rewrite_test_results.json,
trie_verification.json, nlm_rules.txt, fixpos.md, ...
```

- **Debug files** (debug_*.py, cedict_seeding_debug.txt) nên xóa hoặc chuyển vào `scripts/dev/`
- **Patch files** (patch_nc2.py, patch_nc5.py) nên chuyển vào `scripts/migration/`
- **Runner scripts** (run_*.py) nên chuyển vào `scripts/runners/`
- **JSON diagnostic** (diagnose_results.json, pos_db_audit.json...) nên chuyển vào `artifacts/` hoặc xóa
- **Test files JavaScript** (test_basic.js, test_comprehensive.js) nằm lạc ở root, nên chuyển vào `tests/js/`

**2. File `.resolved` không được quản lý đúng cách**

```
implementation_plan.md.resolved
implementation_plan22.md.resolved
metadata_migration_plan.md.resolved
pipeline_guidev2.md.resolved
pipeline_guidev3.md.resolved
walkthrough.md.resolved
```

Đây rõ ràng là artifact tạm thời từ quá trình AI-assisted development. Không nên commit các file này vào git. Nên thêm `*.resolved` vào `.gitignore`.

**3. Video file trong repo**

`SVID_20260423_073257_1.mp4` (~video demo) nằm trực tiếp trong repo git. Video không nên lưu trong git — dùng Git LFS hoặc lưu trên YouTube/Google Drive.

**4. Hai JSON config trùng tên**

```
Converter by DrDuc.json   ← Tên có dấu cách, dấu tiếng Anh viết hoa
converter_by_drduc.json   ← Tên snake_case
```

Không rõ file nào là canonical. Mâu thuẫn, gây nhầm lẫn.

**5. Thư mục `Name project` có tên sai convention**

`Name project` (có dấu cách) nên đổi thành `name_project` hoặc `names/` cho nhất quán.

#### 🟡 Vấn đề Trung Bình

**6. Thiếu CHANGELOG.md**

Dự án có nhiều version (v3, v23.0...) nhưng không có changelog. Khó tracking thay đổi theo thời gian.

**7. Thiếu cấu trúc `artifacts/state/` được định nghĩa rõ**

README đề cập `artifacts/state/` (ignored by git) nhưng không có `.gitkeep` hay hướng dẫn setup cho contributor mới.

**8. Docs phân tán**

Tài liệu nằm ở: `Plan.md`, `UI.md`, `IMPLEMENTATION_SUMMARY.md`, `fixpos.md`, `enhanced_translation_system_plan.md`, `notebook_rules.md`, `docs/`... Không có một entry point tài liệu nhất quán.

**9. Thiếu Makefile / Task Runner**

Không có `Makefile`, `justfile`, hay `taskfile.yml`. Developer mới phải đọc README để biết cách chạy từng lệnh.

---

## 3. Phân Tích Thuật Toán

### 3.1 Trie Engine & Dictionary Pipeline

**Điểm mạnh:**
- 5 tầng priority (P1–P5) rõ ràng, ưu tiên project-specific > global
- Bulk MD format thông minh cho 728K entries VietPhrase
- Hot/cold storage (SQLite cache) để tốc độ loading

**Thiếu sót thuật toán:**

**T1: Longest-Prefix Match có thể gây "greedy trap"**

Thuật toán dual-pointer longest-prefix match theo thiết kế sẽ luôn chọn chuỗi dài nhất khớp. Nhưng trong tiếng Trung, chuỗi dài nhất không luôn là đúng nhất về mặt ngữ nghĩa:

```
Ví dụ: "修为境界突破"
- Greedy match: "修为境界" (4 ký tự, P2) → "tu vi cảnh giới"
- Đúng hơn:     "修为" + "境界" + "突破" (3 mảnh riêng)
```

**Khắc phục:** Thêm cơ chế **Viterbi path scoring** — chấm điểm toàn bộ câu (tổng log-probability của các mảnh) thay vì greedy ở từng bước. Đây là approach của jieba.

**T2: One-Mean mode quá đơn giản**

`split(";")[0]` để lấy nghĩa đầu tiên của từ đa nghĩa không phân biệt ngữ cảnh. Nghĩa số 1 trong dict không luôn là nghĩa phù hợp nhất.

```
Ví dụ: "打" → "đánh;bật;gọi;làm;đánh;..."
Trong câu "打电话" → nên chọn "gọi", không phải "đánh"
```

**Khắc phục:** Thêm **context window bigram check**: nếu từ tiếp theo là một trong các trigger token đã biết (phone, call terms...) thì ưu tiên nghĩa thứ N thay vì nghĩa đầu.

**T3: Trie cache invalidation chưa rõ**

Theo thiết kế, dictionary có thể hot-reload khi file thay đổi. Nhưng không có cơ chế timestamp hoặc hash check để phát hiện khi nào SQLite cache đã stale so với markdown sources.

**Khắc phục:** Lưu `last_modified` hash của tất cả `.md` source vào SQLite metadata table. Khi start, so sánh hash → rebuild nếu cần.

---

### 3.2 Emotion Detection Engine (EAPEE)

**Điểm mạnh:**
- Keyword-based + dialogue verb-based detection là hướng đúng cho Non-LLM
- Emotion State Machine với decay rules là ý tưởng tốt
- Ma trận 4 chiều (Genre × Relationship × Emotion × Gender) rất chi tiết

**Thiếu sót thuật toán:**

**T4: Emotion Detection không xử lý negation**

Từ phủ định đảo ngược cảm xúc nhưng keyword scan đơn giản không phát hiện được:

```
"没有愤怒" (không tức giận) → scan thấy "愤怒" → sai lầm detect angry
"并非不恨你" (không phải không ghét ngươi) → double negation
```

**Khắc phục:** Thêm **negation scope detection**: khi gặp 没有/非/不/并非 trước emotion keyword trong window 3 từ, giảm score hoặc đảo ngược cực tính.

**T5: Emotion inertia (decay) theo số câu, không theo thời gian ngữ cảnh**

Decay rule "angry kéo dài 5 câu" có thể sai trong nhiều tình huống:
- 5 câu mô tả cảnh vật (không liên quan cảm xúc) cũng làm decay
- Nhân vật vẫn đang giận nhưng engine reset vì hết 5 câu

**Khắc phục:** Decay chỉ khi gặp câu có **content liên quan đến nhân vật đó** (speaker detection), không decay với câu miêu tả cảnh vật hoặc câu của nhân vật khác.

**T6: Speaker/Listener detection dễ sai với implicit dialogue**

Pattern "X说/X道" chỉ hoạt động với **explicit attribution**. Tiếng Trung thường có chuỗi dialogue dài không có attribution:

```
"你在哪里？"
"就在这里。"
"快来。"
"好的。"
```

4 câu trên không có "X说", engine không biết ai đang nói.

**Khắc phục:** Thêm **Dialogue Turn Alternation**: khi không có explicit speaker, giả định speaker luân phiên giữa 2 active characters gần nhất.

---

### 3.3 Pronoun Resolution

**Thiếu sót:**

**T7: Ma trận xưng hô chỉ xử lý song tuyến (A↔B), không xử lý đa chiều**

Khi có 3+ nhân vật trong scene cùng nói chuyện, ma trận 2 chiều không đủ:

```
A nói với B (ta/ngươi), nhưng đang nói về C (hắn/y)
B nói với C (ta/ngươi), nhưng đề cập A (lão tiền bối đó)
```

Đại từ ngôi 3 (hắn/nàng/y/thị) cần được resolve dựa trên relationship giữa speaker và person-being-referred-to, không chỉ speaker–listener.

**Khắc phục:** Thêm **third-person pronoun resolution layer**: khi gặp 他/她/它, tra relationship graph của speaker với entity đang được nhắc đến.

**T8: Identity pronoun override thiếu chapter-scoping**

Nhân vật có thể là hoàng đế trong chương 1-100, thoái vị từ chương 101. Nhưng identity pronoun `trẫm` có thể vẫn được áp dụng sau thoái vị nếu không có event trigger.

**Khắc phục:** Identity pronouns trong character MD nên có `valid_from_chapter` và `valid_to_chapter` fields.

---

### 3.4 Pipeline Architecture

**T9: Pipeline không có rollback mechanism**

Nếu bước 4 (Trie RBMT) thất bại giữa chừng của một chapter, toàn bộ output của chapter đó bị mất. Không có checkpoint per-paragraph.

**Khắc phục:** Áp dụng pattern **write-ahead log (WAL)**: sau mỗi paragraph dịch xong, append vào một `.partial` file. Nếu crash, resume từ paragraph cuối cùng thành công.

**T10: Entity scanner dùng frequency threshold cứng**

Threshold "xuất hiện ≥ 3 lần" để nhận diện tên nhân vật có thể bỏ sót nhân vật quan trọng xuất hiện ít (antagonist chỉ xuất hiện 1-2 lần ở phần đầu), hoặc nhận diện nhầm từ thông dụng.

**Khắc phục:** Kết hợp thêm **positional weighting**: từ xuất hiện sau "对...说" hoặc trước "道/说" được tăng score dù tần suất thấp. Từ trong tiêu đề chương được tăng score x3.

---

### 3.5 LuatNhan Engine

**T11: Pattern `{0}` không phân biệt loại entity**

Template như `"与{0}说话"` chỉ có 1 placeholder. Nếu câu nguồn có nhiều entity (person, location, item), engine không biết entity nào điền vào `{0}`.

**Khắc phục:** Nâng cấp template syntax sang `{person:0}`, `{location:0}`, `{item:0}` với type annotation. Engine fill theo type-match.

---

### 3.6 EN→VI Translator

**T12: Grammar transfer rules quá đơn giản cho tiếng Anh**

Theo Plan.md, chỉ có các rules cơ bản: adjective position, possessive, plural. Tiếng Anh có nhiều cấu trúc phức tạp hơn:

- Passive voice: "The book was written by him" → "Cuốn sách được viết bởi anh ta"
- Relative clause: "The man who came yesterday" → "Người đàn ông đã đến hôm qua"
- Conditional: "If I were you..." → "Nếu tôi là bạn..."
- Phrasal verbs: "give up", "look into", "come across"

**Khắc phục:** Ưu tiên xây dựng **phrasal verb dictionary** (3000+ entries) và thêm passive voice transformation rule trước. Đây là hai nguồn lỗi phổ biến nhất EN→VI.

---

## 4. Phân Tích Chất Lượng Code & Kiến Trúc

### 4.1 Vấn Đề Kiến Trúc

**A1: Hai runtime layer tồn tại song song (đã được nhận ra, chưa xử lý triệt để)**

README cũ ghi:
> "JavaScript modules under src/preprocessor/, src/parser/... are prototype/reference material"

README mới ghi:
> "Historical JavaScript design material is archived under docs/archive/"

Nhưng thực tế vẫn còn `test_basic.js`, `test_comprehensive.js`, `index.js` ở root — cho thấy layer JavaScript chưa được dọn dẹp hoàn toàn.

**A2: Thiếu Interface / Abstract Base Class cho các engine**

Các module như `trie_engine`, `luat_nhan_engine`, `pronoun_resolver` không có interface contract rõ ràng (Python ABC hoặc Protocol). Điều này khiến:
- Khó mock trong tests
- Khó swap implementation (ví dụ: thay Trie bằng Aho-Corasick)

**Khắc phục:**
```python
# src/core/interfaces.py
from abc import ABC, abstractmethod

class DictionaryEngine(ABC):
    @abstractmethod
    def lookup(self, text: str, context: dict) -> list[Match]: ...

    @abstractmethod
    def reload(self) -> None: ...
```

**A3: Translation Memory chưa có eviction policy**

SQLite TM sẽ tăng kích thước vô hạn theo thời gian. Không có cơ chế:
- TTL (time-to-live) cho các entry ít dùng
- Capacity limit
- Prioritize frequently-accessed segments

**Khắc phục:** Thêm `access_count` và `last_accessed` columns. Implement LRU eviction khi TM vượt ngưỡng cấu hình.

---

### 4.2 Vấn Đề Testing

**A4: Test coverage không rõ ràng**

170 tests pass, nhưng không rõ:
- Coverage % là bao nhiêu?
- Có integration test không (full pipeline test)?
- Tests có cover edge cases của EAPEE không?

**Khắc phục:** Thêm `coverage.py` vào CI, đặt target ≥ 80% cho `src/core/` và `src/engine/`.

**A5: Không có CI/CD pipeline**

Không có GitHub Actions workflow. Mỗi lần push, không có automated test chạy.

**Khắc phục:** Thêm `.github/workflows/test.yml`:
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: python -m pytest --cov=src --cov-report=xml
```

---

### 4.3 Vấn Đề Bảo Mật & Độ Tin Cậy

**A6: `all_global_errors.jsonl` committed vào git**

File này chứa error logs từ quá trình development. Có thể leak thông tin về đường dẫn hệ thống (absolute paths), stack traces, hoặc data nhạy cảm.

**Khắc phục:** Thêm vào `.gitignore`:
```
*.jsonl
artifacts/
*_debug.txt
diagnose_*.json
pos_*.json
trie_verification.json
```

**A7: Không có input validation ở pipeline entry points**

Nếu user input một file source bị malformed (encoding lạ, ký tự NULL, rất dài), pipeline có thể crash hoặc produce garbage output không có thông báo rõ ràng.

**Khắc phục:** Thêm validation layer ở `document_importer.py`: kiểm tra encoding, max file size, ký tự không hợp lệ, trả về structured error thay vì raise exception không được handle.

---

## 5. Tổng Hợp: Bảng Ưu Tiên Khắc Phục

| # | Vấn đề | Mức độ | Nỗ lực | Ưu tiên |
|---|--------|--------|--------|---------|
| 1 | Root directory ô nhiễm (50+ file lạc) | 🔴 Cao | Thấp | **P0** |
| 2 | CI/CD pipeline chưa có | 🔴 Cao | Thấp | **P0** |
| 3 | `*.resolved`, `*.jsonl`, video trong git | 🔴 Cao | Thấp | **P0** |
| 4 | Trie: Greedy trap, cần Viterbi scoring | 🔴 Cao | Cao | **P1** |
| 5 | Emotion: Thiếu negation detection | 🟡 TB | Trung | **P1** |
| 6 | Speaker detection với implicit dialogue | 🟡 TB | Trung | **P1** |
| 7 | Pipeline thiếu rollback/checkpoint | 🟡 TB | Trung | **P1** |
| 8 | TM thiếu eviction policy | 🟡 TB | Trung | **P2** |
| 9 | One-Mean mode cần context-aware | 🟡 TB | Cao | **P2** |
| 10 | Third-person pronoun resolution | 🟡 TB | Cao | **P2** |
| 11 | Trie cache invalidation chưa đủ | 🟡 TB | Trung | **P2** |
| 12 | Identity pronoun cần chapter-scoping | 🟢 Thấp | Thấp | **P3** |
| 13 | LuatNhan template cần typed placeholder | 🟢 Thấp | Trung | **P3** |
| 14 | Entity scanner: positional weighting | 🟢 Thấp | Trung | **P3** |
| 15 | EN→VI: Phrasal verbs & passive voice | 🟢 Thấp | Cao | **P3** |
| 16 | Thiếu ABC/Interface contracts | 🟢 Thấp | Thấp | **P3** |
| 17 | Input validation ở entry points | 🟢 Thấp | Thấp | **P3** |

---

## 6. Đánh Giá Tổng Thể

### Điểm Mạnh

- **Tư duy thiết kế xuất sắc**: Phân tách rõ ràng hot/cold storage, 5-tier priority Trie, EAPEE 4D matrix đều là những ý tưởng kỹ thuật tốt.
- **Tài liệu kỹ lưỡng**: Plan.md và README cực kỳ chi tiết, hiếm thấy ở project cá nhân.
- **Domain knowledge sâu**: Hệ thống xưng hô, cảm xúc, văn hoá trong truyện dịch được mô hình hóa rất sát thực tế.
- **Test foundation**: 170 tests là nền tảng tốt.

### Điểm Yếu Chính

- **Quản lý repo chưa nghiêm túc**: Quá nhiều file debug, patch, diagnostic bị commit lên git.
- **Thuật toán core còn thiếu sót nghiêm trọng**: Trie greedy trap và emotion negation detection là hai bug có thể ảnh hưởng lớn đến chất lượng dịch.
- **Thiếu DevOps cơ bản**: Không có CI, không có gitignore tốt, không có Makefile.

### Kết Luận

Đây là một project với **tầm nhìn đúng và chi tiết**, nhưng đang ở giai đoạn "grow fast, clean later" — điều hoàn toàn bình thường với dự án cá nhân. Ưu tiên trước mắt nên là: **dọn dẹp repo (P0)** và **vá hai thuật toán core (Trie Viterbi + Negation Detection)** trước khi mở rộng thêm tính năng mới.

---

*Báo cáo được tạo bởi phân tích tự động kết hợp đánh giá kỹ thuật — 29/04/2026*
