# GRAMMAR_TRANSFER_PLAN v11.0 — Ch201–300 Corpus Completion

**Repo:** `converter-drduc`  
**Corpus:** `Hồng Hoang Lịch_Zhttty.html` — chapters 201–300  
**Scope titles:** `chapter-201` = `第二十九章：阴影`, `chapter-300` = `第三十二章：临圣`  
**Generated:** 2026-04-25  
**Goal:** Bổ sung những cấu trúc ngữ pháp, chuyển đổi số, và quy luật nhận diện tên riêng còn thiếu sau khi phân tích sâu 100 chương tiếp theo.

---

## 0. Tóm tắt kết quả phân tích

Đã tách nội dung chương 201–300 từ HTML theo anchor `chapter-201` đến trước `chapter-301`.

```text
Chapters analyzed: 100
Chinese text chars: ~318,700
Sentence-like units: ~5,019
```

100 chương này chuyển trọng tâm sang: **game/faction management, forum-like player discourse, blood-race/vampire arc, elf diplomacy, cultivation + magical-industrial terms, hidden existence / low-dimensional invasion, item/resource accounting, and mythological/civilizational exposition**.

Điều quan trọng: nhóm chương này có mật độ rất cao của `将`, `被`, `所`, `之`, `以...为`, `对...而言`, `随着`, số dạng game resource, số cấp bậc, số phần trăm/phân số, và tên riêng dạng danh ngữ dài không có `的`.

---

## 1. Thống kê pattern nổi bật

| Pattern | Count approx. |
|---|---:|
| 将_disposal/future | 471 |
| 被_passive | 442 |
| 由所/为所 | 76 |
| 虽然但是/不过/却 | 1793 |
| 若/如果/只要/除非/一旦/凡是 | 561 |
| 无论/不管 | 94 |
| 越越 | 74 |
| 连都/也 | 294 |
| 不是而是 | 45 |
| 直到才 | 23 |
| 一就/刚就 | 551 |
| 得_comp | 860 |
| 所谓/名为/称为/叫做 | 105 |
| 对于/对.*来说 | 109 |
| 随着 | 116 |
| 以为/视为/作为/化为/变成 | 319 |
| 并非/并不是 | 77 |
| percent | 28 |
| fraction | 48 |
| range | 37 |
| rank_level | 188 |
| duration | 337 |
| countdown | 21 |
| resource | 250 |
| generation | 13 |
| 所字结构 | 941 |
| 之字结构 | 1101 |
| 在...之中/上/下/内/外 | 145 |
| 以...来 | 144 |
| 以...为 | 142 |
| 不得不/不能不 | 23 |
| 没有任何 | 53 |
| 几乎都/全部 | 181 |
| 逐渐/渐渐 | 70 |
| 反问岂/难道 | 90 |
| 拟声/省略 | 1615 |

### Kết luận từ thống kê

1. `将` xuất hiện cực nhiều, không thể dịch máy móc thành “sẽ”; trong corpus này `将 + O + V` thường là **disposal/formal object-fronting**.
2. `所` và `之` trở thành trọng tâm mới. Đây không chỉ là cổ văn, mà còn tạo danh ngữ kỹ thuật như `所需`, `所有`, `之中`, `之上`, `以...之名`.
3. Số không chỉ là số đếm. Có các lớp số rất khác nhau: **rank/level, game point/resource, duration/countdown, percent, fraction, range, generation, inventory count**.
4. Entity nhận diện chưa đủ nếu chỉ dựa vào tên người. Cần nhận diện thêm **race/species, faction, alliance, realm, item/equipment, game/system term, forum nickname, player slang**.
5. Văn phong có nhiều thoại, nội tâm, PS/tác giả, forum post, hệ thống game. Cần module boundary riêng để không áp dụng grammar rule sai lên metadata hoặc lời nhắn ngoài truyện.

---

## 2. Các cấu trúc ngữ pháp còn thiếu cần bổ sung

## 2.1. `将` disambiguation: future vs disposal vs formal object fronting

### Vấn đề

Ví dụ ngắn trong corpus:

