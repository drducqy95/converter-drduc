# GRAMMAR_TRANSFER_PLAN_v9 — First-100-Chapter Corpus Completion

**Repo:** `converter-drduc`  
**Input corpus:** `Hồng Hoang Lịch_Zhttty.html`  
**Scope phân tích:** 100 chương đầu, từ `chapter-1` đến `chapter-100`  
**Mục tiêu:** bổ sung các cấu trúc ngữ pháp và chuyển đổi số còn thiếu cho thuật toán ZH→VI Grammar Transfer.

---

## 0. Kết luận nhanh

Sau khi đọc và trích xuất 100 chương đầu, corpus có đặc trưng khác rõ so với các chương rời trước đó:

1. Câu rất dài, nhiều mệnh đề lồng nhau.
2. Dày đặc các cấu trúc logic: điều kiện, nhượng bộ, phủ định đối lập, nguyên nhân-kết quả, mục đích, giới hạn.
3. Nhiều danh ngữ dài dạng không có `的`: tổ chức, hệ thống, thuật ngữ tu chân, vật phẩm, quyền hạn, chỉ số.
4. Nhiều số thuộc hệ game/hệ thống: `奖励点数`, `支线剧情`, `天道眷属值`, cấp `a/b/c级`, thứ bậc `一阶/五阶`, phần trăm, phân số, khoảng, xấp xỉ, deadline.
5. Nhiều câu có `将`, `把`, `被`, `由/为...所...`, `使得/导致/造成/令`, cần rule riêng thay vì chỉ dựa vào lexical lookup.
6. Nhiều cấu trúc văn nghị luận/giải thích: `所谓`, `名为`, `称为`, `之一`, `之中`, `之内`, `对于`, `关于`, `至于`, `随着`, `通过`, `凭借`.

Do đó bản v9 bổ sung một lớp mới:

```text
LogicRelationDetector
NumberSemanticClassifier
NominalChainParser
SystemTermProtector
ClauseGraphTransfer
```

Các lớp này chạy sau tokenizer/POS/entity protection, trước transfer rules hiện có.

---

## 1. Dữ liệu quan sát từ 100 chương đầu

### 1.1. Quy mô đọc

Script phân tích nội bộ trích từ HTML:

```text
Chapters read: 100
Text size: ~328k Chinese chars
Sentence-like units: ~4,728
Paragraphs: ~3,926
```

### 1.2. Nhóm cấu trúc xuất hiện nhiều

| Nhóm | Pattern | Tần suất gần đúng trong 100 chương | Mức ưu tiên |
|---|---:|---:|---|
| Nhượng bộ | `虽然...但是/却`, `即便/即使/哪怕` | rất cao | P0 |
| Điều kiện | `若是/如果/只要/一旦/除非` | rất cao | P0 |
| Tiến trình thời gian | `直到...才`, `一...就`, `刚...就`, `先...再` | cao | P0 |
| Đối lập/đính chính | `不是...而是`, `并非/并不是`, `不但...而且` | cao | P0 |
| So sánh/tăng tiến | `越...越`, `越来越`, `越发` | cao | P0 |
| Nhấn mạnh cực hạn | `连...都/也`, `甚至`, `哪怕` | rất cao | P0 |
| Passive formal | `由...所`, `为...所`, `被` | cao | P0 |
| Causative/result | `使得`, `导致`, `造成`, `令`, `从而`, `以至于` | cao | P0 |
| Topic/preposition | `对于`, `关于`, `至于`, `随着`, `通过`, `凭借` | cao | P1 |
| Complement `得` | degree/result/potential-like | rất cao | P0 |
| Định danh/định nghĩa | `所谓`, `名为`, `称为`, `叫做` | cao | P1 |
| Phạm vi | `之一`, `之中`, `之内`, `之间`, `以上`, `以下` | cao | P1 |
| Game/system number | `奖励点数`, `支线剧情`, `天道眷属值`, `级/阶` | rất cao | P0 |

---

## 2. Bổ sung kiến trúc thuật toán v9

### 2.1. Pipeline đề xuất sau v9

```text
Input ZH
  ↓
TextNormalizer / TraditionalSimplified
  ↓
SentenceSegmenter with Quote/System boundary
  ↓
ZHTokenizer + EntityProtector
  ↓
NumberSemanticClassifier          ← NEW
  ↓
POSTagger
  ↓
NominalChainParser                ← NEW
  ↓
LogicRelationDetector             ← NEW
  ↓
ShallowConstructionDetector
  ↓
ClauseGraphTransfer               ← NEW
  ↓
TransferEngine rules
  ↓
RBMT lexical loop existing
  ↓
VI grammar postprocess
  ↓
Output VI
```

### 2.2. Module mới cần thêm

```text
src/grammar/
├── logic_relation_detector.py
├── clause_graph.py
├── nominal_chain_parser.py
├── system_term_protector.py
├── number_semantic_classifier.py
└── transfer_rules/
    ├── rule_logic_condition.py
    ├── rule_logic_concession.py
    ├── rule_logic_contrast.py
    ├── rule_logic_cause_result.py
    ├── rule_logic_temporal.py
    ├── rule_emphasis_even.py
    ├── rule_formal_passive.py
    ├── rule_de_complement.py
    ├── rule_definition_naming.py
    ├── rule_scope_range.py
    └── rule_nominal_chain.py

data/grammar/
├── logic_patterns.json
├── number_semantic_patterns.json
├── system_terms.json
├── cultivation_levels.json
├── game_resource_terms.json
└── nominal_suffix_roles.json
```

