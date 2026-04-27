# GRAMMAR_TRANSFER_PLAN_v14_MERGED_v12_v13

**Repo:** `converter-drduc`  
**Corpus nền:** `Hồng Hoang Lịch_Zhttty.html`  
**Nguồn hợp nhất:** `GRAMMAR_TRANSFER_PLAN_v12_MERGED_v7_v11.md` + `GRAMMAR_TRANSFER_PLAN_v13_CH301_400_COMPLETION.md`  
**Phạm vi corpus đã nghiên cứu:** v7–v11 và chương 301–400  
**Mục tiêu:** Một bản kế hoạch thống nhất, chi tiết, đầy đủ để triển khai thuật toán Grammar Transfer ZH→VI có nhận diện entity, chuyển đổi số, cấu trúc cổ văn/huyền huyễn, game/system và discourse logic.  
**Ngày xuất bản:** 2026-04-25  
**Phiên bản:** v14.0 — Unified Full Plan  

---

## 0. Executive Summary

Bản v14 hợp nhất toàn bộ nội dung từ v12 và v13 thành một kế hoạch triển khai thống nhất cho `converter-drduc`.

Trọng tâm của bản này:

1. **Core grammar transfer ZH→VI**
   - `的`, aspect, passive, disposal, directional complement, serial verb, topic-comment.
2. **Clause/discourse logic**
   - Điều kiện, nhượng bộ, đối lập, nguyên nhân-kết quả, thời gian, phạm vi, modal, câu hỏi tu từ.
3. **Cấu trúc cổ văn/huyền huyễn**
   - `所`, `之`, `以`, `为`, `将`, `便是`, `任凭`, `光是`, `又如何`.
4. **Complement system**
   - Resultative complement, potential complement, degree complement `得`, abstract directional complement `起来/下来/出来`.
5. **Number/format converter**
   - Số đếm, số thứ tự, duration, countdown, phần trăm, phân số, `成`, rank, level, generation, floor/building, game resource.
6. **Entity-aware transfer**
   - Nhân vật, thế lực, địa danh, vật phẩm, vũ khí, pháp bảo, công pháp, chủng tộc, vị diện, SCP/game/system terms.
7. **Protected span engine**
   - Bảo vệ tên riêng, số trong entity, thuật ngữ hệ thống, dialogue/system prompt khỏi bị tách/dịch sai.
8. **Roadmap triển khai**
   - MVP an toàn, feature flag, shallow parser trước dependency parser, đo accuracy theo construction/entity/number.

---

## 1. Những điểm mới so với v12

Bản v13 bổ sung vào nền v12 các nhóm sau, nay được tích hợp chính thức vào v14:

| Nhóm bổ sung | Nội dung |
|---|---|
| Discourse markers | `事实上`, `实际上`, `换言之`, `也就是说`, `看似...事实上` |
| Concession nâng cao | `任凭...任凭...`, `便是/就是...也`, `纵然...依然` |
| Emphasis/rhetoric | `光是...就`, `别说...更别说`, `何止/岂止`, `又如何` |
| Classical function words | classifier sâu cho `所/之/以/为/将` |
| Abstract directional | `想起来`, `看出来`, `记录下来`, `联合起来` |
| `得` complement guard | tránh xử lý sai `觉得/获得/不得不/显得` |
| Number expansion | `% > 100`, `% xấp xỉ`, decimal percent, `成`, rank, floor/building |
| Entity expansion | SCP, Hồng Hoang thần thoại, pháp bảo, quyền柄, vị diện, tổ chức |
| Clause splitter | tách câu nghị luận dài nhưng tránh split trong quote/entity/number range |

---

## 2. Unified Architecture

### 2.1 Pipeline đề xuất

```text
Input ZH sentence
  ↓
Traditional/Simplified normalization
  ↓
Sentence/Clause splitter
  ↓
Entity Intelligence Layer
  ├─ NamedEntityDetector
  ├─ EntityChainParser
  ├─ Alias/CoreferenceResolver
  ├─ ProtectedSpanEngine
  └─ Number-in-Entity Guard
  ↓
ZHTokenizer + POS Tagger
  ↓
ShallowConstructionDetector
  ├─ Core grammar constructions
  ├─ Clause/discourse constructions
  ├─ Classical function-word constructions
  ├─ Complement constructions
  └─ Number/format constructions
  ↓
TransferEngine
  ├─ Structural rules
  ├─ Clause logic rules
  ├─ Classical/xianxia rules
  ├─ Number conversion rules
  └─ Entity-preserving rules
  ↓
Existing RBMT lexical loop
  ├─ Trie lookup
  ├─ LuatNhan
  ├─ NumberConverter fallback
  ├─ Pronoun / EAPEE context
  └─ Vietnamese grammar rewriter
  ↓
Surface cleanup + trace
  ↓
Output VI
```

### 2.2 Nguyên tắc tích hợp an toàn

- Không thay thế toàn bộ `RBMTTranslator` hiện tại.
- Grammar transfer chạy như **structural rewrite layer** có feature flag.
- Không phá lexical loop hiện có.
- Mọi rule mới phải có fallback.
- Protected spans phải chạy trước tokenizer/number converter.
- Chưa cần dependency parser đầy đủ ở MVP; ưu tiên shallow detector + construction parser.

---

## 3. Module triển khai thống nhất

```text
src/
├── core/
│   ├── zh_tokenizer.py
│   ├── pos_tagger.py
│   ├── shallow_grammar_parser.py
│   └── dep_parser.py                    # phase sau
│
├── grammar/
│   ├── __init__.py
│   ├── grammar_data.py
│   ├── pipeline.py
│   ├── construction_detector.py
│   ├── transfer_engine.py
│   ├── surface_realizer.py
│   │
│   ├── entity/
│   │   ├── named_entity_detector.py
│   │   ├── entity_chain_parser.py
│   │   ├── alias_resolver.py
│   │   ├── protected_span.py
│   │   └── entity_glossary.py
│   │
│   ├── number/
│   │   ├── grammar_number_converter.py
│   │   ├── number_context_classifier.py
│   │   ├── protected_number.py
│   │   └── game_resource_number.py
│   │
│   ├── transfer_rules/
│   │   ├── rule_de_inversion.py
│   │   ├── rule_aspect.py
│   │   ├── rule_passive.py
│   │   ├── rule_disposal.py
│   │   ├── rule_directional.py
│   │   ├── rule_serial_verb.py
│   │   ├── rule_topic_comment.py
│   │   ├── rule_clause_logic.py
│   │   ├── rule_discourse_marker.py
│   │   ├── rule_classical_function_words.py
│   │   ├── rule_complement.py
│   │   ├── rule_rhetorical.py
│   │   └── rule_entity_preserve.py
│   │
│   └── postprocess/
│       ├── negation_fixer.py
│       ├── duplicate_marker.py
│       ├── sentence_particle.py
│       ├── punctuation_spacing.py
│       └── trace_formatter.py
│
data/
└── grammar/
    ├── directional_map.json
    ├── directional_abstract_map.json
    ├── aspect_map.json
    ├── sentiment_lexicon.json
    ├── kinship_intimate.txt
    ├── serial_verb_cues.json
    ├── discourse_markers.json
    ├── classical_function_words.json
    ├── entity_suffix_ontology.json
    ├── protected_entity_terms.json
    ├── number_context_patterns.json
    └── game_system_terms.json
```

---

## 4. Unified Rule Priority

Quy tắc nên chạy theo thứ tự ưu tiên sau:

```text
P00 ProtectedSpanEngine
P05 EntityChainParser
P10 ClauseSplitter
P20 Topic / discourse marker
P30 Classical function words: 所/之/以/为/将
P40 Passive / disposal: 被/由所/为所/把/将
P50 DE inversion
P60 Complement: resultative/potential/degree/directional abstract
P70 Aspect markers
P80 Serial verb/action chain
P90 Number/format conversion
P95 Sentence particles/dialogue/system prompt
P99 Postprocess cleanup
```

Lý do:
- Entity và protected span phải chạy trước mọi rewrite.
- Clause/discourse xác định khung logic trước khi đảo cấu trúc.
- `所/之/以/为/将` ảnh hưởng passive/disposal/nominalization.
- Number converter chạy sau khi biết span nào là entity và span nào là quantity.

---

# PART I — Kế hoạch nền hợp nhất từ v12

**Dự án:** `converter-drduc`  
**Mục tiêu:** Hợp nhất các kế hoạch Grammar Transfer đã tạo từ v7 đến v11 thành một kế hoạch chi tiết, đầy đủ, có thể dùng để triển khai tiếp.  
**Phạm vi tổng hợp:**

- v7 — Corpus-driven Grammar/Number Expansion, chương 1–10.
- v8 — Deep Corpus Completion, chương 11–20.
- v9 — First-100-Chapter Corpus Completion, chương 1–100.
- v10 — Ch101–200 Corpus Completion.
- v11 — Ch201–300 Grammar/Number/Entity Completion.

---

### 0. Tóm tắt mục tiêu v12

Kế hoạch v12 gom tất cả bổ sung từ v7–v11 thành một roadmap thống nhất cho thuật toán chuyển đổi ZH→VI, gồm 4 lớp chính:

```text
1. Grammar Transfer Layer
   Nhận diện và chuyển đổi các cấu trúc ngữ pháp Hán hiện đại, cổ văn nhẹ, tiên hiệp, vô hạn lưu, game/system.

2. Number & Format Conversion Layer
   Chuyển đổi số, thời gian, cấp bậc, tài nguyên hệ thống, xác suất, phân số, khoảng số, countdown, đo lường.

3. Entity Intelligence Layer
   Nhận diện tên riêng: nhân vật, chủng tộc, thế lực, địa danh, vị diện, công pháp, vật phẩm, vũ khí, hệ thống, tài nguyên.

4. Trace + Safe Integration Layer
   Tích hợp vào RBMT hiện có bằng feature flag, giữ trace, fallback an toàn, không phá 98 tests cũ.
```

Nguyên tắc triển khai:

```text
- Không thay toàn bộ translator hiện tại.
- Grammar layer là structural rewrite / transfer layer, không phải MT engine độc lập.
- Tận dụng TrieEngine, NumberConverter, LuatNhan, EAPEE hiện có.
- Rule-based trước, parser sâu sau.
- Luôn có protected spans cho entity và number-sensitive phrases.
- Mọi rule phải có trace và test corpus.
```

---

### 1. Kiến trúc tổng thể sau khi hợp nhất v7–v11

#### 1.1 Pipeline đề xuất

```text
Input ZH sentence
  ↓
[Normalize]
  - traditional_to_simplified
  - normalize punctuation
  - preserve quotes/dialogue/system boundary
  ↓
[Entity Intelligence Layer]
  - detect proper names
  - detect system/game terms
  - detect long nominal entities
  - detect protected number-containing names
  - build entity spans
  ↓
[Number Context Pre-classifier]
  - detect numeric spans
  - classify count/duration/date/rank/resource/percent/fraction/entity-number
  - protect number spans that belong to names
  ↓
[Tokenizer + POS]
  - Trie-aware BiMM tokenizer
  - deterministic particles
  - trie metadata POS
  - heuristic fallback
  ↓
[Clause Segmenter]
  - split long sentences by clause markers
  - preserve embedded quotes and system prompts
  - detect logic relation boundaries
  ↓
[Shallow Construction Detector]
  - DE / BA / BEI / ASPECT / DIR / SVC
  - logic relations
  - number patterns
  - entity nominal chain
  ↓
[Grammar Transfer Engine]
  - apply high-priority frame rules
  - apply local structural rules
  - apply number/format conversion hints
  - apply entity rendering policy
  ↓
[Existing RBMT Lexical Loop]
  - locked entities
  - Trie lookup
  - number converter fallback
  - LuatNhan
  - EAPEE/pronoun/emotion
  ↓
[VI Grammar/Postprocess]
  - duplicate marker cleanup
  - punctuation spacing
  - aspect-negation fix
  - classifier cleanup
  - dialogue/system formatting
  ↓
Output VI
```

#### 1.2 Module đề xuất

```text
src/
├── core/
│   ├── zh_tokenizer.py
│   ├── pos_tagger.py
│   ├── shallow_grammar_parser.py
│   ├── clause_segmenter.py
│   └── dep_parser.py                         # phase sau, không blocker MVP
│
├── grammar/
│   ├── __init__.py
│   ├── grammar_data.py
│   ├── construction_detector.py
│   ├── logic_relation_detector.py
│   ├── transfer_engine.py
│   ├── pipeline.py
│   ├── surface_realizer.py
│   │
│   ├── transfer_rules/
│   │   ├── rule_de_inversion.py
│   │   ├── rule_aspect.py
│   │   ├── rule_bei_passive.py
│   │   ├── rule_ba_construction.py
│   │   ├── rule_dir_complement.py
│   │   ├── rule_serial_verb.py
│   │   ├── rule_topic_comment.py
│   │   ├── rule_logic_condition.py
│   │   ├── rule_concession_contrast.py
│   │   ├── rule_comparative_degree.py
│   │   ├── rule_cause_result.py
│   │   ├── rule_purpose_method.py
│   │   ├── rule_modal_necessity.py
│   │   ├── rule_formal_classical.py
│   │   ├── rule_rhetorical_dialogue.py
│   │   ├── rule_long_nominal_chain.py
│   │   ├── rule_system_prompt.py
│   │   └── rule_number_format.py
│   │
│   ├── postprocess/
│   │   ├── negation_fixer.py
│   │   ├── duplicate_marker.py
│   │   ├── sentence_particle.py
│   │   ├── punctuation_fixer.py
│   │   └── dialogue_formatter.py
│   │
│   ├── entities/
│   │   ├── entity_detector.py
│   │   ├── entity_classifier.py
│   │   ├── entity_memory.py
│   │   ├── hanviet_transliterator.py
│   │   ├── alias_resolver.py
│   │   ├── nominal_entity_parser.py
│   │   └── protected_span.py
│   │
│   └── numbers/
│       ├── number_context_classifier.py
│       ├── number_pattern_detector.py
│       ├── rank_level_converter.py
│       ├── resource_number_converter.py
│       ├── percent_fraction_converter.py
│       ├── time_duration_converter.py
│       └── protected_number_span.py
│
data/
└── grammar/
    ├── directional_map.json
    ├── aspect_map.json
    ├── sentiment_lexicon.json
    ├── kinship_intimate.txt
    ├── serial_verb_cues.json
    ├── logic_markers.json
    ├── contrast_markers.json
    ├── modal_markers.json
    ├── classical_markers.json
    ├── rhetorical_markers.json
    ├── number_context_patterns.json
    ├── system_terms.json
    ├── entity_suffix_patterns.json
    ├── entity_prefix_patterns.json
    ├── proper_name_seed.json
    ├── faction_terms.json
    ├── place_terms.json
    ├── artifact_terms.json
    ├── cultivation_terms.json
    └── protected_terms.json
```

