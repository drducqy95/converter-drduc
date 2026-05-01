# CONVERTER-DRDUC — MASTER IMPLEMENTATION PLAN V3 COMPLETE

**Repo:** `drducqy95/converter-drduc`  
**Ngày:** 2026-05-01  
**Phiên bản:** V3 Master Plan  
**Phạm vi:** Hoàn thiện toàn bộ repo theo hướng production-grade, deterministic / non-LLM, có trace, metadata DB, learning loop và regression gate.

> Ghi chú kiểm tra repo: trong phiên này không clone/live-fetch được GitHub do lỗi mạng/DNS. Bản plan này dựa trên:  
> 1. `IMPLEMENTATION_PLAN_V2_COMPLETE.md` do người dùng upload.  
> 2. Các báo cáo nghiên cứu trước về repo `converter-drduc`.  
> 3. Các plan grammar/entity/context/noise/learning đã tổng hợp trước đó.  
> 4. Trạng thái repo đã ghi nhận trước: backbone Python đã có `TrieEngine`, `LuatNhanEngine`, `RBMTTranslator`, `EntityScanner`, `ContextManager`, `QA`, `state/TM`, UI sidecar và desktop shell; nhưng chưa khóa production governance.

---

# 0. TÓM TẮT ĐIỀU HÀNH

Bản V2 hiện tại tập trung rất sâu vào:

```text
Cross-Universe Term Bank
UniverseDetector
Context-Aware Entity Resolution
Entity Enrichment + User Review
EAPEE Integration
```

Đó là một nhánh đúng và cần giữ lại. Tuy nhiên, để hoàn thiện repo toàn diện, V2 cần được đặt trong một master roadmap lớn hơn, bao gồm:

```text
1. Baseline audit và repo housekeeping.
2. Core governance: SegmentPacket, TraceEvent, TM split.
3. Segment typing, protected span, noise filter.
4. Non-LLM grammar pattern scanner.
5. Unknown grammar pattern miner.
6. Grammar transfer planner.
7. Cross-universe term bank.
8. Universe detection.
9. Context-aware entity resolution.
10. Entity enrichment + review workflow.
11. Context resolver + zero-pronoun.
12. Metadata DB + learning loop.
13. Regression gate + CI + performance benchmark.
14. E2E release candidate.
```

---

# 1. NGUYÊN TẮC KIẾN TRÚC BẮT BUỘC

```text
A1. Không viết lại repo từ đầu.
A2. Giữ deterministic-first / non-LLM core.
A3. Python production path là authoritative; JS/TS chỉ là UI/prototype nếu có.
A4. TermBank lookup chạy trước Trie, theo kiểu sequential prepend, không parallel.
A5. Machine output không được đi thẳng vào approved TM.
A6. Mọi segment đi qua SegmentPacket.
A7. Mọi decision phải có trace.
A8. Protected spans thắng mọi rewrite.
A9. Noise filter dùng hard whitelist trước, scoring sau.
A10. Unknown grammar chỉ tạo candidate cần review, không tự promote.
A11. Ambiguous entity không inject tag vào bản dịch; chỉ QA flag + user review.
A12. Learning loop phải có human review + regression gate.
A13. Không promote entity/rule/noise/TM nếu test fail.
A14. Mỗi phase phải chạy full regression.
```

---

# 2. PIPELINE PRODUCTION MỤC TIÊU

```text
Input TXT / Markdown / Project Corpus
  ↓
DocumentImporter
  ↓
ChapterSplitter
  ↓
TextNormalizer
  ↓
SegmentClassifier
  ↓
SegmentPacket
  ↓
ProtectedSpanRegistry
  ↓
NoisePreFilter
  ↓
UniverseDetector
  ↓
TermBank + Trie Sequential Lookup
  ↓
EntityPipeline 7-pass
  ↓
AliasGraph + EntityMemory
  ↓
Non-LLM GrammarPatternScanner
  ↓
UnknownGrammarPatternMiner
  ↓
ClauseSegmenter
  ↓
RelationDetector
  ↓
GrammarRuleRegistry
  ↓
ConflictResolver
  ↓
TransferPlanner
  ↓
LexicalDecoder / LuatNhan / NumberConverter
  ↓
VietnameseSurfaceRealizer
  ↓
ContextResolver / SpeakerTracker / ZeroPronounDetector
  ↓
EAPEE Pronoun + Emotion + Expression
  ↓
NoisePostFilter
  ↓
QA Engine
  ↓
Review UI / Sidecar Commands
  ↓
Metadata DB
  ↓
LearningLoop + PromotionGate
  ↓
TM Approved / Entity Approved / Rule Approved
```

---

# 3. CẤU TRÚC THƯ MỤC ĐÍCH

