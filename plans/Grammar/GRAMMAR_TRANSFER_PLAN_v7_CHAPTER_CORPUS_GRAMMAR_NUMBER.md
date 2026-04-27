# GRAMMAR_TRANSFER_PLAN_v7 — Corpus-driven Grammar/Number Expansion for converter-drduc

**Repo:** converter-drduc  
**Input corpus:** 10 chương upload `0001`–`0010`  
**Mục tiêu:** bổ sung các cấu trúc ngữ pháp và định dạng số còn thiếu sau v6; ưu tiên cấu trúc xuất hiện thật trong corpus truyện: Hồng Hoang / vô hạn lưu / chủ thần không gian / tu chân / tận thế / cổ đại.

---

## 0. Kết luận nhanh sau khi đọc corpus

10 chương này không chỉ là văn xianxia thuần. Nó trộn ít nhất 5 register:

1. **Huyền huyễn / Hồng Hoang:** `洪荒大陆`, `洪荒天庭政府`, `三清道尊`, `不周山`, `天道眷属值`.
2. **Vô hạn lưu / hệ thống:** `主神空间`, `奖励点数`, `支线剧情`, `兑换`, `强化`, `召人`, menu lựa chọn.
3. **Khoa học viễn tưởng / tận thế:** `人工智能`, `超人工智能`, `核武库`, `机器人三定律`, `金属城门`.
4. **Cổ đại lịch sử:** `五胡乱华`, `晋人`, `胡人`, `坞堡`, `一炷香`.
5. **Văn tự sự nội tâm:** câu dài, nhiều `而/但/却/只是/甚至/不过/若是/只要/一旦`, rất nhiều so sánh và nhấn mạnh.

Do đó grammar transfer không nên chỉ thêm BA/BEI/DE/Aspect. Cần bổ sung một lớp **Corpus Grammar Pack** gồm:

- Narrative clause connector transfer
- Existential/location chain transfer
- System/UI command transfer
- Number + measure + game-currency converter
- Approximate/range/ordinal/stage converter
- Resultative/potential/degree complement converter
- Comparative/emphasis/rhetorical converter
- Quote/dialogue/inner-thought formatter
- Proper entity span protection mở rộng cho hệ thống, cảnh giới, vật phẩm, công pháp, tổ chức, địa danh

---

## 1. Các cấu trúc xuất hiện nổi bật trong corpus

### 1.1. Chuỗi danh ngữ định danh / định nghĩa `X 是 Y, 是 Z, 也是 W`

Ví dụ từ chương 1:

```zh
这里是介于存在与不存在之间，是并不具备现实地点意义上的地方，是名为记录高塔的建筑物，是真实历史这一组织的总部，也是其存放所有记录下来的历史文献的地点。
```

Vấn đề:

- Nếu dịch từng token sẽ rời rạc: `nơi này là giữa tồn tại và không tồn tại, là...`.
- Đây là cấu trúc **multi-predicate definition**, cần gom thành một câu VI mượt.

Rule mới: `RULE_DEFINITION_CHAIN`

```text
X 是 A，是 B，是 C，也是 D
→ X là A, là B, là C, đồng thời cũng là D.
```

Nếu A/B/C là locative/abstract noun phrase:

```text
这里是介于 A 与 B 之间
→ Nơi này nằm giữa A và B
```

Ưu tiên khi `这里/那里/此处/此地 + 是 + locative abstract`:

```text
这里是介于存在与不存在之间
→ Nơi này nằm giữa tồn tại và không tồn tại
```

---

### 1.2. Chuỗi locative + existential `在...中/里/上/下/之间`

Corpus có rất nhiều:

```zh
走在导师身后
行走于时间与空间之间
站在高塔大门前
坐在了一张舒适的座椅上
位于无尽绿海中心世界之树残骸之上
在地下二层的一间孤零零小房间
```

Rule mới: `RULE_LOCATIVE_CHAIN`

```text
V 在/于 LOC 上/中/里/之间
→ V ở / trên / trong / giữa LOC
```

Mapping:

```json
{
  "在...上": "trên ...",
  "在...中": "trong ...",
  "在...里": "trong ...",
  "于...之间": "giữa ...",
  "位于...之上": "nằm trên ...",
  "来到...前": "đến trước ...",
  "走入...中": "bước vào trong ..."
}
```

Cần reorder cho VI:

```text
在地下二层的一间孤零零小房间
→ trong một căn phòng nhỏ lẻ loi ở tầng hầm thứ hai
```

Không dịch cứng `之上 = phía trên`; với địa danh/kiến trúc nên là `trên/nằm trên`.

