# KẾ HOẠCH CHI TIẾT HOÀN THIỆN REPO `converter-drduc`

**Mục tiêu:** Hoàn thiện repo `converter-drduc` thành một hệ thống dịch truyện Trung→Việt có lõi deterministic/RBMT ổn định, có trace, metadata database, grammar transfer planner, entity graph, context resolver, noise filter an toàn và learning loop có kiểm duyệt.

**Định hướng tổng thể:** Không viết lại repo từ đầu. Giữ backbone hiện tại gồm `TrieEngine`, `LuatNhanEngine`, `RBMTTranslator`, `EntityScanner`, `ContextManager`, `QA`, `state/TM`, UI sidecar và desktop shell; bổ sung các lớp production-grade còn thiếu.

---

## 0. Mục tiêu tổng thể

Repo cần đạt các năng lực sau:

```text
1. Nhận diện đúng loại segment: lời kể, thoại, suy nghĩ, system panel, tiêu đề chương, ghi chú tác giả, quảng cáo.
2. Bảo vệ entity, số, system UI, quote, idiom, tên riêng trước mọi rewrite.
3. Chuyển đổi ngữ pháp Trung→Việt theo clause/relation thay vì chỉ rewrite chuỗi.
4. Quét tên riêng đa tầng, chuẩn hóa alias/canonical name xuyên chương.
5. Giữ ngữ cảnh nhân vật, người nói, đại từ và zero-pronoun.
6. Lọc cụm rác an toàn, không xóa nhầm nội dung thật.
7. Tách TM máy và TM đã duyệt để tránh học sai.
8. Có metadata database, trace, review workflow và regression gate.
9. Sau mỗi lần dịch, hệ thống học từ bản sửa nhưng chỉ promote sau kiểm duyệt.
```

---

## 1. Kiến trúc mục tiêu

### 1.1. Pipeline đích

```text
Input ZH document
  ↓
DocumentImporter
  ↓
ChapterSplitter
  ↓
SegmentClassifier
  ↓
SegmentPacket
  ↓
ProtectedSpanRegistry
  ↓
NoisePreFilter
  ↓
EntityPipeline 7-pass
  ↓
ClauseSegmenter
  ↓
RelationDetector
  ↓
GrammarRuleRegistry + ConflictResolver
  ↓
TransferPlanner
  ↓
LexicalDecoder / Trie / LuatNhan
  ↓
VietnameseSurfaceRealizer
  ↓
ContextResolver
  ↓
NoisePostFilter
  ↓
QA Engine
  ↓
Review UI
  ↓
Metadata DB
  ↓
LearningLoop / PromotionGate
```

### 1.2. Cấu trúc thư mục đề xuất

```text
src/
  pipeline/
    packet.py
    segment_classifier.py
    protected_span_registry.py
    noise_filter.py
    pretranslation_pipeline.py

  grammar/
    __init__.py
    clause_segmenter.py
    relation_detector.py
    rule_claim.py
    rule_registry.py
    conflict_resolver.py
    transfer_planner.py
    surface_realizer.py
    lexical_decode_policy.py
    idiom_policy.py
    rules/
      rule_viewpoint.py
      rule_condition.py
      rule_concession.py
      rule_passive.py
      rule_ba_construction.py
      rule_parallel_action.py
      rule_definition.py
      rule_evidential.py
      rule_minimizing_suffix.py
      rule_comparison.py
      rule_precaution.py
      rule_time_skip.py
      rule_reference_qizhong.py
      rule_formal_reasoning.py
      rule_emphatic_even.py

  entities/
    __init__.py
    entity_pipeline.py
    exact_lexicon_pass.py
    pattern_ner.py
    repeated_subject_pass.py
    transliteration_engine.py
    alias_graph.py
    entity_ranker.py
    entity_promoter.py
    entity_types.py

  context/
    __init__.py
    speaker_tracker.py
    mention_memory.py
    entity_salience.py
    zero_pronoun_detector.py
    vi_pronoun_selector.py
    register_policy.py

  learning/
    __init__.py
    review_diff.py
    error_classifier.py
    candidate_miner.py
    promotion_gate.py
    regression_runner.py
    evaluation_reporter.py

  state/
    metadata_db.py
    translation_memory.py
    migrations/
      001_tm_split.sql
      002_entities.sql
      003_alias_graph.sql
      004_learning_loop.sql
      005_evaluation_runs.sql

data/
  grammar/
    relation_templates.yml
    grammar_rule_priority.yml
    idiom_lexicon.tsv
    discourse_markers.yml
    register_policy.yml

  entities/
    entity_seed_glossary.csv
    entity_type_patterns.yml
    alias_patterns.yml
    transliteration_rules.yml
    title_suffixes.yml
    faction_suffixes.yml

  noise/
    hard_keep_patterns.yml
    soft_keep_patterns.yml
    stop_phrase_patterns.yml
    author_note_patterns.yml
    forum_patterns.yml
    advertisement_patterns.yml

  tests_gold/
    segments_gold.jsonl
    grammar_patterns_gold.yaml
    entity_gold.jsonl
    coref_miniset.jsonl
    noise_gold.jsonl
    full_chapter_regression/

tests/
  test_segment_typing/
  test_protected_spans/
  test_noise_filter/
  test_clause_segmenter/
  test_relation_detector/
  test_grammar_rules/
  test_entity_pipeline/
  test_alias_graph/
  test_context_resolver/
  test_learning_loop/
  test_tm_governance/
  test_full_chapter_regression/
```

---

