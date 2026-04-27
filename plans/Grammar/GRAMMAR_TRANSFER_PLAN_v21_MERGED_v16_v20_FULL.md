# GRAMMAR_TRANSFER_PLAN_v21_MERGED_v16_v20_FULL

**Repo:** `converter-drduc`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Nguồn hợp nhất:** v16 + v17 + v18 + v19 + v20  
**Phạm vi:** chương 1 → hết truyện  
**Ngày:** 2026-04-25  
**Phiên bản:** v21.0 — Unified New-Story Domain Completion Plan  

---

## 0. Executive Summary

Bản v21 gộp toàn bộ kế hoạch mở rộng từ **v16 đến v20** thành một file thống nhất, phục vụ triển khai thuật toán Grammar Transfer ZH→VI cho corpus mới **Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới**.

Các bản con được hợp nhất:

| Version | Phạm vi | Trọng tâm |
|---|---|---|
| v16 | Chương 1–100 | System panel, simulator log, sci-fi/game foundation, grade/rank, time-flow ratio, currency/resource, tech item, slang/SFX |
| v17 | Chương 101–200 | Space fleet, civilization/faction, auction/price, lifeform grade, gene/module item, navigation/hazard, system upgrade |
| v18 | Chương 201–400 | Planet/race/legion, bloodline, power layer, franchise artifact, evolution/datafication, strategy/admin, named-entity scanner completion |
| v19 | Chương 401–600 | Cosmic artifact, artifact lifecycle, symbiote/biotech, faction war, combat idiom, mythic/divine scanner, alias lifecycle |
| v20 | Chương 601–end | Endgame transcender system, anchor progress, cosmic alliance diplomacy, probability/information state, dimension blockade, final alias hierarchy |

Bản v21 không thay thế các bản v14/v15 nền tảng; nó là **domain expansion tổng hợp** cho truyện mới, tập trung vào:
- System/simulator format.
- Sci-fi/game/space-war grammar.
- Alphanumeric/rank/number conversion.
- Named-entity scanning nhiều miền.
- Entity lifecycle và alias hierarchy.
- Cross-franchise artifacts.
- Endgame cosmic ontology.
- Author-note/meta filtering.

---

## 1. Unified Architecture cho v16–v20

```text
Input chapter / paragraph / sentence
  ↓
ChapterTitleParser + AuthorMetaFilter
  ↓
SystemPanelParser / BracketItemExtractor
  ↓
ProtectedSpanEngine
  ↓
EntityScanner Stack
  ├─ CrossWorldEntityDetector
  ├─ SciFiTechEntityChainParser
  ├─ Space/Civilization/Faction Scanner
  ├─ Planet/Race/Legion Scanner
  ├─ CosmicArtifactScanner
  ├─ TranscenderSystemScanner
  ├─ ProperNameConfidenceScorer
  ├─ AliasHierarchyResolver
  └─ EntityLifecycleTracker
  ↓
Tokenizer + POS + Shallow Construction Detector
  ↓
Domain Grammar Rules
  ├─ System reward/log/state rules
  ├─ Grade/rank/lifeform/power-layer rules
  ├─ Number/currency/resource/time-flow rules
  ├─ Tech/product/equipment/gene-item rules
  ├─ Navigation/hazard/war/action rules
  ├─ Diplomacy/political/strategy discourse rules
  ├─ Probability/dimension/engineering rules
  └─ Colloquial/SFX/meme title rules
  ↓
Existing RBMT lexical loop + LuatNhan + EAPEE
  ↓
Surface cleanup + trace export
  ↓
Output VI
```

---

## 2. Unified Rule Priority v21

```text
P00 ProtectedSpanEngine
P01 ChapterTitleEntitySeeder
P02 SystemPanelParser
P03 EndgameSystemPanelKindClassifier
P04 ChapterTitleParser
P05 AuthorNoteFilter / AuthorMetaParagraphClassifier
P06 BracketItemExtractor / NestedBracketItemParser
P07 CrossWorldEntityDetector
P08 SciFiTechEntityChainParser
P09 Space/Civilization/Faction Scanner
P10 Planet/Race/Legion Scanner
P11 CosmicArtifactScanner
P12 TranscenderSystemScanner
P13 Creator/IntelligenceEntityScanner
P14 CivilizationalHierarchyResolver
P15 FactionHierarchyResolver
P16 AlphanumericGradeGuard
P17 GradeRankConverter
P18 LifeformGradeClassifier
P19 PowerLayerClassifier
P20 ProbabilityInformationTermParser
P21 Tech/Bio/Symbiote/Artifact Entity Parser
P22 ProperNameConfidenceScorer
P23 AliasHierarchyResolver
P24 ArtifactLifecycleTracker
P25 ClauseSplitter
P30 Core Grammar / v15 rules
P35 SystemRewardRule
P36 MissionSettlementRule
P37 SystemUpgradeRule
P40 AuctionPriceParser
P45 TimeFlowRatioConverter
P50 Currency/ResourceNumberConverter
P55 NavigationSpaceRule
P60 LargePopulationNumberConverter
P65 DimensionBlockadeRule
P66 MegaStructureEngineeringRule
P70 Evolution/DataficationRule
P72 ArtifactLifecycleRule
P75 Strategy/Admin/AnnouncementRules
P78 Political/Alliance/DiplomacyRules
P80 ColloquialTone/EAPEE Extension
P85 DramaticImperativeRule
P90 SFXPreserver
P95 Author/Meta cleanup
P99 Postprocess
```

---

## 3. Unified Module Layout

```text
src/grammar/
├── system/
│   ├── system_panel_parser.py
│   ├── system_reward_rule.py
│   ├── system_upgrade_rule.py
│   ├── mission_settlement_rule.py
│   └── endgame_system_panel_classifier.py
│
├── entity/
│   ├── protected_span.py
│   ├── chapter_title_entity_seeder.py
│   ├── bracket_item_extractor.py
│   ├── nested_bracket_item_parser.py
│   ├── cross_world_entity_detector.py
│   ├── sci_fi_entity_chain_parser.py
│   ├── space_entity_detector.py
│   ├── planet_race_legion_scanner.py
│   ├── faction_hierarchy_resolver.py
│   ├── cosmic_artifact_scanner.py
│   ├── transcender_system_scanner.py
│   ├── creator_intelligence_entity_scanner.py
│   ├── proper_name_confidence_scorer.py
│   ├── alias_hierarchy_resolver.py
│   └── entity_lifecycle_tracker.py
│
├── number/
│   ├── grade_rank_converter.py
│   ├── lifeform_grade_classifier.py
│   ├── power_layer_classifier.py
│   ├── time_flow_ratio_converter.py
│   ├── currency_resource_converter.py
│   ├── auction_price_parser.py
│   ├── ammo_measure_converter.py
│   ├── large_population_number_converter.py
│   └── anchor_progress_parser.py
│
├── domain_rules/
│   ├── tech_product_model_parser.py
│   ├── weapon_ammo_rule.py
│   ├── passive_result_rule.py
│   ├── equipment_install_rule.py
│   ├── navigation_space_rule.py
│   ├── radiation_hazard_rule.py
│   ├── bio_gene_item_parser.py
│   ├── evolution_datafication_rule.py
│   ├── artifact_lifecycle_rule.py
│   ├── cosmic_combat_action_rule.py
│   ├── dramatic_imperative_rule.py
│   ├── probability_information_rule.py
│   ├── dimension_blockade_rule.py
│   ├── megastructure_engineering_rule.py
│   ├── diplomacy_scene_rule.py
│   ├── political_blame_rule.py
│   ├── strategy_discourse_rule.py
│   ├── admin_mission_rule.py
│   ├── bounty_announcement_rule.py
│   └── narrative_timeskip_rule.py
│
├── colloquial/
│   ├── slang_tone_rule.py
│   ├── onomatopoeia_rule.py
│   ├── meme_title_parser.py
│   └── author_meta_classifier.py
```

---

## 4. Unified Data Files

```text
data/grammar/
├── system_panel_patterns.json
├── simulator_state_terms.json
├── system_reward_terms.json
├── system_upgrade_terms.json
├── endgame_system_panel_kinds.json
├── anchor_progress_patterns.json
├── mission_settlement_patterns.json
│
├── cross_world_entities.json
├── sci_fi_entity_suffix_ontology.json
├── space_fleet_suffixes.json
├── polity_faction_suffixes.json
├── planet_race_legion_suffixes.json
├── faction_hierarchy_patterns.json
├── cosmic_artifact_glossary.json
├── franchise_artifact_glossary.json
├── creator_intelligence_entities.json
├── transcender_system_terms.json
├── source_essence_terms.json
├── final_arc_entity_seed.json
├── entity_confidence_weights.json
├── domain_transliteration_policy.json
│
├── alphanumeric_grade_patterns.json
├── lifeform_grade_patterns.json
├── power_layer_patterns.json
├── currency_resource_units.json
├── auction_price_patterns.json
├── time_flow_ratio_patterns.json
├── large_population_number_patterns.json
├── weapon_ammo_units.json
├── measurement_approx_patterns.json
│
├── tech_product_suffixes.json
├── bio_gene_item_suffixes.json
├── equipment_install_verbs.json
├── navigation_space_terms.json
├── radiation_hazard_terms.json
├── divinity_force_terms.json
├── evolution_datafication_terms.json
├── symbiote_biotech_terms.json
├── artifact_lifecycle_verbs.json
├── transformation_state_terms.json
├── probability_information_terms.json
├── dimension_blockade_terms.json
├── megastructure_engineering_terms.json
│
├── news_public_opinion_terms.json
├── admin_investigation_terms.json
├── bounty_announcement_terms.json
├── political_blame_terms.json
├── cosmic_alliance_terms.json
├── civilizational_hierarchy_patterns.json
├── projection_communication_terms.json
├── alliance_subordination_patterns.json
│
├── colloquial_slang_map.json
├── onomatopoeia_map.json
├── colloquial_chapter_title_map.json
├── meme_title_map.json
├── author_note_patterns.json
├── author_note_title_patterns.json
├── author_meta_paragraph_patterns.json
├── idiom_guard_ch401_600.txt
├── final_arc_idiom_guard.txt
└── strategy_intrigue_idioms.txt
```

---

## 5. Unified Acceptance Metrics

| Nhóm | Target |
|---|---:|
| Existing v14/v15 tests | 100% pass |
| System panel parser | ≥ 98% |
| Bracket format preservation | 100% |
| Cross-world entity protection | ≥ 97% |
| Sci-fi/tech entity chain | ≥ 95% |
| Space/civilization/faction scanner | ≥ 95% |
| Planet/race/legion scanner | ≥ 96% |
| Cosmic artifact scanner | ≥ 98% |
| Transcender/system term scanner | ≥ 98% |
| Proper-name scanner precision | ≥ 93% |
| Alias hierarchy linking | ≥ 92% |
| Artifact lifecycle tracking | ≥ 95% |
| Grade/rank/lifeform conversion | ≥ 98% |
| Currency/resource/price conversion | ≥ 98% |
| Time-flow ratio conversion | ≥ 95% |
| Anchor-progress parser | ≥ 98% |
| Probability/information-state parser | ≥ 94% |
| Dimension/engineering grammar | ≥ 92% |
| Political/diplomacy discourse | ≥ 90% |
| Slang/SFX/meme title quality | sampled ≥ 90% |
| Author/meta classifier | ≥ 99% |
| No crash on whole new story | 100% |

---

## 6. Unified Test Buckets

```text
tests/test_grammar_new_story/
├── test_system_panel.py
├── test_system_reward.py
├── test_chapter_title_parser.py
├── test_cross_world_entities.py
├── test_sci_fi_tech_entities.py
├── test_space_fleet_faction.py
├── test_planet_race_legion.py
├── test_cosmic_artifact.py
├── test_transcender_system.py
├── test_name_scanner.py
├── test_alias_hierarchy.py
├── test_grade_rank_number.py
├── test_currency_auction_resource.py
├── test_time_flow_ratio.py
├── test_bio_gene_equipment.py
├── test_artifact_lifecycle.py
├── test_navigation_hazard.py
├── test_probability_dimension_engineering.py
├── test_political_diplomacy.py
├── test_colloquial_sfx_meme.py
├── test_author_meta.py
└── test_full_story_regression.py
```

---

# PART I — v16 Full Content: Chapters 1–100

**Repo:** `converter-drduc`  
**Kế thừa:** `GRAMMAR_TRANSFER_PLAN_v14_MERGED_v12_v13_FULL.md` + `GRAMMAR_TRANSFER_PLAN_v15_DEEP_COMPLETION`  
**Corpus mới:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi phân tích:** chương 1–100  
**Ngày:** 2026-04-25  
**Phiên bản:** v16.0 — System/Sci-fi/Game-Corpus Grammar Completion  

---

### 0. Executive Summary

Bản v15 đã bổ sung 25 GAP lớn còn thiếu sau v14: `是/有`, cognitive verb frames, pivot sentence, `而`, VO idiom guard, negation scope, quantifier float, coverb chain, register mixing, ellipsis, number completion, entity possession chain, v.v.

Sau khi đọc corpus mới **Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới** chương 1–100, thuật toán cần mở rộng thêm một nhánh mới: **System/Sci-fi/Game-aware Transfer**.

Truyện này không giống thuần xianxia. Nó trộn nhiều layer:

1. **Văn kể hành động hậu tận thế / sci-fi**
   - tàu vận tải, súng bắn tỉa, robot, năng lượng, cấp bậc chiến lực.
2. **System panel / simulator log**
   - `【宿主:李宇】`, `【分身数量:1（投放中）】`, `【第一天:...】`, `【获得称号-...】`.
3. **Đa thế giới / xuyên giới**
   - `变形金刚世界`, `生化危机世界`, `黑客帝国世界`, `漫威世界`.
4. **Game-resource / grade system**
   - `D级`, `E+级`, `F-`, `称号`, `天赋`, `路线选择`, `冷却时间`, `奖励结算`.
5. **Alphanumeric + Chinese hybrid**
   - `G病毒`, `T病毒`, `1:2`, `1：10`, `F+级`, `D级磁能离子狙击枪–20发子弹`.
6. **Khẩu ngữ/吐槽/Internet slang**
   - `淦`, `md`, `可还行`, `爽麻了`, `智障`, `抽风`, `装逼`, `老梗新活`.
7. **Câu hành động cực ngắn + sound effects**
   - `嗡！`, `啪嗒！`, `轰隆隆！`, `嘭！！`, `砰，砰，砰，砰！`.

Vì vậy v16 bổ sung các lớp thuật toán mới:

```text
A. SystemPanelParser
B. CrossWorldEntityDetector
C. SciFiTechEntityChainParser
D. GradeRankConverter
E. TimeFlowRatioConverter
F. Currency/Resource Number Converter
G. LogEventGrammarParser
H. ColloquialTone/EAPEE Extension
I. Onomatopoeia/SFX Preserver
J. Tech Measurement and Product Model Parser
K. Simulator State Machine Terms
L. Alphanumeric Entity Guard
```

---

### 1. Corpus Signals từ chương 1–100

#### 1.1 Thống kê sơ bộ

```text
Chapters analyzed: 100
Approx. Chinese chars: ~261k
Sentence-like units: ~10.7k
System-panel bracket pairs: ~698
```

Một số pattern tần suất cao trong 100 chương đầu:

| Pattern | Count approx | Ý nghĩa |
|---|---:|---|
| `【...】` | ~698 pairs | system panel/log |
| `是` | ~3.1k | copula/classification/emphasis |
| `有` | ~2.3k | possession/existential/estimation |
| `被` | ~617 | passive/result passive |
| `让` | ~451 | causative/pivot/passive-like |
| `将` | ~156 | disposal/formal object fronting |
| `出来` | ~329 | emergence/perception/output |
| `起来` | ~188 | inceptive/posture/abstract |
| `下来` | ~128 | down/stabilize/record |
| `吧/吗/啊/呢` | ~820 total | thoại khẩu ngữ |
| `星币` | ~133 | currency unit |
| `级` | ~252 | rank/grade level |
| `D级` | ~40 | grade entity |
| `E+` | ~38 | grade with plus |
| `1:2 / 1：10` | multiple | time-flow / odds ratio |
| `24小时` | multiple | cooldown duration |

---

### 2. Những GAP mới sau v15

```text
V16-GAP-01: System panel / log block chưa có parser riêng
V16-GAP-02: Bracketed entity và system item chưa được bảo vệ đầy đủ
V16-GAP-03: Alphanumeric grade/rank: D级, E+级, F-, B+生命体
V16-GAP-04: Time-flow ratio: 主世界比例为1:2, 矩阵世界与主世界比例为1:10
V16-GAP-05: Currency/resource: 星币, 奖励, 称号, 天赋, 分身数量
V16-GAP-06: Cross-world/franchise entity: 生化危机世界, 黑客帝国世界, 漫威世界
V16-GAP-07: Tech product model chain: 巨神运输3型飞船, D级磁能离子狙击枪
V16-GAP-08: Weapon/ammo format: 武器–20发子弹, 子弹/弹匣/发/枚
V16-GAP-09: Simulator state verbs: 投放/回收/冷却/提取/加载/刷新/结算
V16-GAP-10: System reward grammar: 获得X-名称:说明
V16-GAP-11: 被当做/被改造成/被视为 result passive
V16-GAP-12: 把/将 + O + V成/进/到/给 sci-fi action disposal
V16-GAP-13: Colloquial/internet slang and tone particles
V16-GAP-14: Onomatopoeia and SFX preservation
V16-GAP-15: Scientific measurement: 百万吨级, 千米外, 百倍放大, 半人高
V16-GAP-16: Approximate body/size expressions: 足有/不足/只有/仅仅
V16-GAP-17: Dialogue interruption and stutter: 怎么…怎么…会…
V16-GAP-18: Author note / meta text filtering
V16-GAP-19: Nickname/title entity: 狗王, 双刀库尔, 三胖子, 猎人, 寡妇
V16-GAP-20: Multi-world log day heading: 第一天/第二十一天 + colon + event
```

---

## PART A — System Panel Parser

### A1. Vấn đề

Trong corpus mới, system text xuất hiện dày đặc:

```text
【宿主:李宇】
【分身数量:1（投放中）】
【变形金刚世界:分身生存时间–7天】
【获得白色称号【菊花守护者】:可佩戴称号，菊花不破于肥皂。】
【分身冷却中，24小时后可再次进行投放…】
```

Nếu dịch như văn thường, grammar transfer sẽ:
- đảo sai dấu ngoặc,
- tách sai item name,
- dịch lẫn metadata và narrative,
- chuyển số/rank sai trong tên item,
- phá format `key:value`.

### A2. Thuật toán `SystemPanelParser`

#### A2.1 Data model

```python
@dataclass
class SystemPanel:
    raw: str
    start: int
    end: int
    kind: str
    key: str = ""
    value: str = ""
    item_name: str = ""
    grade: str = ""
    description: str = ""
    nested_items: list[str] = field(default_factory=list)
```

#### A2.2 Các loại panel

| Kind | Pattern | Ví dụ |
|---|---|---|
| `STATE` | `【宿主:...】` | `【宿主:李宇】` |
| `COUNT_STATE` | `【分身数量:1（投放中）】` | count + status |
| `WORLD_LOG` | `【世界:事件】` | `【变形金刚世界:分身生存时间–7天】` |
| `DAY_LOG` | `【第N天:...】` | `【第一天:作为一名黑户...】` |
| `REWARD` | `【获得X-名称:说明】` | `【获得绿色称号-剧情破坏者。】` |
| `ITEM` | `【特殊物品–名称，是否提取？】` | `【获得特殊物品–超级士兵血清，是否提取？】` |
| `COOLDOWN` | `【分身冷却中，24小时后...】` | cooldown |
| `ROUTE` | `【路线选择:...】` | choice options |
| `NOTE` | `注:...` trong ngoặc | flow ratio, condition |

#### A2.3 Dịch preserving format

```text
【宿主:李宇】
→ 【Ký chủ: Lý Vũ】

【分身数量:1（投放中）】
→ 【Số lượng phân thân: 1 (đang thả xuống)】

【分身冷却中，24小时后可再次进行投放…】
→ 【Phân thân đang hồi chiêu, sau 24 giờ có thể thả xuống lần nữa...】
```

#### A2.4 Rule

```python
if span.startswith("【") and span.endswith("】"):
    protect_as_system_panel(span)
    parse_inner_with_panel_rules()
    do_not_apply_general_de_inversion_or_ba_rules()
```

---

## PART B — System Reward/Event Grammar

### B1. `获得 X-名称:说明`

```text
【获得白色称号【菊花守护者】:可佩戴称号，菊花不破于肥皂。】
```

**VI:**

```text
【Nhận được danh hiệu trắng [Người Bảo Vệ Hoa Cúc]: danh hiệu có thể đeo, hoa cúc không bị phá bởi xà phòng.】
```

#### Rule

```python
Pattern: 获得 + [GRADE]? + [CATEGORY] + [-/–] + [NAME] + [:] + DESC
Output: Nhận được + CATEGORY_vi + GRADE_vi + [NAME_vi/protected] + ": " + DESC_vi
```

#### Mapping

```python
SYSTEM_CATEGORY_MAP = {
    "称号": "danh hiệu",
    "天赋": "thiên phú",
    "异能": "dị năng",
    "特殊物品": "vật phẩm đặc biệt",
    "生存里程奖励": "thưởng mốc sinh tồn",
    "奖励": "phần thưởng",
    "礼包": "gói quà",
}
```

---

### B2. `是否提取？`

```text
【获得特殊物品–超级士兵血清，是否提取？】
```

**VI:**

```text
【Nhận được vật phẩm đặc biệt – Huyết thanh Siêu Chiến Binh, có rút ra không?】
```

#### Rule

```python
是否 + V → có V không?
是否提取 → có rút ra không?
是否佩戴 → có đeo không?
是否加载 → có tải vào không?
```

---