---

### 1.3. `作为...来说/而言` viewpoint/topic frame

Ví dụ:

```zh
作为前几天还是一个极普通的太清大学大一新生来说，走在这里实在是挑战着他的神经。
作为魔法师，那怕是魔法学徒，埃尔法也知道太多神秘知识。
```

Rule mới: `RULE_AS_ROLE_FRAME`

```text
作为 NP 来说，CLAUSE
→ Với tư cách/là NP, CLAUSE
```

Nếu `NP` là trạng thái quá khứ của nhân vật:

```text
作为前几天还是...来说
→ Đối với một người mà chỉ vài ngày trước còn là...
```

Heuristic:

- `作为 + role + 来说/而言`: `với tư cách là`
- `作为 + long descriptive NP + 来说`: `đối với một ... như vậy`
- `作为 + profession`: `là một ...`

---

### 1.4. `无论是...还是...都/也` exhaustive concessive

Ví dụ chương 1:

```zh
无论是以他的知识储备来看，还是以他所能够获知的超前知识想象来解释，这里的“无”都会吞噬掉一切非圣人的存在。
```

Rule mới: `RULE_WULUN_EXHAUSTIVE`

```text
无论是 A，还是 B，S 都 V
→ Dù xét theo A hay B, S đều V
```

Không dịch `都` thành `đều` nếu đã có `bất kể/dù`; giữ một marker là đủ.

---

### 1.5. `虽然...但是/但/却/不过` concessive chain

Rất phổ biến trong các chương, nhất là chương 2, 5, 6, 8.

Rule mới: `RULE_CONCESSIVE_CHAIN`

```text
虽然 A，但是 B
→ Tuy A, nhưng B

虽然 A，B
→ Tuy A, B

A，但是 B
→ A, nhưng B

A，不过 B
→ A, có điều/tuy nhiên B
```

Register:

- Narration: `tuy nhiên`, `có điều`
- Dialogue: `nhưng`, `mà`
- Cổ văn: `song`, `nhưng mà` hạn chế dùng

---

### 1.6. `若是/如果/只要/一旦/除非/否则` condition logic

Các mẫu xuất hiện nhiều:

```zh
若是你太过贪心，可能就走不出这高塔了。
若真是有人恶作剧，那么三十秒一过就该显出了原型。
只要你有才能，任何力量体系都任由你选。
一旦有人想杀他，那一位必然会直接亲临洪荒大陆。
除非是他不想要这东西，否则就只能够同意。
```

Rule mới: `RULE_CONDITION_CHAIN`

Mapping:

```json
{
  "若是/如果 A, 就 B": "Nếu A thì B",
  "若真是 A, 那么 B": "Nếu đúng là A thì B",
  "只要 A, 就 B": "Chỉ cần A thì B",
  "一旦 A, 就/必然 B": "Một khi A thì/chắc chắn B",
  "除非 A, 否则 B": "Trừ khi A, nếu không thì B"
}
```

Cần bảo vệ `就` khỏi bị dịch lặp khi đã có `thì`.

---

### 1.7. `越...越...` comparative progression

Corpus có dạng:

```zh
越是后面时代的隐秘越多越详细
越是情况危急，他反倒越是冷静
情况越是危机，吴明反倒越是冷静
```

Rule mới: `RULE_YUE_YUE_COMPARATIVE`

```text
越 A 越 B
→ càng A càng B

越是 A，S 反倒越是 B
→ càng A, S ngược lại càng B
```

Nếu có `反倒/反而`:

```text
越是情况危急，他反倒越是冷静
→ Tình huống càng nguy cấp, hắn ngược lại càng bình tĩnh
```

---

### 1.8. `连...都/也` emphatic inclusion

Ví dụ:

```zh
连虚空都算不上
连一个守卫都没有
连动弹都不敢
连一点声响都没有
连那个功能的硬件都拆除了
```

Rule mới: `RULE_LIAN_DOU_EMPHASIS`

```text
连 X 都/也 V/没有
→ ngay cả X cũng V / cũng không có
```

Nếu `连 + numeral classifier + N + 都没有`:

```text
连一个守卫都没有
→ thậm chí một lính gác cũng không có
```

---

### 1.9. `不是...而是.../并不是...而是...` correction contrast

Ví dụ:

```zh
吴明并不是真实的他，或者说，他并不是原本的那个吴明，他穿越了。
不是借假修真，而是修得真实。
不是荒野求生的潜质，而是另一种更要高级得多的东西。
```

Rule mới: `RULE_NOT_A_BUT_B`