```text
将礼物放在了前台
内战将延续至少百年以上
他将成为真正的霸主
```

### Phân loại

| Dạng | Pattern | VI |
|---|---|---|
| Future/modal | `将 + VV/VA`, `将要/将会 + V` | sẽ |
| Disposal | `将 + NP + V` | đem / đưa / chuyển / bỏ marker |
| Formal object-fronting | `将 + abstract NP + 视为/化为/变成/作为` | xem/coi/biến/lấy... làm |
| Title/quote protected | `将` trong tên riêng/thuật ngữ | không xử lý |

### Rule

```python
if token == "将":
    if next_token in {"要", "会"} or next_pos in {"VV", "VA"}:
        return FUTURE_MARKER("sẽ")
    if next_span_is_np() and following_has_verb():
        return DISPOSAL_MARKER(skip=True, style="formal")
```

### Transfer

```text
将礼物放在前台
→ đặt món quà lên quầy trước

将A化为B
→ biến A thành B

将A视为B
→ xem A là B
```

### Tests thêm

```text
将礼物放在了前台 → đặt món quà lên quầy trước rồi
这场内战将延续百年以上 → cuộc nội chiến này sẽ kéo dài hơn trăm năm
将其视为敌人 → xem nó là kẻ địch
```

---

## 2.2. `所` constructions

### Nhóm cần tách

| Pattern | Loại | VI |
|---|---|---|
| `所有 + N` | determiner | tất cả / mọi |
| `所需/所属/所在/所说/所见` | nominalized V | thứ/cái/nơi... mà |
| `为/由/被 + X + 所 + V` | formal passive | bị/được X V |
| `所以` | conjunction | cho nên / vì vậy |
| `所谓` | naming/discourse | cái gọi là / được gọi là |

### Rule priority

```text
1. 所以, 所谓 fixed expression
2. 所有 determiner
3. 为/由/被 ... 所 ... passive
4. 所 + V nominalization
```

### Transfer examples

```text
所有人 → tất cả mọi người
所需的武器 → vũ khí cần thiết
由此爆发出来的战争 → cuộc chiến bùng phát từ đó
为敌人所杀 → bị kẻ địch giết
所谓圣位 → cái gọi là thánh vị
```

### Files cần thêm

```text
src/grammar/transfer_rules/rule_suo_construction.py
data/grammar/suo_patterns.json
tests/test_grammar/test_rule_suo.py
```

---

## 2.3. `之` constructions

### Nhóm chính

| Pattern | Loại | VI |
|---|---|---|
| `A之B` | classical genitive | B của A |
| `A之中/之上/之下/之外/之内` | locative | trong/trên/dưới/ngoài/trong phạm vi A |
| `之后/之前/之时/之际` | temporal | sau/trước/khi/lúc |
| `总之/换言之/反之` | discourse fixed | tóm lại / nói cách khác / ngược lại |
| `以A之名` | formula | nhân danh A |
| `霸主之资/文明之争` | abstract noun phrase | tư chất bá chủ / cuộc tranh văn minh |

### Algorithm

```python
if token == "之":
    if phrase in FIXED_ZHI_EXPRESSIONS:
        translate_fixed()
    elif next_token in LOCATIVE_HEADS:
        realize_locative(A, next_token)
    elif next_token in TEMPORAL_HEADS:
        realize_temporal(A, next_token)
    else:
        # classical genitive
        output = B + " của " + A
```

### Special handling

Không đảo bừa với danh từ đã là thuật ngữ cố định:

```text
先天灵宝之威 → uy của tiên thiên linh bảo
文明之争 → cuộc tranh chấp văn minh
```

Cần entity/term protector chạy trước để bảo vệ tên công pháp/trận pháp.

### Files

```text
src/grammar/transfer_rules/rule_zhi_construction.py
data/grammar/zhi_fixed_expressions.json
tests/test_grammar/test_rule_zhi.py
```

---

## 2.4. `以...为 / 以...来 / 用...来`

### Pattern

```text
以 A 为 B
以 A 来 V
用 A 来 V
拿 A 来 V
```

### Transfer

