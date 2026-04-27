# GRAMMAR_TRANSFER_PLAN_v8 — Corpus-driven Deep Completion

**Repo:** `converter-drduc`  
**Mục tiêu:** Hoàn thiện Grammar Transfer ZH→VI dựa trên phân tích sâu corpus chương 1–20, đặc biệt chương 11–20 mới upload.  
**Trạng thái kế thừa:** v7 đã bổ sung entity-aware, number-aware, format-aware, corpus grammar patterns từ chương 1–10.  
**Bản này:** bổ sung các cấu trúc còn thiếu trong truyện vô hạn lưu / huyền huyễn / xuyên không / chiến đấu / hệ thống, đồng thời chuẩn hóa thêm số, cấp bậc, đo lường, thời gian, tỷ lệ, game-resource và cấu trúc mô tả thế giới.

---

## 0. Kết luận nhanh sau phân tích chương 11–20

Các chương 11–20 xuất hiện dày đặc các dạng mà kế hoạch cũ mới xử lý một phần:

1. **Chuỗi điều kiện - giả định - ngoại lệ dài:** `若是`, `只要`, `除非`, `若无`, `一旦`, `凡是`, `每当`, `不管...都`.
2. **Cấu trúc nhượng bộ và chuyển ý tầng lớp:** `虽然...但是`, `不过`, `只是`, `却`, `反倒`, `甚至`, `乃至`.
3. **Cấu trúc so sánh/tiệm tiến/định lượng:** `越...越`, `比...更`, `至少`, `差不多`, `约莫`, `左右`, `不下`, `接近`, `多一点`, `两三`, `七八`.
4. **Mô tả khả năng - bắt buộc - cấm đoán:** `必须`, `需得`, `只能够`, `不得不`, `不准`, `无法`, `没法`, `能不能`, `可不可以`.
5. **Cấu trúc nguyên nhân - kết quả phức:** `导致`, `使得`, `所以`, `因此`, `正因为如此`, `这才`, `从而`, `以至于`.
6. **Cấu trúc phương tiện / mục đích / vai trò:** `用...来`, `靠...来`, `以...来`, `作为`, `对...来说`, `对于`, `相比于`, `至于`, `按照`.
7. **Câu trình bày hệ thống, thông tin, quy tắc:** `主神处就有信息落到脑海中`, `不准彼此攻击，否则抹杀`, `兑换价格是不等的`.
8. **Danh ngữ dài không có 的:** `洪荒万族第九千七百一十一位低等地精族`, `m国第五代主战斗机所有资料`, `上清诛仙诀残篇`.
9. **Tên riêng / thuật ngữ hệ thống lai chữ - số - Latin:** `z国`, `m国`, `c级`, `a级`, `b级`, `2135年`, `1.2倍`, `1吨`, `1.5吨`.
10. **Số trong hệ thống vô hạn lưu:** `奖励点数`, `支线剧情`, `a/b/c级`, `一百倍`, `十倍`, `三到八倍不等`, `五次轮回之后`, `五十天`.
11. **Chiến đấu / hành động liên tiếp:** `举着...对向...`, `顶着...向前一步`, `一口咬在...`, `不停地搅拌拉扯`, `任凭...如何...都是...`.
12. **Thoại, nội tâm, tu từ, cảm thán:** `莫非`, `难道`, `怎么可能`, `这是什么`, `可真是`, `我了个去`, `呵呵`.

Bản v8 bổ sung một lớp **Deep Grammar Construction Pack** bên trên MVP shallow parser, không thay thế toàn bộ pipeline cũ.

---

## 1. Nguyên tắc thiết kế cập nhật

### 1.1 Không biến rule-based transfer thành full parser quá sớm

Các chương 11–20 cho thấy văn bản có câu rất dài, nhiều mệnh đề, nhiều dấu phẩy, nhiều câu thoại/nội tâm. Nếu cố dependency parse toàn câu ngay sẽ dễ sai lan truyền.

**Chiến lược mới:**

```text
sentence
→ segment clauses by punctuation/dialogue/system markers
→ shallow construction detection per clause
→ protected entity/number span
→ local transfer rules
→ cross-clause connector realization
→ existing RBMT lexical loop
→ VI grammar postprocess
```

### 1.2 Cấu trúc ưu tiên theo độ ổn định

```text
Tier 0: protected spans
  entity, number, unit, game-resource, quote, system term

Tier 1: high-precision constructions
  被/把/将, 的, 了/着/过, 比/越, 若是/只要/除非, 虽然/但是

Tier 2: clause connectors
  因为/所以, 不过/只是/然而, 因此/于是/从而, 正因为如此

Tier 3: style and idiom smoothing
  莫非/难道, 可真是, 我了个去, 呵呵, 罢了, 而已
```

