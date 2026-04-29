# THUẬT TOÁN QUÉT LỌC, PHÂN TÍCH VÀ THỐNG KÊ DẠNG NGỮ PHÁP TRONG FILE TXT — KHÔNG DÙNG LLM

**Repo mục tiêu:** `converter-drduc`  
**Milestone đề xuất:** `v23.5 — Non-LLM Grammar Pattern Mining Engine`  
**Nguyên tắc:** deterministic / rule-based / statistical mining / không dùng LLM / không gọi API AI.

---

## 1. Câu trả lời quan trọng: cấu trúc ngữ pháp chưa nêu trong code có phát hiện được không?

Có, nhưng cần phân biệt rõ **2 mức phát hiện**.

### 1.1. Mức 1 — Nhận diện chính xác theo rule đã khai báo

Nếu cấu trúc đã có trong `grammar_patterns.yml` hoặc trong code scanner, hệ thống có thể nhận diện chính xác:

```text
只要...就...
虽然...但是...
一边...一边...
被...
为...所...
作为...
所谓...
据说...
非...不可...
```

Ở mức này, output sẽ có:

```text
rule_id
category
tên cấu trúc
span match
chapter_id
câu gốc
confidence
ví dụ thật
```

Ví dụ:

```text
只要他愿意，就能离开这里。
→ rule_id = condition_zhiyao_jiu
→ category = condition
→ name = 只要...就...
```

### 1.2. Mức 2 — Phát hiện nghi vấn đối với cấu trúc chưa khai báo

Nếu cấu trúc **chưa được nêu trong code**, hệ thống **không thể tự biết tên ngữ pháp chính xác** như LLM, nhưng vẫn có thể phát hiện bằng thuật toán thống kê và heuristic:

```text
1. Marker mining:
   phát hiện từ/cụm có tần suất cao quanh dấu câu, ví dụ: 偏偏, 索性, 竟是, 倒也, 说到底.

2. Paired-marker mining:
   phát hiện cặp marker lặp lại theo khung A...B, ví dụ: 越...越..., 既...又..., 不是...而是....

3. Frame mining:
   phát hiện khung cú pháp lặp lại có khoảng trống giữa các marker, ví dụ:
   与其X不如Y
   宁可X也不Y
   不是X而是Y

4. Clause-boundary anomaly:
   phát hiện các câu dài có marker lạ quanh dấu phẩy/chấm phẩy nhưng chưa match rule nào.

5. High-frequency unknown pattern:
   thống kê n-gram hoặc skip-gram xuất hiện nhiều lần trong các câu chưa được rule nào bao phủ.

6. Residual-unmatched analysis:
   sau khi quét hết rule đã biết, phần câu còn lại nếu xuất hiện lặp lại nhiều sẽ được đưa vào hàng chờ review.
```

Vì vậy, thuật toán nên có thêm lớp:

```text
UnknownGrammarPatternMiner
```

Output của lớp này không phải “rule chắc chắn”, mà là:

```text
candidate_pattern
candidate_category_guess
frequency
chapter_count
example_sentences
confidence_score
suggested_rule_template
status = REVIEW
```

Kết luận:

```text
- Cấu trúc đã khai báo: nhận diện chính xác.
- Cấu trúc chưa khai báo: phát hiện được dạng nghi vấn / pattern candidate, không tự đặt nhãn tuyệt đối.
- Sau khi người dùng duyệt candidate, hệ thống thêm vào grammar_patterns.yml và từ lần sau nhận diện chính xác.
```

---

## 2. Mục tiêu thuật toán

Thuật toán đọc một file truyện nguồn `.txt` tiếng Trung và tự động:

```text
1. Tách chương.
2. Tách đoạn / segment / câu / mệnh đề.
3. Lọc hoặc đánh dấu đoạn rác: PS, cầu phiếu, quảng cáo, ghi chú tác giả.
4. Bảo vệ system panel, quote, số, tên riêng, bracket entity.
5. Quét các mẫu ngữ pháp đã biết.
6. Phát hiện mẫu ngữ pháp chưa biết bằng thống kê.
7. Phân loại dạng ngữ pháp.
8. Đếm tần suất theo toàn truyện / chương / category.
9. Trích ví dụ thật từ corpus.
10. Xuất JSON / CSV / Markdown.
11. Sinh backlog rule cần bổ sung vào Grammar Transfer.
```