```text
以商业立足 → lấy thương nghiệp làm chỗ đứng
以文明发展为主 → lấy phát triển văn minh làm chính
以A来B → dùng A để B
用A来B → dùng A để B
```

### Disambiguation

`以为` liền nhau = “tưởng rằng”, không phải `以...为`.

```python
if form == "以为":
    translate("tưởng rằng")
elif token == "以" and later_token == "为":
    build_take_as_construction()
```

---

## 2.5. Topic/stance preposition: `对于/对...来说/而言/至于/关于`

### Transfer

```text
对于A来说，B → đối với A mà nói, B
对A而言，B → đối với A, B
至于A，B → còn về A thì B
关于A，B → về A, B
```

### Why important

Trong chương 201–300, phần giải thích thế giới/luận chiến xuất hiện rất nhiều; nếu không nhận diện `对...来说`, tiếng Việt sẽ dễ thành chuỗi word-by-word khó đọc.

### Rule

```python
detect_preposed_topic_pp(
    markers={"对于", "对", "至于", "关于"},
    right_boundary={",", "，", "来说", "而言"}
)
```

---

## 2.6. Accompanying change: `随着...`

### Transfer

```text
随着A，B
→ theo A, B
→ cùng với việc A, B
```

### Heuristic

```python
if A_has_verb_or_aspect:
    vi = "cùng với việc " + A
else:
    vi = "theo " + A
```

Ví dụ:

```text
随着刷怪的进行
→ cùng với việc farm quái tiếp diễn
```

---

## 2.7. Exhaustive alternatives: `无论/不管...也好...都`

### New corpus pattern

```text
不管是A也好，不管是B也好，C
A也好，B也好，C
无论A还是B，都C
```

### Transfer

```text
dù là A hay B thì cũng C
bất kể A hay B, đều C
A cũng được, B cũng được, C
```

### Rule

```python
detect_multi_alt(
    left_markers={"无论", "不管"},
    alt_markers={"还是", "也好", "或是"},
    result_markers={"都", "也"}
)
```

---

## 2.8. Rhetorical questions

### Markers

```text
难道, 岂, 莫非, 怎么可能, 何必, 何不, 怎会
```

### Transfer

| ZH | VI |
|---|---|
| 难道A吗？ | chẳng lẽ A sao? |
| 岂不是A？ | chẳng phải là A sao? |
| 莫非A？ | lẽ nào A? |
| 怎么可能A？ | sao có thể A được? |
| 何必A？ | hà tất phải A? |
| 何不A？ | sao không A? |

### Algorithm

```python
if sentence_has_rhetorical_marker:
    protect_question_particles()
    choose_vi_frame(marker, polarity)
```

### Files

```text
src/grammar/transfer_rules/rule_rhetorical_question.py
data/grammar/rhetorical_markers.json
```

---

## 2.9. Polarity and totality: `没有任何`, `几乎都`, `全部/全都/尽数/统统`

### Transfer

```text
没有任何人可以阻拦
→ không có bất kỳ ai có thể ngăn cản

几乎都看明白了
→ gần như đều đã nhìn ra

全部摆放出来
→ bày ra toàn bộ
```

### Rule

Thêm scope parser cho quantifier để tránh:

```text
không có bất kỳ + NP + có thể + VP
```

không thành:

```text
không có + bất kỳ có thể...
```

---

## 2.10. Modal necessity/compulsion

### Patterns

```text
不得不, 不能不, 必须, 需得, 非...不可, 只能够, 无法不
```

### Transfer

```text
不得不V → đành phải V / không thể không V
非V不可 → nhất định phải V
只能够V → chỉ có thể V
无法不V → không thể không V
```

### Priority

Chạy trước aspect/negative fixer để tránh `không không`.

---

## 2.11. Progressive trend: `越来越`, `越发`, `逐渐`, `渐渐`

### Transfer

```text
越来越A → càng ngày càng A
越发A → càng thêm A
逐渐/渐渐A → dần dần A
```

### Special

`越...越...` đã có ở v7/v8, nhưng `越来越` cần rule riêng, vì không có marker thứ hai.

---

## 2.12. Dialogue, author-note, forum and system boundary