### 1.3 Chuyển đổi phải giữ “trace”

Mỗi rule cần ghi trace:

```python
GrammarTrace(
    rule="R_COND_RUOSHI",
    src_span=(start, end),
    src_text="若是第三次召唤依然没有任何变化变动",
    vi_hint="nếu lần triệu hồi thứ ba vẫn không có thay đổi gì",
    confidence=0.86,
)
```

Trace dùng cho debug và accuracy report.

---

## 2. Bổ sung module mới

```text
src/grammar/
├── clause_segmenter.py              # tách câu dài thành clause an toàn
├── construction_registry.py         # đăng ký rule theo priority/confidence
├── protected_span.py                # entity/number/system span guard
├── discourse_connector.py           # liên từ, nhượng bộ, nguyên nhân-kết quả
├── modality_transfer.py             # phải/có thể/không thể/được phép/cấm
├── comparative_transfer.py          # 比, 越...越, càng...càng
├── conditional_transfer.py          # 若是/只要/除非/一旦/凡是/每当
├── rhetoric_transfer.py             # 难道/莫非/怎么可能/何必
├── nominal_chain_transfer.py        # danh ngữ dài không 的
├── action_chain_transfer.py         # chuỗi hành động chiến đấu
├── system_prompt_transfer.py        # rule cho 主神/兑换/抹杀/thông báo hệ thống
└── number/
    ├── number_context_classifier.py # phân loại số theo ngữ cảnh
    ├── range_approx_converter.py    # 七八, 两三, 十几, 数百, 不下
    ├── rank_level_converter.py      # 第九千..., a级/c级, 一阶, 二十一世纪
    ├── measurement_converter.py     # 米/千米/吨/倍/点数
    ├── time_duration_converter.py   # 秒/分钟/小时/天/年/五十天后
    └── game_resource_converter.py   # 奖励点数/支线剧情/兑换倍率
```

---

## 3. Clause Segmenter cho câu dài

### 3.1 Lý do

Nhiều câu trong corpus có 5–10 mệnh đề liên tiếp, ví dụ dạng:

```text
虽然 A，但是 B，而且 C，若是 D，就 E，所以 F。
```

Nếu xử lý bằng một rule duy nhất sẽ sai thứ tự tiếng Việt. Cần tách clause nhưng không phá quote/entity.

### 3.2 Thuật toán

```python
class ClauseSegmenter:
    HARD_PUNCT = "。！？；"
    SOFT_PUNCT = "，、："
    QUOTE_OPEN = "“‘《「『（("
    QUOTE_CLOSE = "”’》」』）)"

    def segment(self, text: str) -> list[Clause]:
        # 1. Bảo vệ quote/system bracket
        # 2. Tách hard punctuation
        # 3. Trong mỗi sentence, tách soft punctuation nếu gặp connector boundary
        # 4. Không tách trong entity span, number-unit span, title bracket
        # 5. Gắn role: narration / dialogue / inner_thought / system_prompt
```

### 3.3 Boundary markers cần nhận diện

```json
{
  "conditional_start": ["若是", "如果", "只要", "一旦", "除非", "凡是", "每当"],
  "contrast_start": ["但是", "不过", "只是", "然而", "可", "却"],
  "cause_start": ["因为", "由于", "正因为如此"],
  "result_start": ["所以", "因此", "于是", "从而", "这才", "以至于"],
  "temporal_start": ["待到", "直到", "随后", "接着", "然后", "与此同时"],
  "quote_verbs": ["说道", "喊道", "吼道", "嘀咕", "喃喃", "念叨", "冷笑道"]
}
```

---

## 4. Conditional Transfer Pack

### 4.1 `若是 / 如果 / 要是 ... 就 ...`

```text
ZH: 若是第三次召唤依然没有任何变化变动，这三人就会开始疑惑迟疑
VI: Nếu lần triệu hồi thứ ba vẫn không có thay đổi gì, ba người này sẽ bắt đầu nghi hoặc do dự
```

Rule:

```python
if clause startswith [若是|如果|要是]:
    insert "Nếu " before condition
    if following clause has 就/便/则:
        remove 就/便/则 or render as "thì" only when needed
```

### 4.2 `只要 ... 就/便 ...`

```text
ZH: 只要能够度过试炼空间，轮回小队成员自然是开始变强
VI: Chỉ cần vượt qua không gian thử luyện, thành viên tiểu đội luân hồi tự nhiên sẽ bắt đầu mạnh lên
```

Rule:

```text
只要 A, B → Chỉ cần A, B
只要 A 就 B → Chỉ cần A thì B
```

### 4.3 `除非 ... 不然/否则 ...`

```text
ZH: 除非是已经无法动弹了，不然人人是兵
VI: Trừ phi đã không thể cử động, nếu không thì ai ai cũng là binh lính
```

