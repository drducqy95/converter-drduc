# GRAMMAR_TRANSFER_PLAN_v18_NEW_STORY_CH201_400_COMPLETION

**Repo:** `converter-drduc`  
**Kế thừa:** `v14 + v15 + v16 + v17`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 201–400  
**Ngày:** 2026-04-25  
**Phiên bản:** v18.0 — Ch201–400 Grammar + Named-Entity Scanner Completion  

---

## 0. Executive Summary

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

## 1. Corpus Signals chương 201–400

### 1.1 Chapter title signals

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

### 1.2 High-frequency construction signals

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

# PART A — Planet / Race / Legion Scanner

## A1. Vấn đề

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

## A2. Ontology

```json
{
  "planet_suffix": ["星", "星球", "母星", "归星"],
  "star_system_suffix": ["星系", "星域", "星区"],
  "race_suffix": ["族", "生命体", "异形", "巨魔", "半鱼"],
  "legion_suffix": ["军团", "舰队", "部队", "小队", "营地"],
  "military_title": ["指挥官", "副官", "议长", "议员", "军团长"]
}
```

## A3. Rules

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

## A4. Translation examples

```text
巨魔星        → hành tinh Cự Ma
巨魔族        → tộc Cự Ma
巨魔军团      → Quân đoàn Cự Ma
归星          → Quy Tinh / hành tinh Quy
鄂多斯星系    → tinh hệ Eddos / Ngạc Đa Tư
陨星舰队      → Hạm đội Vẫn Tinh
```

---

# PART B — Bloodline-count Race Title

## B1. Pattern

```text
四血巨魔
五血屠英
三血巨魔
血脉属性数量
```

## B2. Meaning

Trong corpus này, `四血/五血` là cấp huyết mạch hoặc số thuộc tính huyết mạch, không phải “bốn máu” literal.

## B3. Rule

```python
Pattern: [NUM]血 + [RACE/PERSON/TITLE]
→ [RACE/PERSON/TITLE] [NUM] huyết / cấp [NUM] huyết
```

## B4. Examples

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

# PART C — Power Layer / Energy Level Classifier

## C1. Patterns

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

## C2. Rule types

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

## C3. Algorithm

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

# PART D — Future / Past / Timeline Grammar

## D1. Patterns

```text
未来？过去
窥探未来
未来层面的交锋
过去的阴影
时间限制
阴差阳错
```

## D2. Rule mapping

| ZH | VI |
|---|---|
| `窥探未来` | nhìn trộm tương lai / dòm ngó tương lai |
| `未来层面的交锋` | giao phong ở tầng diện tương lai |
| `过去的阴影` | bóng ma của quá khứ |
| `时间限制` | giới hạn thời gian |
| `阴差阳错` | trớ trêu thay / tình cờ sai lệch |
| `未来？过去` | tương lai? quá khứ? |

## D3. Timeline expression parser

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

## D4. Protection

Các cụm như `窥探未来` có thể là item/ability trong bracket:

```text
【窥探未来】
```

Nếu nằm trong `【...】`, protect as ability/item name.

---

# PART E — Cross-Franchise Artifact Scanner

## E1. Artifacts/world terms xuất hiện

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

## E2. Entity classes

```json
{
  "marvel": ["钢铁侠", "蜘蛛感应", "无限原石", "科尔森"],
  "dc": ["超人世界", "氪星"],
  "star_wars": ["凯伯水晶", "绝地", "西斯", "千年隼号", "死星", "原力"],
  "transformers": ["火种源碎片", "原始天尊"],
  "system_item": ["装备升级卡", "特殊图纸", "荣耀星路"]
}
```

## E3. Translation policy

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

## E4. Scanner rule

```python
if span in franchise_glossary:
    protect_as_cross_franchise_entity()
elif bracketed and contains known franchise suffix:
    protect_as_system_item()
```

---

# PART F — Force / Faith / Divinity System

## F1. Patterns

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

## F2. Translation

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

## F3. Rule

```python
if token in DIVINITY_TERMS:
    protect_domain_term()
    use divinity glossary
```

---

# PART G — Evolution / Transformation / Datafication Grammar

## G1. Patterns

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

## G2. Rule mapping

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

## G3. Grammar

```text
X 开始 / X 结束
→ X bắt đầu / X kết thúc

进行 X
→ tiến hành X

完成 X
→ hoàn thành X
```

## G4. State-machine handling

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

# PART H — Strategy / Conspiracy / Political Discourse

## H1. Patterns

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

## H2. Translation

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

## H3. Idiom guard