### Problem

Chương 201–300 có nhiều:
- `ps：...`
- `求月票/求订阅`
- forum/title-like phrases
- player slang: `BOSS`, `NPC`, `肝帝`, `脚男`, `开服`, `内测`
- system/game UI: `每日任务`, `倒计时`, `版本更新`

### Rule

Trước grammar transfer cần tách segment type:

```python
class SegmentType(Enum):
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    THOUGHT = "thought"
    SYSTEM_PROMPT = "system_prompt"
    FORUM_POST = "forum_post"
    AUTHOR_NOTE = "author_note"
    CHAPTER_TITLE = "chapter_title"
```

### Handling

```text
AUTHOR_NOTE → optional drop/keep raw based config
CHAPTER_TITLE → number/title converter riêng
FORUM_POST → giữ slang, ít đảo DE/之
SYSTEM_PROMPT → giữ chính xác, ưu tiên term glossary
DIALOGUE → preserve tone/punctuation
```

---

## 3. Bổ sung chuyển đổi số

## 3.1. Phần trăm và xác suất

### Patterns

```text
百分之九十
百分之九十九以上
剩余的百分之一
```

### Transfer

```text
90%
trên 99%
1% còn lại
```

### Algorithm

```python
if pattern == "百分之" + number + qualifier:
    value = chinese_number_to_int(number)
    if qualifier in {"以上", "左右"}:
        attach_qualifier()
```

---

## 3.2. Phân số

### Pattern

```text
二分之一
四分之一
十分之一
三分之二
```

### Transfer

```text
1/2 / một nửa
1/4 / một phần tư
1/10
2/3
```

### Heuristic

```python
if denominator == 2 and context_has_power_comparison:
    "một nửa"
elif denominator in {3,4,10}:
    f"{numerator}/{denominator}" or Vietnamese words by style
```

Config:

```json
{
  "number_style": {
    "fraction": "words|symbol|auto"
  }
}
```

---

## 3.3. Ranges and rank ranges

### Pattern

```text
五百零一到一千名
一千零一到一千五百名
十到十五点经验值
一到两万名额
```

### Transfer

```text
hạng 501 đến 1.000
hạng 1.001 đến 1.500
10 đến 15 điểm kinh nghiệm
10.000 đến 20.000 suất
```

### Algorithm

```python
detect_range(left_number, connector={"到", "至", "-", "—"}, right_number)
if unit_after_right:
    attach_unit_to_whole_range()
if unit == "名" and preceding context has ranking:
    translate_as_rank_range()
```

---

## 3.4. Rank, level, tier, generation

### Patterns

```text
一级, 二级, 二阶, 一阶, 第二代血族, 第一代血族, 三大灾
```

### Transfer

| ZH | VI |
|---|---|
| 一级 | cấp 1 |
| 二阶 | bậc 2 / cấp 2 |
| 第二代血族 | huyết tộc đời thứ hai |
| 三大灾 | ba đại tai họa |

### Rule

```python
if number + {"级", "阶", "层", "品"}:
    semantic = infer_domain(context)
    if game_context:
        return "cấp N"
    if cultivation_context:
        return "bậc/tầng N"
    if item_context:
        return "phẩm cấp N"
```

### Protected entity cases

```text
一阶基因锁 → khóa gien bậc một
二代血族 → huyết tộc đời thứ hai
第一代血族 → huyết tộc đời đầu
```

---

## 3.5. Duration/countdown/frequency

### Patterns

```text
三十天后
四十八小时
每七天开放一次
一天二十四小时
每个月
最多一周之内
```

### Transfer

```text
sau 30 ngày
48 giờ
mở một lần mỗi 7 ngày
24 giờ một ngày
mỗi tháng
trong vòng tối đa một tuần
```

### Algorithm

```python
if number + time_unit + "后":
    output = "sau " + duration
elif "每" + duration + "一次":
    output = "mỗi " + duration + " một lần"
elif duration + "之内":
    output = "trong vòng " + duration
```

---

## 3.6. Inventory/resource quantities

### Patterns

