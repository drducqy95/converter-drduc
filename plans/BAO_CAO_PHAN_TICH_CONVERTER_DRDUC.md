# BÁO CÁO PHÂN TÍCH DỰ ÁN: `converter-drduc`

**Tác giả phân tích:** Claude (Anthropic)  
**Ngày:** 29/04/2026  
**Repo:** https://github.com/drducqy95/converter-drduc  
**Phiên bản phân tích:** v1.0 — Toàn diện

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Phân tích cấu trúc thư mục](#2-phân-tích-cấu-trúc-thư-mục)
3. [Phân tích kỹ thuật — Điểm mạnh](#3-phân-tích-kỹ-thuật--điểm-mạnh)
4. [Thiếu sót về cấu trúc dự án](#4-thiếu-sót-về-cấu-trúc-dự-án)
5. [Thiếu sót về thuật toán & kỹ thuật](#5-thiếu-sót-về-thuật-toán--kỹ-thuật)
6. [Thiếu sót về tổ chức tài liệu & vận hành](#6-thiếu-sót-về-tổ-chức-tài-liệu--vận-hành)
7. [Phương pháp khắc phục đề xuất](#7-phương-pháp-khắc-phục-đề-xuất)
8. [Bảng tổng hợp mức độ ưu tiên](#8-bảng-tổng-hợp-mức-độ-ưu-tiên)
9. [Kế hoạch hành động theo giai đoạn](#9-kế-hoạch-hành-động-theo-giai-đoạn)
10. [Kết luận](#10-kết-luận)

---

## 1. TỔNG QUAN DỰ ÁN

**`converter-drduc`** là hệ thống dịch thuật **Rule-Based Machine Translation (RBMT)**, không sử dụng LLM, chuyên dịch văn bản dài (truyện, tài liệu) từ **Tiếng Trung (ZH)** và **Tiếng Anh (EN)** sang **Tiếng Việt (VI)**. Dự án hướng đến việc bảo toàn ngữ cảnh, xưng hô nhân vật, bảng biểu, công thức và hình ảnh.

**Stack công nghệ:**

- **Backend (Production):** Python (80.5%) — `src/core/`, `src/engine/`, `src/pipeline/`, `src/qa/`, `src/state/`
- **Frontend:** TypeScript + React (13.7%) — Tauri/React desktop shell
- **Scripts:** JavaScript (4.1%) — Module prototype/reference (KHÔNG phải production runtime)
- **Storage:** SQLite (Translation Memory, Trie cache)
- **Config:** `pyproject.toml`, `requirements.txt`

**Trạng thái hiện tại (theo README):**

- Phase 00–07: Implemented and tested (98 tests passed)
- Phase 08: React shell + Python sidecar/Tauri scaffold
- Tauri native packaging: **chưa validate** (thiếu Rust toolchain)

---

## 2. PHÂN TÍCH CẤU TRÚC THƯ MỤC

### 2.1 Cấu trúc hiện tại

```
converter-drduc/
├── .agents/workflows/          ← Workflow config cho AI agents
├── Name project/               ⚠️ Tên thư mục có khoảng trắng
├── data/                       ← Dữ liệu từ điển, corpus
├── desktop/                    ← Tauri + React frontend
├── docs/                       ← Tài liệu
├── plans/                      ← Kế hoạch chi tiết
├── scripts/                    ← Scripts tiện ích
├── src/                        ← Source code chính
│   ├── core/                   (Python production)
│   ├── engine/                 (Python production)
│   ├── pipeline/               (Python production)
│   ├── eapee/                  (Emotion-Aware engine)
│   ├── qa/                     (QA modules)
│   ├── state/                  (State management)
│   ├── en_vi/                  (EN→VI engine)
│   ├── ui/                     (Sidecar protocol)
│   ├── preprocessor/           ⚠️ JS prototype (NOT production)
│   ├── parser/                 ⚠️ JS prototype (NOT production)
│   ├── rules/                  ⚠️ JS prototype (NOT production)
│   └── learning/               ⚠️ JS prototype (NOT production)
├── tests/                      ← Test suite
├── index.js                    ← JS entry point (prototype)
├── pyproject.toml
├── requirements.txt
├── package.json
│
│── [ROOT LEVEL CLUTTER] ──────────────────────────────
├── debug_regex.py              ⚠️ Debug script rò rỉ lên root
├── debug_rewriter.py           ⚠️ Debug script rò rỉ lên root
├── debug_zh_rewriter.py        ⚠️ Debug script rò rỉ lên root
├── clean_dict.py               ⚠️ Utility script lên root
├── patch_nc2.py                ⚠️ Patch script lên root
├── patch_nc5.py                ⚠️ Patch script lên root
├── run_coach_feedback.py       ⚠️ Runner script lên root
├── run_full_pipeline.py        ⚠️ Runner script lên root
├── run_prepare.py              ⚠️ Runner script lên root
├── run_pretranslation.py       ⚠️ Runner script lên root
├── run_translate_ch01.py       ⚠️ Runner script lên root
├── run_translate_ch02.py       ⚠️ Runner script lên root
├── test_basic.js               ⚠️ Test file rò rỉ lên root
├── test_comprehensive.js       ⚠️ Test file rò rỉ lên root
├── test_import.py              ⚠️ Test file rò rỉ lên root
│
│── [DEBUG/DIAGNOSTIC DATA] ───────────────────────────
├── all_global_errors.jsonl     ⚠️ Error log committed vào repo
├── cedict_seeding_debug.txt    ⚠️ Debug data committed
├── diagnose_results.json       ⚠️ Diagnostic output committed
├── pos_db_audit.json           ⚠️ Audit data committed
├── pos_diagnostic_results.json ⚠️ Diagnostic output committed
├── pos_rewrite_test_results.json ⚠️ Test result committed
├── trie_verification.json      ⚠️ Verification data committed
│
│── [PLAN FILES TẠI ROOT] ─────────────────────────────
├── Plan.md                     ⚠️ Nên ở /plans/
├── UI.md                       ⚠️ Nên ở /docs/ hoặc /plans/
├── fixpos.md                   ⚠️ Nên ở /docs/
├── enhanced_translation_system_plan.md  ⚠️ Nên ở /plans/
├── IMPLEMENTATION_SUMMARY.md   (OK — tại root là hợp lý)
├── README.md                   (OK)
│
│── [RESOLVED FILES] ──────────────────────────────────
├── implementation_plan.md.resolved     ⚠️ Phần mở rộng .resolved không chuẩn
├── implementation_plan22.md.resolved   ⚠️
├── metadata_migration_plan.md.resolved ⚠️
├── pipeline_guidev2.md.resolved        ⚠️
├── pipeline_guidev3.md.resolved        ⚠️
├── walkthrough.md.resolved             ⚠️
│
│── [BINARY/MEDIA] ─────────────────────────────────────
├── SVID_20260423_073257_1.mp4  ⚠️ Video file trong repo (~có thể rất lớn)
├── Converter by DrDuc.json     ⚠️ Tên file có khoảng trắng
├── converter_by_drduc.json     (OK)
└── python                      ⚠️ File tên "python" không rõ loại
```

---

## 3. PHÂN TÍCH KỸ THUẬT — ĐIỂM MẠNH

Trước khi đi vào thiếu sót, cần ghi nhận các điểm tích cực đáng kể:

**3.1 Kiến trúc tổng thể tốt:** Quyết định dùng Python làm production runtime thay vì JavaScript là đúng đắn, tận dụng được hệ sinh thái NLP phong phú (jieba, underthesea).

**3.2 Hệ thống từ điển hybrid sáng tạo:** Mô hình Bulk MD (cho ~728K entries) + Rich MD (cho thuật ngữ quan trọng) là giải pháp thực tế và có khả năng mở rộng tốt.

**3.3 EAPEE (Emotion-Aware Pronoun & Expression Engine):** Đây là tính năng đặc biệt và sáng tạo nhất của dự án — ma trận 4 chiều (Genre × Relationship × Emotion × Gender) là cách tiếp cận đúng đắn cho bài toán xưng hô tiếng Việt trong văn học.

**3.4 Multi-world name translation:** Quy tắc phân biệt văn hóa nguồn gốc (Hepburn cho Nhật, Revised Romanization cho Hàn, Hán-Việt cho Trung) là giải pháp thực tiễn và chuyên nghiệp.

**3.5 Test coverage:** 98 tests passed là mức độ kiểm thử đáng khen cho giai đoạn này.

---

## 4. THIẾU SÓT VỀ CẤU TRÚC DỰ ÁN

### 4.1 ❌ ROOT DIRECTORY BỊ NHIỄM BẨN NGHIÊM TRỌNG

**Vấn đề:** Gốc repository chứa hàng chục file không thuộc về đó, tạo ra sự hỗn loạn nghiêm trọng trong điều hướng và bảo trì.

**Chi tiết:**

- **12 script files rò rỉ:** `run_*.py`, `debug_*.py`, `patch_*.py`, `clean_dict.py` — tất cả nên nằm trong `scripts/` hoặc `scripts/dev/`
- **7 file diagnostic/log committed:** `all_global_errors.jsonl`, `diagnose_results.json`, `pos_db_audit.json`, v.v. — **KHÔNG được commit data output vào repo**
- **3 test files tại root:** `test_basic.js`, `test_comprehensive.js`, `test_import.py` — nên nằm trong `tests/`
- **6 file `.md.resolved`:** Phần mở rộng `.resolved` không phải convention chuẩn của bất kỳ tool nào; có vẻ là artifact của AI agent và nên được dọn dẹp hoặc di chuyển
- **4 plan files tại root:** `Plan.md`, `UI.md`, `fixpos.md`, `enhanced_translation_system_plan.md` — nên nằm trong `plans/` hoặc `docs/`

**Hệ quả:**
- Contributor mới không thể xác định điểm vào của dự án
- `git log` và `git diff` bị ô nhiễm bởi noise
- CI/CD pipeline khó cấu hình sạch

### 4.2 ❌ HAI IMPLEMENTATION LAYER CÙNG TỒN TẠI MÀ KHÔNG CÓ RANH GIỚI RÕ RÀNG

**Vấn đề:** README tuyên bố JavaScript modules (`src/preprocessor/`, `src/parser/`, `src/rules/`, `src/learning/`) là "prototype/reference material" nhưng chúng vẫn nằm TRONG `src/` — cùng thư mục với production Python code.

**Chi tiết:**

```
src/
├── core/           ← Python PRODUCTION
├── engine/         ← Python PRODUCTION
├── pipeline/       ← Python PRODUCTION
├── preprocessor/   ← JavaScript PROTOTYPE ← CÓ LẦN LỘN
├── parser/         ← JavaScript PROTOTYPE ← CÓ LẦN LỘN
├── rules/          ← JavaScript PROTOTYPE ← CÓ LẦN LỘN
└── learning/       ← JavaScript PROTOTYPE ← CÓ LẦN LỘN
```

**Hệ quả:**
- Không thể chạy `find src/ -name "*.py"` để lấy tất cả Python source một cách sạch
- `pyproject.toml` config `include = ["src*"]` có thể vô tình include JS files
- Contributor mới không biết file nào là production, file nào là prototype

### 4.3 ❌ TÊN FILE/THƯ MỤC CHỨA KHOẢNG TRẮNG

**Vấn đề:**

- `Name project/` — thư mục với khoảng trắng
- `Converter by DrDuc.json` — file JSON với khoảng trắng

**Hệ quả:** Gây lỗi trên nhiều hệ điều hành (Linux shell scripts), CI/CD pipelines, và một số Python path operations nếu không escape đúng cách.

### 4.4 ❌ MEDIA FILE KHÔNG NÊN CÓ TRONG GIT

**Vấn đề:** `SVID_20260423_073257_1.mp4` — file video trong repository. Các file binary lớn như video làm tăng kích thước clone repository một cách không cần thiết.

**Hệ quả:** Clone time tăng đáng kể; Git performance giảm. File này nên được host trên YouTube/Google Drive và link vào README.

### 4.5 ❌ THIẾU `CONTRIBUTING.md` VÀ ONBOARDING DOCUMENTATION

**Vấn đề:** Không có tài liệu hướng dẫn contributor mới cách thiết lập môi trường phát triển, quy tắc commit, cấu trúc branch, hay quy trình code review.

### 4.6 ❌ THIẾU CI/CD CONFIGURATION

**Vấn đề:** Không có file `.github/workflows/*.yml` nào — không có Continuous Integration. `python -m pytest` chỉ chạy thủ công.

**Hệ quả:** Không có barrier tự động ngăn regression khi push code mới.

### 4.7 ⚠️ `.gitignore` CÓ THỂ CHƯA ĐẦY ĐỦ

**Vấn đề:** Sự hiện diện của `all_global_errors.jsonl`, `diagnose_results.json`, `pos_db_audit.json` trong repo cho thấy `.gitignore` chưa bao gồm các pattern output/diagnostic cần thiết.

---

## 5. THIẾU SÓT VỀ THUẬT TOÁN & KỸ THUẬT

### 5.1 ❌ DUAL IMPLEMENTATION GAP: JS vs PYTHON

**Vấn đề nghiêm trọng nhất về kỹ thuật:** Dự án có TWO hoàn chỉnh plans mô tả cùng một hệ thống:

- `enhanced_translation_system_plan.md` — Mô tả implementation bằng **JavaScript** (Node.js), đề cập tới `src/preprocessor/structure_preserver.js`, `src/parser/morphological_analyzer.js`, CRF via JavaScript, HMM-Viterbi trong JS, v.v.
- `Plan.md` — Mô tả implementation bằng **Python**, đây là roadmap chính thức

**Hệ quả:** Hai tài liệu thiết kế cùng tồn tại mô tả cùng các component nhưng bằng hai ngôn ngữ khác nhau. Điều này gây ra:

- Confusion về "nguồn sự thật" cho kiến trúc hệ thống
- Risk rằng tính năng được implement nhầm bằng JS thay vì Python
- Khó maintain khi một plan update mà plan kia không được sync

### 5.2 ❌ EMOTION DETECTOR: NGƯỠNG QUYẾT ĐỊNH QUÁ THẤP

**Vấn đề:** Theo pseudo-code trong `Plan.md`:

```python
if scores[top_emotion] < 2:
    return 'neutral', 0  # Không đủ signal
```

Ngưỡng `< 2` là quá thấp. Một keyword duy nhất với trọng số 2 đã đủ trigger non-neutral emotion. Trong văn bản tường thuật (không phải dialogue), nhiều từ cảm xúc xuất hiện trong văn phong mô tả, không phải biểu đạt thực sự của speaker.

**Ví dụ lỗi tiềm ẩn:**
```
"他内心充满恐惧，但面上却是平静的。"
(Nội tâm hắn đầy sợ hãi, nhưng mặt ngoài vẫn bình tĩnh.)
```
→ `恐惧` sẽ trigger `fearful` → xưng hô sẽ bị đổi sang mode sợ hãi, nhưng câu này là mô tả trạng thái nội tâm, không phải dialogue.

**Thiếu sót:** Không có cơ chế phân biệt **dialogue context** vs **narrative context** trước khi apply emotion detection.

### 5.3 ❌ PRONOUN RESOLVER: THIẾU MULTI-SPEAKER DIALOGUE HANDLING

**Vấn đề:** Hệ thống xác định speaker từ pattern `X说/X道`, nhưng:

1. **Implicit speaker (省略主语):** Tiếng Trung thường bỏ chủ ngữ. Khi không có `X说`, hệ thống không có cơ chế suy luận speaker từ ngữ cảnh trước đó.

2. **Multi-character dialogue scene:** Khi 3+ nhân vật trong một scene, pattern `A对B说...然后B转向C` cần tracking phức tạp hơn simple speaker-detection.

3. **Inner monologue vs spoken dialogue:** `「想什么呢？」` (độc thoại nội tâm) vs `「想什么呢？」他问道` (lời thoại thực sự) — cần xử lý khác nhau về pronoun.

### 5.4 ❌ TRIE ENGINE: KHÔNG CÓ PARTIAL UPDATE MECHANISM

**Vấn đề:** README đề cập "hot-reload" nhưng khi dictionary thay đổi, hệ thống phải rebuild toàn bộ Trie. Với 728K+ entries trong VietPhrase, mỗi rebuild mất 3–5 giây. Điều này không chấp nhận được trong workflow dịch interactive (user đang dịch, thêm từ mới, muốn rebuild ngay).

**Thiếu sót:** Không có incremental/partial Trie update — chỉ có full rebuild.

### 5.5 ❌ FUZZY TRANSLATION MEMORY: LEVENSHTEIN KHÔNG PHÙ HỢP VỚI CJK

**Vấn đề:** Theo Plan.md: `Fuzzy match (Levenshtein ≤ 15%)`. Levenshtein Distance tính theo **ký tự**, không phải **từ** (word). Với tiếng Trung:

- `他走了` và `她走了` — chỉ khác 1 ký tự (他→她) = distance 1 (33% của 3 chars), nhưng nghĩa hoàn toàn khác (anh ta đi / cô ấy đi)
- `修为大进` và `修炼大成` — distance 2 = 50%, nhưng nghĩa tương đương

**Thiếu sót:** Cần semantic similarity hoặc ít nhất là character n-gram similarity thay vì raw Levenshtein cho CJK.

### 5.6 ❌ ENTITY SCANNER: FALSE POSITIVE RATE CAO

**Vấn đề:** Character Detector theo Plan.md dùng heuristic:

```
Pattern: 2-4 Hán tự liên tiếp + xuất hiện ≥3 lần
```

**False positives dự kiến cao:**

- `一般人` (người bình thường) — xuất hiện 5+ lần → bị nhận diện là tên người
- `这些人` (những người này) — 3 chữ, xuất hiện nhiều → false positive
- `天下人` (người trong thiên hạ) — tương tự

**Thiếu sót:** Không có blacklist các cụm từ phổ biến không phải tên riêng. Không có part-of-speech filtering trước khi apply tên detector.

### 5.7 ❌ CONTEXT MANAGER: KHÔNG XỬ LÝ "CHAPTER BOUNDARY" RÕ RÀNG

**Vấn đề:** Sliding window context (5 câu trước + 5 câu sau) bị ngắt đột ngột khi gặp chapter boundary. Nhân vật, tình huống, và xưng hô từ cuối chapter trước vẫn có thể liên quan đến đầu chapter sau.

**Thiếu sót:** Không có "chapter summary accumulation" đủ để truyền ngữ cảnh emotion state và active character list qua boundary một cách có kiểm soát.

### 5.8 ❌ NUMBER CONVERTER: THIẾU ORDINAL NUMBERS VÀ FRACTIONAL

**Vấn đề:** `number_converter.py` được đề cập handle:

- `一百二十三 → 123` ✓
- `第X → thứ X` ✓

**Nhưng thiếu:**

- Phân số: `三分之一 → một phần ba` (không phải `3/1`)
- Số thập phân: `零点五 → 0.5`
- Số âm: `负三十度 → âm 30 độ / -30°`
- Đơn vị cổ đại: `一石 → một thạch`, `一两 → một lượng`
- Tiền tệ cổ đại: `三百两银子 → 300 lượng bạc`

### 5.9 ⚠️ EAPEE: EMOTION DECAY RULES HARDCODED

**Vấn đề:** Decay rules trong EmotionStateMachine là hardcoded:

```python
DECAY_RULES = {
    'angry': 5,   # Giận dữ kéo dài 5 câu
    'furious': 8, ...
}
```

Số câu này hoàn toàn arbitrary và không có cơ sở thực nghiệm. Không có cơ chế cho phép user/project override decay rules theo thể loại truyện (cảm xúc trong truyện kinh dị kéo dài lâu hơn truyện ngôn tình?).

### 5.10 ⚠️ CULTURAL ORIGIN DETECTION: QUÁ NAIVE

**Vấn đề:** Auto-detect cultural origin dựa trên keyword matching đơn giản:

```python
JAPANESE_CLUES = ['忍者', '武士', '侍', '动漫', ...]
```

**Vấn đề:** Một truyện Xuyên Không Trung Quốc CÓ THỂ đề cập đến `忍者` trong câu thoại mà không có nghĩa là bối cảnh Nhật. Score-based detection sẽ bị confuse bởi cross-cultural references phổ biến trong fan fiction.

### 5.11 ⚠️ THIẾU SYLLABLE-AWARE TOKENIZATION CHO TIẾNG VIỆT OUTPUT

**Vấn đề:** Kết quả dịch là tiếng Việt, nhưng không có module nào đảm bảo output tuân thủ quy tắc viết tiếng Việt: dấu thanh điệu đặt đúng vị trí, tách từ đúng (ví dụ: "sức mạnh" không phải "sứcmạnh"), và không có dấu cách thừa trước dấu câu.

### 5.12 ⚠️ QA ENGINE: KHÔNG CÓ BLEU/METEOR SCORING

**Vấn đề:** `Plan.md` đặt ra mục tiêu "terminology accuracy > 95% vs bản dịch mẫu" nhưng không có benchmark script nào visible để đo BLEU/METEOR score tự động so với ground truth translation.

---

## 6. THIẾU SÓT VỀ TỔ CHỨC TÀI LIỆU & VẬN HÀNH

### 6.1 ❌ KHÔNG CÓ CHANGELOG

Không có `CHANGELOG.md`. Với một project phức tạp đang active develop, changelog là bắt buộc để track what changed between versions.

### 6.2 ❌ KHÔNG CÓ VERSIONING STRATEGY

Dự án ở `version = "0.1.0"` trong `pyproject.toml` nhưng không có quy trình release, tagging, hay semantic versioning documented.

### 6.3 ❌ HAI README MÀ KHÔNG RÕ CANONICAL

`README.md` và `README_VI.md` tồn tại song song. Không rõ file nào là canonical khi có thông tin mâu thuẫn. Cần sync mechanism hoặc chỉ giữ một file với i18n note.

### 6.4 ❌ `requirements.txt` vs `pyproject.toml` — DUAL DEPENDENCY MANAGEMENT

Có cả `requirements.txt` và `pyproject.toml` cùng quản lý dependencies. Đây là anti-pattern: khi hai file không sync, môi trường dev và production khác nhau.

### 6.5 ⚠️ KHÔNG CÓ `docker-compose.yml` HAY CONTAINER SUPPORT

Với hệ thống phức tạp (Python engine + Tauri desktop + SQLite), không có container configuration nghĩa là setup môi trường mới tiềm ẩn nhiều "works on my machine" issues.

### 6.6 ⚠️ `project_progress.json` LÀ STATE FILE KHÔNG NÊN COMMIT

File `project_progress.json` tracking tiến độ là runtime state, không phải source code. Nếu committed vào repo, nó sẽ gây conflict liên tục khi nhiều người làm việc song song.

### 6.7 ⚠️ KHÔNG CÓ SECURITY POLICY

Với một desktop app (Tauri), cần có `SECURITY.md` documented cách report vulnerabilities.

---

## 7. PHƯƠNG PHÁP KHẮC PHỤC ĐỀ XUẤT

### 7.1 KHắC PHỤC CẤU TRÚC THƯ MỤC

**Bước 1: Dọn dẹp root directory**

```bash
# Di chuyển debug scripts
mkdir -p scripts/dev scripts/migration scripts/runners
git mv debug_*.py scripts/dev/
git mv patch_nc*.py scripts/dev/
git mv clean_dict.py scripts/migration/
git mv run_*.py scripts/runners/

# Di chuyển test files
git mv test_basic.js tests/js/
git mv test_comprehensive.js tests/js/
git mv test_import.py tests/

# Di chuyển plan files
git mv Plan.md plans/main_plan.md
git mv UI.md docs/ui_spec.md
git mv fixpos.md docs/
git mv enhanced_translation_system_plan.md plans/
```

**Bước 2: Thêm vào `.gitignore`**

```gitignore
# Diagnostic & debug output
*.jsonl
diagnose_results*.json
pos_*.json
trie_verification.json
cedict_seeding_debug.txt
all_global_errors*

# Runtime state
project_progress.json
session.json

# Media files
*.mp4
*.avi
*.mkv

# Python artifacts
__pycache__/
*.pyc
*.pyo
.pytest_cache/
dist/
build/
*.egg-info/

# JS artifacts
node_modules/
desktop/node_modules/
desktop/dist/

# Database
*.db
*.sqlite
data/_compiled/
```

**Bước 3: Tách JS prototype ra khỏi `src/`**

```bash
mkdir -p prototype/js
git mv src/preprocessor prototype/js/
git mv src/parser prototype/js/
git mv src/rules prototype/js/
git mv src/learning prototype/js/
```

Cập nhật README để ghi rõ `prototype/js/` là reference material không có trong build.

**Bước 4: Đổi tên files có khoảng trắng**

```bash
git mv "Name project" name_project
git mv "Converter by DrDuc.json" converter_by_drduc_v2.json
```

### 7.2 KHẮC PHỤC EMOTION DETECTOR

**Thêm context classifier trước emotion detection:**

```python
class SentenceContextClassifier:
    """
    Phân loại câu trước khi apply emotion detection.
    """
    
    DIALOGUE_MARKERS = {
        'pre': ['道', '说', '叫道', '喊道', '笑道', '怒道'],  # Ngay sau dấu ngoặc kép
        'post': ['的', '地', '着']  # Không áp dụng emotion
    }
    
    NARRATIVE_INDICATORS = [
        '他的心里', '她的内心', '脑海中', '暗想', '心道',  # Mô tả nội tâm
        '心中想', '想到', '想着'
    ]
    
    def classify(self, sentence: str) -> str:
        """Returns: 'dialogue', 'inner_monologue', 'narrative'"""
        if any(kw in sentence for kw in self.NARRATIVE_INDICATORS):
            return 'inner_monologue'  # Không apply pronoun change
        if self._has_dialogue_quote(sentence):
            return 'dialogue'
        return 'narrative'  # Không apply pronoun change

# Sử dụng:
context_type = classifier.classify(sentence)
if context_type == 'dialogue':
    emotion, intensity = detector.detect_emotion(sentence, prev_context)
    # Apply pronoun logic
else:
    emotion = 'narrative_neutral'  # Skip pronoun change
```

**Tăng ngưỡng confidence:**

```python
# Hiện tại
if scores[top_emotion] < 2:
    return 'neutral', 0

# Đề xuất
EMOTION_THRESHOLD = {
    'dialogue': 2,        # Thấp hơn cho dialogue (dễ detect)
    'inner_monologue': 4, # Cao hơn để tránh false positive
    'narrative': 5,       # Cao nhất
}
threshold = EMOTION_THRESHOLD.get(context_type, 3)
if scores[top_emotion] < threshold:
    return 'neutral', 0
```

### 7.3 KHẮC PHỤC IMPLICIT SPEAKER DETECTION

```python
class SpeakerTracker:
    """
    Theo dõi speaker/listener qua nhiều câu liên tiếp.
    """
    
    def __init__(self):
        self.last_speaker = None
        self.last_listener = None
        self.conversation_stack = []  # [A, B, A, B, ...]
    
    def update_from_sentence(self, sentence: str, active_chars: list) -> tuple:
        # Explicit: 林动道/林动说
        for char in active_chars:
            if f"{char.source_name}道" in sentence or \
               f"{char.source_name}说" in sentence:
                speaker = char
                # Listener từ 对X/向X
                for other in active_chars:
                    if f"对{other.source_name}" in sentence or \
                       f"向{other.source_name}" in sentence:
                        listener = other
                        self.last_speaker = speaker
                        self.last_listener = listener
                        return speaker, listener
                # Listener mặc định = người nói trước đó
                listener = self.last_speaker if self.last_speaker != speaker else None
                self.last_speaker = speaker
                return speaker, listener
        
        # Implicit: Không có speaker marker → Đảo speaker
        if len(self.conversation_stack) >= 2:
            # Alternating dialogue assumption
            return self.last_listener, self.last_speaker
        
        return None, None
```

### 7.4 KHẮC PHỤC FUZZY TRANSLATION MEMORY

Thay thế Levenshtein bằng **character n-gram Jaccard similarity** cho CJK:

```python
def cjk_similarity(s1: str, s2: str, n: int = 2) -> float:
    """
    Tính độ tương đồng dựa trên bigram overlap.
    Phù hợp hơn cho CJK so với Levenshtein.
    """
    def get_ngrams(s: str, n: int) -> set:
        return {s[i:i+n] for i in range(len(s) - n + 1)}
    
    bigrams1 = get_ngrams(s1, n)
    bigrams2 = get_ngrams(s2, n)
    
    if not bigrams1 or not bigrams2:
        return 1.0 if s1 == s2 else 0.0
    
    intersection = len(bigrams1 & bigrams2)
    union = len(bigrams1 | bigrams2)
    return intersection / union

# Ngưỡng phù hợp hơn cho CJK:
# similarity > 0.75 → Fuzzy match (thay vì Levenshtein ≤ 15%)
```

### 7.5 KHẮC PHỤC ENTITY SCANNER FALSE POSITIVES

```python
# Thêm blacklist patterns
COMMON_PHRASES_NOT_NAMES = {
    # Đại từ
    '他们', '她们', '我们', '你们', '大家',
    # Cụm từ phổ biến
    '一般人', '这些人', '那些人', '天下人', '众人',
    '世人', '常人', '普通人', '凡人', '路人',
    # Danh từ chung có suffix giống tên
    '修炼者', '武者', '道士', '和尚', '侠客',
    # Negation patterns
    '没有人', '任何人', '每个人',
}

def is_likely_name(candidate: str, frequency: int, context: str) -> bool:
    if candidate in COMMON_PHRASES_NOT_NAMES:
        return False
    if frequency < 3:
        return False
    # Kiểm tra POS context: tên riêng thường đứng trước động từ cảm xúc/nói
    has_speech_verb_context = any(
        verb in context for verb in ['道', '说', '笑', '怒', '喝', '叫']
    )
    return has_speech_verb_context or frequency >= 10
```

### 7.6 THIẾT LẬP CI/CD

Tạo `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: python -m pytest tests/ -v --tb=short
      - name: Check coverage
        run: python -m pytest --cov=src --cov-report=xml

  desktop-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - name: Build desktop
        run: cd desktop && npm install && npm run build
```

### 7.7 CHUẨN HÓA DEPENDENCY MANAGEMENT

Loại bỏ `requirements.txt`, chuyển toàn bộ vào `pyproject.toml`:

```toml
[project]
dependencies = [
    "jieba>=0.42.1",
    "underthesea>=6.8.0",
    "chardet>=5.0.0",
    "markdownify>=0.11.6",
    "sqlalchemy>=2.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov",
    "black",
    "ruff",
    "mypy",
]
```

### 7.8 KHẮC PHỤC DUAL PLAN DOCUMENTS

Merge `enhanced_translation_system_plan.md` (JS-based) vào `Plan.md` (Python-based) như một section lịch sử:

```markdown
## Lịch sử thiết kế

### Phiên bản JS (deprecated - 2026-04 early)
> Xem archive tại `docs/archive/enhanced_translation_system_plan_js.md`
> Đã quyết định chuyển sang Python production vì [lý do].
```

### 7.9 KHẮC PHỤC `.md.resolved` FILES

Các file `.md.resolved` là artifact của AI coding agent (NotebookLM/Claude Code). Nên:

```bash
# Option 1: Convert thành markdown thường
for f in *.md.resolved; do
    mv "$f" "docs/archive/${f%.resolved}"
done

# Option 2: Xóa nếu đã merged vào main plan
git rm *.md.resolved
```

---

## 8. BẢNG TỔNG HỢP MỨC ĐỘ ƯU TIÊN

| # | Vấn đề | Mức độ | Impact | Effort |
|---|--------|--------|--------|--------|
| 1 | Root directory clutter (12+ files sai vị trí) | 🔴 Critical | Maintainability | Thấp |
| 2 | Debug/diagnostic data committed vào repo | 🔴 Critical | Repo health | Thấp |
| 3 | JS prototype trong `src/` lẫn với Python | 🔴 Critical | Build integrity | Thấp |
| 4 | Emotion Detector: thiếu context classifier | 🔴 Critical | Translation quality | Trung bình |
| 5 | Implicit speaker detection chưa implement | 🟠 High | Translation quality | Cao |
| 6 | Dual plan docs (JS vs Python mô tả cùng thing) | 🟠 High | Confusion | Thấp |
| 7 | CI/CD chưa có | 🟠 High | Code quality | Trung bình |
| 8 | Fuzzy TM: Levenshtein không phù hợp CJK | 🟠 High | TM accuracy | Trung bình |
| 9 | Entity scanner: false positive cao | 🟠 High | Terminology quality | Trung bình |
| 10 | Video file trong repo | 🟡 Medium | Repo size | Thấp |
| 11 | Dual dependency management (requirements.txt + pyproject.toml) | 🟡 Medium | Dev environment | Thấp |
| 12 | Tên file/thư mục có khoảng trắng | 🟡 Medium | Cross-platform | Thấp |
| 13 | Number converter thiếu fraction/decimal | 🟡 Medium | Translation quality | Trung bình |
| 14 | EAPEE decay rules hardcoded | 🟡 Medium | Flexibility | Trung bình |
| 15 | Cultural origin detection naive | 🟡 Medium | Name accuracy | Cao |
| 16 | Thiếu CHANGELOG | 🟢 Low | Documentation | Thấp |
| 17 | Thiếu CONTRIBUTING.md | 🟢 Low | Onboarding | Thấp |
| 18 | project_progress.json committed | 🟢 Low | State management | Thấp |
| 19 | Thiếu BLEU/METEOR scoring | 🟢 Low | Benchmarking | Cao |
| 20 | Thiếu SECURITY.md | 🟢 Low | Security posture | Thấp |

---

## 9. KẾ HOẠCH HÀNH ĐỘNG THEO GIAI ĐOẠN

### Giai đoạn 0 — Housekeeping (1–2 ngày)

Mục tiêu: Dọn dẹp repo, không ảnh hưởng đến functionality.

- [ ] Di chuyển tất cả `run_*.py`, `debug_*.py`, `patch_*.py` vào `scripts/`
- [ ] Di chuyển `test_*.py`, `test_*.js` vào `tests/`
- [ ] Di chuyển plan files vào `plans/`
- [ ] Cập nhật `.gitignore` với patterns output/diagnostic
- [ ] Remove video file, thêm link YouTube vào README
- [ ] Đổi tên files/thư mục có khoảng trắng
- [ ] Tách JS prototype vào `prototype/js/`
- [ ] Xóa hoặc archive `.md.resolved` files
- [ ] Hợp nhất `requirements.txt` vào `pyproject.toml`

### Giai đoạn 1 — Core Algorithm Fixes (1–2 tuần)

Mục tiêu: Sửa các lỗi kỹ thuật ảnh hưởng trực tiếp đến chất lượng dịch.

- [ ] Implement `SentenceContextClassifier` (dialogue vs narrative vs inner monologue)
- [ ] Tích hợp context classifier vào Emotion Detector pipeline
- [ ] Implement `SpeakerTracker` cho implicit speaker detection
- [ ] Thay thế Levenshtein bằng n-gram similarity trong Translation Memory
- [ ] Thêm blacklist phrases vào Entity Scanner
- [ ] Bổ sung fraction/decimal vào Number Converter

### Giai đoạn 2 — Infrastructure (1 tuần)

Mục tiêu: Thiết lập infrastructure cho long-term maintainability.

- [ ] Tạo GitHub Actions CI/CD workflow
- [ ] Tạo `CONTRIBUTING.md`
- [ ] Tạo `CHANGELOG.md`
- [ ] Thêm `SECURITY.md`
- [ ] Merge/archive JS plan document
- [ ] Setup pre-commit hooks (black, ruff, pytest)

### Giai đoạn 3 — Quality Improvements (2–3 tuần)

Mục tiêu: Nâng cao chất lượng dịch.

- [ ] Configurable emotion decay rules per genre
- [ ] Context-aware cultural origin detection
- [ ] Vietnamese output post-processor (dấu thanh điệu, khoảng cách)
- [ ] BLEU/METEOR benchmark script
- [ ] Incremental Trie update mechanism (thay vì full rebuild)
- [ ] Chapter boundary context preservation

---

## 10. KẾT LUẬN

### Nhận xét tổng thể

`converter-drduc` là một dự án **đầy tham vọng và được thiết kế có chiều sâu**. Ý tưởng core về RBMT không LLM với EAPEE engine là độc đáo và phù hợp với nhu cầu thực tế của cộng đồng dịch truyện tiếng Việt. Hệ thống từ điển hybrid (Bulk MD + Rich MD) là một giải pháp thực tiễn thông minh.

Tuy nhiên, dự án đang ở giai đoạn phát triển nhanh và **chưa kịp tổ chức lại sau nhiều iteration**. Phần lớn các vấn đề không phải lỗi thiết kế cơ bản mà là technical debt tích lũy trong quá trình prototype nhanh.

### Ưu tiên hành động ngay

Nếu chỉ có thể làm 3 việc ngay lập tức, đó nên là:

**1.** Dọn dẹp root directory và cập nhật `.gitignore` — chi phí thấp, lợi ích lớn cho maintainability.

**2.** Thêm `SentenceContextClassifier` vào Emotion Detector pipeline — đây là bug ảnh hưởng trực tiếp đến chất lượng dịch dialogue.

**3.** Tách JS prototype ra khỏi `src/` — ngăn chặn confusion về production boundary.

### Tiềm năng

Sau khi các vấn đề trên được khắc phục, `converter-drduc` có tiềm năng trở thành **công cụ dịch truyện chữ Hán sang tiếng Việt tốt nhất hiện có trong không gian không-LLM** — đặc biệt nhờ EAPEE engine và hệ thống xưng hô nhân vật context-aware, vốn là điểm yếu lớn nhất của tất cả các translator tự động hiện tại.

---

*Báo cáo này được tổng hợp từ: `README.md`, `Plan.md`, `IMPLEMENTATION_SUMMARY.md`, `enhanced_translation_system_plan.md`, `pyproject.toml`, và cấu trúc thư mục của repository. Một số phân tích thuật toán dựa trên pseudo-code và mô tả trong Plan.md mà không có điều kiện đọc trực tiếp source code Python.*

---

**Ngày phân tích:** 29/04/2026 | **Phiên bản:** v1.0
