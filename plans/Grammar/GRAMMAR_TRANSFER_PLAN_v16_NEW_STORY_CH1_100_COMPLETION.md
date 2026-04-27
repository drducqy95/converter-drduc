# GRAMMAR_TRANSFER_PLAN_v16_NEW_STORY_CH1_100_COMPLETION

**Repo:** `converter-drduc`  
**Kế thừa:** `GRAMMAR_TRANSFER_PLAN_v14_MERGED_v12_v13_FULL.md` + `GRAMMAR_TRANSFER_PLAN_v15_DEEP_COMPLETION`  
**Corpus mới:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi phân tích:** chương 1–100  
**Ngày:** 2026-04-25  
**Phiên bản:** v16.0 — System/Sci-fi/Game-Corpus Grammar Completion  

---

## 0. Executive Summary

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

## 1. Corpus Signals từ chương 1–100

### 1.1 Thống kê sơ bộ

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

## 2. Những GAP mới sau v15

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

# PART A — System Panel Parser

## A1. Vấn đề

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

## A2. Thuật toán `SystemPanelParser`

### A2.1 Data model

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

### A2.2 Các loại panel

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

### A2.3 Dịch preserving format

```text
【宿主:李宇】
→ 【Ký chủ: Lý Vũ】

【分身数量:1（投放中）】
→ 【Số lượng phân thân: 1 (đang thả xuống)】

【分身冷却中，24小时后可再次进行投放…】
→ 【Phân thân đang hồi chiêu, sau 24 giờ có thể thả xuống lần nữa...】
```

### A2.4 Rule

```python
if span.startswith("【") and span.endswith("】"):
    protect_as_system_panel(span)
    parse_inner_with_panel_rules()
    do_not_apply_general_de_inversion_or_ba_rules()
```

---

# PART B — System Reward/Event Grammar

## B1. `获得 X-名称:说明`

```text
【获得白色称号【菊花守护者】:可佩戴称号，菊花不破于肥皂。】
```

**VI:**

```text
【Nhận được danh hiệu trắng [Người Bảo Vệ Hoa Cúc]: danh hiệu có thể đeo, hoa cúc không bị phá bởi xà phòng.】
```

### Rule

```python
Pattern: 获得 + [GRADE]? + [CATEGORY] + [-/–] + [NAME] + [:] + DESC
Output: Nhận được + CATEGORY_vi + GRADE_vi + [NAME_vi/protected] + ": " + DESC_vi
```

### Mapping

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

## B2. `是否提取？`

```text
【获得特殊物品–超级士兵血清，是否提取？】
```

**VI:**

```text
【Nhận được vật phẩm đặc biệt – Huyết thanh Siêu Chiến Binh, có rút ra không?】
```

### Rule

```python
是否 + V → có V không?
是否提取 → có rút ra không?
是否佩戴 → có đeo không?
是否加载 → có tải vào không?
```

---

## B3. `冷却中 / 投放中 / 回收中 / 结算中`

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

# PART C — Cross-world Entity Detector

## C1. Entity pattern

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

## C2. Rule nhận diện

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

### C2.1 Protected translation policy

| ZH | VI |
|---|---|
| `变形金刚世界` | thế giới Transformers |
| `生化危机世界` | thế giới Resident Evil |
| `黑客帝国世界` | thế giới The Matrix |
| `漫威世界` | thế giới Marvel |
| `保护伞公司` | Công ty Umbrella / Tập đoàn Umbrella |
| `T病毒` | virus T |
| `G病毒` | virus G |

## C3. Không number-convert / split inside franchise entity

```text
G病毒稳定强化药剂
→ Dược tề cường hóa ổn định virus G
```

Không tách `G` như grade.

---

# PART D — GradeRankConverter

## D1. Vấn đề

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

## D2. Grade grammar

```python
GRADE_RE = r"\b([SABCDEF])([+\-])?级?(别)?\b"
```

## D3. Mapping

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

## D4. Rule

```python
if token matches grade and next in ["级", "级别"]:
    protect_alphanumeric_grade()
    translate_as_rank()
```

## D5. Grade comparison

```text
比 X 高 N 个等级
→ cao hơn X N cấp

X 以下
→ từ X trở xuống / dưới X

X 之上
→ trên X
```

---

# PART E — TimeFlowRatioConverter

## E1. Pattern

```text
当前投放世界与主世界流速不一致，为1:2
矩阵世界与主世界比例为（1:10）
原本1:5的赔率被人拉到1:2了
```

## E2. Phân biệt ratio type

| Context | Meaning | VI |
|---|---|---|
| `流速/比例/主世界/世界` | time-flow ratio | tỷ lệ thời gian |
| `赔率` | betting odds | tỷ lệ cược |
| `兑换比例` | exchange rate | tỷ lệ quy đổi |
| `能量比例` | energy ratio | tỷ lệ năng lượng |