```text
不是 A，而是 B
→ không phải A, mà là B
并不是 A，而是 B
→ không hẳn/phải A, mà là B
```

Với `或者说`:

```text
A，或者说，B
→ A, hay nói đúng hơn, B
```

---

### 1.10. `直到...才/才总算/才终于` delayed completion

Ví dụ:

```zh
直到太阳都彻底落山时，他的这根木质长矛才总算是彻底造好。
直到吴明已经近在咫尺...它才猛的惊怒而醒。
直到减少到三十七为止才彻底消失。
```

Rule mới: `RULE_UNTIL_CAI_COMPLETION`

```text
直到 A, S 才 B
→ Mãi đến khi A, S mới B

直到 A 为止才 B
→ mãi cho đến A mới B / chỉ đến A thì mới B
```

Không dịch `才` thành `tài` hoặc bỏ mất sắc thái `mới`.

---

### 1.11. `一...就.../刚一...就...` immediate sequence

Ví dụ:

```zh
刚一走入大门，恍惚间一个失神...
一进入就立刻感觉到肉体不受任何控制
一扑之下巨狼就已到了吴明眼前
```

Rule mới: `RULE_IMMEDIATE_SEQUENCE`

```text
刚一 V，就 B
→ vừa V thì B
一 V 就 B
→ hễ/vừa V là B
```

Register theo ngữ cảnh:

- Narrative action: `vừa ... thì ...`
- General rule: `hễ ... là ...`

---

### 1.12. `得` degree/result complement

Corpus có nhiều `V 得 + ADJ/phrase`:

```zh
巨大得多
好得多
宝贝得和什么一样
弱小得多
吓人得多
看得出来
听得出来
```

Rule mới: `RULE_DEGREE_COMPLEMENT_DE`

Patterns:

```text
ADJ 得 多
→ ADJ hơn nhiều

V 得 ADJ/phrase
→ V đến mức ADJ/phrase

V 得 出来
→ có thể V ra / nhìn ra / nghe ra

宝贝得和什么一样
→ quý như bảo bối / quý vô cùng
```

Cần phân biệt `得`:

- `得` complement marker: `V 得 ADJ`
- `得` modal/ability: `能得您垂青` = `có thể được ngài để mắt`
- `得以`: fixed word = `được/có thể`

---

### 1.13. Resultative complement `V 完/好/出/开/住/下/死/光/破/断/成`

Ví dụ:

```zh
看完
走不出
放出来
开启
杀光
撞断
扯短
削得尖锐
造好
刺穿
掀开
拖延过
```

Rule mới: `RULE_RESULTATIVE_COMPLEMENT`

Mapping mẫu:

```json
{
  "V完": "V xong",
  "V好": "V xong / V cho tốt",
  "V出": "V ra",
  "V开": "V ra / mở V",
  "V住": "V được / giữ V lại",
  "V下": "V xuống / V lại",
  "V光": "V sạch / V hết",
  "V断": "V gãy/đứt",
  "V破": "V vỡ/rách/phá",
  "V成": "V thành"
}
```

Cần dùng lexical verb để chọn nghĩa:

```text
撞断 → đâm gãy / húc gãy
杀光 → giết sạch
看完 → xem/đọc xong
走不出 → không ra khỏi được
```

---

### 1.14. Potential complement `V得/不 + RCOMP`

Ví dụ:

```zh
走不出这高塔
看不清楚
拿捏不住
撑不住
想不明白
无法夺取
不能使用
```

Rule mới: `RULE_POTENTIAL_COMPLEMENT`

```text
V 不 出/到/完/住/了/清楚
→ không V được / không thể V ra/tới/xong/giữ/rõ

V 得 出/到/住
→ V được / có thể V ra/tới/giữ
```

Special:

```text
想不明白 → nghĩ không ra / không hiểu nổi
看不清楚 → nhìn không rõ
拿捏不住 → không giữ/khống chế nổi
```

---

### 1.15. Passive/causative `被/由/让/使得/导致/受到/死于`

Corpus cho thấy `被` rất nhiều nhưng không phải tất cả đều cần restructure.

Patterns:

```zh
已经被高等文明杀之取脑
都被扒了下来
被撞得弯了过去
三分之一被焚烧腐化
被一只幽魂附体
死于机器人大军手上
由机器人所取代
导致他的四肢都本能的动弹着
使得他们不停散发出负面意识
```

Rule mới: `RULE_PASSIVE_CAUSATIVE_EXPANDED`

```text
被 + Agent + V
→ bị/được Agent V

被 + V + result complement
→ bị V đến mức/result

由 X 所 V
→ do X V / được X V

死于 X 手上
→ chết dưới tay X / chết bởi X

导致 S V
→ khiến/dẫn đến S V

使得 S V
→ khiến S V
```