```text
一千件精钢武器
五百件皮甲
五百把精品长弓
五十颗灵石
一万多奖励点数
十万是个好数字
```

### Transfer

```text
1.000 món vũ khí thép tinh luyện
500 bộ giáp da
500 cây trường cung thượng phẩm
50 viên linh thạch
hơn 10.000 điểm thưởng
100.000 là một con số đẹp
```

### Unit classifier map

```json
{
  "颗": {"default": "viên", "terms": ["灵石", "丹药", "珠"]},
  "件": {"equipment": "món/bộ", "armor": "bộ"},
  "把": {"weapon": "cây/thanh", "sword": "thanh", "bow": "cây"},
  "枚": {"default": "viên/miếng"},
  "点": {"game": "điểm"},
  "点数": {"game": "điểm"}
}
```

---

## 3.7. Approximation and excess

### Patterns

```text
数十传奇
近十半神
一万多
至少百年以上
差不多十到十五点
超过百分之九十九以上
```

### Transfer

```text
mấy chục truyền kỳ
gần mười bán thần
hơn mười nghìn
ít nhất hơn trăm năm
khoảng 10 đến 15 điểm
trên 99%
```

### Rule priority

```text
超过/以上 > 多 > 近/将近 > 差不多/大约/约 > 数十/数百/数千/数万
```

---

## 4. Bổ sung nhận diện tên riêng / thuật ngữ

## 4.1. Entity types mới từ chương 201–300

| Type | Examples | VI strategy |
|---|---|---|
| PERSON | 吴明, 路西法, 阿莫尔, 喀戎, 诺比汗 | glossary/Hán-Việt/phonetic |
| RACE_SPECIES | 血族, 精灵族, 兽人, 野兽人, 古兽人, 地灵族, 天蛇族 | term dictionary |
| ORGANIZATION | 商业联盟, 掠夺者联盟, 血红玫瑰冒险团 | protect as named entity |
| LOCATION | 金河城, 洪荒大陆, 无尽森林, 精灵帝国 | location suffix parser |
| REALM_PLANE | 外位面, 低纬度, 高纬度, 掌中位面 | technical cosmology term |
| ITEM_EQUIPMENT | 诛仙四剑, 诛仙剑, 河图洛书, 东皇钟 | mythic item glossary |
| RESOURCE | 奖励点数, 灵石, 经验值, 支线剧情 | game/system resource |
| SYSTEM_GAME | 副本, BOSS, NPC, 内测, 开服, 每日任务 | game glossary |
| TITLE_RANK | 圣位, 灵位, 半神, 传奇, 高阶魔法师 | rank/title lexicon |
| CULTIVATION/TECHNIQUE | 中央戊土厚德诀, 真话术, 魔法迷锁 | technique/proper-title protector |

---

## 4.2. Suffix-role classifier mở rộng

### Data file

```text
data/entities/entity_suffix_roles.json
```

### Proposed mapping

```json
{
  "族": "RACE_SPECIES",
  "联盟": "ORGANIZATION",
  "帝国": "ORGANIZATION_OR_LOCATION",
  "冒险团": "ORGANIZATION",
  "城": "LOCATION",
  "大陆": "LOCATION",
  "森林": "LOCATION",
  "位面": "REALM_PLANE",
  "空间": "REALM_PLANE_OR_SYSTEM",
  "副本": "SYSTEM_GAME",
  "点数": "RESOURCE",
  "经验值": "RESOURCE",
  "灵石": "RESOURCE",
  "剑": "WEAPON_OR_ITEM",
  "刀": "WEAPON_OR_ITEM",
  "钟": "ARTIFACT",
  "书": "ITEM_OR_TEXT",
  "诀": "TECHNIQUE",
  "术": "TECHNIQUE_OR_SPELL",
  "法": "TECHNIQUE_OR_METHOD",
  "阵": "FORMATION",
  "圣位": "RANK_TITLE",
  "灵位": "RANK_TITLE",
  "半神": "RANK_TITLE",
  "传奇": "RANK_TITLE"
}
```

---

## 4.3. Long nominal entity detector

### Problem