## E3. Rule

```python
if nearby(["流速", "主世界", "世界比例"]):
    "1:2" → "tỷ lệ 1:2"
elif nearby(["赔率"]):
    "1:2" → "tỷ lệ cược 1:2"
else:
    keep "1:2"
```

## E4. Translation examples

```text
当前投放世界与主世界流速不一致，为1:2
→ tốc độ thời gian giữa thế giới được thả xuống hiện tại và thế giới chính không đồng nhất, là 1:2

矩阵世界与主世界比例为（1:10）
→ tỷ lệ giữa thế giới Ma Trận và thế giới chính là (1:10)
```

---

# PART F — Currency / Resource Number Converter

## F1. Currency units

```python
CURRENCY_UNITS = {
    "星币": "tinh tệ",
    "信用点": "điểm tín dụng",
    "积分": "điểm",
    "奖励点": "điểm thưởng",
    "奖励点数": "điểm thưởng",
}
```

## F2. Number style policy

| Context | Output |
|---|---|
| small narrative | `hai nghìn tinh tệ` |
| large currency | `5.000 tinh tệ`, `30 tỷ tinh tệ` |
| system panel | preserve digits if source uses digits |
| xianxia/literary | can use `vạn`, `ức` if configured |

## F3. Examples

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

## F4. Resource/state numbers

```text
分身数量:1
→ số lượng phân thân: 1

生存时间7天
→ thời gian sinh tồn: 7 ngày

冷却时间六十小时
→ thời gian hồi chiêu: 60 giờ
```

---

# PART G — Tech Product Model Parser

## G1. Product model chain

```text
巨神运输3型飞船
百万吨级的运输船
D级磁能离子狙击枪
棱体能量护盾––蜉蝣型
逆闪单兵推进器
方舟精神转移与肉体重生系统
```

## G2. Pattern

```python
TECH_PRODUCT_PATTERN = [
    BRAND_OR_SERIES,
    FUNCTION_MODIFIER*,
    MODEL_NUMBER?,
    TYPE_SUFFIX
]
```

## G3. Suffix ontology

```python
TECH_SUFFIXES = [
    "飞船", "运输船", "狙击枪", "子弹", "护盾", "推进器",
    "系统", "装置", "药剂", "血清", "机器人", "摩托", "引擎",
    "外骨骼", "义肢", "芯片", "能量核心", "瞄镜", "枪匣"
]
```

## G4. Translation examples

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

## G5. Guard

Nếu product chain có:
- alphanumeric grade,
- model number,
- dash,
- bracketed name,

thì protect toàn span trước grammar inversion.

---

# PART H — Weapon / Ammo Format

## H1. Patterns

```text
D级磁能离子狙击枪–20发子弹
三枚赤色的子弹
一发集束光线
枪匣很长，里面只有二十发子弹
```

## H2. Unit map

| ZH unit | VI |
|---|---|
| `发` | phát / viên đạn / luồng bắn |
| `枚` | viên / quả / cái |
| `柄` | thanh / khẩu |
| `把` | khẩu / thanh / cái |
| `颗` | viên |
| `道` | luồng / vệt |
| `束` | chùm / tia |

## H3. Context classifier

```python
if unit == "发" and head in ["子弹", "炮弹"]:
    "20发子弹" → "20 viên đạn"
elif unit == "发" and head in ["光线", "攻击"]:
    "一发集束光线" → "một phát tia hội tụ"
```

---

# PART I — Passive/Result Passive mở rộng

## I1. Pattern `被当做 / 被视为 / 被改造成`

```text
被当做偷渡客
→ bị coi là kẻ nhập cư lậu

被改造成暴君
→ bị cải tạo thành Tyrant

被视为大号电池
→ bị xem là cục pin cỡ lớn
```

## I2. Rule

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

## I3. Distinguish passive vs lexical compound

```text
被感染者
→ Người bị nhiễm / Kẻ bị nhiễm
```

Nếu `被感染者` là system title/item, protect as item name.

---

# PART J — Simulator State Machine Terms

## J1. Glossary

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

## J2. Event grammar

```text
分身已死亡，回收中，生存时间7天…奖励结算中…
→ Phân thân đã tử vong, đang thu hồi, thời gian sinh tồn 7 ngày... đang kết toán phần thưởng...
```

---

# PART K — Colloquial / Internet Slang / Tone

## K1. Slang map

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

## K2. Tone particles mở rộng

| ZH | VI |
|---|---|
| `吧` | nhỉ / đi / chứ |
| `吗` | không / à |
| `呢` | đây / nhỉ / thì sao |
| `啊` | à / đó / cảm thán |
| `呦` | đó nha / cơ đấy |
| `嘛` | mà |
| `呃` | ờm / ặc |