Sentiment chọn `bị/được`:

- Negative: `杀/扒/撞/焚烧/腐化/囚禁/折磨/附体/攻破` → `bị`
- Positive/neutral: `选中/强化/治愈/修复/给予` → `được`
- `由...所取代` thường là passive neutral: `bị ... thay thế` nếu bất lợi; `được ... thay thế` nếu tích cực.

---

### 1.16. Disposal `将/把/给` expanded

Corpus ít `把` nhưng nhiều `将` ở nghĩa disposal, và `给` làm complement/causative.

Ví dụ:

```zh
将天道盖亚化为封神榜
将其以时间划分开来
将整个身体都挂在了这树枝上
将这树枝给削得尖锐
将电脑拿到维修部去询问一下
将手指按到了yes那个选项上
```

Rule mới: `RULE_JIANG_BA_DISPOSAL`

```text
将/把 O V complement
→ V O complement
```

Nếu văn phong cổ/xianxia hoặc object dài:

```text
将 O 化为 X
→ biến O thành X

将 O 划分开来
→ chia O ra

将 O 给 V 得 R
→ V O đến R / làm cho O R
```

Không dịch cứng `将 = sẽ` khi sau `将` là noun phrase + verb.

Disambiguation:

```text
将 + time/future verb → sẽ
将 + NP + VV → disposal marker
```

---

### 1.17. Serial verbs and action chain dài

Corpus có rất nhiều chuỗi hành động:

```zh
转头看向高塔道
走到墙壁上，默默的抚摸着照片
翻身而起，就看到...
直接跳起将身体挂在了长矛上
顶着长矛与吴明直接撞向了地面
```

Rule mới: `RULE_ACTION_CHAIN`

Types:

```text
V1 着 O V2
→ vừa V1 O vừa V2 / V1 O rồi V2

V1 起身/而起 + V2
→ đứng dậy rồi V2

V1 向/到 LOC + V2
→ V1 về/tới LOC rồi V2

V1 着 O 直接 V2
→ V1 O rồi trực tiếp V2
```

Connector policy:

- Nếu cùng một hành động liền mạch: bỏ connector.
- Nếu có event boundary: thêm `rồi`.
- Nếu simultaneous: `vừa...vừa...`.

---

### 1.18. Rhetorical question and modal exclamation

Corpus có nhiều câu hỏi tu từ:

```zh
莫非……是不周山！？
凭什么成就了内宇宙？
这有什么奇怪的？
不是？
这未免太不可思议了吧？
```

Rule mới: `RULE_RHETORICAL_QUESTION`

Mapping:

```text
莫非 A？ → Chẳng lẽ A?
凭什么 A？ → Dựa vào đâu mà A? / Sao có thể A?
这有什么 X 的？ → Điều này có gì X đâu?
未免太 ADJ 了吧？ → chẳng phải quá ADJ sao?
```

Punctuation:

- `！？` giữ `?!` hoặc `!?` theo style VI.
- Trong truyện dịch Việt thường dùng `!?`.

---

### 1.19. Quote/dialogue/inner monologue formatting

Corpus dùng:

- Chinese quotes `“...”`
- ellipsis `……`
- parenthetical thought `（...）`
- system prompt trong quote
- English option `yes`

Rule mới: `RULE_DIALOGUE_FORMATTER`

```text
“...” → “...” hoặc "..." theo config
（...） → (...)
…… → ... hoặc … theo config
！？ → !?
```

Dialogue tags:

```text
X说道："..."
→ X nói: “...”

X问道："..."
→ X hỏi: “...”

X心中思索/心头大喊着
→ X thầm nghĩ / X gào lên trong lòng
```

System prompt:

```zh
“三十秒内进入光柱，转移目标锁定，失落xxxxx开始传送……”
→ “Tiến vào cột sáng trong vòng ba mươi giây. Đã khóa mục tiêu chuyển di, thất lạc xxxxx bắt đầu truyền tống...”
```

---

## 2. Các định dạng số cần bổ sung / hoàn thiện

### 2.1. Số thời gian countdown / deadline

Ví dụ:

```zh
三十秒内进入光柱
距离...约莫还有三四秒左右
三十秒一过
```

Rule: `NUMBER_COUNTDOWN_DEADLINE`

```text
三十秒内 → trong vòng 30 giây / trong vòng ba mươi giây
三四秒左右 → khoảng 3-4 giây
三十秒一过 → vừa hết 30 giây / sau khi 30 giây trôi qua
```