## 2. Giai đoạn 1 — Hardening baseline và khóa nguồn sự thật

### 2.1. Task H01 — Đồng bộ README, tracker, trạng thái test

#### Việc cần làm

```text
H01.1. Kiểm tra README hiện tại.
H01.2. Kiểm tra project_progress.json.
H01.3. Chạy pytest toàn bộ repo.
H01.4. Ghi lại số test thật hiện tại.
H01.5. Đồng bộ README với số test thật.
H01.6. Đồng bộ tracker với trạng thái module thật.
H01.7. Tạo file docs/ARCHITECTURE_STATUS.md.
```

#### Output

```text
README.md cập nhật.
project_progress.json cập nhật.
docs/ARCHITECTURE_STATUS.md.
```

#### Definition of Done

```text
- README không còn lệch với test count.
- Có danh sách module implemented / partial / missing.
- Có lệnh verify chuẩn.
```

---

### 2.2. Task H02 — Freeze schema trace

#### Model đề xuất

```python
@dataclass
class TraceEvent:
    segment_id: str
    stage: str
    rule_id: str | None
    input_span: tuple[int, int] | None
    output_span: tuple[int, int] | None
    action: str
    confidence: float
    metadata: dict
```

#### File cần tạo/sửa

```text
src/pipeline/packet.py
src/core/trace.py
src/engine/rbmt_translator.py
src/qa/report.py
```

#### Definition of Done

```text
- Mỗi segment có trace_id.
- Mỗi rule/entity/noise/context decision có trace.
- QA report có thể hiển thị decision path.
```

---

### 2.3. Task H03 — Tách Translation Memory machine/approved

Đây là task quan trọng nhất để tránh learning loop tự khuếch đại lỗi. Nếu output RBMT được lưu như “verified”, lỗi entity/grammar có thể bị tái sử dụng nhiều chương sau và trở thành “sự thật giả” trong TM.

#### Schema đề xuất

```sql
CREATE TABLE tm_machine (
  id INTEGER PRIMARY KEY,
  source_hash TEXT NOT NULL,
  source_text TEXT NOT NULL,
  machine_target TEXT NOT NULL,
  engine_version TEXT,
  rule_version TEXT,
  quality_score REAL,
  created_at TEXT,
  trace_json TEXT
);

CREATE TABLE tm_approved (
  id INTEGER PRIMARY KEY,
  source_hash TEXT NOT NULL UNIQUE,
  source_text TEXT NOT NULL,
  approved_target TEXT NOT NULL,
  domain TEXT,
  register TEXT,
  reviewer TEXT,
  approved_at TEXT,
  confidence REAL,
  provenance TEXT
);

CREATE TABLE tm_reviewed (
  id INTEGER PRIMARY KEY,
  source_hash TEXT NOT NULL,
  source_text TEXT NOT NULL,
  machine_target TEXT,
  edited_target TEXT,
  reviewer TEXT,
  review_status TEXT,
  created_at TEXT
);
```

#### Task chi tiết

```text
H03.1. Viết migration 001_tm_split.sql.
H03.2. Sửa TranslationMemory.lookup():
       lookup order = tm_approved exact → tm_approved fuzzy → tm_machine suggestion.
H03.3. Sửa RBMTTranslator:
       output máy chỉ lưu vào tm_machine.
H03.4. Thêm API promote_to_approved().
H03.5. Thêm guard: machine output không bao giờ có status verified.
H03.6. Viết test chống regression.
```

#### Test bắt buộc

```python
def test_rbmt_output_never_goes_to_approved_tm():
    result = translator.translate("他走了。")
    assert tm_machine.exists("他走了。")
    assert not tm_approved.exists("他走了。")

def test_only_reviewed_output_can_promote_to_approved():
    review_id = save_human_review(...)
    promote_to_approved(review_id)
    assert tm_approved.exists(source_hash)
```

---

## 3. Giai đoạn 2 — Segment typing và SegmentPacket

### 3.1. Task S01 — Tạo `SegmentType`

```python
class SegmentType(Enum):
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    THOUGHT = "thought"
    SYSTEM_PROMPT = "system_ui"
    CHAPTER_TITLE = "chapter_title"
    AUTHOR_NOTE = "author_note"
    FORUM_POST = "forum"
    ADVERTISEMENT = "ad"
```

---

### 3.2. Task S02 — Tạo `SegmentPacket`

```python
@dataclass
class SegmentPacket:
    segment_id: str
    chapter_id: str
    position: int
    raw_text: str
    normalized_text: str
    seg_type: SegmentType
    confidence: float
    protected_spans: list[ProtectedSpan]
    metadata: dict
    trace: list[TraceEvent]
```

#### File cần tạo

```text
src/pipeline/packet.py
```

---

### 3.3. Task S03 — Implement `SegmentClassifier`

#### Rule priority

```text
1. Hard pattern:
   - tiêu đề chương
   - system panel
   - author note
   - quảng cáo / CTA
2. Positional heuristic:
   - đầu chương
   - cuối chương
   - sau tiêu đề
3. Content heuristic:
   - thoại
   - suy nghĩ
   - forum
4. Fallback:
   - narration
```

#### Pattern mẫu

```python
CHAPTER_TITLE_PATTERNS = [
    r"^第[零一二三四五六七八九十百千\d]+[章节回卷篇]",
    r"^第\d+章",
    r"^Chapter\s+\d+",
    r"^番外",
]

AUTHOR_NOTE_PATTERNS = [
    r"PS[:：]",
    r"作者有话说",
    r"本章完",
    r"求月票",
    r"求推荐",
    r"求收藏",
    r"新书上传",
]

SYSTEM_PROMPT_PATTERNS = [
    r"^【(?:系统|面板|任务|属性|提示|状态|技能|奖励).{0,40}】$",
]
```