Những cụm như sau không có `的`, nhưng là entity/term hoặc danh ngữ chuyên môn:

```text
血红玫瑰冒险团
洪荒万兽阵
奖励点数使用计划白皮书
魔法工业革命临界点
精灵族的血色气运
```

### Algorithm

```python
def detect_long_nominal_entity(tokens):
    # 1. detect suffix head
    head = rightmost_token_with_entity_suffix()
    # 2. absorb left modifiers until boundary
    span = absorb_left_until(
        stop_pos={"PU", "CC", "SP", "ASP", "BA", "BEI"},
        stop_words={"是", "在", "有", "把", "被", "将"}
    )
    # 3. confidence score
    score = suffix_score + capitalization_score + recurrence_score + glossary_score
    # 4. protect if score >= threshold
```

### Confidence features

```text
+0.35 suffix head known
+0.25 appears >=2 times in corpus
+0.20 contains myth/game/cultivation keyword
+0.20 known glossary hit
-0.30 contains common verb in middle
-0.30 too long without suffix
```

---

## 4.4. Player/forum nickname detector

### New issue

Corpus có slang và nickname kiểu:

```text
我草我草, 曰了狗, 不可能, BOSS, NPC
```

### Rule

```python
if span contains Latin uppercase or slang dictionary hit:
    protect_as_SYSTEM_OR_NICKNAME
```

Config:

```json
{
  "player_slang_terms": {
    "脚男": "người chơi",
    "肝帝": "dân cày",
    "开服": "mở server",
    "内测": "closed beta",
    "公测": "open beta",
    "BOSS": "BOSS",
    "NPC": "NPC"
  }
}
```

---

## 4.5. Mythic item and canon term protector

### Required glossary additions

```json
{
  "东皇钟": "Đông Hoàng Chung",
  "河图洛书": "Hà Đồ Lạc Thư",
  "诛仙四剑": "Tru Tiên Tứ Kiếm",
  "诛仙剑": "Tru Tiên Kiếm",
  "先天灵宝": "tiên thiên linh bảo",
  "先天至宝": "tiên thiên chí bảo",
  "掌中位面": "vị diện trong lòng bàn tay",
  "外位面": "ngoại vị diện",
  "低纬度": "chiều thấp",
  "高纬度": "chiều cao"
}
```

---

## 5. Module bổ sung đề xuất

```text
src/grammar/
├── suo_zhi_detector.py
├── discourse_boundary_detector.py
├── rhetorical_question_detector.py
├── entity_suffix_classifier.py
├── number_context_classifier.py
└── transfer_rules/
    ├── rule_jiang_disambiguation.py
    ├── rule_suo_construction.py
    ├── rule_zhi_construction.py
    ├── rule_yi_construction.py
    ├── rule_topic_stance_pp.py
    ├── rule_accompanying_change.py
    ├── rule_rhetorical_question.py
    ├── rule_totality_quantifier.py
    ├── rule_modal_necessity.py
    └── rule_progressive_trend.py

data/grammar/
├── suo_patterns.json
├── zhi_fixed_expressions.json
├── yi_construction_patterns.json
├── rhetorical_markers.json
├── discourse_segment_markers.json
├── totality_quantifiers.json
├── modal_necessity.json
└── number_context_patterns_v2.json

data/entities/
├── entity_suffix_roles.json
├── game_system_terms.json
├── mythic_items.json
├── race_species_terms.json
├── organization_terms.json
├── realm_plane_terms.json
└── player_slang_terms.json
```

---

## 6. Rule priority cập nhật v11

```text
0. HTML/chapter/author-note cleanup
1. Segment boundary: narration/dialogue/forum/system/title
2. Entity protector + number span protector
3. LogicRelationDetector: condition/concession/contrast/cause/time
4. Suo/Zhi/Yi classical-formal constructions
5. Jiang/BA/BEI disposal-passive
6. DE/nominal-chain parser
7. NumberSemanticClassifier
8. Aspect/DIR/resultative/potential/degree complements
9. Rhetorical question + sentence particle
10. VI surface postprocess
```