Config:

```yaml
number_style:
  narrative_small_numbers: words   # ba mươi giây
  system_prompt_numbers: digits    # 30 giây
```

---

### 2.2. Time chronology with ordinal seconds/minutes

Ví dụ chương 6:

```zh
在第七秒，全世界的核武库开始了启动，第一分二十八秒，第一颗核弹击中城市……
```

Rule: `NUMBER_EVENT_TIMELINE`

```text
第七秒 → ở giây thứ 7
第一分二十八秒 → phút thứ 1 giây thứ 28 / 1 phút 28 giây
第一颗核弹 → quả bom hạt nhân đầu tiên
```

Heuristic:

- `第 + N + 秒/分钟/年` sau timeline marker → ordinal temporal: `giây/phút/năm thứ N`.
- `第一分二十八秒` là elapsed timestamp, không phải `phân thứ nhất hai mươi tám giây`.

---

### 2.3. Age and century

Ví dụ:

```zh
二十一世纪的z国二十七岁宅系青年
王羽近年四十六岁
五六岁的男孩
```

Rule: `NUMBER_AGE_CENTURY`

```text
二十一世纪 → thế kỷ 21
二十七岁 → 27 tuổi
近年四十六岁 → gần 46 tuổi / năm nay 46 tuổi (check context)
五六岁 → năm, sáu tuổi / 5-6 tuổi
```

Special:

- `z国` → `nước Z` / giữ `Z quốc` theo register.
- `宅系青年` → `thanh niên otaku/trạch nam` tùy dictionary.

---

### 2.4. Approximate quantity / range

Ví dụ:

```zh
四五座以上
数个月
几十块钱
三四秒左右
十多米高
数圈
五十到一百人
一两个小时
十几人
七八名
近百人
百万计
数以亿万计
亿亿万万年
```

Rule: `NUMBER_APPROX_RANGE`

Mapping:

```json
{
  "四五座以上": "hơn bốn, năm ngọn / ít nhất bốn, năm ngọn",
  "数个月": "vài tháng",
  "几十块钱": "mấy chục đồng",
  "三四秒左右": "khoảng ba, bốn giây",
  "十多米": "hơn mười mét",
  "数圈": "mấy vòng",
  "五十到一百人": "năm mươi đến một trăm người",
  "一两个小时": "một, hai giờ",
  "十几人": "hơn mười người",
  "七八名": "bảy, tám người",
  "近百人": "gần trăm người",
  "百万计": "tính bằng hàng triệu",
  "数以亿万计": "tính bằng hàng trăm triệu / hàng ức vạn",
  "亿亿万万年": "ức ức vạn vạn năm / vô số năm"
}
```

Config cần có:

```yaml
xianxia_number_style:
  preserve_large_classical: true
```

Nếu true:

```text
亿亿万万年 → ức ức vạn vạn năm
```

Nếu false:

```text
亿亿万万年 → vô số năm
```

---

### 2.5. Units and physical measurements

Ví dụ:

```zh
数百米的高度
十五米高度
百米速度在六秒左右
数吨重的飞行载具
十米距离
三米多长短
成年人腰身粗细
拇指大小的洞口
```

Rule: `NUMBER_MEASURE_PHYSICAL`

```text
数百米的高度 → độ cao mấy trăm mét
十五米高度 → cao 15 mét
百米速度在六秒左右 → chạy 100 mét trong khoảng 6 giây
数吨重 → nặng vài tấn
十米距离 → khoảng cách 10 mét
三米多长短 → dài hơn 3 mét
成年人腰身粗细 → to cỡ vòng eo người trưởng thành
拇指大小 → cỡ ngón cái
```

Cần thêm `measure_context_classifier`:

```text
高度/高 → height
速度 → speed/time performance
重 → weight
距离 → distance
长短 → length
粗细 → thickness
大小 → size
```

---

### 2.6. Fractions / percentages / success rate

Ví dụ:

```zh
三分之一被焚烧腐化
提高至少一成
成功率也只有五成
刺入了三分左右
```

Rule: `NUMBER_FRACTION_RATE`

```text
三分之一 → một phần ba / 1/3
一成 → một thành / 10%
五成 → năm thành / 50%
三分左右 → khoảng ba phần / khoảng 30%? (context-dependent)
```

Context disambiguation:

- `成功率/概率/把握 + N成` → percent: `N0%` hoặc `N thành`.
- `刺入了三分左右` trong hành động vật lý → `đâm vào khoảng ba phần` không nhất thiết là 30%; nên dịch văn học: `đâm vào được khoảng ba phần`.