---

## 3. LogicRelationDetector — nhận diện quan hệ mệnh đề

### 3.1. Data structure

```python
@dataclass(slots=True)
class ClauseSpan:
    start: int
    end: int
    role: str              # condition, result, concession, main, cause, effect, topic...

@dataclass(slots=True)
class LogicRelation:
    type: str              # condition, concession, contrast, cause_result, temporal, emphasis
    markers: list[int]
    clauses: list[ClauseSpan]
    confidence: float = 1.0
    data: dict = field(default_factory=dict)
```

### 3.2. Rule priority

Ưu tiên xử lý theo quan hệ khung câu lớn:

```text
1. quote/dialogue/system prompt boundary
2. condition/concession/contrast
3. cause-result
4. temporal sequencing
5. emphasis/extreme
6. local complements
```

Lý do: nếu xử lý `得`, `了`, `把`, `被` trước khi xác định khung `虽然...但是`, `只要...就`, `直到...才`, output dễ sai trật tự mệnh đề.

---

## 4. Các cấu trúc ngữ pháp cần bổ sung

## 4.1. Điều kiện giả định: `若是/如果/倘若/若`

### Pattern

```text
若是 A, B
如果 A, B
若 A, 则 B
```

### Transfer

```text
Nếu A thì B
Nếu A, B
```

### Thuật toán

```python
if marker in {"若是", "如果", "倘若", "若"}:
    cond = span_after_marker_until_pause_or_result_marker()
    result = remaining_main_clause()
    insert_vi_before(cond, "nếu")
    optional_insert_before(result, "thì") if result_is_long else None
```

### Edge cases

```text
若是从历史真文的时间节点来看
→ nếu xét từ mốc thời gian của chân văn lịch sử
```

Không dịch `若` trong tên riêng/thuật ngữ nếu được entity protector bảo vệ.

---

## 4.2. Điều kiện đủ: `只要...就...`

### Transfer

```text
只要 A 就 B
→ chỉ cần A thì B
```

### Rule

```python
pattern = PairPattern(left="只要", right={"就", "便"})
output = "chỉ cần" + A + "thì" + B
```

### Test

```text
只要出现过的就会全部摆放出来
→ chỉ cần từng xuất hiện thì sẽ được bày ra toàn bộ
```

---

## 4.3. Điều kiện tức thời: `一旦...就/便...`

### Transfer

```text
一旦 A 就 B
→ một khi A thì B
```

### Note

`一旦` không được chuyển thành số `một + sáng` hoặc tách `一/旦`.

```python
protect_fixed_expression("一旦", tag="COND_MARKER")
```

---

## 4.4. Điều kiện loại trừ: `除非...否则...`

### Transfer

```text
除非 A，否则 B
→ trừ khi A, nếu không thì B
```

### Test

```text
除非是拥有文字文明传承的人类部落，否则我无法...
→ trừ khi là bộ lạc nhân loại có chữ viết và truyền thừa văn minh, nếu không thì ta không thể...
```

---

## 4.5. Điều kiện cần: `只有...才...`

### Transfer

```text
只有 A 才 B
→ chỉ khi A mới B
```

### Difference với `只要...就`

```text
只要 A 就 B = sufficient condition = chỉ cần A thì B
只有 A 才 B = necessary condition = chỉ khi A mới B
```

Bắt buộc có classifier riêng, không gom chung.

---

## 4.6. Nhượng bộ: `虽然...但是/却/可...`

### Transfer

```text
虽然 A，但是 B
→ tuy A, nhưng B
```

### Rule

```python
left_markers = {"虽然"}
right_markers = {"但是", "但", "却", "可", "不过"}
```

### Special

Nếu vế B có `却`, dịch `nhưng lại`.

```text
虽然有工作，但是工作的目的正是为了不工作
→ tuy có công việc, nhưng mục đích làm việc chính là để không phải làm việc
```

---

## 4.7. Nhượng bộ cực hạn: `即便/即使/哪怕...也/都...`

### Transfer

```text
即便 A, 也 B
→ cho dù A, cũng B
哪怕 A, 都 B
→ dù A, vẫn B
```

### Algorithm

```python
if left in {"即便", "即使", "哪怕"}:
    mark_clause_as_concession()
    if right in {"也", "都"}:
        map_right_to("cũng" or "vẫn")
```

---

## 4.8. Đối lập/đính chính: `不是...而是...`

### Transfer

```text
不是 A，而是 B
→ không phải A, mà là B
```

### Important

Đây không phải phủ định thường. Không được dịch từng token thành “không là... mà là...” nếu danh ngữ dài.

```python
if pair("不是", "而是"):
    skip_literal_negation = True
    insert("không phải")
    insert("mà là")
```

---

## 4.9. Phủ định xác nhận: `并非/并不是`

### Transfer

```text
并非 A
→ không hề phải là A / vốn không phải A
并不是 A
→ không phải là A
```

### Register

```text
formal/narrative: "không hề phải là"
neutral: "không phải là"
```

---

## 4.10. Liên tiến: `不仅/不但...而且/还/也...`

### Transfer