---

### 2. Tổng hợp các cấu trúc ngữ pháp cần hỗ trợ

Các nhóm dưới đây gom từ v7–v11, loại bỏ trùng lặp và chuẩn hóa thành danh sách triển khai.

---

## PART A — Core Grammar Transfer

### A1. `的` — modifier, possession, relative clause, nominalization

#### A1.1 Tính từ + 的 + danh từ

```text
ZH: 美丽的书
VI: sách đẹp
```

Rule:

```text
[VA/ADJ] 的 [N] → [N] [ADJ]
```

Điều kiện:

```text
- modifier ngắn hoặc là adjective/stative phrase.
- không có verb/action clause bên trái 的.
```

Ví dụ mở rộng:

```text
强大的力量 → sức mạnh cường đại
残暴的幽魂 → u hồn tàn bạo
血色的气运 → khí vận màu máu
```

#### A1.2 Sở hữu `X 的 Y`

```text
ZH: 他的书
VI: sách của hắn

ZH: 林动的功法
VI: công pháp của Lâm Động
```

Rule:

```text
[PRON/NR/ENTITY] 的 [N] → [N] của [PRON/ENTITY]
```

Ngoại lệ thân thuộc:

```text
他的妈妈 → mẹ hắn
他的师父 → sư phụ hắn
他的主人 → chủ nhân hắn
```

Nếu head noun thuộc `kinship_intimate.txt`, bỏ `của`.

#### A1.3 Relative clause ngắn

```text
ZH: 他买的书
VI: sách hắn mua
```

Rule:

```text
[S V] 的 [N] → [N] [S V]
```

Điều kiện:

```text
- modifier span ≤ 3 tokens.
- không có adv/time/location phức.
```

#### A1.4 Relative clause dài

```text
ZH: 他昨天在图书馆借的书
VI: cuốn sách mà hắn mượn ở thư viện hôm qua
```

Rule:

```text
[long clause] 的 [N] → [N] mà [long clause]
```

Nếu modifier là stative nominal phrase:

```text
ZH: 修为深厚的老者
VI: lão giả có tu vi thâm hậu
```

Rule đặc biệt:

```text
[N/attribute + VA] 的 [human noun] → [human noun] có [N/attribute + VA]
```

#### A1.5 `的` nominalization

```text
ZH: 他所说的
VI: điều hắn nói

ZH: 能做到的
VI: điều có thể làm được
```

Rule:

```text
[clause] 的 → điều/người/thứ + [clause]
```

Chọn head:

```text
- nếu clause chỉ người: người
- nếu vật/sự việc: thứ/điều
- nếu abstract/system: điều
```

#### A1.6 Nested DE

```text
ZH: 他昨天买的那本他喜欢的书
VI: cuốn sách hắn thích mà hắn mua hôm qua
```

Thuật toán:

```text
1. Scan 的 từ phải sang trái.
2. Xử lý inner DE trước.
3. Gắn modifier span vào head noun gần nhất bên phải.
4. Nếu nhiều relative clause cùng head, giữ thứ tự tự nhiên VI:
   [head noun] [short relcl] mà [long relcl]
```

---

### A2. Aspect markers — `了 / 着 / 过 / 正在 / 将要`

#### A2.1 `了` mid-sentence → `đã`

```text
ZH: 他吃了饭
VI: hắn đã ăn cơm
```

Rule:

```text
V + 了 + O → đã + V + O
```

#### A2.2 `了` final → `rồi`

```text
ZH: 他走了
VI: hắn đi rồi
```

Rule:

```text
V + 了 + sentence_end → V + rồi
```

#### A2.3 `已经 + V + 了` → `đã ... rồi`

```text
ZH: 他已经走了
VI: hắn đã đi rồi
```

Rule:

```text
已经 + V + 了 → đã + V + rồi
```

#### A2.4 State change `Adj + 了`

```text
ZH: 天亮了
VI: trời sáng rồi
```

Rule:

```text
VA + 了 → VA + rồi
```

#### A2.5 `着` progressive state

```text
ZH: 他站着
VI: hắn đang đứng
```

Rule:

```text
V + 着 → đang + V
```

#### A2.6 `V 着 V` concurrent manner

```text
ZH: 他笑着说
VI: hắn vừa cười vừa nói
```

Rule:

```text
V1 + 着 + V2 → vừa + V1 + vừa + V2
```

#### A2.7 `过` experiential

```text
ZH: 他去过
VI: hắn từng đi
```

Rule:

```text
V + 过 → từng + V
```

Phủ định:

```text
ZH: 他没去过
VI: hắn chưa từng đi
```

Rule:

```text
没 + V + 过 → chưa từng + V
```

#### A2.8 Progressive `在/正在`

```text
ZH: 他正在修炼
VI: hắn đang tu luyện
```

Rule:

```text
正在/正/在 + V → đang + V
```

Cần phân biệt `在` locative:

```text
他在房间里 → hắn ở trong phòng
他在修炼 → hắn đang tu luyện
```

#### A2.9 Future `将/将要/会/要`

```text
ZH: 他将会回来
VI: hắn sẽ trở về
```

Rule:

```text
将会/将要/会/要 + V → sẽ + V
```

Phải phân biệt với `将 O V` disposal, xem mục A8.

---

### A3. Passive — `被 / 由...所 / 为...所 / 受到 / 遭到`

#### A3.1 `被` passive cơ bản

```text
ZH: 杯子被我打碎了
VI: cái cốc bị tôi đập vỡ rồi
```

Rule:

```text
Patient + 被 + Agent + V → Patient + bị/được + Agent + V
```

Chọn `bị/được`:

```text
- verb negative/adverse → bị
- verb positive/beneficial → được
- unknown → bị
```

#### A3.2 Positive passive

```text
ZH: 他被选上了
VI: hắn được chọn rồi
```

Positive verbs:

```text
选, 录取, 接受, 救, 保护, 帮助, 奖励, 认可, 传授, 赐予, 赋予
```

#### A3.3 `由...所...` formal passive

```text
ZH: 由主神所决定
VI: do Chủ Thần quyết định
```

Rule:

```text
由 + Agent + 所 + V → do + Agent + V
```

Nếu V adverse:

```text
由敌人所杀 → bị kẻ địch giết
```

#### A3.4 `为...所...`

```text
ZH: 为天地所不容
VI: không được trời đất dung nạp / bị trời đất không dung
```

Rule:

```text
为 + Agent + 所 + V → bị/được + Agent + V
```

#### A3.5 Event passive `受到/遭到`

```text
ZH: 受到攻击
VI: chịu công kích / bị tấn công

ZH: 遭到袭击
VI: bị tập kích
```

Rule:

```text
受到 + N/event → chịu/nhận + N
遭到 + N/adverse → bị + N/V
```

#### A3.6 `被` compound guard

Không restructure các compound:

```text
被迫 → bị buộc
被困 → bị vây khốn
被封 → bị phong ấn
被动 → bị động
```

Rule:

```text
if 被 + next forms known compound:
  keep lexical translation, skip passive structural transfer
```

---

### A4. Disposal — `把 / 将 / 给`

#### A4.1 `把` cơ bản

```text
ZH: 他把书放在桌上
VI: hắn đặt sách lên bàn
```

Rule:

```text
S + 把 + O + V + complement → S + V + O + complement
```

#### A4.2 Dùng `đem`

```text
ZH: 他把那个欺负过他的人打倒了
VI: hắn đem kẻ từng bắt nạt hắn đó đánh ngã rồi
```

Dùng `đem` khi:

```text
- object dài > 3 tokens
- register cổ/xianxia
- verb thiên về truyền thụ/ban/hiến/tế/luyện hóa
```

#### A4.3 `把 O 当成/视为 Y`

```text
ZH: 把他当成敌人
VI: xem hắn là kẻ địch
```

Rule:

```text
把 + O + 当成/视为 + Y → xem/coi + O + là + Y
```

#### A4.4 `将` future vs disposal

`将` có 3 loại:

```text
1. Future:
   将 + V / 将会 + V / 将要 + V → sẽ + V

2. Disposal:
   将 + O + V → đem + O + V / V + O

3. Formal object-fronting:
   将 + O + 化为/变成/视为/作为 + Y
```

Ví dụ:

```text
他将离开 → hắn sẽ rời đi
他将敌人杀死 → hắn giết chết kẻ địch / hắn đem kẻ địch giết chết
将能量化为火焰 → hóa năng lượng thành lửa
```

#### A4.5 `给` disposal / affected marker

```text
ZH: 他给我打死了
VI: hắn đánh chết cho ta / hắn đã đánh chết nó mất rồi
```

Rule:

```text
给 + affected + V → cho + affected + V
V + 给 + O → V + cho + O
```

Cần xử lý thận trọng vì `给` cũng là verb “cho”.

---

### A5. Directional complement — `来/去/进/出/上/下/回/过/起`

#### A5.1 Compound direction

```text
走进来 → bước vào
走出去 → bước ra
回来 → trở về
过去 → đi qua / qua đó
```

Rule:

```text
V + DCOMP → V + DIR_vi
```

#### A5.2 `起来`

Hai loại:

```text
Literal:
站起来 → đứng dậy
坐起来 → ngồi dậy

Inceptive:
哭起来 → bắt đầu khóc
笑起来 → bật cười / bắt đầu cười
```

Rule:

```text
if V in posture_verbs:
  起来 → dậy
elif V in inceptive_verbs:
  起来 → bắt đầu / bật
else:
  起来 → lên / bắt đầu tùy context
```

#### A5.3 `下来`

```text
停下来 → dừng lại
平静下来 → bình tĩnh lại
记录下来 → ghi lại
```

Rule:

```text
if V is stative/change verb:
  下来 → lại
elif V is record/keep verb:
  下来 → lại
else:
  xuống
```

#### A5.4 Không dịch hướng nghĩa đen trong temporal/system context

```text
时间向前拨动4个小时
→ thời gian được tua tới trước 4 giờ
```

Rule:

```text
if subject/time-object in {时间, 倒计时, 秒数, 时间线}:
  向前/向后/拨动 → tua tới trước / tua lùi
```

---

### A6. Serial Verb Construction / action chain

#### A6.1 Sequential

```text
ZH: 他站起来走了出去
VI: hắn đứng dậy rồi bước ra ngoài
```

Rule:

```text
S + V1 + V2 → S + V1 + rồi + V2
```

Dùng `rồi` khi hai hành động kế tiếp rõ ràng.

#### A6.2 Purpose

```text
ZH: 我去图书馆借书
VI: tôi đến thư viện mượn sách
```

Rule:

```text
motion V1 + location + V2 → V1 + location + V2
```

Không thêm `để` nếu tiếng Việt tự nhiên hơn không dùng.

#### A6.3 Manner/instrument

```text
ZH: 他骑自行车去上班
VI: hắn đi xe đạp đến chỗ làm
```

Rule:

```text
V1 instrument + V2 action → V1 + instrument + V2
```

#### A6.4 Cause-effect

```text
ZH: 弟弟生病住院了
VI: em trai bị bệnh rồi nhập viện
```

Rule:

```text
stative/event V1 + consequence V2 → V1 + rồi + V2
```

#### A6.5 Combat/action chain dài

Corpus có nhiều chuỗi:

```text
冲上去，一拳打出，将其轰飞
```

VI:

```text
lao lên, tung một quyền, đánh bay đối phương
```

Thuật toán:

```text
1. Clause segmenter tách bằng comma/顿号/action markers.
2. Detect sequence verbs.
3. Nếu chain >= 3 verbs:
   - dùng dấu phẩy cho các hành động liệt kê.
   - chỉ thêm “rồi” khi có transition rõ.
4. Bảo vệ combat idioms như 一拳打出, 一剑斩下.
```

---

### A7. Topic-comment

```text
ZH: 这门功法，他已经修炼了百年
VI: môn công pháp này, hắn đã tu luyện trăm năm rồi
```

Rule:

```text
Topic + ， + Comment → Topic + , + Comment
```

Nếu topic không có comma nhưng là fronted object:

```text
那本书我看过
→ cuốn sách đó, tôi từng đọc rồi
```

Heuristic:

```text
if initial NP not subject of following verb and object appears omitted:
  insert comma after topic
```

---

## PART B — Logic / Clause Relations

### B1. Conditional giả định `若是/如果/倘若/要是/若`

```text
ZH: 若是他来了，我就走
VI: nếu hắn đến, ta sẽ đi
```

Rule:

```text
若是/如果/倘若/要是 + C1, 就/便 + C2
→ nếu + C1, thì + C2
```

Nếu không có `就`:

```text
若是他来了，我走
→ nếu hắn đến, ta sẽ đi
```

#### Edge cases

```text
若是如此 → nếu là như vậy
若非如此 → nếu không phải như vậy
```

---

### B2. Điều kiện đủ `只要...就...`

```text
ZH: 只要你愿意，就可以活下去
VI: chỉ cần ngươi bằng lòng, thì có thể sống tiếp
```

Rule:

```text
只要 + C1 + 就/便 + C2 → chỉ cần + C1, thì + C2
```

Phân biệt với `只有...才`.

---

### B3. Điều kiện cần `只有...才...`

```text
ZH: 只有活下去，才有希望
VI: chỉ khi sống tiếp, mới có hy vọng
```

Rule:

```text
只有 + C1 + 才 + C2 → chỉ khi/chỉ có + C1, mới + C2
```

Anti-confusion:

```text
只要 = sufficient condition → chỉ cần
只有 = necessary condition → chỉ khi/chỉ có
```

---

### B4. Điều kiện tức thời `一旦...就/便...`

```text
ZH: 一旦失败，就会死亡
VI: một khi thất bại, sẽ chết
```

Rule:

```text
一旦 + C1 + 就/便 + C2 → một khi + C1, thì + C2
```

---

### B5. Loại trừ `除非...否则/不然...`

```text
ZH: 除非你离开，否则必死
VI: trừ khi ngươi rời đi, nếu không chắc chắn sẽ chết
```

Rule:

```text
除非 + C1 + 否则/不然 + C2
→ trừ khi + C1, nếu không + C2
```

---

### B6. Universal condition `凡是...都...`

```text
ZH: 凡是进入者都会死亡
VI: phàm là kẻ tiến vào đều sẽ chết
```

Rule:

```text
凡是 + NP/Clause + 都 + Predicate
→ phàm là / bất cứ + NP/Clause + đều + Predicate
```

Chọn:

```text
- phàm là: cổ/xianxia/formal
- bất cứ: hiện đại
```

---

### B7. Exhaustive concessive `无论/不管...都/也...`

```text
ZH: 无论是谁都无法逃脱
VI: bất kể là ai cũng không thể trốn thoát
```

Rule:

```text
无论/不管 + X + 都/也 + Y
→ bất kể/dù + X + cũng/đều + Y
```