```python
STRATEGY_IDIOM_GUARD = [
    "螳螂捕蝉", "黄雀在后", "暗流涌动", "风雨欲来",
    "风雨又双叒叕欲来", "阴差阳错", "多层博弈"
]
```

---

# PART I — Meeting / Order / Mission Administration Grammar

## I1. Patterns

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

## I2. Translation mapping

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

## I3. Administrative frame

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

# PART J — Bounty / Wanted / External Announcement

## J1. Patterns

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

## J2. Translation

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

## J3. Rule

```python
if 对外 + [公布/悬赏/声明]:
    output = V_vi + " ra bên ngoài"
```

---

# PART K — Bug / Exploit / System Loophole Grammar

## K1. Patterns

```text
卡到了bug
刷脸
光速完成任务
系统升级
新的世界与功能
套娃
```

## K2. Mapping

| ZH | VI |
|---|---|
| `卡到了bug` | bắt được bug / kẹt được bug |
| `刷脸` | quét mặt / dùng mặt để qua cửa |
| `光速完成任务` | hoàn thành nhiệm vụ với tốc độ ánh sáng |
| `系统升级` | hệ thống nâng cấp |
| `新的世界与功能` | thế giới và chức năng mới |
| `套娃` | búp bê lồng nhau / lồng tầng lặp tầng |

## K3. Rule

Tách domain:

- Nếu trong system context: `bug` giữ nguyên “bug”.
- Nếu văn kể hài: `卡bug` → “lợi dụng bug”.
- Nếu title: giữ phong cách meme.

---

# PART L — Meme Title / Internet Slang Parser

## L1. Title patterns

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

## L2. Mapping policy

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

## L3. Rule

```python
if line_is_chapter_title and contains_slang_or_meme:
    use title_slang_map
else:
    use normal grammar transfer
```

---

# PART M — Nested Bracket Item Title Parser

## M1. Patterns

```text
【钢铁侠的装备升级卡】以及【氪星...】
【泰坦殖装】和【使徒】的联动
【千年隼号】以及【窥探未来】
【死星闪耀】 未来层面的交锋
【特殊图纸死星】
【荣耀星路】
```

## M2. Rule

```python
parse_bracket_items(line):
    items = collect_all("【...】")
    protect each item
    parse connector between items: 以及/和/与
```

## M3. Examples

```text
【泰坦殖装】和【使徒】的联动
→ sự liên động giữa [Thực Trang Titan] và [Sứ Đồ]

【千年隼号】以及【窥探未来】
→ [Millennium Falcon] và [Nhìn Trộm Tương Lai]
```

---

# PART N — Proper Name Scanner v18

## N1. Mục tiêu

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

## N2. Personal name candidates chương 201–400

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

## N3. Alias/title candidates

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

## N4. Faction/entity candidates

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

## N5. Artifact/ability candidates

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

## N6. Scanner stages

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

## N7. Confidence scoring

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

## N8. Short transliterated names

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

## N9. Alias linking

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

# PART O — Organization/Faction Hierarchy Scanner

## O1. Problem

`紫晶` có thể là civilization/faction, còn `紫晶文明` là full entity. `黯星` có thể là person/title/faction root. `星耀帝国` là polity.

## O2. Hierarchy model

```python
@dataclass
class EntityRecord:
    canonical: str
    aliases: list[str]
    entity_type: str
    parent: str | None
    confidence: float
```

## O3. Examples

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

## O4. Conflict resolver

```python
if alias maps to multiple entity records:
    use local suffix/context:
      黯星议会 -> faction
      黯星说/黯星看向 -> person/title
      黯星舰队 -> fleet/faction
```

---

# PART P — Domain-aware Transliteration Policy

## P1. Personal names

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

## P2. Config

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

## P3. Entity class based policy

| Type | Policy |
|---|---|
| Chinese original character | Hán Việt |
| Western/franchise character | Latin common name |
| System item | glossary preferred |
| Faction/civilization | Hán Việt + glossary |
| Place/planet | Hán Việt or transliteration stable |
| Tech product | semantic translation + protected proper prefix |

---

# PART Q — Core grammar gaps newly emphasized

## Q1. `上来就 + V`

```text
上来就开大
→ vừa vào đã tung chiêu cuối
```

Rule:

```python
上来就 + VP -> vừa bắt đầu đã + VP
```

## Q2. `一上来就 + V`

```text
一上来就开打
→ vừa lên đã đánh
```

## Q3. `终于卡到了bug`

```text
终于 + V
→ cuối cùng cũng + V

卡到bug
→ bắt/lợi dụng được bug
```

## Q4. `原来 X 都是 Y`