---

## 3. Kiến trúc module đề xuất

```text
src/analysis/
  __init__.py
  txt_corpus_reader.py
  segment_classifier.py
  noise_segment_filter.py
  protected_span_detector.py
  clause_splitter_for_analysis.py
  grammar_pattern_registry.py
  grammar_pattern_scanner.py
  unknown_pattern_miner.py
  grammar_stats.py
  grammar_reporter.py
  backlog_generator.py

data/grammar/
  grammar_patterns.yml
  grammar_pattern_categories.yml
  discourse_markers.yml
  unknown_marker_seed.yml

data/noise/
  noise_patterns.yml
  hard_keep_patterns.yml

scripts/
  scan_grammar_patterns.py

tests/test_analysis/
  test_txt_corpus_reader.py
  test_noise_segment_filter.py
  test_protected_span_detector.py
  test_grammar_pattern_scanner.py
  test_unknown_pattern_miner.py
  test_grammar_stats.py
```

---

## 4. Pipeline tổng thể

```text
TXT file
  ↓
Normalize text
  ↓
Split chapters
  ↓
Split paragraphs
  ↓
Classify segment
  ↓
Noise filter
  ↓
Protected span detection
  ↓
Sentence split
  ↓
Clause split
  ↓
Known GrammarPatternScanner
  ↓
UnknownGrammarPatternMiner
  ↓
Conflict / overlap resolution
  ↓
Statistics aggregation
  ↓
Export report
  ↓
Generate rule backlog
```

Pseudo-flow:

```python
def analyze_txt_file(txt_path: str, config_path: str):
    text = read_txt(txt_path)
    text = normalize_text(text)

    chapters = split_chapters(text)

    registry = GrammarPatternRegistry.from_yaml(config_path)
    unknown_miner = UnknownGrammarPatternMiner()
    stats = GrammarStats()

    for chapter in chapters:
        paragraphs = split_paragraphs(chapter.text)

        for para_index, paragraph in enumerate(paragraphs):
            seg_type = classify_segment(paragraph)

            noise_decision = filter_noise(paragraph, seg_type)
            if noise_decision.action == "drop":
                stats.add_noise(paragraph, chapter.id, noise_decision)
                continue

            protected_spans = detect_protected_spans(paragraph)
            sentences = split_sentences(paragraph, protected_spans)

            for sent_index, sentence in enumerate(sentences):
                clauses = split_clauses(sentence.text, protected_spans)

                for clause in clauses:
                    known_matches = registry.scan(
                        text=clause.text,
                        protected_spans=protected_spans
                    )

                    resolved_known = resolve_overlaps(known_matches)

                    stats.add_known_matches(
                        matches=resolved_known,
                        chapter_id=chapter.id,
                        paragraph_index=para_index,
                        sentence_index=sent_index,
                        source_sentence=sentence.text
                    )

                    unknown_candidates = unknown_miner.scan_unmatched_clause(
                        clause=clause.text,
                        known_matches=resolved_known,
                        chapter_id=chapter.id,
                        source_sentence=sentence.text
                    )

                    stats.add_unknown_candidates(unknown_candidates)

    return stats.export()
```

---

## 5. Chuẩn hóa văn bản đầu vào

```python
def normalize_text(text: str) -> str:
    replacements = {
        "\ufeff": "",
        "\u3000": " ",
        "\xa0": " ",
        "\r\n": "\n",
        "\r": "\n",
        "﹐": "，",
        "﹑": "、",
        "﹔": "；",
        "﹕": "：",
        "﹗": "！",
        "﹖": "？",
    }

    for src, dst in replacements.items():
        text = text.replace(src, dst)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
```

---

## 6. Tách chương