### B3. `冷却中 / 投放中 / 回收中 / 结算中`

```python
SYSTEM_STATE_MAP = {
    "投放中": "đang thả xuống",
    "冷却中": "đang hồi chiêu",
    "回收中": "đang thu hồi",
    "奖励结算中": "đang kết toán phần thưởng",
    "系统升级中": "hệ thống đang nâng cấp",
    "数据分析中": "đang phân tích dữ liệu",
    "坐标定位中": "đang định vị tọa độ",
    "世界壁垒偷渡通道打开中": "đang mở kênh lén vượt qua vách ngăn thế giới",
}
```

---

## PART C — Cross-world Entity Detector

### C1. Entity pattern

Corpus có nhiều world/franchise terms:

```text
变形金刚世界
生化危机世界
黑客帝国世界
漫威世界
保护伞公司
红后基地
神盾局
美国队长
史密斯
尼奥
T病毒
G病毒
超级士兵血清
```

### C2. Rule nhận diện

```python
WORLD_SUFFIXES = ["世界", "宇宙", "位面", "基地", "公司", "组织", "文明"]
FRANCHISE_ALIASES = {
    "变形金刚": "Transformers",
    "生化危机": "Resident Evil",
    "黑客帝国": "The Matrix",
    "漫威": "Marvel",
    "保护伞公司": "Tập đoàn Umbrella",
    "红后": "Red Queen",
    "神盾局": "S.H.I.E.L.D.",
}
```

#### C2.1 Protected translation policy

| ZH | VI |
|---|---|
| `变形金刚世界` | thế giới Transformers |
| `生化危机世界` | thế giới Resident Evil |
| `黑客帝国世界` | thế giới The Matrix |
| `漫威世界` | thế giới Marvel |
| `保护伞公司` | Công ty Umbrella / Tập đoàn Umbrella |
| `T病毒` | virus T |
| `G病毒` | virus G |

### C3. Không number-convert / split inside franchise entity

```text
G病毒稳定强化药剂
→ Dược tề cường hóa ổn định virus G
```

Không tách `G` như grade.

---

## PART D — GradeRankConverter

### D1. Vấn đề

Corpus có:

```text
D级
E+级
F-
F+级别
B+生命体
E级之上
E+级以下
比F-高了两个等级
```

### D2. Grade grammar

```python
GRADE_RE = r"\b([SABCDEF])([+\-])?级?(别)?\b"
```

### D3. Mapping

| ZH | VI |
|---|---|
| `D级` | cấp D |
| `E+级` | cấp E+ |
| `F-` | F- |
| `F+级别` | cấp bậc F+ |
| `B+生命体` | sinh mệnh thể cấp B+ |
| `E+级以下` | dưới cấp E+ / từ E+ trở xuống |
| `E级之上` | trên cấp E |
| `比F-高两个等级` | cao hơn F- hai cấp |

### D4. Rule

```python
if token matches grade and next in ["级", "级别"]:
    protect_alphanumeric_grade()
    translate_as_rank()
```

### D5. Grade comparison

```text
比 X 高 N 个等级
→ cao hơn X N cấp

X 以下
→ từ X trở xuống / dưới X

X 之上
→ trên X
```

---

## PART E — TimeFlowRatioConverter

### E1. Pattern

```text
当前投放世界与主世界流速不一致，为1:2
矩阵世界与主世界比例为（1:10）
原本1:5的赔率被人拉到1:2了
```

### E2. Phân biệt ratio type

| Context | Meaning | VI |
|---|---|---|
| `流速/比例/主世界/世界` | time-flow ratio | tỷ lệ thời gian |
| `赔率` | betting odds | tỷ lệ cược |
| `兑换比例` | exchange rate | tỷ lệ quy đổi |
| `能量比例` | energy ratio | tỷ lệ năng lượng |

### E3. Rule

```python
if nearby(["流速", "主世界", "世界比例"]):
    "1:2" → "tỷ lệ 1:2"
elif nearby(["赔率"]):
    "1:2" → "tỷ lệ cược 1:2"
else:
    keep "1:2"
```

### E4. Translation examples

```text
当前投放世界与主世界流速不一致，为1:2
→ tốc độ thời gian giữa thế giới được thả xuống hiện tại và thế giới chính không đồng nhất, là 1:2

矩阵世界与主世界比例为（1:10）
→ tỷ lệ giữa thế giới Ma Trận và thế giới chính là (1:10)
```

---

## PART F — Currency / Resource Number Converter

### F1. Currency units

```python
CURRENCY_UNITS = {
    "星币": "tinh tệ",
    "信用点": "điểm tín dụng",
    "积分": "điểm",
    "奖励点": "điểm thưởng",
    "奖励点数": "điểm thưởng",
}
```

### F2. Number style policy

| Context | Output |
|---|---|
| small narrative | `hai nghìn tinh tệ` |
| large currency | `5.000 tinh tệ`, `30 tỷ tinh tệ` |
| system panel | preserve digits if source uses digits |
| xianxia/literary | can use `vạn`, `ức` if configured |

### F3. Examples

```text
5000星币
→ 5.000 tinh tệ

12500星币
→ 12.500 tinh tệ

三十亿星币
→ 30 tỷ tinh tệ

十万星币
→ 100.000 tinh tệ / mười vạn tinh tệ
```

### F4. Resource/state numbers

```text
分身数量:1
→ số lượng phân thân: 1

生存时间7天
→ thời gian sinh tồn: 7 ngày

冷却时间六十小时
→ thời gian hồi chiêu: 60 giờ
```

---

## PART G — Tech Product Model Parser

### G1. Product model chain

```text
巨神运输3型飞船
百万吨级的运输船
D级磁能离子狙击枪
棱体能量护盾––蜉蝣型
逆闪单兵推进器
方舟精神转移与肉体重生系统
```

### G2. Pattern

```python
TECH_PRODUCT_PATTERN = [
    BRAND_OR_SERIES,
    FUNCTION_MODIFIER*,
    MODEL_NUMBER?,
    TYPE_SUFFIX
]
```

### G3. Suffix ontology

```python
TECH_SUFFIXES = [
    "飞船", "运输船", "狙击枪", "子弹", "护盾", "推进器",
    "系统", "装置", "药剂", "血清", "机器人", "摩托", "引擎",
    "外骨骼", "义肢", "芯片", "能量核心", "瞄镜", "枪匣"
]
```

### G4. Translation examples

```text
巨神运输3型飞船
→ phi thuyền vận tải loại 3 Cự Thần

D级磁能离子狙击枪
→ súng bắn tỉa ion từ năng cấp D

百万吨级的运输船
→ tàu vận tải cấp triệu tấn

棱体能量护盾––蜉蝣型
→ khiên năng lượng lăng thể – mẫu Phù Du
```

### G5. Guard

Nếu product chain có:
- alphanumeric grade,
- model number,
- dash,
- bracketed name,

thì protect toàn span trước grammar inversion.

---

## PART H — Weapon / Ammo Format

### H1. Patterns

```text
D级磁能离子狙击枪–20发子弹
三枚赤色的子弹
一发集束光线
枪匣很长，里面只有二十发子弹
```

### H2. Unit map

| ZH unit | VI |
|---|---|
| `发` | phát / viên đạn / luồng bắn |
| `枚` | viên / quả / cái |
| `柄` | thanh / khẩu |
| `把` | khẩu / thanh / cái |
| `颗` | viên |
| `道` | luồng / vệt |
| `束` | chùm / tia |

### H3. Context classifier

```python
if unit == "发" and head in ["子弹", "炮弹"]:
    "20发子弹" → "20 viên đạn"
elif unit == "发" and head in ["光线", "攻击"]:
    "一发集束光线" → "một phát tia hội tụ"
```

---

## PART I — Passive/Result Passive mở rộng

### I1. Pattern `被当做 / 被视为 / 被改造成`

```text
被当做偷渡客
→ bị coi là kẻ nhập cư lậu

被改造成暴君
→ bị cải tạo thành Tyrant

被视为大号电池
→ bị xem là cục pin cỡ lớn
```

### I2. Rule

```python
PASSIVE_RESULT_VERBS = {
    "当做": "coi là",
    "视为": "xem là",
    "改造成": "cải tạo thành",
    "封在": "phong trong / chôn trong",
    "带到": "đưa đến",
}
```

```text
被 + V_RESULT + NP
→ bị + V_RESULT_vi + NP
```

### I3. Distinguish passive vs lexical compound

```text
被感染者
→ Người bị nhiễm / Kẻ bị nhiễm
```

Nếu `被感染者` là system title/item, protect as item name.

---

## PART J — Simulator State Machine Terms

### J1. Glossary

```python
SIMULATOR_TERMS = {
    "分身": "phân thân",
    "本体": "bản thể",
    "投放": "thả xuống / triển khai",
    "回收": "thu hồi",
    "提取": "rút ra / trích xuất",
    "冷却": "hồi chiêu",
    "路线选择": "lựa chọn tuyến đường",
    "综合评价": "đánh giá tổng hợp",
    "生存时间": "thời gian sinh tồn",
    "奖励结算": "kết toán phần thưởng",
    "称号库": "kho danh hiệu",
    "天赋库": "kho thiên phú",
    "加载": "tải vào",
    "刷新": "làm mới / cập nhật",
}
```

### J2. Event grammar

```text
分身已死亡，回收中，生存时间7天…奖励结算中…
→ Phân thân đã tử vong, đang thu hồi, thời gian sinh tồn 7 ngày... đang kết toán phần thưởng...
```

---

## PART K — Colloquial / Internet Slang / Tone

### K1. Slang map

```python
SLANG_MAP = {
    "淦": "đệt",
    "md": "mẹ nó",
    "智障": "thiểu năng",
    "抽风": "lên cơn",
    "装逼": "làm màu / tỏ vẻ",
    "可还行": "thế mà cũng được à",
    "爽麻了": "phê tê người",
    "离谱": "vô lý / quá đáng",
    "老梗新活": "meme cũ trò mới",
}
```

### K2. Tone particles mở rộng

| ZH | VI |
|---|---|
| `吧` | nhỉ / đi / chứ |
| `吗` | không / à |
| `呢` | đây / nhỉ / thì sao |
| `啊` | à / đó / cảm thán |
| `呦` | đó nha / cơ đấy |
| `嘛` | mà |
| `呃` | ờm / ặc |

### K3. Rule

Nếu câu là thoại và có slang:
- giữ sắc thái khẩu ngữ,
- không nâng lên văn phong cổ/xianxia,
- ưu tiên dịch tự nhiên hơn literal.

---

## PART L — Onomatopoeia and SFX Preserver

### L1. Frequent SFX

```text
嗡！
啪嗒！
轰隆隆！
嘭！！
砰，砰，砰，砰！
哗啦啦
飒！
```

### L2. Translation policy

| ZH | VI |
|---|---|
| `嗡` | vù / ong ong |
| `啪嗒` | cạch / bộp |
| `轰隆隆` | ầm ầm / ùng ùng |
| `嘭` | bùm / phịch |
| `砰` | đoàng / bang |
| `哗啦啦` | loảng xoảng / rào rào |
| `飒` | vút |

### L3. Rule

```python
if sentence_is_sfx_only():
    translate_sfx_or_preserve()
    skip grammar transfer
```

---

## PART M — Scientific / Physical Measurement

### M1. Patterns

```text
百万吨级
足有一人高
半人高
两米多高
百倍放大
千米外
十几吨
二十公分长
近百艘战舰
```

### M2. Rule

| ZH | VI |
|---|---|
| `百万吨级` | cấp triệu tấn |
| `足有一人高` | cao bằng cả một người |
| `半人高` | cao nửa thân người |
| `两米多高` | cao hơn hai mét |
| `百倍放大` | phóng đại gấp trăm lần |
| `千米外` | ngoài nghìn mét / cách nghìn mét |
| `十几吨` | hơn mười tấn |
| `二十公分长` | dài 20 cm |
| `近百艘战舰` | gần trăm chiến hạm |

### M3. Approximation triggers

```python
APPROX_TRIGGERS = ["足有", "不足", "不到", "至少", "仅仅", "只有", "近", "近乎", "大约", "左右", "上下", "十几", "几十", "数十"]
```

---

## PART N — Author Note / Meta Text Filter

### N1. Corpus có author note

```text
（新人新书，求求各位大佬的关照了，来者不拒…每天都看看呗，毕竟…追读什么的…）
（新人新书，呜呜呜…求票票，求收藏…）
```

### N2. Rule

```python
if paragraph.startswith("（") and contains(["求票", "求收藏", "求订阅", "新人新书", "月票"]):
    mark_as_author_note
```

### N3. Config

```python
translation_config = {
    "translate_author_notes": False,
    "preserve_author_notes": True,
    "author_note_prefix": "Ghi chú tác giả:"
}
```

---

## PART O — Nickname / Title Entity Recognition

### O1. Nickname patterns

```text
狗王
双刀库尔
三胖子
猎人
寡妇
老陆
小吵闹
山鸡
三先生
```

### O2. Rule

```python
if short span appears repeatedly and used as subject/vocative:
    classify as CHARACTER_ALIAS
```

### O3. Title + name

```text
双刀库尔
→ Song Đao Kuer / Kuer Song Đao

三胖子
→ Tam Bàn Tử

狗王
→ Cẩu Vương

小吵闹
→ Tiểu Ồn Ào / Claptrap nếu glossary maps franchise
```

### O4. Alias memory

```python
EntityMemory.add_alias("库尔", "双刀库尔")
EntityMemory.add_alias("三胖子", "三先生")
```

---

## PART P — `算是 / 也算 / 可算是 / 只能算`

### P1. Pattern

```text
也算小有名气
这算是一个小福利
已经算是好手了
只能算是普通
```

### P2. VI mapping

| ZH | VI |
|---|---|
| `算是` | xem như / coi như là |
| `也算` | cũng xem như |
| `可算是` | cũng có thể xem là |
| `只能算` | chỉ có thể xem là |

### P3. Rule

```python
算是 + NP/ADJ → xem như là + NP/ADJ
```

---

## PART Q — `就这么 / 就这样 / 就这么死了`

### Q1. Pattern

```text
就这么死了
就这样对待
就这么挂了
```

### Q2. VI

```text
cứ thế mà chết
đối xử như vậy
cứ thế mà toi
```

### Q3. Rule

```python
就这么/就这样 + V
→ cứ thế/cứ như vậy mà + V
```

---

## PART R — Rhetorical Dialogue Forms

### R1. Examples

```text
你知不知道...？
这就算还人情了？
这么牵强的吗？
怎么可能？
何必在这个破地方待着？
岂不是太可惜了？
```

### R2. Rule

| Pattern | VI |
|---|---|
| `你知不知道...` | ngươi có biết... không |
| `这就算...了？` | thế này mà cũng tính là...? |
| `这么...的吗？` | ... thế này sao? |
| `怎么可能` | sao có thể |
| `何必...` | cần gì phải |
| `岂不是...` | chẳng phải là ... sao |

---

## PART S — `迫不及待 / 忍不住 / 舍不得 / 懒得`

### S1. Lexicalized modal/emotion guards

```python
EMOTION_MODAL_GUARD = {
    "迫不及待": "không kịp chờ đợi",
    "忍不住": "không nhịn được",
    "舍不得": "không nỡ",
    "懒得": "lười / chẳng buồn",
    "不由得": "không khỏi",
    "不得不": "không thể không / buộc phải",
}
```

### S2. Rule

Treat these as single adverbial/modal units, not normal negation + complement.

---

## PART T — Multi-layer `作为`

### T1. Pattern

```text
作为一名穿越客，这是他赖以生存的本钱
作为一名黑户，在纽约市，您成功被抓了起来
作为目前掌握了子弹时间的你...
```

### T2. Rule

```text
作为 + NP
→ với tư cách là + NP
→ là một + NP, ...
```

### T3. Context

If `作为` begins sentence:
- VI usually fronted: `Với tư cách là...`
If inside system log:
- preserve concise: `Là...`

---

## PART U — Implementation Roadmap v16

### Sprint V16-A — System Panel + Protected Format

- [ ] `system_panel_parser.py`
- [ ] `system_panel_patterns.json`
- [ ] bracket/nested bracket parser
- [ ] preserve `【...】`
- [ ] parse `key:value`, `item-name:desc`, `note`
- [ ] 80 tests

### Sprint V16-B — Sci-fi/Game Entity

- [ ] `cross_world_entity_detector.py`
- [ ] `sci_fi_entity_suffix_ontology.json`
- [ ] franchise glossary: Transformers/Resident Evil/Matrix/Marvel/Umbrella/S.H.I.E.L.D.
- [ ] tech product chain parser
- [ ] alphanumeric entity guard
- [ ] 100 tests

### Sprint V16-C — Grade/Number/Resource

- [ ] `grade_rank_converter.py`
- [ ] `time_flow_ratio_converter.py`
- [ ] `currency_resource_converter.py`
- [ ] `ammo_measure_converter.py`
- [ ] `approx_measure_converter.py`
- [ ] 120 tests

### Sprint V16-D — Colloquial/SFX/Dialogue

- [ ] `slang_tone_map.json`
- [ ] `onomatopoeia_map.json`
- [ ] rhetorical dialogue rule
- [ ] sentence-final particle tone expansion
- [ ] author-note filter
- [ ] 80 tests

### Sprint V16-E — Passive/Result + Simulator Verbs

- [ ] `rule_passive_result.py`
- [ ] `simulator_state_glossary.json`
- [ ] `rule_system_reward.py`
- [ ] `rule_zuowei_frame.py`
- [ ] `rule_suanshi_classification.py`
- [ ] 100 tests

---

## PART V — Test Matrix v16

### V1. System panel

```python
V16_SYSTEM_TESTS = [
    ("【宿主:李宇】", "【Ký chủ: Lý Vũ】"),
    ("【分身数量:1（投放中）】", "【Số lượng phân thân: 1 (đang thả xuống)】"),
    ("【分身冷却中，24小时后可再次进行投放…】",
     "【Phân thân đang hồi chiêu, sau 24 giờ có thể thả xuống lần nữa...】"),
]
```

### V2. Grade/rank

```python
V16_GRADE_TESTS = [
    ("D级磁能离子狙击枪", "súng bắn tỉa ion từ năng cấp D"),
    ("E+级以下的攻击", "công kích từ cấp E+ trở xuống"),
    ("比F-高了两个等级", "cao hơn F- hai cấp"),
]
```

### V3. Time-flow ratio

```python
V16_RATIO_TESTS = [
    ("当前投放世界与主世界流速不一致，为1:2",
     "tốc độ thời gian giữa thế giới được thả xuống hiện tại và thế giới chính không đồng nhất, là 1:2"),
    ("矩阵世界与主世界比例为1:10",
     "tỷ lệ giữa thế giới Ma Trận và thế giới chính là 1:10"),
    ("1:5的赔率被人拉到1:2了",
     "tỷ lệ cược 1:5 bị người ta kéo xuống 1:2"),
]
```

### V4. Currency/resource

```python
V16_CURRENCY_TESTS = [
    ("5000星币", "5.000 tinh tệ"),
    ("三十亿星币", "30 tỷ tinh tệ"),
    ("十万星币", "100.000 tinh tệ"),
]
```

### V5. Passive result

```python
V16_PASSIVE_RESULT_TESTS = [
    ("被当做偷渡客", "bị coi là kẻ nhập cư lậu"),
    ("被改造成暴君", "bị cải tạo thành Tyrant"),
    ("被视为大号电池", "bị xem là cục pin cỡ lớn"),
]
```

### V6. Tech product

```python
V16_TECH_TESTS = [
    ("巨神运输3型飞船", "phi thuyền vận tải loại 3 Cự Thần"),
    ("百万吨级的运输船", "tàu vận tải cấp triệu tấn"),
    ("D级磁能离子狙击枪–20发子弹", "súng bắn tỉa ion từ năng cấp D – 20 viên đạn"),
]
```

### V7. Colloquial/rhetorical

```python
V16_DIALOGUE_TESTS = [
    ("这就算还人情了？", "thế này mà cũng tính là trả nhân tình rồi sao?"),
    ("怎么可能！", "sao có thể!"),
    ("岂不是太可惜了", "chẳng phải là quá đáng tiếc sao"),
    ("可还行", "thế mà cũng được à"),
]
```

### V8. SFX

```python
V16_SFX_TESTS = [
    ("嗡！", "Vù!"),
    ("啪嗒！", "Cạch!"),
    ("轰隆隆！", "Ầm ầm!"),
    ("砰，砰，砰，砰！", "Đoàng, đoàng, đoàng, đoàng!"),
]
```

---

## PART W — Data Files cần bổ sung

```text
data/grammar/
├── system_panel_patterns.json
├── simulator_state_terms.json
├── system_reward_terms.json
├── cross_world_entities.json
├── sci_fi_entity_suffix_ontology.json
├── tech_product_suffixes.json
├── alphanumeric_grade_patterns.json
├── currency_resource_units.json
├── time_flow_ratio_patterns.json
├── weapon_ammo_units.json
├── measurement_approx_patterns.json
├── colloquial_slang_map.json
├── onomatopoeia_map.json
├── author_note_patterns.json
└── nickname_title_patterns.json
```

---

## PART X — Acceptance Metrics v16

| Metric | Target |
|---|---:|
| Existing v14/v15 tests | 100% pass |
| System panel parse accuracy | ≥ 98% |
| Bracket format preservation | 100% |
| Alphanumeric grade conversion | ≥ 98% |
| Time-flow ratio conversion | ≥ 95% |
| Currency/resource number conversion | ≥ 98% |
| Cross-world entity protection | ≥ 97% |
| Tech product chain protection | ≥ 95% |
| Passive-result pattern accuracy | ≥ 92% |
| Colloquial/SFX translation quality | sampled ≥ 90% |
| No crash on chapters 1–100 | 100% |

---

## PART Y — Merge Strategy với v15

### Y1. V16 không thay thế v15

v15 vẫn là nền deep grammar gap analysis. v16 là **domain extension** cho corpus mới.