Lý do: `所/之/以/将` tạo khung danh ngữ và mệnh đề lớn; nếu xử lý sau `DE/BA/Aspect`, rất dễ làm lệch span.

---

## 7. Test suite bổ sung

### 7.1. Grammar tests

```text
test_rule_jiang_disambiguation.py
test_rule_suo_construction.py
test_rule_zhi_construction.py
test_rule_yi_construction.py
test_rule_topic_stance_pp.py
test_rule_rhetorical_question.py
test_rule_modal_necessity.py
test_rule_progressive_trend.py
```

### 7.2. Number tests

```text
百分之九十 → 90%
百分之一 → 1%
二分之一 → một nửa
四分之一 → 1/4
五百零一到一千名 → hạng 501 đến 1.000
一到两万名额 → 10.000 đến 20.000 suất
四十八小时 → 48 giờ
每七天开放一次 → mở một lần mỗi 7 ngày
第二代血族 → huyết tộc đời thứ hai
二阶顶尖 → đỉnh cao bậc hai
一万多奖励点数 → hơn 10.000 điểm thưởng
```

### 7.3. Entity tests

```text
血红玫瑰冒险团 → Blood Red Rose Adventurer Group / Huyết Hồng Mân Côi mạo hiểm đoàn
商业联盟 → Liên minh Thương nghiệp
掠夺者联盟 → Liên minh Cướp đoạt
金河城 → thành Kim Hà
无尽森林 → rừng Vô Tận
诛仙四剑 → Tru Tiên Tứ Kiếm
东皇钟 → Đông Hoàng Chung
河图洛书 → Hà Đồ Lạc Thư
中央戊土厚德诀 → Trung Ương Mậu Thổ Hậu Đức Quyết
```

---

## 8. Acceptance criteria cho v11

```text
A. Grammar:
   - 将 disambiguation accuracy >= 90% trên mẫu ch201–300.
   - 所/之 constructions accuracy >= 85%.
   - Rhetorical question accuracy >= 85%.
   - Topic/stanced PP accuracy >= 85%.

B. Number:
   - percent/fraction/range/duration/resource/rank conversion >= 90%.
   - Không chuyển sai số trong tên riêng/công pháp/trận pháp.
   - Hỗ trợ style config: Arabic/VI words/auto.

C. Entity:
   - Protect đúng >= 90% các entity có suffix rõ.
   - Detect được organization/location/race/item/system term mới.
   - Không tách sai `第二代血族`, `诛仙四剑`, `奖励点数`.

D. Regression:
   - Flag off: toàn bộ baseline tests cũ pass.
   - Flag on: grammar corpus tests pass, fallback không crash.
```

---

## 9. Checklist triển khai thêm vào roadmap

```text
[ ] Add discourse_boundary_detector.py
[ ] Add entity_suffix_classifier.py
[ ] Add suo_zhi_detector.py
[ ] Add rule_jiang_disambiguation.py
[ ] Add rule_suo_construction.py
[ ] Add rule_zhi_construction.py
[ ] Add rule_yi_construction.py
[ ] Add rule_topic_stance_pp.py
[ ] Add rule_rhetorical_question.py
[ ] Add rule_totality_quantifier.py
[ ] Add rule_modal_necessity.py
[ ] Add rule_progressive_trend.py
[ ] Expand number_context_classifier.py
[ ] Add entity suffix data files
[ ] Add game/system/mythic glossary files
[ ] Add 100-chapter regression sample builder
[ ] Add v11 corpus accuracy report
```

---

## 10. Kết luận

Chương 201–300 cho thấy thuật toán hiện cần nâng từ “grammar transfer câu phổ thông” sang **formal/classical + system/game + entity-aware transfer**.

Ba bổ sung quan trọng nhất của v11 là:

```text
1. 所/之/以/将 parser
2. Number semantic classifier v2
3. Entity suffix classifier + long nominal protector
```

Nếu triển khai 3 nhóm này trước, chất lượng dịch các chương 201–300 sẽ tăng rõ nhất, đặc biệt với các đoạn nghị luận thế giới quan, hệ thống game, danh sách tài nguyên, và thuật ngữ thần thoại/tu luyện.