```python
CHAPTER_PATTERNS = [
    r"^第[零一二三四五六七八九十百千万\d]+[章节回卷篇].*$",
    r"^第\s*\d+\s*[章节回卷篇].*$",
    r"^卷[一二三四五六七八九十百千万\d]+.*$",
    r"^番外.*$",
    r"^序章.*$",
    r"^楔子.*$",
]
```

```python
@dataclass
class Chapter:
    id: str
    title: str
    index: int
    text: str
    start_offset: int
    end_offset: int
```

---

## 7. Lọc segment rác

### 7.1. Segment type

```python
class SegmentType(Enum):
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    THOUGHT = "thought"
    SYSTEM_PROMPT = "system_prompt"
    CHAPTER_TITLE = "chapter_title"
    AUTHOR_NOTE = "author_note"
    ADVERTISEMENT = "advertisement"
    FORUM_POST = "forum_post"
    UNKNOWN = "unknown"
```

### 7.2. Noise patterns

```python
NOISE_PATTERNS = {
    "author_note": [
        r"PS[:：]",
        r"作者有话说",
        r"本章完",
        r"未完待续",
        r"今天.*更新",
        r"明天.*更新",
    ],
    "advertisement": [
        r"求收藏",
        r"求推荐",
        r"求月票",
        r"求订阅",
        r"新书上传",
        r"推荐票",
        r"月票",
        r"打赏",
    ],
    "forum": [
        r"楼主",
        r"顶一下",
        r"沙发",
        r"板凳",
        r"水贴",
    ],
}
```

### 7.3. Hard keep patterns

```python
HARD_KEEP_PATTERNS = [
    r"^【(?:系统|面板|属性|任务|技能|奖励|提示|状态).{0,50}】$",
    r"【[^】]{2,40}】.*(?:启动|获得|激活|完成|开启|关闭|出现|绑定)",
    r".*(?:获得|激活|启动|绑定).*【[^】]{2,40}】",
]
```

---

## 8. Protected span detection

```python
@dataclass
class ProtectedSpan:
    start: int
    end: int
    text: str
    span_type: str
    priority: int
```

```python
PROTECTED_PATTERNS = [
    ("system_panel", r"【[^】]{1,80}】", 90),
    ("quote", r"“[^”]{1,300}”", 80),
    ("quote", r"‘[^’]{1,300}’", 80),
    ("time", r"\d{1,2}[:：]\d{2}(?::\d{2})?", 70),
    ("rank", r"[A-Z]{1,3}[+-]?级", 70),
    ("version", r"v\d+(?:\.\d+)+", 70),
    ("number_unit", r"\d+(?:\.\d+)?(?:万|亿|千|百|米|公里|岁|年|天|小时)", 60),
]
```

---

## 9. Known Grammar Pattern Registry

```python
@dataclass
class GrammarPattern:
    rule_id: str
    category: str
    name: str
    regex: str
    priority: int
    description: str
    examples: list[str]
```

```python
@dataclass
class GrammarMatch:
    rule_id: str
    category: str
    name: str
    matched_text: str
    start: int
    end: int
    confidence: float
    source_sentence: str
    chapter_id: str | None = None
    paragraph_index: int | None = None
    sentence_index: int | None = None
```

---

## 10. Danh mục dạng ngữ pháp đã biết cần quét

### 10.1. Điều kiện

```yaml
- rule_id: condition_ruguo_jiu
  category: condition
  name: 如果...就...
  regex: "如果(?P<cond>.+?)(?:，)?就(?P<result>.+)"
  priority: 80

- rule_id: condition_zhiyao_jiu
  category: condition
  name: 只要...就...
  regex: "只要(?P<cond>.+?)(?:，)?就(?P<result>.+)"
  priority: 82

- rule_id: condition_yidan_jiu
  category: condition
  name: 一旦...就/便...
  regex: "一旦(?P<cond>.+?)(?:，)?(?:就|便)(?P<result>.+)"
  priority: 82

- rule_id: condition_chufei_fouze
  category: condition
  name: 除非...否则...
  regex: "除非(?P<cond>.+?)(?:，)?否则(?P<result>.+)"
  priority: 85
```