#### Edge cases bắt buộc

```python
SEGMENT_TYPE_TEST_CASES = [
    ("【面板未开启】", SegmentType.SYSTEM_PROMPT),
    ("第三百二十一章 黑夜之心", SegmentType.CHAPTER_TITLE),
    ("（PS：明天中午12点更新）", SegmentType.AUTHOR_NOTE),
    ("求月票！感谢大家支持！", SegmentType.AUTHOR_NOTE),
    ("【奇迹之冠冕号】启动完成。", SegmentType.NARRATION),
    ("他激活了【蜘蛛感应】技能。", SegmentType.NARRATION),
    ("李宇冷声道：'你走吧。'", SegmentType.DIALOGUE),
    ("他心中暗道：这人到底是谁？", SegmentType.THOUGHT),
    ("【本章完】", SegmentType.AUTHOR_NOTE),
    ("楼主说得对！顶一下！", SegmentType.FORUM_POST),
]
```

---

## 4. Giai đoạn 3 — ProtectedSpanRegistry

### 4.1. Task P01 — Tạo model `ProtectedSpan`

```python
@dataclass
class ProtectedSpan:
    start: int
    end: int
    text: str
    span_type: str
    priority: int
    source: str
    lock_level: str   # HARD_LOCK / SOFT_LOCK / REVIEW
    metadata: dict
```

#### Span types

```text
ENTITY
NUMBER
QUOTE
SYSTEM_UI
CHAPTER_TITLE
IDIOM
TIME
DATE
RANK
TECH_VERSION
BRACKET_ITEM
```

---

### 4.2. Task P02 — Implement registry claim

```python
class ProtectedSpanRegistry:
    def claim(self, span: ProtectedSpan) -> None:
        ...

    def is_protected(self, start: int, end: int) -> bool:
        ...

    def resolve_overlap(self) -> list[ProtectedSpan]:
        ...
```

#### Priority đề xuất

```text
100 — system UI / title locked
90  — approved entity
80  — quote span
70  — number/rank/time
60  — idiom literal forbidden
50  — soft entity candidate
```

---

### 4.3. Task P03 — Tích hợp vào pipeline

#### Sửa các module hiện có

```text
src/pipeline/pretranslation_pipeline.py
src/pipeline/entity_scanner.py
src/engine/number_converter.py
src/engine/zh_structure_rewriter.py
src/engine/rbmt_translator.py
```

#### Nguyên tắc

```text
- Grammar rule không sửa text bên trong hard protected span.
- NumberConverter không convert số nằm trong entity hoặc quoted protected span.
- NoiseFilter không drop hard protected segment.
- Entity scanner có thể claim span mới.
```

---

## 5. Giai đoạn 4 — Noise filter an toàn

### 5.1. Task N01 — Tạo `NoiseDecision`

```python
class NoiseAction(Enum):
    KEEP = "keep"
    DROP = "drop"
    REVIEW = "review"
    METADATA = "metadata"
```

```python
@dataclass
class NoiseDecision:
    action: NoiseAction
    confidence: float
    reason: str
    matched_patterns: list[str]
    trace: list[TraceEvent]
```

---

### 5.2. Task N02 — Hard whitelist

Design đúng là “whitelist thắng tuyệt đối”, không phải regex đánh điểm rồi xóa.

#### Hard keep

```yaml
system_ui:
  - "^【(?:系统|面板|任务|属性|技能|奖励|提示).*】$"

narrative_bracket_entity:
  - "【[^】]{2,30}】.*(启动|获得|激活|完成|开启|关闭|出现)"

chapter_title:
  - "^第[零一二三四五六七八九十百千\\d]+[章节回卷篇]"
```

---

### 5.3. Task N03 — Weighted noise score

```python
def filter_noise(packet, resources, state):
    if hard_whitelist.match(packet, state):
        return NoiseDecision(KEEP, 1.0, "hard_whitelist")

    score = 0.0
    score += author_note_score(packet.raw_text)
    score += ad_score(packet.raw_text)
    score += forum_score(packet.raw_text)
    score += cta_score(packet.raw_text)

    score -= entity_keep_bonus(packet)
    score -= narrative_action_bonus(packet)
    score -= dialogue_keep_bonus(packet)

    if score >= 0.80:
        return DROP
    if score >= 0.45:
        return REVIEW
    return KEEP
```

---

### 5.4. Task N04 — Test false-drop prevention

#### Phải KEEP

```text
【奇迹之冠冕号】启动完成。
他获得了【龙之心脏基因链】。
系统提示：任务完成。
【面板未开启】
```

#### Phải DROP/METADATA

```text
PS：明天中午12点更新。
求月票！
【新书上传，求收藏推荐】
本章完
作者有话说
```

---

## 6. Giai đoạn 5 — ClauseSegmenter

### 6.1. Task C01 — Tạo boundary enum

```python
class ClauseBoundary(Enum):
    SENTENCE_END = "sentence_end"
    CLAUSE_SOFT = "clause_soft"
    CLAUSE_HARD = "clause_hard"
    QUOTE_OPEN = "quote_open"
    QUOTE_CLOSE = "quote_close"
    CONJUNCTION = "conjunction"
    CONDITIONAL = "conditional"
    CONCESSIVE = "concessive"
    CAUSE = "cause"
    RESULT = "result"
    TEMPORAL = "temporal"
```

