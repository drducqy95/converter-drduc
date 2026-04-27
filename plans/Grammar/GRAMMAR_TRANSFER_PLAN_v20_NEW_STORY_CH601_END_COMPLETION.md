# GRAMMAR_TRANSFER_PLAN_v20_NEW_STORY_CH601_END_COMPLETION

**Repo:** `converter-drduc`  
**Kế thừa:** `v14 + v15 + v16 + v17 + v18 + v19`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 601 → hết truyện  
**Ngày:** 2026-04-25  
**Phiên bản:** v20.0 — Endgame / Transcender / Cosmic Alliance / Final Named-Entity Scanner Completion  

---

## 0. Executive Summary

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

## 1. Corpus Signals chương 601 → hết

### 1.1 Endgame system examples

```text
【概率风暴：你处于终极智慧的概率风暴可能性收束锁定中，因此会看见交集画面。
持续时间-720小时】

【源质融合：你正在进化的道路上坚定不移的前进着。】

【10%的锚点进度等待系统升级完毕后发放】

【圣·天尊】
【映照宇宙】
```

### 1.2 Political/cosmic scene examples

```text
大宇宙联盟的公共会议室中座无虚席，所有文明领袖尽皆到来。
今天是大宇宙联盟第一次正式和联合阵线会晤。
由于前段时间他们针对龙尊的内部作战计划遭到了泄露，导致他的声望再次受到了严重损伤。
```

### 1.3 Engineering / mega-construction examples

```text
一座大型的金属构造体正在被一个个综合辅助建造设备团团包围。
这座建筑物的整体已经完成了很大一部分，像是一座带有廊道的巨型传送门。
其基座部分便有常规生命星球的数倍大小。
```

---

# PART A — Transcender / Source-Essence System Scanner

## A1. New domain terms

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

## A2. Ontology

```json
{
  "transcender_status": ["超越者", "进化顶端", "圣·天尊"],
  "source_essence": ["源质", "源质融合", "燃烧源质", "源质核心"],
  "cosmic_authority": ["映照宇宙", "宇宙感知", "烙印攻击", "真名"],
  "anchor_system": ["锚点进度", "锚点", "进度发放"],
  "life_evolution": ["生命跃迁", "重生", "真正意义上的死亡"]
}
```

## A3. Translation policy

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

## A4. Rule

```python
if span in TRANSCENDER_GLOSSARY:
    protect_as_cosmic_system_term(span)

if span contains "源质" and verb in ["融合", "燃烧", "吸收"]:
    classify SOURCE_ESSENCE_ACTION
```

---

# PART B — Anchor Progress / Endgame Reward Parser

## B1. Pattern

```text
【10%的锚点进度等待系统升级完毕后发放】
【圣·天尊】
【映照宇宙】
SSS评价
整体评价只有SS
阶段性的任务完成
整体结算
```

## B2. System reward rules

| Pattern | VI |
|---|---|
| `X%的锚点进度` | X% tiến độ neo điểm |
| `等待系统升级完毕后发放` | chờ hệ thống nâng cấp xong rồi phát |
| `SSS评价` | đánh giá SSS |
| `整体评价只有SS` | đánh giá tổng thể chỉ có SS |
| `阶段性任务` | nhiệm vụ giai đoạn |
| `整体结算` | kết toán tổng thể |
| `阶段性结算` | kết toán theo giai đoạn |

## B3. Rule

```python
Pattern: 【PERCENT + 锚点进度 + WAIT_CONDITION】
Output: 【PERCENT tiến độ neo điểm sẽ được phát sau khi hệ thống nâng cấp hoàn tất】

Pattern: [GRADE]评价
Output: đánh giá [GRADE]
```

## B4. Grade guard

`SSS/SS/S` trong `SSS评价`, `SS整体评价` là rating, không phải entity hoặc chữ cái bình thường.

```python
RATING_RE = r"\bS{1,3}\+?\s*评价\b"
```

---

# PART C — Mission Settlement Grammar

## C1. Patterns

```text
最后任务会结算两次
一次是阶段性的，另一次则是整体结算
其中一些阶段性任务完成的并不算太好
```

## C2. Translation