Pattern mở rộng:

```text
无论是 A 还是 B，都 C
→ dù là A hay B, đều C
```

---

### B8. Concession `虽然...但是/但/却/不过...`

```text
ZH: 虽然他受伤了，但依然站着
VI: tuy hắn bị thương, nhưng vẫn đứng đó
```

Rule:

```text
虽然/虽 + C1 + 但是/但/却/不过 + C2
→ tuy + C1, nhưng + C2
```

Nếu có `依然/仍然`:

```text
→ nhưng vẫn + predicate
```

---

### B9. Extreme concession `即便/即使/哪怕/纵然...也...`

```text
ZH: 哪怕是死，他也不会退
VI: cho dù có chết, hắn cũng sẽ không lùi
```

Rule:

```text
即便/即使/哪怕/纵然 + C1 + 也/都 + C2
→ cho dù/dù cho + C1, cũng/vẫn + C2
```

Chọn `vẫn` nếu C2 có persistence:

```text
也不会退 → vẫn sẽ không lùi
也要去 → vẫn phải đi
```

---

### B10. Correction contrast `不是...而是... / 并非...而是...`

```text
ZH: 这不是梦，而是现实
VI: đây không phải là mơ, mà là hiện thực
```

Rule:

```text
不是/并非 + A + 而是 + B
→ không phải + A, mà là + B
```

Nếu không có `而是`:

```text
并非如此 → không phải như vậy / chẳng phải như vậy
```

---

### B11. Progressive addition `不仅/不但...而且/还/也...`

```text
ZH: 他不但活着，而且变强了
VI: hắn không những còn sống, mà còn trở nên mạnh hơn
```

Rule:

```text
不但/不仅 + C1 + 而且/还/也 + C2
→ không những + C1, mà còn + C2
```

---

### B12. Preference contrast `与其...不如...`

```text
ZH: 与其等死，不如拼命
VI: thay vì chờ chết, chi bằng liều mạng
```

Rule:

```text
与其 + A + 不如 + B
→ thay vì + A, chi bằng/thà + B
```

---

### B13. Dual attribute `既...又...`

```text
ZH: 既强大又危险
VI: vừa mạnh mẽ vừa nguy hiểm
```

Rule:

```text
既 + A + 又 + B → vừa + A + vừa + B
```

Paradox:

```text
既是...又非是...
→ vừa là..., lại vừa không phải...
```

---

### B14. Temporal delayed completion `直到...才...`

```text
ZH: 直到天亮他才离开
VI: mãi đến khi trời sáng hắn mới rời đi
```

Rule:

```text
直到 + T/C1 + 才 + C2
→ mãi đến khi/cho đến khi + T/C1, mới + C2
```

Corpus pattern:

```text
直到减少到三十七为止才彻底消失
→ mãi cho đến khi giảm xuống còn 37 mới hoàn toàn biến mất
```

---

### B15. Immediate sequence `一...就... / 刚...就... / 刚一...就...`

```text
ZH: 他刚一进入，就看到了光柱
VI: hắn vừa tiến vào đã nhìn thấy cột sáng
```

Rule:

```text
刚/刚一/一 + V1 + 就 + V2
→ vừa + V1 + đã + V2
```

Phân biệt `一` số lượng:

```text
一本书 → một cuốn sách, không phải immediate sequence
```

---

### B16. Sequential `先...再/然后/接着/之后...`

```text
ZH: 先兑换，再进入
VI: đổi trước, rồi mới tiến vào
```

Rule:

```text
先 + A + 再/然后/接着 + B
→ trước tiên + A, rồi/sau đó + B
```

---

### B17. Cause-result `因为/由于/正因为...所以/因此...`

```text
ZH: 因为他太弱，所以无法进入
VI: vì hắn quá yếu, nên không thể tiến vào
```

Rule:

```text
因为/由于 + C1 + 所以/因此 + C2
→ vì/do + C1, nên/vì vậy + C2
```

`正因为如此`:

```text
正因为如此，他才选择离开
→ chính vì vậy, hắn mới chọn rời đi
```

---

### B18. Result/cause verbs `使得/导致/造成/令`

```text
ZH: 这导致他死亡
VI: điều này dẫn đến cái chết của hắn / khiến hắn chết
```

Rule:

```text
X + 导致/造成 + Y → X dẫn đến/gây ra Y
X + 使得/令 + Y + predicate → X khiến Y predicate
```

---

### B19. Purpose `为了/以便/用来/用于`

```text
ZH: 为了活下去，他必须战斗
VI: để sống tiếp, hắn bắt buộc phải chiến đấu
```

Rule:

```text
为了 + purpose + C → để + purpose, C
以便 + C → để/nhằm + C
用来/用于 + V/N → dùng để/dùng cho + V/N
```

---

### B20. Method/instrument `通过/凭借/依靠/靠着/以/用...来...`

```text
ZH: 通过修炼获得力量
VI: thông qua tu luyện mà đạt được sức mạnh

ZH: 用积分来兑换
VI: dùng điểm để đổi
```

Rule:

```text
通过/凭借/依靠/靠着 + Method + V
→ thông qua/dựa vào/nhờ + Method + mà V

用/以 + X + 来 + V
→ dùng/lấy + X + để + V
```

---

### B21. Topic / stance preposition `对于/关于/至于/对...来说/而言`

```text
ZH: 对于他来说，这很重要
VI: đối với hắn mà nói, chuyện này rất quan trọng
```

Rule:

```text
对于/对 + X + 来说/而言 + C
→ đối với X mà nói, C

关于 + X + C
→ về X, C

至于 + X + C
→ còn về X thì C
```

---

### B22. Accompanying change `随着...`

```text
ZH: 随着时间流逝，他变强了
VI: theo thời gian trôi qua, hắn đã mạnh lên
```

Rule:

```text
随着 + event/process + C
→ theo/cùng với + event/process, C
```

---

### B23. Totality / scope / polarity

#### B23.1 `没有任何`

```text
ZH: 没有任何希望
VI: không có bất kỳ hy vọng nào
```

Rule:

```text
没有任何 + N → không có bất kỳ + N + nào
```

#### B23.2 `几乎都`

```text
ZH: 几乎都死了
VI: gần như đều đã chết
```

#### B23.3 `全部/全都/尽数/统统`

```text
ZH: 敌人尽数死亡
VI: kẻ địch đều chết sạch / toàn bộ kẻ địch đều chết
```

Rule:

```text
全部/全都/统统 → toàn bộ/đều
尽数 → toàn bộ/đều, thường có sắc thái “hết sạch”
```

---

### B24. Modal / necessity / ability / compulsion

#### B24.1 Bắt buộc

```text
必须 → bắt buộc phải / nhất định phải
需得 → cần phải / phải
一定要 → nhất định phải
```

#### B24.2 Bất đắc dĩ

```text
不得不 → không thể không / đành phải
只能够/只能 → chỉ có thể
```

#### B24.3 Không thể

```text
无法 → không thể
不能够 → không thể
难以 → khó mà
```

#### B24.4 Có thể / đủ để

```text
足以 → đủ để
得以 → có thể / nhờ đó mà
能够 → có thể
可以 → có thể / được phép
```

#### B24.5 Tự phát tâm lý

```text
不由得 → bất giác / không khỏi
忍不住 → không nhịn được
```

Ví dụ:

```text
他不由得笑了起来
→ hắn bất giác bật cười

他忍不住问道
→ hắn không nhịn được hỏi
```

---

### B25. Evidential / appearance `看起来/似乎/仿佛/好像`

```text
ZH: 他看起来很平静
VI: hắn trông có vẻ rất bình tĩnh

ZH: 仿佛什么都没有发生
VI: cứ như thể chẳng có gì xảy ra
```

Rule:

```text
看起来 → trông có vẻ
似乎/好像 → dường như / có vẻ như
仿佛 → như thể / tựa như
```

---

### B26. Rhetorical questions

Markers:

```text
难道, 岂, 岂不是, 莫非, 何必, 怎么可能, 又怎么会, 不是吗
```

Rules:

```text
难道 + Q + 吗？ → chẳng lẽ + Q + sao?
岂不是 + P？ → chẳng phải là + P + sao?
莫非 + P？ → chẳng lẽ / lẽ nào + P?
何必 + V？ → hà tất phải + V?
怎么可能 + V？ → sao có thể + V được?
```

Ví dụ:

```text
难道他真的死了？
→ chẳng lẽ hắn thật sự đã chết sao?

这岂不是找死？
→ đây chẳng phải là tìm chết sao?
```

---

### B27. Dialogue, author-note, forum, system boundary

#### B27.1 Dialogue

Phải giữ dấu:

```text
“...”
「...」
『...』
```

Rule:

```text
- Không merge thoại với narration.
- Không reorder vượt qua quote boundary.
- Nội dung trong quote vẫn được grammar transfer riêng.
```

#### B27.2 Inner thought

Markers:

```text
心想, 暗道, 想到, 念头, 脑海中
```

VI:

```text
thầm nghĩ, nghĩ thầm, trong lòng nghĩ, trong đầu hiện lên
```

#### B27.3 System prompt / game notification

Corpus vô hạn lưu có dạng:

```text
【任务完成】
奖励点数：5000
支线剧情：C级一个
```

Rule:

```text
- Bảo vệ bracket/block format.
- Dịch nhãn hệ thống bằng glossary.
- Số/tài nguyên dùng ResourceNumberConverter.
```

#### B27.4 Author-note / forum title

Các chương 201–300 có dạng title/forum/game commentary, ví dụ:

```text
血族转职利弊分析一二帖
奖励点数使用计划白皮书
```

Rule:

```text
- Treat as title/entity-like span.
- Không phân tách máy móc từng cụm ngữ pháp.
- Dịch theo nominal title policy.
```

---

## PART C — Complement / Result / Degree

### C1. Resultative complement

Patterns:

```text
V 完, V 好, V 出, V 开, V 住, V 下, V 死, V 光, V 破, V 断, V 成, V 到
```

Examples:

```text
看完 → đọc/xem xong
打开 → mở ra
打死 → đánh chết
杀光 → giết sạch
打破 → đánh vỡ / phá vỡ
变成 → biến thành
找到 → tìm thấy
```

Rule:

```text
V + RCOMP → V + complement_vi
```

Mapping:

```text
完 → xong
好 → xong/tốt
出 → ra
开 → ra/mở
住 → lại/được
下 → xuống/lại
死 → chết
光 → sạch/hết
破 → vỡ/phá
断 → đứt/gãy
成 → thành
到 → tới/được/thấy
```

---

### C2. Potential complement `V得/不 + RCOMP`

```text
ZH: 看得见
VI: nhìn thấy được

ZH: 走不出去
VI: không đi ra được
```

Rule:

```text
V + 得 + RCOMP → V + RCOMP_vi + được
V + 不 + RCOMP → không + V + RCOMP_vi + được
```

Examples:

```text
打不过 → đánh không lại
活不下去 → không sống tiếp được
跑不掉 → không chạy thoát được
```

---

### C3. Degree complement `得`

```text
ZH: 他跑得很快
VI: hắn chạy rất nhanh
```

Rule:

```text
V + 得 + degree phrase → V + degree phrase
```

Examples:

```text
痛得发抖 → đau đến run rẩy
强得离谱 → mạnh đến vô lý
快得不可思议 → nhanh đến khó tin
```

#### Guard compounds

Không tách `得` trong:

```text
觉得, 记得, 显得, 懂得, 获得, 取得, 得到, 得以
```

Rule:

```text
if token in 得_compound_guard:
  treat as lexical verb/adverb, not complement marker
```

---

### C4. Extent/result `到...为止 / 到...程度`

```text
ZH: 直到减少到三十七为止
VI: mãi cho đến khi giảm xuống còn 37
```

Rule:

```text
V + 到 + target + 为止 → V đến mức/tới khi + target
```

---

## PART D — Formal / Classical / Xianxia Constructions

### D1. `所` constructions

#### D1.1 `所 + V + 的 + N`

```text
ZH: 他所说的话
VI: lời hắn nói
```

Rule:

```text
S + 所 + V + 的 + N → N + S + V
```

#### D1.2 `所 + V` nominalization

```text
ZH: 所见所闻
VI: những điều thấy nghe
```

Rule:

```text
所 + V → điều/thứ được V / điều V
```

#### D1.3 `所以` guard

```text
所以 → vì vậy/cho nên
```

Không tách thành `所 + 以`.

#### D1.4 `所有` guard

```text
所有人 → tất cả mọi người
所有的 → tất cả
```

Không tách `所 + 有`.

---

### D2. `之` constructions

#### D2.1 Possessive/literary `A 之 B`

```text
ZH: 天道之力
VI: sức mạnh của Thiên Đạo
```

Rule:

```text
A + 之 + B → B của A
```

#### D2.2 Locative `之中/之上/之下/之后/之前`

```text
其中 → trong đó
世界之中 → trong thế giới
战斗之后 → sau trận chiến
```

Rule:

```text
A + 之中 → trong A
A + 之后 → sau A
A + 之前 → trước A
```

#### D2.3 Idiom guard

Không tách:

```text
总之 → tóm lại
换言之 → nói cách khác
久而久之 → lâu dần
反之 → ngược lại
```

---

### D3. `以...为...`

#### D3.1 Regard as

```text
ZH: 以他为首
VI: lấy hắn làm thủ lĩnh / do hắn đứng đầu
```

#### D3.2 Use as

```text
ZH: 以血为引
VI: lấy máu làm vật dẫn
```

#### D3.3 Take X as Y

```text
ZH: 以天地为炉
VI: lấy trời đất làm lò luyện
```

Rule:

```text
以 + X + 为 + Y → lấy X làm Y / coi X là Y
```

Chọn:

```text
- lấy X làm Y: xianxia/ritual/formal
- coi/xem X là Y: modern/evaluative
```

---

### D4. `以...来 / 用...来`

```text
ZH: 以此来证明
VI: dùng điều này để chứng minh
```

Rule:

```text
以/用 + X + 来 + V → dùng/lấy + X + để + V
```

---

### D5. `名为/称为/叫做/所谓`

```text
ZH: 名为主神空间的地方
VI: nơi gọi là Chủ Thần Không Gian

ZH: 所谓的命运
VI: cái gọi là vận mệnh
```

Rules:

```text
名为/称为/叫做 + X → gọi là X
所谓的 + X → cái gọi là X
```

---

## PART E — Long Nominal Chains

### E1. Vấn đề

Corpus có nhiều danh ngữ dài không có `的`, ví dụ:

```text
最初主神空间
天道眷属值来源
血红玫瑰冒险团
中央戊土厚德诀
洪荒万族第九千七百一十一位低等地精族
m国第五代主战斗机所有资料
奖励点数使用计划白皮书
魔法工业革命临界点
```

Nếu tokenizer tách sai, lexical transfer sẽ hỏng thứ tự.

