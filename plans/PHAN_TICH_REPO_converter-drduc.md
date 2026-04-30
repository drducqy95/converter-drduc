# 📋 BÁO CÁO PHÂN TÍCH KỸ THUẬT
## Repository: `drducqy95/converter-drduc`
**Ngày phân tích:** 30/04/2026
**Phiên bản:** main branch (2 commits)
**Phạm vi:** Cấu trúc project, thuật toán, pipeline, và khuyến nghị khắc phục

---

## MỤC LỤC
1. [Tổng quan dự án](#1-tổng-quan)
2. [Phân tích cấu trúc Project](#2-cấu-trúc-project)
3. [Phân tích thuật toán cốt lõi](#3-thuật-toán)
4. [Phân tích Pipeline dịch thuật](#4-pipeline)
5. [Phân tích hệ thống EAPEE](#5-eapee)
6. [Vấn đề về Quality Assurance](#6-qa)
7. [Vấn đề về quản lý dữ liệu](#7-data)
8. [Vấn đề về tích hợp đa ngôn ngữ](#8-integration)
9. [Vấn đề về DevOps & Bảo trì](#9-devops)
10. [Bảng tổng hợp & Ưu tiên khắc phục](#10-summary)

---

## 1. TỔNG QUAN DỰ ÁN

### Mô tả
`converter-drduc` là hệ thống dịch thuật Rule-Based Machine Translation (RBMT) **không dùng LLM**, chuyên dịch tiểu thuyết và tài liệu từ **Tiếng Trung / Tiếng Anh → Tiếng Việt**.

### Stack công nghệ hiện tại
| Layer | Công nghệ |
|-------|-----------|
| Engine dịch | Python 3.11+ |
| Dictionary storage | SQLite (Trie compiled) + Markdown files |
| Desktop UI | React + Tauri (Rust backend) |
| Prototype/Reference | JavaScript/TypeScript |
| Testing | pytest (98 tests passed) |
| Build | pyproject.toml + Vite (desktop) |

### Điểm mạnh
- Kiến trúc RBMT thuần túy — không phụ thuộc cloud/LLM
- Hệ thống EAPEE (cảm xúc + xưng hô) được thiết kế công phu
- Trie 5-tầng ưu tiên là lựa chọn đúng đắn về mặt hiệu năng
- Tài liệu thiết kế (Plan.md) rất chi tiết (56KB, 1388 dòng)

---

## 2. PHÂN TÍCH CẤU TRÚC PROJECT

### 2.1 Vấn đề: Root directory ô nhiễm nghiêm trọng (Critical)

**Hiện trạng:** Root của repo chứa hỗn độn file không có tổ chức:

```
/ (root)
├── clean_dict.py           ← script tiện ích nằm ở root
├── debug_regex.py          ← script debug nằm ở root
├── debug_rewriter.py       ← script debug nằm ở root
├── debug_zh_rewriter.py    ← script debug nằm ở root
├── patch_nc2.py            ← patch script nằm ở root
├── patch_nc5.py            ← patch script nằm ở root
├── run_coach_feedback.py   ← runner nằm ở root
├── run_full_pipeline.py    ← runner nằm ở root
├── run_prepare.py          ← runner nằm ở root
├── run_pretranslation.py   ← runner nằm ở root
├── run_translate_ch01.py   ← runner chapter-specific nằm ở root
├── run_translate_ch02.py   ← runner chapter-specific nằm ở root
├── test_import.py          ← test file nằm ở root
├── test_basic.js           ← test JS nằm ở root
├── test_comprehensive.js   ← test JS nằm ở root
├── index.js                ← entry point JS nằm ở root
├── all_global_errors.jsonl ← artifact/log nằm ở root
├── cedict_seeding_debug.txt← debug log nằm ở root
├── diagnose_results.json   ← artifact nằm ở root
├── pos_db_audit.json       ← artifact nằm ở root
├── pos_diagnostic_results.json ← artifact nằm ở root
├── pos_rewrite_test_results.json ← artifact nằm ở root
├── trie_verification.json  ← artifact nằm ở root
├── nlm_rules.txt           ← data file nằm ở root
├── python                  ← file không rõ loại, không có extension!
└── ... (10+ file .resolved, .md rải rác)
```

**Hậu quả:**
- Không phân biệt được production code vs debug script vs artifact
- `run_translate_ch01.py` và `run_translate_ch02.py` là anti-pattern nguy hiểm: mỗi chương một file runner riêng → sẽ có `run_translate_ch03.py`, `ch04.py`... không thể bảo trì
- File `python` không có extension — hoàn toàn không rõ mục đích
- `.jsonl` và `.json` artifact (log debug) bị commit vào repo — vi phạm nguyên tắc không commit artifacts

**Khắc phục:**
```
Tái cấu trúc thư mục:

scripts/
├── debug/          ← toàn bộ debug_*.py, patch_*.py
├── runners/        ← run_*.py (refactor thành 1 runner với arg)
│   └── run_pipeline.py --chapter 01 --mode pretranslation
└── tools/          ← clean_dict.py, test_import.py

artifacts/          ← hoặc thêm vào .gitignore
├── logs/
└── diagnostics/

# Thêm vào .gitignore:
*.jsonl
*_results.json
*_debug.txt
cedict_seeding_*
diagnose_*
pos_*
trie_verification.json
```

---

### 2.2 Vấn đề: Ranh giới sản xuất - prototype không rõ ràng (High)

**Hiện trạng:** README thừa nhận có hai lớp song song:
- Python (`src/core/`, `src/engine/`) = production
- JavaScript (`src/preprocessor/`, `src/parser/`, `src/rules/`) = prototype

Nhưng không có cơ chế kỹ thuật nào ngăn người dùng/contributor dùng nhầm lớp JS trong production.

**Hậu quả:**
- Cả `index.js` và `test_basic.js`, `test_comprehensive.js` đều ở root — không biết đây là prototype hay production entry point
- `package.json` ở root nhưng là cho JS prototype, dễ gây nhầm với desktop package
- Người mới vào repo không biết nên chạy gì trước: `python run_full_pipeline.py` hay `node index.js`?

**Khắc phục:**
```
Tách rõ ràng bằng cấu trúc thư mục:

src/
├── core/       ← Python production (giữ nguyên)
├── engine/     ← Python production (giữ nguyên)
└── ...

prototype/      ← RENAME từ src/preprocessor, src/parser, src/rules
├── js_engine/  ← Đặt toàn bộ JS code vào đây
│   ├── src/
│   ├── index.js
│   ├── package.json
│   └── README.md  ← Ghi rõ: "ĐÂY LÀ PROTOTYPE, KHÔNG DÙNG TRONG PRODUCTION"
└── tests/
    ├── test_basic.js
    └── test_comprehensive.js
```

---

### 2.3 Vấn đề: File tài liệu bừa bộn với extension `.resolved` (Medium)

**Hiện trạng:** Root chứa nhiều file như:
- `implementation_plan.md.resolved`
- `implementation_plan22.md.resolved`
- `metadata_migration_plan.md.resolved`
- `pipeline_guidev2.md.resolved`
- `pipeline_guidev3.md.resolved`
- `walkthrough.md.resolved`

**Hậu quả:** Đây rõ ràng là artifact từ quá trình merge conflict hoặc agent workflow. Chúng **không nên tồn tại trong repo**. Gây lẫn lộn với tài liệu thực.

**Khắc phục:**
```bash
# Xóa tất cả .resolved files
find . -name "*.resolved" -delete
git rm *.resolved
# Hoặc thêm vào .gitignore:
*.resolved
```

---

### 2.4 Vấn đề: Thư mục `Name project` có tên chứa space (Medium)

**Hiện trạng:** Thư mục tên `Name project` (có khoảng trắng).

**Hậu quả:**
- Scripts bash cần escape: `cd "Name project"` thay vì `cd Name_project`
- Dễ gây lỗi trong CI/CD, cross-platform path handling
- Không rõ mục đích thư mục này là gì

**Khắc phục:**
```bash
git mv "Name project" name_project
# Hoặc đổi thành: project_template / project_scaffold
```

---

### 2.5 Vấn đề: Video file được commit vào repo (Low-Medium)

**Hiện trạng:** `SVID_20260423_073257_1.mp4` tồn tại trong repo.

**Hậu quả:** Binary file lớn trong git repo làm chậm clone/fetch cho tất cả contributor. Git không được thiết kế để track binary media.

**Khắc phục:**
```bash
# Dùng Git LFS hoặc xóa khỏi repo và host trên YouTube/drive
git rm SVID_20260423_073257_1.mp4
# Thêm vào .gitignore: *.mp4 *.avi *.mov
```

---

## 3. PHÂN TÍCH THUẬT TOÁN CỐT LÕI

### 3.1 Trie Engine — Thiếu xử lý ambiguity cho Longest Prefix Match (Critical)

**Mô tả trong Plan.md:**
```
Trie Traversal: Dual-pointer longest-prefix matching
Priority override: P5 > P4 > P3 > P2 > P1
One-Mean mode: split(";")[0] cho P2/P3
```

**Vấn đề phân tích:**

Thuật toán Longest Prefix Match (LPM) trong tiếng Trung có vấn đề cơ bản: **ambiguity khi cụm dài hơn đôi khi SAI hơn cụm ngắn hơn.**

Ví dụ:
```
Input: 他们在讨论问题
                    ↑ "讨论问题" = "thảo luận vấn đề" (4 chars, LPM win)
                    ↑ "讨论" = "thảo luận" + "问题" = "vấn đề" (cũng đúng)

Nhưng với: 他在讨论问题所在
                    ↑ "问题所在" = "vấn đề nằm ở chỗ nào" (4 chars)
                    → Nếu dict chỉ có "问题" thì LPM sẽ match "讨论问题" sai
```

**Không có cơ chế backtracking** khi LPM tạo ra kết quả vô nghĩa trong ngữ cảnh.

**Khắc phục:**
```python
# Thêm N-best Trie matching thay vì greedy LPM
def trie_lookup_nbest(text, n=3):
    """
    Thay vì chỉ trả về 1 kết quả tốt nhất,
    trả về top-N candidates để LuatNhan chọn lọc.
    """
    candidates = []
    # ... collect all valid prefix matches
    return sorted(candidates, key=lambda x: (x.priority, x.length), reverse=True)[:n]

# Thêm confidence score dựa trên context window
def score_candidate(candidate, left_context, right_context):
    score = candidate.base_priority
    # Bonus nếu next token sau match là particle/grammar marker
    if right_context[:1] in VALID_FOLLOWING_PARTICLES:
        score += 0.5
    return score
```

---

### 3.2 LuatNhan Pattern Engine — Thiếu độ ưu tiên và conflict resolution (High)

**Hiện trạng:** Hệ thống có 303 + 15K LuatNhan templates với pattern `{0}`.

**Vấn đề:** Với 15K+ patterns, **không có cơ chế giải quyết conflict** khi nhiều pattern đều match cùng một đoạn văn bản.

Ví dụ:
```
Pattern A: "{0}突破到{1}境界" → "{0} đột phá đến cảnh giới {1}"
Pattern B: "{0}突破" → "{0} đột phá"
Pattern C: "突破到{0}" → "đột phá đến {0}"

Input: "林动突破到涅槃境界"
→ A match: "Lâm Động đột phá đến cảnh giới Niết Bàn" ✅
→ B match: "Lâm Động đột phá" (bỏ phần sau) ❌
→ C match: "đột phá đến Niết Bàn Cảnh Giới" (bỏ tên nhân vật) ❌
```

Thiếu **specificity scoring**: pattern dài hơn (A) nên được ưu tiên hơn pattern ngắn hơn (B, C), nhưng điều này không được mô tả trong thiết kế.

**Khắc phục:**
```python
class LuatNhanPattern:
    def __init__(self, pattern, template, priority=0):
        self.pattern = pattern
        self.template = template
        # Tự động tính specificity score
        self.specificity = (
            len(re.findall(r'\{[0-9]+\}', pattern)),  # số placeholders
            len(pattern),                               # độ dài pattern
            priority                                    # priority thủ công
        )

def apply_patterns(sentence, patterns):
    matches = [(p, p.match(sentence)) for p in patterns if p.match(sentence)]
    # Sort: ít placeholder hơn = cụ thể hơn, dài hơn = cụ thể hơn
    matches.sort(key=lambda x: x[0].specificity, reverse=True)
    return matches[0] if matches else None  # Chọn pattern cụ thể nhất
```

---

### 3.3 Emotion Detector — Sai sót với metaphor và negation (High)

**Hiện trạng:** Emotion detection dựa hoàn toàn vào keyword matching.

**Vấn đề nghiêm trọng - Negation không được xử lý:**
```
# Input: 他没有愤怒 (anh ấy KHÔNG tức giận)
# Detector: tìm thấy keyword "愤怒" → gán emotion = angry ❌
# Correct: emotion = neutral

# Input: 他装作愤怒 (anh ấy GIẢ VỜ tức giận)
# Detector: "愤怒" → angry ❌
# Correct: emotion phức tạp (deceptive/acting)
```

**Vấn đề với metaphor:**
```
# Input: 他的心如死灰 (lòng anh như tro tàn - buồn bã)
# Detector: không có keyword trực tiếp → neutral ❌
# Correct: sad

# Input: 他杀意凛然 (sát ý của anh ta rõ ràng - không phải đang giết)
# Detector: "杀意" → threatening/angry ❌ (hoặc ✅ tùy ngữ cảnh)
```

**Khắc phục:**
```python
def detect_emotion_with_negation(sentence):
    # 1. Detect negation scopes TRƯỚC khi scan emotion
    NEGATORS = ['没有', '不', '未', '无', '非', '否', '装作', '假装', '伪装']
    negation_zones = find_negation_scopes(sentence, NEGATORS)

    scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            pos = sentence.find(kw)
            if pos != -1:
                # Kiểm tra keyword có nằm trong vùng phủ định không
                if not is_in_negation_zone(pos, negation_zones):
                    scores[emotion] = scores.get(emotion, 0) + keyword_weight(kw)

    # 2. Metaphor patterns (separate dictionary)
    for metaphor_pattern, emotion in METAPHOR_EMOTIONS.items():
        if re.search(metaphor_pattern, sentence):
            scores[emotion] = scores.get(emotion, 0) + 2

    return max(scores, key=scores.get) if scores else 'neutral'
```

---

### 3.4 Pronoun Resolution — Logic 4D Matrix chưa xử lý conflict giữa chiều (High)

**Thiết kế:** `Pronoun = f(Genre, Relationship, Emotion, Gender)` — 4 chiều.

**Vấn đề chưa giải quyết:**
```
# Trường hợp conflict:
# - Genre: xianxia → default: ta/ngươi
# - Relationship: lover (M→F) + Emotion: tender → phu quân/thiếp
# - Nhưng Emotion: angry → ta/ngươi
# - Identity: character là Tông Chủ → bổn tọa

# Khi cả 4 chiều conflict, rule nào win?
```

Plan.md chỉ mô tả: "Identity pronouns có priority cao nhất" nhưng không giải quyết conflict giữa Genre vs Relationship vs Emotion khi chúng cho kết quả khác nhau.

**Không có fallback chain được định nghĩa rõ:**
```
# Nếu lookup ma trận thất bại (không có entry):
# → Fallback 1: Genre default? Relationship default? Neutral?
```

**Khắc phục:**
```python
PRONOUN_RESOLUTION_PRIORITY = [
    'identity_override',    # Hoàng đế, Tông Chủ, Bần Tăng... (tuyệt đối)
    'emotion_high',         # Intensity >= 4: override hết
    'relationship_emotion', # Kết hợp relationship + emotion (bảng hiện tại)
    'relationship_only',    # Chỉ relationship (ignore emotion)
    'genre_default',        # Mặc định theo genre
    'universal_fallback',   # ta/ngươi (safest)
]

def resolve_pronoun(speaker, listener, genre, emotion, intensity):
    for strategy in PRONOUN_RESOLUTION_PRIORITY:
        result = try_resolve(strategy, speaker, listener, genre, emotion, intensity)
        if result is not None:
            return result
    return ('ta', 'ngươi')  # Universal fallback
```

---

### 3.5 Viterbi/HMM cho Pinyin Resolution — Thiếu mô tả training data (Medium)

**Từ IMPLEMENTATION_SUMMARY.md:** "Pinyin Processor: Uses HMM and Viterbi algorithm for Pinyin-to-Chinese conversion"

**Vấn đề:** HMM/Viterbi cần:
1. Emission probabilities: P(pinyin | character)
2. Transition probabilities: P(char_i | char_{i-1})

Không có thông tin nào về:
- Training data nguồn gốc từ đâu?
- Kích thước corpus?
- Cách cập nhật/fine-tune khi gặp từ mới?
- Pinyin không dấu (không tone marks) xử lý thế nào?

Ví dụ: `xiu wei` có thể là: 修为 / 修威 / 休为 / 秀威 — không có context window thì Viterbi không thể chọn đúng.

**Khắc phục:**
```python
# Cần document rõ trong code:
class PinyinHMM:
    """
    Training data: CMU Pronouncing Dict + CC-CEDICT
    Corpus size: X entries
    Context window: N-gram (N=?)
    Tone handling: stripped → ambiguous mapping documented
    Unknown pinyin: fallback to phonetic approximation
    """
    def __init__(self, model_path: str):
        self.transition_probs = load_ngram_model(model_path)
        self.emission_probs = load_pinyin_char_map(model_path)
        # CRITICAL: Document what happens with unknown pinyin sequences
        self.unknown_strategy = 'most_common_char'  # Must be explicit
```

---

## 4. PHÂN TÍCH PIPELINE

### 4.1 Vấn đề: Batch pipeline không có error recovery (Critical)

**Hiện trạng (từ Plan.md):**
```python
for chapter in chapters:
    translate(chapter)
    update_progress()
    if chapter_num % 10 == 0:
        checkpoint()
        run_qa_quick()
```

**Vấn đề nghiêm trọng:** Không có `try/except`. Nếu chapter 47 của 500 chương gây lỗi (ví dụ: encoding lạ, ký tự đặc biệt, regex catastrophic backtrack), **toàn bộ pipeline dừng lại**, mất kết quả 46 chương đã dịch xong trong memory.

**Khắc phục:**
```python
from dataclasses import dataclass
from enum import Enum

class ChapterStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ChapterResult:
    chapter_num: int
    status: ChapterStatus
    error: str | None = None
    output_path: str | None = None

def run_pipeline_robust(chapters, config):
    results = []
    for chapter in chapters:
        try:
            result = translate_chapter(chapter, config)
            results.append(ChapterResult(chapter.num, ChapterStatus.SUCCESS,
                                          output_path=result.path))
            checkpoint_if_needed(chapter.num, config)
        except RegexTimeoutError as e:
            logger.error(f"Chapter {chapter.num}: Regex timeout - {e}")
            results.append(ChapterResult(chapter.num, ChapterStatus.FAILED,
                                          error=str(e)))
            # Continue với chapter tiếp theo
        except UnicodeDecodeError as e:
            logger.error(f"Chapter {chapter.num}: Encoding error - {e}")
            results.append(ChapterResult(chapter.num, ChapterStatus.FAILED,
                                          error=str(e)))
        except Exception as e:
            logger.critical(f"Chapter {chapter.num}: Unexpected error - {e}")
            results.append(ChapterResult(chapter.num, ChapterStatus.FAILED,
                                          error=str(e)))
            # Vẫn tiếp tục, không dừng toàn bộ pipeline

    generate_run_report(results)
    return results
```

---

### 4.2 Vấn đề: Context Window không tính đến chapter boundary (High)

**Thiết kế hiện tại:** Context window = 5 câu trước + 5 câu sau.

**Vấn đề:** Câu đầu tiên của chapter 2 sẽ lấy 5 câu từ chapter 1 làm context. Điều này đúng cho tính liên tục ngữ cảnh. **Nhưng:**

1. Pronoun resolver sẽ dùng `active_characters` từ chapter 1 — có thể không còn xuất hiện trong chapter 2
2. Emotion state machine sẽ carry-over emotion từ cuối chapter 1 sang đầu chapter 2 — sai trong nhiều trường hợp có time skip
3. Không có "chapter start signal" để reset một số state và giữ các state khác

**Khắc phục:**
```python
class ContextManager:
    RESET_ON_CHAPTER_BOUNDARY = [
        'emotion_state',        # Reset: mỗi chapter có thể khác mood
        'active_dialogue',      # Reset: dialogue đã kết thúc
    ]
    PRESERVE_ON_CHAPTER_BOUNDARY = [
        'active_characters',    # Giữ: nhân vật vẫn còn
        'relationship_graph',   # Giữ: quan hệ không đổi
        'cultivation_realms',   # Giữ: cảnh giới đã đạt được
        'glossary_cache',       # Giữ: thuật ngữ đã học
    ]

    def on_chapter_start(self, chapter_num):
        # Selective reset
        for field in self.RESET_ON_CHAPTER_BOUNDARY:
            setattr(self, field, self.get_default(field))
        # Log preservation
        logger.info(f"Chapter {chapter_num}: preserved {self.PRESERVE_ON_CHAPTER_BOUNDARY}")
```

---

### 4.3 Vấn đề: Pipeline stage "Structure Preservation" quá đơn giản cho production (High)

**Thiết kế hiện tại:** Dùng regex placeholder wrapping:
```
→ [TABLE_001]...[/TABLE_001]
→ [MATH_001]...[/MATH_001]
```

**Vấn đề với nested structures:**
```
# Input HTML:
<table>
  <tr><td>He uses <code>E=mc²</code></td></tr>
</table>

# Regex sẽ wrap:
[TABLE_001]...[CODE_001]...[/CODE_001]...[/TABLE_001]

# Sau dịch, restore order sai:
# Nếu CODE restore trước TABLE → placeholder lồng nhau bị phá vỡ
```

Không có xử lý **nested placeholder restoration** — chỉ flat structure được đảm bảo.

**Khắc phục:**
```python
class StructurePreserver:
    def wrap(self, text: str) -> tuple[str, dict]:
        """Returns (wrapped_text, restoration_map) using stack-based nesting."""
        stack = []
        restoration_map = {}
        # Dùng recursive descent parser thay vì regex đơn giản
        # để handle nested: TABLE > CODE > MATH
        return self._parse_recursive(text, stack, restoration_map)

    def restore(self, text: str, restoration_map: dict) -> str:
        """Restore theo thứ tự depth-first (innermost first)."""
        sorted_keys = sorted(restoration_map.keys(),
                              key=lambda k: restoration_map[k]['depth'],
                              reverse=True)  # innermost first
        for key in sorted_keys:
            text = text.replace(key, restoration_map[key]['original'])
        return text
```

---

### 4.4 Vấn đề: Translation Memory chỉ dùng Levenshtein — không đủ cho văn bản dịch (Medium)

**Thiết kế:** Fuzzy match TM với Levenshtein ≤ 15%.

**Vấn đề:** Levenshtein distance là **character-level**, không phù hợp cho ngữ nghĩa:
```
Sentence A: "他修为大涨，突破了金丹境界"     (tu vi tăng vọt, đột phá Kim Đan)
Sentence B: "他修为大跌，跌落了金丹境界"     (tu vi giảm, rớt khỏi Kim Đan)

Levenshtein distance giữa A và B: chỉ 2-3 chars khác (涨↔跌, 突破↔跌落)
→ TM sẽ tái sử dụng bản dịch của A cho B ❌ (nghĩa ngược hoàn toàn!)
```

**Khắc phục:**
```python
class TranslationMemory:
    def fuzzy_match(self, source: str, threshold: float = 0.85) -> list[TMEntry]:
        candidates = []
        for entry in self.entries:
            # Dùng token-level similarity thay vì char-level
            token_sim = jaccard_similarity(tokenize(source), tokenize(entry.source))
            # Kiểm tra key semantic tokens không bị đổi nghĩa
            if self._has_semantic_conflict(source, entry.source):
                continue  # Bỏ qua nếu có conflict ngữ nghĩa (大涨 vs 大跌)
            if token_sim >= threshold:
                candidates.append((entry, token_sim))
        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def _has_semantic_conflict(self, s1: str, s2: str) -> bool:
        """Detect antonym pairs that would invert meaning."""
        ANTONYM_PAIRS = [
            ('突破', '跌落'), ('大涨', '大跌'), ('胜利', '失败'),
            ('生', '死'), ('增加', '减少'), ('上升', '下降')
        ]
        for a, b in ANTONYM_PAIRS:
            if (a in s1 and b in s2) or (b in s1 and a in s2):
                return True
        return False
```

---

## 5. PHÂN TÍCH HỆ THỐNG EAPEE

### 5.1 Emotion State Machine — Decay rules quá đơn giản (Medium)

**Thiết kế:** Decay chỉ dựa trên số câu cố định:
```python
DECAY_RULES = {
    'angry': 5,     # Giận dữ kéo dài đúng 5 câu, không hơn không kém
    'furious': 8,
    ...
}
```

**Vấn đề:** Emotion decay theo số câu là cứng nhắc. Trong thực tế:
- Nếu 5 câu tiếp theo toàn là mô tả hành động chiến đấu → anger nên kéo dài hơn
- Nếu có câu "he took a deep breath" → anger nên decay sớm hơn
- Emotion intensity nên ảnh hưởng đến decay rate (intensity=5 decay chậm hơn intensity=1)

**Khắc phục:**
```python
CALM_DOWN_SIGNALS = ['深呼吸', '平复', '冷静', '缓缓', '松了口气', '放松']
ESCALATION_SIGNALS = ['更加', '愈发', '越来越', '彻底', '完全']

def should_decay(self, next_sentence: str) -> bool:
    # Accelerate decay nếu có calm-down signal
    if any(s in next_sentence for s in CALM_DOWN_SIGNALS):
        self.age += 2  # Decay nhanh hơn
    # Slow decay nếu có escalation
    if any(s in next_sentence for s in ESCALATION_SIGNALS):
        self.age -= 1  # Kéo dài thêm
    # Intensity modifier
    effective_max = self.DECAY_RULES[self.current_emotion] + (self.intensity - 3)
    return self.age >= effective_max
```

---

### 5.2 Character Gender Detection — Chỉ dùng 他/她 là không đủ (Medium)

**Thiết kế:** "Gender detection: 她=nữ, 他=nam khi làm chủ ngữ trước tên"

**Vấn đề:**
- 它 (vật/động vật) dễ bị nhầm với 他/她
- Nhân vật có thể không xuất hiện với pronoun trước tên
- Nhân vật lưỡng tính, bí ẩn giới tính (phổ biến trong tiên hiệp) — tác giả cố tình không dùng 他/她

```
# "那道身影缓缓走来" - không có pronoun → gender unknown
# Detector sẽ để là "unknown" → pronoun resolver fallback không chính xác
```

**Khắc phục:**
```python
GENDER_CLUES = {
    'female': [
        '美女', '仙子', '女子', '少女', '姑娘', '夫人', '娘子', '小姐',
        '女侠', '她', '女弟子', '仙女', '花容月貌', '云鬓'
    ],
    'male': [
        '男子', '少年', '公子', '他', '男弟子', '武者', '剑客', '大汉'
    ],
    'ambiguous': ['修士', '强者', '前辈', '存在']
}

def detect_gender_contextual(char_name: str, surrounding_paragraphs: list[str]) -> str:
    """Scan 10 paragraphs around first mention for gender clues."""
    female_score = 0
    male_score = 0
    for para in surrounding_paragraphs:
        if char_name in para:
            for clue in GENDER_CLUES['female']:
                if clue in para: female_score += 1
            for clue in GENDER_CLUES['male']:
                if clue in para: male_score += 1
    if female_score > male_score: return 'female'
    if male_score > female_score: return 'male'
    return 'unknown'  # Explicit unknown thay vì default male
```

---

## 6. VẤN ĐỀ VỀ QUALITY ASSURANCE

### 6.1 QA không có baseline metrics (High)

**Hiện trạng:** QA chỉ check các rule-based violations (terminology, pronoun, structure). Không có:
- BLEU score so sánh với bản dịch tham chiếu
- Human evaluation rubric
- Baseline từ các bản dịch đã có (24 dự án cũ đề cập trong README)

**Vấn đề:** "98 tests passed" không nói lên chất lượng dịch — chỉ nói code không crash. Không biết độ chính xác thực tế là bao nhiêu %.

**Khắc phục:**
```python
# Tạo golden dataset từ 24 dự án đã dịch
class TranslationBenchmark:
    def __init__(self, golden_pairs: list[tuple[str, str]]):
        """
        golden_pairs: list of (source_zh, reference_vi) từ bản dịch đã có
        """
        self.golden = golden_pairs

    def evaluate(self, translator) -> dict:
        predictions = [translator.translate(src) for src, _ in self.golden]
        references = [ref for _, ref in self.golden]
        return {
            'exact_match': exact_match_rate(predictions, references),
            'terminology_accuracy': term_accuracy(predictions, references),
            'pronoun_accuracy': pronoun_accuracy(predictions, references),
            'bleu_1gram': bleu_n(predictions, references, n=1),
        }
```

---

### 6.2 Tests không cover edge cases tiếng Trung đặc thù (Medium)

Không có evidence trong repo về tests cho:
- Văn bản cổ văn (文言文) vs bạch thoại (白话文)
- Phồn thể vs Giản thể cùng đoạn
- Mixed language (tiếng Trung + English terms lẫn lộn)
- Chương rất dài (>10,000 chữ)
- Chương chỉ có dialogue (không có narrative)
- Số La Mã, số Ả Rập, số Hán tự xen kẽ

**Khắc phục:**
```python
# tests/test_edge_cases.py
class TestEdgeCases:
    def test_classical_chinese(self):
        """文言文 mixed with modern characters"""
        source = "子曰：学而时习之，不亦说乎？"
        result = translator.translate(source)
        assert "Khổng Tử nói" in result or "Thầy nói" in result

    def test_mixed_script(self):
        """Chinese + English + numbers mixed"""
        source = "他的HP从100降到了0，使用了Healing Potion后回复了50%"
        result = translator.translate(source)
        assert "HP" in result  # Keep game terms
        assert "50%" in result  # Keep percentage

    def test_empty_chapter(self):
        """Edge: empty or near-empty chapter"""
        assert translator.translate("") == ""
        assert translator.translate("   ") == ""

    def test_very_long_chapter(self):
        """Performance: 10000+ chars"""
        long_text = generate_long_zh_text(10000)
        start = time.time()
        result = translator.translate(long_text)
        assert time.time() - start < 10  # Max 10s
```

---

## 7. VẤN ĐỀ VỀ QUẢN LÝ DỮ LIỆU

### 7.1 Hai file JSON trùng tên ở root (High)

**Hiện trạng:**
```
/ (root)
├── Converter by DrDuc.json      ← tên có space!
└── converter_by_drduc.json      ← underscore version
```

**Vấn đề:** Hai file có nội dung gì? Giống nhau hay khác nhau? Cái nào là canonical? File nào được code đọc? Tên có space là anti-pattern nghiêm trọng.

**Khắc phục:**
```bash
# Kiểm tra sự khác biệt
diff "Converter by DrDuc.json" converter_by_drduc.json

# Nếu giống nhau: xóa file có space
git rm "Converter by DrDuc.json"

# Nếu khác nhau: rename + document purpose
git mv "Converter by DrDuc.json" converter_by_drduc_v1.json
# Thêm comment trong cả hai file giải thích mục đích
```

---

### 7.2 Thiếu schema validation cho Markdown Dictionary (Medium)

**Thiết kế:** Mỗi Rich MD entry có YAML frontmatter phức tạp.

**Vấn đề:** Không có schema validation. Nếu contributor tạo file MD với:
```yaml
---
priority: "three"   # Đáng lẽ phải là integer 3
one_mean: yes       # Đáng lẽ là boolean true
gender: "nữ"        # Không nhất quán (cần "female" hoặc "nữ"?)
---
```
Compiler sẽ xử lý sai hoặc crash không rõ nguyên nhân.

**Khắc phục:**
```python
# src/core/dictionary_schema.py
from pydantic import BaseModel, validator
from typing import Optional, List, Literal

class DictionaryEntry(BaseModel):
    id: str
    source: str
    target: str
    priority: int = Field(ge=1, le=5)
    one_mean: bool = False
    locked: bool = False
    gender: Optional[Literal['male', 'female', 'unknown']] = None
    category: Optional[str] = None

    @validator('source')
    def source_must_have_chinese(cls, v):
        if not any('\u4e00' <= c <= '\u9fff' for c in v):
            raise ValueError('source must contain Chinese characters')
        return v

# Trong compiler:
def compile_entry(raw_yaml: dict) -> DictionaryEntry:
    try:
        return DictionaryEntry(**raw_yaml)
    except ValidationError as e:
        logger.error(f"Invalid entry schema: {e}")
        return None  # Skip invalid entries
```

---

### 7.3 Không có migration versioning cho dictionary schema (Medium)

Khi schema YAML thay đổi (thêm field mới, đổi tên field), tất cả 728K entries cũ sẽ cần update thủ công.

**Khắc phục:**
```python
# data/dictionaries/_schema_version.json
{
    "version": "1.2.0",
    "changelog": [
        {"version": "1.2.0", "change": "Added 'cultural_origin' field"},
        {"version": "1.1.0", "change": "Renamed 'type' to 'category'"},
        {"version": "1.0.0", "change": "Initial schema"}
    ]
}

# src/core/schema_migrator.py
def migrate_entry(entry: dict, from_version: str, to_version: str) -> dict:
    """Auto-migrate old entries to new schema version."""
    if from_version == "1.0.0" and to_version >= "1.1.0":
        if 'type' in entry and 'category' not in entry:
            entry['category'] = entry.pop('type')
    return entry
```

---

## 8. VẤN ĐỀ VỀ TÍCH HỢP ĐA NGÔN NGỮ

### 8.1 EN-VI Engine quá sơ lược (High)

**Thiết kế:** "Phrase matching + basic grammar rules + LacViet/Babylon/CEDICT"

**Vấn đề:** Tiếng Anh có grammatical complexity mà rule đơn giản không xử lý được:
- Tense system: past/present/future/perfect → không có equivalent trong tiếng Việt (dùng "đã/đang/sẽ")
- Passive voice: "was destroyed by" → "bị phá hủy bởi" (thường đúng) vs "bị phá hủy" (đôi khi tốt hơn)
- Relative clauses: "the man who came yesterday" → cần đảo ngược cấu trúc
- Phrasal verbs: "give up", "put off" — không phải phrase matching đơn giản

Rule `"Adjective position: 'red car' → 'xe đỏ' (reverse)"` là đúng nhưng không cover:
```
"big red car" → "xe màu đỏ to" hay "xe to màu đỏ"? (thứ tự adj khác nhau)
"fast-moving red sports car" → ???
```

**Khắc phục:** Hoặc thu hẹp phạm vi EN-VI (chỉ cover thể loại cụ thể), hoặc tích hợp một lightweight dependency parser như spaCy (en_core_web_sm) mà không vi phạm No-LLM constraint.

---

### 8.2 Thiếu xử lý Traditional Chinese input path (Medium)

**Thiết kế:** Multi-dictionary conversion: T2S, TW2S, TW2SP, HK2S.

**Vấn đề:** Thứ tự áp dụng conversion chains không được xác định rõ. Ví dụ:
```
Input: 雲 (phồn thể, cả Taiwan và Hong Kong dùng)
T2S: 雲 → 云 (giản thể đại lục)
TW2S: 雲 → 云 (Taiwan simplified)
HK2S: 雲 → 云 (HK simplified)

# Nếu input có từ chỉ có trong TW2SP mà T2S không biết?
# Thứ tự convert: T2S trước rồi TW2SP? Hay ngược lại?
```

Conflict không được document.

---

## 9. VẤN ĐỀ VỀ DEVOPS & BẢO TRÌ

### 9.1 Không có CI/CD pipeline (High)

**Hiện trạng:** Repo có `/.agents/workflows/` nhưng không có GitHub Actions workflows (`.github/workflows/*.yml`).

**Hậu quả:**
- Không có automated test khi push code
- `python -m pytest` chỉ chạy thủ công — không biết code có bị regress không
- Không có linting, type checking tự động

**Khắc phục:**
```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -e ".[dev]"
      - run: python -m pytest --cov=src --cov-report=xml
      - run: mypy src/ --ignore-missing-imports
      - run: ruff check src/

  desktop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd desktop && npm ci && npm run build
```

---

### 9.2 requirements.txt không pin phiên bản (Medium)

**Vấn đề:** Không biết requirements.txt có pin exact versions không (không xem được file nhưng pyproject.toml chỉ pin `>=3.11` cho Python).

**Khắc phục:**
```toml
# pyproject.toml - thêm optional dependencies
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
]

# requirements.txt should be:
# jieba==0.42.1          # Pin exact version
# chardet==5.2.0
# pydantic==2.4.2
# NOT: jieba>=0.42      # This can break on update
```

---

### 9.3 Thiếu logging framework chuẩn (Medium)

**Hiện trạng:** Đề cập "comprehensive logging" trong README nhưng không rõ dùng framework gì.

**Vấn đề:** Nếu dùng `print()` thay vì `logging` module:
- Không thể tắt/bật log levels
- Không có timestamp, không có context
- Không thể redirect ra file

**Khắc phục:**
```python
# src/utils/logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path | None = None):
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        handlers=handlers
    )
    # Suppress noisy third-party loggers
    logging.getLogger('chardet').setLevel(logging.WARNING)
```

---

### 9.4 Tauri native build chưa được validate (Low-Medium)

**README thừa nhận:** "Native Tauri packaging has not been validated in this environment because Rust tooling is not installed"

**Vấn đề:** Nếu native build không hoạt động, desktop app chỉ là web shell — mất đi toàn bộ lý do chọn Tauri (lightweight, secure). Đây là risk chưa được giảm thiểu.

**Khắc phục:**
```yaml
# .github/workflows/tauri-build.yml
name: Tauri Build Test
on: [push]
jobs:
  tauri:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: tauri-apps/tauri-action@v0
        with:
          projectPath: desktop
```

---

## 10. BẢNG TỔNG HỢP & ƯU TIÊN KHẮC PHỤC

| # | Vấn đề | Mức độ | Effort | Ưu tiên |
|---|--------|--------|--------|---------|
| 1 | Root directory ô nhiễm — scripts, artifacts, debug files lẫn lộn | 🔴 Critical | Thấp | **P0** |
| 2 | Pipeline không có error recovery — crash làm mất toàn bộ batch | 🔴 Critical | Thấp | **P0** |
| 3 | LPM không có backtracking — dịch sai khi prefix match vô nghĩa | 🔴 Critical | Cao | **P1** |
| 4 | Emotion detector không xử lý negation — "không tức giận" → angry | 🔴 High | Trung bình | **P1** |
| 5 | LuatNhan không có conflict resolution — pattern nào win? | 🔴 High | Trung bình | **P1** |
| 6 | TM dùng Levenshtein char-level — tái dùng bản dịch có nghĩa ngược | 🔴 High | Trung bình | **P1** |
| 7 | Pronoun 4D matrix không có fallback chain | 🔴 High | Trung bình | **P1** |
| 8 | Không có CI/CD — code regress không được phát hiện | 🔴 High | Thấp | **P1** |
| 9 | Context window không xử lý chapter boundary đúng cách | 🟡 Medium | Trung bình | **P2** |
| 10 | Emotion state machine decay quá cứng nhắc | 🟡 Medium | Thấp | **P2** |
| 11 | Prototype JS/Python ranh giới không rõ | 🟡 Medium | Thấp | **P2** |
| 12 | Nested structure preservation bị phá vỡ | 🟡 Medium | Cao | **P2** |
| 13 | QA không có baseline/BLEU metric | 🟡 Medium | Cao | **P2** |
| 14 | Schema validation thiếu cho MD dictionary entries | 🟡 Medium | Thấp | **P2** |
| 15 | File `.resolved` artifact trong repo | 🟡 Medium | Thấp | **P2** |
| 16 | Video file binary trong git repo | 🟡 Medium | Thấp | **P2** |
| 17 | Hai file JSON trùng tên (space vs underscore) | 🟡 Medium | Thấp | **P2** |
| 18 | Thiếu test edge cases tiếng Trung đặc thù | 🟡 Medium | Trung bình | **P3** |
| 19 | EN-VI engine quá sơ lược cho văn bản phức tạp | 🟡 Medium | Cao | **P3** |
| 20 | Tauri native build chưa validate | 🟡 Low-Med | Trung bình | **P3** |
| 21 | HMM training data không được document | 🟡 Medium | Thấp | **P3** |
| 22 | Gender detection chỉ dựa 他/她 — bỏ sót nhiều trường hợp | 🟡 Medium | Thấp | **P3** |
| 23 | requirements.txt không pin exact versions | 🟢 Low | Thấp | **P4** |
| 24 | Logging framework không chuẩn | 🟢 Low | Thấp | **P4** |
| 25 | `Name project` thư mục có khoảng trắng | 🟢 Low | Thấp | **P4** |

---

## ROADMAP KHẮC PHỤC ĐỀ XUẤT

### Sprint 1 — Nền tảng vững chắc (1-2 tuần)
- [ ] Tái cấu trúc root directory: di chuyển toàn bộ scripts/debug/artifacts
- [ ] Xóa file `.resolved`, binary `.mp4`, unify 2 JSON files
- [ ] Thêm CI/CD GitHub Actions (test + lint)
- [ ] Bọc toàn bộ pipeline loop bằng try/except + error recovery
- [ ] Pin versions trong requirements.txt

### Sprint 2 — Sửa lỗi thuật toán (2-4 tuần)
- [ ] Implement negation detection trong Emotion Detector
- [ ] Thêm specificity scoring cho LuatNhan conflict resolution
- [ ] Thay Levenshtein bằng token-level + semantic conflict check trong TM
- [ ] Implement fallback chain cho Pronoun 4D Matrix

### Sprint 3 — Nâng cao chất lượng (4-6 tuần)
- [ ] Thêm N-best matching cho Trie (thay greedy LPM)
- [ ] Fix chapter boundary handling trong Context Manager
- [ ] Pydantic schema validation cho MD dictionary
- [ ] Tạo golden benchmark dataset từ 24 dự án cũ
- [ ] Thêm edge case tests

### Sprint 4 — Production readiness (6-8 tuần)
- [ ] Validate Tauri native build trên Windows/Mac/Linux
- [ ] Nâng cấp EN-VI engine với lightweight dependency parsing
- [ ] Schema migration versioning
- [ ] Document HMM training data source

---

*Báo cáo được tạo tự động từ phân tích static của source code và tài liệu thiết kế. Một số vấn đề có thể đã được giải quyết trong code chưa được commit hoặc chưa được public.*