```text
nhiệm vụ cuối cùng sẽ được kết toán hai lần
một lần là theo giai đoạn, lần còn lại là kết toán tổng thể
một số nhiệm vụ giai đoạn trong đó hoàn thành không được tốt lắm
```

## C3. Rule

```python
if sentence contains ["结算", "阶段性", "整体"]:
    use mission_settlement_frame
```

---

# PART D — Cosmic Alliance Diplomacy Grammar

## D1. Entities

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

## D2. Diplomatic terms

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

## D3. Translation

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

## D4. Rule

```python
if sentence contains alliance/faction entities and meeting terms:
    classify DIPLOMATIC_SCENE
    preserve formal register
```

---

# PART E — Formal Meeting / Summit / Projection Discourse

## E1. Scene grammar

```text
会议室中座无虚席
所有文明领袖尽皆到来
他们把目光放在最前列的五道身影上
第一时间双方都没有说话，而是在互相打量着
```

## E2. Translation patterns

| ZH | VI |
|---|---|
| `座无虚席` | không còn chỗ trống / kín chỗ |
| `尽皆到来` | đều đã đến đông đủ |
| `最前列` | hàng đầu tiên / vị trí trước nhất |
| `第一时间` | ngay lập tức / ngay thời điểm đầu tiên |
| `互相打量` | quan sát lẫn nhau |
| `话音刚落` | lời vừa dứt |

## E3. Rule

These are mostly idiomatic discourse chunks; add to `meeting_scene_idiom_guard.txt`.

---

# PART F — Civilizational Hierarchy and Role Scanner

## F1. Entity-role structure

```text
星耀帝国加入大宇宙联盟
星耀帝国的帝皇
帝国高等教育部
天才少年班
五大文明之中
零号文明秘密仓库
永恒文明核心
```

## F2. Hierarchy model

```python
EntityRecord(
    canonical="星耀帝国",
    type="civilization/polity",
    children=["帝国高等教育部", "天才少年班"],
    roles=["帝皇", "德罗耶达"]
)
```

## F3. Rule

```python
Pattern: ENTITY + 的 + ROLE/DEPARTMENT
Output:
  if role: ROLE của ENTITY
  if department: DEPARTMENT thuộc ENTITY
```

## F4. Examples

```text
星耀帝国的帝皇
→ Đế Hoàng của Tinh Diệu Đế Quốc

帝国高等教育部
→ Bộ Giáo dục Cao đẳng của Đế Quốc

零号文明秘密仓库
→ kho bí mật của Văn minh Số Không
```

---

# PART G — Creator / Intelligence Entity Scanner

## G1. Entities

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

## G2. Rule

- `终极智慧` is not a common noun phrase; protect as entity/title.
- `创世神` may be entity-title or common title depending context.
- `先知` can be title-name entity if repeated as subject.
- `龙尊` is title/alias for Li Yu, link to `李宇`.

## G3. Alias mapping

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

## G4. Entity confidence

```python
if term appears in dialogue as addressee + 阁下:
    score += 3
if term appears as speaker subject repeatedly:
    score += 2
if term is title-like and chapter-final arc:
    score += 2
```

---

# PART H — Probability Storm / Information-State Grammar

## H1. Patterns

```text
概率风暴
可能性收束锁定
交集画面
信息态收敛
身体中不会发生任何无缘无故的事情
主动能力催发
来自外界因素
```

## H2. Translation

| ZH | VI |
|---|---|
| `概率风暴` | bão xác suất |
| `可能性收束锁定` | khóa thu hẹp khả năng |
| `交集画面` | hình ảnh giao hội / hình ảnh giao điểm |
| `信息态收敛` | thu liễm trạng thái thông tin |
| `主动能力催发` | năng lực chủ động kích phát |
| `外界因素` | yếu tố bên ngoài |

## H3. Rule

```python
if span contains "概率/可能性/收束/信息态":
    classify INFORMATION_PROBABILITY_TECH
```

## H4. Scientific phrase guard

Do not split `可能性收束锁定` into generic `khả năng + thu + bó`.

---

# PART I — Dimension Isolation / Blockade / Bridge Device Grammar

## I1. Patterns

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

## I2. Translation

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

## I3. Rule