Rule:

```text
除非 A，不然/否则 B → Trừ phi A, nếu không thì B
```

### 4.4 `一旦 ... 就 ...`

```text
ZH: 一旦天王大军渡江，汉人衣冠就此绝矣
VI: Một khi đại quân Thiên Vương vượt sông, y quan Hán nhân sẽ tuyệt diệt từ đây
```

Rule:

```text
一旦 A, B → Một khi A, B
一旦 A 就 B → Một khi A thì B
```

### 4.5 `凡是 ... 都 ...`

```text
ZH: 凡是能够进入这里的都是人类
VI: Phàm là người có thể tiến vào nơi này đều là nhân loại
```

Rule:

```text
凡是 A 都 B → Phàm là A đều B
```

### 4.6 `每当 / 每次 / 每开启`

```text
ZH: 每当他有气感吸纳天地游离能量时，奖励点数就会减少
VI: Mỗi khi hắn có khí cảm hấp thu năng lượng du ly trong trời đất, điểm thưởng sẽ giảm
```

Rule:

```text
每当 A 时, B → Mỗi khi A, B
每次 A 后, B → Mỗi lần sau khi A, B
每 + V + NUM/CLS 都需要 ... → Mỗi lần V ... đều cần ...
```

---

## 5. Concession / Contrast Transfer Pack

### 5.1 `虽然 ... 但是/但/不过 ...`

```text
ZH: 虽然极为微弱，但是至少可以让他反应敏锐超过常人
VI: Tuy cực kỳ yếu ớt, nhưng ít nhất có thể khiến phản ứng của hắn nhạy bén hơn người thường
```

Rule:

```text
虽然 A，但是 B → Tuy A, nhưng B
虽然 A，但 B → Tuy A, nhưng B
虽然 A，B → Tuy A, B
```

### 5.2 `只是 / 不过 / 然而 / 可 / 却`

```text
只是 → chỉ là / nhưng
不过 → có điều / nhưng / tuy nhiên
然而 → thế nhưng / tuy nhiên
却 → lại / nhưng lại
反倒 / 反而 → ngược lại / trái lại
```

Selection heuristic:

```python
if marker == "却" and clause polarity contrasts previous:
    vi = "nhưng lại"
elif marker in ["反倒", "反而"]:
    vi = "ngược lại"
elif marker == "只是" and starts clause:
    vi = "chỉ là"
else:
    vi = "nhưng"
```

### 5.3 `即便/即使/哪怕/那怕/纵然 ... 也 ...`

```text
ZH: 哪怕使用都要偷偷摸摸
VI: Dù có sử dụng cũng phải lén lút
```

Rule:

```text
哪怕 A 也 B → Dù A cũng B
即便 A 也 B → Cho dù A cũng B
纵然 A 也 B → Dẫu A cũng B
```

---

## 6. Comparative / Degree Transfer Pack

### 6.1 `越 ... 越 ...`

```text
ZH: 吸纳越多的游离能量形成真力，奖励点数减少得就越多
VI: Hấp thu càng nhiều năng lượng du ly để hình thành chân lực, điểm thưởng giảm càng nhiều
```

```text
ZH: 越早开启试炼空间，对他未来成长的潜力就越大
VI: Càng mở không gian thử luyện sớm, tiềm lực trưởng thành tương lai của hắn càng lớn
```

Rule:

```python
pattern: 越 A 越 B
output: càng A càng B

pattern: NP 越 A, NP2 就越 B
output: NP càng A, NP2 càng B
```

### 6.2 `比 ... 更/更加/还要 ...`

```text
ZH: 比当初那头巨狼更加厉害
VI: còn lợi hại hơn con sói khổng lồ lúc trước
```

Rule:

```text
X 比 Y 更 A → X A hơn Y
比 Y 更 A → A hơn Y
还要 A → còn A hơn
```

### 6.3 `得` degree complement

Corpus patterns:

```text
减少得越多
疼得要命
烧得焦黑
震慑得说不出话来
```

Rule:

```text
V 得 ADJ/COMP → V đến mức ADJ/COMP
V 得 + result adjective → V đến ADJ
ADJ 得 + complement → ADJ đến mức complement
```

Examples:

```text
疼得要命 → đau muốn chết
烧得焦黑 → cháy đến đen sì
震慑得说不出话来 → bị chấn nhiếp đến không nói nên lời
```

### 6.4 `有/没有 + degree + ADJ`

```text
没有太多信息 → không có quá nhiều thông tin
有些发毛 → hơi sởn gai ốc
有些忌惮 → hơi kiêng dè
```

Rule:

```text
有些 + ADJ/Vpsych → hơi / có chút
没有太多 + N → không có nhiều N lắm
```

---

## 7. Necessity / Permission / Ability Pack

### 7.1 Bắt buộc