### Y2. Rule priority cập nhật

```text
P00 ProtectedSpanEngine
P02 SystemPanelParser
P03 AuthorNoteFilter
P05 EntityChainParser + CrossWorldEntityDetector
P07 AlphanumericGradeGuard
P10 ClauseSplitter
P20 Core Grammar / v15 rules
P30 SystemRewardRule
P40 GradeRankConverter
P50 TimeFlowRatioConverter
P60 Currency/ResourceNumberConverter
P70 TechProductRealizer
P80 ColloquialTone/EAPEE Extension
P90 SFXPreserver
P99 Postprocess
```

### Y3. Vì sao SystemPanelParser phải chạy trước grammar rules

Nếu không:
- `【获得白色称号【菊花守护者】:...】` có nested bracket, dễ split sai.
- `D级` bị xử lý như chữ cái đơn.
- `24小时后` có thể bị time reorder sai.
- `是否提取？` có thể bị parse như normal `是否`.
- item name có thể bị number converter phá.

---

## PART Z — Definition of Done v16

Bản v16 hoàn thành khi:

1. Dịch được system panels mà vẫn giữ format `【...】`.
2. Không phá alphanumeric entity như `G病毒`, `T病毒`, `D级`, `E+`.
3. Dịch đúng tỷ lệ thời gian `1:2`, `1:10` theo context.
4. Dịch đúng tiền tệ và tài nguyên như `星币`, `称号`, `天赋`, `分身数量`.
5. Nhận diện protected entity đa thế giới: Marvel, Matrix, Resident Evil, Transformers, Umbrella, S.H.I.E.L.D.
6. Không tách sai chuỗi sản phẩm sci-fi: `巨神运输3型飞船`, `D级磁能离子狙击枪`.
7. Có rule cho `被当做/被改造成/被视为`.
8. Có map khẩu ngữ/slang và SFX.
9. Có author-note filter.
10. Có ít nhất 480 tests mới cho v16.

---

*v16.0 — System/Sci-fi/Game-Corpus Grammar Completion*  
*Bổ sung 20 GAP mới, 15 data files, 10 module/rule nhóm, ~480 tests đề xuất.*


---

# PART II — v17 Full Content: Chapters 101–200

**Repo:** `converter-drduc`  
**Kế thừa:** `GRAMMAR_TRANSFER_PLAN_v14_MERGED_v12_v13_FULL.md` + `v15` + `v16`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 101–200  
**Ngày:** 2026-04-25  
**Phiên bản:** v17.0 — Space-war / Auction / Civilization / High-tech Entity Completion  

---

### 0. Executive Summary

Bản v16 đã bổ sung lớp **System/Sci-fi/Game-aware Transfer** cho chương 1–100: system panel, phân thân log, cấp bậc `D级/E+级`, tỷ lệ thời gian, `星币`, đa thế giới, vũ khí-công nghệ, slang/SFX.

Sau khi quét chương **101–200**, corpus chuyển mạnh sang các nhánh:

1. **Marvel / vũ trụ / chiến tranh liên sao**
   - `【漫威】世界`, `帝国舰队`, `黯星`, `战舰`, `跃迁`, `坐标`, `星际网络`.
2. **Gene / ability / module / biological sci-fi**
   - `病毒原液`, `岩狮基因链`, `金血天赋`, `维罗妮卡模组`, `泰坦殖装`.
3. **Auction / exchange / pricing**
   - `拍卖`, `报价`, `竞价`, `成交`, `起拍价`, `星币`, `买下`, `卖出`.
4. **Civilization / faction / polity**
   - `文明`, `帝国`, `舰队`, `组织`, `集团`, `族群`, `星际公民`.
5. **Power scale / lifeform grade**
   - `A级生命体`, `B级生命体`, `高级生命体`, `超级生命体`, `E+级以下`.
6. **Radiation / hazard zone / biological danger**
   - `重度辐射区`, `辐射`, `污染`, `变异`, `病毒`.
7. **Mission / investigation / census**
   - `普查`, `调查`, `消息`, `线索`, `任务`, `计划`.
8. **Colloquial combat exclamation**
   - `好猛`, `好爽`, `暴打小朋友`, `内奸吧`.

Thống kê sơ bộ chương 101–200:

```text
Chapters analyzed: 100
Approx. Chinese chars: ~426k
System panels: ~890
Grade/rank tokens: ~422
星币 occurrences: ~109
舰/飞船/战舰 terms: ~667
能量/装甲/护盾/武器 terms: ~1247
组织/文明/舰队/帝国 terms: ~1033
投放/分身/日志/冷却 terms: ~207
拍卖/报价/价格 terms: ~95
```

Bản v17 bổ sung 18 nhóm thuật toán mới:

```text
V17-GAP-01  Space-fleet / starship entity chain
V17-GAP-02  Civilization/faction polity detector
V17-GAP-03  Auction/price grammar
V17-GAP-04  Lifeform grade classifier
V17-GAP-05  Gene/virus/module item chain
V17-GAP-06  Armor/equipment/mod install grammar
V17-GAP-07  Coordinate/jump/navigation expressions
V17-GAP-08  Radiation/hazard-zone expressions
V17-GAP-09  Power synchronization / system upgrade grammar
V17-GAP-10  Probability/risk/evaluation phrases
V17-GAP-11  News/report/public-opinion discourse
V17-GAP-12  Administrative/census/investigation grammar
V17-GAP-13  Multi-token named titles with bracketed names
V17-GAP-14  “对...产生作用/影响” frame
V17-GAP-15  “以...作为原材料/基础” material-source frame
V17-GAP-16  Large-scale casualty / population number converter
V17-GAP-17  Percent/probability + success-rate in sci-fi context
V17-GAP-18  Colloquial reaction and meme-like chapter titles
```

---

## PART A — Space Fleet / Starship Entity Chain

### A1. Vấn đề

Chương 101–200 có mật độ rất cao các danh ngữ kỹ thuật/quân sự liên sao:

```text
帝国舰队
黑瞳舰队
星际战舰
运输舰
小型飞船
跃迁轨道
星际网络
生命星球
巨魔星
归星
本菲尔文明之战
```

Nếu dùng rule danh ngữ chung, dễ dịch sai:
- `黑瞳舰队` → “hạm đội mắt đen” literal nhưng đây là tên riêng.
- `本菲尔文明之战` → phải nhận là event name.
- `巨魔星` → địa danh hành tinh, không phải “ngôi sao quỷ khổng lồ” nếu đã xuất hiện như proper place.

### A2. Entity suffix ontology mở rộng

```json
{
  "space_fleet": ["舰队", "战舰", "运输舰", "星舰", "飞船", "母舰", "旗舰"],
  "space_place": ["星", "星球", "行星", "恒星", "星域", "星系", "星港", "跃迁轨道"],
  "space_network": ["星际网络", "通讯网络", "频道", "坐标", "航线"],
  "war_event": ["之战", "战争", "战役", "冲突", "袭击"]
}
```

### A3. Rule

```python
if span.endswith(("舰队", "战舰", "飞船", "星球", "星", "之战")):
    if span has proper-name prefix or repeated in corpus:
        protect_as_entity(span)
    else:
        translate_as_common_noun_chain(span)
```

### A4. Examples

```text
黑瞳舰队
→ Hạm đội Hắc Đồng

帝国舰队
→ hạm đội Đế Quốc

本菲尔文明之战
→ trận chiến văn minh Benfell

巨魔星
→ hành tinh Cự Ma / Troll Star theo glossary

生命星球
→ hành tinh có sự sống
```

---

## PART B — Civilization / Faction / Polity Detector

### B1. Pattern

```text
文明
帝国
集团
组织
舰队
族群
星际公民
高级生命体群体
```

### B2. Rule

```python
POLITY_SUFFIXES = ["文明", "帝国", "集团", "组织", "族群", "舰队", "联盟", "公司"]
```

### B3. Translation policy

| ZH | VI |
|---|---|
| `文明` | nền văn minh |
| `帝国` | đế quốc |
| `集团` | tập đoàn / nhóm |
| `组织` | tổ chức |
| `舰队` | hạm đội |
| `族群` | tộc quần / chủng quần |
| `星际公民` | công dân liên sao |

### B4. Proper-name detection

```text
本菲尔文明
→ nền văn minh Benfell

归星
→ Quy Tinh / hành tinh Quy, protected place

光电科技
→ Quang Điện Khoa Kỹ / Công nghệ Quang Điện, organization
```

---

## PART C — Auction / Price / Exchange Grammar

### C1. Vấn đề

Chương 101–200 xuất hiện nhiều ngữ cảnh mua bán, đấu giá:

```text
报价
竞价
起拍价
成交
卖出
买下
价格
价值
星币
三十亿星币
```

### C2. Auction frame

| Pattern | VI |
|---|---|
| `起拍价为 X` | giá khởi điểm là X |
| `报价 X` | ra giá X |
| `竞价到 X` | đấu giá lên đến X |
| `以 X 成交` | chốt giao dịch ở mức X |
| `买下 X` | mua lại X |
| `卖出 X` | bán ra X |
| `价值 X` | trị giá X |

### C3. Rule

```python
AUCTION_VERB_MAP = {
    "报价": "ra giá",
    "竞价": "đấu giá",
    "起拍": "khởi điểm đấu giá",
    "成交": "chốt giao dịch",
    "买下": "mua lại",
    "卖出": "bán ra",
    "出价": "ra giá",
}
```

### C4. Number format

```text
三十亿星币
→ 30 tỷ tinh tệ

一百二十万星币
→ 1,2 triệu tinh tệ / 1.200.000 tinh tệ

起拍价五千万星币
→ giá khởi điểm 50 triệu tinh tệ
```

**Config:**

```python
currency_style = "vietnamese_large"  # tỷ, triệu
currency_style = "digit"             # 30.000.000.000
currency_style = "literary"          # ba mươi ức tinh tệ
```

---

## PART D — Lifeform Grade Classifier

### D1. Pattern

```text
A级生命体
B级生命体
高级生命体
超级生命体
两个A级生命体的战斗
E+级以下的攻击
```

### D2. Rule

```python
LIFEFORM_GRADE_PATTERN = r"([SABCDEF][+\-]?级|高级|超级|低级|中级)\s*生命体"
```

### D3. VI

| ZH | VI |
|---|---|
| `A级生命体` | sinh mệnh thể cấp A |
| `B级生命体` | sinh mệnh thể cấp B |
| `高级生命体` | sinh mệnh thể cao cấp |
| `超级生命体` | sinh mệnh thể siêu cấp |
| `两个A级生命体` | hai sinh mệnh thể cấp A |

### D4. Combat/casualty context

```text
两个A级生命体的战斗，不小心波及了一颗生命星球
→ trận chiến của hai sinh mệnh thể cấp A vô tình lan đến một hành tinh có sự sống
```

---

## PART E — Gene / Virus / Module Item Chain

### E1. Corpus examples

```text
病毒原液
岩狮基因链
金血天赋
维罗妮卡模组
泰坦殖装
超级士兵血清
G病毒
T病毒
```

### E2. Ontology

```json
{
  "bio_item_suffixes": ["病毒", "原液", "血清", "药剂", "基因链", "基因", "模组"],
  "ability_suffixes": ["天赋", "能力", "技能", "模块", "插件"],
  "equipment_suffixes": ["殖装", "装甲", "护盾", "武器", "推进器"]
}
```

### E3. Translation examples

```text
病毒原液
→ nguyên dịch virus

岩狮基因链
→ chuỗi gen Sư Tử Đá

金血天赋
→ thiên phú Huyết Kim

维罗妮卡模组
→ mô-đun Veronica

泰坦殖装
→ thực trang Titan / giáp sinh thể Titan

超级士兵血清
→ huyết thanh Siêu Chiến Binh
```

### E4. Guard

Nếu có bracket `【维罗妮卡模组】` hoặc `【泰坦殖装】`, protect toàn span.

---

## PART F — Armor / Equipment / Mod Install Grammar

### F1. Pattern

```text
塞进了【泰坦殖装】中
融入了他的躯体中
安装在装甲上
加载到系统中
提取出来
融合完成
同步完成
```

### F2. Transfer

| ZH | VI |
|---|---|
| `塞进 X 中` | nhét vào trong X |
| `融入 X 中` | hòa vào trong X |
| `安装在 X 上` | lắp lên X |
| `加载到 X 中` | tải vào X |
| `提取出来` | rút ra / trích xuất ra |
| `同步完成` | đồng bộ hoàn tất |
| `融合完成` | dung hợp hoàn tất |

### F3. Rule

```python
EQUIP_INSTALL_VERBS = ["塞进", "融入", "安装", "加载", "装载", "插入", "提取", "融合", "同步"]
```

**Directional complement xử lý theo domain kỹ thuật:**
- `出来` trong `提取出来` → `rút ra`, không phải chỉ `đi ra`.
- `进去` trong `塞进去` → `nhét vào`.

---

## PART G — Coordinate / Jump / Navigation Expressions

### G1. Pattern

```text
坐标定位中
跃迁轨道
返航
前往巨魔星
到达归星
航线
打开通道
世界壁垒偷渡通道
```

### G2. Mapping

| ZH | VI |
|---|---|
| `坐标定位中` | đang định vị tọa độ |
| `跃迁轨道` | quỹ đạo chuyển tiếp / đường nhảy跃迁 |
| `返航` | trở về hành trình / quay về |
| `前往 X` | đi đến X |
| `到达 X` | đến X |
| `航线` | tuyến bay / đường hàng hành |
| `打开通道` | mở kênh/lối thông đạo |
| `世界壁垒偷渡通道` | kênh lén vượt qua vách ngăn thế giới |

### G3. Rule

```python
if verb in ["前往", "到达", "返航"] and object is space_place:
    use navigation translation
```

---

## PART H — Radiation / Hazard Zone

### H1. Pattern

```text
重度辐射区
辐射污染
污染区域
变异
毒素
感染
病毒泄露
危险区域
```

### H2. Translation

| ZH | VI |
|---|---|
| `重度辐射区` | khu vực bức xạ nặng |
| `辐射污染` | ô nhiễm bức xạ |
| `污染区域` | khu vực ô nhiễm |
| `变异` | biến dị |
| `感染` | lây nhiễm / bị nhiễm |
| `病毒泄露` | rò rỉ virus |
| `危险区域` | khu vực nguy hiểm |

### H3. Passive-result patterns

```text
被感染
→ bị nhiễm

被辐射污染
→ bị ô nhiễm bức xạ

受到辐射影响
→ chịu ảnh hưởng bức xạ
```

---

## PART I — System Upgrade / Power Sync Grammar

### I1. Corpus pattern

```text
分身已死亡…分身回收成功…发现宿主初次生命跃迁完成，分身实力同步中…需要时间––720小时
分身实力同步完成后，系统将会进行升级。
一号分身的实力同步快要结束
```

### I2. Rule

| ZH | VI |
|---|---|
| `分身已死亡` | phân thân đã tử vong |
| `分身回收成功` | thu hồi phân thân thành công |
| `生命跃迁完成` | hoàn tất bước nhảy sinh mệnh |
| `实力同步中` | đang đồng bộ thực lực |
| `需要时间 X` | cần thời gian X |
| `同步完成后` | sau khi đồng bộ hoàn tất |
| `系统将会进行升级` | hệ thống sẽ tiến hành nâng cấp |
| `快要结束` | sắp kết thúc |

### I3. Duration converter

```text
720小时
→ 720 giờ / 30 ngày

是否 auto-normalize 720h → 30 ngày phụ thuộc config:
- preserve_source_unit=True: 720 giờ
- humanize_duration=True: 30 ngày
```

---

## PART J — Probability / Risk / Evaluation Phrases

### J1. Pattern

```text
大概率
小概率
可能性
成功率
风险
不一定
未必
八成
十有八九
```

### J2. Mapping

| ZH | VI |
|---|---|
| `大概率` | khả năng cao |
| `小概率` | xác suất thấp |
| `可能性` | khả năng |
| `成功率` | tỷ lệ thành công |
| `风险` | rủi ro |
| `不一定` | chưa chắc |
| `未必` | chưa hẳn |
| `八成` | tám phần / khoảng 80% |
| `十有八九` | mười phần thì tám chín / gần như chắc |

### J3. Rule

```python
if "概率/成功率/几率" nearby:
    convert 成 as probability ratio
else:
    use general ratio converter
```

---

## PART K — News / Report / Public Opinion Discourse

### K1. Pattern

```text
新闻
报道
讨论度
热度
广泛讨论
对外公布
言论
声明
消息
传闻
流言
```

### K2. Translation

| ZH | VI |
|---|---|
| `新闻热度` | độ nóng tin tức |
| `广泛讨论度` | mức độ thảo luận rộng rãi |
| `对外公布` | công bố ra bên ngoài |
| `言论` | lời phát biểu |
| `声明` | tuyên bố |
| `消息` | tin tức |
| `传闻` | lời đồn |
| `流言` | tin đồn |

### K3. Discourse frame

```text
最近比较火热的新闻，是...
→ tin tức khá nóng gần đây là...

主要是...
→ chủ yếu là...

当然，如果仅仅是这件事本身，还不足以...
→ đương nhiên, nếu chỉ là bản thân chuyện này thì vẫn chưa đủ để...
```

---

## PART L — Administrative / Census / Investigation Grammar

### L1. Pattern

```text
普查
调查
审查
登记
身份
内奸
线索
证据
消息来源
```

### L2. Translation

| ZH | VI |
|---|---|
| `普查` | tổng điều tra / kiểm tra phổ quát |
| `调查` | điều tra |
| `审查` | thẩm tra |
| `登记` | đăng ký |
| `身份` | thân phận |
| `内奸` | nội gián |
| `线索` | manh mối |
| `证据` | chứng cứ |
| `消息来源` | nguồn tin |

### L3. Rule

```python
ADMIN_INVESTIGATION_TERMS = {...}
```

Need classify `普查老爷子` as title/nickname phrase:
- `普查老爷子` → “ông lão tổng điều tra” / protected alias if repeated.

---

## PART M — Bracketed Named Title / Chapter Title Preservation

### M1. Chapter titles

```text
第101章 【漫威】世界
第106章 【黯星】和帝国舰队
第108章 【岩狮基因链】
第197章 好猛，好爽！
```

### M2. Rule

```python
if line startswith 第N章:
    parse as ChapterTitle
    translate title separately
    preserve bracketed entity
```

### M3. Examples

```text
第101章 【漫威】世界
→ Chương 101: Thế giới [Marvel]

第106章 【黯星】和帝国舰队
→ Chương 106: [Ám Tinh] và Hạm đội Đế Quốc

第108章 【岩狮基因链】
→ Chương 108: [Chuỗi gen Sư Tử Đá]
```

---

## PART N — `对...产生作用/影响` Frame

### N1. Pattern

```text
对如今的李宇产生作用
对战斗产生影响
对外公布
对抗分身
对他无用
```

### N2. Classifier

| Pattern | VI |
|---|---|
| `对 X 产生作用` | có tác dụng đối với X |
| `对 X 产生影响` | gây ảnh hưởng đến X |
| `对外公布` | công bố ra bên ngoài |
| `对抗 X` | đối kháng/chống lại X |
| `对 X 无用` | vô dụng với X |

### N3. Rule

```python
if token == "对":
    if next == "外" and later("公布"): fixed "công bố ra bên ngoài"
    elif later("产生作用"): frame_effect_on
    elif later("产生影响"): frame_impact_on
    else: preposition "đối với/với"
```

---

## PART O — `以...作为原材料/基础` Frame

### O1. Pattern

```text
以破碎母盒作为原材料打造
以X作为基础
以X为核心
以X作为能源
```

### O2. VI

```text
lấy Hộp Mẹ vỡ làm nguyên liệu để chế tạo
lấy X làm nền tảng
lấy X làm hạch tâm
lấy X làm nguồn năng lượng
```

### O3. Rule

```python
Pattern: 以 [NP] 作为 [ROLE] V
Output: lấy [NP] làm [ROLE] để V
```

---

## PART P — Large-scale Casualty / Population Number Converter

### P1. Pattern

```text
超过千万级别的人员伤亡
数十万生命
上百万公民
近百艘战舰
```

### P2. Rule

| ZH | VI |
|---|---|
| `超过千万级别` | vượt mức hàng chục triệu |
| `数十万` | mấy chục vạn / hàng trăm nghìn |
| `上百万` | hơn một triệu |
| `近百艘` | gần trăm chiếc |
| `人员伤亡` | thương vong về người |

### P3. Converter

```python
if number_prefix in ["数", "上", "近", "超过"]:
    classify as approximate_large_number
```

---

## PART Q — Percent / Probability / Success-rate

### Q1. Pattern

```text
成功率百分之八十
概率不到百分之一
几率极低
八成把握
```

### Q2. Rule

```text
成功率百分之八十
→ tỷ lệ thành công 80%

概率不到百分之一
→ xác suất chưa đến 1%

八成把握
→ nắm chắc khoảng 80%
```

---

## PART R — Colloquial Reaction / Meme Chapter Titles

### R1. Pattern

```text
好猛，好爽！
暴打小朋友
你是内奸吧
惊喜原来是
```

### R2. Rule

| ZH | VI |
|---|---|
| `好猛` | mạnh dữ / dữ dội thật |
| `好爽` | đã quá / sướng quá |
| `暴打小朋友` | đánh trẻ con không trượt phát nào / hành trẻ con |
| `你是内奸吧` | ngươi là nội gián đấy à |
| `惊喜原来是` | hóa ra bất ngờ là... |

**Config tone:**

```python
tone_mode = "natural_webnovel"
tone_mode = "formal_translation"
```

---

## PART S — Data files cần bổ sung