```python
if sentence has "从 X 中 + 隔离/脱离/切断":
    use separation_frame

Pattern: 切断 A 和 B 的联系
→ cắt đứt liên hệ giữa A và B
```

---

# PART J — Large Engineering Megastructure Grammar

## J1. Patterns

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

## J2. Translation

| ZH | VI |
|---|---|
| `大型金属构造体` | kết cấu kim loại cỡ lớn |
| `综合辅助建造设备` | thiết bị hỗ trợ xây dựng tổng hợp |
| `巨型传送门` | cổng truyền tống khổng lồ |
| `基座部分` | phần bệ nền |
| `数倍大小` | lớn gấp mấy lần |
| `每扩张一微米` | mỗi khi mở rộng thêm một micromet |
| `几何倍数递增` | tăng theo cấp số nhân |

## J3. Number/measure addition

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

# PART K — Political Blame / Reputation Damage / Public Denunciation

## K1. Patterns

```text
内部作战计划遭到了泄露
导致他的声望再次受到了严重损伤
口诛笔伐
栽赃成他们支援不力
宣泄的地方
明着威胁，暗中引诱
```

## K2. Translation

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

## K3. Passive political frame

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

# PART L — Threat / Coercion + Hidden Inducement Discourse

## L1. Pattern

```text
明着威胁，暗中引诱
为星耀帝国铺路
完全不上心
```

## L2. Rule

```text
明着 X，暗中 Y
→ ngoài mặt X, âm thầm/ngầm Y
```

## L3. Examples

```text
明着威胁，暗中引诱
→ ngoài mặt uy hiếp, ngầm dụ dỗ
```

---

# PART M — Time-skip and Long-duration Narrative Transfer

## M1. Patterns

```text
转眼间便是两个月之后
时间匆匆而过
又是接近两个月的时间转瞬即逝
三年过去了
十年来
日渐强大
缓步进行中
```

## M2. Translation

| ZH | VI |
|---|---|
| `转眼间便是两个月之后` | chớp mắt đã là hai tháng sau |
| `时间匆匆而过` | thời gian vội vã trôi qua |
| `转瞬即逝` | thoáng cái đã trôi qua |
| `三年过去了` | ba năm đã trôi qua |
| `十年来` | suốt mười năm qua |
| `日渐强大` | ngày càng lớn mạnh |
| `缓步进行中` | đang tiến hành chậm rãi |

## M3. Rule

```python
if sentence startswith time_skip_marker:
    classify NARRATIVE_TIME_SKIP
```

---

# PART N — Semantic Negation: `不会真正意义上的死亡`

## N1. Pattern

```text
超越者不会真正意义上的死亡
```

## N2. Problem

Literal “không chết trên ý nghĩa chân chính” awkward.

## N3. Rule

```text
不会 + 真正意义上 + V/N
→ sẽ không thật sự V / không V theo đúng nghĩa
```

## N4. Translation

```text
超越者不会真正意义上的死亡
→ Siêu Việt Giả sẽ không thật sự chết theo đúng nghĩa.
```

---

# PART O — Stacked Discourse Linkers

## O1. Patterns

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

## O2. Mapping

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

## O3. Rule

If multiple discourse linkers appear, collapse to natural VI:

```text
只不过，他倒是没想到...
→ chỉ có điều, hắn lại không ngờ rằng...
```

Avoid duplicate `nhưng tuy nhiên`.

---

# PART P — Proverb / Conditional Guard

## P1. Patterns

```text
一旦扩散
覆巢之下安有完卵
藏拙
木已成舟
一山不容二虎
```

## P2. Translation

| ZH | VI |
|---|---|
| `一旦扩散` | một khi lan rộng |
| `覆巢之下安有完卵` | tổ đã lật thì làm gì còn trứng lành |
| `藏拙` | giấu nghề / che giấu thực lực |
| `木已成舟` | ván đã đóng thuyền |
| `一山不容二虎` | một núi không dung hai hổ |

## P3. Guard

Protect as idiom before word-level grammar.

---

# PART Q — Author-note / Meta Paragraph Classifier

## Q1. Pattern