### E2. Thuật toán Nominal Chain Parser

```text
Input tokens: [modifier/entity/rank/number/core/suffix]

1. Detect core head by suffix:
   团, 族, 国, 城, 界, 位面, 空间, 功, 诀, 法, 刀, 剑, 阵, 值, 点数, 计划, 白皮书, 资料

2. Detect left modifiers:
   color, rank, domain, proper name, faction, number, generation, level

3. Protect full span if:
   - contains known entity suffix
   - contains system term
   - contains proper-name seed
   - contains number that belongs to title/rank/name

4. Render VI by type.
```

### E3. Translation policy

#### E3.1 System/game terms

```text
主神空间 → Chủ Thần Không Gian
奖励点数 → điểm thưởng
支线剧情 → tình tiết nhánh
天道眷属值 → điểm thân thuộc Thiên Đạo
轮回世界 → thế giới luân hồi
公众副本 → phó bản công cộng
```

#### E3.2 Faction/group

```text
血红玫瑰冒险团 → Đoàn mạo hiểm Huyết Hồng Mai Côi
商业联盟 → Liên minh Thương nghiệp
血族会议 → hội nghị Huyết tộc
```

#### E3.3 Cultivation / technique

```text
中央戊土厚德诀 → Trung Ương Mậu Thổ Hậu Đức Quyết
上清诛仙功残篇 → tàn thiên Thượng Thanh Tru Tiên Công
一阶基因锁 → khóa gene bậc một
```

#### E3.4 Long administrative / tech title

```text
奖励点数使用计划白皮书
→ Sách trắng kế hoạch sử dụng điểm thưởng

魔法工业革命临界点
→ điểm tới hạn của cách mạng công nghiệp ma pháp
```

---

## PART F — Number & Format Conversion

### F1. Nguyên tắc chung

Không chuyển số bằng một rule duy nhất. Phải phân loại context trước:

```text
NumberContext:
- COUNT
- ORDINAL
- DURATION
- DEADLINE
- COUNTDOWN
- DATE_TIME
- AGE
- CENTURY
- RANGE
- APPROX
- PERCENT
- FRACTION
- MULTIPLIER
- RANK_LEVEL
- GAME_RESOURCE
- MEASUREMENT
- CHAPTER_TITLE
- ENTITY_PROTECTED
```

Pipeline:

```text
1. Detect numeric span.
2. Check if inside protected entity.
3. If protected → do not numeric-convert unless entity policy allows.
4. Else classify context by unit/suffix/prefix.
5. Convert with specialized converter.
6. Return trace.
```

---

### F2. Basic number

```text
一 → một
二 → hai
三 → ba
十 → mười
三十七 → ba mươi bảy / 37 tùy context
一百二十 → một trăm hai mươi / 120
五千 → năm nghìn / 5.000
```

Policy:

```text
- Narrative natural count: chữ tiếng Việt.
- Game/system/resource/stat: chữ số Arabic.
- Large resource/currency: 5.000, 10.000.
```

---

### F3. Duration / deadline / countdown

```text
三十秒内 → trong vòng 30 giây
4个小时 → 4 giờ
每二十四小时 → mỗi 24 giờ
七天之后 → sau 7 ngày
两个月 → hai tháng / 2 tháng
```

Rules:

```text
NUM + 秒/分钟/小时/天/月/年 + 内
→ trong vòng + NUM + giây/phút/giờ/ngày/tháng/năm

NUM + 个 + 小时
→ NUM + giờ

每 + NUM + unit
→ mỗi + NUM + unit
```

---

### F4. Time chronology

```text
第一分二十八秒
→ phút thứ 1 giây thứ 28 / 1 phút 28 giây
```

Rule:

```text
第 + NUM + 分 + NUM + 秒
→ NUM phút NUM giây
```

Nếu là ranking minute:

```text
第一分钟 → phút đầu tiên
```

---

### F5. Date / age / century

```text
十八岁 → 18 tuổi
二十一世纪 → thế kỷ 21
第一年 → năm đầu tiên
第三天 → ngày thứ ba
```

Rules:

```text
NUM + 岁 → NUM tuổi
第 + NUM + 天/月/年 → ngày/tháng/năm thứ NUM
NUM + 世纪 → thế kỷ NUM
```

---

### F6. Range / approximate

```text
三四个 → ba bốn cái
三到五个 → từ ba đến năm cái
三五天 → ba năm ngày / vài ngày
数十人 → mấy chục người
上百人 → hơn trăm người
近千人 → gần nghìn người
```

Rules:

```text
A 到 B + unit → từ A đến B + unit
A 至 B + unit → từ A đến B + unit
A-B → A-B / từ A đến B tùy format
三四 + unit → ba bốn + unit
数十 → mấy chục
数百 → mấy trăm
上百 → hơn trăm
近千 → gần nghìn
```

---

### F7. Percent / probability

```text
百分之三十 → 30%
三成 → ba phần / 30%
七成把握 → bảy phần chắc chắn / 70% nắm chắc
```

Rules:

```text
百分之 + NUM → NUM%
NUM + 成 + chance/confidence → NUM phần / NUM*10%
```

Choice:

```text
- technical/system: 30%
- narrative confidence: ba phần, bảy phần
```

---

### F8. Fraction

```text
三分之一 → một phần ba
十分之一 → một phần mười
二分之一 → một nửa
```

Rule:

```text
DENOM + 分之 + NUMERATOR
→ NUMERATOR phần DENOM
```

Special:

```text
二分之一 → một nửa
```

---

### F9. Multiplier / fold / times

```text
三倍 → gấp ba lần
数倍 → gấp mấy lần
十倍以上 → trên gấp mười lần
第一次 → lần đầu tiên
三次 → ba lần
```

Rule:

```text
NUM + 倍 → gấp NUM lần
NUM + 次 → NUM lần
第 + NUM + 次 → lần thứ NUM
```

---

### F10. Rank / level / tier / generation

```text
一阶 → bậc một / cấp một
二阶基因锁 → khóa gene bậc hai
c级支线剧情 → tình tiết nhánh cấp C
第五代主战斗机 → máy bay chiến đấu chủ lực thế hệ thứ năm
低等地精族 → chủng Địa Tinh cấp thấp
第九千七百一十一位 → vị thứ 9.711
```

Rules:

```text
一阶/二阶/三阶 → bậc một/hai/ba
A/B/C/S级 → cấp A/B/C/S
第 + NUM + 代 → thế hệ thứ NUM
第 + NUM + 位 → vị thứ NUM
低等/中等/高等 → cấp thấp/trung/cao
```

Protected cases:

```text
一阶基因锁 → protected term with rank, not plain “một bậc gene lock”
中央戊土厚德诀 → number-like/element-like terms not numeric context
八卦符文 → Bát Quái phù văn, not “tám quẻ” unless glossary says
```

---

### F11. Game/resource quantities

```text
五千奖励点数 → 5.000 điểm thưởng
一个c级支线剧情 → một tình tiết nhánh cấp C
三枚符文 → ba phù văn
十万天道眷属值 → 100.000 điểm thân thuộc Thiên Đạo
```

Rules:

```text
NUM + 奖励点数 → NUM + điểm thưởng
NUM + 天道眷属值 → NUM + điểm thân thuộc Thiên Đạo
NUM + 级支线剧情 → tình tiết nhánh cấp NUM/LETTER
NUM + 枚/颗/件 + item → NUM + item, classifier usually dropped
```

---

### F12. Measurement / physical units

```text
三米 → 3 mét
十公里 → 10 km / 10 ki-lô-mét
一公斤 → 1 kg / một ký
```

Policy:

```text
- Technical/system: use Arabic + unit.
- Narrative: can use Vietnamese words if short.
```

---

### F13. Chapter title number/range

```text
第二十九，三十章 → chương 29, 30
第四十五，六章 → chương 45, 46
上，下 / 上，中，下 → thượng, hạ / thượng, trung, hạ hoặc phần trên/dưới
```

Rule:

```text
chapter title context → preserve title formatting, convert chapter numbers consistently.
```

---

## PART G — Entity Recognition Rules

### G1. Entity types cần nhận diện

```text
PERSON             nhân vật
FACTION            thế lực, tổ chức, môn phái, đoàn đội
RACE               chủng tộc
PLACE              địa danh, thành, quốc gia, vị diện, không gian
SYSTEM_TERM        thuật ngữ hệ thống/game/vô hạn lưu
CULTIVATION        cảnh giới, cấp bậc tu luyện
TECHNIQUE          công pháp, pháp quyết, kỹ năng, thần thông
ARTIFACT           pháp bảo, vật phẩm, linh bảo, đạo cụ
WEAPON             vũ khí
EQUIPMENT          trang bị
RESOURCE           điểm thưởng, điểm thân thuộc, chi phí, tiền tệ
TITLE_RANK         chức danh, danh hiệu, bậc, cấp
BOOK_DOC_TITLE     sách, bạch thư, tư liệu, kế hoạch
EVENT_MISSION      nhiệm vụ, phó bản, chiến dịch, sự kiện
```

---

### G2. Suffix-based entity detection

#### G2.1 Person/title

```text
者, 人, 主, 王, 皇, 帝, 圣, 神, 魔, 仙, 尊, 师, 徒, 兄, 弟, 姐, 妹
```

Examples:

```text
智者, 主人, 大领主, 人皇, 圣位, 魔法师
```

#### G2.2 Faction/group

```text
族, 国, 城, 团, 队, 盟, 会, 宗, 门, 派, 教, 军, 部落, 冒险团, 商团, 雇佣兵
```

Examples:

```text
血族, 商业联盟, 血红玫瑰冒险团, 钢铁部落
```

#### G2.3 Place/world

```text
界, 位面, 空间, 世界, 地府, 血海, 地狱, 学院都市, 福地, 领地, 地底裂缝
```

Examples:

```text
主神空间, 轮回世界, 外位面, 机械境, 银色大地
```

#### G2.4 Technique/cultivation

```text
功, 法, 诀, 经, 术, 神通, 符文, 阵, 剑阵, 基因锁, 金丹, 元婴, 筑基
```

Examples:

```text
中央戊土厚德诀, 上清诛仙功残篇, 诛仙剑阵, 一阶基因锁
```

#### G2.5 Artifact/weapon/equipment

```text
刀, 剑, 镜, 图, 炉, 阵, 宝, 灵宝, 机甲, 巨神兵, 导弹, 罗盘
```

Examples:

```text
化血神刀, 昊天镜, 巨神兵, 洪荒级缩爆弹导弹系列
```

#### G2.6 System/game/resource

```text
点数, 支线剧情, 副本, 任务, 兑换, 权限, 标签, 倒计时, 资格, 奖励
```

Examples:

```text
奖励点数, 支线剧情, 公众副本, 首测资格, 轮回世界倒计时
```

---

### G3. Prefix-based entity detection

```text
最初, 初代, 中央, 上清, 洪荒, 先天, 后天, 天道, 主神, 轮回, 血红, 幽冥, 大罗, 玄黄
```

Examples:

```text
最初主神空间
初代主神空间
中央戊土厚德诀
上清诛仙功残篇
洪荒万兽诛仙阵
先天灵宝
后天灵宝
天道眷属值
```

---

### G4. Number-containing entity protection

Phải bảo vệ số khi số là một phần của tên/cấp/thuật ngữ:

```text
一阶基因锁
第五代主战斗机
三大灾
八卦符文
九箭模因
三秒套餐
十万是个好数字
大罗星斗鸿蒙阵
洪荒万族第九千七百一十一位低等地精族
```

Rule:

```text
if numeric span inside entity candidate:
  classify as ENTITY_PROTECTED or RANK_LEVEL, not generic count
```

---

### G5. Han-Viet transliteration policy

#### G5.1 Person names

```text
吴明 → Ngô Minh
郑吒 → Trịnh Tra
楚轩 → Sở Hiên
```

Policy:

```text
- Dùng Han-Viet nếu chưa có glossary.
- Giữ nhất quán qua entity_memory.
```

#### G5.2 Faction/technique/artifact names

```text
中央戊土厚德诀 → Trung Ương Mậu Thổ Hậu Đức Quyết
化血神刀 → Hóa Huyết Thần Đao
昊天镜 → Hạo Thiên Kính
```

Policy:

```text
- Công pháp/pháp bảo: ưu tiên Hán-Việt.
- Có thể thêm nghĩa nếu glossary yêu cầu.
```

#### G5.3 System/game terms

```text
主神空间 → Chủ Thần Không Gian
奖励点数 → điểm thưởng
支线剧情 → tình tiết nhánh
副本 → phó bản
```

Policy:

```text
- Thuật ngữ hệ thống: ưu tiên bản dịch nghĩa ổn định.
- Không transliterate máy móc nếu term đã phổ biến.
```

---

### G6. Alias/coreference

Cần lưu:

```text
吴明 = 他 = 主人 = 大领主   tùy context
主神空间 = 最初主神空间 = 初代主神空间  nếu corpus xác nhận
```

Data structure:

```python
@dataclass
class EntityRecord:
    zh: str
    vi: str
    entity_type: str
    aliases: list[str]
    first_seen_chapter: int
    confidence: float
    source: str       # glossary | detected | user_confirmed
```

---

## PART H — Rule Priority sau khi hợp nhất

Thứ tự rule đề xuất:

```text
00. Preserve/protect spans
    - quote, dialogue, system prompt, HTML/title boundary
    - entity spans
    - protected number spans

05. Clause segmentation
    - split long sentence into manageable clauses
    - detect relation markers

10. Logic frame rules
    - condition
    - concession
    - contrast
    - cause-result
    - temporal relation

20. Topic/stance/preposition frame
    - 对于/关于/至于/作为/随着

30. Formal/classical frame
    - 所
    - 之
    - 以...为
    - 由/为...所

40. Core structural rules
    - BA/将 disposal
    - BEI passive
    - DE inversion
    - nominal chain

50. Verb local rules
    - aspect
    - directional complement
    - resultative complement
    - potential complement
    - degree complement

60. Serial/action chain rules
    - sequential
    - purpose
    - manner
    - combat chain

70. Number/format rendering
    - duration
    - percent/fraction
    - resource
    - rank/level
    - measurement

80. Entity rendering
    - Han-Viet transliteration
    - glossary selection
    - alias memory

90. Dialogue/system formatting

99. Postprocess cleanup
```

---

## PART I — Data files cần bổ sung

### I1. `logic_markers.json`

```json
{
  "condition_if": ["若是", "如果", "倘若", "要是", "若"],
  "condition_sufficient": ["只要"],
  "condition_necessary": ["只有"],
  "condition_once": ["一旦"],
  "unless": ["除非"],
  "otherwise": ["否则", "不然"],
  "then": ["就", "便", "则"],
  "universal": ["凡是"],
  "regardless": ["无论", "不管"]
}
```

### I2. `contrast_markers.json`