```text
src/
  core/
    trace.py
    trie_engine.py
    luat_nhan_engine.py
    runtime_support.py

  pipeline/
    packet.py
    text_normalizer.py
    document_importer.py
    chapter_splitter.py
    segment_classifier.py
    protected_span_registry.py
    noise_filter.py
    pretranslation_pipeline.py
    term_bank.py
    universe_detector.py
    entity_scanner.py
    entity_enrichment.py
    relationship_builder.py
    terminology_suggester.py

  analysis/
    __init__.py
    txt_corpus_reader.py
    grammar_pattern_registry.py
    grammar_pattern_scanner.py
    unknown_pattern_miner.py
    grammar_stats.py
    grammar_reporter.py
    backlog_generator.py

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
      rule_reference.py
      rule_formal_reasoning.py
      rule_emphatic_even.py

  entities/
    entity_types.py
    alias_graph.py
    entity_memory.py
    transliteration_engine.py
    entity_ranker.py
    entity_promoter.py

  context/
    speaker_tracker.py
    mention_memory.py
    entity_salience.py
    zero_pronoun_detector.py
    vi_pronoun_selector.py
    register_policy.py

  learning/
    review_diff.py
    error_classifier.py
    candidate_miner.py
    promotion_gate.py
    regression_runner.py
    evaluation_reporter.py

  state/
    metadata_db.py
    translation_memory.py
    project_state.py
    migrations/
      001_tm_split.sql
      002_entities.sql
      003_alias_graph.sql
      004_learning_loop.sql
      005_evaluation_runs.sql
      006_term_bank_versioning.sql

data/
  grammar/
    grammar_patterns.yml
    unknown_marker_seed.yml
    relation_templates.yml
    grammar_rule_priority.yml
    idiom_lexicon.tsv
    discourse_markers.yml
    register_policy.yml

  noise/
    hard_keep_patterns.yml
    soft_keep_patterns.yml
    stop_phrase_patterns.yml
    author_note_patterns.yml
    forum_patterns.yml
    advertisement_patterns.yml

  term_bank/
    global/
      proper_names.jsonl
      shared_cultivation.jsonl
      shared_titles.jsonl
      real_world.jsonl
    universes/
      fingerprints.json
      tu_tien/
      dau_khi/
      dau_la/
      than_dong/
      kiem_lai/
      quy_bi/
      oc_fanfic/

  tests_gold/
    segments_gold.jsonl
    grammar_patterns_gold.yaml
    entity_gold.jsonl
    coref_miniset.jsonl
    noise_gold.jsonl
    full_chapter_regression/

scripts/
  scan_grammar_patterns.py
  md_to_jsonl_converter.py
  validate_jsonl.py
  backfill_proper_names.py
  run_regression_gate.py
  benchmark_chapter.py

tests/
  test_core/
  test_pipeline/
  test_analysis/
  test_grammar/
  test_entities/
  test_context/
  test_learning/
  test_ui/
  test_e2e/
```

---

# 4. PHASE 0 — BASELINE AUDIT & REPO HOUSEKEEPING

**Ưu tiên:** P0  
**Thời lượng:** 3–5 ngày  
**Dependency:** Không có

## Mục tiêu

Xác nhận trạng thái thật của repo sau update, đồng bộ tài liệu, làm sạch root và thiết lập trạng thái nền trước khi thêm code mới.

## Tasks

### P0-T1 — Clone và verify repo

```bash
git clone https://github.com/drducqy95/converter-drduc
cd converter-drduc
python -m pytest --tb=short
```

Ghi lại:

```text
- Python version
- OS
- số tests passed
- số tests failed
- warnings
- runtime
```

### P0-T2 — Đồng bộ README / tracker / Plan

```text
- Kiểm tra README.md.
- Kiểm tra Plan.md.
- Kiểm tra project_progress.json nếu có.
- Đồng bộ số test thật.
- Tạo docs/ARCHITECTURE_STATUS.md.
```

### P0-T3 — Dọn root directory

```bash
mkdir -p scripts/debug scripts/run
git mv debug_*.py scripts/debug/ 2>/dev/null || true
git mv run_*.py scripts/run/ 2>/dev/null || true
git mv patch_*.py scripts/debug/ 2>/dev/null || true
```

### P0-T4 — Fix pyproject/dependencies

```toml
[project]
dependencies = [
    "pytest>=7.4",
    "python-rapidjson>=1.10",
    "PyYAML>=6.0",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

## Definition of Done

```text
[ ] Repo cài được bằng pip install -e .
[ ] pytest chạy được.
[ ] README không lệch test count.
[ ] Root directory sạch.
[ ] docs/ARCHITECTURE_STATUS.md tồn tại.
```

---

# 5. PHASE 1 — CORE GOVERNANCE: SegmentPacket, TraceEvent, TM Split

**Ưu tiên:** P0  
**Thời lượng:** 1–2 tuần  
**Dependency:** Phase 0

## Mục tiêu

Khóa governance nền trước khi thêm entity/grammar/learning. Đây là phase quan trọng nhất để tránh hệ thống tự học sai.

## Tasks

### P1-T1 — Tạo TraceEvent

File:

```text
src/core/trace.py
```

Code khung:

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

### P1-T2 — Tạo SegmentPacket

File:

```text
src/pipeline/packet.py
```

Code khung:

```python
@dataclass
class SegmentPacket:
    segment_id: str
    chapter_id: str
    position: int
    raw_text: str
    normalized_text: str
    seg_type: str
    confidence: float
    protected_spans: list
    metadata: dict
    trace: list[TraceEvent]
```

### P1-T3 — Tách Translation Memory

Migration:

```text
src/state/migrations/001_tm_split.sql
```

Schema:

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
```

### P1-T4 — Sửa TranslationMemory lookup order

```text
1. tm_approved exact
2. tm_approved fuzzy
3. tm_machine suggestion only
4. fallback RBMT
```