---

### 2.7. Cultivation/stage/order number

Ví dụ:

```zh
一阶基因锁
第五阶
五阶基因锁
筑基、金丹、元婴
初级法师
初级轮回小队成员
第一权限者
次级权限属性
```

Rule: `NUMBER_STAGE_RANK`

```text
一阶基因锁 → khóa gen bậc một / khóa gen cấp một
第五阶 → bậc năm
五阶基因锁 → khóa gen bậc năm
初级法师 → pháp sư sơ cấp
初级轮回小队成员 → thành viên tiểu đội luân hồi sơ cấp
第一权限者 → người có quyền hạn thứ nhất / quyền hạn cấp một cao nhất
次级权限属性 → thuộc tính quyền hạn thứ cấp
```

Config:

```yaml
rank_style:
  阶: "bậc"
  级: "cấp"
  初级: "sơ cấp"
  高级: "cao cấp"
```

---

### 2.8. Game/system currency and reward number

Ví dụ:

```zh
获得奖励点数五十
数字是五十，但是正在不停的减少，直到减少到三十七为止
每次召唤十点奖励点数
超过十人后，每次召唤一百奖励点数
五千奖励点数以及一个c级支线剧情
五百点次级奖励点数
一千五百奖励点数
每二十四小时就需要重复消耗一次奖励点数
```

Rule: `NUMBER_GAME_CURRENCY`

Mapping:

```text
奖励点数五十 → 50 điểm thưởng
十点奖励点数 → 10 điểm thưởng
一百奖励点数 → 100 điểm thưởng
五千奖励点数 → 5.000 điểm thưởng
五百点次级奖励点数 → 500 điểm thưởng thứ cấp
一千五百奖励点数 → 1.500 điểm thưởng
c级支线剧情 → một tình tiết nhánh cấp C
每二十四小时 → cứ mỗi 24 giờ
```

Important:

- In system/UI context, prefer digits for readability.
- Normalize Latin grade: `c级` → `cấp C`, uppercase.
- `点` after number + reward = point unit, not time `giờ`.

---

### 2.9. Historical time / elapsed years

Ví dụ:

```zh
一百一十年前
五十年过去了
六十年前
三个月前
十年前
半年时间
十年时间
二十九天之后
```

Rule: `NUMBER_HISTORICAL_TIME`

```text
一百一十年前 → 110 năm trước
五十年过去了 → 50 năm trôi qua
六十年前 → 60 năm trước
三个月前 → ba tháng trước / 3 tháng trước
十年前 → 10 năm trước
半年时间 → nửa năm / sáu tháng
十年时间 → mười năm
二十九天之后 → sau 29 ngày
```

Register:

- Narrative: words for small numbers, digits for technical/system.
- Historical exposition: digits acceptable for `110 năm`, `50 năm`, `29 ngày`.

---

### 2.10. Ancient time unit

Ví dụ:

```zh
一炷香的时间
```

Rule: `NUMBER_ANCIENT_TIME_UNIT`

```text
一炷香的时间 → thời gian một nén nhang / khoảng thời gian cháy hết một nén nhang
```

Config:

```yaml
ancient_time_style:
  literal: "một nén nhang"
  approximate_minutes: false
```

Không tự đổi sang 15 phút nếu không được cấu hình.

---

## 3. Entity expansion từ corpus

### 3.1. Entity types cần thêm

```python
class EntityType(Enum):
    PERSON = "PERSON"                  # 李铭, 吴明, 王羽, 徐文, 埃尔法
    TITLE_ROLE = "TITLE_ROLE"          # 导师, 主上, 法师学徒, 记录员
    ORG_FORCE = "ORG_FORCE"            # 真实历史, 洪荒天庭政府, 光辉阵营, 漆黑阵营
    PLACE = "PLACE"                    # 洪荒大陆, 西兰, 精灵主城绿光, 死亡平原
    FACILITY = "FACILITY"              # 记录高塔, 主神空间, 试炼空间
    ITEM = "ITEM"                      # 石头手表, 魔法卷轴, 手掌电脑
    WEAPON_EQUIP = "WEAPON_EQUIP"      # 木质长矛, 钢刀, 能量武器
    SKILL_ART = "SKILL_ART"            # 上清战拳, 冰心功, 上清诛仙功残篇
    SYSTEM_TERM = "SYSTEM_TERM"        # 奖励点数, 支线剧情, 天道眷属值
    CULTIVATION_STAGE = "CULTIVATION_STAGE" # 筑基, 金丹, 元婴, 圣人, 仙人
    SPECIES_RACE = "SPECIES_RACE"      # 精灵, 半精灵, 哥布林, 地精, 狗头人
    HISTORICAL_EVENT = "HISTORICAL_EVENT" # 永嘉之乱, 五胡乱华, 光辉之战
```