### 10.2. Nhượng bộ

```yaml
- rule_id: concession_suiran_danshi
  category: concession
  name: 虽然...但是...
  regex: "虽然(?P<a>.+?)(?:，)?(?:但是|但|却)(?P<b>.+)"
  priority: 80

- rule_id: concession_jibian_ye
  category: concession
  name: 即便...也...
  regex: "即便(?P<a>.+?)(?:，)?也(?P<b>.+)"
  priority: 82

- rule_id: concession_napa_ye
  category: concession
  name: 哪怕...也...
  regex: "哪怕(?P<a>.+?)(?:，)?也(?P<b>.+)"
  priority: 84

- rule_id: concession_jiusuan_ye
  category: concession
  name: 就算...也...
  regex: "就算(?P<a>.+?)(?:，)?也(?P<b>.+)"
  priority: 84
```

### 10.3. Bị động

```yaml
- rule_id: passive_bei
  category: passive
  name: 被 passive
  regex: "被(?P<agent>[^，。！？；]{1,20})?(?P<verb>[^，。！？；]{1,40})"
  priority: 75

- rule_id: passive_wei_suo
  category: passive
  name: 为...所...
  regex: "为(?P<agent>[^，。！？；]{1,30})所(?P<verb>[^，。！？；]{1,30})"
  priority: 85

- rule_id: passive_bei_suo
  category: passive
  name: 被...所...
  regex: "被(?P<agent>[^，。！？；]{1,30})所(?P<verb>[^，。！？；]{1,30})"
  priority: 85
```

### 10.4. Các nhóm khác

```yaml
- rule_id: ba_construction
  category: disposal
  name: 把 construction
  regex: "把(?P<object>[^，。！？；]{1,40})(?P<verb>[^，。！？；]{1,40})"
  priority: 78

- rule_id: viewpoint_zuowei
  category: viewpoint
  name: 作为...
  regex: "作为(?P<role>[^，。！？；]{1,30})(?:而言|来说|来讲)?"
  priority: 82

- rule_id: parallel_yibian_yibian
  category: parallel_action
  name: 一边...一边...
  regex: "一边(?P<a>[^，。！？；]{1,40})一边(?P<b>[^，。！？；]{1,40})"
  priority: 84

- rule_id: definition_suowei
  category: definition
  name: 所谓...
  regex: "所谓(?P<term>[^，。！？；]{1,40})"
  priority: 78

- rule_id: minimizing_bale
  category: minimizing
  name: X罢了
  regex: "[^，。！？；]{1,40}罢了"
  priority: 75

- rule_id: evidential_jushuo
  category: evidential
  name: 据说
  regex: "据说"
  priority: 70

- rule_id: comparison_yu_x_xiangbi
  category: comparison
  name: 与X相比
  regex: "与(?P<x>[^，。！？；]{1,30})相比"
  priority: 78

- rule_id: precaution_yifang
  category: precaution
  name: 以防...
  regex: "以防(?P<x>[^，。！？；]{1,40})"
  priority: 78

- rule_id: emphatic_jiulian_ye
  category: emphatic_even
  name: 就连X也Y
  regex: "就连(?P<x>[^，。！？；]{1,30})也(?P<y>[^，。！？；]{1,40})"
  priority: 82

- rule_id: enumeration_yilai_erlai
  category: enumeration
  name: 一来...二来...
  regex: "一来(?P<a>.+?)二来(?P<b>.+)"
  priority: 82

- rule_id: necessity_fei_buke
  category: necessity
  name: 非X不可
  regex: "非(?P<x>[^，。！？；]{1,30})不可"
  priority: 82
```

---

## 11. UnknownGrammarPatternMiner — phát hiện cấu trúc chưa có trong code

### 11.1. Candidate model

```python
@dataclass
class UnknownPatternCandidate:
    candidate_id: str
    pattern_text: str
    pattern_type: str
    frequency: int
    chapter_count: int
    confidence: float
    examples: list[str]
    guessed_category: str | None
    suggested_regex: str | None
    status: str = "review"
```