```text
data/grammar/
├── space_fleet_suffixes.json
├── polity_faction_suffixes.json
├── auction_price_patterns.json
├── lifeform_grade_patterns.json
├── bio_gene_item_suffixes.json
├── equipment_install_verbs.json
├── navigation_space_terms.json
├── radiation_hazard_terms.json
├── system_upgrade_terms.json
├── probability_risk_terms.json
├── news_public_opinion_terms.json
├── admin_investigation_terms.json
├── bracketed_chapter_title_patterns.json
├── effect_frame_patterns.json
├── material_source_frame_patterns.json
├── large_population_number_patterns.json
└── colloquial_chapter_title_map.json
```

---

## PART T — Implementation Roadmap v17

### Sprint V17-A — Space/Civilization Entity

- [ ] `space_entity_detector.py`
- [ ] `polity_faction_detector.py`
- [ ] `space_fleet_suffixes.json`
- [ ] `polity_faction_suffixes.json`
- [ ] Tests: 80 cases

### Sprint V17-B — Auction/Resource/Price

- [ ] `auction_price_parser.py`
- [ ] `currency_large_number_converter.py`
- [ ] `auction_price_patterns.json`
- [ ] Tests: 80 cases

### Sprint V17-C — Grade/Lifeform/Bio Item

- [ ] `lifeform_grade_classifier.py`
- [ ] `bio_gene_item_parser.py`
- [ ] `equipment_install_rule.py`
- [ ] Tests: 100 cases

### Sprint V17-D — Navigation/Hazard/System Upgrade

- [ ] `navigation_space_rule.py`
- [ ] `radiation_hazard_rule.py`
- [ ] `system_upgrade_rule.py`
- [ ] Tests: 100 cases

### Sprint V17-E — Discourse/Frame Completion

- [ ] `news_public_opinion_rule.py`
- [ ] `admin_investigation_rule.py`
- [ ] `dui_effect_frame_rule.py`
- [ ] `yi_material_source_rule.py`
- [ ] Tests: 100 cases

### Sprint V17-F — Chapter Title / Colloquial

- [ ] `chapter_title_parser.py`
- [ ] `bracketed_title_preserver.py`
- [ ] `colloquial_chapter_title_map.json`
- [ ] Tests: 80 cases

---

## PART U — Test Matrix v17

### U1. Space entity

```python
V17_SPACE_TESTS = [
    ("黑瞳舰队", "Hạm đội Hắc Đồng"),
    ("帝国舰队", "hạm đội Đế Quốc"),
    ("生命星球", "hành tinh có sự sống"),
    ("本菲尔文明之战", "trận chiến văn minh Benfell"),
]
```

### U2. Auction/price

```python
V17_AUCTION_TESTS = [
    ("起拍价为三十亿星币", "giá khởi điểm là 30 tỷ tinh tệ"),
    ("以五千万星币成交", "chốt giao dịch ở mức 50 triệu tinh tệ"),
    ("报价一百万星币", "ra giá 1 triệu tinh tệ"),
]
```

### U3. Lifeform grade

```python
V17_LIFEFORM_TESTS = [
    ("A级生命体", "sinh mệnh thể cấp A"),
    ("两个A级生命体的战斗", "trận chiến của hai sinh mệnh thể cấp A"),
    ("E+级以下的攻击", "công kích từ cấp E+ trở xuống"),
]
```

### U4. Bio item

```python
V17_BIO_ITEM_TESTS = [
    ("病毒原液", "nguyên dịch virus"),
    ("岩狮基因链", "chuỗi gen Sư Tử Đá"),
    ("维罗妮卡模组", "mô-đun Veronica"),
    ("泰坦殖装", "thực trang Titan"),
]
```

### U5. System upgrade

```python
V17_SYSTEM_UPGRADE_TESTS = [
    ("分身实力同步中，需要时间720小时", "đang đồng bộ thực lực phân thân, cần 720 giờ"),
    ("系统将会进行升级", "hệ thống sẽ tiến hành nâng cấp"),
    ("分身回收成功", "thu hồi phân thân thành công"),
]
```

### U6. Effect/material frame

```python
V17_FRAME_TESTS = [
    ("对如今的李宇产生作用", "có tác dụng đối với Lý Vũ hiện nay"),
    ("以破碎母盒作为原材料打造", "lấy Hộp Mẹ vỡ làm nguyên liệu để chế tạo"),
]
```

### U7. Large casualty

```python
V17_POPULATION_NUMBER_TESTS = [
    ("超过千万级别的人员伤亡", "thương vong vượt mức hàng chục triệu người"),
    ("近百艘战舰", "gần trăm chiến hạm"),
]
```

### U8. Chapter title

```python
V17_TITLE_TESTS = [
    ("第101章 【漫威】世界", "Chương 101: Thế giới [Marvel]"),
    ("第106章 【黯星】和帝国舰队", "Chương 106: [Ám Tinh] và Hạm đội Đế Quốc"),
    ("第197章 好猛，好爽！", "Chương 197: Mạnh dữ, đã quá!"),
]
```

---

## PART V — Rule Priority cập nhật sau v17

```text
P00 ProtectedSpanEngine
P02 SystemPanelParser
P03 ChapterTitleParser
P04 AuthorNoteFilter
P05 CrossWorldEntityDetector
P06 Space/Civilization Entity Detector
P07 AlphanumericGradeGuard
P08 LifeformGradeClassifier
P09 Tech/Bio/Equipment Entity Parser
P10 ClauseSplitter
P20 Core Grammar / v15 rules
P30 SystemRewardRule
P35 SystemUpgradeRule
P40 GradeRankConverter
P45 AuctionPriceParser
P50 TimeFlowRatioConverter
P55 NavigationSpaceRule
P60 Currency/ResourceNumberConverter
P65 LargePopulationNumberConverter
P70 TechProductRealizer
P75 BioItemRealizer
P80 ColloquialTone/EAPEE Extension
P90 SFXPreserver
P99 Postprocess
```

---

## PART W — Acceptance Metrics v17

| Metric | Target |
|---|---:|
| Existing v14–v16 tests | 100% pass |
| Space entity protection | ≥ 97% |
| Civilization/faction detection | ≥ 95% |
| Auction/price grammar | ≥ 95% |
| Lifeform grade conversion | ≥ 98% |
| Bio/gene item protection | ≥ 97% |
| Equipment install grammar | ≥ 92% |
| Navigation/coordinate expressions | ≥ 92% |
| Radiation/hazard grammar | ≥ 92% |
| System upgrade grammar | ≥ 98% |
| Large casualty number conversion | ≥ 95% |
| Chapter title parser | ≥ 99% |
| No crash on chapters 101–200 | 100% |

---

## PART X — Merge Strategy

v17 là **domain expansion** tiếp theo của v16. Không thay thế v15/v16.

- v15 = deep general grammar completion.
- v16 = system/sci-fi/game foundation for new story chapters 1–100.
- v17 = space-war/civilization/auction/high-tech expansion for chapters 101–200.

Khi merge vào master plan:
1. Giữ `SystemPanelParser` từ v16.
2. Thêm `ChapterTitleParser` chạy sớm hơn entity parser.
3. Mở rộng entity ontology từ sci-fi item sang space polity/fleet.
4. Thêm parser cho auction/price và casualty statistics.
5. Thêm high-tech biological item chain.
6. Mở rộng number converter theo context: currency, grade, lifeform, casualty, probability.

---

## END OF v17


---

# PART III — v18 Full Content: Chapters 201–400

**Repo:** `converter-drduc`  
**Kế thừa:** `v14 + v15 + v16 + v17`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 201–400  
**Ngày:** 2026-04-25  
**Phiên bản:** v18.0 — Ch201–400 Grammar + Named-Entity Scanner Completion  

---

### 0. Executive Summary

Sau v17, thuật toán đã có nền cho:

- System panel/log.
- Sci-fi/game entity.
- Grade/rank/lifeform.
- Space fleet/faction/civilization.
- Auction/price/currency.
- Bio/gene/module/equipment.
- System upgrade/sync.
- Chapter title parser.

Khi quét tiếp **chương 201–400**, corpus mở rộng mạnh sang các nhánh mới:

1. **Hành tinh/chủng tộc/quân đoàn**
   - `巨魔星`, `巨魔族`, `巨魔军团`, `四血巨魔`, `五血屠英`.
2. **Liên minh/thế lực/văn minh nhiều tầng**
   - `星耀帝国`, `紫晶文明`, `黯星议会`, `异维度研究营地`, `救世方舟`, `变革者`, `补完舰队`.
3. **Franchise/cross-world entity dày hơn**
   - Marvel, Superman, Star Wars, Transformers: `超人世界`, `无限原石`, `凯伯水晶`, `原力`, `千年隼号`, `死星`.
4. **Future/time/reality grammar**
   - `窥探未来`, `未来层面的交锋`, `过去的阴影`, `未来？过去`, `阴差阳错`.
5. **Power-scale và energy taxonomy**
   - `A5层次`, `超级生命体`, `能级划分`, `红莲状态`, `属神`, `神格雏形`.
6. **Gene/evolution/soul/data transformation**
   - `基因优化`, `灵肉合一蜕变`, `二次进化`, `数据化`, `数字灵魂`.
7. **Strategy/conspiracy/negotiation language**
   - `各方算计`, `多层博弈`, `暗流涌动`, `紧急会议`, `谈判契机`, `招揽`, `调令`.
8. **Internet meme / khẩu ngữ tiêu đề**
   - `上来就开大`, `风雨又双叒叕欲来啦`, `干一炮就跑？`, `主宰竟是我自己？`, `套娃`.
9. **Tên riêng ngắn, alias, title + name**
   - `泰塔斯`, `多诺万`, `埃尔顿`, `荷鲁斯`, `霖克`, `古斯特`, `撒斯特`, `维玛拉`, `阿列克谢`, `科尔森`.

Bản v18 bổ sung 22 nhóm thuật toán mới:

```text
V18-GAP-01  Planet/race/legion scanner
V18-GAP-02  Bloodline-count race title: 四血/五血 + race/person
V18-GAP-03  Power-layer classifier: A5层次, 能级, 超级生命体
V18-GAP-04  Future/past/time-line grammar
V18-GAP-05  Cross-franchise artifact scanner: 无限原石/凯伯水晶/千年隼号/死星
V18-GAP-06  Force/faith/divinity system: 原力/信仰/神格/属神
V18-GAP-07  Evolution/transformation grammar: 蜕变/数据化/二次进化/灵肉合一
V18-GAP-08  Strategy/conspiracy discourse: 算计/博弈/暗流/风波/序幕
V18-GAP-09  Meeting/order/mission admin grammar: 调令/召见/招揽/提交/汇报
V18-GAP-10  Bounty/wanted/external announcement: 悬赏/通缉/对外悬赏
V18-GAP-11  Bug/exploit/system loophole grammar: 卡bug/刷脸/光速完成任务
V18-GAP-12  Meme title / internet slang parser
V18-GAP-13  Nested bracket item title parser
V18-GAP-14  Entity scanner: short transliterated personal names
V18-GAP-15  Entity scanner: alias-title fusion
V18-GAP-16  Entity scanner: organization/faction hierarchy
V18-GAP-17  Entity scanner: tech/artifact blueprint names
V18-GAP-18  Entity scanner: world/franchise terms
V18-GAP-19  Proper noun confidence scoring + first-seen memory
V18-GAP-20  Pronoun/coreference tied to entity memory
V18-GAP-21  Domain-aware Han-Viet/transliteration policy
V18-GAP-22  Chapter-title-derived glossary seeding
```

---

### 1. Corpus Signals chương 201–400

#### 1.1 Chapter title signals

Các tiêu đề từ chương 201–400 cho thấy những miền cần mở rộng:

```text
第201章 巨魔星见闻
第205章 佩顿的方法，五血屠英！
第210章 罗德的邀请，加入紫晶？
第212章 黯星议会的奸商都该死！
第214章 突如其来的掠夺者舰队
第224章 异纬度研究营地
第231章 定制武器，弥补不足
第241章 星际标题党
第246章 【钢铁侠的装备升级卡】以及【氪星...】
第251章 【使徒】？
第255章 陨星舰队降临，意料之外的敌人
第265章 【蜘蛛感应】与A级生命体！
第267章 能级划分
第278章 【火种源碎片】
第291章 【泰坦殖装】和【使徒】的联动
第300章 【超人世界】
第306章 系统升级 新的世界与功能
第316章 凯伯水晶
第333章 【千年隼号】以及【窥探未来】
第345章 绝地与西斯
第358章 重返漫威，无限原石
第370章 【死星闪耀】 未来层面的交锋
第389章 【特殊图纸死星】
第390章 【荣耀星路】
第397章 泰塔斯发难，光速完成任务的一号
第398章 数据化
```

#### 1.2 High-frequency construction signals

Trên vùng chương 201–400, các token có tần suất cao cho thấy rule cần ưu tiên:

```text
对 / 以 / 而 / 为 / 之 / 被 / 让 / 并 / 成 / 所
不是 / 而是 / 并非
A级 / B级 / A5 / 能级 / 生命体
归星 / 紫晶 / 星耀帝国 / 巨魔 / 舰队 / 文明
基因 / 殖装 / 装甲 / 能量 / 护盾 / 网络
调令 / 招揽 / 召见 / 会议 / 汇报 / 悬赏
未来 / 过去 / 窥探 / 时间限制 / 数据化
```

---

## PART A — Planet / Race / Legion Scanner

### A1. Vấn đề

Các cụm như:

```text
巨魔星
巨魔族
巨魔军团
半鱼
炽眼族
归星
鄂多斯星系
恒丰星系
琉星
```

không thể dùng một rule danh ngữ chung. Cần tách:

- Planet/place.
- Race/species.
- Legion/military unit.
- Star system.
- Individual nickname.

### A2. Ontology

```json
{
  "planet_suffix": ["星", "星球", "母星", "归星"],
  "star_system_suffix": ["星系", "星域", "星区"],
  "race_suffix": ["族", "生命体", "异形", "巨魔", "半鱼"],
  "legion_suffix": ["军团", "舰队", "部队", "小队", "营地"],
  "military_title": ["指挥官", "副官", "议长", "议员", "军团长"]
}
```

### A3. Rules

```python
if span.endswith("星") and len(span) <= 6:
    classify PLACE_PLANET
elif span.endswith("星系"):
    classify PLACE_STAR_SYSTEM
elif span.endswith("族") or span in known_species:
    classify SPECIES
elif span.endswith(("军团", "舰队")):
    classify MILITARY_GROUP
```

### A4. Translation examples

```text
巨魔星        → hành tinh Cự Ma
巨魔族        → tộc Cự Ma
巨魔军团      → Quân đoàn Cự Ma
归星          → Quy Tinh / hành tinh Quy
鄂多斯星系    → tinh hệ Eddos / Ngạc Đa Tư
陨星舰队      → Hạm đội Vẫn Tinh
```

---

## PART B — Bloodline-count Race Title

### B1. Pattern

```text
四血巨魔
五血屠英
三血巨魔
血脉属性数量
```

### B2. Meaning

Trong corpus này, `四血/五血` là cấp huyết mạch hoặc số thuộc tính huyết mạch, không phải “bốn máu” literal.

### B3. Rule

```python
Pattern: [NUM]血 + [RACE/PERSON/TITLE]
→ [RACE/PERSON/TITLE] [NUM] huyết / cấp [NUM] huyết
```

### B4. Examples

```text
四血巨魔
→ Cự Ma tứ huyết

五血屠英
→ Đồ Anh ngũ huyết

血脉属性数量
→ số lượng thuộc tính huyết mạch
```

**Config:**

```python
bloodline_style = "hanviet"  # tứ huyết, ngũ huyết
bloodline_style = "plain"    # bốn huyết, năm huyết
```

---

## PART C — Power Layer / Energy Level Classifier

### C1. Patterns

```text
A级生命体
B级精神力
A5层次
能级划分
超级生命体
属神
神格雏形
红莲状态
赛亚状态
```

### C2. Rule types

| Pattern | Type | VI |
|---|---|---|
| `A级生命体` | lifeform grade | sinh mệnh thể cấp A |
| `B级精神力` | stat grade | tinh thần lực cấp B |
| `A5层次` | sub-grade layer | tầng A5 / cấp độ A5 |
| `能级划分` | power taxonomy | phân chia năng cấp |
| `超级生命体` | super lifeform | sinh mệnh thể siêu cấp |
| `属神` | subordinate god | thuộc thần |
| `神格雏形` | divine spark prototype | hình thức sơ khai của thần cách |
| `红莲状态` | transformation state | trạng thái Hồng Liên |
| `赛亚状态` | Saiyan state | trạng thái Saiya |

### C3. Algorithm

```python
if re.match(r"[SABCDEF][+\-]?\d?层次", span):
    classify POWER_LAYER
elif re.match(r"[SABCDEF][+\-]?级", span):
    classify GRADE_RANK
elif span.endswith("状态"):
    classify FORM_STATE
elif span in ["属神", "神格雏形"]:
    classify DIVINITY_SYSTEM
```

---

## PART D — Future / Past / Timeline Grammar

### D1. Patterns

```text
未来？过去
窥探未来
未来层面的交锋
过去的阴影
时间限制
阴差阳错
```

### D2. Rule mapping

| ZH | VI |
|---|---|
| `窥探未来` | nhìn trộm tương lai / dòm ngó tương lai |
| `未来层面的交锋` | giao phong ở tầng diện tương lai |
| `过去的阴影` | bóng ma của quá khứ |
| `时间限制` | giới hạn thời gian |
| `阴差阳错` | trớ trêu thay / tình cờ sai lệch |
| `未来？过去` | tương lai? quá khứ? |

### D3. Timeline expression parser

```python
TIMELINE_TERMS = {
    "未来": "tương lai",
    "过去": "quá khứ",
    "现在": "hiện tại",
    "时间线": "dòng thời gian",
    "时间限制": "giới hạn thời gian",
    "时间节点": "mốc thời gian",
    "窥探未来": "nhìn trộm tương lai",
}
```

### D4. Protection

Các cụm như `窥探未来` có thể là item/ability trong bracket:

```text
【窥探未来】
```

Nếu nằm trong `【...】`, protect as ability/item name.

---

## PART E — Cross-Franchise Artifact Scanner

### E1. Artifacts/world terms xuất hiện

```text
【钢铁侠的装备升级卡】
【氪星...】
【蜘蛛感应】
【火种源碎片】
【超人世界】
凯伯水晶
绝地
西斯
千年隼号
无限原石
死星
【特殊图纸死星】
【荣耀星路】
原力
原力附魔
```

### E2. Entity classes

```json
{
  "marvel": ["钢铁侠", "蜘蛛感应", "无限原石", "科尔森"],
  "dc": ["超人世界", "氪星"],
  "star_wars": ["凯伯水晶", "绝地", "西斯", "千年隼号", "死星", "原力"],
  "transformers": ["火种源碎片", "原始天尊"],
  "system_item": ["装备升级卡", "特殊图纸", "荣耀星路"]
}
```

### E3. Translation policy

| ZH | VI |
|---|---|
| `钢铁侠的装备升级卡` | thẻ nâng cấp trang bị của Iron Man |
| `蜘蛛感应` | Spider-Sense / cảm ứng Nhện |
| `火种源碎片` | mảnh vỡ AllSpark |
| `超人世界` | thế giới Superman |
| `凯伯水晶` | tinh thể Kyber |
| `绝地` | Jedi |
| `西斯` | Sith |
| `千年隼号` | Millennium Falcon |
| `无限原石` | Viên đá Vô Cực |
| `死星` | Death Star |
| `原力` | Thần Lực / Force |

### E4. Scanner rule

```python
if span in franchise_glossary:
    protect_as_cross_franchise_entity()
elif bracketed and contains known franchise suffix:
    protect_as_system_item()
```

---

## PART F — Force / Faith / Divinity System

### F1. Patterns

```text
窃取信仰
虚拟信仰
神名
神格雏形
属神
降神
战神子
原力种子
原力附魔
```

### F2. Translation

| ZH | VI |
|---|---|
| `窃取信仰` | đánh cắp tín ngưỡng |
| `虚拟信仰` | tín ngưỡng ảo |
| `神名` | thần danh |
| `神格雏形` | hình thức sơ khai của thần cách |
| `属神` | thuộc thần |
| `降神` | thần giáng / giáng thần |
| `战神子` | Chiến Thần Tử |
| `原力种子` | hạt giống Force / hạt giống Nguyên Lực |
| `原力附魔` | phụ ma bằng Force / Nguyên Lực phụ ma |

### F3. Rule

```python
if token in DIVINITY_TERMS:
    protect_domain_term()
    use divinity glossary
```

---

## PART G — Evolution / Transformation / Datafication Grammar

### G1. Patterns

```text
基因优化
灵肉合一蜕变开始
蜕变结束
二次进化
数据化
数字灵魂
前身的秘密
生命法典
强化异形母皇
```

### G2. Rule mapping

| ZH | VI |
|---|---|
| `基因优化` | tối ưu gen |
| `灵肉合一` | linh nhục hợp nhất |
| `蜕变开始` | bắt đầu lột xác/biến đổi |
| `蜕变结束` | biến đổi kết thúc |
| `二次进化` | tiến hóa lần hai |
| `数据化` | dữ liệu hóa |
| `数字灵魂` | linh hồn số |
| `生命法典` | pháp điển sinh mệnh / Life Codex |
| `强化异形母皇` | cường hóa Dị Hình Mẫu Hoàng |

### G3. Grammar

```text
X 开始 / X 结束
→ X bắt đầu / X kết thúc

进行 X
→ tiến hành X

完成 X
→ hoàn thành X
```

### G4. State-machine handling

Nếu nằm trong system panel:

```text
【数据化中...】
→ 【Đang dữ liệu hóa...】
```

Nếu là chapter title:

```text
第398章 数据化
→ Chương 398: Dữ liệu hóa
```

---

## PART H — Strategy / Conspiracy / Political Discourse

### H1. Patterns

```text
各方算计
多层博弈
暗流涌动
风波骤起
序幕拉开
局势诡谲
意料之外
螳螂捕蝉
黄雀在后
```