---

### 6.2. Task C02 — Implement tách clause

#### Nguyên tắc

```text
- Không tách trong ProtectedSpan.
- Không tách trong quote.
- Dấu 。！？ là SENTENCE_END.
- Dấu ； là CLAUSE_HARD.
- Dấu ， chỉ tách nếu có marker hoặc độ dài clause đủ lớn.
- Nếu gặp 如果/若/只要/一旦 → CONDITIONAL.
- Nếu gặp 虽然/即便/哪怕/就算 → CONCESSIVE.
- Nếu gặp 因为/由于 → CAUSE.
- Nếu gặp 所以/因此/于是 → RESULT.
```

#### Pseudo-code

```python
def segment(text, protected_spans):
    chars = list(text)
    boundaries = []

    for i, ch in enumerate(chars):
        if registry.is_inside(i):
            continue

        if ch in "。！？":
            boundaries.append(Boundary(i, SENTENCE_END))
        elif ch == "；":
            boundaries.append(Boundary(i, CLAUSE_HARD))
        elif ch == "，":
            marker = detect_marker_around(text, i)
            if marker:
                boundaries.append(Boundary(i, marker.boundary_type))
            elif should_soft_split(text, i):
                boundaries.append(Boundary(i, CLAUSE_SOFT))

    return build_clauses(text, boundaries)
```

---

## 7. Giai đoạn 6 — RelationDetector

### 7.1. Task R01 — Tạo relation enum

```python
class RelationType(Enum):
    CONDITION = "condition"
    CONCESSION = "concession"
    CAUSE_EFFECT = "cause_effect"
    CONTRAST = "contrast"
    TEMPORAL = "temporal"
    PURPOSE = "purpose"
    VIEWPOINT = "viewpoint"
    PASSIVE = "passive"
    DISPOSAL = "ba_construction"
    PARALLEL_ACTION = "parallel_action"
    DEFINITION = "definition"
    EVIDENTIAL = "evidential"
    COMPARISON = "comparison"
    PRECAUTION = "precaution"
    EMPHATIC_EVEN = "emphatic_even"
    NECESSITY = "necessity"
```

---

### 7.2. Task R02 — Tạo marker map

```yaml
condition:
  - 如果
  - 若
  - 只要
  - 一旦
  - 除非

concession:
  - 虽然
  - 即便
  - 哪怕
  - 就算
  - 尽管

viewpoint:
  - 作为
  - 从X角度来看
  - 就X而言
  - 对X来说

parallel_action:
  - 一边
  - 一面
  - 边X边Y

definition:
  - 所谓
  - 也就是说
  - 换言之

evidential:
  - 据说
  - 据X称
  - 据X说

precaution:
  - 以防
  - 以防万一
  - 以备不时之需
```

---

## 8. Giai đoạn 7 — Rule Registry và Conflict Resolver

### 8.1. Task G01 — Tạo `RuleClaim`

```python
@dataclass
class RuleClaim:
    rule_id: str
    relation_type: RelationType
    source_span: tuple[int, int]
    priority: int
    confidence: float
    replacement_plan: dict
    protected: bool
    trace: TraceEvent
```

---

### 8.2. Task G02 — Tạo priority map

```yaml
priority:
  protected_span_guard: 100
  entity_guard: 95
  number_guard: 90
  quote_guard: 90
  system_ui_guard: 90
  idiom_literal_forbidden: 85

  viewpoint_frame: 80
  condition_frame: 78
  concession_frame: 78
  passive_frame: 76
  ba_construction: 76
  parallel_action: 74
  evidential_frame: 72
  definition_frame: 72

  modifier_de: 60
  possession_de: 60
  classifier: 55
  result_complement: 55
  direction_complement: 55

  vi_surface_cleanup: 20
  punctuation_cleanup: 10
```

---

### 8.3. Task G03 — Implement conflict resolver

```python
class ConflictResolver:
    def resolve(self, claims: list[RuleClaim]) -> list[RuleClaim]:
        claims = sorted(claims, key=lambda c: (-c.priority, -c.confidence))
        accepted = []
        occupied = SpanSet()

        for claim in claims:
            if claim.protected:
                accepted.append(claim)
                occupied.add(claim.source_span)
                continue

            if not occupied.overlaps(claim.source_span):
                accepted.append(claim)
                occupied.add(claim.source_span)
            else:
                self.trace_rejection(claim, reason="span_conflict")

        return accepted
```

---

## 9. Giai đoạn 8 — Grammar rules P0/P1

### 9.1. Nhóm rule P0 bắt buộc

```text
G-P0-01: 作为X而言 / 作为X来讲
G-P0-02: 只要X就Y
G-P0-03: 一旦X就/便Y
G-P0-04: 除非X否则Y
G-P0-05: 哪怕X也Y
G-P0-06: 就算X也Y
G-P0-07: 虽然X但是Y
G-P0-08: 把 construction
G-P0-09: 被 construction
G-P0-10: 为X所V / 被X所V classical passive
G-P0-11: 一边X一边Y
G-P0-12: 所谓X
G-P0-13: X罢了 / X而已
G-P0-14: 据说 / 据X称
G-P0-15: 就连X也Y
```

---

### 9.2. Nhóm rule P1

```text
G-P1-01: 在X的情况下
G-P1-02: 其中 / 其余 / 其他 reference
G-P1-03: 此后X年 / 自此之后
G-P1-04: 恰好 / 刚好 / 正好 coincidence
G-P1-05: 说不定 / 也许 / 或许 probability hedging
G-P1-06: 一来...二来... enumeration
G-P1-07: 无论如何 / 不管怎样 regardless
G-P1-08: 非X不可 / 非X莫属 necessity
G-P1-09: 鉴于X / 有鉴于此 formal reasoning
G-P1-10: 并非 / 不是真正意义上的 semantic negation
```

