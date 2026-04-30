# 🔬 BÁO CÁO PHÂN TÍCH KỸ THUẬT SÂU
## Repository: `drducqy95/converter-drduc`

> **Ngày phân tích:** 30/04/2026 — **Nhánh:** `main` — **Phiên bản:** v23.0 (hardening)
> **Cơ sở phân tích:** README.md, README_VI.md, Plan.md (56KB/1388 dòng), IMPLEMENTATION_SUMMARY.md, enhanced_translation_system_plan.md, pyproject.toml, cấu trúc thư mục root

---

## MỤC LỤC

| # | Nhóm | Nội dung |
|---|------|---------|
| 1 | [Tổng quan & Trạng thái](#1-tổng-quan) | Điểm mạnh, thống kê, ngữ cảnh |
| 2 | [Cấu trúc Project](#2-cấu-trúc-project) | 6 vấn đề về tổ chức repo |
| 3 | [Thuật toán Trie & LPM](#3-thuật-toán-trie--lpm) | 4 vấn đề về core matching |
| 4 | [Pipeline Dịch Thuật](#4-pipeline-dịch-thuật) | 5 vấn đề về orchestration |
| 5 | [Hệ thống EAPEE](#5-hệ-thống-eapee) | 4 vấn đề về emotion/pronoun |
| 6 | [Grammar Transfer Engine](#6-grammar-transfer-engine) | 3 vấn đề về cú pháp |
| 7 | [Translation Memory](#7-translation-memory) | 3 vấn đề về TM/learning |
| 8 | [QA & Testing](#8-qa--testing) | 3 vấn đề về chất lượng |
| 9 | [DevOps & Maintainability](#9-devops--maintainability) | 4 vấn đề vận hành |
| 10 | [Mâu thuẫn Kiến trúc](#10-mâu-thuẫn-kiến-trúc) | Xung đột chiến lược |
| 11 | [Ma trận Ưu tiên](#11-ma-trận-ưu-tiên) | Bảng tổng hợp 26 vấn đề |
| 12 | [Roadmap Khắc phục](#12-roadmap-khắc-phục) | Lộ trình theo sprint |

---

## 1. TỔNG QUAN

### 1.1 Mô tả hệ thống

`converter-drduc` là hệ thống **Rule-Based Machine Translation (RBMT) không dùng LLM**, chuyên dịch tiểu thuyết và tài liệu dài **ZH/EN → VI**, với các tính năng nổi bật:

- Trie 5 tầng ưu tiên (P1–P5) trên nền SQLite
- EAPEE: engine cảm xúc + xưng hô theo ngữ cảnh 4 chiều
- Grammar Transfer Engine với clause segmentation và conflict resolver
- Translation Memory phân tầng: `tm_machine` / `tm_approved` / `tm_reviewed`
- Desktop app: React + Tauri (Rust backend)

### 1.2 Trạng thái hiện tại (v23 hardening)

| Metric | Giá trị |
|--------|---------|
| Test suite | **183 passed** (tăng từ 98) |
| Ngôn ngữ chính | Python 80.5%, TypeScript 13.7%, JS 4.1% |
| Build desktop | ✅ Vite web shell |
| Tauri native | ⚠️ Chưa validate |
| Số commit | 2 (cực ít) |
| CI/CD | ❌ Không có |
| Tài liệu kế hoạch | ~200KB+ (Plan.md, enhanced_plan, pipeline_guides…) |

### 1.3 Điểm mạnh ghi nhận

- **Thiết kế tư tưởng tốt**: Ràng buộc No-LLM được tuân thủ nhất quán
- **EAPEE ma trận 4 chiều** (Genre × Relationship × Emotion × Gender) là thiết kế sáng tạo, hiếm trong RBMT mã nguồn mở
- **TM phân 3 tầng** (`machine`/`approved`/`reviewed`) cho phép governance chất lượng bản dịch
- **v23 hardening** đã tự nhận ra và bổ sung specificity conflict resolution, segment typing, protected span — cho thấy project đang tiến hóa đúng hướng

---

## 2. CẤU TRÚC PROJECT

### 2.1 🔴 Root directory vẫn còn ô nhiễm nặng sau v23

**Hiện trạng quan sát được:**

```
/ (root — trạng thái hiện tại)
├── all_global_errors.jsonl       ← log artifact bị commit
├── cedict_seeding_debug.txt      ← debug output bị commit
├── diagnose_results.json         ← artifact runtime bị commit
├── pos_db_audit.json             ← audit artifact bị commit
├── pos_diagnostic_results.json   ← diagnostic artifact bị commit
├── pos_rewrite_test_results.json ← test result artifact bị commit
├── trie_verification.json        ← verification artifact bị commit
├── implementation_plan.md.resolved    ← merge artifact
├── implementation_plan22.md.resolved  ← merge artifact
├── metadata_migration_plan.md.resolved
├── pipeline_guidev2.md.resolved
├── pipeline_guidev3.md.resolved
├── walkthrough.md.resolved
├── clean_dict.py                 ← utility script ở root
├── debug_regex.py                ← debug script ở root
├── debug_rewriter.py             ← debug script ở root
├── debug_zh_rewriter.py          ← debug script ở root
├── patch_nc2.py                  ← patch script ở root
├── patch_nc5.py                  ← patch script ở root
├── python                        ← file không có extension!
├── SVID_20260423_073257_1.mp4    ← binary media trong git
└── "Converter by DrDuc.json"     ← filename có khoảng trắng
```

README_VI.md (v23) tuyên bố đã cải thiện: *"Runner nằm trong `scripts/runners/`, utility dev trong `scripts/dev/`"* — nhưng phần lớn file trên vẫn còn hiện diện trong root. Đây là **tech debt tích lũy** chưa được dọn sạch.

**Hậu quả thực tế:**
- `git clone` sẽ tải về binary `.mp4` làm chậm mọi contributor
- `.jsonl`/`.json` artifact là state cụ thể của máy tác giả — commit vào repo gây confusion khi contributor khác chạy và có kết quả khác
- File `python` (không extension) hoàn toàn không rõ mục đích; có thể là symlink bị broken

**Khắc phục:**

```bash
# 1. Xóa toàn bộ artifacts khỏi git tracking
git rm all_global_errors.jsonl cedict_seeding_debug.txt \
       diagnose_results.json pos_*.json trie_verification.json \
       SVID_20260423_073257_1.mp4

# 2. Xóa .resolved files (merge artifacts)
git rm *.resolved

# 3. Thêm vào .gitignore
cat >> .gitignore << 'EOF'
# Runtime artifacts
*.jsonl
*_results.json
*_diagnostic*.json
*_audit.json
*_verification.json
*_debug.txt

# Media
*.mp4 *.avi *.mov *.mkv

# Merge artifacts
*.resolved
EOF

# 4. Làm rõ file "python"
file python  # Xem loại thực sự
# Nếu là script → đổi tên thành python_env_check.sh hoặc xóa
```

---

### 2.2 🔴 Hai kế hoạch triển khai song song mâu thuẫn nhau

**Vấn đề:** Repo chứa **hai bản kế hoạch triển khai hoàn toàn khác ngôn ngữ**:

| File | Ngôn ngữ | Engine | Status |
|------|----------|--------|--------|
| `Plan.md` (56KB) | Python | Python RBMT + SQLite Trie | Production path |
| `enhanced_translation_system_plan.md` (15KB) | **JavaScript** | JS modules, Node.js, Jest | ??? |

`enhanced_translation_system_plan.md` mô tả toàn bộ kiến trúc bằng JavaScript:
```
src/preprocessor/structure_preserver.js
src/preprocessor/hmm_viterbi_decoder.js
src/parser/morphological_analyzer.js
src/rules/syntax_transfer_rules.js
src/learning/translation_memory.js
```

Trong khi README_VI.md tuyên bố: *"Tài liệu/prototype JavaScript cũ đã được archive dưới `docs/archive/`"* — nhưng `enhanced_translation_system_plan.md` vẫn nằm ở **root**, không bị archive, không có nhãn deprecated.

**Rủi ro:** Contributor mới đọc file này sẽ bắt đầu implement bằng JS — sai hoàn toàn với production path.

**Khắc phục:**

```bash
# Ngay lập tức: thêm deprecation header
cat > /tmp/deprecation_header.md << 'EOF'
> ⚠️ **[DEPRECATED - KHÔNG DÙNG]** Tài liệu này mô tả phương án JavaScript
> đã bị loại bỏ. Production path là Python. Xem `Plan.md` để biết thiết kế
> hiện tại. File này được giữ lại chỉ để tham chiếu lịch sử.
EOF

# Hoặc tốt hơn: di chuyển vào docs/archive/
git mv enhanced_translation_system_plan.md docs/archive/
git mv *.resolved docs/archive/
```

---

### 2.3 🟡 `run_translate_ch01.py` / `run_translate_ch02.py` là anti-pattern

**Vấn đề:** Tồn tại 2 runner riêng biệt theo chương. Nếu không refactor, pattern này sẽ tạo ra `ch03.py`, `ch04.py`... đến `ch500.py`.

**Tuy nhiên**, README_VI.md ghi: *"Runner nằm trong `scripts/runners/`"* — có thể v23 đã refactor nhưng chưa xóa file cũ.

**Khắc phục xác nhận:**

```bash
# Kiểm tra và xóa nếu đã obsolete
ls scripts/runners/
# Nếu có run_pipeline.py hoặc run_translate.py với argument:
git rm run_translate_ch01.py run_translate_ch02.py

# Đảm bảo runner mới hỗ trợ:
# python scripts/runners/run_translate.py --chapter 01
# python scripts/runners/run_translate.py --range 01-10
# python scripts/runners/run_translate.py --all
```

---

### 2.4 🟡 Thư mục `Name project` vi phạm naming convention

**Vấn đề:** Thư mục tên `Name project` (có khoảng trắng). README_VI.md ghi: *"Name dictionaries: `name_project/`"* — gợi ý tên đúng là `name_project` nhưng thư mục thực tế vẫn có space.

**Hậu quả:** Cross-platform path issues trong CI/CD, Windows vs Linux shell escaping khác nhau.

```bash
git mv "Name project" name_project
# Cập nhật tất cả references trong code
grep -r "Name project" src/ scripts/ --include="*.py" | xargs sed -i 's/Name project/name_project/g'
```

---

### 2.5 🟡 Hai JSON file trùng nội dung, một cái có filename có space

**Hiện trạng root:**
- `Converter by DrDuc.json` (tên có space)
- `converter_by_drduc.json` (underscore)

Không rõ canonical version là gì; không có comment giải thích mục đích.

```bash
diff "Converter by DrDuc.json" converter_by_drduc.json
# Nếu giống nhau → xóa file có space
# Nếu khác nhau → document sự khác biệt rõ ràng
```

---

### 2.6 🟢 Video binary bị commit vào git

`SVID_20260423_073257_1.mp4` làm tăng kích thước repo không cần thiết. Host trên YouTube/Google Drive và link trong README.

---

## 3. THUẬT TOÁN TRIE & LPM

### 3.1 🔴 Viterbi segmentation trong Trie chưa xử lý catastrophic backtracking

**README_VI.md ghi nhận (v23):** *"Viterbi segmentation cho Trie"* — đây là cải tiến so với greedy LPM thuần túy.

**Tuy nhiên**, Viterbi segmentation trong Trie có một điểm yếu kinh điển khi gặp **regex-like patterns trong dictionary entries** hoặc **văn bản có chuỗi ký tự lặp lại**:

```python
# Ví dụ nguy hiểm:
input_text = "哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈"  # 17 chữ "哈"

# Nếu Trie có: 哈哈 → "haha", 哈哈哈 → "hahaha", 哈哈哈哈 → ...
# Viterbi phải duyệt tất cả các cách tổ hợp → exponential state space
# Với 17 chars: 2^16 = 65536 states trong worst case
```

Tiểu thuyết thường xuyên có: `啊啊啊啊啊`, `哈哈哈哈哈`, dấu chấm lửng `……………`, khoảng trắng lặp lại.

**Khắc phục:**

```python
# src/core/trie_engine.py
import re
import signal
from contextlib import contextmanager

# Thêm timeout guard cho Viterbi
@contextmanager
def viterbi_timeout(seconds=2):
    def handler(signum, frame):
        raise TimeoutError("Viterbi timeout")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Pre-normalize lặp ký tự trước khi đưa vào Trie
REPETITION_NORMALIZE = [
    (r'(哈){4,}', '哈哈哈'),      # Chuẩn hóa chuỗi cười dài
    (r'(啊){4,}', '啊啊啊'),      # Chuỗi cảm thán dài
    (r'(……){2,}', '……'),          # Nhiều dấu chấm lửng
    (r'([！]){3,}', '！！！'),    # Nhiều dấu chấm than
]

def normalize_repetitions(text: str) -> str:
    for pattern, replacement in REPETITION_NORMALIZE:
        text = re.sub(pattern, replacement, text)
    return text
```

---

### 3.2 🔴 One-Mean mode (`split(";")[0]`) mất thông tin ngữ cảnh quan trọng

**Thiết kế hiện tại:** Với P2/P3 (VietPhrase chung), từ có nhiều nghĩa được lấy nghĩa đầu tiên bằng `split(";")[0]`.

**Vấn đề thực tế:**

```
Từ: 打
Dict P2: "打" = "đánh;đánh dấu;gọi điện;mua;đập"

Trường hợp 1: 打电话 → "gọi điện thoại"
  → "打" nên là "gọi" nhưng split(";")[0] = "đánh"
  → Kết quả: "đánh điện thoại" ❌

Trường hợp 2: 打人 → "đánh người"
  → split(";")[0] = "đánh" ✅ (may mắn đúng)

Trường hợp 3: 打折 → "giảm giá"
  → split(";")[0] = "đánh" → "đánh gấp" ❌
```

One-Mean mode chỉ đúng khi nghĩa đầu tiên trong dictionary là nghĩa **phổ biến nhất**, nhưng không có cơ chế nào đảm bảo dictionary entries được sắp xếp theo tần suất.

**Khắc phục:**

```python
class SmartOneMeanResolver:
    """
    Thay thế split(";")[0] bằng context-aware selection.
    Không dùng LLM — dùng bigram co-occurrence từ dictionary.
    """
    def __init__(self, bigram_db_path: str):
        self.bigrams = self._load_bigrams(bigram_db_path)

    def resolve(self, token: str, right_context: str, all_meanings: list[str]) -> str:
        if len(all_meanings) == 1:
            return all_meanings[0]

        # Kiểm tra compound: nếu token + right_context[0:2] có trong dict → dùng nghĩa compound
        compound = token + right_context[:2]
        if compound in self.trie:
            return self.trie[compound]

        # Bigram scoring: nghĩa nào likely hơn khi đứng trước right_context?
        scores = {}
        for meaning in all_meanings:
            next_token = right_context[:3]  # 3 chars lookahead
            scores[meaning] = self.bigrams.get((meaning, next_token), 0.0)

        best = max(scores, key=scores.get)
        # Fallback: nếu tất cả score = 0 → dùng nghĩa đầu tiên
        return best if scores[best] > 0 else all_meanings[0]
```

---

### 3.3 🟡 Priority hệ thống P1–P5 không có cơ chế override tạm thời

**Thiết kế:** P5 (project-specific) luôn thắng P1 (phiên âm). Điều này đúng **99% thời gian**.

**Edge case không được xử lý:**

```
Dự án "Naruto" (Japanese origin):
P5 có entry: 林 → "Hayashi" (tên nhân vật người Nhật trong truyện)
P2 có entry: 林 → "Lâm" (Hán-Việt)

Chương 1-50: nhân vật Hayashi xuất hiện → P5 thắng ✅
Chương 51: tác giả đề cập "林木" (rừng cây) theo nghĩa thông thường
  → P5 vẫn thắng: "Hayashi mộc" ❌ (sai vì đây không phải tên nhân vật)
```

Không có cơ chế **"scope-limited P5"** — entry P5 được áp dụng blindly cho mọi occurrence kể cả khi không phải tên riêng.

**Khắc phục:**

```python
@dataclass
class TrieEntry:
    source: str
    target: str
    priority: int
    is_proper_noun: bool = False  # NEW: đánh dấu tên riêng vs từ thường
    apply_only_as_entity: bool = False  # NEW: chỉ áp dụng khi confirmed là entity

def trie_lookup_with_entity_check(token: str, context: str,
                                   entity_registry: set[str]) -> TrieEntry:
    entry = trie.lookup(token)
    if entry and entry.apply_only_as_entity:
        # Chỉ dùng P5 override khi token là entity đã xác nhận
        if token not in entity_registry:
            # Fallback về P2/P1
            return trie.lookup_fallback(token, max_priority=3)
    return entry
```

---

### 3.4 🟡 Hot-reload dictionary gây race condition trong batch processing

**Thiết kế:** *"Hot-reload: watch dictionary folder, rebuild incremental"*

**Vấn đề:** Nếu dictionary file thay đổi trong khi batch processing chương 50/500 đang chạy:

```
Timeline:
T=0:   Batch start, Trie loaded với version A
T=120s: User sửa dict, hot-reload kích hoạt
T=121s: Trie rebuild (version B)
T=122s: Chapter 51 dùng Trie version B
        Chapter 50 đang chạy dở với Trie version A (race!)

Kết quả: Chapter 49 (A) ≠ Chapter 51 (B) — inconsistent terminology
```

**Khắc phục:**

```python
class TrieEngine:
    def __init__(self):
        self._trie = None
        self._version = 0
        self._lock = threading.RWLock()
        self._pending_rebuild = False

    def hot_reload(self):
        """Mark pending rebuild — apply sau khi batch hiện tại hoàn thành."""
        self._pending_rebuild = True
        logger.info("Dictionary change detected. Reload scheduled after current batch.")

    def apply_pending_reload_if_needed(self, batch_checkpoint: bool = False):
        """Chỉ apply reload tại checkpoint (sau mỗi 10 chapters)."""
        if batch_checkpoint and self._pending_rebuild:
            with self._lock.write():
                self._rebuild_trie()
                self._pending_rebuild = False
                logger.info(f"Dictionary hot-reloaded at checkpoint. Version: {self._version}")
```

---

## 4. PIPELINE DỊCH THUẬT

### 4.1 🔴 Pipeline batch không có fault isolation — một chapter lỗi dừng toàn bộ

**Thiết kế hiện tại (từ Plan.md):**

```python
for chapter in chapters:
    translate(chapter)
    update_progress()
    if chapter_num % 10 == 0:
        checkpoint()
        run_qa_quick()
```

Không có `try/except`. Nếu chapter 47/500 gặp:
- Ký tự Unicode lạ (surrogate pairs)
- Catastrophic regex backtracking
- Memory spike (chương rất dài)
- Encoding edge case

→ **Toàn bộ 500-chapter job crash, mất tiến độ**. Đây là vấn đề nghiêm trọng nhất về reliability trong production.

**Khắc phục:**

```python
# src/pipeline/robust_batch_runner.py
from enum import Enum
from dataclasses import dataclass, field
import traceback
import signal

class ChapterStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"

@dataclass
class ChapterResult:
    chapter_id: str
    status: ChapterStatus
    duration_seconds: float = 0.0
    error_type: str | None = None
    error_detail: str | None = None
    output_path: str | None = None
    segments_translated: int = 0
    tm_reuse_rate: float = 0.0

def run_batch_with_fault_isolation(
    chapters: list,
    translator,
    config: BatchConfig
) -> BatchReport:
    results: list[ChapterResult] = []
    consecutive_failures = 0

    for chapter in chapters:
        result = _translate_chapter_safe(chapter, translator, config)
        results.append(result)

        if result.status == ChapterStatus.SUCCESS:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            logger.error(f"Chapter {chapter.id} failed: {result.error_type} — {result.error_detail}")

            # Circuit breaker: 5 failures liên tiếp → dừng và alert
            if consecutive_failures >= config.circuit_breaker_threshold:
                logger.critical(f"Circuit breaker triggered after {consecutive_failures} consecutive failures!")
                _send_alert(results, config)
                break

        # Checkpoint sau mỗi N chapters dù có lỗi hay không
        if chapter.num % config.checkpoint_interval == 0:
            _save_checkpoint(results, translator.state)
            translator.trie.apply_pending_reload_if_needed(batch_checkpoint=True)

    return BatchReport(results)

def _translate_chapter_safe(chapter, translator, config) -> ChapterResult:
    start = time.monotonic()
    try:
        with translation_timeout(config.chapter_timeout_seconds):
            output = translator.translate_chapter(chapter)
        return ChapterResult(
            chapter_id=chapter.id,
            status=ChapterStatus.SUCCESS,
            duration_seconds=time.monotonic() - start,
            output_path=output.path,
            segments_translated=output.segment_count,
            tm_reuse_rate=output.tm_reuse_rate
        )
    except TimeoutError:
        return ChapterResult(chapter.id, ChapterStatus.TIMEOUT,
                             error_type="TimeoutError",
                             error_detail=f"Exceeded {config.chapter_timeout_seconds}s")
    except UnicodeError as e:
        return ChapterResult(chapter.id, ChapterStatus.FAILED,
                             error_type="UnicodeError", error_detail=str(e))
    except MemoryError:
        return ChapterResult(chapter.id, ChapterStatus.FAILED,
                             error_type="MemoryError",
                             error_detail="Chapter too large, consider splitting")
    except Exception as e:
        return ChapterResult(chapter.id, ChapterStatus.FAILED,
                             error_type=type(e).__name__,
                             error_detail=traceback.format_exc()[-500:])
```

---

### 4.2 🔴 Structure Preservation không xử lý nested placeholders

**Thiết kế hiện tại:** Wrapping bằng `[TABLE_001]...[/TABLE_001]`.

**Vấn đề với nested structures:**

```
Input:
<table>
  <tr>
    <td>Công thức: <math>E = mc²</math></td>
    <td>Code: <code>print("hello")</code></td>
  </tr>
</table>

# Regex wrap TABLE trước: [TABLE_001]<tr><td>...[MATH_001]...[/MATH_001]...[CODE_001]...[/CODE_001]...</td></tr>[/TABLE_001]
# Sau dịch và restore:
#   Nếu restore theo thứ tự alphabet: CODE_001 → MATH_001 → TABLE_001 ✅
#   Nếu restore theo thứ tự xuất hiện: TABLE_001 first →
#     [TABLE_001] chưa có nội dung đầy đủ vì MATH/CODE chưa restore ❌
```

**Khắc phục:**

```python
# src/engine/structure_preserver.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Placeholder:
    id: str
    original: str
    depth: int          # 0 = top-level, 1 = nested, 2 = double-nested...
    parent_id: Optional[str] = None
    children_ids: list[str] = field(default_factory=list)

class StructurePreserver:
    def wrap(self, text: str) -> tuple[str, dict[str, Placeholder]]:
        placeholders: dict[str, Placeholder] = {}
        depth_stack: list[str] = []  # Stack of current parent placeholder IDs

        def wrap_match(match, struct_type: str) -> str:
            pid = f"[{struct_type}_{len(placeholders):03d}]"
            parent = depth_stack[-1] if depth_stack else None
            depth = len(depth_stack)

            ph = Placeholder(id=pid, original=match.group(0),
                             depth=depth, parent_id=parent)
            placeholders[pid] = ph

            if parent:
                placeholders[parent].children_ids.append(pid)

            depth_stack.append(pid)
            # Recursive wrap nội dung bên trong
            inner = self.wrap(match.group(1))[0]  # Recurse!
            depth_stack.pop()
            return pid

        # ... áp dụng patterns
        return text, placeholders

    def restore(self, text: str, placeholders: dict[str, Placeholder]) -> str:
        """Restore theo thứ tự depth-first (innermost first)."""
        # Sort: depth cao nhất trước
        ordered = sorted(placeholders.values(), key=lambda p: -p.depth)
        for ph in ordered:
            text = text.replace(ph.id, ph.original)
        return text
```

---

### 4.3 🟡 Context Window không phân biệt "chapter start" vs "mid-chapter"

**Thiết kế:** Sliding window 5 câu trước + 5 câu sau. Câu đầu của chapter N lấy 5 câu cuối của chapter N-1 làm context — đúng về tính liên tục, nhưng **không reset các state cần reset**.

**Vấn đề cụ thể:**

| State | Hành vi mong muốn tại chapter boundary | Hành vi hiện tại |
|-------|----------------------------------------|-----------------|
| `emotion_state` | Reset (time skip thường xảy ra) | Carry-over ❌ |
| `active_dialogue_pair` | Reset (scene kết thúc) | Carry-over ❌ |
| `scene_location` | Reset nếu không có continuity signal | Carry-over ❌ |
| `active_characters` | GIỮ (nhân vật vẫn tồn tại) | ✅ |
| `relationship_graph` | GIỮ (quan hệ không đổi) | ✅ |
| `glossary_cache` | GIỮ (thuật ngữ vẫn áp dụng) | ✅ |

**Khắc phục:**

```python
# src/engine/context_manager.py
CHAPTER_BOUNDARY_RESET = frozenset([
    'emotion_state', 'emotion_age', 'emotion_intensity',
    'active_dialogue_pair', 'last_speaker', 'last_listener',
    'scene_location', 'active_scene_mood',
])

CHAPTER_BOUNDARY_PRESERVE = frozenset([
    'active_characters', 'relationship_graph', 'glossary_cache',
    'cultivation_realms', 'faction_memberships', 'worldview_id',
    'chapter_summaries',  # Thêm summary của chapter vừa xong
])

class ContextManager:
    def on_chapter_boundary(self, finished_chapter_num: int):
        # Tạo summary của chapter vừa xong
        summary = self._summarize_chapter(finished_chapter_num)
        self.chapter_summaries[finished_chapter_num] = summary

        # Selective reset
        for field in CHAPTER_BOUNDARY_RESET:
            if hasattr(self, field):
                setattr(self, field, self._get_default(field))

        logger.debug(f"Chapter boundary {finished_chapter_num}→{finished_chapter_num+1}: "
                     f"reset {len(CHAPTER_BOUNDARY_RESET)} fields, "
                     f"preserved {len(CHAPTER_BOUNDARY_PRESERVE)} fields")
```

---

### 4.4 🟡 Number Converter thiếu xử lý số ordinal và phân số

**Thiết kế:** `一百二十三 → 123`, `三千年 → 3000 năm`, `第X → thứ X`.

**Các trường hợp chưa được đề cập:**

```python
# Phân số và tỷ lệ
三分之一   → 1/3 hoặc "một phần ba"   (tùy ngữ cảnh)
百分之五十 → 50%

# Số thập phân
三点一四   → 3.14

# Số La Mã trong mixed text (tiểu thuyết dịch từ phương Tây)
第VII章    → Chương VII hay Chương 7?

# Đơn vị tiền tệ
一百万元   → 1.000.000 tệ / 1 triệu nhân dân tệ
三千金币   → 3.000 đồng vàng (game context)

# Thời gian chi tiết
凌晨三点一刻 → 3 giờ 15 phút sáng
```

**Khắc phục:** Mở rộng `number_converter.py` với regex patterns cho từng loại, áp dụng theo thứ tự từ phức tạp nhất đến đơn giản nhất (tránh partial match).

---

### 4.5 🟡 Không có resumable batch — pipeline restart phải chạy lại từ đầu

**Vấn đề:** Nếu máy crash giữa chapter 300/500, tiến trình phải restart từ chương 1 (hay checkpoint gần nhất nếu có checkpoint).

**Khắc phục — Resume từ bất kỳ chapter nào:**

```python
# src/state/project_manager.py
class ProjectManager:
    def get_pending_chapters(self) -> list[Chapter]:
        """Trả về list chapters chưa SUCCESS."""
        all_chapters = self._load_chapter_list()
        completed = self._load_completed_set()  # từ SQLite
        failed = self._load_failed_set()

        return [c for c in all_chapters
                if c.id not in completed
                and c.id not in failed]  # Skip failed, retry explicit

    def mark_complete(self, chapter_id: str, output_path: str):
        self._db.execute(
            "INSERT OR REPLACE INTO chapter_status VALUES (?, 'SUCCESS', ?, datetime('now'))",
            (chapter_id, output_path)
        )

# Trong runner:
pending = pm.get_pending_chapters()
logger.info(f"Resuming: {len(pending)} chapters remaining")
run_batch_with_fault_isolation(pending, translator, config)
```

---

## 5. HỆ THỐNG EAPEE

### 5.1 🔴 Emotion Detector không xử lý negation và giả vờ

**Thiết kế:** Keyword matching + dialogue verb mapping. Đây là cốt lõi, nhưng:

**Vấn đề negation:**

```python
input_1 = "他没有愤怒，脸色平静"   # Anh ta KHÔNG tức giận, mặt bình thản
# Detector: tìm thấy "愤怒" → emotion = angry, intensity = 2 ❌
# Correct:  emotion = neutral (hoặc cold)

input_2 = "她强忍着愤怒"            # Cô ấy cố nén cơn tức giận
# Detector: "愤怒" → angry ✅ (đúng vì cô ấy ĐANG tức)

input_3 = "他装作愤怒的样子"        # Anh ta GIẢ VỜ tức giận
# Detector: "愤怒" → angry ❌ (thực tế là deceptive/neutral)
```

**Vấn đề metaphor:**

```python
input_4 = "他的心如死灰"            # Lòng anh như tro tàn (buồn bã sâu sắc)
# Detector: không có keyword trực tiếp → neutral ❌
# Correct: sad (intensity 4)

input_5 = "他冷如寒冰，不发一语"    # Lạnh như băng, không nói một lời
# Detector: "冷" → cold ✅ nhưng intensity underestimated
```

**Khắc phục:**

```python
# src/eapee/emotion_detector.py

NEGATION_SCOPE_WORDS = frozenset(['没有', '不', '未', '无', '非', '并非', '绝非'])
PRETEND_WORDS = frozenset(['装作', '假装', '伪装', '装出', '佯装'])
SUPPRESS_WORDS = frozenset(['强忍', '压制', '克制', '忍住'])

def detect_emotion_v2(sentence: str, prev_context: EmotionContext) -> tuple[str, int]:
    # Step 1: Tìm vùng phủ định
    negation_zones = _find_negation_zones(sentence, NEGATION_SCOPE_WORDS)
    pretend_zones  = _find_negation_zones(sentence, PRETEND_WORDS)

    scores: dict[str, float] = defaultdict(float)

    # Step 2: Scan keywords với negation check
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            pos = sentence.find(kw)
            if pos == -1:
                continue
            if _in_zone(pos, negation_zones):
                scores['neutral'] += 1.0   # Phủ định → nghiêng về neutral
                continue
            if _in_zone(pos, pretend_zones):
                continue  # Giả vờ → bỏ qua hoàn toàn
            # SUPPRESS: cảm xúc vẫn hiện diện nhưng intensity giảm
            intensity_modifier = 0.6 if _in_zone(pos, SUPPRESS_WORDS) else 1.0
            scores[emotion] += keyword_weight(kw) * intensity_modifier

    # Step 3: Metaphor matching (separate dictionary)
    for pattern, (emotion, weight) in METAPHOR_EMOTION_PATTERNS.items():
        if re.search(pattern, sentence):
            scores[emotion] += weight

    # Step 4: Dialogue verb (strongest signal, không bị negation ảnh hưởng)
    verb = _extract_dialogue_verb(sentence)
    if verb and (verb_emotion := VERB_EMOTION_MAP.get(verb)):
        scores[verb_emotion] += 3.0

    if not scores:
        return 'neutral', 0
    top_emotion = max(scores, key=scores.get)
    return (top_emotion, 0) if scores[top_emotion] < 1.5 else (top_emotion, min(5, int(scores[top_emotion])))
```

---

### 5.2 🔴 Pronoun 4D Matrix thiếu fallback chain tường minh

**Thiết kế:** `Pronoun = f(Genre, Relationship, Emotion, Gender)`.

**Vấn đề:** Khi không có entry trong ma trận cho tổ hợp cụ thể, hành vi fallback **không được định nghĩa**. Ví dụ:

```
Genre: horror (ma quái — chưa có trong ma trận)
Relationship: master_spirit → disciple
Emotion: terrified
Gender: male → female

→ Ma trận tra không có entry → ???
→ Crash? → dùng ("ta","ngươi")? → không ai biết
```

Thêm nữa, **conflict resolution khi các chiều mâu thuẫn** không được document:

```
Identity: character là Tông Chủ → bổn tọa (highest priority)
Emotion: furious (intensity=5) → thường override thành ta/ngươi

Theo Plan.md: "Identity pronouns có priority cao nhất, ghi đè emotion-based"
Nhưng intensity=5 (cuồng nộ cực độ) có override Identity không? Không rõ.
```

**Khắc phục:**

```python
# src/eapee/pronoun_resolver.py

RESOLUTION_CHAIN = [
    ('identity_override',    _try_identity_override),    # Hoàng đế, Tông Chủ...
    ('explicit_emotion_high',_try_high_intensity),       # intensity >= 4 override hầu hết
    ('full_4d',              _try_full_matrix),          # Genre × Rel × Emotion × Gender
    ('rel_emotion_3d',       _try_rel_emotion),          # Rel × Emotion (drop genre)
    ('rel_only_2d',          _try_rel_only),             # Rel × neutral (drop emotion)
    ('genre_default',        _try_genre_default),        # Chỉ genre default
    ('universal_fallback',   lambda *_: ('ta', 'ngươi')),# Never fails
]

def resolve_pronoun(speaker: Character, listener: Character,
                    genre: str, emotion: str, intensity: int) -> tuple[str, str]:
    for strategy_name, strategy_fn in RESOLUTION_CHAIN:
        result = strategy_fn(speaker, listener, genre, emotion, intensity)
        if result is not None:
            logger.debug(f"Pronoun resolved via '{strategy_name}': {result}")
            return result
    return ('ta', 'ngươi')  # Unreachable, nhưng type-safe
```

---

### 5.3 🟡 Emotion Decay hoàn toàn cứng nhắc — không nhạy với context

**Thiết kế:** `angry → 5 câu`, `furious → 8 câu` (cố định).

**Bất hợp lý:**

```
# Tình huống 1: Cảnh chiến đấu kéo dài (50 câu hành động liên tục)
# → angry decay sau đúng 5 câu, câu 6 dùng pronoun neutral — SAI

# Tình huống 2: Sau khi nhân vật hít thở sâu, nhìn lên trời
# → angry nên decay ngay lập tức, không cần đợi 5 câu

# Tình huống 3: Scene break ***
# → Emotion nên reset ngay lập tức
```

**Khắc phục:**

```python
SCENE_BREAK_SIGNALS = frozenset(['***', '---', '===', '※', '▼', '◆'])
ESCALATION_KEYWORDS = frozenset(['更加', '愈发', '越来越', '彻底', '怒火中烧'])
CALM_DOWN_KEYWORDS  = frozenset(['深吸', '平复', '冷静下来', '放松', '叹了口气', '无奈'])

class EmotionStateMachine:
    def step(self, new_sentence: str, new_emotion: str, new_intensity: int):
        # Scene break → hard reset
        if any(sig in new_sentence for sig in SCENE_BREAK_SIGNALS):
            self._reset()
            return

        # New emotion detected → override
        if new_intensity > 0 and new_emotion != 'neutral':
            self.emotion = new_emotion
            self.intensity = new_intensity
            self.age = 0
            return

        # Trong trạng thái hiện tại: kiểm tra decay signals
        if any(kw in new_sentence for kw in CALM_DOWN_KEYWORDS):
            self.age += 3   # Accelerate decay
        elif any(kw in new_sentence for kw in ESCALATION_KEYWORDS):
            self.age = max(0, self.age - 1)  # Slow decay
        else:
            self.age += 1

        max_age = DECAY_RULES.get(self.emotion, 3)
        # Intensity modifier: intensity 5 kéo dài gấp đôi
        effective_max = int(max_age * (0.5 + self.intensity / 5.0))
        if self.age >= effective_max:
            self._reset()
```

---

### 5.4 🟡 Gender Detection chỉ dựa vào 他/她 — thiếu sót với nhân vật phức tạp

**Vấn đề:**

```
# 1. 它 (vật/linh thú) dễ bị nhầm với 他 (nam)
# 2. Nhân vật bí ẩn: "那人" không có pronoun → gender = unknown → fallback sai
# 3. Linh thú hóa nhân: đôi khi tác giả dùng 它 đôi khi 他 cho cùng một nhân vật
# 4. Xuyên thể: nhân vật đổi gender giữa chừng → gender cần được update
```

**Khắc phục:** Xây dựng gender detection đa nguồn tín hiệu:

```python
FEMALE_SIGNALS = ['她', '美女', '仙子', '女子', '少女', '姑娘', '夫人', '娘子',
                  '女弟子', '女侠', '小姐', '妹子', '女儿', '母亲', '妻子']
MALE_SIGNALS   = ['他', '男子', '少年', '公子', '男弟子', '武者', '剑客', '儿子', '父亲']
AMBIGUOUS      = ['修士', '强者', '前辈', '存在', '那人', '此人']

def detect_character_gender(name: str, full_text_sample: str) -> str:
    """Scan 20 sentences around each occurrence of name for gender signals."""
    female_score = 0
    male_score = 0

    for match in re.finditer(re.escape(name), full_text_sample):
        start = max(0, match.start() - 200)
        end   = min(len(full_text_sample), match.end() + 200)
        context = full_text_sample[start:end]

        for sig in FEMALE_SIGNALS:
            if sig in context: female_score += (3 if sig in ['她'] else 1)
        for sig in MALE_SIGNALS:
            if sig in context: male_score += (3 if sig in ['他'] else 1)

    if female_score > male_score * 1.5: return 'female'
    if male_score > female_score * 1.5: return 'male'
    return 'unknown'  # Rõ ràng là unknown, không default male
```

---

## 6. GRAMMAR TRANSFER ENGINE

### 6.1 🔴 Dependency Parser không xử lý pro-drop của tiếng Trung

**Vấn đề kinh điển của tiếng Trung:** Subject/Object thường bị lược bỏ (pro-drop).

```
# Câu gốc: "看到她，微微一笑" (Nhìn thấy cô ấy, [anh ta] khẽ mỉm cười)
# Subject "他" bị lược hoàn toàn

# Dependency parser hiện tại:
#   Verb: "看到", "微微一笑"
#   Object: "她"
#   Subject: ??? → Không tìm thấy

# Nếu không resolve pro-drop:
#   Output: "Nhìn thấy cô ấy, khẽ mỉm cười" — tiếng Việt cũng chấp nhận được
# Nhưng với xưng hô:
#   "他对她说" (anh ấy nói với cô ấy) → nếu pro-drop đoạn sau:
#   "转身离去" (quay người bỏ đi) — ai quay? Không biết → pronoun resolver crash
```

**Khắc phục:**

```python
class ProDropResolver:
    """
    Giải quyết pro-drop: tìm subject/object bị lược trong context window.
    Không dùng LLM — dùng co-reference chain từ dialogue tracking.
    """
    def resolve_missing_subject(self, sentence: str, context: ContextWindow) -> str | None:
        # 1. Nếu câu là dialogue và speaker đã xác định → subject = speaker
        if context.active_speaker:
            return context.active_speaker

        # 2. Nếu câu trước có explicit subject → carry-forward
        if context.last_explicit_subject:
            age = context.sentences_since_last_explicit
            if age <= 3:  # Carry-forward tối đa 3 câu
                return context.last_explicit_subject

        # 3. Heuristic: Subject thường là protagonist nếu không có cue
        return context.scene_focus_character  # Nhân vật đang "được focus"

    def annotate_sentence(self, sentence: str, context: ContextWindow) -> str:
        """Thêm [SUBJ:name] annotation để pronoun resolver sử dụng."""
        if not has_explicit_subject(sentence):
            subj = self.resolve_missing_subject(sentence, context)
            if subj:
                return f"[SUBJ:{subj}] {sentence}"
        return sentence
```

---

### 6.2 🟡 Passive voice "被" resolver chỉ dùng 2 nhãn (được/bị) — quá đơn giản

**Thiết kế từ enhanced_plan:** *"Ma trận nội hàm 4D phân tích cực cảm xúc — ánh xạ '被' thành 'được' (tích cực) hoặc 'bị' (tiêu cực)"*

**Vấn đề:**

```
被爱      → được yêu        (tích cực ✅)
被打      → bị đánh         (tiêu cực ✅)
被选中    → được chọn       (tích cực ✅)
被杀死    → bị giết chết     (tiêu cực ✅)

Nhưng:
被批评    → bị phê bình (tiêu cực) hay được góp ý (trung lập/tích cực)?
            → Phụ thuộc hoàn toàn vào context và perspective của narrator
被迫      → bị ép buộc (seldom "được ép" ✅ always negative)
被遗忘    → bị lãng quên (usually negative, nhưng có thể "được quên lãng" trong Phật giáo context)
被曝光    → bị lộ/phơi bày (negative for villain, neutral for journalist)
```

Chỉ dùng 2 nhãn + emotion heuristic là **không đủ**. Cần từ điển "valence" cho từng verbal complement.

**Khắc phục:**

```python
# data/dictionaries/global/grammar/passive_valence.md
# Format: verb_complement → valence_score (-2 to +2) + notes
PASSIVE_VALENCE = {
    '爱':   +2,   # được/bị yêu → luôn "được"
    '恨':   -2,   # bị ghét → luôn "bị"
    '打':   -2,   # bị đánh → luôn "bị"
    '选':   +1,   # được chọn → thường "được"
    '批评': -1,   # bị phê bình → thường "bị"
    '曝光':  0,   # context-dependent → default "bị", nhưng check narrator POV
}

def resolve_passive(verb: str, context_emotion: str, narrator_pov: str) -> str:
    valence = PASSIVE_VALENCE.get(verb, 0)
    if valence > 0:  return "được"
    if valence < 0:  return "bị"
    # valence == 0: context-dependent
    if narrator_pov == 'villain' and context_emotion in ('angry', 'threatening'):
        return "bị"
    return "được" if context_emotion in ('happy', 'grateful') else "bị"
```

---

### 6.3 🟡 GrammarTransferEngine thiếu xử lý V-得-C (Potential complement)

**Từ enhanced_plan (JS version):** *"Potential Complement: nhận dạng [V]+得/不+[C] → triệt tiêu '得'/'不' → chuyển hóa thành trợ từ năng nguyện"*

**Thiếu xót khi V-得-C là câu hỏi:**

```
他跑得了吗？ → Anh ấy có thể chạy thoát không?
     ↑ 了 là aspect marker, KHÔNG phải complement

他吃得完吗？ → Anh ấy có thể ăn hết không?
          ↑ 完 là resultative complement ✅

他吃得了吗？ → Anh ấy có thể ăn được không? / Anh ấy có ổn để ăn không?
         ↑ 了 ở đây là potential complement (ambiguous với aspect marker!)
```

Grammar Transfer Engine cần phân biệt `了` trong V-得-了 (potential complement) vs `了` là aspect marker — hai trường hợp cho kết quả dịch hoàn toàn khác nhau.

**Khắc phục:** Bổ sung context check: nếu pattern `V-得/不-了` xuất hiện trong clause có `吗` hoặc dạng câu nghi vấn → treat as potential complement; otherwise default to aspect marker.

---

## 7. TRANSLATION MEMORY

### 7.1 🔴 TM Fuzzy match dùng edit distance — nguy cơ reuse bản dịch có nghĩa ngược

**Thiết kế:** Fuzzy match với Levenshtein ≤ 15%.

**Vấn đề nghiêm trọng:**

```
Segment A (TM entry): "他修为大涨，突破了金丹境界"
  → "Tu vi của hắn tăng vọt, đột phá Kim Đan cảnh giới"

Segment B (new input): "他修为大跌，跌落了金丹境界"
  Levenshtein distance: chỉ 3 chars khác (涨↔跌, 突破↔跌落)
  → 15% threshold → MATCH → reuse bản dịch của A cho B

Output B: "Tu vi của hắn tăng vọt, đột phá Kim Đan cảnh giới" ❌
Correct B: "Tu vi của hắn sụt giảm, rớt khỏi Kim Đan cảnh giới"
```

**Khắc phục:**

```python
# src/state/translation_memory.py

SEMANTIC_ANTONYM_PAIRS = [
    # Cultivation
    ('大涨', '大跌'), ('突破', '跌落'), ('晋升', '降级'),
    ('增加', '减少'), ('提升', '下降'), ('成功', '失败'),
    # Emotion
    ('高兴', '悲伤'), ('胜利', '失败'), ('生', '死'),
    ('爱', '恨'), ('希望', '绝望'),
    # Action
    ('前进', '后退'), ('进攻', '防守'), ('召唤', '驱散'),
]

def has_semantic_antonym_conflict(s1: str, s2: str) -> bool:
    """True nếu s1 và s2 chứa một cặp antonym → nghĩa ngược nhau."""
    for a, b in SEMANTIC_ANTONYM_PAIRS:
        if (a in s1 and b in s2) or (b in s1 and a in s2):
            return True
    return False

def fuzzy_match(self, source: str, threshold: float = 0.85) -> list[TMEntry] | None:
    candidates = []
    for entry in self.entries:
        # Bước 1: Semantic antonym check TRƯỚC khi tính edit distance
        if has_semantic_antonym_conflict(source, entry.source):
            continue  # Hard reject

        # Bước 2: Token-level Jaccard thay vì char-level Levenshtein
        sim = _jaccard_token_similarity(source, entry.source)
        if sim >= threshold:
            candidates.append((entry, sim))

    return sorted(candidates, key=lambda x: x[1], reverse=True) or None
```

---

### 7.2 🟡 TM 3 tầng thiếu promotion/demotion workflow rõ ràng

**Thiết kế (v23):** `tm_machine` → `tm_approved` → `tm_reviewed`

**Vấn đề:** Không có tài liệu về:
- Điều kiện gì để promote `tm_machine` → `tm_approved`? (User action? Automatic confidence threshold?)
- Nếu `tm_approved` entry sau này phát hiện sai → có thể demote không?
- Khi dùng TM lookup, ưu tiên tầng nào? (`tm_reviewed` > `tm_approved` > `tm_machine`?)
- Entry trong `tm_approved` có override P5 dictionary không?

**Khắc phục:**

```python
# src/state/translation_memory.py — document policy rõ ràng

TM_TIER_PRIORITY = {
    'tm_reviewed': 10,   # Cao nhất: đã được human review
    'tm_approved': 7,    # Trung: user approved
    'tm_machine':  3,    # Thấp: machine-generated only
}

# Promotion policy
PROMOTION_RULES = {
    'machine_to_approved': 'explicit_user_action',  # KHÔNG tự động
    'approved_to_reviewed': 'explicit_review_action',
}

# Demotion policy
DEMOTION_RULES = {
    'reviewed_to_approved': 'user_flag_incorrect',
    'approved_to_machine':  'user_flag_incorrect',
}

# Lookup priority: tier cao nhất thắng; nếu cùng tier → similarity cao nhất thắng
# TM KHÔNG override P5 dictionary; P5 luôn thắng TM (names are canonical)
```

---

### 7.3 🟡 Incremental Learning thiếu cơ chế "catastrophic forgetting" prevention

**Thiết kế (từ enhanced_plan):** *"Rule induction từ post-editing feedback"* + *"Tránh catastrophic forgetting"*

**Vấn đề:** Chỉ đề cập mục tiêu, không có mechanism cụ thể. Với suffix array approach:

```
Project 1: "修为" → "tu vi" (consistent, high-frequency)
Project 2: translator gặp bản dịch "修为 → năng lực" → học rule mới
→ Rule mới override rule cũ
→ Project 3: "修为" → "năng lực" (mặc dù convention là "tu vi") ← Catastrophic forgetting
```

**Khắc phục — EWC (Elastic Weight Consolidation) đơn giản cho rule-based system:**

```python
class RuleInductionEngine:
    def learn_from_feedback(self, source: str, correction: str,
                            context: ProjectContext):
        new_rule = self._extract_rule(source, correction)

        if new_rule is None:
            return

        existing = self.rule_registry.get(new_rule.pattern)
        if existing:
            # Consolidation: weight mới dựa trên frequency của rule cũ
            old_weight = existing.frequency_weight
            # Nếu rule cũ rất phổ biến → giảm learning rate
            learning_rate = 1.0 / (1.0 + 0.1 * old_weight)
            new_rule.confidence = existing.confidence * (1 - learning_rate) + \
                                   new_rule.base_confidence * learning_rate

            # Hard floor: rule cũ không thể bị giảm confidence quá 70%
            new_rule.confidence = max(new_rule.confidence, existing.confidence * 0.7)

        # Tag rule với project_id để có thể trace nguồn gốc
        new_rule.source_project = context.project_id
        self.rule_registry.upsert(new_rule)
```

---

## 8. QA & TESTING

### 8.1 🔴 183 tests nhưng không có integration test end-to-end

**Vấn đề:** "183 passed" là unit tests. Không có bằng chứng về:
- Test pipeline từ raw Chinese text → Vietnamese output hoàn chỉnh
- Test với file thực tế (HTML, DOCX, TXT)
- Test với các thể loại khác nhau (xianxia, modern, horror)
- Performance benchmark (< 5s/3000 chars như spec)

**Khắc phục:**

```python
# tests/integration/test_full_pipeline.py
import pytest
import time
from pathlib import Path

SAMPLE_DIR = Path("tests/fixtures/chapters")

class TestFullPipelineIntegration:
    @pytest.fixture(scope="class")
    def translator(self):
        from src.engine.rbmt_translator import RBMTTranslator
        t = RBMTTranslator.from_config("tests/fixtures/test_config.json")
        t.warm_up()
        return t

    def test_xianxia_short_chapter(self, translator):
        source = (SAMPLE_DIR / "xianxia_ch001_short.txt").read_text()
        result = translator.translate(source)
        assert result.output_text, "Output must not be empty"
        assert result.untranslated_ratio < 0.05, "Max 5% untranslated"

    def test_performance_3000_chars(self, translator):
        source = (SAMPLE_DIR / "benchmark_3000chars.txt").read_text()
        assert len(source) >= 3000
        start = time.monotonic()
        result = translator.translate(source)
        duration = time.monotonic() - start
        assert duration < 5.0, f"Performance target: <5s, got {duration:.2f}s"

    def test_structure_preservation(self, translator):
        source = (SAMPLE_DIR / "with_tables_and_math.md").read_text()
        result = translator.translate(source)
        # Kiểm tra LaTeX nguyên vẹn
        assert "E=mc²" in result.output_text or "E = mc^2" in result.output_text
        # Kiểm tra tables còn đủ cột
        assert result.table_integrity_check()

    def test_batch_fault_tolerance(self, translator):
        """Batch không dừng khi 1 chapter lỗi."""
        chapters = [
            MockChapter("001", valid=True),
            MockChapter("002", valid=False, raise_exception=UnicodeError),
            MockChapter("003", valid=True),
        ]
        from src.pipeline.robust_batch_runner import run_batch_with_fault_isolation
        report = run_batch_with_fault_isolation(chapters, translator, config=default_config())

        assert report.success_count == 2
        assert report.failed_count == 1
        assert report.results["002"].status == ChapterStatus.FAILED
        assert report.results["003"].status == ChapterStatus.SUCCESS
```

---

### 8.2 🟡 QA Engine thiếu baseline từ bản dịch đã có

**Vấn đề:** README đề cập đến "24 dự án cũ" đã dịch. Đây là **golden dataset** hoàn hảo để đánh giá accuracy, nhưng không có evidence về việc xây dựng benchmark từ chúng.

**Khắc phục:**

```python
# scripts/tools/build_golden_benchmark.py
"""
Xây dựng golden benchmark từ 24 dự án đã dịch để đo regression.
Chạy 1 lần, kết quả lưu vào tests/fixtures/golden/
"""

def extract_golden_pairs(project_path: Path, sample_size: int = 100) -> list[GoldenPair]:
    """Trích xuất N cặp (source_zh, reference_vi) đã được human-approved."""
    tm = load_tm_reviewed(project_path)  # Chỉ dùng tm_reviewed tier
    pairs = tm.get_all_approved_pairs()
    # Sample diverse: ngắn/dài, dialogue/narrative, nhiều genre
    return stratified_sample(pairs, sample_size)

# Sau đó trong CI:
# python -m pytest tests/benchmark/test_accuracy.py --golden-path tests/fixtures/golden/
```

---

### 8.3 🟡 Không có CI/CD — không phát hiện regression

**Hiện trạng:** Repo có `/.agents/workflows/` (agent task files) nhưng KHÔNG có `.github/workflows/*.yml`.

**Hậu quả trực tiếp:** Không biết khi nào code bị regress. "183 passed" hôm nay, nhưng commit tiếp theo có thể phá vỡ 10 tests mà không ai biết cho đến khi chạy tay.

**Khắc phục:**

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e ".[dev]"
      - run: python -m pytest --tb=short --cov=src --cov-report=xml -q
      - uses: codecov/codecov-action@v4

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install ruff mypy
      - run: ruff check src/
      - run: mypy src/ --ignore-missing-imports --no-error-summary

  desktop-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd desktop && npm ci && npm run build

  # Optional: Validate Tauri native build (slow, run weekly)
  # tauri-build:
  #   runs-on: [ubuntu-latest, windows-latest, macos-latest]
  #   ...
```

---

## 9. DEVOPS & MAINTAINABILITY

### 9.1 🟡 pyproject.toml thiếu dependency pinning

**Hiện trạng:**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]

[project]
requires-python = ">=3.11"
# Không có dependencies list!
```

Không có dependencies được khai báo trong `pyproject.toml`. Nếu `requirements.txt` cũng không pin exact versions, environment reproduction là không đảm bảo.

**Khắc phục:**

```toml
[project]
name = "drduc-translator"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "chardet>=5.2.0,<6.0",
    "pydantic>=2.4.0,<3.0",
    "jieba>=0.42.1",
    # ... thêm tất cả runtime deps
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.9",
    "mypy>=1.5.0",
]

[project.scripts]
drduc-translate = "src.cli:main"  # Thêm CLI entry point
```

---

### 9.2 🟡 Chỉ 2 commits — không thể trace lịch sử thay đổi

**Hiện trạng:** Repository chỉ có **2 commits** dù project đã ở v23 (rất nhiều iteration).

**Vấn đề:** Toàn bộ lịch sử phát triển, quyết định thiết kế, và bugfix đã bị squash. Không thể:
- Biết khi nào một feature được thêm vào
- Rollback khi một thay đổi gây regression
- Review pull request với context lịch sử

**Khuyến nghị:** Không thể phục hồi lịch sử đã mất, nhưng từ đây nên:
- Commit thường xuyên với messages rõ ràng (conventional commits)
- Sử dụng feature branches
- Không squash toàn bộ thành 1-2 commits

---

### 9.3 🟡 Không có entry point CLI thống nhất

**Hiện trạng:** Có nhiều runner scripts: `run_full_pipeline.py`, `run_prepare.py`, `run_pretranslation.py`...

**Khuyến nghị:** Consolidate thành một CLI:

```bash
# Hiện tại (fragmented):
python run_prepare.py project_name
python run_pretranslation.py project_name
python run_full_pipeline.py project_name
python run_translate_ch01.py  # ← hardcoded chapter!

# Mục tiêu:
drduc init project_name --source ./raw/
drduc scan project_name
drduc translate project_name --chapters all
drduc translate project_name --chapters 1-10
drduc qa project_name --report
drduc export project_name --format epub
```

---

### 9.4 🟢 Tauri native build chưa được validate

**README thừa nhận:** *"Native Tauri packaging has not been validated in this environment because Rust tooling is not installed"*

Đây là risk cụ thể: Tauri được chọn vì lightweight native build, nhưng nếu build lỗi trên Windows/Mac thì mất toàn bộ lý do chọn Tauri thay vì Electron.

**Khuyến nghị:** Thêm Tauri build vào CI (có thể chạy theo schedule weekly thay vì mỗi push để tiết kiệm CI minutes).

---

## 10. MÂU THUẪN KIẾN TRÚC

### 10.1 🔴 Hai hệ thống Dependency Parsing song song, không rõ Production path

**Quan sát:**

Trong `Plan.md` (Python path):
> `src/grammar/`: ClauseSegmenter, RelationDetector, GrammarTransferEngine, RuleClaim/RuleRegistry/ConflictResolver

Trong `enhanced_translation_system_plan.md` (JS path, chưa archive):
> `src/parser/morphological_analyzer.js`, `dependency_parser.js`, `tree_graph_builder.js`

Cả hai đều mô tả **cùng một chức năng** (dependency parsing) nhưng bằng ngôn ngữ khác nhau và với thiết kế khác nhau. Mặc dù README_VI.md tuyên bố JS đã archive, file JS plan vẫn ở root và không có dấu hiệu deprecated.

**Rủi ro:** Nếu Grammar Transfer Engine Python (v23) được thiết kế không nhất quán với thiết kế JS ban đầu (vì developer đọc JS plan và implement Python), có thể có gaps không được phát hiện.

---

### 10.2 🟡 EAPEE và Grammar Transfer Engine hoạt động trên cùng sentence nhưng không có handoff protocol

**Vấn đề:**

```
Sentence: "她愤怒地对他说：'你给我滚！'"

EAPEE xử lý:
  - Speaker: 她 (female)
  - Listener: 他 (male)
  - Emotion: angry (intensity=3)
  - Pronoun: ta/ngươi (angry override)
  - Expression: "cút" cho 滚

Grammar Transfer Engine xử lý:
  - "她...对他说" → subject + indirect_object + verb_say structure
  - "你给我" → pronoun structure cần dịch
  - 给 = direction/dative marker

CONFLICT: EAPEE đã resolve "你" = "ngươi" nhưng Grammar Engine có thể
  xử lý "你给我" như một đơn vị và produce "anh cho tôi" (neutral grammar default)
  → Hai kết quả mâu thuẫn nhau!
```

**Khắc phục — Định nghĩa rõ thứ tự xử lý và handoff:**

```python
# Thứ tự PIPELINE phải được document rõ:
# 1. Structure Preservation (trước hết, bảo toàn non-text)
# 2. Pro-drop Resolution (annotate missing subjects)
# 3. EAPEE Emotion Detection (detect emotion, prepare pronoun context)
# 4. Grammar Transfer Engine (structural transformation)
#    → GTE NHẬN pronoun context từ EAPEE, KHÔNG tự resolve pronoun
# 5. EAPEE Pronoun Resolution (thay thế 我/你/他/她 bằng kết quả từ step 3)
#    → Chạy SAU Grammar Transfer để có đúng structure
# 6. Trie/LuatNhan Translation (apply dictionary lookup)
# 7. Number Conversion
# 8. Structure Restoration

class TranslationPipeline:
    def translate_sentence(self, sentence: str, ctx: TranslationContext) -> str:
        # Immutable context → mỗi stage tạo new context
        s = self.structure_preserver.wrap(sentence)
        s = self.pro_drop_resolver.annotate(s, ctx)
        emotion_ctx = self.emotion_detector.detect(s, ctx)   # Step 3: detect only
        s = self.grammar_engine.transform(s, emotion_ctx)    # Step 4: structural transform
        s = self.pronoun_resolver.resolve(s, emotion_ctx)    # Step 5: pronoun replace
        s = self.trie_engine.translate(s, ctx)               # Step 6: dictionary
        s = self.number_converter.convert(s)                 # Step 7
        s = self.structure_preserver.restore(s)              # Step 8
        return s
```

---

## 11. MA TRẬN ƯU TIÊN

| # | Vấn đề | Module | Mức độ | Effort | Ưu tiên |
|---|--------|--------|--------|--------|---------|
| 1 | Pipeline batch không có fault isolation | Pipeline | 🔴 Critical | Thấp | **P0** |
| 2 | Root directory ô nhiễm (artifacts, .resolved, .mp4) | Repo | 🔴 Critical | Thấp | **P0** |
| 3 | enhanced_translation_system_plan.md chưa archive/deprecated | Repo | 🔴 Critical | Thấp | **P0** |
| 4 | Emotion Detector không xử lý negation & pretend | EAPEE | 🔴 High | Trung bình | **P1** |
| 5 | One-Mean `split(";")[0]` mất context | Trie | 🔴 High | Cao | **P1** |
| 6 | TM Fuzzy match reuse bản dịch nghĩa ngược | TM | 🔴 High | Trung bình | **P1** |
| 7 | Pronoun 4D Matrix thiếu fallback chain | EAPEE | 🔴 High | Trung bình | **P1** |
| 8 | Không có CI/CD | DevOps | 🔴 High | Thấp | **P1** |
| 9 | EAPEE ↔ Grammar Engine không có handoff protocol | Architecture | 🔴 High | Cao | **P1** |
| 10 | Viterbi không xử lý catastrophic backtracking | Trie | 🟡 Medium | Trung bình | **P2** |
| 11 | Nested placeholder restoration sai thứ tự | Pipeline | 🟡 Medium | Trung bình | **P2** |
| 12 | Context Window không reset đúng tại chapter boundary | Pipeline | 🟡 Medium | Thấp | **P2** |
| 13 | Hot-reload race condition trong batch | Trie | 🟡 Medium | Trung bình | **P2** |
| 14 | Passive "được/bị" chỉ có 2 nhãn — thiếu valence dict | Grammar | 🟡 Medium | Trung bình | **P2** |
| 15 | Emotion Decay cứng nhắc — không nhạy với context | EAPEE | 🟡 Medium | Thấp | **P2** |
| 16 | 183 tests không có E2E integration test | Testing | 🟡 Medium | Cao | **P2** |
| 17 | TM 3 tầng thiếu promotion/demotion policy | TM | 🟡 Medium | Thấp | **P2** |
| 18 | P5 Priority không có scope-limited cho tên riêng | Trie | 🟡 Medium | Trung bình | **P3** |
| 19 | Pro-drop không được xử lý (missing subject) | Grammar | 🟡 Medium | Cao | **P3** |
| 20 | V-得-C potential complement nhầm với aspect marker | Grammar | 🟡 Medium | Trung bình | **P3** |
| 21 | Number Converter thiếu phân số, thập phân | Pipeline | 🟡 Medium | Thấp | **P3** |
| 22 | Gender Detection chỉ dựa 他/她 | EAPEE | 🟡 Medium | Thấp | **P3** |
| 23 | Incremental Learning thiếu forgetting prevention | TM/Learning | 🟡 Medium | Cao | **P3** |
| 24 | pyproject.toml thiếu dependencies & pinning | DevOps | 🟢 Low | Thấp | **P4** |
| 25 | Không có CLI entry point thống nhất | DevOps | 🟢 Low | Trung bình | **P4** |
| 26 | Tauri native build chưa validate | Desktop | 🟢 Low | Thấp | **P4** |

---

## 12. ROADMAP KHẮC PHỤC

### 🏃 Sprint 0 — Dọn dẹp ngay (1-3 ngày)

> Không cần code, chỉ cần git commands và một vài dòng text.

```bash
# 1. Xóa artifacts khỏi git
git rm *.jsonl *_results.json *_debug.txt trie_verification.json SVID_*.mp4
git rm *.resolved
git add .gitignore && git commit -m "chore: remove committed artifacts and merge leftovers"

# 2. Deprecate JS plan
echo '> ⚠️ DEPRECATED: Xem Plan.md. File này là kế hoạch JS cũ đã abandon.' \
  | cat - enhanced_translation_system_plan.md > /tmp/tmp && \
  mv /tmp/tmp enhanced_translation_system_plan.md
git add enhanced_translation_system_plan.md
git commit -m "docs: mark enhanced_translation_system_plan as deprecated"

# 3. Fix thư mục tên có space
git mv "Name project" name_project
git commit -m "refactor: rename 'Name project' → name_project (remove space)"
```

### 🔧 Sprint 1 — Reliability cốt lõi (1-2 tuần)

- [ ] Implement `robust_batch_runner.py` với fault isolation (4.1)
- [ ] Thêm CI/CD GitHub Actions (8.3)
- [ ] Document và test fallback chain cho Pronoun 4D Matrix (5.2)
- [ ] Thêm semantic antonym check vào TM fuzzy match (7.1)
- [ ] Thêm negation detection vào Emotion Detector (5.1)

### 🧠 Sprint 2 — Chất lượng thuật toán (2-4 tuần)

- [ ] Smart One-Mean resolver thay thế `split(";")[0]` (3.2)
- [ ] Viterbi pre-normalization cho repeated chars (3.1)
- [ ] Chapter boundary selective reset trong Context Manager (4.3)
- [ ] Nested placeholder restoration theo depth-first (4.2)
- [ ] Define và implement EAPEE ↔ Grammar Engine handoff protocol (10.2)

### 🏗️ Sprint 3 — Nâng cao & Validation (4-6 tuần)

- [ ] Xây dựng E2E integration tests với golden fixtures (8.1)
- [ ] Xây dựng golden benchmark từ 24 dự án cũ (8.2)
- [ ] Emotion Decay context-aware (5.3)
- [ ] Passive valence dictionary cho "được/bị" (6.2)
- [ ] Pro-drop resolver cho dependency parser (6.1)
- [ ] Number Converter mở rộng (phân số, thập phân) (4.4)
- [ ] TM promotion/demotion policy documentation (7.2)

### 🚀 Sprint 4 — Production hardening (6-8 tuần)

- [ ] Resumable batch processing từ any checkpoint (4.5)
- [ ] Hot-reload race condition fix (3.4)
- [ ] Forgetting prevention trong Rule Induction (7.3)
- [ ] CLI unified entry point (9.3)
- [ ] Tauri native build CI validation (9.4)
- [ ] pyproject.toml dependency pinning (9.1)

---

*Báo cáo dựa trên phân tích README.md, README_VI.md, Plan.md (56KB), IMPLEMENTATION_SUMMARY.md, enhanced_translation_system_plan.md, pyproject.toml và cấu trúc thư mục root được quan sát công khai. Một số module (trie_engine.py, rbmt_translator.py, etc.) không thể truy cập trực tiếp do robots.txt — các vấn đề được suy luận từ đặc tả thiết kế.*