### H2. Translation

| ZH | VI |
|---|---|
| `各方算计` | các bên tính toán |
| `多层博弈` | cuộc博弈 nhiều tầng / thế cờ nhiều lớp |
| `暗流涌动` | sóng ngầm cuộn trào |
| `风波骤起` | phong ba đột khởi |
| `序幕拉开` | màn mở đầu kéo ra |
| `局势诡谲` | cục diện quỷ quyệt/khó lường |
| `意料之外` | ngoài dự liệu |
| `螳螂捕蝉` | bọ ngựa bắt ve |
| `黄雀在后` | chim sẻ ở phía sau |

### H3. Idiom guard

```python
STRATEGY_IDIOM_GUARD = [
    "螳螂捕蝉", "黄雀在后", "暗流涌动", "风雨欲来",
    "风雨又双叒叕欲来", "阴差阳错", "多层博弈"
]
```

---

## PART I — Meeting / Order / Mission Administration Grammar

### I1. Patterns

```text
调令
邀请
加入
召见
招揽
提交
汇报
紧急会议
上门
发难
前往
重返
返回基地
```

### I2. Translation mapping

| ZH | VI |
|---|---|
| `调令` | lệnh điều động |
| `邀请` | lời mời |
| `加入` | gia nhập |
| `召见` | triệu kiến |
| `招揽` | chiêu mộ |
| `提交` | nộp / đệ trình |
| `汇报` | báo cáo |
| `紧急会议` | hội nghị khẩn cấp |
| `上门` | đến tận cửa |
| `发难` | làm khó / ra tay chất vấn |
| `前往` | đi đến |
| `重返` | trở lại |
| `返回基地` | quay về căn cứ |

### I3. Administrative frame

```text
X 的调令
→ lệnh điều động của X

Y 召见 X
→ Y triệu kiến X

提交病毒疫苗
→ nộp vaccine virus

紧急会议，倒霉的荷鲁斯
→ hội nghị khẩn cấp, Horus xui xẻo
```

---

## PART J — Bounty / Wanted / External Announcement

### J1. Patterns

```text
对外悬赏
悬赏
通缉
声明
公告
对外公布
消息传出
星际标题党
```

### J2. Translation

| ZH | VI |
|---|---|
| `对外悬赏` | treo thưởng ra bên ngoài |
| `悬赏` | treo thưởng |
| `通缉` | truy nã |
| `声明` | tuyên bố |
| `公告` | thông cáo |
| `对外公布` | công bố ra bên ngoài |
| `消息传出` | tin tức truyền ra |
| `星际标题党` | giật tít liên sao |

### J3. Rule

```python
if 对外 + [公布/悬赏/声明]:
    output = V_vi + " ra bên ngoài"
```

---

## PART K — Bug / Exploit / System Loophole Grammar

### K1. Patterns

```text
卡到了bug
刷脸
光速完成任务
系统升级
新的世界与功能
套娃
```

### K2. Mapping

| ZH | VI |
|---|---|
| `卡到了bug` | bắt được bug / kẹt được bug |
| `刷脸` | quét mặt / dùng mặt để qua cửa |
| `光速完成任务` | hoàn thành nhiệm vụ với tốc độ ánh sáng |
| `系统升级` | hệ thống nâng cấp |
| `新的世界与功能` | thế giới và chức năng mới |
| `套娃` | búp bê lồng nhau / lồng tầng lặp tầng |

### K3. Rule

Tách domain:

- Nếu trong system context: `bug` giữ nguyên “bug”.
- Nếu văn kể hài: `卡bug` → “lợi dụng bug”.
- Nếu title: giữ phong cách meme.

---

## PART L — Meme Title / Internet Slang Parser

### L1. Title patterns

```text
可恶的熊孩子
隔夜饭糊脸
上来就开大
风雨又双叒叕欲来啦
老子的枪又回来了？
主宰竟是我自己？
干一炮就跑？
烂俗的桥段
懵逼的埃尔顿
```

### L2. Mapping policy

| ZH | Natural VI |
|---|---|
| `熊孩子` | nhóc quỷ |
| `隔夜饭糊脸` | cơm nguội qua đêm úp vào mặt |
| `上来就开大` | vừa vào đã tung chiêu cuối |
| `又双叒叕` | lại-lại-lại nữa |
| `老子的枪又回来了？` | súng của ông đây lại quay về rồi? |
| `主宰竟是我自己？` | hóa ra Chúa Tể lại là chính ta? |
| `干一炮就跑？` | bắn một phát rồi chạy? |
| `烂俗的桥段` | tình tiết cũ rích |
| `懵逼的埃尔顿` | Elton ngơ ngác |

### L3. Rule

```python
if line_is_chapter_title and contains_slang_or_meme:
    use title_slang_map
else:
    use normal grammar transfer
```

---

## PART M — Nested Bracket Item Title Parser

### M1. Patterns

```text
【钢铁侠的装备升级卡】以及【氪星...】
【泰坦殖装】和【使徒】的联动
【千年隼号】以及【窥探未来】
【死星闪耀】 未来层面的交锋
【特殊图纸死星】
【荣耀星路】
```

### M2. Rule

```python
parse_bracket_items(line):
    items = collect_all("【...】")
    protect each item
    parse connector between items: 以及/和/与
```

### M3. Examples

```text
【泰坦殖装】和【使徒】的联动
→ sự liên động giữa [Thực Trang Titan] và [Sứ Đồ]

【千年隼号】以及【窥探未来】
→ [Millennium Falcon] và [Nhìn Trộm Tương Lai]
```

---

## PART N — Proper Name Scanner v18

### N1. Mục tiêu

Hoàn thiện thuật toán quét tên riêng cho các loại sau:

1. Nhân vật Hán phiên âm.
2. Alias/nghề nghiệp/chức danh.
3. Thế lực/văn minh/quân đoàn.
4. Hành tinh/tinh hệ/địa danh.
5. Vật phẩm hệ thống/bracket item.
6. Artifact/franchise.
7. Kỹ năng/trạng thái/ability.
8. Công nghệ/vũ khí/tàu/giáp.
9. Sự kiện/trận chiến.
10. Meme/title phrase.

### N2. Personal name candidates chương 201–400

```text
佩顿
罗德
克莱因
荷鲁斯
泰塔斯
简斯
汉内斯
洛汗
霖克
克瑞
布鲁克斯
古斯特
撒斯特
科尔森
维玛拉
阿列克谢
埃尔顿
多诺万
索利
蒂戈尔
奥利维亚
马克斯
泰德
```

### N3. Alias/title candidates

```text
黯星
猎人
小吵闹
使徒
占星者
救世方舟
主宰
战神子
第一任女王
抓李专家多诺万
```

### N4. Faction/entity candidates

```text
星耀帝国
紫晶文明
黯星议会
巨魔军团
异维度研究营地
救世方舟
补完舰队
陨星舰队
变革者
金壁银行
归星
鄂多斯星系
恒丰星系
琉星
```

### N5. Artifact/ability candidates

```text
泰坦殖装
使徒
钢铁侠的装备升级卡
氪星相关 item
蜘蛛感应
火种源碎片
原始天尊
原力种子
凯伯水晶
千年隼号
窥探未来
无限原石
死星闪耀
特殊图纸死星
荣耀星路
原力附魔
生命法典
```

### N6. Scanner stages

```text
Stage 0: ChapterTitle seeding
Stage 1: BracketItem extraction
Stage 2: Known glossary exact match
Stage 3: Suffix ontology match
Stage 4: Short-name transliteration candidate
Stage 5: Repetition + syntactic role scoring
Stage 6: Alias/coreference linking
Stage 7: Confidence threshold + review export
```

### N7. Confidence scoring

```python
score = 0

if in_bracket: score += 5
if appears_in_chapter_title: score += 4
if in_known_glossary: score += 5
if suffix_in_entity_ontology: score += 3
if appears_as_subject_or_dialogue_speaker: score += 2
if repeated_count >= 3: score += 2
if preceded_by_title_or_followed_by_said: score += 2
if contains_grade_or_number_inside_known_item: score += 2
if single_common_word_without_context: score -= 3
if overlaps_with_normal_grammar_function_word: score -= 4
```

Threshold:

```python
score >= 7  -> auto protect
score 4-6   -> candidate, protect if no conflict
score <= 3  -> leave to normal tokenizer
```

### N8. Short transliterated names

Pattern:

```python
TRANSLIT_NAME_RE = r"^[\u4e00-\u9fff]{2,4}$"
```

But only if:
- repeated ≥ 3 times, or
- appears near `说/道/问/看向/摇头/皱眉`, or
- appears in chapter title.

Examples:

```text
泰塔斯
多诺万
埃尔顿
维玛拉
阿列克谢
```

### N9. Alias linking

```python
if "抓李专家多诺万":
    alias_title = "抓李专家"
    name = "多诺万"
    add_alias(name, alias_title + name)

if "黯星议会":
    entity = "黯星议会"
    alias base = "黯星"  # but mark conflict: 黯星 can be person/title/faction keyword
```

---

## PART O — Organization/Faction Hierarchy Scanner

### O1. Problem

`紫晶` có thể là civilization/faction, còn `紫晶文明` là full entity. `黯星` có thể là person/title/faction root. `星耀帝国` là polity.

### O2. Hierarchy model

```python
@dataclass
class EntityRecord:
    canonical: str
    aliases: list[str]
    entity_type: str
    parent: str | None
    confidence: float
```

### O3. Examples

```json
{
  "紫晶文明": {
    "aliases": ["紫晶"],
    "type": "civilization"
  },
  "黯星议会": {
    "aliases": ["黯星"],
    "type": "council/faction"
  },
  "巨魔军团": {
    "aliases": ["巨魔"],
    "type": "legion",
    "parent": "巨魔族"
  }
}
```

### O4. Conflict resolver

```python
if alias maps to multiple entity records:
    use local suffix/context:
      黯星议会 -> faction
      黯星说/黯星看向 -> person/title
      黯星舰队 -> fleet/faction
```

---

## PART P — Domain-aware Transliteration Policy

### P1. Personal names

Default:
- Chinese transliteration to Hán Việt if known.
- Foreign-sounding transliteration optionally use Latin-like if glossary.

```text
泰塔斯 → Titus / Thái Tháp Tư
多诺万 → Donovan / Đa Nặc Vạn
科尔森 → Coulson / Khoa Nhĩ Sâm
阿列克谢 → Alexei / A Liệt Khắc Tạ
埃尔顿 → Elton / Ai Nhĩ Đốn
```

### P2. Config

```python
name_style = "hanviet"
name_style = "latin_if_franchise"
name_style = "mixed"
```

Recommended for this story:

```python
name_style = "mixed"
franchise_names_latin = True
original_xianxia_names_hanviet = True
```

### P3. Entity class based policy

| Type | Policy |
|---|---|
| Chinese original character | Hán Việt |
| Western/franchise character | Latin common name |
| System item | glossary preferred |
| Faction/civilization | Hán Việt + glossary |
| Place/planet | Hán Việt or transliteration stable |
| Tech product | semantic translation + protected proper prefix |

---

## PART Q — Core grammar gaps newly emphasized

### Q1. `上来就 + V`

```text
上来就开大
→ vừa vào đã tung chiêu cuối
```

Rule:

```python
上来就 + VP -> vừa bắt đầu đã + VP
```

### Q2. `一上来就 + V`

```text
一上来就开打
→ vừa lên đã đánh
```

### Q3. `终于卡到了bug`

```text
终于 + V
→ cuối cùng cũng + V

卡到bug
→ bắt/lợi dụng được bug
```

### Q4. `原来 X 都是 Y`

```text
原来大家都是内奸
→ hóa ra mọi người đều là nội gián
```

### Q5. `竟然是你 / 是他，就是他`

```text
竟然是你
→ hóa ra lại là ngươi

是他，就是他
→ là hắn, chính là hắn
```

### Q6. `拿下 / 镇压`

```text
拿下，镇压
→ bắt giữ, trấn áp
```

If combat:
- `拿下` → hạ/bắt lấy.
If political:
- `拿下 X` → giành được X.

---

## PART R — New Data Files

```text
data/grammar/
├── planet_race_legion_suffixes.json
├── bloodline_race_patterns.json
├── power_layer_patterns.json
├── timeline_future_past_terms.json
├── franchise_artifact_glossary.json
├── divinity_force_terms.json
├── evolution_datafication_terms.json
├── strategy_idiom_guard.txt
├── admin_mission_terms.json
├── bounty_announcement_terms.json
├── bug_exploit_terms.json
├── meme_title_map.json
├── nested_bracket_item_patterns.json
├── personal_name_translit_candidates.json
├── faction_hierarchy_patterns.json
├── entity_confidence_weights.json
└── domain_transliteration_policy.json
```

---

## PART S — Implementation Roadmap v18

### Sprint V18-A — Chapter title + bracket glossary seeding

- [ ] `ChapterTitleEntitySeeder`
- [ ] Extract bracket items from chapter titles.
- [ ] Extract non-bracket title proper nouns.
- [ ] Seed entity memory before body translation.
- [ ] Tests: 80 cases.

### Sprint V18-B — Planet/Race/Faction hierarchy

- [ ] `PlanetRaceLegionScanner`
- [ ] `FactionHierarchyResolver`
- [ ] `BloodlineRaceTitleRule`
- [ ] Tests: 100 cases.

### Sprint V18-C — Franchise artifact and ability scanner

- [ ] `FranchiseArtifactScanner`
- [ ] `CrossWorldAbilityScanner`
- [ ] `NestedBracketItemParser`
- [ ] Tests: 120 cases.

### Sprint V18-D — Power/evolution/datafication grammar

- [ ] `PowerLayerClassifier`
- [ ] `EvolutionTransformationRule`
- [ ] `DataficationRule`
- [ ] `DivinityForceRule`
- [ ] Tests: 120 cases.

### Sprint V18-E — Strategy/admin/announcement grammar

- [ ] `StrategyDiscourseRule`
- [ ] `AdminMissionRule`
- [ ] `BountyAnnouncementRule`
- [ ] `BugExploitRule`
- [ ] Tests: 120 cases.

### Sprint V18-F — Proper-name scanner completion

- [ ] Confidence scoring.
- [ ] Short transliteration detection.
- [ ] Alias linking.
- [ ] Entity hierarchy memory.
- [ ] Export review file for low-confidence entities.
- [ ] Tests: 150 cases.

---

## PART T — Test Matrix v18

### T1. Planet/race/legion

```python
V18_PLANET_RACE_TESTS = [
    ("巨魔星", "hành tinh Cự Ma"),
    ("巨魔族", "tộc Cự Ma"),
    ("巨魔军团", "Quân đoàn Cự Ma"),
    ("鄂多斯星系", "tinh hệ Eddos"),
]
```

### T2. Bloodline

```python
V18_BLOODLINE_TESTS = [
    ("四血巨魔", "Cự Ma tứ huyết"),
    ("五血屠英", "Đồ Anh ngũ huyết"),
    ("血脉属性数量", "số lượng thuộc tính huyết mạch"),
]
```

### T3. Power layer

```python
V18_POWER_TESTS = [
    ("A5层次", "tầng A5"),
    ("B级精神力", "tinh thần lực cấp B"),
    ("超级生命体", "sinh mệnh thể siêu cấp"),
    ("神格雏形", "hình thức sơ khai của thần cách"),
]
```

### T4. Franchise artifact

```python
V18_FRANCHISE_TESTS = [
    ("【蜘蛛感应】", "[Spider-Sense]"),
    ("【火种源碎片】", "[mảnh vỡ AllSpark]"),
    ("凯伯水晶", "tinh thể Kyber"),
    ("千年隼号", "Millennium Falcon"),
    ("无限原石", "Viên đá Vô Cực"),
    ("【特殊图纸死星】", "[bản vẽ đặc biệt Death Star]"),
]
```

### T5. Evolution/datafication

```python
V18_EVOLUTION_TESTS = [
    ("基因优化", "tối ưu gen"),
    ("灵肉合一蜕变开始", "bắt đầu linh nhục hợp nhất và biến đổi"),
    ("二次进化", "tiến hóa lần hai"),
    ("数据化", "dữ liệu hóa"),
]
```

### T6. Strategy/admin

```python
V18_STRATEGY_TESTS = [
    ("各方算计", "các bên tính toán"),
    ("多层博弈", "thế cờ nhiều lớp"),
    ("紧急会议", "hội nghị khẩn cấp"),
    ("对外悬赏", "treo thưởng ra bên ngoài"),
]
```

### T7. Meme title

```python
V18_MEME_TITLE_TESTS = [
    ("上来就开大", "vừa vào đã tung chiêu cuối"),
    ("风雨又双叒叕欲来啦", "phong ba lại-lại-lại nữa sắp đến rồi"),
    ("主宰竟是我自己？", "hóa ra Chúa Tể lại là chính ta?"),
    ("干一炮就跑？", "bắn một phát rồi chạy?"),
]
```

### T8. Proper name scanner

```python
V18_NAME_SCANNER_TESTS = [
    ("泰塔斯", "PERSON"),
    ("多诺万", "PERSON"),
    ("阿列克谢", "PERSON"),
    ("维玛拉", "PERSON"),
    ("星耀帝国", "POLITY"),
    ("紫晶文明", "CIVILIZATION"),
    ("异维度研究营地", "ORGANIZATION"),
    ("金壁银行", "ORGANIZATION"),
]
```

---

## PART U — Rule Priority cập nhật sau v18

```text
P00 ProtectedSpanEngine
P01 ChapterTitleEntitySeeder
P02 SystemPanelParser
P03 ChapterTitleParser
P04 AuthorNoteFilter
P05 BracketItemExtractor
P06 CrossWorldEntityDetector
P07 Planet/Race/Faction Scanner
P08 FactionHierarchyResolver
P09 AlphanumericGradeGuard
P10 PowerLayerClassifier
P11 Tech/Bio/Equipment/Artifact Entity Parser
P12 ProperNameConfidenceScorer
P13 ClauseSplitter
P20 Core Grammar / v15 rules
P30 SystemRewardRule
P35 SystemUpgradeRule
P40 GradeRankConverter
P45 AuctionPriceParser
P50 TimeFlowRatioConverter
P55 NavigationSpaceRule
P60 Currency/ResourceNumberConverter
P65 LargePopulationNumberConverter
P70 Evolution/DataficationRule
P75 Strategy/Admin/AnnouncementRules
P80 ColloquialTone/EAPEE Extension
P90 SFXPreserver
P99 Postprocess
```

---

## PART V — Acceptance Metrics v18

| Metric | Target |
|---|---:|
| Existing v14–v17 tests | 100% pass |
| Chapter-title entity seeding | ≥ 98% |
| Planet/race/legion scanner | ≥ 96% |
| Bloodline race title conversion | ≥ 95% |
| Power layer classifier | ≥ 97% |
| Franchise artifact scanner | ≥ 98% |
| Evolution/datafication grammar | ≥ 94% |
| Strategy/admin discourse | ≥ 90% |
| Meme title translation | sampled ≥ 90% |
| Short personal-name scanner precision | ≥ 92% |
| Entity alias linking | ≥ 90% |
| No crash on chapters 201–400 | 100% |

---

## PART W — Merge Strategy

v18 là domain expansion tiếp theo của v16/v17:

- v16: system/sci-fi/game foundation, chương 1–100.
- v17: space-war/civilization/auction/high-tech, chương 101–200.
- v18: planet/race/faction hierarchy, franchise artifact, timeline/future, power/evolution/datafication, proper-name scanner completion, chương 201–400.

Khi merge vào master plan:

1. Đưa `ChapterTitleEntitySeeder` lên trước parser chính.
2. Mở rộng entity ontology để bao phủ planet/race/legion/faction/franchise.
3. Mở rộng system item scanner để xử lý nested bracket items trong tiêu đề.
4. Thêm confidence scoring cho tên riêng ngắn.
5. Thêm alias hierarchy resolver cho `紫晶`, `黯星`, `巨魔`.
6. Mở rộng number/rank converter cho `A5层次`, `四血/五血`, `能级`.
7. Thêm meme title mode cho tiêu đề chương và thoại khẩu ngữ.

---

## END OF v18


---

# PART IV — v19 Full Content: Chapters 401–600

**Repo:** `converter-drduc`  
**Kế thừa:** `v14 + v15 + v16 + v17 + v18`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 401–600  
**Ngày:** 2026-04-25  
**Phiên bản:** v19.0 — Cosmic Artifact / Faction War / Symbiote-BioTech / Name Scanner Completion  

---

### 0. Executive Summary

Bản v18 đã hoàn thiện lớp quét tên riêng cho chương 201–400: planet/race/faction hierarchy, franchise artifact, timeline, power/evolution/datafication, proper-name confidence scoring.

Khi quét tiếp **chương 401–600**, corpus chuyển sang giai đoạn **chiến tranh liên sao + artifact vũ trụ + faction war + sinh thể/công nghệ cộng sinh + Marvel/Transformers/Star Wars/Warhammer-style mixed universe**.

Các tín hiệu nổi bật trong vùng chương này:

```text
第401章 暗流涌动
第406章 【无限手套】与【力量宝石】
第415章 进度条堆满的【死星】
第417章 冈戈尔之刃的进阶形态
第421章 【共生殖装】的猜想
第422章 【共生殖装】诞生
第427章 【死星】出世
第450章 点化【死星】
第451章 【帝死星】
第464章 反抗组织联合舰队，超大规模战争
第468章 一枪崩掉万神殿
第469章 弑神手枪
第481章 围攻死星！
第483章 我，即是原力！
第493章 【现实宝石】
第501章 伊戈的基因样本【创世】与【吞星】
第519章 天神基因链，三次进化
第537章 异形机械军团！
第542章 邪恶王冠，沙巴克形态
第545章 清虚道德天尊，袭杀驻点
第553章 【黑寡妇】与【伤害无效化】
第577章 【混沌魔法】与【物品打造】
第578章 【灰烬之泰坦基因链】
第581章 真正的吞星
第582章 恐虐意识体
第594章 银流星？混沌爆发
第596章 镇压恐虐
第599章 点化伊斯特拉
```