```text
不但 A，而且 B
→ không chỉ A, mà còn B
不仅 A，还 B
→ không chỉ A, còn B
```

### Rule

Pair marker bắt buộc. Nếu chỉ có `不仅` không có right marker, fallback:

```text
不仅 A。B
→ không chỉ A. B
```

---

## 4.11. So sánh tăng tiến: `越...越...`

### Transfer

```text
越 A 越 B
→ càng A càng B
```

### Variants

```text
越是 A，越是 B
→ càng là/càng A, càng B
情况越危急，他越冷静
→ tình huống càng nguy cấp, hắn càng bình tĩnh
```

### Algorithm

```python
detect all 越 tokens within same sentence
if count >= 2:
    split at first two 越
    map each to "càng"
```

### Edge

`越发` = “càng thêm/ngày càng”, không phải pair structure.

---

## 4.12. Tăng tiến trạng thái: `越来越/越发`

### Transfer

```text
越来越 A
→ ngày càng A
越发 A
→ càng thêm A / ngày càng A
```

### Protection

Không tách `越` làm marker pair nếu token là `越来越` hoặc `越发`.

---

## 4.13. Nhấn mạnh cực hạn: `连...都/也...`

### Transfer

```text
连 A 都 B
→ ngay cả A cũng B
连虚空都算不上
→ ngay cả hư không cũng không tính là
```

### Algorithm

```python
span = between("连", right_marker in {"都", "也"})
insert_before(span, "ngay cả")
map_right_marker_to("cũng")
```

### Interaction with negation

```text
连一个守卫都没有
→ ngay cả một thủ vệ cũng không có
```

---

## 4.14. Temporal: `直到...才...`

### Transfer

```text
直到 A 才 B
→ mãi đến khi A mới B
```

### Rule

```python
pair("直到", "才")
```

Nếu `直到` + time phrase không có `才`, dịch “cho đến khi”.

---

## 4.15. Temporal immediate: `一...就...`, `刚...就...`, `刚一...就...`

### Transfer

```text
一 A 就 B
→ vừa A thì đã B
刚 A 就 B
→ vừa mới A đã B
刚一 A 就 B
→ vừa mới A thì đã B
```

### Ambiguity

`一` trong số lượng không được nhận là temporal marker nếu sau là classifier/object:

```text
一个人就...
```

Rule cần POS/Phrase check:

```python
if token("一") and next_pos in {CLF, NUM_UNIT}:
    not_temporal()
```

---

## 4.16. Sequential: `先...再/然后/之后...`

### Transfer

```text
先 A，然后 B
→ trước tiên A, sau đó B
先 A 再 B
→ trước tiên A rồi B
```

### Corpus need

Câu dài hành động liên tiếp rất nhiều, đặc biệt các đoạn chiến đấu, thao tác hệ thống, đổi thưởng.

---

## 4.17. Cause-result: `因为/由于/正因为...所以/因此...`

### Transfer

```text
因为 A，所以 B
→ vì A nên B
由于 A，因此 B
→ do A nên B
正因为如此
→ chính vì vậy
```

### Rule

```python
cause_markers = {"因为", "由于", "正因为"}
result_markers = {"所以", "因此", "故", "从而"}
```

---

## 4.18. Result/cause verbs: `使得/导致/造成/令`

### Transfer

```text
A 导致 B
→ A dẫn đến B
A 使得 B
→ A khiến B
A 造成 B
→ A gây ra B
令 B A
→ khiến B A
```

### Algorithm

`令` cần phân biệt:

```text
命令 = ra lệnh
令 + NP + VP/Adj = khiến NP VP/Adj
```

---

## 4.19. Purpose: `为了/以便/用来/用于`

### Transfer

```text
为了 A, B
→ để A, B / vì A mà B
B 用来 A
→ B dùng để A
用于 A
→ dùng cho A / dùng để A
以便 A
→ để tiện A / nhằm A
```

### Difference

`为了` có thể là purpose hoặc beneficiary:

```text
为了人类
→ vì nhân loại
为了查看历史真文
→ để xem chân văn lịch sử
```

Heuristic:

```python
if following_span_has_verb: "để"
else: "vì"
```

---

## 4.20. Method/instrument: `通过/凭借/依靠/靠着`

### Transfer

```text
通过 A, B
→ thông qua A, B
凭借 A, B
→ nhờ vào A, B
依靠 A, B
→ dựa vào A, B
靠着 A, B
→ dựa vào/nhờ A, B
```

### Parser role

Mark span as `advcl:means`, không làm object chính.

---

## 4.21. Topic-preposition: `对于/关于/至于`

### Transfer

```text
对于 A, B
→ đối với A, B
关于 A, B
→ về A, B
至于 A, B
→ còn về A thì B
```

### Important

Cấu trúc này thường mở đầu mệnh đề nghị luận, cần giữ đầu câu trong tiếng Việt.

---

## 4.22. Accompanying change: `随着...`

### Transfer

```text
随着 A, B
→ theo A, B
→ cùng với việc A, B
```

### Heuristic

```python
if A is nominal: "theo" + A
if A contains verb/aspect: "cùng với việc" + A
```

---

## 4.23. Formal passive: `由...所...`, `为...所...`

### Transfer

```text
由 A 所 V
→ do A V / được A V
为 A 所 V
→ bị/được A V
```

### Sentiment decision