### 11.2. Marker seed

```python
UNKNOWN_MARKER_SEED = [
    "偏偏", "索性", "竟是", "竟然", "倒也", "反倒", "终究", "毕竟",
    "说到底", "换句话说", "与其", "不如", "宁可", "也不",
    "不是", "而是", "既", "又", "越", "越", "再怎么", "也",
    "莫非", "难不成", "何况", "更何况", "只不过", "不过是",
]
```

### 11.3. Paired marker mining

```python
PAIRED_MARKERS = [
    ("与其", "不如", "preference"),
    ("宁可", "也不", "preference"),
    ("不是", "而是", "contrast_correction"),
    ("既", "又", "parallel_attribute"),
    ("越", "越", "progressive_comparison"),
    ("再", "也", "concession_limit"),
    ("哪怕", "也", "concession"),
    ("即使", "也", "concession"),
]
```

```python
def mine_paired_markers(sentence: str) -> list[UnknownPatternCandidate]:
    candidates = []

    for left, right, guess in PAIRED_MARKERS:
        if left in sentence and right in sentence:
            lpos = sentence.find(left)
            rpos = sentence.find(right)

            if 0 <= lpos < rpos:
                candidates.append(UnknownPatternCandidate(
                    candidate_id=f"unknown_pair_{left}_{right}",
                    pattern_text=f"{left}...{right}",
                    pattern_type="paired_marker",
                    frequency=1,
                    chapter_count=1,
                    confidence=0.75,
                    examples=[sentence],
                    guessed_category=guess,
                    suggested_regex=f"{left}(?P<a>.+?){right}(?P<b>.+)",
                ))

    return candidates
```

### 11.4. High-frequency n-gram mining

```python
def char_ngrams(text: str, n_min=2, n_max=6):
    for n in range(n_min, n_max + 1):
        for i in range(0, len(text) - n + 1):
            gram = text[i:i+n]
            if should_keep_ngram(gram):
                yield gram


def should_keep_ngram(gram: str) -> bool:
    if re.search(r"[，。！？；、\s]", gram):
        return False

    if len(gram) < 2:
        return False

    if re.fullmatch(r"\d+", gram):
        return False

    return True
```

### 11.5. Grammar-like marker scoring

```python
GRAMMAR_LIKE_CHARS = set("虽若即便但却而乃则就也都只又再还更非无未莫何其所为被把将于以因由故")


def looks_like_grammar_marker(gram: str) -> bool:
    if gram in UNKNOWN_MARKER_SEED:
        return True

    if any(ch in GRAMMAR_LIKE_CHARS for ch in gram):
        return True

    if gram.endswith(("而已", "罢了", "来说", "而言", "之下", "之中")):
        return True

    return False
```

### 11.6. Clause anomaly mining

```python
def mine_clause_anomaly(clause: str, known_matches: list[GrammarMatch]):
    if known_matches:
        return []

    markers = [m for m in UNKNOWN_MARKER_SEED if m in clause]

    if len(clause) >= 20 and markers:
        return [
            UnknownPatternCandidate(
                candidate_id=f"unknown_clause_{hash_text(clause[:30])}",
                pattern_text=" / ".join(markers),
                pattern_type="clause_anomaly",
                frequency=1,
                chapter_count=1,
                confidence=0.55 + min(len(markers) * 0.05, 0.2),
                examples=[clause],
                guessed_category=None,
                suggested_regex=None,
            )
        ]

    return []
```

### 11.7. Unknown miner class