```json
{
  "although": ["虽然", "虽"],
  "but": ["但是", "但", "却", "不过", "然而", "可"],
  "even_if": ["即便", "即使", "哪怕", "纵然"],
  "not_but": ["不是", "并非", "并不是"],
  "rather": ["而是"],
  "not_only": ["不但", "不仅"],
  "also": ["而且", "还", "也"],
  "prefer_a": ["与其"],
  "prefer_b": ["不如"]
}
```

### I3. `modal_markers.json`

```json
{
  "must": ["必须", "需得", "一定要"],
  "have_to": ["不得不"],
  "only_can": ["只能", "只能够"],
  "cannot": ["无法", "不能", "不能够"],
  "difficult": ["难以"],
  "enough_to": ["足以"],
  "can_thus": ["得以"],
  "involuntary": ["不由得"],
  "cannot_help": ["忍不住"]
}
```

### I4. `classical_markers.json`

```json
{
  "zhi_possessive": ["之"],
  "suo": ["所"],
  "yi": ["以"],
  "wei": ["为"],
  "formal_passive": ["由", "为", "所"],
  "guard_words": ["所以", "所有", "总之", "换言之", "久而久之", "反之"]
}
```

### I5. `rhetorical_markers.json`

```json
{
  "rhetorical": ["难道", "岂", "岂不是", "莫非", "何必", "怎么可能", "又怎么会"],
  "question_particles": ["吗", "呢", "吧", "啊"],
  "exclamation": ["啊", "呀", "嘛", "啦"]
}
```

### I6. `number_context_patterns.json`

```json
{
  "duration_units": ["秒", "分钟", "分", "小时", "时", "天", "日", "月", "年"],
  "deadline_suffix": ["内", "之内", "以内"],
  "rank_markers": ["第", "阶", "级", "位", "层", "代"],
  "percent_markers": ["百分之", "成"],
  "fraction_marker": "分之",
  "resource_terms": ["奖励点数", "天道眷属值", "支线剧情", "积分", "权限"],
  "approx_prefix": ["数", "近", "上", "约", "大约", "差不多"],
  "range_markers": ["到", "至", "-", "—"]
}
```

### I7. `entity_suffix_patterns.json`

```json
{
  "faction": ["族", "国", "团", "队", "盟", "会", "宗", "门", "派", "部落", "冒险团", "商团"],
  "place": ["界", "位面", "空间", "世界", "地府", "血海", "福地", "领地", "都市"],
  "technique": ["功", "法", "诀", "经", "术", "神通", "符文", "阵", "剑阵"],
  "artifact": ["刀", "剑", "镜", "图", "炉", "宝", "灵宝", "机甲", "罗盘"],
  "system": ["点数", "剧情", "副本", "任务", "权限", "标签", "资格", "奖励"]
}
```

### I8. `system_terms.json`

```json
{
  "主神空间": "Chủ Thần Không Gian",
  "最初主神空间": "Chủ Thần Không Gian ban sơ",
  "轮回世界": "thế giới luân hồi",
  "奖励点数": "điểm thưởng",
  "支线剧情": "tình tiết nhánh",
  "天道眷属值": "điểm thân thuộc Thiên Đạo",
  "公众副本": "phó bản công cộng",
  "基因锁": "khóa gene",
  "兑换": "đổi thưởng",
  "抹杀": "xóa sổ"
}
```

---

## PART J — Test suite tổng hợp

### J1. Grammar tests

```text
tests/test_grammar/test_logic_condition.py
tests/test_grammar/test_concession_contrast.py
tests/test_grammar/test_comparative_degree.py
tests/test_grammar/test_cause_result.py
tests/test_grammar/test_formal_classical.py
tests/test_grammar/test_de_aspect_ba_bei.py
tests/test_grammar/test_complements.py
tests/test_grammar/test_serial_action_chain.py
tests/test_grammar/test_dialogue_rhetorical.py
```

### J2. Number tests

```text
tests/test_numbers/test_duration_deadline.py
tests/test_numbers/test_percent_fraction.py
tests/test_numbers/test_rank_level.py
tests/test_numbers/test_resource_numbers.py
tests/test_numbers/test_range_approx.py
tests/test_numbers/test_protected_number_entity.py
```

### J3. Entity tests

```text
tests/test_entities/test_entity_detector.py
tests/test_entities/test_nominal_entity_parser.py
tests/test_entities/test_hanviet_transliterator.py
tests/test_entities/test_alias_resolver.py
tests/test_entities/test_entity_number_protection.py
```

### J4. Integration corpus tests

```text
tests/test_corpus/test_ch001_100_patterns.py
tests/test_corpus/test_ch101_200_patterns.py
tests/test_corpus/test_ch201_300_patterns.py
```

---

### J5. Test cases bắt buộc — Grammar

```python
GRAMMAR_CASES = [
    ("若是他来了，我就走", "nếu hắn đến, ta sẽ đi", "condition if"),
    ("只要活下去，就有希望", "chỉ cần sống tiếp, thì sẽ có hy vọng", "sufficient condition"),
    ("只有活下去，才有希望", "chỉ khi sống tiếp, mới có hy vọng", "necessary condition"),
    ("除非你离开，否则必死", "trừ khi ngươi rời đi, nếu không chắc chắn sẽ chết", "unless"),
    ("无论是谁都无法逃脱", "bất kể là ai cũng không thể trốn thoát", "regardless"),
    ("虽然他受伤了，但依然站着", "tuy hắn bị thương, nhưng vẫn đứng đó", "concession"),
    ("哪怕是死，他也不会退", "cho dù có chết, hắn cũng sẽ không lùi", "even if"),
    ("这不是梦，而是现实", "đây không phải là mơ, mà là hiện thực", "not but"),
    ("与其等死，不如拼命", "thay vì chờ chết, chi bằng liều mạng", "preference"),
    ("他刚一进入，就看到了光柱", "hắn vừa tiến vào đã nhìn thấy cột sáng", "immediate sequence"),
    ("直到天亮他才离开", "mãi đến khi trời sáng hắn mới rời đi", "until cai"),
    ("他不由得笑了起来", "hắn bất giác bật cười", "involuntary"),
    ("难道他真的死了？", "chẳng lẽ hắn thật sự đã chết sao?", "rhetorical"),
]
```

### J6. Test cases bắt buộc — Number

```python
NUMBER_CASES = [
    ("三十秒内进入光柱", "tiến vào cột sáng trong vòng 30 giây", "deadline"),
    ("第一分二十八秒", "1 phút 28 giây", "timestamp"),
    ("五千奖励点数", "5.000 điểm thưởng", "resource"),
    ("一个c级支线剧情", "một tình tiết nhánh cấp C", "rank resource"),
    ("百分之三十", "30%", "percent"),
    ("三分之一", "một phần ba", "fraction"),
    ("三到五天", "từ ba đến năm ngày", "range"),
    ("数十人", "mấy chục người", "approx"),
    ("第五代主战斗机", "máy bay chiến đấu chủ lực thế hệ thứ năm", "generation"),
    ("一阶基因锁", "khóa gene bậc một", "rank protected"),
]
```

### J7. Test cases bắt buộc — Entity

```python
ENTITY_CASES = [
    ("最初主神空间", "Chủ Thần Không Gian ban sơ", "system place"),
    ("天道眷属值来源", "nguồn gốc điểm thân thuộc Thiên Đạo", "system resource nominal chain"),
    ("血红玫瑰冒险团", "Đoàn mạo hiểm Huyết Hồng Mai Côi", "faction"),
    ("中央戊土厚德诀", "Trung Ương Mậu Thổ Hậu Đức Quyết", "technique"),
    ("上清诛仙功残篇", "tàn thiên Thượng Thanh Tru Tiên Công", "technique fragment"),
    ("化血神刀", "Hóa Huyết Thần Đao", "weapon"),
    ("洪荒万兽诛仙阵", "Hồng Hoang Vạn Thú Tru Tiên Trận", "formation"),
    ("奖励点数使用计划白皮书", "Sách trắng kế hoạch sử dụng điểm thưởng", "document title"),
]
```

---

## PART K — Roadmap triển khai chi tiết

### Sprint K1 — Data + Protected Span Foundation

#### Mục tiêu

Tạo nền cho grammar/number/entity mà không can thiệp sâu vào translator.

#### Tasks

```text
K1.1  Tạo data files:
      - logic_markers.json
      - contrast_markers.json
      - modal_markers.json
      - classical_markers.json
      - rhetorical_markers.json
      - number_context_patterns.json
      - entity_suffix_patterns.json
      - system_terms.json

K1.2  Tạo GrammarData loader cache.

K1.3  Tạo ProtectedSpan model:
      - start/end
      - type
      - source
      - confidence
      - payload

K1.4  Tạo trace schema:
      - rule_name
      - input_span
      - output_span
      - confidence
      - warning

K1.5  Regression test flag-off.
```

#### Acceptance

```text
- Load data thành công.
- Không ảnh hưởng pipeline cũ.
- ProtectedSpan có unit tests.
```

---

### Sprint K2 — Entity Intelligence MVP

#### Tasks

```text
K2.1  entity_suffix_patterns detector.
K2.2  system_terms exact matcher.
K2.3  long nominal entity detector.
K2.4  number-in-entity protector.
K2.5  Han-Viet fallback transliterator.
K2.6  EntityMemory local JSON cache.
```

#### Acceptance

```text
- Detect đúng >85% entity cases trong test set.
- Không numeric-convert sai các cụm như 一阶基因锁, 八卦符文.
- System terms được giữ nhất quán.
```

---

### Sprint K3 — Number Context Converter

#### Tasks

```text
K3.1  number_context_classifier.py
K3.2  duration/deadline converter.
K3.3  percent/fraction converter.
K3.4  rank/level/generation converter.
K3.5  resource number converter.
K3.6  range/approx converter.
K3.7  integration với NumberConverter hiện có.
```

#### Acceptance

```text
- Number tests pass.
- Không phá NumberConverter cũ.
- Có trace cho mỗi numeric conversion.
```

---

### Sprint K4 — Clause Segmenter + LogicRelationDetector

#### Tasks

```text
K4.1  clause_segmenter.py
K4.2  detect condition:
      若是/如果/只要/只有/除非/一旦/凡是
K4.3  detect concession/contrast:
      虽然/即便/不是而是/与其不如/不仅而且
K4.4  detect temporal:
      直到才/刚一就/一就/先再
K4.5  detect cause-result:
      因为所以/导致/使得/令
K4.6  unit tests.
```

#### Acceptance

```text
- Long sentence không bị rewrite vượt clause boundary.
- Logic relations có confidence + trace.
```

---

### Sprint K5 — Formal/Classical Pack

#### Tasks

```text
K5.1  rule_suo.py:
      所 + V, 所 + V + 的 + N, guard 所以/所有

K5.2  rule_zhi.py:
      A之B, 之中/之后, guard 总之/换言之

K5.3  rule_yi_wei.py:
      以X为Y, 以X来V, 用X来V

K5.4  rule_formal_passive.py:
      由/为...所...

K5.5  tests.
```

#### Acceptance

```text
- Cổ văn nhẹ dịch tự nhiên hơn.
- Guard words không bị tách sai.
```

---

### Sprint K6 — Complement Pack

#### Tasks

```text
K6.1  resultative complement map.
K6.2  potential complement V得/不 + result.
K6.3  degree complement 得.
K6.4  得 compound guard.
K6.5  directional complement deepening.
K6.6  tests.
```

#### Acceptance

```text
- 打死/杀光/看完/打不过/痛得发抖 xử lý đúng.
- 觉得/获得/得到 không bị parse sai.
```

---

### Sprint K7 — Long Nominal Chain + Entity Rendering

#### Tasks

```text
K7.1  nominal_entity_parser.py.
K7.2  head suffix detection.
K7.3  modifier chain ordering.
K7.4  render policies by entity type.
K7.5  glossary override support.
K7.6  tests from v7-v11 entity cases.
```

#### Acceptance

```text
- Long nominal chains dịch ổn.
- Entity có số được bảo vệ.
- Tên công pháp/pháp bảo giữ Hán-Việt nhất quán.
```

---

### Sprint K8 — Dialogue/System/Rhetorical Pack

#### Tasks

```text
K8.1  quote boundary detector.
K8.2  inner thought markers.
K8.3  system prompt formatter.
K8.4  rhetorical question transfer.
K8.5  author-note/forum title handling.
K8.6  tests.
```

#### Acceptance

```text
- Không reorder sai trong quote.
- System block giữ format.
- Câu hỏi tu từ chuyển tự nhiên.
```

---

### Sprint K9 — Integration + Corpus Accuracy

#### Tasks

```text
K9.1  Feature flag enable_grammar_transfer_v12.
K9.2  Integrate into RBMT before existing lexical loop.
K9.3  Append traces to CandidateTrace.
K9.4  Run regression tests old 98 tests.
K9.5  Run corpus tests ch1–300.
K9.6  Generate error report by construction type.
```

#### Acceptance

```text
- Flag off: output y như cũ.
- Flag on: grammar corpus tests pass target.
- Zero crash trên sample 300 chương.
```

---

## PART L — Accuracy metrics

### L1. Per-construction accuracy target

```text
DE inversion                  >= 85%
Aspect                        >= 90%
BA/将 disposal                >= 80%
Passive                       >= 85%
Directional complement         >= 85%
Resultative complement         >= 85%
Potential complement           >= 80%
Logic relation                 >= 85%
Formal/classical 所/之/以      >= 80%
Number conversion              >= 90%
Entity detection               >= 85%
Protected number/entity guard  >= 95%
Dialogue/system boundary       >= 95%
```

### L2. Error report format

```text
Construction | Total | Correct | Accuracy | Top Errors
-------------|-------|---------|----------|-----------
DE           | 120   | 104     | 86.7%    | nested DE, hidden head
Number       | 210   | 194     | 92.4%    | entity-number, rank ambiguity
Entity       | 180   | 154     | 85.6%    | long faction title
```

### L3. Trace fields

```python
@dataclass
class GrammarTrace:
    rule: str
    source_text: str
    input_span: tuple[int, int]
    output_text: str
    confidence: float
    protected: bool = False
    warning: str = ""
```

---

## PART M — Known limitations và fallback

### M1. Long nested grammar

Với câu cực dài nhiều mệnh đề lồng nhau:

```text
- Không cố parse full dependency tree.
- Segment theo clause trước.
- Apply local transfer trong từng clause.
- Nếu confidence thấp, fallback lexical order.
```

### M2. Entity ambiguity

```text
主神 có thể là title/entity.
圣位 có thể là rank/entity/state.
```

Fallback:

```text
- Nếu có trong glossary: dùng glossary.
- Nếu suffix strongly indicates entity: protect.
- Nếu confidence thấp: transliterate + mark review.
```

### M3. Number ambiguity