Use sentiment lexicon:

```python
if verb in negative: "bị"
elif verb in positive: "được"
else: "do ... V" for neutral formal
```

### Examples

```text
由机器人所取代
→ bị robot thay thế / được robot thay thế tùy ngữ cảnh
为...所困
→ bị ... vây khốn
```

---

## 4.24. `将` disposal/formal object-fronting

### Pattern

```text
将 O V
将 O 作为/视为/称为 C
```

### Transfer

```text
将 O V
→ V O / đem O V
将 O 作为 C
→ lấy O làm C
将 O 视为 C
→ xem O là C
将 O 称为 C
→ gọi O là C
```

### Difference với future `将`

```python
if 将 followed by verb directly: future = "sẽ"
if 将 followed by NP then verb: disposal = object marker
```

---

## 4.25. `把` disposal nâng cấp

### Bổ sung pattern từ corpus

```text
把 O V成 C
把 O V到 Location/State
把 O V为 C
把 O V得 Complement
```

### Transfer

```text
把 O 变成 C
→ biến O thành C
把 O 放到 X
→ đặt O đến/vào X
把 O 看作 C
→ xem O là C
```

---

## 4.26. Complement `得` — rule chi tiết hơn

`得` là pattern xuất hiện rất nhiều, cần tách 4 loại:

### Type A — Degree complement

```text
Adj/V 得 很/多/可怜/厉害/出奇
→ V/Adj đến mức ... / rất ...
```

Examples:

```text
少得可怜
→ ít đến đáng thương
大得出奇
→ lớn đến kỳ lạ
弱小得多
→ yếu hơn nhiều
```

### Type B — Result complement

```text
V 得 NP/Clause
→ V đến mức NP/Clause
```

### Type C — Potential complement

```text
V 得了 / V 不得
V 得动 / V 不动
```

```text
走得动
→ đi nổi
走不动
→ không đi nổi
```

### Type D — Structural `得` after perception/feeling

```text
觉得 / 记得 / 显得 / 懂得
```

Phải protect as lexical compounds, không split.

```python
protected_de_compounds = {"觉得", "记得", "显得", "懂得", "获得"}
```

---

## 4.27. Definition/naming: `所谓/名为/称为/叫做`

### Transfer

```text
所谓 A
→ cái gọi là A
名为 A 的 B
→ B tên là A / B được gọi là A
A 称为 B
→ A được gọi là B
叫做 A
→ gọi là A
```

### Entity interaction

Nếu A là protected entity, giữ nguyên transliteration/glossary.

---

## 4.28. Scope/range: `之一/之中/之内/之间/以上/以下/以内`

### Transfer

```text
A 之一
→ một trong những A
A 之中
→ trong A
A 之内 / 以内
→ trong vòng A / trong phạm vi A
A 之间
→ giữa A
A 以上
→ từ A trở lên / trên A
A 以下
→ từ A trở xuống / dưới A
```

### Semantic classification

```python
if A is duration: 以内/之内 = "trong vòng"
if A is location/group: 之内 = "bên trong/trong"
if A is rank/level: 以上/以下 = "trở lên/trở xuống"
```

---

## 4.29. Existential/possessive: `有着/具有/拥有`

### Transfer

```text
有着 A
→ có A / mang A
具有 A
→ có/sở hữu A
拥有 A
→ sở hữu A
```

### Style

Xianxia/formal:

```text
有着特殊性
→ có tính đặc thù
具有资质
→ có tư chất
拥有权限
→ có quyền hạn
```

---

## 4.30. Appearance/evidential: `似乎/仿佛/看起来/显得/宛如`

### Transfer

```text
似乎 A
→ dường như A
仿佛 A
→ như thể A
看起来 A
→ trông có vẻ A
显得 A
→ tỏ ra/có vẻ A
宛如 A
→ tựa như A
```

---

## 5. NumberSemanticClassifier — hoàn thiện chuyển đổi số

## 5.1. Mục tiêu

Không chỉ chuyển chữ số, mà phải phân loại chức năng số theo context:

```text
NUM_CARDINAL        số đếm thường
NUM_ORDINAL         thứ tự
NUM_DURATION        thời lượng
NUM_DEADLINE        deadline/countdown
NUM_DATE            ngày tháng năm
NUM_TIME_CLOCK      giờ trong ngày
NUM_PERCENT         phần trăm
NUM_FRACTION        phân số
NUM_RANGE           khoảng
NUM_APPROX          xấp xỉ
NUM_MULTIPLIER      bội số
NUM_LEVEL_RANK      cấp/bậc/giai
NUM_GAME_RESOURCE   điểm thưởng, kịch tình nhánh
NUM_CULTIVATION     cảnh giới tu luyện
NUM_POWER_INDEX     chỉ số sức mạnh
NUM_ENTITY_PROTECTED số thuộc tên riêng/thuật ngữ
```

---

## 5.2. Deadline/countdown

### Pattern

```text
三十秒内
三十秒之内
十天后
倒计时三十秒
```

### Transfer

```text
三十秒内进入光柱
→ tiến vào cột sáng trong vòng 30 giây
十天后
→ sau 10 ngày
```

### Rule