```text
必须 → nhất định phải / bắt buộc phải
需得 → cần phải / phải
非得要 ... 不可 → nhất định phải ... mới được
不得不 → không thể không / đành phải
```

Examples:

```text
我必须凑齐至少一千奖励点数
→ ta nhất định phải gom đủ ít nhất 1.000 điểm thưởng

非得要灭你祖宗十八代不可
→ nhất định phải diệt cả mười tám đời tổ tông của ngươi mới được
```

### 7.2 Cấm đoán / quy tắc hệ thống

```text
不准彼此攻击，否则抹杀
→ không được tấn công lẫn nhau, nếu không sẽ bị xóa sổ
```

Rule:

```text
不准/禁止 A，否则 B → Không được A, nếu không B
不能/无法/没法 A → không thể A
```

### 7.3 Khả năng / bất khả năng

```text
能不能 / 可不可以 → có thể ... hay không
无法 / 没法 → không thể
做不到 → không làm được
```

Special:

```text
杀得过 → giết nổi / đánh thắng được
杀不过 → không giết nổi / không đánh lại
撑不下来 → không chống đỡ nổi
```

Need add potential complement rule:

```text
V 得 过 → V nổi / V được
V 不 过 → không V nổi
V 得 下去 → V tiếp được
V 不 下去 → không V tiếp được
```

---

## 8. Cause / Result / Purpose Pack

### 8.1 `导致 / 使得 / 让`

```text
导致了火山口大得如同一片海洋一样
→ khiến miệng núi lửa lớn như một vùng biển
```

Rule:

```text
A 导致 B → A dẫn đến B / khiến B
A 使得 B → A khiến B
A 让 B V/ADJ → A khiến B V/ADJ
```

### 8.2 `所以 / 因此 / 于是 / 正因为如此`

```text
正因为如此，吴明宁可放弃...
→ Chính vì vậy, Ngô Minh thà từ bỏ...
```

Rule:

```text
正因为如此 → chính vì vậy
因此/所以 → vì vậy / cho nên
于是 → thế là / vì thế
从而 → từ đó / qua đó
```

### 8.3 `以 / 用 / 靠 ... 来 ...`

Corpus:

```text
靠的不是拳头或者牙齿，而是人类特有的智慧
以小牺牲来成就大局
用支线剧情来解锁试炼空间
```

Rule:

```text
用 A 来 B → dùng A để B
靠 A 来 B → dựa vào A để B
以 A 来 B → lấy/dùng A để B
以 A 为 B → lấy A làm B
```

---

## 9. `不是...而是...`, `并非`, `莫不是`, `无非`

### 9.1 `不是 A，而是 B`

```text
不是血肉，不是内脏，而是极为精密的金属仪器
→ không phải máu thịt, không phải nội tạng, mà là thiết bị kim loại cực kỳ tinh vi
```

### 9.2 `并非`

```text
并非每只动物都有所谓的天道眷属值
→ không phải con vật nào cũng có cái gọi là giá trị quyến thuộc Thiên Đạo
```

Rule:

```text
并非 + universal → không phải ... nào cũng ...
并非 + clause → không phải là ...
```

### 9.3 `无非就是`

```text
无非就是火，烟，陷阱三大法宝
→ chẳng qua chỉ là ba pháp bảo lớn: lửa, khói, bẫy
```

### 9.4 `莫不是 / 莫非`

```text
莫非这书生是主角？
→ Chẳng lẽ tên thư sinh này là nhân vật chính?
```

---

## 10. Long Nominal Chain Transfer

### 10.1 Vấn đề

Corpus có nhiều danh ngữ dài không có `的`, ví dụ:

```text
洪荒万族第九千七百一十一位低等地精族
洪荒万族第八百六十一位高等地精族
洪荒万族中排行第九十八族的最上等种族
m国第五代主战斗机所有资料
二十一世纪初左右的科技造物
上清诛仙诀
初代主神空间
轮回小队成员
```

### 10.2 Thuật toán

```python
class NominalChainTransfer:
    HEAD_SUFFIXES = ["族", "人", "者", "物", "器", "诀", "功", "空间", "成员", "资料", "武器", "血统"]
    RANK_MARKERS = ["第", "排行", "级", "阶", "代"]
    OWNER_MARKERS = ["中", "的", "所属", "来自"]

    def parse_chain(tokens):
        # 1. tìm head noun cuối
        # 2. bảo vệ rank/level span
        # 3. modifier trước head chuyển sau hoặc trước tùy loại
        # 4. entity title giữ nguyên Han-Viet hoặc dictionary translation
```

### 10.3 Output rules