### P1-T5 — Chặn machine output vào approved TM

Test bắt buộc:

```python
def test_rbmt_output_never_goes_to_approved_tm():
    result = translator.translate("他走了。")
    assert tm_machine.exists("他走了。")
    assert not tm_approved.exists("他走了。")
```

## Definition of Done

```text
[ ] TraceEvent có thể attach vào mọi stage.
[ ] SegmentPacket dùng được trong pipeline.
[ ] TM được tách machine/reviewed/approved.
[ ] Machine output không bao giờ status verified.
[ ] Test tm governance pass.
```

---

# 6. PHASE 2 — SEGMENT TYPING, PROTECTED SPAN, NOISE FILTER

**Ưu tiên:** P0  
**Thời lượng:** 2 tuần  
**Dependency:** Phase 1

## Mục tiêu

Tách đúng loại segment, bảo vệ nội dung thật, lọc rác an toàn.

## Tasks

### P2-T1 — SegmentType

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

### P2-T2 — SegmentClassifier

File:

```text
src/pipeline/segment_classifier.py
```

Pattern nhóm:

```text
- chapter title
- dialogue
- thought
- system panel
- author note
- advertisement
- forum post
```

Test bắt buộc:

```text
【面板未开启】 → SYSTEM_PROMPT
【新书上传，求收藏推荐。】 → AUTHOR_NOTE / ADVERTISEMENT
他激活了【蜘蛛感应】技能。 → NARRATION
李宇冷声道：“你走吧。” → DIALOGUE
```

### P2-T3 — ProtectedSpanRegistry

File:

```text
src/pipeline/protected_span_registry.py
```

Span types:

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

Priority:

```text
100 — system UI / title locked
90  — approved entity
80  — quote span
70  — number/rank/time
60  — idiom literal forbidden
50  — soft entity candidate
```

### P2-T4 — NoiseFilterWithSafeWhitelist

File:

```text
src/pipeline/noise_filter.py
```

Nguyên tắc:

```text
Hard whitelist thắng noise score.
Không drop entity/system/bracket item thật.
Author note / advertisement / PS / cầu phiếu → drop hoặc metadata.
```

Noise patterns:

```text
PS:
作者有话说
本章完
未完待续
求收藏
求推荐
求月票
求订阅
新书上传
打赏
```

Hard keep patterns:

```text
【系统...】
【面板...】
【任务...】
【技能...】
【奖励...】
【实体名】启动完成
获得【实体名】
激活【实体名】
```

## Definition of Done

```text
[ ] Segment typing macro-F1 target ≥ 0.93 trên seed gold.
[ ] Noise false drop ≤ 0.02.
[ ] System panel không bị drop.
[ ] Advertisement / author note bị drop/metadata.
[ ] Full regression pass.
```

---

# 7. PHASE 3 — NON-LLM GRAMMAR PATTERN SCANNER

**Ưu tiên:** P1  
**Thời lượng:** 1–2 tuần  
**Dependency:** Phase 2

## Mục tiêu

Quét file txt nguồn để thống kê dạng ngữ pháp đã biết và phát hiện candidate chưa biết mà không dùng LLM.

## Tasks

### P3-T1 — Tạo analysis package

```text
src/analysis/
  txt_corpus_reader.py
  grammar_pattern_registry.py
  grammar_pattern_scanner.py
  unknown_pattern_miner.py
  grammar_stats.py
  grammar_reporter.py
  backlog_generator.py
```

### P3-T2 — Known GrammarPatternScanner

Config:

```text
data/grammar/grammar_patterns.yml
```

Nhóm rule cần có:

```text
condition: 如果...就, 只要...就, 一旦...就, 除非...否则
concession: 虽然...但是, 即便...也, 哪怕...也, 就算...也
passive: 被, 为...所, 被...所
disposal: 把
viewpoint: 作为, 对X而言
parallel: 一边...一边, 边...边
definition: 所谓, 也就是说, 换言之
minimizing: 罢了, 而已
evidential: 据说, 据X称, 据X说
comparison: 相比之下, 与X相比
precaution: 以防, 以防万一
emphatic: 就连...也, 连...都
enumeration: 一来...二来, 其一...其二
necessity: 非...不可, 非...莫属
```

### P3-T3 — UnknownGrammarPatternMiner

Phát hiện cấu trúc chưa có trong code bằng:

```text
1. marker mining
2. paired-marker mining
3. n-gram mining
4. frame-template mining
5. clause anomaly mining
6. residual-unmatched analysis
```

Candidate output:

```json
{
  "candidate_id": "unknown_xxx",
  "pattern_text": "与其...不如",
  "pattern_type": "paired_marker",
  "frequency": 37,
  "chapter_count": 18,
  "confidence": 0.86,
  "guessed_category": "preference",
  "suggested_regex": "与其(?P<a>.+?)不如(?P<b>.+)",
  "status": "review"
}
```

### P3-T4 — CLI script

```text
scripts/scan_grammar_patterns.py
```

Run:

```bash
python scripts/scan_grammar_patterns.py \
  --input data/corpus/source.txt \
  --patterns data/grammar/grammar_patterns.yml \
  --out-dir reports/grammar_scan/source \
  --unknown-min-count 5
```

### P3-T5 — Export reports

```text
grammar_stats.json
grammar_stats.csv
grammar_report.md
rule_backlog.json
```