```python
if unit in TIME_UNITS and suffix in {"内", "之内", "以内"}:
    type = NUM_DEADLINE
    vi = f"trong vòng {number} {unit_vi}"
elif suffix in {"后", "之后"}:
    vi = f"sau {number} {unit_vi}"
elif suffix in {"前", "之前"}:
    vi = f"trước {number} {unit_vi}"
```

---

## 5.3. Duration

### Pattern

```text
一小时
五六个小时
数个月时间
百年内
亿亿万万年
```

### Transfer

```text
一小时 → một giờ / 1 giờ
五六个小时 → khoảng 5-6 giờ
数个月时间 → mấy tháng / vài tháng
百年内 → trong vòng trăm năm
亿亿万万年 → hàng ức ức vạn vạn năm
```

### Note

`亿亿万万` nên giữ sắc thái phóng đại, không convert máy móc thành số 10^n.

---

## 5.4. Approximation

### Pattern

```text
约莫三四秒
大约四到六人
差不多一小时
至少五天
最多一个月以内
超过十人后
近百人
数以亿万计
```

### Transfer

```text
约莫三四秒 → khoảng 3-4 giây
大约四到六人 → khoảng 4-6 người
至少五天 → ít nhất 5 ngày
最多一个月以内 → nhiều nhất trong vòng 1 tháng
超过十人后 → sau khi vượt quá 10 người
数以亿万计 → tính bằng hàng ức vạn
```

### Algorithm

```python
approx_markers = {
  "约", "约莫", "大约", "差不多", "左右", "上下",
  "至少", "最多", "近", "将近", "超过", "不足", "数以"
}
```

---

## 5.5. Range

### Pattern

```text
五十到一百人
四到六人
20-50之间
200-300左右
两到三寸
```

### Transfer

```text
五十到一百人 → 50 đến 100 người
四到六人 → 4 đến 6 người
20-50之间 → trong khoảng 20-50
两到三寸 → 2 đến 3 thốn
```

### Rule

```python
range_markers = {"到", "至", "-", "—", "~"}
if both sides numeric:
    type = NUM_RANGE
```

---

## 5.6. Percent

### Pattern

```text
百分之九十八点几
百分之三十七左右
百分之九十三还多
```

### Transfer

```text
百分之九十八点几 → hơn 98% / khoảng 98 phẩy mấy phần trăm
百分之三十七左右 → khoảng 37%
百分之九十三还多 → hơn 93%
```

### Algorithm

```python
if pattern 百分之 + number + 点几:
    vi = "khoảng/hơn {int} phẩy mấy phần trăm"
if suffix 左右:
    vi = "khoảng {n}%"
if suffix 还多:
    vi = "hơn {n}%"
```

---

## 5.7. Fraction

### Pattern

```text
三分之一
万分之一
二分之一
```

### Transfer

```text
三分之一 → một phần ba
万分之一 → một phần vạn
二分之一 → một nửa / một phần hai
```

### Rule

```python
X分之Y = Y / X
```

Special Vietnamese naturalization:

```text
二分之一 → một nửa
三分之一 → một phần ba
四分之一 → một phần tư
```

---

## 5.8. Level/rank/class

### Pattern

```text
五阶基因锁
一阶实力
c级支线剧情
初级权限
第一权限者
第六感
第五代主战斗机
```

### Transfer

```text
五阶基因锁 → khóa gen bậc năm
一阶实力 → thực lực bậc một
c级支线剧情 → tình tiết nhánh cấp C
初级权限 → quyền hạn sơ cấp
第一权限者 → người có quyền hạn cấp một / quyền hạn số một
第六感 → giác quan thứ sáu
第五代主战斗机 → tiêm kích chủ lực thế hệ thứ năm
```

### Classifier

```python
if suffix in {"阶", "级"}:
    if next_token in cultivation_terms: NUM_CULTIVATION
    elif prev/next contains 支线剧情: NUM_GAME_RESOURCE
    else: NUM_LEVEL_RANK
if pattern 第N代:
    type = GENERATION
if fixed_expression 第六感:
    protect as lexical idiom
```

---

## 5.9. Game/system resources

### Pattern

```text
奖励点数五十
三点奖励点数
五千点奖励点数
一个c级支线剧情
天道眷属值
每次召唤十点奖励点数
超过十人后，每次召唤一百奖励点数
```

### Transfer

```text
奖励点数五十 → 50 điểm thưởng
三点奖励点数 → 3 điểm thưởng
五千点奖励点数 → 5.000 điểm thưởng
一个c级支线剧情 → một tình tiết nhánh cấp C
天道眷属值 → điểm thân thuộc Thiên Đạo / trị số quyến thuộc Thiên Đạo
每次召唤十点奖励点数 → mỗi lần triệu hoán tốn 10 điểm thưởng
```

### Rule

Resource unit có thể đứng trước hoặc sau số:

```python
patterns = [
  RESOURCE + NUM,
  NUM + RESOURCE,
  NUM + 点 + RESOURCE,
  一个 + GRADE + 支线剧情,
]
```

---

## 5.10. Date/time clock

### Pattern

```text
2019年5月29日
中午12点左右
3点左右
6点左右
每天三更
二十一世纪
```

### Transfer

```text
2019年5月29日 → ngày 29 tháng 5 năm 2019
中午12点左右 → khoảng 12 giờ trưa
3点左右 → khoảng 3 giờ
每天三更 → mỗi ngày ba canh / mỗi ngày ba lượt cập nhật, tùy context
二十一世纪 → thế kỷ 21
```