```text
第九千七百一十一位低等地精族
→ Địa tinh tộc cấp thấp, xếp thứ 9.711

第八百六十一位高等地精族
→ Địa tinh tộc cấp cao, xếp thứ 861

第九十八族的最上等种族
→ chủng tộc thượng đẳng nhất, xếp thứ 98

m国第五代主战斗机所有资料
→ toàn bộ tư liệu về chiến đấu cơ chủ lực thế hệ thứ năm của nước M
```

---

## 11. System / Infinite-flow Prompt Transfer

### 11.1 Patterns

```text
不准彼此攻击，否则抹杀
兑换价格是不等的
需要十五万奖励点数以及一个a级支线剧情
只需要1奖励点数就可以兑换1吨大米
可兑换的东西真的太多了
```

### 11.2 Module

```text
src/grammar/system_prompt_transfer.py
```

### 11.3 Rules

```text
抹杀 → xóa sổ / mạt sát
奖励点数 → điểm thưởng
支线剧情 → tình tiết nhánh
兑换 → đổi / quy đổi / vật phẩm đổi thưởng
试炼空间 → không gian thử luyện
轮回小队成员 → thành viên tiểu đội luân hồi
主神空间 → không gian Chủ Thần
```

### 11.4 Game resource numbers

```text
一个a级支线剧情 → một tình tiết nhánh cấp A
两个c级 → hai tình tiết nhánh cấp C
十五万奖励点数 → 150.000 điểm thưởng
一百倍的奖励点数 → gấp 100 lần điểm thưởng
三到八倍不等 → dao động từ gấp 3 đến gấp 8
```

---

## 12. Advanced Number Completion

### 12.1 Range / Approximate numbers

Corpus examples:

```text
七八米长短
两到三寸左右
200-300左右
8000-10000左右
一两百种
十几秒
两三个月
十天之后
五次轮回之后
```

Rules:

```text
七八 + unit → 7–8 + unit
两三 + unit → 2–3 + unit
十几 + unit → hơn mười + unit
一两百 → một hai trăm / khoảng 100–200
A 到 B → từ A đến B
A-B → A–B
左右/上下/约莫/大约 → khoảng
不下 + N → không dưới N / ít nhất N
接近 + N → gần N
N 多一点 → hơn N một chút
```

### 12.2 Measurement units

```text
米 → mét
千米 → km / kilômét
尺 / 寸 / 丈 → thước / tấc / trượng, hoặc giữ theo tiên hiệp nếu register cổ
吨 → tấn
倍 → lần / gấp
点 → điểm
秒 → giây
分钟 → phút
小时 → giờ
天 → ngày
年 → năm
世纪 → thế kỷ
```

### 12.3 Context classifier

```python
class NumberContext(Enum):
    CARDINAL = "cardinal"
    ORDINAL = "ordinal"
    RANKING = "ranking"
    LEVEL = "level"
    AGE = "age"
    YEAR = "year"
    DURATION = "duration"
    MEASUREMENT = "measurement"
    RANGE = "range"
    APPROX = "approx"
    GAME_POINTS = "game_points"
    GAME_BRANCH = "game_branch"
    TECH_GENERATION = "tech_generation"
    CULTIVATION_STAGE = "cultivation_stage"
```

### 12.4 Ordinal / rank / generation

```text
第一章 → Chương 1
第九千七百一十一位 → vị trí thứ 9.711 / xếp thứ 9.711
第五代战斗机 → chiến đấu cơ thế hệ thứ năm
一阶基因锁 → khóa gien cấp một
四阶及以下 → cấp bốn trở xuống
二十一世纪初 → đầu thế kỷ 21
```

### 12.5 Decimal and multiplier

```text
1.2倍左右 → khoảng gấp 1,2 lần
三倍 → gấp ba lần
十倍 → gấp mười lần
一百倍 → gấp một trăm lần
三到八倍不等 → dao động từ gấp ba đến gấp tám
```

### 12.6 Large numbers

```text
十五万 → 150.000
千万里 → nghìn vạn dặm / hàng chục triệu dặm, tùy register
上亿 → hơn trăm triệu
数百年 → mấy trăm năm
```

Register rule:

```text
Narration modern/system → dùng số Ả Rập: 150.000, 1.000, 1,2 lần
Xianxia cổ/đối thoại trang trọng → có thể dùng chữ: một nghìn, mười lăm vạn
```

---

## 13. Movement / Direction / Locative Deepening

### 13.1 Directional path verbs

Corpus:

```text
顺着足迹向着狗头人队伍直追而去
向南方行去
往东方走
从后面露出
从里面抓出
冲入到了空间之中
```

Rules:

```text
顺着 A 而去 → men theo A mà đi / đi theo A
向着 A 而去 → đi về phía A
往 A 走 → đi về phía A
从 A 露出 → lộ ra từ A
从 A 抓出 B → lôi B ra từ A
冲入到 A 之中 → lao vào trong A
```