## Definition of Done

```text
[ ] Scanner không dùng LLM.
[ ] Known patterns được thống kê.
[ ] Unknown candidates được xuất review.
[ ] Không scan trong protected spans.
[ ] Có JSON/CSV/Markdown report.
```

---

# 8. PHASE 4 — CROSS-UNIVERSE TERM BANK DATA MIGRATION

**Ưu tiên:** P1  
**Thời lượng:** 1 tuần  
**Dependency:** Phase 2

## Mục tiêu

Triển khai Phase 1 của bản V2: chuyển MD entity bank sang JSONL universe-aware.

## Tasks

### P4-T1 — Tạo term_bank structure

```text
data/term_bank/
  global/
    proper_names.jsonl
    shared_cultivation.jsonl
    shared_titles.jsonl
    real_world.jsonl
  universes/
    fingerprints.json
    tu_tien/
    dau_khi/
    dau_la/
    than_dong/
    kiem_lai/
    quy_bi/
    oc_fanfic/
```

### P4-T2 — md_to_jsonl_converter.py

```text
scripts/md_to_jsonl_converter.py
```

Yêu cầu:

```text
- Parse *, -, • bullet.
- Parse 中文 = Hán Việt.
- Parse slash alias.
- Map section header → entity_type.
- Map file path → universe/work.
- Primary key = source|universe.
- Idempotent.
```

### P4-T3 — validate_jsonl.py

Checks:

```text
- valid JSON per line
- required fields
- no duplicate primary keys
- entity_type allowed
- confidence in [0,1]
```

### P4-T4 — backfill proper_names.jsonl

Thêm fields:

```text
universe
scope
confidence
status
version
context_markers
co_occurring_entities
aliases_source
aliases_target
tags
```

## Definition of Done

```text
[ ] JSONL valid.
[ ] No duplicate primary keys.
[ ] proper_names được backfill.
[ ] shared_cultivation/shared_titles/real_world tồn tại.
[ ] Unit tests pass.
```

---

# 9. PHASE 5 — TERM BANK SCHEMA EXPANSION

**Ưu tiên:** P1  
**Thời lượng:** 1 tuần  
**Dependency:** Phase 4

## Mục tiêu

Mở rộng `TermBankRecord` để hỗ trợ universe/context/versioning.

## Tasks

### P5-T1 — TermBankRecord fields

```python
@dataclass(slots=True)
class TermBankRecord:
    source: str
    target: str
    entity_type: str = "term"
    universe: str = ""
    work: str = ""
    scope: str = "global"
    aliases_source: list[str] = field(default_factory=list)
    aliases_target: list[str] = field(default_factory=list)
    context_markers: list[str] = field(default_factory=list)
    co_occurring_entities: list[str] = field(default_factory=list)
    confidence: float = 1.0
    status: str = "active"
    version: int = 1
    notes: str = ""
    tags: list[str] = field(default_factory=list)
```

### P5-T2 — score_against_context

```text
universe match weight = 0.5
context markers weight = 0.3
co-occurrence weight = 0.2
multiply by confidence
```

### P5-T3 — Lazy-load universe data

```text
TermBank._universe_cache
TermBank._load_universe()
TermBank.reload_universe()
TermBank.get_universe_glossary()
```

### P5-T4 — lookup_with_context

Return sorted candidates; caller decides ambiguity.

## Definition of Done

```text
[ ] 5 required fields exist: universe, scope, confidence, status, version.
[ ] lookup_with_context sorted by score.
[ ] deprecated records ignored.
[ ] reload_universe works.
[ ] Tests pass.
```

---

# 10. PHASE 6 — UNIVERSE DETECTOR

**Ưu tiên:** P1  
**Thời lượng:** 1 tuần  
**Dependency:** Phase 5

## Mục tiêu

Triển khai module riêng `UniverseDetector`.

## Tasks

### P6-T1 — fingerprints.json

File:

```text
data/term_bank/universes/fingerprints.json
```

Cấu trúc:

```json
{
  "version": 1,
  "universes": {
    "tu_tien": {
      "fingerprint_terms": [{"term": "灵根", "weight": 1.5}],
      "canonical_chars": ["韩立", "王林"],
      "co_occurrence_seeds": [{"pair": ["韩立", "南宫婉"], "confidence": 0.99}],
      "exclusion_terms": []
    }
  },
  "multi_universe_threshold": 0.65,
  "min_confidence_for_active": 0.4
}
```

### P6-T2 — UniverseDetector

File:

```text
src/pipeline/universe_detector.py
```

Dataclasses:

```python
@dataclass(frozen=True)
class UniverseSignal:
    universe_id: str
    confidence: float
    matched_fingerprints: list[str]
    matched_characters: list[str]

@dataclass
class UniverseContext:
    active_universes: list[str]
    signals: list[UniverseSignal]
    is_multi_universe: bool
    is_unknown: bool
```

Algorithm:

```text
1. Weighted fingerprint scan.
2. Canonical character scan.
3. Co-occurrence scan.
4. Normalize score.
5. Filter by threshold.
6. Return UniverseContext.
```

### P6-T3 — detect_sentence_level

Use sentence ±1 context radius.

### P6-T4 — expand_cooccurrence_from_term_bank

Tự học pair từ `co_occurring_entities`.