```text
各位读者老板们，最后“任务”也揭晓了，应该不少人都能猜到。
如果嫌等的太烦，可以45678天后直接来看结局，反正二十号之前肯定完结。
```

## Q2. Rule

```python
if paragraph contains ["读者", "老板们", "完结", "结局", "作者", "求票", "二十号之前"]:
    classify AUTHOR_META_PARAGRAPH
```

## Q3. Config

```python
translate_author_meta = False
preserve_author_meta = True
author_meta_prefix = "Ghi chú tác giả:"
```

---

# PART R — Final-Arc Proper Name Scanner

## R1. New / important entities

### Personal / title entities

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

### Factions / civilizations

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

### Cosmic/system concepts

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

## R2. Alias hierarchy

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

## R3. Endgame entity scoring additions

```python
if term appears in system reward bracket: +6
if term appears with 阁下: +3
if term appears in diplomatic scene as faction: +3
if term appears in cosmic concept glossary: +4
if term appears after "被称之为": +2
if term appears with quote marks “...” in title/name context: +2
```

---

# PART S — Projection / Communication Scene Grammar

## S1. Patterns

```text
结束通讯吧
远程投影
投影消失在虚空中
屏幕
交接
具体细节
```

## S2. Translation

| ZH | VI |
|---|---|
| `结束通讯` | kết thúc liên lạc |
| `远程投影` | hình chiếu từ xa |
| `投影消失` | hình chiếu biến mất |
| `屏幕` | màn hình |
| `交接` | bàn giao / tiếp nhận |
| `具体细节` | chi tiết cụ thể |

---

# PART T — Entity Ownership / Subordination in Alliances

## T1. Patterns

```text
星耀帝国加入大宇宙联盟
其他文明境内
帝国高等教育部
大宇宙联盟的公共会议室
联合阵线的众多文明
```

## T2. Rule

```python
Pattern: FACTION_A + 加入 + FACTION_B
→ FACTION_A gia nhập FACTION_B

Pattern: FACTION + 境内
→ trong lãnh thổ của FACTION

Pattern: FACTION + 的 + ORG_PLACE
→ ORG_PLACE của/thuộc FACTION
```

---

# PART U — Ultimate Status / State Panel Grammar

## U1. Patterns

```text
【概率风暴：...持续时间-720小时】
【源质融合：...】
【圣·天尊】
【映照宇宙】
【10%的锚点进度...】
```

## U2. Rule

Use `SystemPanelParser` from v16, but add:

```python
SYSTEM_PANEL_KIND_ENDGAME = [
    "STATUS_EFFECT",
    "COSMIC_REWARD",
    "ANCHOR_PROGRESS",
    "TRANSCENDER_TITLE",
]
```

## U3. Examples

```text
【概率风暴：你处于终极智慧的概率风暴可能性收束锁定中，因此会看见交集画面。
持续时间-720小时】
→ 【Bão Xác Suất: ngươi đang ở trong khóa thu hẹp khả năng của Bão Xác Suất từ Tối Chung Trí Tuệ, vì vậy sẽ nhìn thấy hình ảnh giao hội. Thời gian duy trì: 720 giờ】

【源质融合：你正在进化的道路上坚定不移的前进着。】
→ 【Dung Hợp Nguyên Chất: ngươi đang kiên định tiến bước trên con đường tiến hóa.】
```

---

# PART V — Data files cần bổ sung

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

# PART W — Implementation Roadmap v20

## Sprint V20-A — Endgame system/reward parser

- [ ] `TranscenderSystemScanner`
- [ ] `AnchorProgressParser`
- [ ] `MissionSettlementRule`
- [ ] `EndgameSystemPanelKindClassifier`
- [ ] Tests: 120 cases.

## Sprint V20-B — Cosmic diplomacy/faction hierarchy

- [ ] `CosmicAllianceScanner`
- [ ] `DiplomaticSceneRule`
- [ ] `CivilizationalHierarchyResolver`
- [ ] `AllianceSubordinationRule`
- [ ] Tests: 120 cases.

## Sprint V20-C — Information/probability/dimension technology

- [ ] `ProbabilityInformationTermParser`
- [ ] `DimensionBlockadeRule`
- [ ] `MegaStructureEngineeringRule`
- [ ] Tests: 120 cases.