```text
三成: 30% hay ba phần?
一阶: bậc một hay một bậc?
第五代: thế hệ thứ năm hay đời thứ năm?
```

Fallback:

```text
- context resource/system → Arabic/stat style.
- narrative/cultivation → Vietnamese rank style.
- protected entity → không đổi số tùy tiện.
```

### M4. `将` ambiguity

```text
将离开 → future
将敌人杀死 → disposal
将能量化为火焰 → conversion
```

Fallback:

```text
if 将 + 会/要/V directly:
  future
elif 将 + NP + V:
  disposal/formal object-fronting
else:
  leave lexical and trace warning
```

---

## PART N — Checklist tổng hợp

### N1. Grammar core

- [ ] DE inversion nâng cao.
- [ ] Aspect 了/着/过/正在/将要.
- [ ] Passive 被/由所/为所/受到/遭到.
- [ ] BA/将/给 disposal.
- [ ] Directional complement.
- [ ] Serial verb/action chain.
- [ ] Topic-comment.
- [ ] Resultative complement.
- [ ] Potential complement.
- [ ] Degree complement.

### N2. Logic relations

- [ ] 若是/如果/倘若/要是.
- [ ] 只要...就.
- [ ] 只有...才.
- [ ] 除非...否则.
- [ ] 一旦...就.
- [ ] 凡是...都.
- [ ] 无论/不管...都.
- [ ] 虽然...但是/却.
- [ ] 即便/哪怕...也.
- [ ] 不是...而是.
- [ ] 不仅...而且.
- [ ] 与其...不如.
- [ ] 直到...才.
- [ ] 刚一...就.
- [ ] 因为...所以.
- [ ] 导致/使得/令.

### N3. Formal/classical

- [ ] 所 + V.
- [ ] 所 + V + 的 + N.
- [ ] 所以/所有 guards.
- [ ] A之B.
- [ ] 之中/之后/之前.
- [ ] 总之/换言之 guards.
- [ ] 以X为Y.
- [ ] 以X来V / 用X来V.
- [ ] 名为/称为/所谓.

### N4. Numbers

- [ ] Basic Chinese numbers.
- [ ] Deadline/duration/countdown.
- [ ] Timestamp.
- [ ] Age/century/date.
- [ ] Range/approx.
- [ ] Percent.
- [ ] Fraction.
- [ ] Multiplier/frequency.
- [ ] Rank/level/tier/generation.
- [ ] Game/resource quantities.
- [ ] Measurement units.
- [ ] Chapter title numbers.
- [ ] Protected number in entity.

### N5. Entity

- [ ] Person names.
- [ ] Factions/groups.
- [ ] Races.
- [ ] Places/worlds/planes.
- [ ] System/game terms.
- [ ] Cultivation levels.
- [ ] Techniques.
- [ ] Artifacts/weapons/equipment.
- [ ] Resource terms.
- [ ] Long nominal chain.
- [ ] Alias/coreference.
- [ ] Han-Viet fallback.

### N6. Formatting

- [ ] Quote boundary.
- [ ] Inner thought.
- [ ] System prompt block.
- [ ] Forum/title handling.
- [ ] Rhetorical question.
- [ ] Sentence particles.
- [ ] Punctuation spacing.
- [ ] Duplicate marker cleanup.

---

## PART O — Kết luận triển khai

Bản v12 hợp nhất toàn bộ nội dung từ v7–v11 thành một kế hoạch triển khai theo hướng **corpus-driven, entity-aware, number-aware**. Trọng tâm không còn chỉ là 7 rule grammar ban đầu, mà là một hệ thống gồm:

```text
- Logic relation transfer
- Formal/classical transfer
- Complement transfer
- Long nominal/entity transfer
- Number context conversion
- System/game format transfer
- Dialogue/rhetorical formatting
```

Chiến lược tốt nhất:

```text
1. Làm protected spans + entity + number context trước.
2. Sau đó làm clause segmenter + logic rules.
3. Tiếp theo mới làm formal/classical/complement rules.
4. Cuối cùng tích hợp vào RBMT bằng feature flag và trace.
```

Mục tiêu cuối:

```text
- Không phá pipeline hiện tại.
- Giảm lỗi số và tên riêng, vì đây là lỗi dễ gây sai nghiêm trọng nhất.
- Tăng tự nhiên tiếng Việt cho câu dài, logic clause, bổ ngữ, cổ văn nhẹ.
- Có corpus test từ chương 1–300 để đo tiến bộ thực tế.
```


---

# PART II — Bổ sung mở rộng từ v13: Chương 301–400

**Repo:** `converter-drduc`  
**Corpus:** `Hồng Hoang Lịch_Zhttty.html` — phân tích chương 301–400  
**Mục tiêu:** Bổ sung các cấu trúc ngữ pháp, chuyển đổi số, nhận diện tên riêng/entity còn thiếu sau bản v12.  
**Ngày:** 2026-04-25  

---

### 0. Tóm tắt kết quả phân tích chương 301–400

Vùng chương 301–400 có đặc trưng khác các cụm chương trước:

1. Mật độ nghị luận/giải thích thế giới quan cao: `事实上`, `换言之`, `从表面上来看`, `这么说吧`, `也就是说`.
2. Cấu trúc cổ văn/huyền huyễn tăng mạnh: `圣位之下皆蝼蚁`, `吾等`, `便是`, `可谓是`, `所处`, `所在`, `所化`.
3. Entity đa hệ: thần thoại Hồng Hoang, SCP, Cthulhu/ẩn mật tồn tại, fantasy, game/system.
4. Số xuất hiện nhiều ở dạng phần trăm, phân số, xấp xỉ, rank, tầng/lầu, cấp bậc, thời lượng.
5. Câu dài nhiều tầng logic: điều kiện + nhượng bộ + kết quả + so sánh + đánh giá.

Thống kê sơ bộ trên chương 301–400:

```text
Chapters: 100
Approx Chinese text chars: ~278k
Sentence-like units: ~5.4k
```

Một số pattern có tần suất cao trong mẫu phân tích:

| Nhóm cấu trúc | Tần suất xấp xỉ |
|---|---:|
| `一...就` / `刚一...就` | ~1.2k |
| `得` complement / lexicalized `得` | ~650 |
| `虽然...但是/却` | ~220 |
| `连...都/也` | ~230 |
| `若是/如果/要是...就/则/便` | ~290 |
| `难以/无法/不能够/不可能/没办法` | ~280 |
| `看似/似乎/仿佛/犹如` | ~240 |
| `把/将` disposal-result | ~130 |
| `所谓/名为/称为/叫做` | ~130 |
| `V起来/下来` abstract/directional | ~340 |
| `百分之...` | 12+ |
| duration/time quantity | 300+ |
| classifier/measure quantity | 1.7k+ |
| rank/level `阶/级/位/层/代` | 170+ |
| fraction/ratio `成/分之/百分之` | 60+ |

---

### 1. Bổ sung nhóm ngữ pháp nghị luận/giải thích

#### 1.1 `事实上 / 实际上 / 说实话 / 换言之 / 也就是说`

**Vấn đề:** Các cụm này thường đứng đầu câu, tạo quan hệ diễn giải, không nên dịch từng chữ cứng.

**Quy tắc chuyển đổi:**

| ZH | VI đề xuất |
|---|---|
| `事实上` | `trên thực tế` |
| `实际上` | `thực ra` / `trên thực tế` |
| `说实话` | `nói thật` |
| `换言之` | `nói cách khác` |
| `也就是说` | `cũng có nghĩa là` |
| `这么说吧` | `nói thế này đi` |
| `从表面上来看` | `nhìn bề ngoài` / `xét từ bề ngoài` |

**Algorithm:**

```python
DISCOURSE_MARKERS = {
    "事实上": "trên thực tế",
    "实际上": "thực ra",
    "说实话": "nói thật",
    "换言之": "nói cách khác",
    "也就是说": "cũng có nghĩa là",
    "这么说吧": "nói thế này đi",
    "从表面上来看": "nhìn bề ngoài",
}
```

**Tích hợp:** Chạy trong `DiscourseMarkerRule` trước surface realization, không ảnh hưởng dependency tree.

---

#### 1.2 `看似...事实上/但是...`

**Pattern:**

```text
看似 A，但是/事实上 B
```

**VI:**

```text
Nhìn như A, nhưng/trên thực tế B
```

**Ví dụ từ corpus dạng:**

```text
看似临圣不是圣位，并不具备...
```

**Rule:**

```python
if sentence.startswith("看似") and has_connector(["但是", "事实上", "其实"]):
    map 看似 -> "nhìn như"
    map 但是/事实上/其实 -> "nhưng/trên thực tế/thực ra"
```

**Lưu ý:** `看似` không phải động từ `xem`, mà là evidential marker.

---

#### 1.3 `可以说 / 可谓是 / 堪称`

**VI:**

| ZH | VI |
|---|---|
| `可以说` | `có thể nói là` |
| `可谓是` | `có thể gọi là` |
| `堪称` | `xứng đáng gọi là` |
| `足称` | `đủ để gọi là` |

**Rule:** Treat as evaluative copular phrase, không dịch `谓` thành động từ nói.

---

### 2. Bổ sung concession nâng cao

#### 2.1 `任凭...任凭...`

Xuất hiện trong kiểu câu:

```text
任凭你阴谋算计，任凭你雄兵百万，任凭你种族围攻...
```

**VI đề xuất:**

```text
Dù ngươi mưu tính thế nào, dù ngươi có trăm vạn hùng binh, dù cả chủng tộc vây công...
```

**Rule:**

```python
Pattern: 任凭 X, 任凭 Y, 任凭 Z, MAIN
Output: Dù X, dù Y, dù Z, MAIN
```

**Implementation:**

```python
class RenPingConcessionRule:
    trigger = "任凭"

    def transform(clauses):
        repeated = collect_repeated_prefix("任凭")
        return ["dù " + transfer(c.remove_prefix("任凭")) for c in repeated]
```

---

#### 2.2 `便是/就是...也/都...`

**Pattern:**

```text
便是 A，也 B
就是 A，都 B
```

**VI:**

```text
Cho dù là A, cũng B
```

**Cần phân biệt:**

| Pattern | Meaning |
|---|---|
| `便是 N` | chính là / là |
| `便是 A，也 B` | cho dù là A, cũng B |

**Rule:** Nếu trong cùng clause có `也/都` sau `便是/就是`, ưu tiên concession.

---

#### 2.3 `纵然/即便/哪怕...依然/仍然/还是...`

Mở rộng v12:

```python
CONCESSIVE_START = ["即便", "即使", "哪怕", "纵然", "便是", "就是"]
CONCESSIVE_RESUME = ["也", "都", "依然", "仍然", "还是", "照样"]
```

**VI:**

```text
dù / cho dù / ngay cả khi ... vẫn ...
```

---

### 3. Bổ sung logic điều kiện mạnh

#### 3.1 `只要不是...那基本上就...`

**Pattern:**

```text
只要不是 A，不去 B，自己不要 C，那基本上就 D
```

**VI:**

```text
Chỉ cần không phải A, không đi B, bản thân không C, thì về cơ bản sẽ D
```

**Rule:** gom chuỗi điều kiện phủ định trước `那/就`.

```python
Pattern:
  只要 [NEG_COND_1]，[NEG_COND_2]，...，那? 基本上? 就 MAIN
Output:
  Chỉ cần [không ...], [không ...], ... thì về cơ bản MAIN
```

---

#### 3.2 `若是能够...便是...又如何`

**Pattern tu từ điều kiện:**

```text
若是能够脱身，坏了你人族的宇宙，便是隐秘存在重新出现又如何！？
```

**VI:**

```text
Nếu có thể thoát thân, phá hỏng vũ trụ của nhân tộc các ngươi, thì dù Ẩn Mật Tồn Tại xuất hiện trở lại cũng đã sao!?
```

**Rule:**

- `若是/若/如果` → `nếu`
- `便是...又如何` → `dù ... thì đã sao`

---

#### 3.3 `否则 / 不然 / 到时候`

**VI:**

| ZH | VI |
|---|---|
| `否则` | `nếu không` |
| `不然` | `nếu không thì` |
| `到时候` | `đến lúc đó` |

**Scope:** sentence connector, không attach vào verb.

---

### 4. Cấu trúc nhấn mạnh và đánh giá

#### 4.1 `光是...就/都...`

**Pattern:**

```text
光是 A，就 B
光是 A，都可以 B
```

**VI:**

```text
Chỉ riêng A đã B
```

**Ví dụ dạng corpus:**

```text
光是我们两人，只要想，随时都可以冲破这封印
```

**Rule:**

```python
if clause.startswith("光是") and has(["就", "都"]):
    光是 -> "chỉ riêng"
    就/都 -> "đã"
```

---

#### 4.2 `别说...更别说...`

**Pattern:**

```text
别说 A，更别说 B
```

**VI:**

```text
Đừng nói đến A, càng đừng nói đến B
```

**Rule:** treat as scalar negative comparison.

---

#### 4.3 `何止 / 岂止`

**VI:**

```text
đâu chỉ / nào chỉ
```

**Rhetorical intensifier:** không dịch thành câu hỏi thường nếu không có `？`.

---

#### 4.4 `简直 / 根本 / 完全 / 彻底`

**Cần phân tầng cường độ:**

| ZH | VI |
|---|---|
| `简直` | `quả thực` / `đúng là` |
| `根本` | `căn bản` / `hoàn toàn` |
| `完全` | `hoàn toàn` |
| `彻底` | `triệt để` / `hoàn toàn` |

**Postprocess:** tránh `hoàn toàn hoàn toàn`.

---

### 5. `所` nâng cao — không chỉ passive

Chương 301–400 có nhiều `所` không phải `为...所...`.

#### 5.1 Phân loại `所`

| Dạng | Ví dụ pattern | VI |
|---|---|---|
| Passive | `为 A 所 V` | `bị/được A V` |
| Location nominal | `所处位置` | `vị trí đang ở` |
| Belonging/extent | `所有 X` | `tất cả X` |
| Reason connector | `所以` | `vì vậy` |
| Relative nominal | `所说/所做/所见` | `điều đã nói/làm/thấy` |
| Existential location | `所在地/所在之处` | `nơi ở / nơi tọa lạc` |

#### 5.2 Thuật toán

```python
def classify_suo(tokens, i):
    if tokens[i].form == "所以":
        return SUO_REASON
    if tokens[i].form.startswith("所有"):
        return SUO_ALL
    if prev_in(["为", "被", "由"]) and next_is_verb():
        return SUO_PASSIVE
    if next_in(["处", "在", "地", "位置"]):
        return SUO_LOCATION
    if next_is_verb():
        return SUO_NOMINALIZED_RELATIVE
    return SUO_UNKNOWN
```

#### 5.3 Rule output

```text
他所说的话
→ lời hắn nói / những lời hắn đã nói

目前所处位置
→ vị trí hiện tại đang ở

所有资料
→ tất cả tư liệu
```