---

### 9.3. Template rule mẫu

```python
class RuleJiuSuan:
    rule_id = "concession_jiusuan_ye"
    priority = 78

    pattern = re.compile(r"就算(?P<cond>.+?)(?:，)?也(?P<result>.+)")

    def claim(self, clause):
        if m := self.pattern.search(clause.text):
            return RuleClaim(
                rule_id=self.rule_id,
                relation_type=RelationType.CONCESSION,
                source_span=m.span(),
                priority=self.priority,
                confidence=0.92,
                replacement_plan={
                    "template": "dù cho {cond}, {result} cũng/vẫn {result}",
                    "slots": {
                        "cond": m.group("cond"),
                        "result": m.group("result"),
                    }
                },
                protected=False,
                trace=...
            )
```

---

## 10. Giai đoạn 9 — Idiom/Chengyu policy

### 10.1. Task I01 — Tạo idiom policy

```python
class IdiomPolicy(Enum):
    LITERAL_FORBIDDEN = "literal_forbidden"
    HAN_VIET_OK = "han_viet_ok"
    SEMANTIC_REQUIRED = "semantic_required"
    ALLUSION_WITH_GLOSS = "allusion_with_gloss"
```

---

### 10.2. Task I02 — Tạo `idiom_lexicon.tsv`

```text
source	vi_target	policy	register	note
一边...一边...	vừa...vừa...	SEMANTIC_REQUIRED	all	parallel action
为众人所知	được mọi người biết đến	SEMANTIC_REQUIRED	all	classical passive
九死一生	thập tử nhất sinh	HAN_VIET_OK	xianxia	idiom
画蛇添足	vẽ rắn thêm chân	ALLUSION_WITH_GLOSS	formal	allusion
```

---

### 10.3. Task I03 — Tích hợp idiom guard

```text
- Idiom matched span được claim vào ProtectedSpanRegistry.
- Nếu policy = LITERAL_FORBIDDEN, cấm lexical word-by-word decode.
- Nếu policy = SEMANTIC_REQUIRED, bắt buộc dùng target semantic template.
- Nếu policy = HAN_VIET_OK, cho phép Hán-Việt nếu register phù hợp.
```

---

## 11. Giai đoạn 10 — EntityPipeline 7-pass

### 11.1. Task E01 — Entity ontology

```python
class EntityType(Enum):
    PERSON = "person"
    LOCATION = "location"
    SECT_OR_ORG = "sect_or_org"
    DYNASTY_OR_COUNTRY = "dynasty_or_country"
    FACTION = "faction"
    RACE = "race"
    PLANET = "planet"
    ARTIFACT = "artifact"
    WEAPON = "weapon"
    SKILL = "skill"
    CULTIVATION_REALM = "cultivation_realm"
    TITLE = "title"
    SYSTEM_PANEL = "system_panel"
    TECH_PRODUCT = "tech_product"
    SHIP = "ship"
    FRANCHISE_ENTITY = "franchise_entity"
```

---

### 11.2. Task E02 — Exact lexicon pass

```text
- Dùng TrieEngine hiện có.
- Dùng runtime dictionary.
- Match longest phrase first.
- Nếu glossary locked → tạo ProtectedSpan HARD_LOCK.
```

---

### 11.3. Task E03 — Pattern NER pass

```yaml
person_title_suffix:
  - 仙师
  - 道友
  - 师兄
  - 师姐
  - 长老
  - 捕头
  - 王
  - 尊
  - 帝

location_suffix:
  - 城
  - 镇
  - 山
  - 谷
  - 宗
  - 派
  - 王朝
  - 大陆
  - 星
  - 星域

artifact_suffix:
  - 剑
  - 刀
  - 幡
  - 炉
  - 印
  - 珠
  - 冠冕号
  - 基因链
  - 殖装
```

---

### 11.4. Task E04 — Repeated subject confirmation

```python
def repeated_subject_pass(candidates, chapter_memory):
    for cand in candidates:
        cand.evidence_count += count_occurrences(cand.source)
        if appears_as_subject(cand):
            cand.score += 0.15
        if appears_near_speech_verb(cand):
            cand.score += 0.10
        if appears_in_title(cand):
            cand.score += 0.20
```

---

### 11.5. Task E05 — TransliterationDecisionTree

```python
class TransliterationDecisionTree:
    def resolve(self, source, entity_type, register):
        if glossary.has_locked(source):
            return glossary.get(source)

        if entity_type in {PERSON, LOCATION} and looks_foreign_name(source):
            return phoneme_rebuild(source)

        if entity_type in {PERSON, SECT_OR_ORG, ARTIFACT, SKILL, TITLE}:
            return han_viet(source)

        if entity_type == TECH_PRODUCT:
            return mixed_semantic_translit(source)

        return han_viet(source)
```

---

### 11.6. Task E06 — AliasGraph