### 13.2 Locative nouns

```text
之中 → trong / bên trong
之上 → trên / bên trên
之下 → dưới / bên dưới
之外 → ngoài / bên ngoài
之间 → giữa / trong khoảng
旁边 → bên cạnh
边缘 → rìa / mép
深处 → sâu trong
```

### 13.3 Avoid literal direction when temporal/system

```text
时间流动 → dòng chảy thời gian
回归之时 → khi trở về
五次轮回之后 → sau năm lần luân hồi
```

---

## 14. Action Chain / Combat Sequence Transfer

### 14.1 Common patterns

```text
举着 A 对向 B
顶着 A 向前一步
一口咬在 B 上
不停地 V1 V2
任凭 A 如何 B 都 C
```

### 14.2 Rules

```text
举着 A 对向 B → giơ A chĩa về phía B
顶着 A 向前一步 → mặc/đỡ A mà bước tới một bước
一口咬在 B 上 → cắn phập một cái vào B
不停地 V → không ngừng V
任凭 A 如何 V 都 B → mặc cho A V thế nào cũng B
```

### 14.3 Serial combat chain segmentation

```python
if sentence has repeated action verbs separated by commas:
    preserve chronological order
    insert "rồi", "tiếp đó", "sau đó" only when Vietnamese needs clarity
```

Example:

```text
他嘿嘿一笑，脚下再向前踏出一步，然后一口直接咬在了这深色狗头人的脸上
→ Hắn cười hắc hắc, dưới chân lại bước tới một bước, rồi cắn phập vào mặt con cẩu đầu nhân sẫm màu kia
```

---

## 15. Rhetorical / Dialogue / Inner Thought Transfer

### 15.1 Rhetorical question markers

```text
难道 A 吗？ → Chẳng lẽ A sao?
莫非 A？ → Chẳng lẽ A?
怎么可能 A？ → Sao có thể A được?
何必 A 呢？ → Hà tất phải A?
这是什么情况？ → Đây là tình huống gì vậy?
```

### 15.2 Tone particles

```text
啊 → a / vậy / đấy / ! tùy câu
吧 → đi / nhỉ / phải không
呢 → thế / vậy / còn ... thì sao
嘛 → mà / thôi mà
罢了 → mà thôi / thôi
而已 → mà thôi / chỉ vậy thôi
```

### 15.3 Spoken phrases in corpus

```text
我了个去 → mẹ kiếp / vãi / trời đất, tùy register
呵呵 → ha ha / hừ hừ / cười lạnh, tùy emotion
嘿嘿 → hắc hắc
好样的 → khá lắm / giỏi lắm
开什么玩笑 → đùa gì vậy / đùa kiểu gì thế
```

Need route through EAPEE emotion layer:

```text
呵呵 + 冷笑 → cười lạnh
嘿嘿 + 愤怒/杀意 → cười gằn
哈哈大笑 → cười ha hả
苦笑 → cười khổ
```

---

## 16. Entity Expansion từ chương 11–20

### 16.1 Entity types bổ sung

```text
PERSON: 吴明, 王羽, 徐文, 闻泽涛, 埃尔法, 洛丝, 骨, 吒, 车干, 李铭
RACE/FACTION: 地灵族, 地精族, 高等地精族, 低等地精族, 漆黑阵营, 光辉阵营, 泰夫林, 半精灵, 半兽人, 炼狱女妖
PLACE/WORLD: 洪荒大陆, 洪荒天庭, 天冻原, 瀚海, 火狱, 圣灵大陆, 西兰, 地球z国, m国
SYSTEM: 初代主神空间, 试炼空间, 轮回小队, 奖励点数, 支线剧情, 天道眷属值
ITEM/TECH: 超频宇宙弦能级反应堆, 第五代战斗机, 核反应堆, 太阳能光板, 武器生产线, 弹药生产线
CULTIVATION/POWER: 水运诀, 上清诛仙诀, 基因锁, 灵光, 真力, 筑基期, 金丹期, 圣位, 灵位
```

### 16.2 Protected span rules

```text
Do not split:
- 上清诛仙诀
- 初代主神空间
- 天道眷属值
- 奖励点数
- 支线剧情
- 第五代战斗机
- 一阶基因锁
- 二十一世纪初
- 洪荒万族第九千七百一十一位
```

### 16.3 Entity translation policy

```text
Character names: Han-Viet or memory-consistent transliteration
System terms: fixed glossary
Modern country abbreviations: z国 → nước Z, m国 → nước M unless glossary says otherwise
Race/faction: translate semantic + preserve proper noun if needed
Cultivation terms: use established xianxia Vietnamese terms
```

---

## 17. Rule priority cập nhật