---

### 6. `之` nâng cao — cổ văn, định ngữ, locative, idiom

#### 6.1 Phân loại `之`

| Dạng | Pattern | VI |
|---|---|---|
| Possessive classical | `A之B` | `B của A` |
| Locative | `之中/之上/之下/之外/之间/之后/之前` | `trong/trên/dưới/ngoài/giữa/sau/trước` |
| Idiom | `换言之/总之/久而久之` | fixed phrase |
| Verb substitute | rare | `điều đó` |
| Domain phrase | `圣位之下皆蝼蚁` | `dưới Thánh Vị đều là sâu kiến` |

#### 6.2 Rule cho `A之B`

```python
if token == "之" and left_is_nominal() and right_is_nominal():
    output = right + " của " + left
```

**Nhưng cần protected idiom/entity:**

```text
昊天镜, 东皇钟, 诛仙四剑, 轮回盘
```

Không tách nhầm entity có `天/皇/镜`, nhưng nếu có `之` thật thì tách.

#### 6.3 Rule locative

```python
ZHI_LOC = {
    "之中": "trong",
    "之内": "trong vòng / bên trong",
    "之外": "ngoài",
    "之上": "trên",
    "之下": "dưới",
    "之间": "giữa",
    "之后": "sau đó / sau",
    "之前": "trước đó / trước",
}
```

---

### 7. `以` nâng cao

#### 7.1 Các lớp nghĩa

| Dạng | Pattern | VI |
|---|---|---|
| Instrument | `以 A V` | `dùng A để V` |
| Standard | `以 A 为 B` | `lấy A làm B` |
| Center/core | `以 A 为中心/为核` | `lấy A làm trung tâm/hạt nhân` |
| Cause/result | `以至于` | `đến mức / đến nỗi` |
| Sequence | `从而/进而` | `từ đó / tiếp đó` |
| Range | `以上/以下/以内/以外` | `trở lên/trở xuống/trong vòng/ngoài` |

#### 7.2 Rule `以 A 为 B`

```text
以他为中心
→ lấy hắn làm trung tâm

以魔罗为核
→ lấy Ma La làm hạt nhân
```

**Implementation:**

```python
Pattern: 以 [NP] 为 [NP/ADJ]
Output: lấy [NP] làm [NP/ADJ]
```

#### 7.3 Rule `以至于`

```text
A，以至于 B
→ A, đến mức B
```

Không tách `以` và `至于`.

---

### 8. `为` nâng cao — copula, passive, purpose, transform

#### 8.1 Phân loại

| Pattern | VI |
|---|---|
| `A 为 B` | `A là B` |
| `为 A 所 V` | `bị/được A V` |
| `为了 A` | `để/vì A` |
| `为此` | `vì vậy / vì chuyện này` |
| `称为/名为/视为` | `được gọi là / xem là` |
| `化为/变为/转化为` | `hóa thành / biến thành` |

#### 8.2 Rule `为...所...`

```python
if form == "为" and later("所") and later_verb():
    build_passive(agent_span=between(为, 所), verb=after(所))
```

**VI:**

```text
为敌所困
→ bị địch vây khốn
```

---

### 9. `将` nâng cao — future vs disposal vs formal fronting

#### 9.1 Phân biệt

| Pattern | Type | VI |
|---|---|---|
| `将要/将会 V` | future | `sắp/sẽ V` |
| `将 O V` | disposal/fronting | `V O` hoặc `đem O V` |
| `将 A 化为 B` | transform | `biến A thành B` |
| `将 A 视为 B` | classify | `xem A là B` |
| `即将 V` | imminent | `sắp V` |

#### 9.2 Decision tree

```python
def classify_jiang(i):
    if next in ["要", "会", "来", "临"]:
        return FUTURE
    if prev == "即":
        return IMMINENT
    if next_is_np() and has_later_verb():
        return DISPOSAL
    return VERB_OR_UNKNOWN
```

---

### 10. Bổ ngữ `得` — cần tách lexicalized vs complement

#### 10.1 Vấn đề

Các pattern `得` xuất hiện nhiều, nhưng không phải cái nào cũng là degree complement.

#### 10.2 Lexicalized guard

Không xử lý như complement nếu thuộc:

```text
觉得, 记得, 显得, 懂得, 获得, 得到, 不得不, 不得了, 免得, 省得, 难得
```

#### 10.3 Các loại cần nhận diện

| Type | Pattern | VI |
|---|---|---|
| Degree | `V/Adj 得 很/非常/极其` | `rất/cực kỳ` |
| Result | `V 得 A` | `V đến mức A` |
| Potential positive | `V 得 了` | `V nổi / có thể V` |
| Potential negative | `V 不 了` | `không V nổi` |
| Structural | `得以 V` | `có thể / được V` |

#### 10.4 Rule

```python
if token == "得":
    if compound_guard(): skip
    elif next in DEGREE_WORDS: DEGREE_COMPLEMENT
    elif next in ["了", "动", "起", "下", "过"]: POTENTIAL
    else: RESULT_COMPLEMENT
```

---

### 11. Directional complement abstract

#### 11.1 `起来` không chỉ “đứng dậy”

Các dạng cần phân biệt:

| Pattern | VI |
|---|---|
| `站起来/坐起来` | `đứng/ngồi dậy` |
| `想起来/记起来` | `nhớ ra` |
| `看起来` | `trông có vẻ` |
| `联合起来/组织起来` | `liên hợp/tổ chức lại` |
| `冲起来/飞起来` | `lao/bay lên` |
| `说起来` | `nói ra thì / nhắc đến` |

#### 11.2 `下来`

| Pattern | VI |
|---|---|
| `停下来/平静下来` | `dừng/bình tĩnh lại` |
| `记录下来/保存下来` | `ghi/lưu lại` |
| `落下来/降下来` | `rơi/hạ xuống` |
| `坚持下来` | `kiên trì được` |

#### 11.3 `出来`

| Pattern | VI |
|---|---|
| `看出来/听出来` | `nhìn/nghe ra` |
| `说出来` | `nói ra` |
| `显露出来/冒出来` | `hiện/lộ ra` |
| `制造出来` | `chế tạo ra` |

#### 11.4 Rule data file

Bổ sung `data/grammar/directional_abstract_map.json`:

```json
{
  "起来": {
    "posture": ["站", "坐", "躺", "爬"],
    "inceptive": ["说", "哭", "笑", "跑", "唱", "打"],
    "appear": ["看", "听", "想", "记"],
    "collective": ["联合", "组织", "集合"]
  },
  "下来": {
    "stabilize": ["停", "平静", "安静", "冷静"],
    "record": ["记", "记录", "保存", "写"],
    "downward": ["落", "降", "掉"]
  },
  "出来": {
    "perception": ["看", "听", "认", "分辨"],
    "speech": ["说", "喊", "叫"],
    "emergence": ["显露", "冒", "钻", "浮现"]
  }
}
```

---

### 12. `一...就` cần phân loại sâu

Pattern này rất nhiều, không thể xử lý chung một kiểu.

#### 12.1 Loại thời gian tức thì

```text
一进入，就发现...
→ vừa bước vào đã phát hiện...
```

#### 12.2 Loại điều kiện

```text
一旦/一...就...
→ một khi ... thì ...
```

#### 12.3 Loại hành động tức thì

```text
刚一接触就炸裂
→ vừa chạm vào đã nổ tung
```

#### 12.4 Rule

```python
if prefix in ["刚一", "才一"]:
    output = "vừa ... đã ..."
elif first_verb_is_eventive():
    output = "vừa ... đã ..."
else:
    output = "một khi ... thì ..."
```

---

### 13. Rhetorical question expansion

#### 13.1 Patterns

| ZH | VI |
|---|---|
| `难道...吗？` | `chẳng lẽ ... sao?` |
| `莫非...？` | `chẳng lẽ ...?` |
| `岂不是...？` | `chẳng phải là ... sao?` |
| `何必...？` | `cần gì phải ...?` |
| `又如何！？` | `thì đã sao!?` |
| `怎么可能...？` | `sao có thể ... được?` |

#### 13.2 Special xianxia/game tone

`又如何` thường là thách thức, nên dịch mạnh:

```text
...又如何！？
→ ... thì đã sao!?
```

---

### 14. Long nominal chain không có `的`

Chương 301–400 có rất nhiều danh ngữ kiểu:

```text
洪荒天庭
十大顶级先天灵宝
SCP基金会
机械境
地皇后土
精神力控制者
人皇权柄
高阶圣位
```

#### 14.1 Bổ sung EntityChainParser

**Mục tiêu:** tránh tách sai thành từng chữ hoặc đảo sai.

```python
class EntityChainParser:
    def parse_chain(tokens):
        # [modifier*] [head_suffix]
        # suffix: 族/会/团/军/位面/世界/灵宝/权柄/圣位/基金会/控制者
```

#### 14.2 Suffix ontology mở rộng

```json
{
  "rank_power": ["圣位", "临圣", "半神", "高阶圣位", "二阶", "三阶"],
  "mythic_artifact": ["灵宝", "先天灵宝", "镜", "钟", "盘", "剑", "刀", "莲"],
  "organization": ["基金会", "冒险团", "军团", "联盟", "帝国", "王国", "协会"],
  "race": ["族", "龙族", "精灵族", "烂泥族", "鸽族", "血族"],
  "place": ["位面", "世界", "大陆", "地狱", "天庭", "机械境"],
  "ability": ["权柄", "符文", "魔法", "真意", "大道", "模因"],
  "role": ["控制者", "领主", "人皇", "地皇", "魔罗", "主神"]
}
```

#### 14.3 Rule bảo vệ

Nếu chuỗi kết thúc bằng suffix thuộc ontology và độ dài 2–16 ký tự:

```python
protect_as_entity(span, entity_type)
```

Không cho DE inversion, number converter, hoặc directional rule tách giữa chuỗi.

---

### 15. Entity từ chương 301–400 cần bổ sung glossary

#### 15.1 Nhân vật/thần thoại

```text
伊露维塔
昊
后土
地皇后土
魔罗
东皇
罗睺
计都
盘古
郑吒
楚轩
阿赖耶识
```

#### 15.2 Chủng tộc/thế lực

```text
精灵族
洪荒万族
烂泥族
鸽族
极古族
血族
天蛇族
鲲族
鹏族
泰坦巨人
SCP基金会 / scp基金会
```

#### 15.3 Địa danh/vị diện

```text
洪荒大陆
洪荒天庭
纳尼亚位面
机械境
多元宇宙
外位面
地狱
人类城
```

#### 15.4 Pháp bảo/công pháp/khái niệm

```text
昊天镜
东皇钟
轮回盘
诛仙四剑
人皇权柄
先天灵宝
顶级先天灵宝
八卦符文
符文解析法
大罗星斗鸿蒙阵
六道轮回
```

#### 15.5 SCP/game/system

```text
SCP基金会
收容物
keter收容物
BOSS
NPC
主神
兑换
奖励点数
支线剧情
模因
现实扭曲者
```

---

### 16. Số và định dạng số bổ sung

#### 16.1 Phần trăm lớn hơn 100%

Xuất hiện dạng:

```text
百分之一百二十
```

**VI:**

```text
120%
```

Không dịch thành “một trăm hai mươi phần trăm” nếu mode numeric.

#### 16.2 Phần trăm xấp xỉ

```text
百分之七八十
→ khoảng 70–80%
```

Rule:

```python
百分之 + 七八十 => khoảng 70-80%
百分之 + 三四十 => khoảng 30-40%
```

#### 16.3 Số thập phân dài

```text
百分之九十九点九九九九九
→ 99,99999%
```

**Rule:**

- `点` → dấu phẩy hoặc dấu chấm theo config locale.
- Nếu là phần trăm, giữ `%`.

#### 16.4 `成` ratio

| ZH | VI |
|---|---|
| `一成` | `10%` / `một phần mười` |
| `五成` | `50%` / `năm phần` |
| `九成` | `90%` |
| `七八成` | `khoảng 70–80%` |

**Config:**

```python
number_style = "numeric"  # 90%
number_style = "literary" # chín phần
```

#### 16.5 Rank/race ranking

```text
洪荒万族二十位
→ hạng 20 trong vạn tộc Hồng Hoang
```

Pattern:

```python
[DOMAIN] [NUMBER] 位
```

Nếu trước có `排行`, output `xếp hạng`.

#### 16.6 Tầng/lầu/tòa nhà

```text
三四栋三四十层楼的大楼
→ ba bốn tòa nhà cao ba bốn mươi tầng
```

Rule:

```python
三四栋 -> ba bốn tòa
三四十层 -> ba bốn mươi tầng
```

#### 16.7 Time/duration

```text
96天
→ 96 ngày

五分钟
→ 5 phút

千年
→ nghìn năm / một nghìn năm
```

#### 16.8 Scientific/game unit

```text
二阶职业者
→ chức nghiệp giả bậc hai

高阶圣位
→ Thánh Vị cao giai

第一层
→ tầng thứ nhất / lớp thứ nhất
```

Cần context: `阶` trong tu luyện/game không phải “bậc cầu thang”.

---

### 17. Thuật toán bảo vệ số trong entity

#### 17.1 Không chuyển số khi thuộc tên riêng

```text
诛仙四剑
十大顶级先天灵宝
六道轮回
八卦符文
三清
九宫
十二品黑莲
```

#### 17.2 Nhưng vẫn chuyển nếu là quantity

```text
十二条尾巴
→ mười hai cái đuôi

八颗光团
→ tám quầng sáng

三点阴影团
→ ba khối bóng tối
```

#### 17.3 Decision

```python
if number + suffix in PROTECTED_ENTITY_SUFFIX:
    protect
elif suffix in CLASSIFIER_SUFFIX:
    convert_quantity
elif phrase in KNOWN_ENTITY:
    protect
else:
    context_score()
```

---

### 18. Chuỗi hành động chiến đấu/quy mô lớn

Chương 301–400 có nhiều câu combat cosmic:

```text
从空而落
猛的对撞
同时炸裂
显露出来
阻挡在...之前
被迫停止
```

#### 18.1 Rule action chain

```python
ACTION_CHAIN_VERBS = [
    "冲", "撞", "炸裂", "显露", "阻挡", "停止", "落", "轰击",
    "挡", "冒出", "化为", "镇压", "封印"
]
```

**VI connector:**

| Relation | VI |
|---|---|
| sequential | `rồi` |
| simultaneous | `đồng thời` |
| cause-result | `khiến cho` / `làm cho` |
| direction | giữ complement `ra/lên/xuống/tới` |

#### 18.2 `同时`

`同时` đứng trước nhiều VP:

```text
都同时炸裂，露出了...
→ đều đồng thời nổ tung, lộ ra...
```

---

### 19. Bổ sung thuật toán sentence segmentation cho câu nghị luận dài