## Sprint V20-D — Political discourse + time skip

- [ ] `PoliticalBlameRule`
- [ ] `ThreatInducementRule`
- [ ] `NarrativeTimeSkipRule`
- [ ] `StackedDiscourseLinkerCleaner`
- [ ] Tests: 100 cases.

## Sprint V20-E — Final-arc entity scanner

- [ ] Add final arc entity seeds.
- [ ] Add endgame alias hierarchy.
- [ ] Link `李宇 ↔ 龙尊 ↔ 超越者 ↔ 圣·天尊`.
- [ ] Add projection/communication scene terms.
- [ ] Export final glossary review.
- [ ] Tests: 150 cases.

## Sprint V20-F — Author/meta + idiom guards

- [ ] `AuthorMetaParagraphClassifier`
- [ ] `FinalArcIdiomGuard`
- [ ] `SemanticNegationRule`
- [ ] Tests: 80 cases.

---

# PART X — Test Matrix v20

## X1. Transcender/source essence

```python
V20_TRANSCENDER_TESTS = [
    ("超越者", "Siêu Việt Giả"),
    ("源质融合", "dung hợp nguyên chất"),
    ("生命跃迁完成", "hoàn tất bước nhảy sinh mệnh"),
    ("圣·天尊", "Thánh · Thiên Tôn"),
    ("映照宇宙", "Ánh Chiếu Vũ Trụ"),
]
```

## X2. Anchor/reward/settlement

```python
V20_REWARD_TESTS = [
    ("10%的锚点进度等待系统升级完毕后发放",
     "10% tiến độ neo điểm sẽ được phát sau khi hệ thống nâng cấp hoàn tất"),
    ("直接刷出来SSS评价", "trực tiếp刷 ra đánh giá SSS"),
    ("整体评价只有SS", "đánh giá tổng thể chỉ có SS"),
    ("最后任务会结算两次", "nhiệm vụ cuối cùng sẽ được kết toán hai lần"),
]
```

## X3. Alliance/diplomacy

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

## X4. Probability/info/dimension

```python
V20_INFO_TECH_TESTS = [
    ("概率风暴", "bão xác suất"),
    ("可能性收束锁定", "khóa thu hẹp khả năng"),
    ("信息态收敛", "thu liễm trạng thái thông tin"),
    ("从主宇宙之中隔离出来", "tách ra khỏi vũ trụ chính"),
    ("切断这片星域和主宇宙的联系", "cắt đứt liên hệ giữa tinh vực này và vũ trụ chính"),
]
```

## X5. Engineering

```python
V20_ENGINEERING_TESTS = [
    ("大型金属构造体", "kết cấu kim loại cỡ lớn"),
    ("综合辅助建造设备", "thiết bị hỗ trợ xây dựng tổng hợp"),
    ("巨型传送门", "cổng truyền tống khổng lồ"),
    ("每扩张一微米", "mỗi khi mở rộng thêm một micromet"),
    ("消耗材料呈几何倍数递增", "vật liệu tiêu hao tăng theo cấp số nhân"),
]
```

## X6. Political discourse

```python
V20_POLITICAL_TESTS = [
    ("内部作战计划遭到了泄露", "kế hoạch tác chiến nội bộ bị rò rỉ"),
    ("声望再次受到了严重损伤", "danh vọng lại bị tổn hại nghiêm trọng"),
    ("口诛笔伐", "công kích bằng lời nói và ngòi bút"),
    ("栽赃成他们支援不力", "vu oan thành việc bọn họ chi viện không hiệu quả"),
]
```

## X7. Time skip / discourse

```python
V20_TIME_DISCOURSE_TESTS = [
    ("转眼间便是两个月之后", "chớp mắt đã là hai tháng sau"),
    ("三年过去了", "ba năm đã trôi qua"),
    ("十年来", "suốt mười năm qua"),
    ("只不过，他倒是没想到", "chỉ có điều, hắn lại không ngờ rằng"),
]
```

## X8. Final entity scanner

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

# PART Y — Rule Priority cập nhật sau v20

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

# PART Z — Acceptance Metrics v20

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

## Merge Strategy

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

# END OF v20