## K3. Rule

Nếu câu là thoại và có slang:
- giữ sắc thái khẩu ngữ,
- không nâng lên văn phong cổ/xianxia,
- ưu tiên dịch tự nhiên hơn literal.

---

# PART L — Onomatopoeia and SFX Preserver

## L1. Frequent SFX

```text
嗡！
啪嗒！
轰隆隆！
嘭！！
砰，砰，砰，砰！
哗啦啦
飒！
```

## L2. Translation policy

| ZH | VI |
|---|---|
| `嗡` | vù / ong ong |
| `啪嗒` | cạch / bộp |
| `轰隆隆` | ầm ầm / ùng ùng |
| `嘭` | bùm / phịch |
| `砰` | đoàng / bang |
| `哗啦啦` | loảng xoảng / rào rào |
| `飒` | vút |

## L3. Rule

```python
if sentence_is_sfx_only():
    translate_sfx_or_preserve()
    skip grammar transfer
```

---

# PART M — Scientific / Physical Measurement

## M1. Patterns

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

## M2. Rule

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

## M3. Approximation triggers

```python
APPROX_TRIGGERS = ["足有", "不足", "不到", "至少", "仅仅", "只有", "近", "近乎", "大约", "左右", "上下", "十几", "几十", "数十"]
```

---

# PART N — Author Note / Meta Text Filter

## N1. Corpus có author note

```text
（新人新书，求求各位大佬的关照了，来者不拒…每天都看看呗，毕竟…追读什么的…）
（新人新书，呜呜呜…求票票，求收藏…）
```

## N2. Rule

```python
if paragraph.startswith("（") and contains(["求票", "求收藏", "求订阅", "新人新书", "月票"]):
    mark_as_author_note
```

## N3. Config

```python
translation_config = {
    "translate_author_notes": False,
    "preserve_author_notes": True,
    "author_note_prefix": "Ghi chú tác giả:"
}
```

---

# PART O — Nickname / Title Entity Recognition

## O1. Nickname patterns

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

## O2. Rule

```python
if short span appears repeatedly and used as subject/vocative:
    classify as CHARACTER_ALIAS
```

## O3. Title + name

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

## O4. Alias memory

```python
EntityMemory.add_alias("库尔", "双刀库尔")
EntityMemory.add_alias("三胖子", "三先生")
```

---

# PART P — `算是 / 也算 / 可算是 / 只能算`

## P1. Pattern

```text
也算小有名气
这算是一个小福利
已经算是好手了
只能算是普通
```

## P2. VI mapping

| ZH | VI |
|---|---|
| `算是` | xem như / coi như là |
| `也算` | cũng xem như |
| `可算是` | cũng có thể xem là |
| `只能算` | chỉ có thể xem là |

## P3. Rule

```python
算是 + NP/ADJ → xem như là + NP/ADJ
```

---

# PART Q — `就这么 / 就这样 / 就这么死了`

## Q1. Pattern

```text
就这么死了
就这样对待
就这么挂了
```

## Q2. VI

```text
cứ thế mà chết
đối xử như vậy
cứ thế mà toi
```

## Q3. Rule

```python
就这么/就这样 + V
→ cứ thế/cứ như vậy mà + V
```

---

# PART R — Rhetorical Dialogue Forms

## R1. Examples

```text
你知不知道...？
这就算还人情了？
这么牵强的吗？
怎么可能？
何必在这个破地方待着？
岂不是太可惜了？
```

## R2. Rule

| Pattern | VI |
|---|---|
| `你知不知道...` | ngươi có biết... không |
| `这就算...了？` | thế này mà cũng tính là...? |
| `这么...的吗？` | ... thế này sao? |
| `怎么可能` | sao có thể |
| `何必...` | cần gì phải |
| `岂不是...` | chẳng phải là ... sao |

---

# PART S — `迫不及待 / 忍不住 / 舍不得 / 懒得`

## S1. Lexicalized modal/emotion guards

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

## S2. Rule

Treat these as single adverbial/modal units, not normal negation + complement.

---

# PART T — Multi-layer `作为`

## T1. Pattern

```text
作为一名穿越客，这是他赖以生存的本钱
作为一名黑户，在纽约市，您成功被抓了起来
作为目前掌握了子弹时间的你...
```

## T2. Rule

```text
作为 + NP
→ với tư cách là + NP
→ là một + NP, ...
```

## T3. Context

If `作为` begins sentence:
- VI usually fronted: `Với tư cách là...`
If inside system log:
- preserve concise: `Là...`

---

# PART U — Implementation Roadmap v16

## Sprint V16-A — System Panel + Protected Format

- [ ] `system_panel_parser.py`
- [ ] `system_panel_patterns.json`
- [ ] bracket/nested bracket parser
- [ ] preserve `【...】`
- [ ] parse `key:value`, `item-name:desc`, `note`
- [ ] 80 tests