Bản v19 bổ sung 26 nhóm thuật toán mới:

```text
V19-GAP-01  Cosmic artifact scanner: 无限手套/力量宝石/现实宝石/死星/帝死星
V19-GAP-02  Artifact lifecycle grammar: 点化/出世/进阶/解锁/激活/诞生/堆满进度条
V19-GAP-03  Symbiote/BioTech chain: 共生殖装/血雷龙基因链/灰烬之泰坦基因链
V19-GAP-04  War-scale faction composition: 反抗组织联合舰队/异形机械军团/金狮军团
V19-GAP-05  Battle/cosmic action chain: 围攻/镇压/碾压/俘获/袭杀/伏击/总攻
V19-GAP-06  Transformation/state forms: 沙巴克形态/红莲状态/赛亚状态/混沌爆发
V19-GAP-07  Divinity/mythic title scanner: 清虚道德天尊/万神殿/弑神手枪/恐虐
V19-GAP-08  Force/cosmic identity grammar: 我，即是原力
V19-GAP-09  Progress-bar/system build grammar: 进度条堆满/解锁/打造/物品打造
V19-GAP-10  Plan/intrigue script grammar: 剧本展开/步步为营/坐地分赃/明争暗斗
V19-GAP-11  Media/public-opinion/scandal grammar: 舆论影响/星际震动/聚光灯下
V19-GAP-12  Named entity scanner for Western-like names: 科德里/西格尔/莱茵哈特/比安奇/尼尔森
V19-GAP-13  Alias collision resolver: 死星 vs 帝死星 vs 特殊图纸死星
V19-GAP-14  Bracketed item chain with possessive: 【冈戈尔之刃】/【昆塔莎的生命权杖】
V19-GAP-15  “X之威/之死/之战/之形态” title grammar
V19-GAP-16  “一枪/一拳/一击 + result” combat quantifier idiom
V19-GAP-17  “给我去 V / 出来吧 X / 向您问好” imperative/dramatic speech
V19-GAP-18  “我知道，但我不同意” contrast-retort rule
V19-GAP-19  “只是/不过/倒也/毕竟/至于” discourse chaining
V19-GAP-20  “逐渐/终于/再次/重归/又见/又要” aspect/adverb progression
V19-GAP-21  “如果我俩角色互换” counterfactual frame
V19-GAP-22  “只差一步/一举三得/一脉相承” idiom guard
V19-GAP-23  “被排挤/被抓/被镇压/被俘获” institutional passive extension
V19-GAP-24  “隐藏的小九九/各怀鬼胎/胜券在握” mental-state idiom guard
V19-GAP-25  In-title author-note stripping when title has parenthetical thanks
V19-GAP-26  Proper-name review export expanded with chapter-source evidence
```

---

### 1. Corpus Signals chương 401–600

#### 1.1 Tần suất và domain signals

Trong vùng chương 401–600, một số cụm xuất hiện nhiều:

```text
泰坦            ~650+
死星            ~300+
救世方舟        ~220+
共生殖装        ~100+
无限手套        ~90+
智能终端        ~90+
深渊 / 研究所   rất cao ở đoạn sau
恐虐            ~100+
伊斯特拉        ~50+
银流星          ~50+
机械章鱼        ~40+
冈戈尔之刃      ~30+
力量宝石        ~20+
```

Điều này cho thấy thuật toán không chỉ cần nhận diện entity, mà còn cần **lifecycle tracking**: một entity có thể được nhắc ở nhiều trạng thái khác nhau:

```text
【死星】 → 点化【死星】 → 【帝死星】 → 围攻死星 → 死星出世
```

#### 1.2 Chương tiêu đề có nhiều entity seed

Chương 401–600 có mật độ tiêu đề chứa entity rất cao. Vì vậy **ChapterTitleEntitySeeder** phải được nâng cấp thành nguồn glossary chính, không chỉ là phụ trợ.

---

## PART A — Cosmic Artifact Scanner

### A1. Problem

Các vật phẩm vũ trụ có thể là:
- franchise artifact,
- system item,
- weapon,
- ship/station,
- divine/mythic artifact,
- blueprint,
- ability.

Ví dụ:

```text
【无限手套】
【力量宝石】
【现实宝石】
【死星】
【帝死星】
【冈戈尔之刃】
【昆塔莎的生命权杖】
【弑神手枪】
【邪恶王冠】
【黑寡妇】
【伤害无效化】
【混沌魔法】
【物品打造】
```

### A2. Ontology

```json
{
  "cosmic_artifact": ["无限手套", "力量宝石", "现实宝石", "火种源碎片", "昆塔莎的生命权杖"],
  "super_weapon": ["死星", "帝死星", "特殊图纸死星"],
  "divine_weapon": ["弑神手枪", "冈戈尔之刃", "邪恶王冠"],
  "ability_item": ["蜘蛛感应", "伤害无效化", "混沌魔法", "物品打造"],
  "character_item_alias": ["黑寡妇"]
}
```

### A3. Translation policy

| ZH | VI |
|---|---|
| `无限手套` | Găng Tay Vô Cực / Infinity Gauntlet |
| `力量宝石` | Viên đá Sức Mạnh / Power Stone |
| `现实宝石` | Viên đá Hiện Thực / Reality Stone |
| `死星` | Death Star / Tử Tinh |
| `帝死星` | Đế Tử Tinh / Imperial Death Star |
| `冈戈尔之刃` | Lưỡi Dao Gongor |
| `昆塔莎的生命权杖` | Quyền Trượng Sinh Mệnh của Quintessa |
| `弑神手枪` | Súng Ngắn Thí Thần |
| `邪恶王冠` | Vương Miện Tà Ác |
| `混沌魔法` | Ma Pháp Hỗn Độn |
| `伤害无效化` | vô hiệu hóa sát thương |

### A4. Scanner rule

```python
if bracketed_item:
    exact_glossary_first()
    if contains artifact suffix: classify ARTIFACT
    if contains ability suffix: classify ABILITY
    if contains "死星": link to DeathStarEntity
```

---

## PART B — Artifact Lifecycle Grammar

### B1. Patterns

```text
点化【死星】
【死星】出世
【共生殖装】诞生
冈戈尔之刃的进阶形态
纲要解锁
进度条堆满
超级武器
物品打造
现实宝石之威
```

### B2. Rule mapping

| ZH | VI |
|---|---|
| `点化 X` | điểm hóa X |
| `X 出世` | X xuất thế / ra đời |
| `X 诞生` | X ra đời |
| `X 的进阶形态` | hình thái tiến giai của X |
| `解锁 X` | mở khóa X |
| `进度条堆满` | thanh tiến độ được lấp đầy |
| `打造 X` | chế tạo X |
| `X 之威` | uy lực của X |
| `X 之死` | cái chết của X |

### B3. Lifecycle state record

```python
@dataclass
class EntityLifecycle:
    entity_id: str
    states: list[str]  # created, awakened, upgraded, unlocked, deployed, destroyed
    first_seen_chapter: int
    last_seen_chapter: int
```

### B4. Example

```text
点化【死星】
→ điểm hóa [Death Star]

【帝死星】
→ [Đế Tử Tinh]  # alias/evolved form of Death Star
```

---

## PART C — Symbiote / BioTech Entity Chain

### C1. Patterns

```text
【共生殖装】
血雷龙基因链
天神基因链
灰烬之泰坦基因链
异形机械军团
基因链进度又要拉满了
三次进化
变异
```

### C2. Ontology

```json
{
  "symbiote": ["共生殖装", "殖装", "共生体"],
  "gene_chain": ["血雷龙基因链", "天神基因链", "灰烬之泰坦基因链"],
  "evolution": ["进化", "三次进化", "变异", "强化"],
  "bio_mech": ["异形机械军团", "机械章鱼", "泰坦殖装"]
}
```

### C3. Translation

| ZH | VI |
|---|---|
| `共生殖装` | thực trang cộng sinh / giáp sinh thể cộng sinh |
| `血雷龙基因链` | chuỗi gen Huyết Lôi Long |
| `天神基因链` | chuỗi gen Thiên Thần |
| `灰烬之泰坦基因链` | chuỗi gen Titan Tro Tàn |
| `异形机械军团` | quân đoàn cơ giới Dị Hình |
| `三次进化` | tiến hóa lần ba |

### C4. Rule

```python
if span.endswith("基因链"):
    classify BIO_GENE_CHAIN
elif span.endswith("殖装"):
    classify SYMBIOTE_EQUIPMENT
elif span.endswith("军团") and contains bio/mech term:
    classify BIOMECH_ARMY
```

---

## PART D — War-scale Faction Composition

### D1. Patterns

```text
反抗组织联合舰队
黑瞳舰队
金狮军团
使徒小队
变形军团
异形机械军团
万神殿
救世方舟
星耀帝国
```

### D2. Faction composition rule

```python
Pattern: [modifier/faction] + [联合] + [舰队/军团/小队]
```

### D3. Examples

```text
反抗组织联合舰队
→ hạm đội liên hợp của tổ chức phản kháng

金狮军团
→ Quân đoàn Kim Sư

使徒小队
→ tiểu đội Sứ Đồ

变形军团
→ Quân đoàn Biến Hình

万神殿
→ Vạn Thần Điện / Pantheon
```

### D4. Hierarchy link

```python
EntityHierarchy.link("金狮军团", parent="星耀帝国", type="military_unit")
EntityHierarchy.link("黑瞳舰队", parent="黯星/议会?", type="fleet")
```

---

## PART E — Cosmic Battle Action Grammar

### E1. Combat verbs

```python
COSMIC_COMBAT_VERBS = [
    "围攻", "镇压", "碾压", "俘获", "袭杀", "伏击", "总攻",
    "撕裂", "崩掉", "攻破", "夺取", "屠杀", "轰击", "扫荡",
    "点化", "封锁", "锁定", "反向锁定", "压制", "偷袭"
]
```

### E2. Pattern: `一枪/一拳/一击 + result`

```text
一枪崩掉万神殿
→ một phát súng bắn sập Vạn Thần Điện

一拳，你拿什么挡
→ một quyền này, ngươi lấy gì mà đỡ?

一击秒杀
→ một đòn miểu sát
```

### E3. Rule

```python
Pattern: 一 + weapon/action_measure + V_RESULT + O
Output: một + unit_vi + V_RESULT_vi + O
```

### E4. Special idiom

```text
认真一拳
→ Một Quyền Nghiêm Túc / cú đấm nghiêm túc
```

If chapter-title or known meme from One Punch style → protect as meme ability.

---

## PART F — Transformation / Form State

### F1. Patterns

```text
沙巴克形态
红莲状态
赛亚状态
混沌爆发
帝死星
机械神通
```

### F2. Rule

```python
if span.endswith(("形态", "状态")):
    classify FORM_STATE
elif span.endswith("爆发"):
    classify BURST_STATE
elif span.endswith("神通"):
    classify ABILITY_TECHNIQUE
```

### F3. Translation

```text
沙巴克形态
→ hình thái Shabak

混沌爆发
→ Hỗn Độn bộc phát

机械神通显威
→ thần thông cơ giới hiển uy
```

---

## PART G — Mythic/Divine Title Scanner

### G1. Patterns

```text
清虚道德天尊
万神殿
弑神手枪
恐虐
恐虐意识体
渊首
伊斯特拉
```

### G2. Rule

```python
if span contains ["天尊", "神", "神殿", "弑神", "意识体"]:
    classify MYTHIC_DIVINE
```

### G3. Translation

| ZH | VI |
|---|---|
| `清虚道德天尊` | Thanh Hư Đạo Đức Thiên Tôn |
| `万神殿` | Vạn Thần Điện / Pantheon |
| `弑神手枪` | Súng Ngắn Thí Thần |
| `恐虐` | Khorne / Khủng Ngược |
| `恐虐意识体` | ý thức thể Khorne |
| `渊首` | Uyên Thủ |
| `伊斯特拉` | Istra / Y Tư Đặc Lạp |

### G4. Franchise-sensitive name style

Nếu `恐虐` thuộc Warhammer, dùng glossary `Khorne`. Nếu không có glossary, fallback Hán Việt.

---

## PART H — Force/Cosmic Identity Grammar

### H1. Pattern

```text
我，即是原力！
```

### H2. Rule

```python
Pattern: 我，即是 X
Output: Ta, chính là X!
```

### H3. Related

```text
X 即是 Y
X 即为 Y
X 乃是 Y
```

Đã có từ v15, nhưng v19 cần thêm **dramatic comma mode** cho thoại/tiêu đề:

```text
我，即是原力！
→ Ta, chính là Force!
```

---

## PART I — Progress Bar / Build System Grammar

### I1. Patterns

```text
进度条堆满
基因链进度又要拉满了
纲要解锁
物品打造
系统升级
功能解锁
```

### I2. Translation

| ZH | VI |
|---|---|
| `进度条堆满` | thanh tiến độ được lấp đầy |
| `进度拉满` | kéo tiến độ đầy |
| `又要拉满了` | lại sắp được kéo đầy |
| `纲要解锁` | cương yếu được mở khóa |
| `物品打造` | chế tạo vật phẩm |
| `功能解锁` | mở khóa chức năng |

### I3. Rule

```python
if span contains "进度" and "满":
    classify PROGRESS_BAR
```

---

## PART J — Strategy/Intrigue Script Grammar

### J1. Patterns

```text
剧本展开
步步为营
坐地分赃
明争暗斗
各怀鬼胎
胜券在握
暗流涌动
风波影响
大幕揭开
```

### J2. Translation

| ZH | VI |
|---|---|
| `剧本展开` | kịch bản triển khai |
| `步步为营` | từng bước chắc chắn |
| `坐地分赃` | ngồi tại chỗ chia chiến lợi phẩm |
| `明争暗斗` | đấu đá công khai lẫn ngấm ngầm |
| `各怀鬼胎` | mỗi người đều mang mưu đồ riêng |
| `胜券在握` | nắm chắc phần thắng |
| `暗流涌动` | sóng ngầm cuộn trào |
| `大幕揭开` | màn lớn mở ra |

### J3. Idiom guard

Protect as idiom before word-level grammar.

---

## PART K — Media / Public Opinion / Spotlight

### K1. Patterns

```text
舆论影响
星际震动
聚光灯下的黑瞳舰队
演讲
采访
声明
事件纷沓
```

### K2. Translation

| ZH | VI |
|---|---|
| `舆论影响` | ảnh hưởng dư luận |
| `星际震动` | chấn động liên sao |
| `聚光灯下的黑瞳舰队` | Hạm đội Hắc Đồng dưới ánh đèn spotlight |
| `扯淡的演讲` | bài diễn thuyết nhảm nhí |
| `采访` | phỏng vấn |
| `声明` | tuyên bố |
| `事件纷沓` | sự kiện dồn dập kéo đến |

---

## PART L — Proper-name Scanner 401–600

### L1. New personal names / aliases

```text
科德里
西格尔
莱茵哈特
比安奇
尼尔森
莫里斯
雷蒙
哈尔肯
西蒙
洛伦
黛拉
蒂戈尔
荷鲁斯
渊首
伊斯特拉
科德温里
安东尼
墨多
屠英
影魔
灵宝
比安奇
清虚道德天尊
```

### L2. Organization / faction / group names

```text
救世方舟
黑瞳舰队
反抗组织联合舰队
星耀帝国
金狮军团
使徒小队
变革者
万神殿
泰坦圣殿
鲜血大公
深渊研究所
联合舰队
异形机械军团
```

### L3. Artifact / ability / item names

```text
无限手套
力量宝石
现实宝石
死星
帝死星
冈戈尔之刃
昆塔莎的生命权杖
弑神手枪
共生殖装
血雷龙基因链
天神基因链
灰烬之泰坦基因链
黑寡妇
伤害无效化
混沌魔法
物品打造
邪恶王冠
```

### L4. Entity scanner upgrades

#### Stage order

```text
1. ChapterTitleEntitySeeder
2. BracketItemExtractor
3. Known franchise glossary
4. Cosmic artifact scanner
5. Faction hierarchy scanner
6. Proper-name transliteration scanner
7. Alias collision resolver
8. Lifecycle state updater
9. Review export
```

#### Scoring additions

```python
if appears in chapter title: +5
if bracketed: +5
if has artifact suffix 宝石/手套/权杖/之刃/手枪: +4
if has faction suffix 方舟/舰队/军团/圣殿/研究所: +4
if appears near verbs 说/道/皱眉/看向/沉默: +2
if appears near lifecycle verbs 点化/出世/解锁/诞生: +3
if entity has evolved alias pattern X -> 帝X: +3
```

### L5. Alias collision examples

```text
死星
帝死星
特殊图纸死星
点化【死星】
围攻死星
```

Resolution:

```python
canonical = "死星"
aliases = ["帝死星", "特殊图纸死星"]
states = ["blueprint", "awakened", "evolved"]
```

---

## PART M — Bracketed Possessive Item Parser

### M1. Patterns

```text
【昆塔莎的生命权杖】
【冈戈尔之刃】
【钢铁侠的装备升级卡】
【灰烬之泰坦基因链】
```

### M2. Rule

```python
if bracketed and contains 的/之:
    parse internal possessive but keep item as one protected span
```

### M3. Translation

```text
【昆塔莎的生命权杖】
→ [Quyền Trượng Sinh Mệnh của Quintessa]

【冈戈尔之刃】
→ [Lưỡi Dao Gongor]

【灰烬之泰坦基因链】
→ [Chuỗi gen Titan Tro Tàn]
```

---

## PART N — Dramatic Imperative / Combat Speech

### N1. Patterns

```text
出来吧，【帝死星】
给我去杀！
向您问好
拿下，镇压
开打开打
```

### N2. Translation

| ZH | VI |
|---|---|
| `出来吧，X` | ra đây đi, X |
| `给我去杀` | đi giết cho ta |
| `向您问好` | gửi lời chào đến ngài |
| `拿下，镇压` | bắt lấy, trấn áp |
| `开打开打` | đánh thôi, đánh thôi |

### N3. Rule

Imperative detection:

```python
if sentence startswith imperative verb or contains "给我去":
    tone = COMMAND
```

---

## PART O — Contrast Retort Rule

### O1. Pattern

```text
我知道，但我不同意
```

### O2. Translation

```text
Ta biết, nhưng ta không đồng ý.
```

### O3. Generalization

```python
Pattern: 我知道/我明白/我懂 + 但/但是/不过 + 我不...
```

---

## PART P — Counterfactual / Role Swap Frame

### P1. Pattern

```text
如果我俩角色互换
```

### P2. Translation

```text
nếu hai chúng ta đổi vai cho nhau
```

### P3. Rule

```python
Pattern: 如果/若是 + A/B + 角色互换
→ nếu A và B đổi vai cho nhau
```

---

## PART Q — Idiom Guard Additions

```text
只差一步
一举三得
一脉相承
人赃俱获
弄巧成拙
急转直下
蠢蠢欲动
卷土重来
危机四伏
心态爆炸
稳步发展
想一块去了
坏了，我成替身啦
```

Translation suggestions:

| ZH | VI |
|---|---|
| `只差一步` | chỉ còn thiếu một bước |
| `一举三得` | một công ba việc |
| `一脉相承` | cùng một mạch truyền thừa |
| `人赃俱获` | bắt được cả người lẫn tang vật |
| `弄巧成拙` | khéo quá hóa vụng |
| `急转直下` | chuyển biến xấu đột ngột |
| `蠢蠢欲动` | rục rịch muốn động |
| `卷土重来` | cuốn đất trở lại / quay lại mạnh mẽ |
| `危机四伏` | nguy cơ bốn bề |
| `心态爆炸` | tâm thái nổ tung / sụp mood |

---

## PART R — Author-note-in-title stripping

### R1. Problem

Một số tiêu đề có phần tác giả xen vào:

```text
第476章 徒手撕裂世界壁垒！（感谢本草纲目...
第504章 申饬（月初求月票，对了，好像能说...
第587章 信任基础（呜呜呜，不好意思，迟到...
```

### R2. Rule

```python
if chapter_title contains parenthetical and parenthetical has:
    ["感谢", "求月票", "求订阅", "不好意思", "迟到"]
then:
    title_main = before_parenthetical
    author_note = parenthetical
```

Config:

```python
preserve_author_note_in_title = False
```

---

## PART S — Data files cần bổ sung

```text
data/grammar/
├── cosmic_artifact_glossary.json
├── artifact_lifecycle_verbs.json
├── symbiote_biotech_terms.json
├── war_faction_composition_patterns.json
├── cosmic_combat_verbs.json
├── transformation_state_terms.json
├── mythic_divine_titles.json
├── progress_bar_system_terms.json
├── strategy_intrigue_idioms.txt
├── media_public_opinion_terms.json
├── proper_name_ch401_600_seed.json
├── bracketed_possessive_item_patterns.json
├── dramatic_imperative_patterns.json
├── counterfactual_role_swap_patterns.json
├── idiom_guard_ch401_600.txt
└── author_note_title_patterns.json
```

---

## PART T — Implementation Roadmap v19

### Sprint V19-A — Cosmic Artifact + Lifecycle

- [ ] `cosmic_artifact_scanner.py`
- [ ] `artifact_lifecycle_tracker.py`
- [ ] `bracketed_possessive_item_parser.py`
- [ ] data: `cosmic_artifact_glossary.json`
- [ ] Tests: 120 cases.

### Sprint V19-B — Symbiote/BioTech + Transformation

- [ ] `symbiote_biotech_parser.py`
- [ ] `gene_chain_state_tracker.py`
- [ ] `transformation_state_rule.py`
- [ ] Tests: 100 cases.

### Sprint V19-C — War/Faction + Cosmic Combat

- [ ] `war_faction_composition_parser.py`
- [ ] `cosmic_combat_action_rule.py`
- [ ] `dramatic_imperative_rule.py`
- [ ] Tests: 120 cases.