## Definition of Done

```text
[ ] detect() accuracy ≥ 90% trên benchmark.
[ ] detect_sentence_level() hoạt động.
[ ] multi_universe threshold 0.65.
[ ] oc_fanfic fallback có.
[ ] Tests pass.
```

---

# 11. PHASE 7 — CONTEXT-AWARE ENTITY RESOLUTION

**Ưu tiên:** P1  
**Thời lượng:** 2 tuần  
**Dependency:** Phase 6

## Mục tiêu

Nâng cấp `EntityScanner` để dùng UniverseContext, TermBank context scoring, mixed-script detection và entity types mới.

## Resolution chain

```text
1. Project-private TermBank
2. Universe-specific TermBank
3. Global TermBank
4. Trie P5 project-specific names
5. Trie P4 global proper names
6. Trie P3 project VietPhrase
7. Trie P2 global VietPhrase
8. Trie P1 PhienAm
9. Heuristic name mining
```

## Tasks

### P7-T1 — Pre-scan universe

```python
universe_ctx = self._universe_detector.detect(text)
sentence_ctxs = self._universe_detector.detect_sentence_level(sentences)
```

### P7-T2 — Resolve entity with context

```python
candidates = self._term_bank.lookup_with_context(
    entity.source,
    context_window=context_window,
    entity_type=entity.entity_type,
    detected_universes=active_universes,
)
```

If score gap < 0.15:

```text
entity.ambiguous = True
entity.needs_qa_review = True
entity.ambiguous_candidates = top 3
```

Do not inject `[universe_tag]`.

### P7-T3 — Mixed-script detection

Patterns:

```text
克莱恩·莫雷蒂
Klein
Sequence 9
M829A3
AL2O3
```

### P7-T4 — Expanded entity types

```text
title
creature
faction
term
tech_product
ship
planet
race
artifact
skill
cultivation_realm
```

## Definition of Done

```text
[ ] Same-name disambiguation works.
[ ] Mixed-script entity detected.
[ ] TermBank before Trie.
[ ] Ambiguity becomes QA flag.
[ ] No universe tag appears in translation.
[ ] Tests pass.
```

---

# 12. PHASE 8 — GRAMMAR TRANSFER PLANNER

**Ưu tiên:** P1  
**Thời lượng:** 3 tuần  
**Dependency:** Phase 3 and Phase 7

## Mục tiêu

Nâng grammar transfer từ rewrite chuỗi lên clause/relation/rule-claim planner.

## Tasks

### P8-T1 — ClauseSegmenter

File:

```text
src/grammar/clause_segmenter.py
```

Boundary types:

```text
SENTENCE_END
CLAUSE_SOFT
CLAUSE_HARD
CONDITIONAL
CONCESSIVE
CAUSE
RESULT
TEMPORAL
CONJUNCTION
```

### P8-T2 — RelationDetector

Relations:

```text
CONDITION
CONCESSION
CAUSE_EFFECT
CONTRAST
TEMPORAL
PURPOSE
VIEWPOINT
PASSIVE
DISPOSAL
PARALLEL_ACTION
DEFINITION
EVIDENTIAL
COMPARISON
PRECAUTION
EMPHATIC_EVEN
NECESSITY
```

### P8-T3 — RuleClaim

```python
@dataclass
class RuleClaim:
    rule_id: str
    relation_type: str
    source_span: tuple[int, int]
    priority: int
    confidence: float
    replacement_plan: dict
    protected: bool
    trace: TraceEvent
```

### P8-T4 — RuleRegistry + ConflictResolver

Priority:

```text
100 protected span guard
95  entity guard
90  number/quote/system guard
85  idiom literal forbidden
80  viewpoint
78  condition/concession
76  passive/disposal
74  parallel
72  evidential/definition
60  DE/modifier/possessive
55  classifier/complement/aspect
20  VI surface cleanup
```

### P8-T5 — Grammar P0 rules

```text
作为X而言
只要X就Y
一旦X就Y
除非X否则Y
哪怕X也Y
就算X也Y
虽然X但是Y
把 construction
被 construction
为X所V
被X所V
一边X一边Y
所谓X
X罢了 / X而已
据说 / 据X称
就连X也Y
```

## Definition of Done

```text
[ ] Grammar P0 pass rate ≥ 0.92.
[ ] Rule conflict resolved by priority.
[ ] Protected span not modified.
[ ] Trace available for every rule decision.
[ ] Tests pass.
```

---

# 13. PHASE 9 — ENTITY ENRICHMENT & USER REVIEW

**Ưu tiên:** P1  
**Thời lượng:** 1 tuần  
**Dependency:** Phase 7

## Mục tiêu

Scan entity → enrich metadata → user review → save approved only.

## Tasks

### P9-T1 — EntitySuggestion extended fields

```python
universe: str
work: str
review_status: str
enrichment_ready: bool
suggested_tags: list[str]
suggested_context_markers: list[str]
suggested_co_occurring: list[str]
ambiguous: bool
ambiguous_candidates: list[str]
needs_qa_review: bool
resolution_source: str
sentence_index: int
```

### P9-T2 — EntityEnrichmentManager

File:

```text
src/pipeline/entity_enrichment.py
```

Methods:

```text
prepare_for_review()
approve_entity()
reject_entity()
save_to_term_bank()
export_review_report()
```