## Sprint V16-B — Sci-fi/Game Entity

- [ ] `cross_world_entity_detector.py`
- [ ] `sci_fi_entity_suffix_ontology.json`
- [ ] franchise glossary: Transformers/Resident Evil/Matrix/Marvel/Umbrella/S.H.I.E.L.D.
- [ ] tech product chain parser
- [ ] alphanumeric entity guard
- [ ] 100 tests

## Sprint V16-C — Grade/Number/Resource

- [ ] `grade_rank_converter.py`
- [ ] `time_flow_ratio_converter.py`
- [ ] `currency_resource_converter.py`
- [ ] `ammo_measure_converter.py`
- [ ] `approx_measure_converter.py`
- [ ] 120 tests

## Sprint V16-D — Colloquial/SFX/Dialogue

- [ ] `slang_tone_map.json`
- [ ] `onomatopoeia_map.json`
- [ ] rhetorical dialogue rule
- [ ] sentence-final particle tone expansion
- [ ] author-note filter
- [ ] 80 tests

## Sprint V16-E — Passive/Result + Simulator Verbs

- [ ] `rule_passive_result.py`
- [ ] `simulator_state_glossary.json`
- [ ] `rule_system_reward.py`
- [ ] `rule_zuowei_frame.py`
- [ ] `rule_suanshi_classification.py`
- [ ] 100 tests

---

# PART V — Test Matrix v16

## V1. System panel

```python
V16_SYSTEM_TESTS = [
    ("【宿主:李宇】", "【Ký chủ: Lý Vũ】"),
    ("【分身数量:1（投放中）】", "【Số lượng phân thân: 1 (đang thả xuống)】"),
    ("【分身冷却中，24小时后可再次进行投放…】",
     "【Phân thân đang hồi chiêu, sau 24 giờ có thể thả xuống lần nữa...】"),
]
```

## V2. Grade/rank

```python
V16_GRADE_TESTS = [
    ("D级磁能离子狙击枪", "súng bắn tỉa ion từ năng cấp D"),
    ("E+级以下的攻击", "công kích từ cấp E+ trở xuống"),
    ("比F-高了两个等级", "cao hơn F- hai cấp"),
]
```

## V3. Time-flow ratio

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

## V4. Currency/resource

```python
V16_CURRENCY_TESTS = [
    ("5000星币", "5.000 tinh tệ"),
    ("三十亿星币", "30 tỷ tinh tệ"),
    ("十万星币", "100.000 tinh tệ"),
]
```

## V5. Passive result

```python
V16_PASSIVE_RESULT_TESTS = [
    ("被当做偷渡客", "bị coi là kẻ nhập cư lậu"),
    ("被改造成暴君", "bị cải tạo thành Tyrant"),
    ("被视为大号电池", "bị xem là cục pin cỡ lớn"),
]
```

## V6. Tech product

```python
V16_TECH_TESTS = [
    ("巨神运输3型飞船", "phi thuyền vận tải loại 3 Cự Thần"),
    ("百万吨级的运输船", "tàu vận tải cấp triệu tấn"),
    ("D级磁能离子狙击枪–20发子弹", "súng bắn tỉa ion từ năng cấp D – 20 viên đạn"),
]
```

## V7. Colloquial/rhetorical

```python
V16_DIALOGUE_TESTS = [
    ("这就算还人情了？", "thế này mà cũng tính là trả nhân tình rồi sao?"),
    ("怎么可能！", "sao có thể!"),
    ("岂不是太可惜了", "chẳng phải là quá đáng tiếc sao"),
    ("可还行", "thế mà cũng được à"),
]
```

## V8. SFX

```python
V16_SFX_TESTS = [
    ("嗡！", "Vù!"),
    ("啪嗒！", "Cạch!"),
    ("轰隆隆！", "Ầm ầm!"),
    ("砰，砰，砰，砰！", "Đoàng, đoàng, đoàng, đoàng!"),
]
```

---

# PART W — Data Files cần bổ sung

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

# PART X — Acceptance Metrics v16

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

# PART Y — Merge Strategy với v15

## Y1. V16 không thay thế v15

v15 vẫn là nền deep grammar gap analysis. v16 là **domain extension** cho corpus mới.

## Y2. Rule priority cập nhật

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

## Y3. Vì sao SystemPanelParser phải chạy trước grammar rules

Nếu không:
- `【获得白色称号【菊花守护者】:...】` có nested bracket, dễ split sai.
- `D级` bị xử lý như chữ cái đơn.
- `24小时后` có thể bị time reorder sai.
- `是否提取？` có thể bị parse như normal `是否`.
- item name có thể bị number converter phá.

---

# PART Z — Definition of Done v16

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