### Special

`三更` trong author note có thể là “ba chương/cập nhật”, không phải canh ba. Nếu nằm trong đoạn `ps/求订阅/更新`, tag là `AUTHOR_NOTE`, có thể bỏ qua hoặc dịch theo văn cảnh.

---

## 5.11. Power index / numeric stat

### Pattern

```text
1实力
20-50之间
200-300左右
解析度百分之三十七
危险度
```

### Transfer

```text
1实力 → chỉ số thực lực 1
20-50之间 → trong khoảng 20-50
解析度百分之三十七 → độ phân tích khoảng 37%
```

### Module

```text
PowerStatParser
```

Detect số ngay trước/sau:

```text
实力, 解析度, 危险度, 权限, 等级, 数值, 指数
```

---

## 6. NominalChainParser — danh ngữ dài không có `的`

### 6.1. Vấn đề

Corpus có nhiều chuỗi danh từ/danh ngữ dài:

```text
洪荒天庭政府
最初主神空间
天道眷属值来源
血红玫瑰冒险团
幽冥地府血海阵
掌中位面
先天一气
中央戊土厚德诀
```

Nếu tokenizer chỉ tách bằng Trie, vẫn cần phân loại quan hệ nội bộ để dịch đúng trật tự.

### 6.2. Suffix-role map

```json
{
  "政府": "organization",
  "空间": "domain/system/place",
  "值": "metric",
  "来源": "source",
  "冒险团": "organization",
  "阵": "formation",
  "位面": "plane/domain",
  "诀": "cultivation_method",
  "功": "method",
  "法": "method/law",
  "锁": "system_level",
  "权限": "permission",
  "剧情": "game_resource",
  "点数": "game_resource"
}
```

### 6.3. Transfer rule

```text
Modifier + Head
→ Head của Modifier
```

Examples:

```text
洪荒天庭政府 → Chính phủ Thiên Đình Hồng Hoang
最初主神空间 → Không gian Chủ Thần ban đầu
天道眷属值来源 → nguồn điểm quyến thuộc Thiên Đạo
血红玫瑰冒险团 → đoàn mạo hiểm Huyết Hồng Mân Côi
中央戊土厚德诀 → Trung Ương Mậu Thổ Hậu Đức Quyết
```

### 6.4. Entity protection

Nếu danh ngữ đã được glossary/entity memory xác nhận là tên riêng, không đảo tự động.

```python
if entity.type in {ORG, TECHNIQUE, ITEM, FORMATION, DOMAIN}:
    use_entity_translation()
else:
    apply_nominal_chain_transfer()
```

---

## 7. SystemTermProtector — thuật ngữ hệ thống/game/vô hạn lưu

### 7.1. Terms cần bảo vệ trong 100 chương đầu

```text
主神空间
最初主神空间
轮回小队
奖励点数
支线剧情
天道眷属值
初级权限
第一权限者
兑换
召唤项
位面之子
基因锁
五阶基因锁
圣人
正统修真
符文解析
中央戊土厚德诀
水运诀
上清诛仙功残篇
血红玫瑰冒险团
幽冥地府血海阵
```

### 7.2. Rule

```python
class SystemTermProtector:
    def protect(tokens):
        # longest-match first
        # mark as protected span
        # prevent number splitting inside terms
```

### 7.3. Number inside protected terms

```text
第六感 → giác quan thứ sáu, lexical idiom
五阶基因锁 → khóa gen bậc năm, structured term
第一权限者 → quyền hạn giả số một / người có quyền hạn số một
一阶与冒险 → bậc một và mạo hiểm, title/context
```

---

## 8. ClauseGraphTransfer — xử lý câu dài

### 8.1. Vấn đề

Câu trong corpus thường dài, nhiều marker lồng nhau:

```text
虽然 A，但是 B，而且 C，所以 D
若是 A，那么 B，而 C 又 D
```

Rule tuyến tính sẽ dễ loạn thứ tự.

### 8.2. Giải pháp

Tạo graph mệnh đề nhẹ:

```python
@dataclass(slots=True)
class ClauseNode:
    id: int
    span: tuple[int, int]
    text: str
    relation_to_parent: str
    markers: list[str]
    children: list[int]
```

### 8.3. Split priority

```text
1. quote boundaries: “...”
2. sentence punctuation: 。！？；
3. strong comma with markers: 虽然/但是/若是/所以/而/却
4. enumerative comma: 、
5. parenthetical author note: （...）
```

### 8.4. Transfer

```text
Render each ClauseNode recursively:
condition before main
concession before main
cause before effect
contrast preserves “nhưng/mà”
```

---

## 9. Dialogue/SystemPrompt handling

### 9.1. Corpus patterns

```text
“击杀风行魔狼，获得奖励点数五十...”
“三十秒内进入光柱...”
（ps：中午12点左右一更...）
```

### 9.2. Rule

```python
if paragraph starts with system style quote or contains 奖励点数/支线剧情/传送/锁定:
    register = "system"
    output should be concise, mechanical
```

### 9.3. Author note

Parentheses with `ps`, `求订阅`, `求月票`:

```text
mark AUTHOR_NOTE
optional skip in novel translation mode
or translate in metadata mode
```

---

## 10. Bổ sung tests từ 100 chương đầu

### 10.1. Test logic condition/concession