### P9-T3 — Atomic write

```text
write temp → validate → append/dedup → rename/unlink → reload universe
```

### P9-T4 — Sidecar commands

```text
entity_scan_review
entity_approve
entity_reject
entity_save_to_term_bank
entity_export_report
```

## Definition of Done

```text
[ ] prepare_for_review auto-fills universe if single active universe.
[ ] save_to_term_bank atomic and deduped.
[ ] hot reload after save.
[ ] sidecar schemas documented.
[ ] tests pass.
```

---

# 14. PHASE 10 — CONTEXT RESOLVER, ZERO-PRONOUN, EAPEE

**Ưu tiên:** P1  
**Thời lượng:** 2 tuần  
**Dependency:** Phase 7 and Phase 9

## Mục tiêu

Ổn định đại từ, người nói, zero-pronoun và liên kết EAPEE với UniverseContext.

## Tasks

### P10-T1 — EntitySalienceMemory

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

### P10-T2 — SpeakerTracker

Detect:

```text
X说
X道
X喊
X问
X冷声道
X心中暗道
```

### P10-T3 — ZeroPronounDetector

Verbs:

```text
站, 坐, 走, 跑, 看, 想, 说, 叫, 拿,
转身, 回头, 低头, 抬头, 皱眉, 点头, 摇头
```

Only insert pronoun when:

```text
- subject omitted
- salient entity exists
- sentence needs subject clarity in VI
- no high ambiguity
```

### P10-T4 — VietnamesePronounSelector

Register matrix:

```text
xianxia male → hắn
xianxia female → nàng
modern male → anh ta
modern female → cô ấy
elder xianxia → lão
master relation → sư phụ
```

### P10-T5 — EAPEE Integration

`PronounResolver.resolve()` accepts:

```python
universe_context: UniverseContext | None = None
```

## Definition of Done

```text
[ ] Speaker attribution accuracy target ≥ 0.90.
[ ] Pronoun consistency target ≥ 0.85.
[ ] Zero-pronoun false insertion ≤ 0.08.
[ ] EAPEE receives UniverseContext.
[ ] Tests pass.
```

---

# 15. PHASE 11 — METADATA DB & LEARNING LOOP

**Ưu tiên:** P0/P1  
**Thời lượng:** 2 tuần  
**Dependency:** Phase 1, 8, 9, 10

## Mục tiêu

Tạo hệ tự học có kiểm duyệt sau mỗi lần dịch.

## Tables

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

CREATE TABLE rule_candidates (
  id INTEGER PRIMARY KEY,
  pattern TEXT,
  proposed_action TEXT,
  evidence_count INTEGER,
  positive_examples TEXT,
  negative_examples TEXT,
  precision_estimate REAL,
  status TEXT
);

CREATE TABLE noise_patterns (
  id INTEGER PRIMARY KEY,
  pattern TEXT,
  category TEXT,
  action TEXT,
  confidence REAL,
  false_drop_count INTEGER,
  status TEXT
);

CREATE TABLE evaluation_runs (
  id INTEGER PRIMARY KEY,
  engine_version TEXT,
  corpus_id TEXT,
  metrics_json TEXT,
  failed_cases_json TEXT,
  created_at TEXT
);
```

## Error tags

```text
ENTITY_ERROR
ALIAS_ERROR
GRAMMAR_ERROR
CONTEXT_ERROR
PRONOUN_ERROR
NOISE_FALSE_KEEP
NOISE_FALSE_DROP
REGISTER_ERROR
NUMBER_ERROR
IDIOM_ERROR
```

## Promotion gate

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

## Definition of Done

```text
[ ] Review diff stored.
[ ] Candidate miner creates rule/entity/noise/TM candidates.
[ ] No auto-promotion without review.
[ ] No promotion when regression fails.
[ ] evaluation_runs saved.
```

---

# 16. PHASE 12 — REGRESSION GATE, CI, PERFORMANCE

**Ưu tiên:** P0  
**Thời lượng:** 1 tuần  
**Dependency:** All functional phases

## Metrics

```python
@dataclass
class RegressionThresholds:
    segment_macro_f1: float = 0.93
    grammar_p0_pass_rate: float = 0.92
    entity_span_f1: float = 0.88
    entity_canonical_accuracy: float = 0.90
    transliteration_top1: float = 0.95
    alias_chain_accuracy: float = 0.88
    universe_detection_accuracy: float = 0.90
    pronoun_consistency: float = 0.85
    zero_pronoun_false_insert: float = 0.08
    noise_drop_precision: float = 0.95
    noise_false_drop_rate: float = 0.02
    residual_hanzi: int = 0
    tm_machine_into_approved: int = 0
```

## Scripts

```text
scripts/run_regression_gate.py
scripts/benchmark_chapter.py
```

## GitHub Actions

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
      - run: pip install -r requirements.txt
      - run: pip install -e .
      - run: python -m pytest
      - run: python scripts/run_regression_gate.py
```

## Definition of Done

```text
[ ] CI runs tests.
[ ] CI runs regression gate.
[ ] Performance benchmark exists.
[ ] Failing metric blocks promotion.
```

---

# 17. PHASE 13 — E2E INTEGRATION & RELEASE CANDIDATE

**Ưu tiên:** P1  
**Thời lượng:** 1–2 tuần  
**Dependency:** Phase 12