```text
00 ProtectedSpanDetector
01 ClauseSegmenter
02 EntityDetector + NumberContextClassifier
03 SystemPromptDetector
04 ConditionalTransfer
05 ConcessionContrastTransfer
06 CauseResultTransfer
07 Disposal/Passive BA-BEI-JIANG
08 DE/NominalChainTransfer
09 ComparativeDegreeTransfer
10 ModalityTransfer
11 DirectionalLocativeTransfer
12 AspectTransfer
13 ActionChainTransfer
14 RhetoricDialogueTransfer
15 SurfacePostprocess
```

Lý do: entity/number phải khóa trước; conditional/connector nên xử lý trước các rule nhỏ; action/rhetoric xử lý sau khi đã có cấu trúc chính.

---

## 18. Data files bổ sung

```text
data/grammar/
├── discourse_connectors.json
├── modality_map.json
├── comparative_patterns.json
├── conditional_patterns.json
├── rhetoric_map.json
├── locative_map.json
├── combat_action_map.json
├── system_terms.json
├── number_context_patterns.json
├── measurement_units.json
├── game_resource_terms.json
└── entity_titles_xianxia_infinite.json
```

### 18.1 `system_terms.json`

```json
{
  "主神空间": "không gian Chủ Thần",
  "初代主神空间": "không gian Chủ Thần sơ đại",
  "试炼空间": "không gian thử luyện",
  "轮回小队": "tiểu đội luân hồi",
  "轮回小队成员": "thành viên tiểu đội luân hồi",
  "奖励点数": "điểm thưởng",
  "支线剧情": "tình tiết nhánh",
  "天道眷属值": "giá trị quyến thuộc Thiên Đạo",
  "抹杀": "xóa sổ"
}
```

### 18.2 `number_context_patterns.json`

```json
{
  "game_points": ["奖励点数", "天道眷属值"],
  "game_branch": ["支线剧情", "剧情"],
  "rank": ["第", "排行", "位"],
  "level": ["阶", "级", "层次", "境界"],
  "tech_generation": ["第", "代", "战斗机", "科技"],
  "duration": ["秒", "分钟", "小时", "天", "年"],
  "measurement": ["米", "千米", "尺", "寸", "丈", "吨", "倍"],
  "approx_markers": ["约莫", "大约", "差不多", "左右", "上下", "不下", "接近"]
}
```

---

## 19. Test corpus bổ sung từ chương 11–20

### 19.1 Conditional / concession

```python
("若是第三次召唤依然没有任何变化变动，这三人就会开始疑惑迟疑",
 "Nếu lần triệu hồi thứ ba vẫn không có bất kỳ thay đổi nào, ba người này sẽ bắt đầu nghi hoặc do dự")

("只要轮回小队成员度过了试炼空间，他们就可以兑换试炼空间里的东西",
 "Chỉ cần thành viên tiểu đội luân hồi vượt qua không gian thử luyện, bọn họ có thể đổi vật phẩm trong không gian thử luyện")

("除非是已经无法动弹了，不然人人是兵",
 "Trừ phi đã không thể cử động, nếu không thì ai ai cũng là binh lính")
```

### 19.2 Comparative / degree

```python
("吸纳越多的游离能量形成真力，奖励点数减少得就越多",
 "Hấp thu càng nhiều năng lượng du ly để hình thành chân lực, điểm thưởng giảm càng nhiều")

("比当初那头巨狼更加厉害",
 "lợi hại hơn con sói khổng lồ lúc trước")

("烧得焦黑",
 "cháy đến đen sì")
```

### 19.3 Number / resource

```python
("需要十五万奖励点数以及一个a级支线剧情",
 "cần 150.000 điểm thưởng và một tình tiết nhánh cấp A")

("只需要1奖励点数就可以兑换1吨大米或者面粉",
 "chỉ cần 1 điểm thưởng là có thể đổi 1 tấn gạo hoặc bột mì")

("三到八倍不等",
 "dao động từ gấp 3 đến gấp 8")

("1.2倍左右的程度",
 "mức độ khoảng gấp 1,2 lần")
```

### 19.4 System prompt

```python
("不准彼此攻击，否则抹杀吗？",
 "Không được tấn công lẫn nhau, nếu không sẽ bị xóa sổ sao?")

("兑换价格是不等的",
 "giá quy đổi không giống nhau")
```

### 19.5 Nominal chain

```python
("洪荒万族第九千七百一十一位低等地精族",
 "Địa tinh tộc cấp thấp, xếp thứ 9.711 trong vạn tộc Hồng Hoang")

("m国第五代主战斗机所有资料",
 "toàn bộ tư liệu về chiến đấu cơ chủ lực thế hệ thứ năm của nước M")
```

### 19.6 Rhetoric / dialogue

```python
("莫非这书生是主角？",
 "Chẳng lẽ tên thư sinh này là nhân vật chính?")

("开什么玩笑",
 "Đùa gì vậy")
```