### 3.2. Protected span rules

Không tách sai:

```text
最初主神空间
洪荒天庭政府
太清大学 / 太清学府 / 玉清学府 / 上清学府
上清诛仙功残篇
天道眷属值
c级支线剧情
一阶基因锁 / 五阶基因锁
世界之树残骸
机器人三定律
```

### 3.3. Translation policy

```yaml
entity_translation:
  PERSON: han_viet_or_dictionary
  ORG_FORCE: dictionary_then_han_viet
  PLACE: dictionary_then_han_viet
  SKILL_ART: han_viet_with_gloss_optional
  SYSTEM_TERM: semantic_vi
  CULTIVATION_STAGE: established_xianxia_vi
```

Examples:

```text
主神空间 → Chủ Thần Không Gian
最初主神空间 → Chủ Thần Không Gian sơ khai / ban đầu
奖励点数 → điểm thưởng
天道眷属值 → giá trị quyến thuộc Thiên Đạo
支线剧情 → tình tiết nhánh
上清战拳 → Thượng Thanh Chiến Quyền
冰心功 → Băng Tâm Công
上清诛仙功残篇 → tàn thiên Thượng Thanh Tru Tiên Công
```

---

## 4. Module bổ sung vào repo

### 4.1. Files mới

```text
src/grammar/corpus_rules/
├── __init__.py
├── rule_definition_chain.py
├── rule_locative_chain.py
├── rule_as_role_frame.py
├── rule_wulun_exhaustive.py
├── rule_concessive_chain.py
├── rule_condition_chain.py
├── rule_yue_yue.py
├── rule_lian_dou.py
├── rule_not_a_but_b.py
├── rule_until_cai.py
├── rule_immediate_sequence.py
├── rule_degree_complement.py
├── rule_resultative_complement.py
├── rule_potential_complement.py
├── rule_passive_causative_expanded.py
├── rule_jiang_ba_disposal.py
├── rule_action_chain.py
├── rule_rhetorical_question.py
└── rule_dialogue_formatter.py

src/numbering/
├── __init__.py
├── number_context_classifier.py
├── game_currency_converter.py
├── measurement_converter.py
├── approximate_number_converter.py
├── timeline_number_converter.py
├── ancient_time_converter.py
└── protected_number_span.py

data/grammar/
├── connector_map.json
├── resultative_complement_map.json
├── potential_complement_map.json
├── degree_complement_map.json
├── rhetorical_map.json
├── locative_suffix_map.json
└── system_terms.json
```

### 4.2. Pipeline order revised

```text
Input ZH
  ↓
Sentence/quote segmentation
  ↓
Entity + protected number span detection
  ↓
Tokenizer + POS
  ↓
Construction detector
  ↓
Corpus grammar rules
  ↓
Core grammar rules: DE/Aspect/BEI/BA/DIR/SV/Topic
  ↓
Number/context converter for remaining numeric spans
  ↓
Existing RBMT lexical loop / Trie / LuatNhan
  ↓
EAPEE + Vietnamese grammar postprocess
  ↓
Output VI
```

Important:

- `protected_number_span` chạy trước `NumberConverter` để bảo vệ `五阶基因锁`, `c级支线剧情`, `一炷香`, `二十一世纪`, `第一权限者`.
- `game_currency_converter` chạy trước generic `NumberConverter`.
- `measurement_converter` chạy trước generic date/time converter.

---

## 5. Test suite cần bổ sung

### 5.1. Corpus-driven grammar tests

```python
CORPUS_GRAMMAR_TESTS = [
    ("无论是以他的知识储备来看，还是以他所能够获知的知识来解释", "Dù xét theo vốn tri thức của hắn hay dùng kiến thức hắn có thể biết để giải thích"),
    ("越是情况危急，他反倒越是冷静", "Tình huống càng nguy cấp, hắn ngược lại càng bình tĩnh"),
    ("连一个守卫都没有", "thậm chí một lính gác cũng không có"),
    ("不是借假修真，而是修得真实", "không phải mượn giả tu chân, mà là tu được chân thực"),
    ("直到减少到三十七为止才彻底消失", "mãi cho đến khi giảm xuống còn 37 mới hoàn toàn biến mất"),
    ("刚一走入大门，他就失神了", "vừa bước vào cổng, hắn liền thất thần"),
    ("看不清楚", "nhìn không rõ"),
    ("走不出这高塔", "không ra khỏi tòa tháp cao này được"),
    ("将天道盖亚化为封神榜", "biến Thiên Đạo Gaia thành Phong Thần Bảng"),
]
```