### Sprint V19-D — Proper-name Scanner Expansion

- [ ] Add chapter 401–600 seed names.
- [ ] Add alias lifecycle resolver.
- [ ] Add faction hierarchy links.
- [ ] Add evolved artifact alias.
- [ ] Export candidate review report.
- [ ] Tests: 150 cases.

### Sprint V19-E — Discourse/Idiom/Title Cleanup

- [ ] `strategy_intrigue_idiom_guard.py`
- [ ] `media_public_opinion_rule.py`
- [ ] `counterfactual_role_swap_rule.py`
- [ ] `author_note_title_filter.py`
- [ ] Tests: 100 cases.

---

## PART U — Test Matrix v19

### U1. Cosmic artifact

```python
V19_ARTIFACT_TESTS = [
    ("【无限手套】", "[Găng Tay Vô Cực]"),
    ("【力量宝石】", "[Viên đá Sức Mạnh]"),
    ("【现实宝石】", "[Viên đá Hiện Thực]"),
    ("【帝死星】", "[Đế Tử Tinh]"),
    ("【昆塔莎的生命权杖】", "[Quyền Trượng Sinh Mệnh của Quintessa]"),
]
```

### U2. Lifecycle

```python
V19_LIFECYCLE_TESTS = [
    ("点化【死星】", "điểm hóa [Death Star]"),
    ("【死星】出世", "[Death Star] xuất thế"),
    ("【共生殖装】诞生", "[Thực Trang Cộng Sinh] ra đời"),
    ("冈戈尔之刃的进阶形态", "hình thái tiến giai của Lưỡi Dao Gongor"),
]
```

### U3. Symbiote/BioTech

```python
V19_BIOTECH_TESTS = [
    ("【共生殖装】", "[Thực Trang Cộng Sinh]"),
    ("血雷龙基因链", "chuỗi gen Huyết Lôi Long"),
    ("天神基因链", "chuỗi gen Thiên Thần"),
    ("灰烬之泰坦基因链", "chuỗi gen Titan Tro Tàn"),
]
```

### U4. War/faction

```python
V19_FACTION_TESTS = [
    ("反抗组织联合舰队", "hạm đội liên hợp của tổ chức phản kháng"),
    ("金狮军团", "Quân đoàn Kim Sư"),
    ("使徒小队", "tiểu đội Sứ Đồ"),
    ("异形机械军团", "quân đoàn cơ giới Dị Hình"),
]
```

### U5. Combat action

```python
V19_COMBAT_TESTS = [
    ("一枪崩掉万神殿", "một phát súng bắn sập Vạn Thần Điện"),
    ("一击秒杀", "một đòn miểu sát"),
    ("认真一拳", "Một Quyền Nghiêm Túc"),
    ("拿下，镇压", "bắt lấy, trấn áp"),
]
```

### U6. Identity / dramatic speech

```python
V19_SPEECH_TESTS = [
    ("我，即是原力！", "Ta, chính là Force!"),
    ("出来吧，【帝死星】", "ra đây đi, [Đế Tử Tinh]"),
    ("我知道，但我不同意", "Ta biết, nhưng ta không đồng ý"),
    ("如果我俩角色互换", "nếu hai chúng ta đổi vai cho nhau"),
]
```

### U7. Idiom/title

```python
V19_IDIOM_TESTS = [
    ("一举三得", "một công ba việc"),
    ("一脉相承", "cùng một mạch truyền thừa"),
    ("弄巧成拙", "khéo quá hóa vụng"),
    ("人赃俱获", "bắt được cả người lẫn tang vật"),
]
```

### U8. Name scanner

```python
V19_NAME_TESTS = [
    ("科德里", "PERSON"),
    ("西格尔", "PERSON"),
    ("莱茵哈特", "PERSON"),
    ("比安奇", "PERSON"),
    ("金狮军团", "MILITARY_UNIT"),
    ("泰坦圣殿", "ORGANIZATION"),
    ("万神殿", "MYTHIC_ORG"),
    ("深渊研究所", "ORGANIZATION"),
]
```

---

## PART V — Rule Priority cập nhật sau v19

```text
P00 ProtectedSpanEngine
P01 ChapterTitleEntitySeeder
P02 SystemPanelParser
P03 ChapterTitleParser
P04 AuthorNoteFilter
P05 BracketItemExtractor
P06 CrossWorldEntityDetector
P07 CosmicArtifactScanner
P08 Planet/Race/Faction Scanner
P09 FactionHierarchyResolver
P10 AlphanumericGradeGuard
P11 PowerLayerClassifier
P12 Tech/Bio/Symbiote/Artifact Entity Parser
P13 ProperNameConfidenceScorer
P14 ArtifactLifecycleTracker
P15 ClauseSplitter
P20 Core Grammar / v15 rules
P30 SystemRewardRule
P35 SystemUpgradeRule
P40 GradeRankConverter
P45 AuctionPriceParser
P50 TimeFlowRatioConverter
P55 NavigationSpaceRule
P60 Currency/ResourceNumberConverter
P65 LargePopulationNumberConverter
P70 Evolution/DataficationRule
P72 ArtifactLifecycleRule
P75 Strategy/Admin/AnnouncementRules
P80 ColloquialTone/EAPEE Extension
P85 DramaticImperativeRule
P90 SFXPreserver
P99 Postprocess
```

---

## PART W — Acceptance Metrics v19

| Metric | Target |
|---|---:|
| Existing v14–v18 tests | 100% pass |
| Cosmic artifact scanner | ≥ 98% |
| Artifact lifecycle tracking | ≥ 95% |
| Symbiote/BioTech entity detection | ≥ 97% |
| War/faction composition detection | ≥ 95% |
| Combat action idiom conversion | ≥ 92% |
| Transformation state detection | ≥ 95% |
| Mythic/divine title scanner | ≥ 95% |
| Proper-name scanner precision | ≥ 93% |
| Alias collision resolver | ≥ 92% |
| Author-note-in-title filter | ≥ 99% |
| No crash on chapters 401–600 | 100% |

---

## PART X — Merge Strategy

v19 là domain expansion tiếp theo của v18.

- v16: system/sci-fi/game foundation.
- v17: space-war/civilization/auction/high-tech.
- v18: planet/race/faction hierarchy + franchise artifacts + proper-name confidence scoring.
- v19: cosmic artifacts, artifact lifecycle, symbiote biotech, faction war, combat idioms, dramatic speech, expanded proper-name scanner.

Khi merge vào master plan:

1. Đưa `CosmicArtifactScanner` chạy ngay sau `CrossWorldEntityDetector`.
2. Thêm `ArtifactLifecycleTracker` để map alias như `死星 -> 帝死星`.
3. Thêm `SymbioteBioTechParser` cho `共生殖装`, `基因链`, `机械军团`.
4. Thêm `WarFactionCompositionParser` cho `联合舰队/军团/小队`.
5. Thêm `DramaticImperativeRule` cho thoại chiến đấu.
6. Thêm `AuthorNoteTitleFilter` để tách title chính và note tác giả.
7. Mở rộng `ProperNameConfidenceScorer` bằng evidence từ chương 401–600.

---

## END OF v19


---

# PART V — v20 Full Content: Chapters 601–End

**Repo:** `converter-drduc`  
**Kế thừa:** `v14 + v15 + v16 + v17 + v18 + v19`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 601 → hết truyện  
**Ngày:** 2026-04-25  
**Phiên bản:** v20.0 — Endgame / Transcender / Cosmic Alliance / Final Named-Entity Scanner Completion  

---

### 0. Executive Summary

Bản v19 đã bổ sung lớp **Cosmic Artifact / Faction War / Symbiote-BioTech / Name Scanner** cho chương 401–600.  
Khi quét tiếp từ **chương 601 đến hết**, truyện chuyển sang giai đoạn **endgame cosmic-scale**:

1. **Siêu tiến hóa / transcender**
   - `超越者`, `源质`, `源质融合`, `生命跃迁`, `进化顶端`, `真正意义上的死亡`.
2. **Hệ thống vũ trụ / anchor progress / reward endgame**
   - `锚点进度`, `SSS评价`, `SS整体评价`, `阶段性任务`, `整体结算`, `【圣·天尊】`, `【映照宇宙】`.
3. **Đại liên minh / ngoại giao / hội nghị**
   - `大宇宙联盟`, `联合阵线`, `五大文明`, `正式会晤`, `和谈`, `公共会议室`, `文明领袖`.
4. **Tối hậu trí tuệ / creator entities**
   - `终极智慧`, `创世神`, `先知`, `星灵大祭司`, `德罗耶达`, `罗杰`.
5. **Văn minh / công trình vũ trụ**
   - `零号文明`, `星耀帝国`, `永恒文明`, `铁血文明`, `链接通道`, `桥接设备`, `维度魔神`.
6. **Xác suất / thông tin thái / phong tỏa chiều không gian**
   - `概率风暴`, `可能性收束锁定`, `信息态收敛`, `空间封锁`, `从各个层面的完全脱离`.
7. **Chính trị / dư luận / đổ trách nhiệm**
   - `口诛笔伐`, `栽赃`, `声望受损`, `内部作战计划遭到泄露`, `联合施压`.
8. **Dòng thời gian dài / time skip**
   - `两个月之后`, `三年`, `十年来`, `转瞬即逝`, `日渐强大`.
9. **Kết truyện / author note**
   - `各位读者老板们`, `最后任务也揭晓了`, `可以45678天后直接来看结局`, `二十号之前肯定完结`.

Bản v20 bổ sung 24 nhóm thuật toán mới:

```text
V20-GAP-01  Transcender/Source-Essence system scanner
V20-GAP-02  Anchor-progress and endgame reward parser
V20-GAP-03  Stage-vs-overall mission settlement grammar
V20-GAP-04  Cosmic-alliance diplomacy grammar
V20-GAP-05  Formal meeting / summit / projection discourse
V20-GAP-06  Civilizational hierarchy and faction-role scanner
V20-GAP-07  Creator/intelligence entity scanner
V20-GAP-08  Probability-storm / information-state grammar
V20-GAP-09  Dimension-isolation / blockade / bridge-device grammar
V20-GAP-10  Large engineering megastructure grammar
V20-GAP-11  Political blame / reputation damage / public denunciation
V20-GAP-12  Threat/coercion + hidden inducement discourse
V20-GAP-13  Time-skip and long-duration narrative transfer
V20-GAP-14  Endgame title/reward bracket item scanner
V20-GAP-15  “不会真正意义上的死亡” semantic negation rule
V20-GAP-16  “只不过/不过/倒是/反而/而且还” stacked discourse linker
V20-GAP-17  “不是...而是...” extended correction with cosmic terms
V20-GAP-18  “一旦扩散/覆巢之下安有完卵” proverb/condition guard
V20-GAP-19  Author-note/meta paragraph classifier inside body
V20-GAP-20  Final-arc proper-name scanner and alias hierarchy
V20-GAP-21  Projection/communication scene grammar
V20-GAP-22  Entity ownership and subordination in alliances
V20-GAP-23  Ultimate-status/state panel grammar
V20-GAP-24  End-of-novel glossary export and review pipeline
```

---

### 1. Corpus Signals chương 601 → hết

#### 1.1 Endgame system examples

```text
【概率风暴：你处于终极智慧的概率风暴可能性收束锁定中，因此会看见交集画面。
持续时间-720小时】

【源质融合：你正在进化的道路上坚定不移的前进着。】

【10%的锚点进度等待系统升级完毕后发放】

【圣·天尊】
【映照宇宙】
```

#### 1.2 Political/cosmic scene examples

```text
大宇宙联盟的公共会议室中座无虚席，所有文明领袖尽皆到来。
今天是大宇宙联盟第一次正式和联合阵线会晤。
由于前段时间他们针对龙尊的内部作战计划遭到了泄露，导致他的声望再次受到了严重损伤。
```

#### 1.3 Engineering / mega-construction examples

```text
一座大型的金属构造体正在被一个个综合辅助建造设备团团包围。
这座建筑物的整体已经完成了很大一部分，像是一座带有廊道的巨型传送门。
其基座部分便有常规生命星球的数倍大小。
```

---

## PART A — Transcender / Source-Essence System Scanner

### A1. New domain terms

```text
超越者
源质
源质融合
生命跃迁
进化顶端
圣·天尊
映照宇宙
锚点进度
烙印攻击
真名
宇宙感知
宇宙中重生
```

### A2. Ontology

```json
{
  "transcender_status": ["超越者", "进化顶端", "圣·天尊"],
  "source_essence": ["源质", "源质融合", "燃烧源质", "源质核心"],
  "cosmic_authority": ["映照宇宙", "宇宙感知", "烙印攻击", "真名"],
  "anchor_system": ["锚点进度", "锚点", "进度发放"],
  "life_evolution": ["生命跃迁", "重生", "真正意义上的死亡"]
}
```

### A3. Translation policy

| ZH | VI |
|---|---|
| `超越者` | Siêu Việt Giả |
| `源质` | nguyên chất / source essence |
| `源质融合` | dung hợp nguyên chất |
| `生命跃迁` | bước nhảy sinh mệnh |
| `进化顶端` | đỉnh cao tiến hóa |
| `圣·天尊` | Thánh · Thiên Tôn |
| `映照宇宙` | Ánh Chiếu Vũ Trụ |
| `锚点进度` | tiến độ neo điểm |
| `烙印攻击` | công kích lạc ấn |
| `真名` | chân danh |

### A4. Rule

```python
if span in TRANSCENDER_GLOSSARY:
    protect_as_cosmic_system_term(span)

if span contains "源质" and verb in ["融合", "燃烧", "吸收"]:
    classify SOURCE_ESSENCE_ACTION
```

---

## PART B — Anchor Progress / Endgame Reward Parser

### B1. Pattern

```text
【10%的锚点进度等待系统升级完毕后发放】
【圣·天尊】
【映照宇宙】
SSS评价
整体评价只有SS
阶段性的任务完成
整体结算
```

### B2. System reward rules

| Pattern | VI |
|---|---|
| `X%的锚点进度` | X% tiến độ neo điểm |
| `等待系统升级完毕后发放` | chờ hệ thống nâng cấp xong rồi phát |
| `SSS评价` | đánh giá SSS |
| `整体评价只有SS` | đánh giá tổng thể chỉ có SS |
| `阶段性任务` | nhiệm vụ giai đoạn |
| `整体结算` | kết toán tổng thể |
| `阶段性结算` | kết toán theo giai đoạn |

### B3. Rule

```python
Pattern: 【PERCENT + 锚点进度 + WAIT_CONDITION】
Output: 【PERCENT tiến độ neo điểm sẽ được phát sau khi hệ thống nâng cấp hoàn tất】

Pattern: [GRADE]评价
Output: đánh giá [GRADE]
```

### B4. Grade guard

`SSS/SS/S` trong `SSS评价`, `SS整体评价` là rating, không phải entity hoặc chữ cái bình thường.

```python
RATING_RE = r"\bS{1,3}\+?\s*评价\b"
```

---

## PART C — Mission Settlement Grammar

### C1. Patterns

```text
最后任务会结算两次
一次是阶段性的，另一次则是整体结算
其中一些阶段性任务完成的并不算太好
```

### C2. Translation

```text
nhiệm vụ cuối cùng sẽ được kết toán hai lần
một lần là theo giai đoạn, lần còn lại là kết toán tổng thể
một số nhiệm vụ giai đoạn trong đó hoàn thành không được tốt lắm
```

### C3. Rule

```python
if sentence contains ["结算", "阶段性", "整体"]:
    use mission_settlement_frame
```

---

## PART D — Cosmic Alliance Diplomacy Grammar

### D1. Entities

```text
大宇宙联盟
联合阵线
五大文明
星耀帝国
零号文明
永恒文明
铁血文明
星灵文明
泰坦文明废墟
```

### D2. Diplomatic terms

```text
正式会晤
和谈
联合施压
加入
会晤
公共会议室
文明领袖
远程投影
对峙关系
避免升级成更大的摩擦
```

### D3. Translation

| ZH | VI |
|---|---|
| `大宇宙联盟` | Đại Vũ Trụ Liên Minh |
| `联合阵线` | Liên Hợp Trận Tuyến |
| `五大文明` | năm nền văn minh lớn |
| `正式会晤` | cuộc gặp chính thức |
| `和谈` | hòa đàm |
| `联合施压` | cùng gây sức ép |
| `远程投影` | hình chiếu từ xa |
| `文明领袖` | lãnh tụ các nền văn minh |
| `对峙关系` | quan hệ đối đầu |
| `升级成更大的摩擦` | leo thang thành ma sát/xung đột lớn hơn |

### D4. Rule

```python
if sentence contains alliance/faction entities and meeting terms:
    classify DIPLOMATIC_SCENE
    preserve formal register
```

---

## PART E — Formal Meeting / Summit / Projection Discourse

### E1. Scene grammar

```text
会议室中座无虚席
所有文明领袖尽皆到来
他们把目光放在最前列的五道身影上
第一时间双方都没有说话，而是在互相打量着
```

### E2. Translation patterns

| ZH | VI |
|---|---|
| `座无虚席` | không còn chỗ trống / kín chỗ |
| `尽皆到来` | đều đã đến đông đủ |
| `最前列` | hàng đầu tiên / vị trí trước nhất |
| `第一时间` | ngay lập tức / ngay thời điểm đầu tiên |
| `互相打量` | quan sát lẫn nhau |
| `话音刚落` | lời vừa dứt |

### E3. Rule

These are mostly idiomatic discourse chunks; add to `meeting_scene_idiom_guard.txt`.

---

## PART F — Civilizational Hierarchy and Role Scanner

### F1. Entity-role structure

```text
星耀帝国加入大宇宙联盟
星耀帝国的帝皇
帝国高等教育部
天才少年班
五大文明之中
零号文明秘密仓库
永恒文明核心
```

### F2. Hierarchy model

```python
EntityRecord(
    canonical="星耀帝国",
    type="civilization/polity",
    children=["帝国高等教育部", "天才少年班"],
    roles=["帝皇", "德罗耶达"]
)
```

### F3. Rule

```python
Pattern: ENTITY + 的 + ROLE/DEPARTMENT
Output:
  if role: ROLE của ENTITY
  if department: DEPARTMENT thuộc ENTITY
```

### F4. Examples

```text
星耀帝国的帝皇
→ Đế Hoàng của Tinh Diệu Đế Quốc

帝国高等教育部
→ Bộ Giáo dục Cao đẳng của Đế Quốc

零号文明秘密仓库
→ kho bí mật của Văn minh Số Không
```

---

## PART G — Creator / Intelligence Entity Scanner

### G1. Entities

```text
终极智慧
创世神
先知
星灵大祭司
德罗耶达
罗杰
哈纳多
阿尔弗莱
帝皇
黄金战甲
龙尊
维度魔神
```

### G2. Rule

- `终极智慧` is not a common noun phrase; protect as entity/title.
- `创世神` may be entity-title or common title depending context.
- `先知` can be title-name entity if repeated as subject.
- `龙尊` is title/alias for Li Yu, link to `李宇`.

### G3. Alias mapping

```json
{
  "李宇": ["龙尊", "超越者", "圣·天尊"],
  "终极智慧": ["智能生命", "永恒文明核心?"],
  "创世神": ["地缚灵"],
  "先知": ["零号文明先知"],
  "德罗耶达": ["星耀帝国代表?"],
  "罗杰": ["联合阵线/星耀? role context"]
}
```

### G4. Entity confidence

```python
if term appears in dialogue as addressee + 阁下:
    score += 3
if term appears as speaker subject repeatedly:
    score += 2
if term is title-like and chapter-final arc:
    score += 2
```

---

## PART H — Probability Storm / Information-State Grammar

### H1. Patterns

```text
概率风暴
可能性收束锁定
交集画面
信息态收敛
身体中不会发生任何无缘无故的事情
主动能力催发
来自外界因素
```

### H2. Translation

| ZH | VI |
|---|---|
| `概率风暴` | bão xác suất |
| `可能性收束锁定` | khóa thu hẹp khả năng |
| `交集画面` | hình ảnh giao hội / hình ảnh giao điểm |
| `信息态收敛` | thu liễm trạng thái thông tin |
| `主动能力催发` | năng lực chủ động kích phát |
| `外界因素` | yếu tố bên ngoài |

### H3. Rule

```python
if span contains "概率/可能性/收束/信息态":
    classify INFORMATION_PROBABILITY_TECH
```

### H4. Scientific phrase guard

Do not split `可能性收束锁定` into generic `khả năng + thu + bó`.

---

## PART I — Dimension Isolation / Blockade / Bridge Device Grammar

### I1. Patterns

```text
从主宇宙之中隔离出来
从各个层面的完全脱离
切断这片星域和主宇宙的联系
空间封锁装置
链接通道
桥接设备
规则纠缠区域
深层维度世界的污染一旦扩散
```

### I2. Translation

| ZH | VI |
|---|---|
| `主宇宙` | vũ trụ chính |
| `隔离出来` | tách/cách ly ra |
| `各个层面` | mọi tầng diện |
| `完全脱离` | hoàn toàn tách rời |
| `切断联系` | cắt đứt liên hệ |
| `空间封锁装置` | thiết bị phong tỏa không gian |
| `链接通道` | kênh liên kết |
| `桥接设备` | thiết bị cầu nối |
| `规则纠缠区域` | khu vực quy tắc rối cuốn |
| `深层维度世界` | thế giới chiều sâu tầng |

### I3. Rule

```python
if sentence has "从 X 中 + 隔离/脱离/切断":
    use separation_frame

Pattern: 切断 A 和 B 的联系
→ cắt đứt liên hệ giữa A và B
```

---

## PART J — Large Engineering Megastructure Grammar

### J1. Patterns

```text
大型的金属构造体
综合辅助建造设备
巨型传送门
基座部分
常规生命星球的数倍大小
数倍大小
每扩张一微米
消耗材料呈几何倍数递增
```

