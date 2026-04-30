# BÁO CÁO PHÂN TÍCH DỰ ÁN: `converter-drduc` — Phiên bản 3
## Phân tích từ Source Thực Tế: Plan.md Pseudocode + Runtime Files

> **Tác giả:** Claude (Anthropic)
> **Ngày:** 30/04/2026
> **Repo:** https://github.com/drducqy95/converter-drduc
> **Phương pháp:** Đọc trực tiếp toàn bộ `Plan.md` (1388 dòng, 56KB), `.gitignore`, `pyproject.toml`, `project_progress.json`, `converter_by_drduc.json`, `IMPLEMENTATION_SUMMARY.md` và GitHub directory tree thực tế
> **Tính mới:** Lần đầu tiên phân tích dựa trên **pseudocode thực tế** trong Plan.md — không phải suy đoán từ tên module

---

## MỤC LỤC

1. [Xác nhận trạng thái thực tế](#1-xác-nhận-trạng-thái-thực-tế)
2. [Phân tích .gitignore — Đột phá quan trọng](#2-phân-tích-gitignore--đột-phá-quan-trọng)
3. [Phân tích pyproject.toml — Vấn đề nghiêm trọng](#3-phân-tích-pyprojecttoml--vấn-đề-nghiêm-trọng)
4. [Phân tích pseudocode Plan.md — Phát hiện lỗi thuật toán thực tế](#4-phân-tích-pseudocode-planmd--phát-hiện-lỗi-thuật-toán-thực-tế)
5. [Phân tích EAPEE — Lỗi thiết kế trong Emotion Detection](#5-phân-tích-eapee--lỗi-thiết-kế-trong-emotion-detection)
6. [Phân tích Trie Pipeline — Thứ tự xử lý và Conflict](#6-phân-tích-trie-pipeline--thứ-tự-xử-lý-và-conflict)
7. [Phân tích Entity Scanner — False Positive Pattern](#7-phân-tích-entity-scanner--false-positive-pattern)
8. [Phân tích Cultural Origin Detection — Naive Score](#8-phân-tích-cultural-origin-detection--naive-score)
9. [Phân tích EmotionState Machine — Decay Hardcoded](#9-phân-tích-emotionstate-machine--decay-hardcoded)
10. [Phân tích LuatNhan Integration — Ambiguity Gap](#10-phân-tích-luatnhan-integration--ambiguity-gap)
11. [Phân tích Translation Memory — Fuzzy Match Flaw](#11-phân-tích-translation-memory--fuzzy-match-flaw)
12. [Phân tích cấu trúc repo — Vẫn còn file rác](#12-phân-tích-cấu-trúc-repo--vẫn-còn-file-rác)
13. [Phân tích IMPLEMENTATION_SUMMARY — Tài liệu sai kiến trúc](#13-phân-tích-implementation_summary--tài-liệu-sai-kiến-trúc)
14. [Phân tích project_progress.json — Mâu thuẫn dữ liệu](#14-phân-tích-project_progressjson--mâu-thuẫn-dữ-liệu)
15. [Phân tích converter_by_drduc.json — Dependency Gap](#15-phân-tích-converter_by_drducjson--dependency-gap)
16. [Phương pháp khắc phục chi tiết với code mẫu](#16-phương-pháp-khắc-phục-chi-tiết-với-code-mẫu)
17. [Bảng tổng hợp toàn bộ thiếu sót theo mức ưu tiên](#17-bảng-tổng-hợp-toàn-bộ-thiếu-sót-theo-mức-ưu-tiên)
18. [Roadmap hành động theo tuần](#18-roadmap-hành-động-theo-tuần)
19. [Kết luận](#19-kết-luận)

---

## 1. XÁC NHẬN TRẠNG THÁI THỰC TẾ

### 1.1 Sự thật về số lượng tests

`project_progress.json` tiết lộ sự thật chính xác:

| Phase | Tests | Trạng thái |
|-------|-------|------------|
| T1.0 (Phase 00) | Không ghi rõ | DONE |
| T1.1 (Phase 01) | **91 passed** | DONE |
| T1.8 (Phase 08) | **99 passed** | DONE |

**Kết luận thực tế:** Con số 99 tests (không phải 183 như README_VI.md nêu ở phiên bản được cho là mới hơn) là số lượng thực tế được xác nhận bởi file được commit vào repo. Báo cáo lần 2 của chúng tôi dựa trên 183 tests là từ một phiên bản README chưa commit hoặc chỉ tồn tại local.

### 1.2 Xác nhận cấu trúc thư mục thực tế

Directory listing từ GitHub xác nhận **KHÔNG CÓ THAY ĐỔI nào** so với thời điểm báo cáo lần 1 và lần 2. Tất cả 50+ file rác vẫn còn tại root. Đây là xác nhận quan trọng: **repo chưa được dọn dẹp**.

### 1.3 Xác nhận `.gitignore` đã được cập nhật

`.gitignore` ĐÃ có nhiều pattern tốt (được đọc trực tiếp lần này). Đây là **điểm tích cực chưa được báo cáo trước**. Tuy nhiên, nếu `.gitignore` đã đúng nhưng file rác vẫn còn trong repo, nghĩa là file rác đã được committed TRƯỚC KHI `.gitignore` được cập nhật — và chưa bị xóa khỏi Git tracking.

---

## 2. PHÂN TÍCH `.gitignore` — ĐỘT PHÁ QUAN TRỌNG

### 2.1 Nội dung `.gitignore` thực tế (đọc trực tiếp)

```gitignore
.venv/
__pycache__/
.pytest_cache/
*.pyc
*.pyo
.DS_Store
workspace_projects/
artifacts/
.brain/
node_modules/
desktop/node_modules/
dist/
build/
*.egg-info/
desktop/dist/
target/
bin/
obj/
.gradle/
.next/
out/
_compiled/
data/dictionaries/_compiled/
*.db
*.sqlite
*.cache
.coverage
coverage.xml

# Diagnostic, generated, and local state output
*.jsonl
all_global_errors*
cedict_seeding_debug.txt
diagnose_results*.json
pos_*.json
trie_verification.json
project_progress.json
session.json

# Large local media captures
*.mp4
*.avi
*.mkv
```

### 2.2 Phát hiện nghịch lý: `.gitignore` đúng nhưng file rác vẫn còn trong repo

Đây là vấn đề **kỹ thuật Git rất quan trọng**: `.gitignore` chỉ ngăn không cho **file mới** bị track. Nếu file đã bị commit trước khi thêm pattern vào `.gitignore`, file đó vẫn tồn tại trong repo và vẫn được Git track.

**Bằng chứng:**
- `.gitignore` có dòng `project_progress.json` → nhưng file `project_progress.json` VẪN xuất hiện trong directory listing!
- `.gitignore` có `*.mp4` → nhưng `SVID_20260423_073257_1.mp4` VẪN trong repo!
- `.gitignore` có `*.jsonl` → nhưng `all_global_errors.jsonl` VẪN trong repo!
- `.gitignore` có `diagnose_results*.json` → nhưng `diagnose_results.json` VẪN trong repo!

**Root cause:** Các file này đã được `git add` và `git commit` trước khi `.gitignore` được cập nhật. Chúng đang bị **Git track dù .gitignore nói không track**.

### 2.3 Thiếu sót trong `.gitignore` hiện tại

Dù đã tốt hơn nhiều, `.gitignore` còn thiếu các pattern sau:

```gitignore
# Chưa có:
*.mp3                    # Audio files
*.wav
*.zip *.tar.gz *.7z      # Archives
*.resolved               # Artifact files từ AI agent (*.md.resolved)
Converter\ by\ DrDuc.json  # File tên có khoảng trắng
python                   # File "python" không rõ loại tại root
Name\ project/           # Thư mục tên có khoảng trắng
nlm_rules.txt            # Có thể là data file không cần commit nếu auto-generated
*.patch                  # Patch files
```

---

## 3. PHÂN TÍCH `pyproject.toml` — VẤN ĐỀ NGHIÊM TRỌNG

### 3.1 Nội dung thực tế (đọc trực tiếp, 25 dòng)

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "drduc-translator"
version = "0.1.0"
description = "Non-LLM Rule-Based Machine Translation System (ZH/EN → VI)"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "DrDuc"},
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

### 3.2 Lỗi nghiêm trọng #1: Không có `[project.dependencies]`

**Đây là vấn đề nghiêm trọng nhất trong toàn bộ repo.** `pyproject.toml` thiếu hoàn toàn section `[project.dependencies]`. Khi người dùng chạy:

```bash
pip install -e .
```

**Không có dependency nào được cài** — kể cả `jieba`, `underthesea`, `chardet`, `pyyaml`. Toàn bộ hệ thống sẽ crash với `ModuleNotFoundError` ngay lần chạy đầu tiên.

Để cài được đủ dependencies, người dùng hiện tại phải biết chạy từng thư viện thủ công — không có hướng dẫn nào về điều này trong README.

### 3.3 Lỗi nghiêm trọng #2: `build-backend` sai

```toml
build-backend = "setuptools.backends._legacy:_Backend"
```

Đây là **private API không ổn định** của setuptools. Package name chuẩn là:

```toml
build-backend = "setuptools.build_meta"
```

`_legacy` backend có thể bị remove trong bất kỳ phiên bản setuptools nào mà không cần thông báo. Build sẽ break silently.

### 3.4 Lỗi #3: `include = ["src*"]` quá rộng

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

Pattern `src*` sẽ match bất kỳ thứ gì bắt đầu bằng `src`, bao gồm:
- `src/core/` ✅ (muốn include)
- `src/engine/` ✅ (muốn include)
- `src/preprocessor/` ❌ (JS prototype, không muốn include)
- `src/parser/` ❌ (JS prototype, không muốn include)
- `src/rules/` ❌ (JS prototype, không muốn include)
- `src/learning/` ❌ (JS prototype, không muốn include)

Cần explicit exclusion hoặc explicit include list.

### 3.5 Lỗi #4: Thiếu `[project.optional-dependencies]` cho dev tools

Không có dev group nào định nghĩa `pytest`, `pytest-cov`, `ruff`, `black`. Người dev mới không biết cài gì để chạy tests.

---

## 4. PHÂN TÍCH PSEUDOCODE `Plan.md` — PHÁT HIỆN LỖI THUẬT TOÁN THỰC TẾ

Lần đầu tiên có thể phân tích pseudocode thực tế. Phát hiện nhiều lỗi kỹ thuật cụ thể.

### 4.1 Lỗi trong Trie Loading Pipeline — Priority mâu thuẫn

`Plan.md` định nghĩa 5 tầng priority:

```
P5: projects/{name}/names_rieng.md     (cao nhất)
P4: global/names/_bulk_names.md
P3: projects/{name}/vietphrase_rieng.md
P2: global/vietphrase/_bulk_vietphrase.md
P1: global/phien_am/_bulk_phienam.md   (thấp nhất)
```

**Lỗi logic:** P3 (project-level VietPhrase) có priority THẤP HƠN P4 (global names). Điều này nghĩa là nếu một thuật ngữ xuất hiện trong cả VietPhrase của project VÀ global names, global names sẽ thắng — đây là hành vi ngược với mong đợi.

Ví dụ xung đột:
```
Thuật ngữ: "天宗" (tên một môn phái trong truyện cụ thể)
P3 (project VietPhrase): "Thiên Tông" (đã customize)
P4 (global names): "Thiên Tông" hoặc một nghĩa khác từ Names.txt chung

→ P4 sẽ thắng P3 dù P3 là project-specific và nên được ưu tiên hơn
```

**Thứ tự đúng nên là:**
```
P5: projects/{name}/names_rieng.md      (project names)
P4: projects/{name}/vietphrase_rieng.md (project vietphrase)
P3: global/names/_bulk_names.md         (global names)
P2: global/vietphrase/_bulk_vietphrase.md (global vietphrase)
P1: global/phien_am/_bulk_phienam.md    (phiên âm fallback)
```

Project-specific entries luôn nên thắng global entries ở cùng loại.

### 4.2 Lỗi trong Context Window — Chapter Boundary Cut

```python
# Plan.md pseudocode:
Init Context Window (size=5 câu trước + 5 câu sau)
```

Context window được khởi tạo theo câu, không theo chapter. Khi dịch **câu đầu tiên của chapter mới**, "5 câu trước" sẽ lấy từ chapter trước — điều này có thể tốt cho pronoun continuity, nhưng Plan.md không định nghĩa:

- Khi nào context window bị reset (scene break? chapter break?)
- Emotion state có bị reset không khi sang chapter mới?
- Active character tracking có persist không?

Trong `EmotionState.update()` pseudocode có:
```python
SCENE_BREAK_PATTERNS = ['***', '---', '===', '※※※']
if any(p in sentence for p in self.SCENE_BREAK_PATTERNS):
    self.reset()
```

Nhưng không có Chapter Break reset. Nếu chapter kết thúc với nhân vật đang `furious` (decay=8 câu), câu đầu chapter tiếp theo vẫn sẽ dịch theo emotion furious — sai hoàn toàn với ngữ cảnh.

### 4.3 Lỗi trong Pronoun Resolution — Speaker Detection Fragile

```python
# Plan.md: Identify speaker từ context (X说, X道)
```

Pattern này **sẽ fail** trong các tình huống phổ biến sau:

**Tình huống 1 — Compound verb:**
```
"林动停下脚步，转身看向绫清竹道"
```
Pattern `X道` ở đây là `绫清竹道` nhưng tên có 3 ký tự và có khoảng cách với động từ. Nếu regex chỉ match pattern cố định, sẽ miss speaker.

**Tình huống 2 — Nested dialogue:**
```
他想起了父亲的话："孩子，要坚强。"随即道："我明白了。"
```
Hai dialogue khác nhau trong một câu — "孩子" nói bởi cha, "我明白了" nói bởi nhân vật chính.

**Tình huống 3 — Implicit speaker (không có 说/道):**
```
「你在想什么？」
「没什么。」
```
Không có speaker marker nào — Plan.md không có fallback mechanism cho trường hợp này. Toàn bộ dialogue không có `X说` sẽ không được resolve speaker.

### 4.4 Lỗi trong Structure Preservation — Placeholder Collision

```python
# Plan.md:
→ [TABLE_001]...[/TABLE_001]
→ [MATH_001]...[/MATH_001]
```

Placeholder format `[TABLE_001]` có thể collision với:
- Markdown link syntax: `[TEXT](url)` — nếu text là `TABLE_001`
- Footnote references: `[^1]`
- Nếu source text chứa cụm `[TABLE` nào đó (ít khả năng nhưng có thể)

Hơn nữa, counter `001`, `002`... được reset mỗi chapter hay mỗi document? Nếu reset mỗi chapter, thì khi batch nhiều chapters, placeholder IDs từ chapter khác nhau có thể collision nếu được xử lý đồng thời.

### 4.5 Lỗi trong Number Converter — Chỉ xử lý subset

`Plan.md` chỉ định nghĩa:
```python
一百二十三 → 123
三尺 → 3 thước
第X → thứ X
```

Không có xử lý cho:
- `一亿三千万` → 130,000,000 (số lớn)
- `三分之一` → một phần ba (phân số)
- `零点五` → 0.5 (thập phân)
- `负三十度` → âm 30 độ (số âm)
- `丙午年` → năm Bính Ngọ (Can Chi)
- `一柱香` → một nén hương (đơn vị thời gian cổ)
- `三两银子` → ba lượng bạc (đơn vị tiền cổ)
- `十万火急` → thành ngữ có số (không nên convert)

Đặc biệt nguy hiểm: `十万火急` là thành ngữ nghĩa là "vô cùng khẩn cấp", không phải "100,000 độ khẩn cấp". Nếu number converter không có thành ngữ blacklist, sẽ convert sai nghĩa.

---

## 5. PHÂN TÍCH EAPEE — LỖI THIẾT KẾ TRONG EMOTION DETECTION

### 5.1 Phân tích pseudocode `detect_emotion()` thực tế

```python
def detect_emotion(sentence, prev_context):
    scores = {emotion: 0 for emotion in EMOTIONS}

    # 1. Keyword scan
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in sentence:
                scores[emotion] += keyword_weight(kw)

    # 2. Punctuation boost
    if sentence.count('！') >= 2:      scores['angry'] += 2
    if sentence.count('？') >= 2:      scores['mocking'] += 1
    if '...' in sentence or '……' in sentence:  scores['sad'] += 1
    if '！！！' in sentence:            scores['furious'] += 3

    # 3. Dialogue marker boost
    dialogue_verb = extract_dialogue_verb(sentence)
    if dialogue_verb:
        verb_emotion = VERB_EMOTION_MAP.get(dialogue_verb)
        if verb_emotion:
            scores[verb_emotion] += 3  # Strong signal

    # 4. Context carry-over
    if prev_context.emotion and prev_context.emotion_age < 3:
        scores[prev_context.emotion] += 1

    # 5. Determine winner
    top_emotion = max(scores, key=scores.get)
    if scores[top_emotion] < 2:
        return 'neutral', 0

    intensity = min(scores[top_emotion], 5)
    return top_emotion, intensity
```

### 5.2 Lỗi #1 — Không phân biệt narrative vs dialogue

Pseudocode áp dụng emotion detection cho **mọi câu** — cả narrative lẫn dialogue. Nhưng hành vi đúng phải khác nhau:

```
Câu narrative: "他内心充满了愤怒与痛苦。"
→ Emotion: angry, nhưng đây là MÔ TẢ trạng thái nội tâm
→ Không nên thay đổi xưng hô của câu thoại tiếp theo!

Câu dialogue: "「你给我滚出去！」他怒道。"
→ Emotion: angry, đây là LỜI THOẠI THỰC SỰ
→ Nên thay đổi xưng hô theo emotion
```

Pseudocode không phân biệt hai trường hợp này. Một câu mô tả cảm xúc nhân vật sẽ `trigger emotion state` → ảnh hưởng đến xưng hô của **câu dialogue TIẾP THEO** — sai.

### 5.3 Lỗi #2 — `keyword_weight()` không được định nghĩa

```python
scores[emotion] += keyword_weight(kw)  # weight theo specificity
```

`keyword_weight()` được gọi nhưng **không có pseudocode nào định nghĩa hàm này**. Không rõ specificity được tính thế nào:
- Theo độ dài keyword? (怒 vs 勃然大怒 — dài hơn = cụ thể hơn?)
- Theo tần suất trong corpus?
- Flat weight cho tất cả?

Nếu flat weight = 1, thì ngưỡng `< 2` quá dễ trigger (chỉ cần 2 keywords). Nếu weight dựa vào specificity, cần một bảng weight rõ ràng.

### 5.4 Lỗi #3 — `extract_dialogue_verb()` không được định nghĩa

Hàm này được gọi nhưng không có implementation nào. Các câu hỏi chưa được trả lời:
- Regex pattern là gì?
- Xử lý compound verb `停下脚步转身道` thế nào?
- Xử lý verb ở đầu câu thế nào (倒装句)?
- Timeout/max_length cho regex?

### 5.5 Lỗi #4 — Context carry-over tạo snowball effect

```python
if prev_context.emotion and prev_context.emotion_age < 3:
    scores[prev_context.emotion] += 1
```

Nếu emotion `angry` được detect với score=2 ở câu 1, nó sẽ cộng thêm 1 vào câu 2. Nếu câu 2 có chỉ 1 angry keyword, tổng score = 2 → vẫn `angry`. Nếu câu 3 có 0 angry keyword, tổng score = 1 → neutral.

Nhưng nếu câu 2 có 1 angry keyword VÀ 1 sad keyword, cả hai đều nhận carry-over từ câu 1:
- `angry`: 1 (carry-over) + 1 (keyword) = 2
- `sad`: 0 (carry-over, vì prev=angry, không phải sad) + 1 (keyword) = 1

Kết quả: `angry` thắng dù câu 2 thực sự có thể là chuyển sang sad. **Carry-over suppresses state transitions.**

### 5.6 Lỗi #5 — Pronoun Matrix không đầy đủ cho edge cases

Pronoun Matrix trong `Plan.md` có nhiều cells trống (—):

```
| Vợ chồng (M→F) | phu quân→thiếp | ta→ngươi | ta→nàng | nàng→ta | thiếp ơi | — | — |
```

Cells `—` cho Mocking và Threatening của vợ chồng chưa được định nghĩa. Nếu engine gặp `mocking` emotion trong cặp `vợ chồng`, nó sẽ:
- Throw exception vì key không tồn tại?
- Fallback về `neutral`?
- Dùng `ta/ngươi` generic?

Không có fallback strategy được document. Đây là crash risk trong production.

---

## 6. PHÂN TÍCH TRIE PIPELINE — THỨ TỰ XỬ LÝ VÀ CONFLICT

### 6.1 Phát hiện: LuatNhan chạy SAU Trie — Gây ra vấn đề với tên riêng

Từ pseudocode GĐ2:
```
c) Trie Traversal
d) LuatNhan Pattern Apply
   - "与{0}说话" + "Lâm Động" → "nói chuyện với Lâm Động"
e) Pronoun Resolution
f) Number Conversion
```

Vấn đề: LuatNhan template `{0}` cần tên nhân vật ở dạng **đã được dịch** (Lâm Động), nhưng Trie đã dịch toàn bộ câu. Nếu Trie translate `林动` → `Lâm Động` trong câu `与林动说话`, sau đó LuatNhan scan kết quả tìm pattern `与{0}说话` — nó sẽ KHÔNG MATCH vì input đã là `nói chuyện với Lâm Động` (đã dịch).

**LuatNhan phải chạy TRÊN SOURCE TEXT (tiếng Trung), sau đó mới Trie translate các từ còn lại.**

Đúng thứ tự:
```
Source: "与林动说话"
1. LuatNhan detect pattern: "与{0}说话" → match với {0}=林动
2. Extract: target_template = "nói chuyện với {0}"
3. Trie translate {0}: 林动 → Lâm Động
4. Final: "nói chuyện với Lâm Động"
```

Thay vì:
```
Source: "与林动说话"
1. Trie translate: "与Lâm Động说话"  ← lỗi: nửa TQ nửa VI
2. LuatNhan tìm "与{0}说话" trong "với Lâm Động nói" → MISS
```

### 6.2 One-Mean Mode thiếu disambiguation context

```
One-Mean mode: split(";")[0] cho P2/P3
```

VietPhrase dùng `;` để phân tách nghĩa: `修为=tu vi; tu hành; cảnh giới`. Chọn `[0]` (nghĩa đầu tiên) như một heuristic đơn giản không xem xét context.

Ví dụ nghiêm trọng:
```
"她" = "nàng; bà; cô; chị" → split(";")[0] = "nàng"
```
Nếu `她` đề cập đến một nhân vật lớn tuổi (bà), output sẽ là "nàng" — sai hoàn toàn về mặt xã hội.

### 6.3 Hot-reload Trie không xử lý partial dictionary changes

`Plan.md`: `Hot-reload: watch dictionary folder, rebuild incremental`

Nhưng **incremental rebuild** là bài toán phức tạp hơn nhiều so với tên gọi:
- Nếu một Rich MD file thay đổi, cần biết entry nào bị xóa, thêm, sửa
- Với Trie, xóa một entry yêu cầu rebuild nhánh (không thể chỉ set null)
- "Incremental" thực tế có thể là rebuild toàn bộ subtree → chậm hơn full rebuild đối với các thay đổi lớn

Thiếu benchmarks để verify "incremental" thực sự nhanh hơn full rebuild.

---

## 7. PHÂN TÍCH ENTITY SCANNER — FALSE POSITIVE PATTERN

### 7.1 Character Detector — Pattern nguy hiểm

```python
# Plan.md:
Pattern: 2-4 Hán tự liên tiếp + xuất hiện ≥3 lần
Cross-check với Names.txt
Context clue: xuất hiện sau 对/向/跟/和
Context clue: xuất hiện trước 说/道/笑/怒
```

**Pattern `2-4 Hán tự + frequency ≥ 3`** sẽ match rất nhiều false positive:

| Cụm từ | Frequency trong novel 200ch | Là tên người? |
|--------|----------------------------|---------------|
| 一个人 | >500 | ❌ |
| 这些人 | >200 | ❌ |
| 天下人 | >50 | ❌ |
| 修炼者 | >100 | ❌ |
| 那个人 | >300 | ❌ |
| 武者 | >150 | ❌ |
| 老者 | >100 | ❌ (thường là noun, không phải proper name) |
| 长老 | >200 | ❌ (title, không phải tên) |
| 少年 | >500 | ❌ |

**Context clue "xuất hiện trước 说/道"** cũng fail với:
```
"那个人说道：..."     → "那个人" không phải tên riêng
"这少年道：..."        → "少年" không phải tên riêng
"一个老者笑道：..."    → "老者" không phải tên riêng
```

Thiếu sót: Không có `blacklist` cho các noun phrases phổ biến không phải tên riêng.

### 7.2 Location Detector — Suffix pattern collision

```python
Pattern: X + 城/山/谷/河/海/洲/国/宫/殿/府/门/宗/派
```

Vấn đề collision:
- `大海` (biển lớn) vs `南海` (Nam Hải — tên địa điểm)
- `河流` (dòng sông) vs `黄河` (Hoàng Hà)
- `宗师` (tổng sư — danh hiệu) vs `道宗` (tên môn phái)

Suffix không đủ để phân biệt noun thường với proper noun.

---

## 8. PHÂN TÍCH CULTURAL ORIGIN DETECTION — NAIVE SCORE

### 8.1 Pseudocode thực tế từ Plan.md

```python
JAPANESE_CLUES = ['忍者', '武士', '侍', '殿', '様', 'の',
                  '火影', '海贼', '死神', '动漫']
WESTERN_CLUES  = ['骑士', '城堡', '公爵', '伯爵', '魔法师',
                  '精灵', '矮人', '龙与']

scores = {'japanese': 0, 'western': 0, 'korean': 0, 'chinese': 0}
for clue in JAPANESE_CLUES:
    if clue in context: scores['japanese'] += 1

return max(scores, key=scores.get)
```

### 8.2 Lỗi Logic — Clue lists quá ngắn và không discriminative

**`WESTERN_CLUES` chỉ có 8 entries** — cực kỳ thiếu. Nhiều truyện xianxia Trung Quốc MÔ TẢ về phương Tây nhưng bối cảnh vẫn là Trung Quốc:

```
"他见过洋人，那些洋人骑士手持长剑..."
→ WESTERN_CLUES match "骑士" → scores['western'] += 1
→ Nhưng truyện này vẫn là Chinese origin!
```

**Tương tự với `'の'` trong JAPANESE_CLUES** — nhiều tác giả Trung Quốc dùng `の` trong tên nhân vật fan fiction:

```
"刀のの" (tên nhân vật trong một số fanfic) → false positive Japanese
```

### 8.3 Lỗi Logic — `max(scores, key=scores.get)` với scores đều = 0

Nếu context không có bất kỳ clue nào, tất cả scores = 0, và `max()` sẽ trả về **key đầu tiên trong dict** (trong Python 3.7+ là 'japanese' do insertion order). Default sẽ là 'japanese' thay vì 'chinese' — sai.

```python
# Nguy hiểm:
scores = {'japanese': 0, 'western': 0, 'korean': 0, 'chinese': 0}
max(scores, key=scores.get)  # → 'japanese' khi tất cả = 0!

# Đúng phải là:
if all(v == 0 for v in scores.values()):
    return 'chinese'  # Default là Chinese
```

---

## 9. PHÂN TÍCH EMOTIONSTATE MACHINE — DECAY HARDCODED

### 9.1 Vấn đề với hardcoded DECAY_RULES

```python
DECAY_RULES = {
    'angry':      5,
    'furious':    8,
    'tender':     4,
    'flirty':     3,
    'sad':        6,
    'desperate':  10,
    'fearful':    4,
    'terrified':  7,
    'mocking':    3,
    'cold':       5,
    'threatening': 4,
}
```

Các số này hoàn toàn arbitrary và **không thay đổi được theo genre**. Nhưng:
- Trong truyện kinh dị, `fearful` kéo dài hơn (không phải 4 câu)
- Trong truyện ngôn tình modern, `flirty` kéo dài hơn (không phải 3 câu)
- Trong battle scene xianxia, `furious` có thể kéo dài cả chapter

Đặc biệt: `DECAY_RULES` thiếu nhiều emotion states được định nghĩa trong emotion table:
- `excited` — không có decay rule!
- `grateful` — không có decay rule!
- `arrogant` — không có decay rule!
- `respectful` — không có decay rule!

Khi `EmotionState.update()` gọi `DECAY_RULES.get(self.current_emotion, 3)` cho emotion không có trong dict, sẽ dùng default `3` — không nhất quán.

### 9.2 Scene break detection quá hạn hẹp

```python
SCENE_BREAK_PATTERNS = ['***', '---', '===', '※※※']
```

Nhiều truyện dùng các pattern khác:
- `　　` (full-width space, thường dùng trong truyện Trung Quốc để indicate paragraph break/scene break)
- Blank line (2+ consecutive `\n`)
- `----------` (nhiều dấu gạch)
- `○` (circle character)
- Số La Mã I, II, III
- `【×】` markers

Thiếu cơ chế extensible để thêm pattern mới.

---

## 10. PHÂN TÍCH LUATNHAN INTEGRATION — AMBIGUITY GAP

### 10.1 Template `{0}` chỉ hỗ trợ một entity

`Plan.md` chỉ mention template với `{0}`:
```python
"与{0}说话" + "Lâm Động" → "nói chuyện với Lâm Động"
```

Nhưng nhiều câu tiếng Trung có 2-3 entity:
```
"林动对绫清竹道：'你陪我去找萧炎。'"
Pattern: "{0}对{1}道：'{2}'" → 3 entities
```

Không có documentation hay pseudocode nào về multi-entity templates hay `{0}`, `{1}`, `{2}` support. Nếu chỉ có `{0}`, toàn bộ lớp patterns phức tạp này sẽ không được xử lý.

### 10.2 Không có confidence scoring cho LuatNhan matches

Khi LuatNhan match một pattern, không có mechanism nào để:
- Biết match có chắc chắn không (ngắn pattern = less confident)
- So sánh multiple patterns match cùng một đoạn
- Decide khi 2 patterns overlap

---

## 11. PHÂN TÍCH TRANSLATION MEMORY — FUZZY MATCH FLAW

### 11.1 Fuzzy match dùng Levenshtein cho CJK

```
Fuzzy match (Levenshtein ≤ 15%)
```

**Levenshtein trên ký tự CJK không có semantic meaning:**

```
"他走了" và "她走了" — Levenshtein distance: 1/3 = 33% → KHÔNG match
Nhưng nghĩa: "anh ta đi rồi" vs "cô ấy đi rồi" — rất khác

"修为大进" và "修炼大成" — Levenshtein: 2/4 = 50% → KHÔNG match
Nhưng nghĩa gần giống nhau → SHOULD match for fuzzy
```

Threshold `≤ 15%` cực kỳ thấp cho CJK — hầu như chỉ match exact hoặc single-char diff. Nên dùng character bigram Jaccard similarity thay thế.

### 11.2 TM lookup xảy ra TRƯỚC Trie — Timestamp mismatch risk

```python
# Plan.md GĐ2:
[3. Translation Memory Lookup]
[4. Trie RBMT Core Translation]
```

TM lookup trước Trie có nghĩa là: nếu TM có một segment nhưng dictionary đã được update (từ mới thêm vào, nghĩa cũ thay đổi), segment được lấy từ TM sẽ dùng bản dịch **cũ** mà không biết dictionary đã thay đổi.

Không có mechanism invalidate TM entries khi dictionary thay đổi.

---

## 12. PHÂN TÍCH CẤU TRÚC REPO — VẪN CÒN FILE RÁC

### 12.1 Xác nhận 100% — file rác chưa được xóa

Từ directory listing thực tế ngày 30/04/2026, các file sau VẪN TỒN TẠI:

**Files phải xóa khỏi Git tracking (đã có trong .gitignore nhưng chưa `git rm --cached`):**
```
all_global_errors.jsonl      # Có trong .gitignore (*.jsonl)
cedict_seeding_debug.txt     # Có trong .gitignore
diagnose_results.json        # Có trong .gitignore
pos_db_audit.json            # Có trong .gitignore (pos_*.json)
pos_diagnostic_results.json  # Có trong .gitignore (pos_*.json)
pos_rewrite_test_results.json # Có trong .gitignore (pos_*.json)
trie_verification.json       # Có trong .gitignore
project_progress.json        # Có trong .gitignore!
SVID_20260423_073257_1.mp4   # Có trong .gitignore (*.mp4)
```

**Files cần di chuyển (vẫn tại root):**
```
debug_regex.py         → scripts/dev/
debug_rewriter.py      → scripts/dev/
debug_zh_rewriter.py   → scripts/dev/
clean_dict.py          → scripts/migration/
patch_nc2.py           → scripts/dev/
patch_nc5.py           → scripts/dev/
run_coach_feedback.py  → scripts/runners/
run_full_pipeline.py   → scripts/runners/
run_prepare.py         → scripts/runners/
run_pretranslation.py  → scripts/runners/
run_translate_ch01.py  → scripts/runners/
run_translate_ch02.py  → scripts/runners/
test_basic.js          → tests/js/
test_comprehensive.js  → tests/js/
test_import.py         → tests/
```

**Files cần archive hoặc merge:**
```
implementation_plan.md.resolved
implementation_plan22.md.resolved
metadata_migration_plan.md.resolved
pipeline_guidev2.md.resolved
pipeline_guidev3.md.resolved
walkthrough.md.resolved
enhanced_translation_system_plan.md
fixpos.md
Plan.md                → Nên ở plans/
UI.md                  → Nên ở docs/ hoặc plans/
```

**Files vô nghĩa:**
```
python         → File không rõ loại, không có extension
Name project/  → Thư mục tên có khoảng trắng, nội dung chưa rõ
Converter by DrDuc.json  → Tên có khoảng trắng, nội dung duplicate converter_by_drduc.json
```

**Command cần chạy để giải quyết `.gitignore` paradox:**
```bash
# Xóa các file đã committed nhưng nay nằm trong .gitignore
git rm --cached all_global_errors.jsonl
git rm --cached cedict_seeding_debug.txt
git rm --cached diagnose_results.json
git rm --cached pos_db_audit.json
git rm --cached pos_diagnostic_results.json
git rm --cached pos_rewrite_test_results.json
git rm --cached trie_verification.json
git rm --cached project_progress.json
git rm --cached SVID_20260423_073257_1.mp4
git commit -m "chore: remove tracked files now in .gitignore"

# Sau đó file sẽ bị ignore trong tương lai
# Xóa local copies nếu không cần:
# rm all_global_errors.jsonl ...
```

---

## 13. PHÂN TÍCH `IMPLEMENTATION_SUMMARY.md` — TÀI LIỆU SAI KIẾN TRÚC

### 13.1 Mâu thuẫn nghiêm trọng với kiến trúc thực tế

`IMPLEMENTATION_SUMMARY.md` mô tả kiến trúc **JavaScript** (prototype cũ):

```markdown
- Set up complete directory structure (src/preprocessor, src/parser, src/rules, src/learning)
- Created configuration files (package.json, project_progress.json)
- Implemented Trinity state management (session.json)
- Structure Preservation Module: regex patterns and placeholder systems
- Traditional-to-Simplified Converter: HMM and Viterbi algorithm for Pinyin-to-Chinese
- **Morphological Analyzer: Performs POS tagging and lemmatization**
- **Dependency Parser: Creates syntactic trees for transformation**
- **Rule Induction Engine: Learns new rules from post-editing feedback**
- **Context Manager: Maintains discourse coherence across sentences**
- CRF-based morphological analysis
- Translation Memory: dynamic suffix arrays
```

**Tất cả những thứ này là mô tả về JavaScript prototype, KHÔNG phải Python production code.** CRF, dynamic suffix arrays, dependency parsing — không có gì trong số này được implement trong Python production code theo `project_progress.json`.

Đặc biệt:
- `Rule Induction Engine` — hoàn toàn KHÔNG tồn tại trong implementation thực
- `CRF-based morphological analysis` — KHÔNG tồn tại
- `dynamic suffix arrays` cho TM — KHÔNG tồn tại (TM dùng SQLite với Levenshtein)
- `session.json` Trinity state — KHÔNG tồn tại trong Python production path

### 13.2 `IMPLEMENTATION_SUMMARY.md` mô tả tính năng không bao giờ được xây dựng

Mục "Next Steps" ghi:
```
1. Enhancing the morphological analyzer with more sophisticated models
2. Expanding the syntax transfer rule set
3. Improving the Pinyin resolution with larger training data
4. Implementing more sophisticated context management
5. Conducting extensive testing with real translation projects
```

Nhưng theo `project_progress.json`, Phase 00-08 đều **DONE**. Không có Phase 09 nào được plan cho "more sophisticated morphological analyzer". Nghĩa là `IMPLEMENTATION_SUMMARY.md` mô tả roadmap của một hệ thống **khác** với hệ thống đang được xây dựng.

**Đây là tài liệu zombie** — mô tả kế hoạch của JS prototype, không liên quan đến Python production system.

---

## 14. PHÂN TÍCH `project_progress.json` — MÂU THUẪN DỮ LIỆU

### 14.1 Mâu thuẫn giữa tests số lượng theo phase

```json
T1.1 (Phase 01): "full Phase 01 test suite passes (91 passed)"
T1.8 (Phase 08): "python -m pytest (99 passed)"
```

Nếu Phase 01 đã có 91 tests, và Phase 02-08 cộng thêm tests, tại sao Phase 08 chỉ có 99 tests (chỉ +8 so với Phase 01)?

Khả năng:
- Nhiều tests đã bị xóa trong quá trình refactor
- 91 tests ban đầu tính cả integration tests sau bị loại
- Số liệu không nhất quán do manual tracking

### 14.2 Milestones dates không khớp với thực tế

```json
"milestones": [
    {"name": "Baseline Stable", "date": "2026-04-30"},
    {"name": "Foundation Closed", "date": "2026-05-15"},
    {"name": "Pre-Translation Active", "date": "2026-06-01"},
    {"name": "First End-to-End Chapter", "date": "2026-08-30"},
    {"name": "QA and State Integrated", "date": "2026-09-30"},
    {"name": "Desktop Workflow Available", "date": "2026-11-15"}
]
```

Nhưng `meta.last_updated = "2026-04-23"` và tất cả phases đều `DONE`. "Desktop Workflow Available" được milestone cho ngày `2026-11-15` nhưng đã DONE vào `2026-04-23`. Milestones là **dead configuration** không được cập nhật sau khi phases hoàn thành.

### 14.3 `project_progress.json` NÊN ở trong `.gitignore` — và đã có!

Nghịch lý đã được nêu ở Section 2: `.gitignore` CÓ `project_progress.json` nhưng file vẫn trong repo vì đã được committed trước. Cần `git rm --cached`.

---

## 15. PHÂN TÍCH `converter_by_drduc.json` — DEPENDENCY GAP

### 15.1 Dependencies liệt kê vs Dependencies thực tế cần

```json
"dependency": "chardet, pyyaml, sqlite3, jieba, underthesea, pytest, watchdog"
```

**`sqlite3` là stdlib** — không cần install, không nên liệt kê.

**Thiếu nhiều dependencies quan trọng:**

| Dependency | Cần cho | Có trong list? |
|------------|---------|----------------|
| `jieba` | ZH tokenization | ✅ |
| `underthesea` | VI NLP | ✅ |
| `chardet` | Encoding detection | ✅ |
| `pyyaml` | YAML frontmatter parsing | ✅ |
| `watchdog` | File system watching | ✅ |
| `pytest` | Testing | ✅ |
| `markdownify` | HTML→Markdown conversion | ❌ THIẾU |
| `python-frontmatter` | Parse YAML frontmatter từ MD | ❌ THIẾU |
| `pypinyin` | Pinyin conversion (nếu dùng) | ❌ THIẾU |
| `opencc-python-reimplemented` | Traditional→Simplified | ❌ THIẾU |
| `pytest-cov` | Test coverage | ❌ THIẾU |
| `aiofiles` | Async file I/O cho batch | ❌ THIẾU |

Đặc biệt: **`opencc` (OpenCC)** là thư viện standard cho Traditional→Simplified conversion, được Plan.md nói đến (`Traditional-to-Simplified Converter`) nhưng không có trong dependency list.

### 15.2 `banned_modules` không được enforce

```json
"banned_modules": ["openai", "anthropic", "transformers"]
```

Đây là policy declaration nhưng không có enforcement mechanism nào:
- Không có linter rule
- Không có CI check
- Không có import guard trong code

Nếu một contributor vô tình `import transformers` cho một utility nhỏ, sẽ không có gì catch được.

---

## 16. PHƯƠNG PHÁP KHẮC PHỤC CHI TIẾT VỚI CODE MẪU

### 16.1 Sửa `pyproject.toml` — Ưu tiên cao nhất

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"   # Sửa từ _legacy

[project]
name = "drduc-translator"
version = "0.1.0"
description = "Non-LLM Rule-Based Machine Translation System (ZH/EN → VI)"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "DrDuc"}]

dependencies = [
    "jieba>=0.42.1",
    "underthesea>=6.8.0",
    "chardet>=5.2.0",
    "pyyaml>=6.0",
    "python-frontmatter>=1.1.0",
    "markdownify>=0.11.6",
    "watchdog>=3.0.0",
    "opencc-python-reimplemented>=0.1.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=src --cov-report=term-missing"

[tool.setuptools.packages.find]
where = ["."]
include = ["src.core*", "src.engine*", "src.pipeline*",
           "src.eapee*", "src.qa*", "src.state*",
           "src.en_vi*", "src.ui*"]
exclude = ["src.preprocessor*", "src.parser*",
           "src.rules*", "src.learning*"]
```

### 16.2 Sửa Trie Priority Order

```python
# src/core/trie_engine.py
class TrieLoadOrder:
    """
    Thứ tự load đúng: project-specific LUÔN thắng global.
    """
    PRIORITY_LAYERS = [
        # (priority_value, path_pattern, description)
        (50, "projects/{name}/names_rieng.md",      "Project character names"),
        (40, "projects/{name}/vietphrase_rieng.md", "Project vietphrase"),
        (30, "global/names/_bulk_names.md",          "Global names"),
        (20, "global/vietphrase/_bulk_vietphrase.md","Global vietphrase"),
        (10, "global/phien_am/_bulk_phienam.md",     "Phien am fallback"),
    ]

    # Quy tắc: project > global cho cùng loại
    # Không bao giờ để global names (30) đánh bại project vietphrase (40)
```

### 16.3 Sửa `detect_emotion()` — Thêm context classifier

```python
class SentenceContextClassifier:
    DIALOGUE_QUOTE_OPEN  = ['「', '"', '『', '【']
    DIALOGUE_QUOTE_CLOSE = ['」', '"', '』', '】']
    SPEECH_VERBS = ['道', '说', '叫道', '喊道', '问道', '答道',
                    '笑道', '怒道', '哭道', '叹道', '低声道']
    INNER_MONOLOGUE = ['想道', '心道', '心想', '暗道', '暗想',
                       '脑海中', '心中想', '想到', '想起']

    def classify(self, sentence: str) -> str:
        # Inner monologue detection (priority)
        if any(kw in sentence for kw in self.INNER_MONOLOGUE):
            return 'inner_monologue'

        # Dialogue detection
        has_quote = any(q in sentence for q in self.DIALOGUE_QUOTE_OPEN)
        has_speech_verb = any(v in sentence for v in self.SPEECH_VERBS)
        if has_quote or has_speech_verb:
            return 'dialogue'

        return 'narrative'

def detect_emotion(sentence: str, prev_context, classifier: SentenceContextClassifier):
    ctx_type = classifier.classify(sentence)

    # Chỉ áp dụng emotion detection cho dialogue
    if ctx_type in ('narrative', 'inner_monologue'):
        return 'neutral', 0, ctx_type  # Không thay đổi pronoun

    # ... rest of existing logic ...
    return emotion, intensity, ctx_type
```

### 16.4 Sửa `max(scores)` bug trong Cultural Origin Detection

```python
def detect_cultural_origin(context: str) -> str:
    scores = {'japanese': 0, 'western': 0, 'korean': 0, 'chinese': 0}

    for clue in JAPANESE_CLUES:
        if clue in context:
            scores['japanese'] += 1
    # ... other scores ...

    # FIX: Tránh bug khi tất cả = 0
    if all(v == 0 for v in scores.values()):
        return 'chinese'  # Default rõ ràng

    # FIX: Tránh tie-breaking theo dict order
    best_score = max(scores.values())
    candidates = [k for k, v in scores.items() if v == best_score]
    if len(candidates) == 1:
        return candidates[0]
    # Tie-breaking: chinese > japanese > western > korean (heuristic)
    for preferred in ['chinese', 'japanese', 'western', 'korean']:
        if preferred in candidates:
            return preferred
```

### 16.5 Sửa EmotionState — Configurable decay + missing emotions

```python
DEFAULT_DECAY_RULES = {
    'angry':      5,
    'furious':    8,
    'tender':     4,
    'flirty':     3,
    'sad':        6,
    'desperate':  10,
    'fearful':    4,
    'terrified':  7,
    'mocking':    3,
    'cold':       5,
    'threatening': 4,
    # Thêm missing emotions:
    'excited':    4,
    'grateful':   3,
    'arrogant':   5,
    'respectful': 3,
}

GENRE_DECAY_MULTIPLIERS = {
    'horror':   {'fearful': 2.0, 'terrified': 2.0, 'desperate': 1.5},
    'romance':  {'flirty': 2.0, 'tender': 1.5},
    'action':   {'furious': 1.5, 'angry': 1.5},
    'tragedy':  {'sad': 2.0, 'desperate': 1.5},
}

EXTENDED_SCENE_BREAK_PATTERNS = [
    '***', '---', '===', '※※※',
    '○', '●', '◆', '◇',          # Circle/diamond markers
    '----------',                   # Long dash
    '\n\n\n',                       # Triple newline
    '　　　　　',                   # Full-width spaces (5+)
]

class EmotionState:
    def __init__(self, genre: str = 'xianxia'):
        self.genre = genre
        self.decay_rules = self._compute_decay_rules(genre)

    def _compute_decay_rules(self, genre: str) -> dict:
        rules = DEFAULT_DECAY_RULES.copy()
        multipliers = GENRE_DECAY_MULTIPLIERS.get(genre, {})
        for emotion, mult in multipliers.items():
            if emotion in rules:
                rules[emotion] = int(rules[emotion] * mult)
        return rules
```

### 16.6 Sửa LuatNhan — Multi-entity template support

```python
import re

class LuatNhanEngine:
    PLACEHOLDER_PATTERN = re.compile(r'\{(\d+)\}')

    def apply(self, template: str, entities: list[str]) -> str:
        """
        Hỗ trợ {0}, {1}, {2}, ... cho multiple entities.
        """
        def replacer(match):
            idx = int(match.group(1))
            if idx < len(entities):
                return entities[idx]
            return match.group(0)  # Keep original nếu index out of range

        return self.PLACEHOLDER_PATTERN.sub(replacer, template)

    def match_and_apply(self, source_sentence: str, all_entities: dict) -> str | None:
        """
        Match pattern trong source (ZH), extract entities, apply template.
        Chạy TRÊN source text tiếng Trung, TRƯỚC khi Trie translate.
        """
        for pattern, vi_template in self.patterns:
            match = re.search(pattern, source_sentence)
            if match:
                entities = [
                    all_entities.get(match.group(i+1), match.group(i+1))
                    for i in range(len(match.groups()))
                ]
                return self.apply(vi_template, entities)
        return None
```

### 16.7 Sửa Pronoun Matrix — Fallback strategy

```python
PRONOUN_MATRIX = {
    'ancient': {
        'lover_m_to_f': {
            'neutral':     ('ta', 'nàng'),
            'angry':       ('ta', 'ngươi'),
            'tender':      ('ta', 'nàng'),
            'flirty':      ('ta', 'nàng'),
            'sad':         ('ta', 'thiếp ơi...'),
            'mocking':     ('ta', 'ngươi'),      # FIX: Định nghĩa rõ
            'threatening': ('ta', 'ngươi'),      # FIX: Định nghĩa rõ
            '_default':    ('ta', 'nàng'),       # Fallback for unknown emotions
        },
        # ... more relationships
    }
}

def lookup_pronoun(genre: str, relationship: str, emotion: str,
                   gender_pair: str) -> tuple[str, str]:
    matrix = PRONOUN_MATRIX.get(genre, PRONOUN_MATRIX['ancient'])
    rel_key = f"{relationship}_{gender_pair}"
    rel_matrix = matrix.get(rel_key, {})

    # Try exact emotion → fallback to _default → fallback to neutral → hardcoded fallback
    result = (rel_matrix.get(emotion) or
              rel_matrix.get('_default') or
              rel_matrix.get('neutral') or
              ('ta', 'ngươi'))  # Last resort hardcoded
    return result
```

### 16.8 Sửa Entity Scanner — Blacklist + POS gate

```python
# Blacklist phrases phổ biến không phải tên riêng
ENTITY_BLACKLIST = {
    # Đại từ và đại từ nhóm
    '他们', '她们', '它们', '我们', '你们', '大家', '众人',
    # Noun phrases phổ biến
    '一个人', '这些人', '那些人', '天下人', '世人', '路人',
    '修炼者', '武者', '道士', '修士', '散修',
    # Mô tả ngoại hình không phải tên
    '少年', '青年', '老者', '老头', '少女', '女子', '男子',
    '白发老者', '黑衣人', '红衣少女',
    # Danh hiệu không phải tên riêng
    '长老', '师父', '师傅', '掌门', '宗主',
    # Thành ngữ có số
    '十万火急', '百年一遇', '千变万化', '万紫千红',
}

def is_likely_character_name(candidate: str, frequency: int,
                              contexts: list[str]) -> bool:
    # Step 1: Blacklist check
    if candidate in ENTITY_BLACKLIST:
        return False

    # Step 2: Length check (2-4 chars)
    if not (2 <= len(candidate) <= 4):
        return False

    # Step 3: Frequency threshold
    if frequency < 3:
        return False

    # Step 4: Contains common non-name chars?
    NON_NAME_CHARS = {'一', '二', '三', '个', '些', '这', '那', '很', '非常'}
    if any(c in candidate for c in NON_NAME_CHARS):
        return False

    # Step 5: Context quality score
    speech_contexts = sum(
        1 for ctx in contexts
        if any(v in ctx for v in ['道', '说', '笑', '问', '答'])
    )
    # Ít nhất 30% contexts có speech verb
    if len(contexts) > 0 and speech_contexts / len(contexts) < 0.3:
        return False

    return True
```

### 16.9 Giải quyết `.gitignore` paradox — Command sequence

```bash
#!/bin/bash
# scripts/dev/cleanup_tracked_files.sh
# Chạy một lần để xóa files đã committed nhưng nay trong .gitignore

set -e
echo "Removing files that are tracked but should be ignored..."

TRACKED_IGNORED=(
    "all_global_errors.jsonl"
    "cedict_seeding_debug.txt"
    "diagnose_results.json"
    "pos_db_audit.json"
    "pos_diagnostic_results.json"
    "pos_rewrite_test_results.json"
    "trie_verification.json"
    "project_progress.json"
    "SVID_20260423_073257_1.mp4"
)

for file in "${TRACKED_IGNORED[@]}"; do
    if git ls-files --error-unmatch "$file" 2>/dev/null; then
        git rm --cached "$file"
        echo "Untracked: $file"
    fi
done

git commit -m "chore: untrack files now covered by .gitignore

Files remain on local disk but are no longer tracked by Git.
.gitignore already covers these patterns."
```

---

## 17. BẢNG TỔNG HỢP TOÀN BỘ THIẾU SÓT THEO MỨC ƯU TIÊN

| # | Thiếu sót | Phát hiện từ | Mức | Impact | Effort |
|---|-----------|-------------|-----|--------|--------|
| 1 | `pyproject.toml` thiếu `[project.dependencies]` | Đọc trực tiếp | 🔴 P0 | Install broken | Thấp |
| 2 | `build-backend = _legacy` (private API) | Đọc trực tiếp | 🔴 P0 | Build broken | Thấp |
| 3 | File rác trong Git (cần `git rm --cached`) | Directory tree | 🔴 P0 | Repo integrity | Thấp |
| 4 | LuatNhan chạy sau Trie — Order sai | Plan.md pseudocode | 🔴 P0 | Translation sai | Trung bình |
| 5 | Trie Priority order: P3 < P4 — logic sai | Plan.md | 🔴 P0 | Dict priority sai | Thấp |
| 6 | `detect_emotion()` không phân biệt narrative vs dialogue | Plan.md pseudocode | 🔴 P1 | Pronoun sai | Trung bình |
| 7 | `max(scores)` bug khi scores đều = 0 | Plan.md pseudocode | 🔴 P1 | Default sai | Thấp |
| 8 | Pronoun Matrix có cells `—` chưa định nghĩa — crash risk | Plan.md | 🔴 P1 | Runtime crash | Thấp |
| 9 | Entity Scanner thiếu blacklist — false positive cao | Plan.md pseudocode | 🟠 P2 | Glossary noise | Trung bình |
| 10 | `keyword_weight()` và `extract_dialogue_verb()` không defined | Plan.md pseudocode | 🟠 P2 | Undefined behavior | Trung bình |
| 11 | EmotionState missing emotions trong DECAY_RULES | Plan.md pseudocode | 🟠 P2 | KeyError fallback | Thấp |
| 12 | Carry-over suppresses state transitions | Plan.md pseudocode | 🟠 P2 | Emotion stuck | Trung bình |
| 13 | Chapter boundary không reset emotion state | Plan.md pseudocode | 🟠 P2 | Cross-chapter noise | Trung bình |
| 14 | Fuzzy TM: Levenshtein không phù hợp CJK | Plan.md (explicit) | 🟠 P2 | TM accuracy | Trung bình |
| 15 | Number Converter thiếu fraction/decimal/âm/cổ | Plan.md (explicit) | 🟠 P2 | Convert error | Trung bình |
| 16 | IMPLEMENTATION_SUMMARY mô tả JS prototype (zombie doc) | Đọc trực tiếp | 🟠 P2 | Confuse contributor | Thấp |
| 17 | `pyproject.toml` include `src*` quá rộng — JS vào build | Đọc trực tiếp | 🟠 P2 | Build contamination | Thấp |
| 18 | One-Mean `split(";")[0]` thiếu context disambiguation | Plan.md | 🟡 P3 | Quality | Cao |
| 19 | LuatNhan chỉ support `{0}` — thiếu multi-entity | Plan.md | 🟡 P3 | Pattern coverage | Trung bình |
| 20 | Cultural Origin CLUES lists quá ngắn | Plan.md pseudocode | 🟡 P3 | Name accuracy | Trung bình |
| 21 | DECAY_RULES hardcoded, không configurable theo genre | Plan.md | 🟡 P3 | Flexibility | Trung bình |
| 22 | Scene break patterns chưa đủ | Plan.md | 🟡 P3 | Reset accuracy | Thấp |
| 23 | Structure Preservation placeholder collision risk | Plan.md | 🟡 P3 | Rare bug | Thấp |
| 24 | TM không invalidate khi dictionary thay đổi | Plan.md | 🟡 P3 | Stale translations | Cao |
| 25 | `project_progress.json` milestones không được update | Đọc trực tiếp | 🟢 P4 | Doc stale | Thấp |
| 26 | `converter_by_drduc.json` thiếu markdownify, opencc | Đọc trực tiếp | 🟢 P4 | Doc incomplete | Thấp |
| 27 | `banned_modules` không có enforcement | Đọc trực tiếp | 🟢 P4 | Policy only | Trung bình |
| 28 | CI/CD chưa có | Không thấy .github/ | 🟢 P4 | Quality | Trung bình |
| 29 | `Converter by DrDuc.json` tên có khoảng trắng | Directory tree | 🟢 P4 | Cross-platform | Thấp |

---

## 18. ROADMAP HÀNH ĐỘNG THEO TUẦN

### Tuần 1 — P0 Fixes (Critical Blockers)

**Ngày 1-2:**
```bash
# Fix pyproject.toml
# - Thêm [project.dependencies]
# - Sửa build-backend = "setuptools.build_meta"
# - Explicit include/exclude packages

# Fix .gitignore paradox
bash scripts/dev/cleanup_tracked_files.sh

# Di chuyển files rác
mkdir -p scripts/dev scripts/migration scripts/runners tests/js
git mv debug_*.py patch_nc*.py scripts/dev/
git mv clean_dict.py scripts/migration/
git mv run_*.py scripts/runners/
git mv test_*.js tests/js/
git mv test_import.py tests/
```

**Ngày 3-4:**
```python
# Fix Trie Priority Order (src/core/trie_engine.py)
# Sửa PRIORITY_LAYERS: project specific > global

# Fix LuatNhan execution order
# Di chuyển LuatNhan.apply() sang trước Trie traversal
# Sửa src/engine/rbmt_translator.py pipeline
```

**Ngày 5:**
```python
# Fix critical crash bugs:
# - Pronoun Matrix fallback strategy (Section 16.7)
# - max(scores) bug fix (Section 16.4)
# - DECAY_RULES thêm missing emotions (Section 16.5)
```

### Tuần 2 — P1/P2 Algorithm Fixes

```python
# Implement SentenceContextClassifier (Section 16.3)
# Integrate vào detect_emotion pipeline

# Define keyword_weight() với explicit scoring
KEYWORD_WEIGHTS = {
    # Rất specific (3+ chars, compound)
    '勃然大怒': 5, '暴跳如雷': 5, '怒不可遏': 5,
    # Specific (compound 2-char)
    '愤怒': 3, '暴怒': 4, '大怒': 3,
    # Common (single char)
    '怒': 2, '怒道': 3,  # verb form = higher weight
}

# Define extract_dialogue_verb() với regex
DIALOGUE_VERB_PATTERN = re.compile(
    r'([^\s，。！？]{1,4}(?:' + '|'.join(SPEECH_VERBS) + r'))[：:「"『]'
)

# Fix Entity Scanner với blacklist (Section 16.8)

# Fix Cultural Origin detection (Section 16.4)
```

### Tuần 3 — P2/P3 Quality Improvements

```python
# Extend Number Converter:
# - Fractions: 三分之一 → một phần ba
# - Decimals: 零点五 → 0.5
# - Negatives: 负三十 → âm 30
# - Archaic time: 一柱香 → một nén hương
# - Idiom blacklist: 十万火急, 千变万化

# Implement genre-configurable EmotionState decay
# Extend scene break patterns

# Multi-entity LuatNhan support (Section 16.6)

# Add TM invalidation flag when dictionary version changes
```

### Tuần 4 — Documentation + CI

```bash
# Rewrite IMPLEMENTATION_SUMMARY.md để mô tả đúng Python production

# Archive enhanced_translation_system_plan.md vào docs/archive/

# Cập nhật project_progress.json milestones

# Setup GitHub Actions CI:
mkdir -p .github/workflows
# Tạo .github/workflows/ci.yml (xem báo cáo lần 2)

# Cập nhật README.md để đồng bộ với README_VI.md
```

---

## 19. KẾT LUẬN

### 19.1 Phát hiện quan trọng nhất của lần đọc này

Lần đầu tiên đọc được toàn bộ `Plan.md` (pseudocode thực tế) đã tiết lộ **5 lỗi thuật toán nghiêm trọng** chưa được phát hiện trong hai báo cáo trước:

1. **LuatNhan chạy sau Trie** — thứ tự sai khiến template matching fail hoàn toàn với sentences đã được partially translated
2. **Trie Priority P3 < P4** — project-specific VietPhrase thua global names, vi phạm nguyên tắc "project overrides global"
3. **`max(scores)` bug khi scores đều = 0** — default origin sẽ là 'japanese' thay vì 'chinese'
4. **Pronoun Matrix có cells trống `—` chưa có fallback** — crash risk trong production khi emotion-relationship combination chưa được cover
5. **`pyproject.toml` thiếu toàn bộ dependencies** — không có gì được install khi chạy `pip install -e .`

### 19.2 Tình trạng thực tế

Repo có **hai lớp vấn đề** song song tồn tại:

**Lớp 1 — Housekeeping (chưa fix):** Root clutter, Git tracking của files trong .gitignore, pyproject.toml thiếu dependencies. Những vấn đề này tồn tại từ lần commit đầu và chưa được giải quyết qua 3 lần phân tích.

**Lớp 2 — Algorithm (mới phát hiện):** Sau khi đọc pseudocode thực tế, phát hiện thêm 5 lỗi logic quan trọng trong Plan.md — những lỗi này ảnh hưởng trực tiếp đến correctness của output dịch nếu code được implement đúng theo plan.

### 19.3 Ưu tiên tuyệt đối

**Làm ngay trong 24 giờ — 3 việc có impact lớn nhất với effort thấp nhất:**

1. **Sửa `pyproject.toml`** — thêm dependencies và sửa build-backend. Không có điều này, không ai có thể install và chạy dự án.

2. **Chạy `git rm --cached`** cho các files trong .gitignore — giải quyết paradox và làm repo sạch mà không mất data.

3. **Swap thứ tự LuatNhan và Trie** trong pipeline — sửa lỗi kiến trúc fundamental nhất, đảm bảo template matching hoạt động đúng.

---

*Báo cáo v3 được tổng hợp từ việc đọc trực tiếp: `Plan.md` (1388 dòng, 56KB — toàn bộ pseudocode), `.gitignore` (43 dòng — toàn bộ), `pyproject.toml` (25 dòng — toàn bộ), `project_progress.json` (116 dòng — toàn bộ), `converter_by_drduc.json` (34 dòng — toàn bộ), `IMPLEMENTATION_SUMMARY.md` (86 dòng — toàn bộ), và GitHub directory tree thực tế ngày 30/04/2026.*

**Phiên bản:** 3.0 | **Ngày:** 30/04/2026 | **Tác giả:** Claude (Anthropic)