```sql
CREATE TABLE entities (
  id INTEGER PRIMARY KEY,
  canonical_source TEXT,
  canonical_target TEXT,
  entity_type TEXT,
  register_policy TEXT,
  first_seen_chapter TEXT,
  last_seen_chapter TEXT,
  confidence REAL,
  status TEXT,
  provenance TEXT
);

CREATE TABLE entity_aliases (
  id INTEGER PRIMARY KEY,
  entity_id INTEGER,
  alias_source TEXT,
  alias_target TEXT,
  alias_type TEXT,
  confidence REAL,
  first_seen_chapter TEXT,
  evidence_count INTEGER
);

CREATE TABLE entity_occurrences (
  id INTEGER PRIMARY KEY,
  entity_id INTEGER,
  chapter_id TEXT,
  segment_id TEXT,
  source_span TEXT,
  context_before TEXT,
  context_after TEXT,
  role TEXT,
  confidence REAL
);
```

---

### 11.7. Task E07 — Entity promotion gate

```python
def can_auto_promote_entity(candidate):
    return (
        candidate.confidence >= 0.92
        and candidate.evidence_count >= 3
        and not candidate.blacklisted
        and candidate.has_valid_context
    )
```

---

## 12. Giai đoạn 11 — ContextResolver

### 12.1. Task X01 — EntitySalienceMemory

```python
@dataclass
class EntitySalience:
    entity_id: str
    last_seen_segment: str
    last_role: str
    salience_score: float
    gender: str | None
    number: str | None
    register: str | None
```

---

### 12.2. Task X02 — SpeakerTracker

```text
- Nhận diện X说 / X道 / X喊 / X问.
- Gán speaker cho DIALOGUE.
- Nếu dialogue liên tiếp, suy luận speaker luân phiên khi có 2 nhân vật nổi bật.
- Nếu thiếu speaker, đánh REVIEW thay vì đoán quá tự tin.
```

---

### 12.3. Task X03 — ZeroPronounDetector

```python
SINGLE_AGENT_VERBS = {
    "站", "坐", "走", "跑", "看", "想", "说", "叫", "拿",
    "转身", "回头", "低头", "抬头", "皱眉", "点头", "摇头",
}

REQUIRES_EXPLICIT_SUBJECT_VI = {
    "说", "道", "喊", "叫",
    "笑", "哭", "叹息",
    "转身", "回头",
}
```

#### Logic

```python
def detect_zp_slots(zh_sentence, entity_memory, segment_type):
    if segment_type not in {NARRATION, THOUGHT}:
        return []

    if starts_with_verb_or_adv(zh_sentence):
        salient = entity_memory.get_most_salient(top_k=3)
        if salient:
            return [ZeroPronounSlot(position=0, candidates=salient)]

    return []
```

---

### 12.4. Task X04 — VietnamesePronounSelector

```python
PRONOUN_MATRIX = {
    ("MALE", "xianxia", "neutral"): "hắn",
    ("MALE", "modern", "neutral"): "anh ta",
    ("FEMALE", "xianxia", "neutral"): "nàng",
    ("FEMALE", "modern", "neutral"): "cô ấy",
    ("ELDER", "xianxia", "respect"): "lão",
    ("MASTER", "xianxia", "disciple_relation"): "sư phụ",
}
```

---

## 13. Giai đoạn 12 — Register-aware lexical decode

### 13.1. Task L01 — Register detection

```python
class Register(Enum):
    XIANXIA = "xianxia"
    WUXIA = "wuxia"
    MODERN = "modern"
    SCIFI = "scifi"
    GAME_SYSTEM = "game_system"
    FORMAL = "formal"
    COMEDY = "comedy"
```

---

### 13.2. Task L02 — Lexical policy

```yaml
他:
  xianxia: "hắn"
  modern: "anh ta"
  comedy: "hắn"
  formal: "ông ấy"

她:
  xianxia: "nàng"
  modern: "cô ấy"

老者:
  xianxia: "lão giả"
  modern: "ông lão"

系统:
  game_system: "hệ thống"
  scifi: "hệ thống"
```

---

## 14. Giai đoạn 13 — Metadata DB và Learning Loop

### 14.1. Task M01 — Human review table

```sql
CREATE TABLE human_reviews (
  id INTEGER PRIMARY KEY,
  source_text TEXT,
  machine_target TEXT,
  edited_target TEXT,
  diff_json TEXT,
  error_tags TEXT,
  reviewer TEXT,
  created_at TEXT,
  status TEXT
);
```

---

### 14.2. Task M02 — Error classifier

```python
class ErrorTag(Enum):
    ENTITY_ERROR = "entity_error"
    ALIAS_ERROR = "alias_error"
    GRAMMAR_ERROR = "grammar_error"
    CONTEXT_ERROR = "context_error"
    PRONOUN_ERROR = "pronoun_error"
    NOISE_FALSE_KEEP = "noise_false_keep"
    NOISE_FALSE_DROP = "noise_false_drop"
    REGISTER_ERROR = "register_error"
    NUMBER_ERROR = "number_error"
    IDIOM_ERROR = "idiom_error"
```

---

### 14.3. Task M03 — Candidate miner

```text
Nếu sửa tên riêng lặp lại → entity candidate.
Nếu sửa alias → alias edge candidate.
Nếu sửa cùng một grammar frame nhiều lần → grammar rule candidate.
Nếu xóa một cụm rác nhiều lần → noise pattern candidate.
Nếu sửa câu hoàn chỉnh và được approve → tm_approved candidate.
```

---

### 14.4. Task M04 — PromotionGate

```python
def can_promote(candidate):
    return (
        candidate.evidence_count >= 3
        and candidate.precision_estimate >= 0.95
        and candidate.false_positive_rate <= 0.02
        and candidate.review_status == "approved"
        and regression_suite_passed(candidate)
    )
```

---

## 15. Giai đoạn 14 — RegressionGate, CI/CD và metrics