```python
class UnknownGrammarPatternMiner:
    def __init__(self):
        self.candidate_counter = Counter()
        self.examples = defaultdict(list)
        self.chapter_sets = defaultdict(set)

    def scan_unmatched_clause(
        self,
        clause: str,
        known_matches: list[GrammarMatch],
        chapter_id: str,
        source_sentence: str
    ) -> list[UnknownPatternCandidate]:
        candidates = []

        candidates.extend(mine_paired_markers(clause))
        candidates.extend(mine_clause_anomaly(clause, known_matches))

        for cand in candidates:
            key = cand.pattern_text
            self.candidate_counter[key] += 1
            self.chapter_sets[key].add(chapter_id)

            if len(self.examples[key]) < 10:
                self.examples[key].append(source_sentence)

        return candidates

    def finalize(self, min_count=5) -> list[UnknownPatternCandidate]:
        finalized = []

        for pattern_text, count in self.candidate_counter.items():
            if count < min_count:
                continue

            chapters = self.chapter_sets[pattern_text]
            examples = self.examples[pattern_text]

            finalized.append(UnknownPatternCandidate(
                candidate_id=f"unknown_{hash_text(pattern_text)}",
                pattern_text=pattern_text,
                pattern_type="aggregated_unknown",
                frequency=count,
                chapter_count=len(chapters),
                confidence=self._score(count, len(chapters)),
                examples=examples,
                guessed_category=guess_category_from_marker(pattern_text),
                suggested_regex=suggest_regex_from_pattern_text(pattern_text),
                status="review"
            ))

        return sorted(finalized, key=lambda c: (-c.confidence, -c.frequency))

    def _score(self, frequency: int, chapter_count: int) -> float:
        score = 0.35
        score += min(frequency / 50, 0.35)
        score += min(chapter_count / 20, 0.2)
        return min(score, 0.95)
```

---

## 12. Backlog generator

```python
def generate_rule_backlog(stats: GrammarStats, unknown_candidates: list[UnknownPatternCandidate], min_count: int = 20):
    backlog = []

    for rule_id, stat in stats.by_rule.items():
        if stat.count >= min_count:
            backlog.append({
                "type": "known_rule_optimization",
                "rule_id": rule_id,
                "category": stat.category,
                "count": stat.count,
                "priority": estimate_priority(stat),
                "reason": "high_frequency_known_pattern",
                "examples": [ex.source_sentence for ex in stat.examples[:3]],
            })

    for cand in unknown_candidates:
        if cand.frequency >= 10 and cand.confidence >= 0.65:
            backlog.append({
                "type": "new_rule_candidate",
                "candidate_id": cand.candidate_id,
                "pattern_text": cand.pattern_text,
                "guessed_category": cand.guessed_category,
                "count": cand.frequency,
                "priority": estimate_unknown_priority(cand),
                "reason": "frequent_unknown_grammar_frame",
                "suggested_regex": cand.suggested_regex,
                "examples": cand.examples[:3],
            })

    return sorted(backlog, key=lambda x: -x["priority"])
```

---

## 13. Output mong muốn

### 13.1. JSON

```json
{
  "summary": {
    "total_rules_matched": 42,
    "total_matches": 18321,
    "by_category": {
      "condition": 1230,
      "concession": 884,
      "passive": 702,
      "parallel_action": 391
    },
    "unknown_candidate_count": 87
  },
  "unknown_candidates": [
    {
      "candidate_id": "unknown_abc123",
      "pattern_text": "与其...不如",
      "pattern_type": "paired_marker",
      "frequency": 37,
      "chapter_count": 18,
      "confidence": 0.86,
      "guessed_category": "preference",
      "suggested_regex": "与其(?P<a>.+?)不如(?P<b>.+)",
      "status": "review"
    }
  ]
}
```

### 13.2. Markdown

```md
# Báo cáo thống kê dạng ngữ pháp

## Tổng quan

- Tổng số rule matched: 42
- Tổng số match: 18321
- Tổng số unknown candidates: 87

## Candidate cấu trúc chưa có trong code

| Candidate | Type | Frequency | Chapters | Confidence | Guess |
|---|---|---:|---:|---:|---|
| `与其...不如` | paired_marker | 37 | 18 | 0.86 | preference |
| `不是...而是` | paired_marker | 54 | 21 | 0.90 | contrast_correction |
```

---

## 14. Test cases bắt buộc