```python
def test_zhiyao_jiu():
    assert transfer("只要出现过的就会全部摆放出来") == \
        "Chỉ cần từng xuất hiện thì sẽ được bày ra toàn bộ"

def test_chufei_fouze():
    assert transfer("除非是拥有文字文明传承的人类部落，否则我无法得知这些信息") == \
        "Trừ khi là bộ lạc nhân loại có chữ viết và truyền thừa văn minh, nếu không thì ta không thể biết được những thông tin này"

def test_suiran_danshi():
    assert transfer("虽然有工作，但是工作的目的正是为了不工作") == \
        "Tuy có công việc, nhưng mục đích làm việc chính là để không phải làm việc"
```

### 10.2. Test temporal

```python
def test_sanshi_miao_nei():
    assert transfer("三十秒内进入光柱") == "Tiến vào cột sáng trong vòng 30 giây"

def test_zhidao_cai():
    assert transfer("直到天色微红时，他才回过神来") == \
        "Mãi đến khi sắc trời hơi đỏ, hắn mới hoàn hồn"
```

### 10.3. Test number/game resources

```python
def test_reward_points_postposed():
    assert transfer("获得奖励点数五十") == "nhận được 50 điểm thưởng"

def test_reward_points_preposed():
    assert transfer("三点奖励点数") == "3 điểm thưởng"

def test_branch_plot():
    assert transfer("一个c级支线剧情") == "một tình tiết nhánh cấp C"

def test_percent_decimal_ji():
    assert transfer("百分之九十八点几") in {
        "hơn 98%", "khoảng 98 phẩy mấy phần trăm"
    }
```

### 10.4. Test nominal chain

```python
def test_nominal_chain_main_god_space():
    assert transfer("最初主神空间") == "Không gian Chủ Thần ban đầu"

def test_nominal_chain_reward_source():
    assert transfer("天道眷属值来源") == "nguồn điểm quyến thuộc Thiên Đạo"

def test_nominal_chain_adventure_group():
    assert transfer("血红玫瑰冒险团") == "đoàn mạo hiểm Huyết Hồng Mân Côi"
```

---

## 11. Data files cần bổ sung

### 11.1. `data/grammar/logic_patterns.json`

```json
{
  "condition": {
    "if": ["若是", "如果", "倘若", "若"],
    "sufficient": [["只要", "就"], ["只要", "便"]],
    "necessary": [["只有", "才"]],
    "unless": [["除非", "否则"]],
    "once": [["一旦", "就"], ["一旦", "便"]]
  },
  "concession": {
    "although": [["虽然", "但是"], ["虽然", "却"], ["虽然", "但"]],
    "even_if": [["即便", "也"], ["即使", "也"], ["哪怕", "都"]]
  },
  "contrast": {
    "not_but": [["不是", "而是"]],
    "not_only": [["不但", "而且"], ["不仅", "还"], ["不仅", "也"]]
  },
  "temporal": {
    "until": [["直到", "才"]],
    "immediate": [["刚", "就"], ["刚一", "就"], ["一", "就"]],
    "sequence": [["先", "再"], ["先", "然后"]]
  },
  "emphasis": {
    "even": [["连", "都"], ["连", "也"]],
    "more_more": [["越", "越"]]
  }
}
```

### 11.2. `data/grammar/number_semantic_patterns.json`

```json
{
  "time_units": ["秒", "分钟", "小时", "个小时", "天", "日", "月", "年", "世纪", "刻"],
  "deadline_suffixes": ["内", "之内", "以内"],
  "relative_suffixes": ["前", "之前", "后", "之后"],
  "approx_markers": ["约", "约莫", "大约", "差不多", "左右", "上下", "至少", "最多", "近", "将近", "超过", "不足", "数以"],
  "range_markers": ["到", "至", "-", "—", "~"],
  "resource_terms": ["奖励点数", "支线剧情", "天道眷属值", "因果点"],
  "stat_terms": ["实力", "解析度", "危险度", "权限", "等级", "数值", "指数"],
  "level_suffixes": ["级", "阶", "层", "代"]
}
```

### 11.3. `data/grammar/system_terms.json`

```json
{
  "game_system": [
    "主神空间", "最初主神空间", "轮回小队", "奖励点数", "支线剧情",
    "天道眷属值", "初级权限", "第一权限者", "兑换", "召唤项"
  ],
  "cultivation": [
    "基因锁", "五阶基因锁", "圣人", "正统修真", "符文解析",
    "水运诀", "中央戊土厚德诀", "上清诛仙功残篇"
  ],
  "organizations": [
    "真实历史", "洪荒天庭政府", "血红玫瑰冒险团"
  ],
  "formations": [
    "幽冥地府血海阵"
  ]
}
```

---

## 12. Implementation roadmap v9

## Sprint V9.1 — Corpus Pattern Detector

```text
V9.1a  Implement logic_patterns.json
V9.1b  Implement LogicRelationDetector
V9.1c  Add pair-marker matching with nesting-safe spans
V9.1d  Add tests for condition/concession/contrast/temporal/emphasis
```

Acceptance:

```text
Detect ≥90% pair patterns in 100-chapter sample without crashing.
```

---

## Sprint V9.2 — Number Semantic Classifier