### 15.1. Task Q01 — RegressionGate

```python
@dataclass
class RegressionThresholds:
    segment_macro_f1: float = 0.93
    grammar_p0_pass_rate: float = 0.92
    entity_span_f1: float = 0.88
    entity_canonical_accuracy: float = 0.90
    transliteration_top1: float = 0.95
    alias_chain_accuracy: float = 0.88
    pronoun_consistency: float = 0.85
    zero_pronoun_false_insert: float = 0.08
    noise_drop_precision: float = 0.95
    noise_false_drop_rate: float = 0.02
    residual_hanzi: int = 0
    tm_machine_into_approved: int = 0
```

---

### 15.2. Task Q02 — Test suite bắt buộc

```text
tests/test_segment_typing/
tests/test_protected_spans/
tests/test_noise_filter/
tests/test_clause_segmenter/
tests/test_relation_detector/
tests/test_grammar_rules/
tests/test_entity_pipeline/
tests/test_alias_graph/
tests/test_transliteration/
tests/test_context_resolver/
tests/test_tm_governance/
tests/test_learning_loop/
tests/test_full_chapter_regression/
```

---

### 15.3. Task Q03 — GitHub Actions

```yaml
name: converter-drduc-regression

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -e ".[dev]"
      - run: python -m pytest
      - run: python scripts/run_regression_gate.py
```

---

## 16. Roadmap triển khai theo sprint

### Sprint 0 — Baseline audit

**Thời lượng:** 3–5 ngày.

```text
S0-01. Clone repo sạch.
S0-02. Chạy toàn bộ tests.
S0-03. Ghi lại failing tests nếu có.
S0-04. Đồng bộ README/tracker/test count.
S0-05. Lập docs/ARCHITECTURE_STATUS.md.
S0-06. Xác định exact production entrypoint.
```

**Deliverable**

```text
- Báo cáo baseline.
- Danh sách module implemented/partial/missing.
- Test count chính xác.
```

---

### Sprint 1 — TM split + trace schema

**Thời lượng:** 1–2 tuần.

```text
S1-01. Tạo migrations 001_tm_split.sql.
S1-02. Tạo tm_machine.
S1-03. Tạo tm_reviewed.
S1-04. Tạo tm_approved.
S1-05. Sửa TranslationMemory lookup order.
S1-06. Sửa RBMTTranslator để không save machine output vào approved.
S1-07. Tạo promote_to_approved().
S1-08. Tạo TraceEvent.
S1-09. Gắn trace vào translator.
S1-10. Viết test tm governance.
```

---

### Sprint 2 — SegmentPacket + SegmentClassifier

**Thời lượng:** 2 tuần.

```text
S2-01. Tạo SegmentType.
S2-02. Tạo SegmentPacket.
S2-03. Implement hard patterns.
S2-04. Implement positional heuristics.
S2-05. Implement dialogue detection.
S2-06. Implement thought detection.
S2-07. Implement author/ad/forum detection.
S2-08. Tích hợp vào pretranslation_pipeline.
S2-09. Tạo segments_gold.jsonl seed.
S2-10. Viết test segment typing.
```

---

### Sprint 3 — Protected spans + Noise filter

**Thời lượng:** 2 tuần.

```text
S3-01. Tạo ProtectedSpan.
S3-02. Tạo ProtectedSpanRegistry.
S3-03. Tích hợp entity claim span.
S3-04. Tích hợp number claim span.
S3-05. Tích hợp system UI claim span.
S3-06. Implement hard whitelist.
S3-07. Implement weighted noise score.
S3-08. Implement KEEP/DROP/REVIEW/METADATA.
S3-09. Viết false-drop prevention tests.
S3-10. Tạo data/noise/*.yml.
```

---

### Sprint 4 — ClauseSegmenter + RelationDetector

**Thời lượng:** 3 tuần.

```text
S4-01. Tạo ClauseBoundary.
S4-02. Implement boundary detection.
S4-03. Không tách trong protected span.
S4-04. Không tách trong quote.
S4-05. Detect conditional markers.
S4-06. Detect concessive markers.
S4-07. Detect cause/result markers.
S4-08. Tạo RelationType.
S4-09. Tạo relation_templates.yml.
S4-10. Viết test cho 100 câu clause/relation.
```

---

### Sprint 5 — RuleRegistry + Grammar P0

**Thời lượng:** 3 tuần.

```text
S5-01. Tạo RuleClaim.
S5-02. Tạo GrammarRule base class.
S5-03. Tạo RuleRegistry.
S5-04. Tạo ConflictResolver.
S5-05. Implement rule 作为X而言.
S5-06. Implement rule 只要X就Y.
S5-07. Implement rule 一旦X就Y.
S5-08. Implement rule 除非X否则Y.
S5-09. Implement rule 哪怕X也Y.
S5-10. Implement rule 就算X也Y.
S5-11. Implement rule 虽然X但是Y.
S5-12. Implement rule 被/为...所 passive.
S5-13. Implement rule 一边X一边Y.
S5-14. Implement rule 所谓X.
S5-15. Implement rule X罢了/X而已.
S5-16. Implement rule 据说/据X称.
S5-17. Implement rule 就连X也Y.
S5-18. Viết grammar_patterns_gold.yaml.
S5-19. Viết test positive/negative cho từng rule.
```

---

### Sprint 6 — EntityPipeline 7-pass

**Thời lượng:** 3 tuần.