#### 19.1 Vấn đề

Nhiều câu dài chứa nhiều dấu phẩy và connector logic. Nếu dịch nguyên câu, rule conflict.

#### 19.2 Clause splitter

Tách theo priority:

```python
CLAUSE_SPLIT_CONNECTORS = [
    "但是", "不过", "然而", "可是",
    "所以", "因此", "于是",
    "因为", "由于",
    "若是", "如果", "只要", "除非",
    "虽然", "即便", "哪怕",
    "换言之", "也就是说",
]
```

#### 19.3 Không split trong entity/quote

Không split nếu dấu nằm trong:

- `「...」`
- `“...”`
- protected entity span
- number range `三十，四十章`
- list title

---

### 20. Test suite mới cho chương 301–400

#### 20.1 Grammar tests

```python
def test_renping_concession():
    zh = "任凭你阴谋算计，任凭你雄兵百万，他都立于不败之地"
    expect_contains = ["dù", "mưu tính", "trăm vạn hùng binh", "vẫn", "bất bại"]

def test_guangshi_emphasis():
    zh = "光是我们两人，只要想，随时都可以冲破这封印"
    expect = "Chỉ riêng hai người chúng ta, chỉ cần muốn, bất cứ lúc nào cũng có thể phá vỡ phong ấn này"

def test_ruo_neng_you_ru_he():
    zh = "若是能够脱身，便是隐秘存在重新出现又如何"
    expect_contains = ["nếu", "có thể thoát thân", "dù", "xuất hiện trở lại", "thì đã sao"]

def test_suo_location():
    zh = "众人目前所处位置"
    expect = "vị trí hiện tại mọi người đang ở"

def test_yi_np_wei_np():
    zh = "以他为中心"
    expect = "lấy hắn làm trung tâm"

def test_zhi_locative():
    zh = "圣位之下皆蝼蚁"
    expect = "dưới Thánh Vị đều là sâu kiến"
```

#### 20.2 Number tests

```python
def test_percent_over_100():
    assert convert("百分之一百二十") == "120%"

def test_percent_approx():
    assert convert("百分之七八十") == "khoảng 70–80%"

def test_decimal_percent():
    assert convert("百分之九十九点九九九九九") in ["99,99999%", "99.99999%"]

def test_cheng_ratio():
    assert convert("九成") in ["90%", "chín phần"]

def test_floor_building_approx():
    zh = "三四栋三四十层楼的大楼"
    expect = "ba bốn tòa nhà cao ba bốn mươi tầng"
```

#### 20.3 Entity tests

```python
def test_scp_uppercase_entity():
    assert protect("scp基金会") == "SCP基金会"

def test_mythic_artifact():
    assert protect("昊天镜").type == "artifact"

def test_number_protected_artifact():
    assert protect("诛仙四剑").do_not_convert_number is True

def test_quantity_not_protected():
    assert convert("十二条尾巴") == "mười hai cái đuôi"
```

---

### 21. Roadmap bổ sung vào v12

#### Sprint C301-400.1 — Discourse + concession

- [ ] `DiscourseMarkerRule`
- [ ] `RenPingConcessionRule`
- [ ] `GuangShiEmphasisRule`
- [ ] `BianShiYeConcessionRule`
- [ ] Tests 30 cases

#### Sprint C301-400.2 — Classical function words

- [ ] `SuoClassifier`
- [ ] `ZhiClassifier`
- [ ] `YiWeiRule`
- [ ] `WeiClassifier`
- [ ] Tests 40 cases

#### Sprint C301-400.3 — Directional abstract

- [ ] `directional_abstract_map.json`
- [ ] `QilaiAbstractRule`
- [ ] `XialaiAbstractRule`
- [ ] `ChulaiAbstractRule`
- [ ] Tests 30 cases

#### Sprint C301-400.4 — Number expansion

- [ ] percent over 100
- [ ] percent approximate
- [ ] decimal percent
- [ ] `成` ratio
- [ ] floor/building approximate numbers
- [ ] rank/race ranking
- [ ] protected number inside entity
- [ ] Tests 50 cases

#### Sprint C301-400.5 — Entity expansion

- [ ] Extend ontology suffix list
- [ ] Add SCP/game/system entity detection
- [ ] Add mythic artifact detector
- [ ] Add race/faction detector
- [ ] Add place/plane/world detector
- [ ] Tests 60 cases

---

### 22. Acceptance metrics cập nhật

| Metric | Target |
|---|---:|
| Existing 98 tests | 100% pass |
| v7–v12 grammar tests | 100% pass |
| New C301–400 unit tests | ≥ 95% pass |
| Number conversion tests | ≥ 98% pass |
| Entity protected-span tests | ≥ 98% pass |
| No crash on chapters 301–400 | 100% |
| Grammar fallback warnings | logged, not fatal |
| Wrong number conversion inside entity | < 1% sampled errors |
| `所/之/以/为` classifier accuracy | ≥ 85% on sampled cases |
| Directional abstract accuracy | ≥ 85% on sampled cases |

---

### 23. Kết luận

Chương 301–400 yêu cầu thuật toán không chỉ là ZH→VI grammar transfer cơ bản, mà cần thêm lớp **classical/discourse/entity-aware parsing**:

1. `所/之/以/为/将` phải có classifier riêng.
2. `任凭`, `光是`, `便是...也`, `又如何` phải được xử lý như rhetorical/concessive structures.
3. `起来/下来/出来` cần abstract complement map, không chỉ directional map.
4. Number converter phải hỗ trợ `% > 100`, `% xấp xỉ`, decimal percent, `成`, rank, tầng/lầu, và bảo vệ số trong entity.
5. Entity detector phải mở rộng sang SCP, thần thoại Hồng Hoang, chủng tộc, pháp bảo, quyền柄, vị diện, thế giới, tổ chức.

Bản v13 nên được merge vào kế hoạch v12 như một module mở rộng:  
`Corpus Expansion Track — Chapters 301–400`.


---

# PART III — Roadmap triển khai thống nhất v14

## 1. Sprint U1 — Compatibility & Guard Rails

**Mục tiêu:** Tích hợp skeleton nhưng không phá pipeline cũ.

- [ ] Thêm feature flag `enable_grammar_transfer`
- [ ] Thêm `ZHVIGrammarTransferPipeline.transfer_safe()`
- [ ] Thêm `GrammarTrace`
- [ ] Tích hợp quanh `rewrite_chinese_structure(sentence)`
- [ ] Flag off: 98 tests cũ phải pass
- [ ] Flag on: chỉ chạy smoke tests

**Acceptance:**

```text
python -m pytest
→ toàn bộ tests cũ pass khi flag off
```

---

## 2. Sprint U2 — Entity + Protected Span MVP

**Mục tiêu:** Không dịch/tách sai tên riêng, số trong entity, thuật ngữ hệ thống.

- [ ] `ProtectedSpan`
- [ ] `NamedEntityDetector`
- [ ] `EntityChainParser`
- [ ] `entity_suffix_ontology.json`
- [ ] `protected_entity_terms.json`
- [ ] Guard số trong entity
- [ ] Tests cho nhân vật, thế lực, địa danh, công pháp, pháp bảo, SCP/system

**Acceptance:**

```text
诛仙四剑      → protected artifact, không đổi “四” thành quantity riêng
六道轮回      → protected concept
SCP基金会     → protected organization
十二条尾巴    → quantity, vẫn đổi thành “mười hai cái đuôi”
```

---

## 3. Sprint U3 — Core Grammar MVP

**Mục tiêu:** 7 rule lõi hoạt động.

- [ ] `的` inversion
- [ ] Aspect `了/着/过/正在`
- [ ] Passive `被/由...所/为...所`
- [ ] Disposal `把/将`
- [ ] Directional complement
- [ ] Serial verb/action chain
- [ ] Topic-comment

**Acceptance:** ≥ 90% pass trên core unit tests.

---

## 4. Sprint U4 — Clause Logic + Discourse

**Mục tiêu:** Xử lý câu dài, nghị luận, điều kiện, nhượng bộ.

- [ ] Conditional rules
- [ ] Concession rules
- [ ] Contrast/correction
- [ ] Cause-result
- [ ] Discourse markers
- [ ] Rhetorical questions
- [ ] Clause splitter an toàn quote/entity

**Acceptance:** ≥ 85% sampled accuracy trên câu logic dài.

---

## 5. Sprint U5 — Classical/Xianxia Function Words

**Mục tiêu:** Hoàn thiện `所/之/以/为/将/便是`.

- [ ] `SuoClassifier`
- [ ] `ZhiClassifier`
- [ ] `YiClassifier`
- [ ] `WeiClassifier`
- [ ] `JiangClassifier`
- [ ] `BianShiConcessionRule`
- [ ] `RenPingRule`
- [ ] `YouRuHeRule`

**Acceptance:** ≥ 85% classifier accuracy.

---

## 6. Sprint U6 — Complement System

**Mục tiêu:** Bổ sung result/potential/degree/abstract directional.

- [ ] Resultative complement
- [ ] Potential complement
- [ ] Degree complement `得`
- [ ] Lexicalized guard for `得`
- [ ] Directional abstract map
- [ ] `起来/下来/出来` context classifier

**Acceptance:** ≥ 85% complement accuracy.

---

## 7. Sprint U7 — Number/Format Completion

**Mục tiêu:** Không còn lỗi lớn về số trong 400 chương đầu.

- [ ] Duration/countdown
- [ ] Approx range
- [ ] Percent >100
- [ ] Decimal percent
- [ ] `成` ratio
- [ ] Fraction
- [ ] Rank/level/generation
- [ ] Floor/building approximate
- [ ] Game resource numbers
- [ ] Entity-protected number

**Acceptance:** ≥ 98% number unit tests pass.

---

## 8. Sprint U8 — Corpus Regression & Calibration

**Mục tiêu:** Đo accuracy thật trên các chương đã phân tích.

- [ ] Build corpus test cases từ v7–v13
- [ ] 30 câu integration core
- [ ] 100 câu grammar logic
- [ ] 100 câu number/entity
- [ ] 200 câu mixed corpus
- [ ] Report theo construction type
- [ ] Fix top 10 error patterns

**Acceptance:**

| Metric | Target |
|---|---:|
| Existing tests | 100% pass |
| Core grammar tests | ≥ 95% |
| Clause/discourse tests | ≥ 90% |
| Classical function words | ≥ 85% |
| Number conversion | ≥ 98% |
| Entity protection | ≥ 98% |
| No crash on sampled chapters | 100% |

---

# PART IV — Unified Test Matrix

## 1. Core grammar

```python
CASES_CORE = [
    ("美丽的书", "sách đẹp"),
    ("他买的书", "sách hắn mua"),
    ("他已经走了", "hắn đã đi rồi"),
    ("杯子被我打碎了", "cái cốc bị tôi đập vỡ rồi"),
    ("他把书放在桌上", "hắn đặt sách lên bàn"),
    ("他走进来了", "hắn bước vào rồi"),
]
```

## 2. Clause/discourse

```python
CASES_CLAUSE = [
    ("虽然他很弱，但是他没有退后", "tuy hắn rất yếu, nhưng hắn không lùi lại"),
    ("只要不是圣位，那基本上就还有机会", "chỉ cần không phải Thánh Vị, thì về cơ bản vẫn còn cơ hội"),
    ("光是我们两人，就可以冲破封印", "chỉ riêng hai người chúng ta đã có thể phá vỡ phong ấn"),
    ("任凭你阴谋算计，他都不惧", "dù ngươi mưu tính thế nào, hắn cũng không sợ"),
]
```

## 3. Classical function words

```python
CASES_CLASSICAL = [
    ("他所说的话", "lời hắn nói"),
    ("圣位之下皆蝼蚁", "dưới Thánh Vị đều là sâu kiến"),
    ("以他为中心", "lấy hắn làm trung tâm"),
    ("为敌所困", "bị địch vây khốn"),
    ("便是隐秘存在重新出现又如何", "dù Ẩn Mật Tồn Tại xuất hiện trở lại thì đã sao"),
]
```

## 4. Number

```python
CASES_NUMBER = [
    ("百分之一百二十", "120%"),
    ("百分之七八十", "khoảng 70–80%"),
    ("九成", "90%"),
    ("三四栋三四十层楼的大楼", "ba bốn tòa nhà cao ba bốn mươi tầng"),
    ("二阶职业者", "chức nghiệp giả bậc hai"),
]
```

## 5. Entity/protected spans

```python
CASES_ENTITY = [
    ("诛仙四剑", "protected artifact"),
    ("六道轮回", "protected concept"),
    ("昊天镜", "protected artifact"),
    ("SCP基金会", "protected organization"),
    ("十二条尾巴", "quantity, not entity"),
]
```

---

# PART V — Definition of Done v14

Bản thuật toán được xem là hoàn thiện giai đoạn v14 khi đạt:

1. **Không phá baseline**
   - Toàn bộ tests cũ pass khi feature flag off.
2. **Core grammar ổn định**
   - 7 rule lõi pass ≥ 95% unit tests.
3. **Entity/number protection ổn định**
   - Không đổi sai số trong entity.
   - Không tách sai tên pháp bảo/công pháp/thế lực.
4. **Câu dài có fallback**
   - Parser fail không crash.
   - Rule fail chỉ skip rule đó.
5. **Trace rõ ràng**
   - Mỗi rewrite có source span, rule name, confidence.
6. **Có corpus regression**
   - Có bộ test từ chương 1–400, chia theo construction.
7. **Có accuracy report**
   - Theo từng nhóm: DE, aspect, passive, disposal, clause, classical, number, entity.

---

# PART VI — Ghi chú triển khai quan trọng

## 1. Không dùng parser nặng quá sớm

Ưu tiên:

```text
Protected spans → tokenizer/POS → shallow construction detector → rule transfer
```

Dependency parser đầy đủ chỉ nên dùng sau khi MVP đã ổn.

## 2. Không để number converter chạy trước entity guard

Sai lầm cần tránh:

```text
诛仙四剑 → Tru Tiên bốn kiếm
```

Đúng:

```text
诛仙四剑 → Tru Tiên Tứ Kiếm / bốn thanh kiếm Tru Tiên
```

Tùy glossary nhưng không được tách số mù.

## 3. Không dịch `将` cứng thành “sẽ”

```text
将 A 化为 B → biến A thành B
将要 V      → sắp/sẽ V
```

## 4. Không dịch `所` cứng

```text
所以       → vì vậy
所有       → tất cả
所说       → điều đã nói / lời nói
所处位置   → vị trí đang ở
为...所... → bị/được...
```

## 5. Không dịch directional complement chỉ theo nghĩa không gian

```text
想起来   → nhớ ra
记录下来 → ghi lại
看出来   → nhìn ra
联合起来 → liên hợp lại
站起来   → đứng dậy
```

---

# END OF v14