```text
原来大家都是内奸
→ hóa ra mọi người đều là nội gián
```

## Q5. `竟然是你 / 是他，就是他`

```text
竟然是你
→ hóa ra lại là ngươi

是他，就是他
→ là hắn, chính là hắn
```

## Q6. `拿下 / 镇压`

```text
拿下，镇压
→ bắt giữ, trấn áp
```

If combat:
- `拿下` → hạ/bắt lấy.
If political:
- `拿下 X` → giành được X.

---

# PART R — New Data Files

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

# PART S — Implementation Roadmap v18

## Sprint V18-A — Chapter title + bracket glossary seeding

- [ ] `ChapterTitleEntitySeeder`
- [ ] Extract bracket items from chapter titles.
- [ ] Extract non-bracket title proper nouns.
- [ ] Seed entity memory before body translation.
- [ ] Tests: 80 cases.

## Sprint V18-B — Planet/Race/Faction hierarchy

- [ ] `PlanetRaceLegionScanner`
- [ ] `FactionHierarchyResolver`
- [ ] `BloodlineRaceTitleRule`
- [ ] Tests: 100 cases.

## Sprint V18-C — Franchise artifact and ability scanner

- [ ] `FranchiseArtifactScanner`
- [ ] `CrossWorldAbilityScanner`
- [ ] `NestedBracketItemParser`
- [ ] Tests: 120 cases.

## Sprint V18-D — Power/evolution/datafication grammar

- [ ] `PowerLayerClassifier`
- [ ] `EvolutionTransformationRule`
- [ ] `DataficationRule`
- [ ] `DivinityForceRule`
- [ ] Tests: 120 cases.

## Sprint V18-E — Strategy/admin/announcement grammar

- [ ] `StrategyDiscourseRule`
- [ ] `AdminMissionRule`
- [ ] `BountyAnnouncementRule`
- [ ] `BugExploitRule`
- [ ] Tests: 120 cases.

## Sprint V18-F — Proper-name scanner completion

- [ ] Confidence scoring.
- [ ] Short transliteration detection.
- [ ] Alias linking.
- [ ] Entity hierarchy memory.
- [ ] Export review file for low-confidence entities.
- [ ] Tests: 150 cases.

---

# PART T — Test Matrix v18

## T1. Planet/race/legion

```python
V18_PLANET_RACE_TESTS = [
    ("巨魔星", "hành tinh Cự Ma"),
    ("巨魔族", "tộc Cự Ma"),
    ("巨魔军团", "Quân đoàn Cự Ma"),
    ("鄂多斯星系", "tinh hệ Eddos"),
]
```

## T2. Bloodline

```python
V18_BLOODLINE_TESTS = [
    ("四血巨魔", "Cự Ma tứ huyết"),
    ("五血屠英", "Đồ Anh ngũ huyết"),
    ("血脉属性数量", "số lượng thuộc tính huyết mạch"),
]
```

## T3. Power layer

```python
V18_POWER_TESTS = [
    ("A5层次", "tầng A5"),
    ("B级精神力", "tinh thần lực cấp B"),
    ("超级生命体", "sinh mệnh thể siêu cấp"),
    ("神格雏形", "hình thức sơ khai của thần cách"),
]
```

## T4. Franchise artifact

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

## T5. Evolution/datafication

```python
V18_EVOLUTION_TESTS = [
    ("基因优化", "tối ưu gen"),
    ("灵肉合一蜕变开始", "bắt đầu linh nhục hợp nhất và biến đổi"),
    ("二次进化", "tiến hóa lần hai"),
    ("数据化", "dữ liệu hóa"),
]
```

## T6. Strategy/admin

```python
V18_STRATEGY_TESTS = [
    ("各方算计", "các bên tính toán"),
    ("多层博弈", "thế cờ nhiều lớp"),
    ("紧急会议", "hội nghị khẩn cấp"),
    ("对外悬赏", "treo thưởng ra bên ngoài"),
]
```

## T7. Meme title

```python
V18_MEME_TITLE_TESTS = [
    ("上来就开大", "vừa vào đã tung chiêu cuối"),
    ("风雨又双叒叕欲来啦", "phong ba lại-lại-lại nữa sắp đến rồi"),
    ("主宰竟是我自己？", "hóa ra Chúa Tể lại là chính ta?"),
    ("干一炮就跑？", "bắn một phát rồi chạy?"),
]
```

## T8. Proper name scanner

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

# PART U — Rule Priority cập nhật sau v18

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

# PART V — Acceptance Metrics v18

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

# PART W — Merge Strategy

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

# END OF v18