```python
def test_detect_condition_zhiyao_jiu():
    text = "只要他愿意，就能离开这里。"
    matches = registry.scan(text, [])
    assert any(m.rule_id == "condition_zhiyao_jiu" for m in matches)


def test_detect_parallel_yibian():
    text = "他一边走一边说。"
    matches = registry.scan(text, [])
    assert any(m.rule_id == "parallel_yibian_yibian" for m in matches)


def test_do_not_scan_inside_system_panel():
    text = "【系统提示：只要完成任务就能获得奖励】"
    spans = detect_protected_spans(text)
    matches = registry.scan(text, spans)
    assert len(matches) == 0


def test_noise_drop_author_note():
    text = "PS：明天中午12点更新，求月票。"
    seg_type = classify_segment(text)
    decision = filter_noise(text, seg_type)
    assert decision.action in {"drop", "metadata"}


def test_hard_keep_system_panel():
    text = "【面板未开启】"
    seg_type = classify_segment(text)
    decision = filter_noise(text, seg_type)
    assert decision.action == "keep"


def test_unknown_pair_marker_detection():
    text = "与其坐以待毙，不如主动出击。"
    cands = mine_paired_markers(text)
    assert any(c.pattern_text == "与其...不如" for c in cands)


def test_unknown_candidate_is_review_not_auto_rule():
    text = "与其坐以待毙，不如主动出击。"
    cands = mine_paired_markers(text)
    assert cands[0].status == "review"
```

---

## 15. Checklist triển khai

```text
A. Corpus reader
  [ ] read_txt()
  [ ] normalize_text()
  [ ] split_chapters()
  [ ] split_paragraphs()

B. Segment/noise
  [ ] SegmentType
  [ ] classify_segment()
  [ ] filter_noise()
  [ ] hard_keep_patterns
  [ ] stop_phrase_patterns

C. Protected span
  [ ] ProtectedSpan
  [ ] detect_protected_spans()
  [ ] resolve overlap

D. Sentence/clause
  [ ] split_sentences()
  [ ] split_clauses()
  [ ] marker table

E. Known grammar pattern
  [ ] GrammarPattern
  [ ] GrammarMatch
  [ ] GrammarPatternRegistry
  [ ] grammar_patterns.yml
  [ ] overlap resolver

F. Unknown grammar mining
  [ ] UnknownPatternCandidate
  [ ] UnknownGrammarPatternMiner
  [ ] marker seed
  [ ] paired-marker mining
  [ ] n-gram mining
  [ ] frame-template mining
  [ ] clause anomaly mining

G. Statistics
  [ ] GrammarStats
  [ ] by_rule
  [ ] by_category
  [ ] by_chapter
  [ ] unknown_candidates
  [ ] examples

H. Export
  [ ] JSON
  [ ] CSV
  [ ] Markdown
  [ ] backlog generation

I. CLI
  [ ] scripts/scan_grammar_patterns.py
  [ ] argparse
  [ ] out-dir
  [ ] unknown-min-count

J. Tests
  [ ] condition
  [ ] concession
  [ ] passive
  [ ] ba
  [ ] system protected
  [ ] noise
  [ ] unknown pair marker
  [ ] export
```

---

## 16. Kết luận

Thuật toán này có 2 tầng:

```text
1. GrammarPatternScanner:
   nhận diện chính xác các cấu trúc đã khai báo trong code/config.

2. UnknownGrammarPatternMiner:
   phát hiện cấu trúc chưa khai báo bằng thống kê, marker, n-gram, paired-marker và frame-template.
```

Câu trả lời cho câu hỏi “các cấu trúc chưa được nêu bên trong code thì có nhận diện được không?” là:

```text
Có thể phát hiện dưới dạng candidate/review, không tự khẳng định chắc chắn là rule hoàn chỉnh.

Muốn nhận diện chính xác ở các lần sau, cần:
1. Review candidate.
2. Đặt tên rule_id/category.
3. Thêm regex/template vào grammar_patterns.yml.
4. Viết test.
5. Đưa vào Grammar Transfer nếu cần.
```

Như vậy, hệ thống vẫn **không dùng LLM**, nhưng vẫn có khả năng mở rộng dần nhờ thống kê corpus và vòng lặp review.