### 5.2. Number tests

```python
CORPUS_NUMBER_TESTS = [
    ("三十秒内进入光柱", "tiến vào cột sáng trong vòng 30 giây"),
    ("三四秒左右", "khoảng 3-4 giây"),
    ("第一分二十八秒", "1 phút 28 giây"),
    ("二十一世纪", "thế kỷ 21"),
    ("二十七岁", "27 tuổi"),
    ("五十到一百人", "50 đến 100 người"),
    ("三分之一", "một phần ba"),
    ("五成", "50%"),
    ("一炷香的时间", "thời gian một nén nhang"),
    ("五千奖励点数以及一个c级支线剧情", "5.000 điểm thưởng và một tình tiết nhánh cấp C"),
    ("每二十四小时", "cứ mỗi 24 giờ"),
    ("一阶基因锁", "khóa gen bậc một"),
]
```

### 5.3. Entity tests

```python
CORPUS_ENTITY_TESTS = [
    ("最初主神空间", "FACILITY", "Chủ Thần Không Gian sơ khai"),
    ("洪荒天庭政府", "ORG_FORCE", "Chính phủ Thiên Đình Hồng Hoang"),
    ("上清诛仙功残篇", "SKILL_ART", "tàn thiên Thượng Thanh Tru Tiên Công"),
    ("天道眷属值", "SYSTEM_TERM", "giá trị quyến thuộc Thiên Đạo"),
    ("c级支线剧情", "SYSTEM_TERM", "tình tiết nhánh cấp C"),
]
```

---

## 6. Ưu tiên triển khai sau v6

### Sprint V7.1 — Corpus connector rules

- `RULE_CONCESSIVE_CHAIN`
- `RULE_CONDITION_CHAIN`
- `RULE_YUE_YUE_COMPARATIVE`
- `RULE_LIAN_DOU_EMPHASIS`
- `RULE_NOT_A_BUT_B`
- `RULE_UNTIL_CAI_COMPLETION`
- `RULE_IMMEDIATE_SEQUENCE`

Target: giảm lỗi câu dài nghị luận/tự sự.

### Sprint V7.2 — Complement rules

- `RULE_RESULTATIVE_COMPLEMENT`
- `RULE_POTENTIAL_COMPLEMENT`
- `RULE_DEGREE_COMPLEMENT_DE`
- `RULE_ACTION_CHAIN`

Target: cải thiện câu hành động chiến đấu và mô tả trạng thái.

### Sprint V7.3 — Number pack

- `number_context_classifier.py`
- `game_currency_converter.py`
- `timeline_number_converter.py`
- `approximate_number_converter.py`
- `measurement_converter.py`
- `ancient_time_converter.py`

Target: không còn dịch sai `奖励点数五十`, `第一分二十八秒`, `一炷香`, `五成`, `三分之一`.

### Sprint V7.4 — Entity/system term pack

- `system_terms.json`
- `skill_art_detector.py`
- `facility_force_detector.py`
- `stage_rank_detector.py`

Target: bảo vệ tên riêng, công pháp, hệ thống, cảnh giới và thuật ngữ chủ thần.

---

## 7. Acceptance criteria

1. 98 tests cũ vẫn pass khi `enable_grammar_transfer=false`.
2. 150 tests grammar/number/entity mới pass.
3. Với 10 chương upload, log trace không có crash.
4. Các số sau phải được convert đúng theo context:
   - `三十秒内`
   - `第一分二十八秒`
   - `三分之一`
   - `五成`
   - `一炷香`
   - `五千奖励点数`
   - `c级支线剧情`
   - `一阶基因锁`
5. Các cấu trúc sau phải có rule riêng, không fallback lexical thuần:
   - `无论是...还是...都`
   - `越...越...`
   - `连...都`
   - `不是...而是...`
   - `直到...才`
   - `刚一...就`
   - `V不出/V不住/V得出`
   - `将/把 O V`
   - `由...所.../使得/导致/死于`

---

## 8. Ghi chú tích hợp với kế hoạch v6

Bản v7 không thay thế v6. Nó bổ sung thêm tầng **Corpus Grammar Pack** và **Number Context Pack**. Thứ tự ưu tiên mới:

```text
v6 Locative/Class/Time-shift
→ v7 Corpus connectors + complements
→ v7 Number context pack
→ v7 Entity/system term pack
→ DepParser nâng cấp nếu shallow detector không đủ
```