---

## 20. Implementation sprint bổ sung

### Sprint 7 — Deep Grammar Pack

```text
S7.1 ClauseSegmenter + tests
S7.2 ConditionalTransfer + tests
S7.3 ConcessionContrastTransfer + tests
S7.4 CauseResultTransfer + tests
S7.5 ModalityTransfer + tests
S7.6 ComparativeDegreeTransfer + tests
```

### Sprint 8 — Number/System/Entity Completion

```text
S8.1 NumberContextClassifier
S8.2 RangeApproxConverter
S8.3 RankLevelConverter
S8.4 MeasurementConverter
S8.5 GameResourceConverter
S8.6 SystemPromptTransfer
S8.7 Entity glossary expansion from chapters 1–20
```

### Sprint 9 — Narrative/Action/Dialog Polish

```text
S9.1 NominalChainTransfer
S9.2 DirectionalLocativeTransfer deepening
S9.3 ActionChainTransfer
S9.4 RhetoricDialogueTransfer
S9.5 EAPEE tone integration
```

### Sprint 10 — Evaluation

```text
S10.1 Build chapter 1–20 construction-tagged test corpus
S10.2 Measure per-construction accuracy
S10.3 Error buckets:
      - entity split error
      - number context error
      - connector reorder error
      - long clause segmentation error
      - tone particle error
S10.4 Fix top 10 patterns
S10.5 Ensure old 98 tests + grammar tests pass
```

---

## 21. Accuracy targets cập nhật

```text
Protected entity span accuracy:      > 95%
Number context classification:       > 92%
System/game resource conversion:     > 95%
Conditional/concession transfer:     > 88%
Comparative/degree transfer:         > 85%
Nominal chain transfer:              > 82%
Action chain transfer:               > 80%
Rhetoric/dialogue tone transfer:     > 80%
Zero crash on chapter 1–20 corpus:   100%
```

---

## 22. Known limitations cần ghi trong docs

1. `呵呵`, `嘿嘿`, `啊`, `吧`, `呢` phụ thuộc cảm xúc; cần EAPEE hỗ trợ, rule đơn không đủ.
2. `得` có nhiều loại: degree/result/potential; cần POS + context, không thể map một chiều.
3. Danh ngữ dài chứa tên riêng và rank dễ bị tách sai nếu entity detector yếu.
4. Số Trung trong tên công pháp/địa danh/vũ khí phải được bảo vệ, không chuyển bừa sang số Ả Rập.
5. Câu dài > 80 ký tự nên ưu tiên clause segmentation, không dependency parse toàn câu.
6. `那怕` trong corpus có thể là biến thể/typo của `哪怕`; cần normalize nhưng vẫn preserve nếu xuất bản nguyên văn.

---

## 23. Checklist bổ sung v8

```text
[ ] Add ClauseSegmenter
[ ] Add ProtectedSpan + NumberContext before grammar rules
[ ] Add ConditionalTransfer: 若是/如果/只要/除非/一旦/凡是/每当
[ ] Add ConcessionContrastTransfer: 虽然/但是/不过/只是/却/反倒/哪怕
[ ] Add CauseResultTransfer: 导致/使得/所以/正因为如此/从而/以至于
[ ] Add ModalityTransfer: 必须/需得/只能够/不得不/无法/不准/否则
[ ] Add ComparativeDegreeTransfer: 越/比/更/得 complement
[ ] Add NominalChainTransfer for long nouns without 的
[ ] Add SystemPromptTransfer for 主神/兑换/抹杀/奖励点数/支线剧情
[ ] Add NumberContextClassifier
[ ] Add range/approx/measurement/rank/game-resource converters
[ ] Add ActionChainTransfer for combat sequences
[ ] Add RhetoricDialogueTransfer
[ ] Expand entity glossary from chapters 1–20
[ ] Build tagged test corpus from chapters 1–20
[ ] Run regression: old 98 tests must pass
```

---

## 24. Final architecture sau v8

```text
Input ZH
  ↓
Traditional/Simplified normalization
  ↓
ClauseSegmenter
  ↓
ProtectedSpanDetector
  ├─ EntityDetector
  ├─ NumberContextClassifier
  └─ SystemTermDetector
  ↓
ZHTokenizer + POS Tagger
  ↓
ConstructionDetector
  ├─ Core grammar: DE/BA/BEI/ASP/DIR
  ├─ Deep grammar: conditional/concession/cause/comparative/modality
  ├─ Narrative grammar: action chain/locative/dialogue/rhetoric
  └─ System grammar: game resource/rules/prompt
  ↓
TransferEngine with trace
  ↓
Existing RBMT lexical loop
  ↓
LuatNhan + EAPEE
  ↓
VI grammar postprocess
  ↓
Output VI
```