### J2. Translation

| ZH | VI |
|---|---|
| `大型金属构造体` | kết cấu kim loại cỡ lớn |
| `综合辅助建造设备` | thiết bị hỗ trợ xây dựng tổng hợp |
| `巨型传送门` | cổng truyền tống khổng lồ |
| `基座部分` | phần bệ nền |
| `数倍大小` | lớn gấp mấy lần |
| `每扩张一微米` | mỗi khi mở rộng thêm một micromet |
| `几何倍数递增` | tăng theo cấp số nhân |

### J3. Number/measure addition

Add unit:

```text
微米 → micromet / μm
```

Rule:

```python
每 + V + 一 + UNIT
→ mỗi khi V thêm một UNIT
```

---

## PART K — Political Blame / Reputation Damage / Public Denunciation

### K1. Patterns

```text
内部作战计划遭到了泄露
导致他的声望再次受到了严重损伤
口诛笔伐
栽赃成他们支援不力
宣泄的地方
明着威胁，暗中引诱
```

### K2. Translation

| ZH | VI |
|---|---|
| `内部作战计划` | kế hoạch tác chiến nội bộ |
| `遭到泄露` | bị rò rỉ |
| `声望受损` | danh vọng bị tổn hại |
| `严重损伤` | tổn hại nghiêm trọng |
| `口诛笔伐` | bị công kích bằng lời nói và ngòi bút |
| `栽赃成` | vu oan thành |
| `支援不力` | chi viện bất lực/không hiệu quả |
| `宣泄的地方` | nơi để trút giận |
| `明着威胁，暗中引诱` | ngoài mặt uy hiếp, ngầm dụ dỗ |

### K3. Passive political frame

```text
计划遭到泄露
声望受到损伤
死亡被栽赃成...
```

Rule:

```python
遭到/受到 + negative_event
→ bị + negative_event_vi
```

---

## PART L — Threat / Coercion + Hidden Inducement Discourse

### L1. Pattern

```text
明着威胁，暗中引诱
为星耀帝国铺路
完全不上心
```

### L2. Rule

```text
明着 X，暗中 Y
→ ngoài mặt X, âm thầm/ngầm Y
```

### L3. Examples

```text
明着威胁，暗中引诱
→ ngoài mặt uy hiếp, ngầm dụ dỗ
```

---

## PART M — Time-skip and Long-duration Narrative Transfer

### M1. Patterns

```text
转眼间便是两个月之后
时间匆匆而过
又是接近两个月的时间转瞬即逝
三年过去了
十年来
日渐强大
缓步进行中
```

### M2. Translation

| ZH | VI |
|---|---|
| `转眼间便是两个月之后` | chớp mắt đã là hai tháng sau |
| `时间匆匆而过` | thời gian vội vã trôi qua |
| `转瞬即逝` | thoáng cái đã trôi qua |
| `三年过去了` | ba năm đã trôi qua |
| `十年来` | suốt mười năm qua |
| `日渐强大` | ngày càng lớn mạnh |
| `缓步进行中` | đang tiến hành chậm rãi |

### M3. Rule

```python
if sentence startswith time_skip_marker:
    classify NARRATIVE_TIME_SKIP
```

---

## PART N — Semantic Negation: `不会真正意义上的死亡`

### N1. Pattern

```text
超越者不会真正意义上的死亡
```

### N2. Problem

Literal “không chết trên ý nghĩa chân chính” awkward.

### N3. Rule

```text
不会 + 真正意义上 + V/N
→ sẽ không thật sự V / không V theo đúng nghĩa
```

### N4. Translation

```text
超越者不会真正意义上的死亡
→ Siêu Việt Giả sẽ không thật sự chết theo đúng nghĩa.
```

---

## PART O — Stacked Discourse Linkers

### O1. Patterns

```text
只不过
不过
倒是
反而
而且还
当然也
特别是
更不用多说
```

### O2. Mapping

| ZH | VI |
|---|---|
| `只不过` | chỉ có điều |
| `不过` | có điều / tuy nhiên |
| `倒是` | ngược lại thì / lại là |
| `反而` | ngược lại |
| `而且还` | hơn nữa còn |
| `当然也` | đương nhiên cũng |
| `特别是` | đặc biệt là |
| `更不用多说` | càng không cần phải nói |

### O3. Rule

If multiple discourse linkers appear, collapse to natural VI:

```text
只不过，他倒是没想到...
→ chỉ có điều, hắn lại không ngờ rằng...
```

Avoid duplicate `nhưng tuy nhiên`.

---

## PART P — Proverb / Conditional Guard

### P1. Patterns

```text
一旦扩散
覆巢之下安有完卵
藏拙
木已成舟
一山不容二虎
```

### P2. Translation

| ZH | VI |
|---|---|
| `一旦扩散` | một khi lan rộng |
| `覆巢之下安有完卵` | tổ đã lật thì làm gì còn trứng lành |
| `藏拙` | giấu nghề / che giấu thực lực |
| `木已成舟` | ván đã đóng thuyền |
| `一山不容二虎` | một núi không dung hai hổ |

### P3. Guard

Protect as idiom before word-level grammar.

---

## PART Q — Author-note / Meta Paragraph Classifier

### Q1. Pattern

```text
各位读者老板们，最后“任务”也揭晓了，应该不少人都能猜到。
如果嫌等的太烦，可以45678天后直接来看结局，反正二十号之前肯定完结。
```

### Q2. Rule

```python
if paragraph contains ["读者", "老板们", "完结", "结局", "作者", "求票", "二十号之前"]:
    classify AUTHOR_META_PARAGRAPH
```

### Q3. Config

```python
translate_author_meta = False
preserve_author_meta = True
author_meta_prefix = "Ghi chú tác giả:"
```

---

## PART R — Final-Arc Proper Name Scanner

### R1. New / important entities

#### Personal / title entities

```text
德罗耶达
罗杰
终极智慧
创世神
先知
星灵大祭司
哈纳多
阿尔弗莱
帝皇
黄金战甲
龙尊
```

#### Factions / civilizations

```text
大宇宙联盟
联合阵线
星耀帝国
零号文明
永恒文明
铁血文明
星灵文明
泰坦文明废墟
五大文明
```

#### Cosmic/system concepts

```text
超越者
源质
源质融合
概率风暴
可能性收束锁定
信息态
锚点进度
映照宇宙
圣·天尊
链接通道
桥接设备
维度魔神
深层维度世界
荒芜宇宙带
```

### R2. Alias hierarchy

```json
{
  "李宇": ["龙尊", "超越者", "圣·天尊"],
  "终极智慧": ["智能生命", "永恒文明核心"],
  "星耀帝国": ["帝国"],
  "大宇宙联盟": ["联盟"],
  "联合阵线": ["阵线"],
  "零号文明": ["零号"],
  "维度魔神": ["魔神"]
}
```

### R3. Endgame entity scoring additions

```python
if term appears in system reward bracket: +6
if term appears with 阁下: +3
if term appears in diplomatic scene as faction: +3
if term appears in cosmic concept glossary: +4
if term appears after "被称之为": +2
if term appears with quote marks “...” in title/name context: +2
```

---

## PART S — Projection / Communication Scene Grammar

### S1. Patterns

```text
结束通讯吧
远程投影
投影消失在虚空中
屏幕
交接
具体细节
```

### S2. Translation

| ZH | VI |
|---|---|
| `结束通讯` | kết thúc liên lạc |
| `远程投影` | hình chiếu từ xa |
| `投影消失` | hình chiếu biến mất |
| `屏幕` | màn hình |
| `交接` | bàn giao / tiếp nhận |
| `具体细节` | chi tiết cụ thể |

---

## PART T — Entity Ownership / Subordination in Alliances

### T1. Patterns

```text
星耀帝国加入大宇宙联盟
其他文明境内
帝国高等教育部
大宇宙联盟的公共会议室
联合阵线的众多文明
```

### T2. Rule

```python
Pattern: FACTION_A + 加入 + FACTION_B
→ FACTION_A gia nhập FACTION_B

Pattern: FACTION + 境内
→ trong lãnh thổ của FACTION

Pattern: FACTION + 的 + ORG_PLACE
→ ORG_PLACE của/thuộc FACTION
```

---

## PART U — Ultimate Status / State Panel Grammar

### U1. Patterns

```text
【概率风暴：...持续时间-720小时】
【源质融合：...】
【圣·天尊】
【映照宇宙】
【10%的锚点进度...】
```

### U2. Rule

Use `SystemPanelParser` from v16, but add:

```python
SYSTEM_PANEL_KIND_ENDGAME = [
    "STATUS_EFFECT",
    "COSMIC_REWARD",
    "ANCHOR_PROGRESS",
    "TRANSCENDER_TITLE",
]
```

### U3. Examples

```text
【概率风暴：你处于终极智慧的概率风暴可能性收束锁定中，因此会看见交集画面。
持续时间-720小时】
→ 【Bão Xác Suất: ngươi đang ở trong khóa thu hẹp khả năng của Bão Xác Suất từ Tối Chung Trí Tuệ, vì vậy sẽ nhìn thấy hình ảnh giao hội. Thời gian duy trì: 720 giờ】

【源质融合：你正在进化的道路上坚定不移的前进着。】
→ 【Dung Hợp Nguyên Chất: ngươi đang kiên định tiến bước trên con đường tiến hóa.】
```

---

## PART V — Data files cần bổ sung

```text
data/grammar/
├── transcender_system_terms.json
├── source_essence_terms.json
├── anchor_progress_patterns.json
├── mission_settlement_patterns.json
├── cosmic_alliance_terms.json
├── summit_meeting_idiom_guard.txt
├── civilizational_hierarchy_patterns.json
├── creator_intelligence_entities.json
├── probability_information_terms.json
├── dimension_blockade_terms.json
├── megastructure_engineering_terms.json
├── political_blame_terms.json
├── threat_inducement_patterns.json
├── narrative_timeskip_markers.json
├── semantic_negation_patterns.json
├── stacked_discourse_linkers.json
├── final_arc_idiom_guard.txt
├── author_meta_paragraph_patterns.json
├── final_arc_entity_seed.json
├── projection_communication_terms.json
├── alliance_subordination_patterns.json
└── endgame_system_panel_kinds.json
```

---

## PART W — Implementation Roadmap v20

### Sprint V20-A — Endgame system/reward parser

- [ ] `TranscenderSystemScanner`
- [ ] `AnchorProgressParser`
- [ ] `MissionSettlementRule`
- [ ] `EndgameSystemPanelKindClassifier`
- [ ] Tests: 120 cases.

### Sprint V20-B — Cosmic diplomacy/faction hierarchy

- [ ] `CosmicAllianceScanner`
- [ ] `DiplomaticSceneRule`
- [ ] `CivilizationalHierarchyResolver`
- [ ] `AllianceSubordinationRule`
- [ ] Tests: 120 cases.

### Sprint V20-C — Information/probability/dimension technology

- [ ] `ProbabilityInformationTermParser`
- [ ] `DimensionBlockadeRule`
- [ ] `MegaStructureEngineeringRule`
- [ ] Tests: 120 cases.

### Sprint V20-D — Political discourse + time skip

- [ ] `PoliticalBlameRule`
- [ ] `ThreatInducementRule`
- [ ] `NarrativeTimeSkipRule`
- [ ] `StackedDiscourseLinkerCleaner`
- [ ] Tests: 100 cases.

### Sprint V20-E — Final-arc entity scanner

- [ ] Add final arc entity seeds.
- [ ] Add endgame alias hierarchy.
- [ ] Link `李宇 ↔ 龙尊 ↔ 超越者 ↔ 圣·天尊`.
- [ ] Add projection/communication scene terms.
- [ ] Export final glossary review.
- [ ] Tests: 150 cases.

### Sprint V20-F — Author/meta + idiom guards

- [ ] `AuthorMetaParagraphClassifier`
- [ ] `FinalArcIdiomGuard`
- [ ] `SemanticNegationRule`
- [ ] Tests: 80 cases.

---

## PART X — Test Matrix v20

### X1. Transcender/source essence

```python
V20_TRANSCENDER_TESTS = [
    ("超越者", "Siêu Việt Giả"),
    ("源质融合", "dung hợp nguyên chất"),
    ("生命跃迁完成", "hoàn tất bước nhảy sinh mệnh"),
    ("圣·天尊", "Thánh · Thiên Tôn"),
    ("映照宇宙", "Ánh Chiếu Vũ Trụ"),
]
```

### X2. Anchor/reward/settlement

```python
V20_REWARD_TESTS = [
    ("10%的锚点进度等待系统升级完毕后发放",
     "10% tiến độ neo điểm sẽ được phát sau khi hệ thống nâng cấp hoàn tất"),
    ("直接刷出来SSS评价", "trực tiếp刷 ra đánh giá SSS"),
    ("整体评价只有SS", "đánh giá tổng thể chỉ có SS"),
    ("最后任务会结算两次", "nhiệm vụ cuối cùng sẽ được kết toán hai lần"),
]
```

### X3. Alliance/diplomacy

```python
V20_DIPLOMACY_TESTS = [
    ("大宇宙联盟第一次正式和联合阵线会晤",
     "Đại Vũ Trụ Liên Minh lần đầu chính thức gặp gỡ Liên Hợp Trận Tuyến"),
    ("星耀帝国加入大宇宙联盟",
     "Tinh Diệu Đế Quốc gia nhập Đại Vũ Trụ Liên Minh"),
    ("联合施压", "cùng gây sức ép"),
    ("远程投影", "hình chiếu từ xa"),
]
```

### X4. Probability/info/dimension

```python
V20_INFO_TECH_TESTS = [
    ("概率风暴", "bão xác suất"),
    ("可能性收束锁定", "khóa thu hẹp khả năng"),
    ("信息态收敛", "thu liễm trạng thái thông tin"),
    ("从主宇宙之中隔离出来", "tách ra khỏi vũ trụ chính"),
    ("切断这片星域和主宇宙的联系", "cắt đứt liên hệ giữa tinh vực này và vũ trụ chính"),
]
```

### X5. Engineering

```python
V20_ENGINEERING_TESTS = [
    ("大型金属构造体", "kết cấu kim loại cỡ lớn"),
    ("综合辅助建造设备", "thiết bị hỗ trợ xây dựng tổng hợp"),
    ("巨型传送门", "cổng truyền tống khổng lồ"),
    ("每扩张一微米", "mỗi khi mở rộng thêm một micromet"),
    ("消耗材料呈几何倍数递增", "vật liệu tiêu hao tăng theo cấp số nhân"),
]
```

### X6. Political discourse

```python
V20_POLITICAL_TESTS = [
    ("内部作战计划遭到了泄露", "kế hoạch tác chiến nội bộ bị rò rỉ"),
    ("声望再次受到了严重损伤", "danh vọng lại bị tổn hại nghiêm trọng"),
    ("口诛笔伐", "công kích bằng lời nói và ngòi bút"),
    ("栽赃成他们支援不力", "vu oan thành việc bọn họ chi viện không hiệu quả"),
]
```

### X7. Time skip / discourse

```python
V20_TIME_DISCOURSE_TESTS = [
    ("转眼间便是两个月之后", "chớp mắt đã là hai tháng sau"),
    ("三年过去了", "ba năm đã trôi qua"),
    ("十年来", "suốt mười năm qua"),
    ("只不过，他倒是没想到", "chỉ có điều, hắn lại không ngờ rằng"),
]
```

### X8. Final entity scanner

```python
V20_ENTITY_TESTS = [
    ("终极智慧", "ENTITY_CREATOR_INTELLIGENCE"),
    ("创世神", "ENTITY_CREATOR_GOD"),
    ("大宇宙联盟", "COSMIC_ALLIANCE"),
    ("联合阵线", "COSMIC_FACTION"),
    ("星耀帝国", "CIVILIZATION_POLITY"),
    ("维度魔神", "DIMENSION_DEMON"),
    ("荒芜宇宙带", "COSMIC_REGION"),
    ("龙尊", "ALIAS_OF_LI_YU"),
]
```

---

## PART Y — Rule Priority cập nhật sau v20

```text
P00 ProtectedSpanEngine
P01 ChapterTitleEntitySeeder
P02 SystemPanelParser
P03 EndgameSystemPanelKindClassifier
P04 ChapterTitleParser
P05 AuthorNoteFilter / AuthorMetaParagraphClassifier
P06 BracketItemExtractor
P07 CrossWorldEntityDetector
P08 CosmicArtifactScanner
P09 TranscenderSystemScanner
P10 Creator/IntelligenceEntityScanner
P11 CosmicAlliance/FactionScanner
P12 Planet/Race/Faction Scanner
P13 CivilizationalHierarchyResolver
P14 AlphanumericGradeGuard
P15 PowerLayerClassifier
P16 ProbabilityInformationTermParser
P17 Tech/Bio/Symbiote/Artifact Entity Parser
P18 ProperNameConfidenceScorer
P19 ArtifactLifecycleTracker
P20 ClauseSplitter
P30 Core Grammar / v15 rules
P35 MissionSettlementRule
P40 SystemRewardRule
P45 SystemUpgradeRule
P50 GradeRankConverter
P55 AuctionPriceParser
P60 TimeFlowRatioConverter
P65 NavigationSpaceRule
P70 Currency/ResourceNumberConverter
P75 LargePopulationNumberConverter
P80 DimensionBlockadeRule
P82 MegaStructureEngineeringRule
P85 Political/Alliance/AnnouncementRules
P88 NarrativeTimeSkipRule
P90 ColloquialTone/EAPEE Extension
P92 DramaticImperativeRule
P95 SFXPreserver
P99 Postprocess
```

---

## PART Z — Acceptance Metrics v20

| Metric | Target |
|---|---:|
| Existing v14–v19 tests | 100% pass |
| Transcender/system term scanner | ≥ 98% |
| Anchor-progress parser | ≥ 98% |
| Mission settlement grammar | ≥ 95% |
| Cosmic diplomacy scene detection | ≥ 94% |
| Civilizational hierarchy resolver | ≥ 92% |
| Creator/intelligence entity scanner | ≥ 96% |
| Probability/information-state parser | ≥ 94% |
| Dimension blockade grammar | ≥ 92% |
| Megastructure engineering grammar | ≥ 92% |
| Political blame discourse | ≥ 90% |
| Time-skip transfer | ≥ 95% |
| Author meta paragraph classifier | ≥ 99% |
| Final-arc entity alias linking | ≥ 93% |
| No crash from chapter 601 to end | 100% |

---

### Merge Strategy

v20 là lớp hoàn thiện endgame cho toàn bộ truyện.

- v16: system/sci-fi/game foundation.
- v17: space-war/civilization/auction/high-tech.
- v18: planet/race/faction hierarchy + franchise artifacts + proper-name confidence scoring.
- v19: cosmic artifacts + artifact lifecycle + symbiote biotech + faction war.
- v20: transcender system + anchor/reward + cosmic alliance diplomacy + probability/information/dimension technology + final named-entity scanner.

Khi merge vào master plan:

1. Thêm `TranscenderSystemScanner` và `EndgameSystemPanelKindClassifier`.
2. Mở rộng `SystemPanelParser` để xử lý reward cuối truyện, SSS/SS rating, anchor progress.
3. Thêm `CosmicAllianceScanner` và `CivilizationalHierarchyResolver`.
4. Thêm `ProbabilityInformationTermParser` cho `概率风暴`, `信息态`, `可能性收束`.
5. Thêm `DimensionBlockadeRule` và `MegaStructureEngineeringRule`.
6. Thêm `AuthorMetaParagraphClassifier` cho đoạn tác giả chen vào body.
7. Hoàn thiện `FinalArcEntitySeed` và `AliasHierarchy`: `李宇 ↔ 龙尊 ↔ 超越者 ↔ 圣·天尊`.

---

## END OF v20


---

# PART VI — Final Merge Strategy

## 1. Mục tiêu v21

Bản v21 là file tổng hợp đầy đủ, dùng làm nền để tạo master plan implementation cho riêng truyện mới.  
Nó nên được merge với v14/v15 như sau:

```text
v14/v15 = Grammar core + general deep gaps
v21     = New-story domain expansion
```

## 2. Thứ tự triển khai đề xuất

```text
Phase 1 — Format Safety
  SystemPanelParser
  ChapterTitleParser
  BracketItemExtractor
  AuthorMetaClassifier

Phase 2 — Entity Safety
  ProtectedSpanEngine
  CrossWorldEntityDetector
  Tech/Sci-fi entity parser
  ProperNameConfidenceScorer
  AliasHierarchyResolver

Phase 3 — Number/Rank Safety
  GradeRankConverter
  TimeFlowRatioConverter
  CurrencyResourceConverter
  AuctionPriceParser
  AnchorProgressParser

Phase 4 — Domain Grammar
  Passive/result
  Equipment install
  Bio/gene/evolution
  Space navigation/hazard
  Artifact lifecycle
  Diplomacy/political discourse
  Dimension/engineering rules

Phase 5 — Style/Tone
  Slang
  SFX
  Meme titles
  Dramatic imperative
  Author notes

Phase 6 — Whole-story Regression
  Chapter range tests
  Entity glossary export
  Low-confidence review list
  Accuracy report by domain
```

## 3. Definition of Done v21

- Có thể parse giữ format toàn bộ `【...】`.
- Không phá entity alphanumeric như `D级`, `E+`, `G病毒`, `SSS评价`.
- Quét được tên riêng nhân vật, thế lực, vật phẩm, công nghệ, chủng tộc, hành tinh, văn minh, artifact.
- Có alias hierarchy xuyên truyện, ví dụ `李宇 ↔ 龙尊 ↔ 超越者 ↔ 圣·天尊`.
- Có lifecycle cho artifact như `死星 → 帝死星`.
- Dịch đúng số/tỷ lệ/tiền tệ/rating/anchor progress.
- Có author-meta filter.
- Có regression test trên toàn bộ truyện.
- No crash trên toàn corpus.

---

# END OF v21