```text
V9.2a  Implement number_semantic_patterns.json
V9.2b  Add NumberSemanticClassifier before NumberConverter
V9.2c  Classify duration/deadline/range/approx/percent/fraction/level/game-resource
V9.2d  Protect system terms containing number/grade
V9.2e  Add tests from first 100 chapters
```

Acceptance:

```text
三十秒内 → trong vòng 30 giây
五千点奖励点数 → 5.000 điểm thưởng
一个c级支线剧情 → một tình tiết nhánh cấp C
百分之九十八点几 → hơn 98% / khoảng 98 phẩy mấy phần trăm
五阶基因锁 → khóa gen bậc năm
```

---

## Sprint V9.3 — Nominal Chain + System Term Protection

```text
V9.3a  Implement system_terms.json
V9.3b  Implement SystemTermProtector longest-match
V9.3c  Implement NominalChainParser suffix-role
V9.3d  Add protected span behavior to tokenizer/transfer engine
```

Acceptance:

```text
最初主神空间 protected
天道眷属值 protected/translated as term
血红玫瑰冒险团 recognized as organization
中央戊土厚德诀 recognized as cultivation method
```

---

## Sprint V9.4 — Complement and Formal Passive

```text
V9.4a  Implement rule_de_complement.py
V9.4b  Implement rule_formal_passive.py for 由/为...所
V9.4c  Extend BEI passive with formal variants
V9.4d  Add tests for 少得可怜, 大得出奇, 为...所困, 由...所取代
```

---

## Sprint V9.5 — Clause Graph Transfer for long sentences

```text
V9.5a  Implement clause_graph.py
V9.5b  Split long sentences into clause nodes
V9.5c  Render logic relations with Vietnamese connectors
V9.5d  Add diff reporter for first 100-chapter sample
```

Acceptance:

```text
No crash on 100 chapters.
Long-sentence output improves without breaking existing short sentence tests.
```

---

## 13. Priority matrix

| Priority | Module/rule | Reason |
|---|---|---|
| P0 | `NumberSemanticClassifier` | corpus cực nhiều số game/cấp/thời gian |
| P0 | `LogicRelationDetector` | câu dài phụ thuộc marker đôi |
| P0 | `rule_de_complement` | `得` xuất hiện dày đặc |
| P0 | `rule_emphasis_even` | `连...都/也` rất nhiều |
| P0 | `rule_formal_passive` | `由/为...所` thường xuyên |
| P0 | `SystemTermProtector` | tránh phá thuật ngữ/vật phẩm/hệ thống |
| P1 | `NominalChainParser` | cải thiện danh ngữ dài |
| P1 | `ClauseGraphTransfer` | cần cho câu dài nhưng làm sau detector |
| P1 | `rule_definition_naming` | nhiều thuật ngữ định nghĩa |
| P2 | author-note handler | không ảnh hưởng nội dung chính |

---

## 14. Definition of Done v9

```text
1. Đọc được 100 chương đầu, không crash.
2. Tất cả 98 tests cũ vẫn pass khi feature flag off.
3. Grammar transfer flag on:
   - logic detector tests pass
   - number semantic tests pass
   - nominal chain tests pass
   - first-100 smoke test pass
4. Có báo cáo coverage pattern theo nhóm:
   - condition
   - concession
   - contrast
   - temporal
   - cause-result
   - emphasis
   - number semantic
5. Tạo được CSV/MD report top 100 câu còn lỗi để tiếp tục calibration.
```

---

## 15. Lưu ý tích hợp với repo hiện tại

1. Không thay thế `NumberConverter` hiện có ngay. Thêm `NumberSemanticClassifier` phía trước để gắn nhãn context, rồi gọi converter cũ hoặc converter mở rộng.
2. Không để SurfaceRealizer dịch lại toàn bộ. Chỉ chèn token VI structural, phần lexical vẫn để RBMT loop xử lý.
3. Luôn dùng feature flag:

```python
enable_grammar_transfer_v9 = False
```

4. Khi flag off, output phải giữ nguyên.
5. Khi rule fail, fallback về structural rewrite cũ hoặc lexical-only, không crash.

---

## 16. Checklist bổ sung vào kế hoạch tổng

```text
[ ] V9.1 LogicRelationDetector
[ ] V9.2 ClauseGraph data structure
[ ] V9.3 Condition rules: 若是/如果/只要/只有/一旦/除非
[ ] V9.4 Concession rules: 虽然/即便/哪怕
[ ] V9.5 Contrast rules: 不是...而是/并非/不仅
[ ] V9.6 Temporal rules: 直到...才/一...就/先...再
[ ] V9.7 Cause-result rules: 因为/导致/使得/从而
[ ] V9.8 Emphasis rules: 连...都/越...越
[ ] V9.9 Method/purpose/topic-prep rules: 通过/为了/对于/随着
[ ] V9.10 Formal passive: 由/为...所
[ ] V9.11 `将` disposal vs future disambiguation
[ ] V9.12 `得` complement classifier
[ ] V9.13 Definition/naming: 所谓/名为/称为/叫做
[ ] V9.14 Scope/range: 之一/之中/之内/以上/以下
[ ] V9.15 NumberSemanticClassifier
[ ] V9.16 Game/system number conversion
[ ] V9.17 NominalChainParser
[ ] V9.18 SystemTermProtector
[ ] V9.19 First-100-chapter smoke runner
[ ] V9.20 Pattern coverage report
```