## E2E tests

```text
1. Single xianxia chapter.
2. Sci-fi/system panel chapter.
3. Chư Thiên / multi-universe sample.
4. Dialogue-heavy chapter.
5. Author-note/noise-heavy chapter.
6. Mixed-script names chapter.
```

## Release checks

```text
[ ] No [universe_tag] in output.
[ ] No residual Hanzi except protected intentional spans.
[ ] Entity consistency across chapter.
[ ] TM approved clean.
[ ] Grammar P0 pass.
[ ] Noise false drop within threshold.
[ ] Performance acceptable.
```

## Documentation

```text
docs/ARCHITECTURE_STATUS.md
docs/CROSS_UNIVERSE_GUIDE.md
docs/GRAMMAR_PATTERN_SCANNER.md
docs/GRAMMAR_TRANSFER_PLANNER.md
docs/LEARNING_LOOP.md
docs/REGRESSION_POLICY.md
docs/PROMOTION_POLICY.md
```

---

# 18. TIMELINE TỔNG THỂ

| Phase | Tên | Thời lượng | Ưu tiên | Dependency |
|---|---|---:|---|---|
| 0 | Baseline audit & housekeeping | 3–5 ngày | P0 | — |
| 1 | Core governance / TM split | 1–2 tuần | P0 | P0 |
| 2 | Segment / protected / noise | 2 tuần | P0 | P1 |
| 3 | Grammar pattern scanner | 1–2 tuần | P1 | P2 |
| 4 | Term bank data migration | 1 tuần | P1 | P2 |
| 5 | TermBank schema expansion | 1 tuần | P1 | P4 |
| 6 | UniverseDetector | 1 tuần | P1 | P5 |
| 7 | Context-aware entity resolution | 2 tuần | P1 | P6 |
| 8 | Grammar transfer planner | 3 tuần | P1 | P3/P7 |
| 9 | Entity enrichment & review | 1 tuần | P1 | P7 |
| 10 | Context resolver + EAPEE | 2 tuần | P1 | P7/P9 |
| 11 | Metadata DB + learning loop | 2 tuần | P0/P1 | P1/P8/P9/P10 |
| 12 | Regression gate + CI | 1 tuần | P0 | all |
| 13 | E2E release candidate | 1–2 tuần | P1 | P12 |

**Tổng thực tế:** 16–22 tuần nếu triển khai chắc chắn, có test và review.  
**Bản V2 riêng Cross-Universe có thể làm trong ~5 tuần**, nhưng để production toàn repo nên đi theo roadmap V3.

---

# 19. DANH SÁCH FILE CẦN THÊM/SỬA

## 19.1. Files mới

```text
src/core/trace.py
src/pipeline/packet.py
src/pipeline/segment_classifier.py
src/pipeline/protected_span_registry.py
src/pipeline/noise_filter.py
src/pipeline/universe_detector.py
src/pipeline/entity_enrichment.py

src/analysis/txt_corpus_reader.py
src/analysis/grammar_pattern_registry.py
src/analysis/grammar_pattern_scanner.py
src/analysis/unknown_pattern_miner.py
src/analysis/grammar_stats.py
src/analysis/grammar_reporter.py
src/analysis/backlog_generator.py

src/grammar/clause_segmenter.py
src/grammar/relation_detector.py
src/grammar/rule_claim.py
src/grammar/rule_registry.py
src/grammar/conflict_resolver.py
src/grammar/transfer_planner.py
src/grammar/surface_realizer.py
src/grammar/idiom_policy.py

src/entities/entity_types.py
src/entities/alias_graph.py
src/entities/entity_memory.py
src/entities/transliteration_engine.py
src/entities/entity_ranker.py
src/entities/entity_promoter.py

src/context/speaker_tracker.py
src/context/mention_memory.py
src/context/entity_salience.py
src/context/zero_pronoun_detector.py
src/context/vi_pronoun_selector.py
src/context/register_policy.py

src/learning/review_diff.py
src/learning/error_classifier.py
src/learning/candidate_miner.py
src/learning/promotion_gate.py
src/learning/regression_runner.py
src/learning/evaluation_reporter.py
```

## 19.2. Files cần sửa

```text
pyproject.toml
README.md
Plan.md
src/engine/rbmt_translator.py
src/state/translation_memory.py
src/pipeline/pretranslation_pipeline.py
src/pipeline/entity_scanner.py
src/pipeline/term_bank.py
src/eapee/pronoun_resolver.py
src/ui/sidecar_bridge.py
src/qa/*
```

## 19.3. Data files mới

```text
data/grammar/grammar_patterns.yml
data/grammar/unknown_marker_seed.yml
data/grammar/relation_templates.yml
data/grammar/grammar_rule_priority.yml
data/grammar/idiom_lexicon.tsv
data/grammar/register_policy.yml

data/noise/hard_keep_patterns.yml
data/noise/soft_keep_patterns.yml
data/noise/stop_phrase_patterns.yml
data/noise/author_note_patterns.yml
data/noise/forum_patterns.yml
data/noise/advertisement_patterns.yml

data/term_bank/global/shared_cultivation.jsonl
data/term_bank/global/shared_titles.jsonl
data/term_bank/global/real_world.jsonl
data/term_bank/universes/fingerprints.json
```