```text
S6-01. Tạo EntityType.
S6-02. Tạo EntityCandidate.
S6-03. Tạo ExactLexiconPass.
S6-04. Tạo PatternNERPass.
S6-05. Tạo RepeatedSubjectPass.
S6-06. Tạo EntityRanker.
S6-07. Tạo TransliterationDecisionTree.
S6-08. Tạo AliasGraph.
S6-09. Tạo migrations entities/aliases/occurrences.
S6-10. Tạo ReviewExporter.
S6-11. Tạo entity_seed_glossary.csv.
S6-12. Viết test entity span.
S6-13. Viết test canonical name.
S6-14. Viết test alias chain.
```

---

### Sprint 7 — ContextResolver

**Thời lượng:** 2–3 tuần.

```text
S7-01. Tạo EntitySalienceMemory.
S7-02. Tạo SpeakerTracker.
S7-03. Tạo MentionExtractor.
S7-04. Tạo ZeroPronounDetector.
S7-05. Tạo VietnamesePronounSelector.
S7-06. Tạo RegisterPolicy.
S7-07. Tích hợp vào RBMTTranslator sau surface realization.
S7-08. Tạo coref_miniset.jsonl.
S7-09. Viết test zero pronoun.
S7-10. Viết test pronoun consistency.
S7-11. Viết test speaker attribution.
```

---

### Sprint 8 — LearningLoop + PromotionGate

**Thời lượng:** 2 tuần.

```text
S8-01. Tạo human_reviews table.
S8-02. Tạo review_diff.py.
S8-03. Tạo ErrorClassifier.
S8-04. Tạo CandidateMiner.
S8-05. Tạo RuleCandidate table.
S8-06. Tạo NoisePattern candidate table.
S8-07. Tạo EntityPromotion candidate.
S8-08. Tạo PromotionGate.
S8-09. Tích hợp review UI command.
S8-10. Viết test: không promote nếu chưa review.
S8-11. Viết test: không promote nếu regression fail.
```

---

### Sprint 9 — Regression + CI + performance

**Thời lượng:** 1–2 tuần.

```text
S9-01. Tạo RegressionGate.
S9-02. Tạo evaluation_runs table.
S9-03. Tạo scripts/run_regression_gate.py.
S9-04. Tạo scripts/benchmark_chapter.py.
S9-05. Tạo performance reporter.
S9-06. Tạo GitHub Actions.
S9-07. Tạo docs/REGRESSION_POLICY.md.
S9-08. Tạo docs/PROMOTION_POLICY.md.
```

---

## 17. Danh sách task ưu tiên tuyệt đối

```text
P0-01. Đồng bộ README/tracker/test count.
P0-02. Tách tm_machine / tm_approved.
P0-03. Chặn machine output vào approved TM.
P0-04. Tạo TraceEvent.
P0-05. Tạo SegmentPacket.
P0-06. Implement SegmentClassifier.
P0-07. Implement ProtectedSpanRegistry.
P0-08. Implement NoiseFilter hard whitelist.
P0-09. Viết false-drop tests.
P0-10. Tạo ClauseSegmenter.
P0-11. Tạo RelationDetector.
P0-12. Tạo RuleClaim / RuleRegistry / ConflictResolver.
P0-13. Implement grammar P0.
P0-14. Implement EntityPipeline 7-pass.
P0-15. Implement AliasGraph.
P0-16. Implement ZeroPronounDetector.
P0-17. Implement LearningLoop + PromotionGate.
P0-18. Implement RegressionGate.
```

---

## 18. Definition of Done toàn repo

Repo được xem là hoàn thiện mức production v23 khi đạt:

```text
1. Machine output không bao giờ vào approved TM.
2. Mọi segment đi qua SegmentPacket.
3. Segment typing macro-F1 ≥ 0.93.
4. Noise false-drop ≤ 0.02.
5. Grammar P0 pass rate ≥ 0.92.
6. Entity span F1 ≥ 0.88.
7. Entity canonical accuracy ≥ 0.90.
8. Transliteration known-name accuracy ≥ 0.95.
9. Alias-chain accuracy ≥ 0.88.
10. Pronoun consistency ≥ 0.85.
11. Zero-pronoun false insertion ≤ 0.08.
12. Residual Hanzi trong output cuối = 0, trừ protected intentional span.
13. Mọi rule/entity/noise pattern mới có trace + evidence.
14. Promotion chỉ xảy ra sau human review + regression pass.
15. CI chạy test + regression gate trước merge.
```

---

## 19. Milestone version đề xuất

```text
converter-drduc-v23-core-hardening
```

```text
v23.0 — Core Governance + Segment/Noise Safety
v23.1 — Grammar Transfer Planner
v23.2 — Entity Normalization + Alias Graph
v23.3 — Context Resolver + Zero Pronoun
v23.4 — Learning Loop + Regression Gate
v24.0 — Production Release Candidate
```

---

## 20. Kết luận triển khai

Hướng hoàn thiện đúng nhất:

```text
Giữ backbone hiện tại
→ khóa TM an toàn
→ chuẩn hóa SegmentPacket
→ bảo vệ protected spans
→ lọc noise bằng whitelist tuyệt đối
→ thêm ClauseSegmenter + RelationDetector
→ thêm Grammar Rule Priority
→ nâng EntityScanner thành EntityGraph
→ thêm ContextResolver
→ thêm LearningLoop có PromotionGate
→ khóa CI/regression/metrics.
```

Đây là con đường ngắn nhất để `converter-drduc` đi từ một RBMT engine nhiều module sang một hệ thống dịch truyện Trung→Việt có thể vận hành dài hạn, đo được chất lượng, tránh học sai và tự hoàn thiện an toàn.