---

# 20. TEST PLAN

## 20.1. Test groups

```text
tests/test_core/test_trace.py
tests/test_pipeline/test_segment_classifier.py
tests/test_pipeline/test_protected_span_registry.py
tests/test_pipeline/test_noise_filter.py
tests/test_analysis/test_grammar_pattern_scanner.py
tests/test_analysis/test_unknown_pattern_miner.py
tests/test_grammar/test_clause_segmenter.py
tests/test_grammar/test_relation_detector.py
tests/test_grammar/test_rule_registry.py
tests/test_grammar/test_transfer_planner.py
tests/test_entities/test_term_bank_universe.py
tests/test_entities/test_universe_detector.py
tests/test_entities/test_entity_context.py
tests/test_entities/test_entity_enrichment.py
tests/test_context/test_speaker_tracker.py
tests/test_context/test_zero_pronoun_detector.py
tests/test_learning/test_promotion_gate.py
tests/test_e2e/test_cross_universe_translation.py
tests/test_e2e/test_full_chapter_regression.py
```

## 20.2. Required test examples

```python
def test_machine_output_never_goes_to_approved_tm():
    ...

def test_system_panel_hard_keep():
    ...

def test_author_note_drop():
    ...

def test_unknown_grammar_candidate_review_only():
    ...

def test_universe_detection_dau_khi():
    ...

def test_multi_universe_detection():
    ...

def test_ambiguous_entity_gets_qa_flag_not_output_tag():
    ...

def test_protected_span_not_modified_by_grammar_rule:
    ...

def test_zero_pronoun_insert_when_subject_omitted():
    ...

def test_no_promotion_when_regression_fails():
    ...
```

---

# 21. PRIORITY BACKLOG

## P0 — Làm ngay

```text
P0-01. Verify repo sau update.
P0-02. Đồng bộ README/tracker/test count.
P0-03. Fix pyproject.
P0-04. Tạo TraceEvent.
P0-05. Tạo SegmentPacket.
P0-06. Tách tm_machine/tm_reviewed/tm_approved.
P0-07. Chặn RBMT output vào approved TM.
P0-08. SegmentClassifier.
P0-09. ProtectedSpanRegistry.
P0-10. NoiseFilterWithSafeWhitelist.
P0-11. RegressionGate skeleton.
```

## P1 — Core feature

```text
P1-01. GrammarPatternScanner.
P1-02. UnknownGrammarPatternMiner.
P1-03. JSONL TermBank migration.
P1-04. TermBank schema expansion.
P1-05. UniverseDetector.
P1-06. Context-aware EntityScanner.
P1-07. Grammar Transfer Planner.
P1-08. EntityEnrichmentManager.
P1-09. ContextResolver + ZeroPronoun.
P1-10. LearningLoop.
```

## P2 — Optimization

```text
P2-01. Performance benchmark.
P2-02. CI/CD.
P2-03. Annotation workflow.
P2-04. Dashboard/report.
P2-05. More universe packs.
P2-06. More grammar rules.
P2-07. More idiom/chengyu database.
```

---

# 22. DEFINITION OF DONE TOÀN REPO

Repo đạt mức production v24 khi:

```text
[ ] Repo clone/install/test sạch.
[ ] Mọi segment dùng SegmentPacket.
[ ] Mọi stage có trace.
[ ] tm_machine và tm_approved tách biệt.
[ ] Machine output không vào approved TM.
[ ] Segment typing macro-F1 ≥ 0.93.
[ ] Noise drop precision ≥ 0.95.
[ ] Noise false drop ≤ 0.02.
[ ] Grammar P0 pass rate ≥ 0.92.
[ ] Entity span F1 ≥ 0.88.
[ ] Entity canonical accuracy ≥ 0.90.
[ ] Universe detection accuracy ≥ 0.90.
[ ] Transliteration known-name accuracy ≥ 0.95.
[ ] Alias-chain accuracy ≥ 0.88.
[ ] Pronoun consistency ≥ 0.85.
[ ] Zero-pronoun false insertion ≤ 0.08.
[ ] Residual Hanzi = 0 trừ protected intentional spans.
[ ] No [universe_tag] in output.
[ ] Learning promotion requires review + regression pass.
[ ] CI blocks failed regression.
[ ] E2E full chapter tests pass.
```

---

# 23. KẾT LUẬN

Bản V2 là kế hoạch tốt cho nhánh Cross-Universe Entity. Tuy nhiên để hoàn thiện toàn repo `converter-drduc`, cần triển khai theo V3:

```text
1. Khóa governance trước.
2. Tách TM an toàn.
3. Chuẩn hóa SegmentPacket/Trace.
4. Làm segment/protected/noise.
5. Thêm grammar scanner non-LLM.
6. Nâng term bank/universe/entity.
7. Làm grammar transfer planner.
8. Làm context resolver.
9. Làm metadata DB + learning loop.
10. Khóa regression/CI/release.
```

Tên nhánh đề xuất:

```text
converter-drduc-v24-production-hardening
```

Tên milestone:

```text
v23.5 — Non-LLM Grammar Pattern Mining
v23.6 — Core Governance + TM Split
v23.7 — Segment/Noise Safety
v23.8 — Cross-Universe Entity System
v23.9 — Grammar Transfer Planner
v24.0 — Production Release Candidate
```
