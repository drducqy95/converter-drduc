# GRAMMAR_TRANSFER_PLAN_v17_NEW_STORY_CH101_200_COMPLETION

**Repo:** `converter-drduc`  
**Kế thừa:** `GRAMMAR_TRANSFER_PLAN_v14_MERGED_v12_v13_FULL.md` + `v15` + `v16`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 101–200  
**Ngày:** 2026-04-25  
**Phiên bản:** v17.0 — Space-war / Auction / Civilization / High-tech Entity Completion  

---

## 0. Executive Summary

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

# PART A — Space Fleet / Starship Entity Chain

## A1. Vấn đề

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

## A2. Entity suffix ontology mở rộng

```json
{
  "space_fleet": ["舰队", "战舰", "运输舰", "星舰", "飞船", "母舰", "旗舰"],
  "space_place": ["星", "星球", "行星", "恒星", "星域", "星系", "星港", "跃迁轨道"],
  "space_network": ["星际网络", "通讯网络", "频道", "坐标", "航线"],
  "war_event": ["之战", "战争", "战役", "冲突", "袭击"]
}
```

## A3. Rule

```python
if span.endswith(("舰队", "战舰", "飞船", "星球", "星", "之战")):
    if span has proper-name prefix or repeated in corpus:
        protect_as_entity(span)
    else:
        translate_as_common_noun_chain(span)
```

## A4. Examples

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

# PART B — Civilization / Faction / Polity Detector

## B1. Pattern

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

## B2. Rule

```python
POLITY_SUFFIXES = ["文明", "帝国", "集团", "组织", "族群", "舰队", "联盟", "公司"]
```

## B3. Translation policy

| ZH | VI |
|---|---|
| `文明` | nền văn minh |
| `帝国` | đế quốc |
| `集团` | tập đoàn / nhóm |
| `组织` | tổ chức |
| `舰队` | hạm đội |
| `族群` | tộc quần / chủng quần |
| `星际公民` | công dân liên sao |

## B4. Proper-name detection

```text
本菲尔文明
→ nền văn minh Benfell

归星
→ Quy Tinh / hành tinh Quy, protected place

光电科技
→ Quang Điện Khoa Kỹ / Công nghệ Quang Điện, organization
```

---

# PART C — Auction / Price / Exchange Grammar

## C1. Vấn đề

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

## C2. Auction frame

| Pattern | VI |
|---|---|
| `起拍价为 X` | giá khởi điểm là X |
| `报价 X` | ra giá X |
| `竞价到 X` | đấu giá lên đến X |
| `以 X 成交` | chốt giao dịch ở mức X |
| `买下 X` | mua lại X |
| `卖出 X` | bán ra X |
| `价值 X` | trị giá X |

## C3. Rule

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

## C4. Number format

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

# PART D — Lifeform Grade Classifier

## D1. Pattern

```text
A级生命体
B级生命体
高级生命体
超级生命体
两个A级生命体的战斗
E+级以下的攻击
```

## D2. Rule

```python
LIFEFORM_GRADE_PATTERN = r"([SABCDEF][+\-]?级|高级|超级|低级|中级)\s*生命体"
```

## D3. VI

| ZH | VI |
|---|---|
| `A级生命体` | sinh mệnh thể cấp A |
| `B级生命体` | sinh mệnh thể cấp B |
| `高级生命体` | sinh mệnh thể cao cấp |
| `超级生命体` | sinh mệnh thể siêu cấp |
| `两个A级生命体` | hai sinh mệnh thể cấp A |

## D4. Combat/casualty context

```text
两个A级生命体的战斗，不小心波及了一颗生命星球
→ trận chiến của hai sinh mệnh thể cấp A vô tình lan đến một hành tinh có sự sống
```

---

# PART E — Gene / Virus / Module Item Chain

## E1. Corpus examples

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

## E2. Ontology

```json
{
  "bio_item_suffixes": ["病毒", "原液", "血清", "药剂", "基因链", "基因", "模组"],
  "ability_suffixes": ["天赋", "能力", "技能", "模块", "插件"],
  "equipment_suffixes": ["殖装", "装甲", "护盾", "武器", "推进器"]
}
```

## E3. Translation examples

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

## E4. Guard

Nếu có bracket `【维罗妮卡模组】` hoặc `【泰坦殖装】`, protect toàn span.

---

# PART F — Armor / Equipment / Mod Install Grammar

## F1. Pattern

```text
塞进了【泰坦殖装】中
融入了他的躯体中
安装在装甲上
加载到系统中
提取出来
融合完成
同步完成
```

## F2. Transfer

| ZH | VI |
|---|---|
| `塞进 X 中` | nhét vào trong X |
| `融入 X 中` | hòa vào trong X |
| `安装在 X 上` | lắp lên X |
| `加载到 X 中` | tải vào X |
| `提取出来` | rút ra / trích xuất ra |
| `同步完成` | đồng bộ hoàn tất |
| `融合完成` | dung hợp hoàn tất |

## F3. Rule

```python
EQUIP_INSTALL_VERBS = ["塞进", "融入", "安装", "加载", "装载", "插入", "提取", "融合", "同步"]
```

**Directional complement xử lý theo domain kỹ thuật:**
- `出来` trong `提取出来` → `rút ra`, không phải chỉ `đi ra`.
- `进去` trong `塞进去` → `nhét vào`.

---

# PART G — Coordinate / Jump / Navigation Expressions

## G1. Pattern

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

## G2. Mapping

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

## G3. Rule

```python
if verb in ["前往", "到达", "返航"] and object is space_place:
    use navigation translation
```

---

# PART H — Radiation / Hazard Zone

## H1. Pattern

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

## H2. Translation

| ZH | VI |
|---|---|
| `重度辐射区` | khu vực bức xạ nặng |
| `辐射污染` | ô nhiễm bức xạ |
| `污染区域` | khu vực ô nhiễm |
| `变异` | biến dị |
| `感染` | lây nhiễm / bị nhiễm |
| `病毒泄露` | rò rỉ virus |
| `危险区域` | khu vực nguy hiểm |

## H3. Passive-result patterns

```text
被感染
→ bị nhiễm

被辐射污染
→ bị ô nhiễm bức xạ

受到辐射影响
→ chịu ảnh hưởng bức xạ
```

---

# PART I — System Upgrade / Power Sync Grammar

## I1. Corpus pattern

```text
分身已死亡…分身回收成功…发现宿主初次生命跃迁完成，分身实力同步中…需要时间––720小时
分身实力同步完成后，系统将会进行升级。
一号分身的实力同步快要结束
```

## I2. Rule

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

## I3. Duration converter

```text
720小时
→ 720 giờ / 30 ngày

是否 auto-normalize 720h → 30 ngày phụ thuộc config:
- preserve_source_unit=True: 720 giờ
- humanize_duration=True: 30 ngày
```

---

# PART J — Probability / Risk / Evaluation Phrases

## J1. Pattern

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

## J2. Mapping

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

## J3. Rule

```python
if "概率/成功率/几率" nearby:
    convert 成 as probability ratio
else:
    use general ratio converter
```

---

# PART K — News / Report / Public Opinion Discourse

## K1. Pattern

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

## K2. Translation

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

## K3. Discourse frame

```text
最近比较火热的新闻，是...
→ tin tức khá nóng gần đây là...

主要是...
→ chủ yếu là...

当然，如果仅仅是这件事本身，还不足以...
→ đương nhiên, nếu chỉ là bản thân chuyện này thì vẫn chưa đủ để...
```

---

# PART L — Administrative / Census / Investigation Grammar

## L1. Pattern

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

## L2. Translation

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

## L3. Rule

```python
ADMIN_INVESTIGATION_TERMS = {...}
```

Need classify `普查老爷子` as title/nickname phrase:
- `普查老爷子` → “ông lão tổng điều tra” / protected alias if repeated.

---

# PART M — Bracketed Named Title / Chapter Title Preservation

## M1. Chapter titles

```text
第101章 【漫威】世界
第106章 【黯星】和帝国舰队
第108章 【岩狮基因链】
第197章 好猛，好爽！
```

## M2. Rule

```python
if line startswith 第N章:
    parse as ChapterTitle
    translate title separately
    preserve bracketed entity
```

## M3. Examples

```text
第101章 【漫威】世界
→ Chương 101: Thế giới [Marvel]

第106章 【黯星】和帝国舰队
→ Chương 106: [Ám Tinh] và Hạm đội Đế Quốc

第108章 【岩狮基因链】
→ Chương 108: [Chuỗi gen Sư Tử Đá]
```

---

# PART N — `对...产生作用/影响` Frame

## N1. Pattern

```text
对如今的李宇产生作用
对战斗产生影响
对外公布
对抗分身
对他无用
```

## N2. Classifier

| Pattern | VI |
|---|---|
| `对 X 产生作用` | có tác dụng đối với X |
| `对 X 产生影响` | gây ảnh hưởng đến X |
| `对外公布` | công bố ra bên ngoài |
| `对抗 X` | đối kháng/chống lại X |
| `对 X 无用` | vô dụng với X |

## N3. Rule

```python
if token == "对":
    if next == "外" and later("公布"): fixed "công bố ra bên ngoài"
    elif later("产生作用"): frame_effect_on
    elif later("产生影响"): frame_impact_on
    else: preposition "đối với/với"
```

---

# PART O — `以...作为原材料/基础` Frame

## O1. Pattern

```text
以破碎母盒作为原材料打造
以X作为基础
以X为核心
以X作为能源
```

## O2. VI

```text
lấy Hộp Mẹ vỡ làm nguyên liệu để chế tạo
lấy X làm nền tảng
lấy X làm hạch tâm
lấy X làm nguồn năng lượng
```

## O3. Rule

```python
Pattern: 以 [NP] 作为 [ROLE] V
Output: lấy [NP] làm [ROLE] để V
```

---

# PART P — Large-scale Casualty / Population Number Converter

## P1. Pattern

```text
超过千万级别的人员伤亡
数十万生命
上百万公民
近百艘战舰
```

## P2. Rule

| ZH | VI |
|---|---|
| `超过千万级别` | vượt mức hàng chục triệu |
| `数十万` | mấy chục vạn / hàng trăm nghìn |
| `上百万` | hơn một triệu |
| `近百艘` | gần trăm chiếc |
| `人员伤亡` | thương vong về người |

## P3. Converter

```python
if number_prefix in ["数", "上", "近", "超过"]:
    classify as approximate_large_number
```

---

# PART Q — Percent / Probability / Success-rate

## Q1. Pattern

```text
成功率百分之八十
概率不到百分之一
几率极低
八成把握
```

## Q2. Rule

```text
成功率百分之八十
→ tỷ lệ thành công 80%

概率不到百分之一
→ xác suất chưa đến 1%

八成把握
→ nắm chắc khoảng 80%
```

---

# PART R — Colloquial Reaction / Meme Chapter Titles

## R1. Pattern

```text
好猛，好爽！
暴打小朋友
你是内奸吧
惊喜原来是
```

## R2. Rule

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

# PART S — Data files cần bổ sung

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

# PART T — Implementation Roadmap v17

## Sprint V17-A — Space/Civilization Entity

- [ ] `space_entity_detector.py`
- [ ] `polity_faction_detector.py`
- [ ] `space_fleet_suffixes.json`
- [ ] `polity_faction_suffixes.json`
- [ ] Tests: 80 cases

## Sprint V17-B — Auction/Resource/Price

- [ ] `auction_price_parser.py`
- [ ] `currency_large_number_converter.py`
- [ ] `auction_price_patterns.json`
- [ ] Tests: 80 cases

## Sprint V17-C — Grade/Lifeform/Bio Item

- [ ] `lifeform_grade_classifier.py`
- [ ] `bio_gene_item_parser.py`
- [ ] `equipment_install_rule.py`
- [ ] Tests: 100 cases

## Sprint V17-D — Navigation/Hazard/System Upgrade

- [ ] `navigation_space_rule.py`
- [ ] `radiation_hazard_rule.py`
- [ ] `system_upgrade_rule.py`
- [ ] Tests: 100 cases

## Sprint V17-E — Discourse/Frame Completion

- [ ] `news_public_opinion_rule.py`
- [ ] `admin_investigation_rule.py`
- [ ] `dui_effect_frame_rule.py`
- [ ] `yi_material_source_rule.py`
- [ ] Tests: 100 cases

## Sprint V17-F — Chapter Title / Colloquial

- [ ] `chapter_title_parser.py`
- [ ] `bracketed_title_preserver.py`
- [ ] `colloquial_chapter_title_map.json`
- [ ] Tests: 80 cases

---

# PART U — Test Matrix v17

## U1. Space entity

```python
V17_SPACE_TESTS = [
    ("黑瞳舰队", "Hạm đội Hắc Đồng"),
    ("帝国舰队", "hạm đội Đế Quốc"),
    ("生命星球", "hành tinh có sự sống"),
    ("本菲尔文明之战", "trận chiến văn minh Benfell"),
]
```

## U2. Auction/price

```python
V17_AUCTION_TESTS = [
    ("起拍价为三十亿星币", "giá khởi điểm là 30 tỷ tinh tệ"),
    ("以五千万星币成交", "chốt giao dịch ở mức 50 triệu tinh tệ"),
    ("报价一百万星币", "ra giá 1 triệu tinh tệ"),
]
```

## U3. Lifeform grade

```python
V17_LIFEFORM_TESTS = [
    ("A级生命体", "sinh mệnh thể cấp A"),
    ("两个A级生命体的战斗", "trận chiến của hai sinh mệnh thể cấp A"),
    ("E+级以下的攻击", "công kích từ cấp E+ trở xuống"),
]
```

## U4. Bio item

```python
V17_BIO_ITEM_TESTS = [
    ("病毒原液", "nguyên dịch virus"),
    ("岩狮基因链", "chuỗi gen Sư Tử Đá"),
    ("维罗妮卡模组", "mô-đun Veronica"),
    ("泰坦殖装", "thực trang Titan"),
]
```

## U5. System upgrade

```python
V17_SYSTEM_UPGRADE_TESTS = [
    ("分身实力同步中，需要时间720小时", "đang đồng bộ thực lực phân thân, cần 720 giờ"),
    ("系统将会进行升级", "hệ thống sẽ tiến hành nâng cấp"),
    ("分身回收成功", "thu hồi phân thân thành công"),
]
```

## U6. Effect/material frame

```python
V17_FRAME_TESTS = [
    ("对如今的李宇产生作用", "có tác dụng đối với Lý Vũ hiện nay"),
    ("以破碎母盒作为原材料打造", "lấy Hộp Mẹ vỡ làm nguyên liệu để chế tạo"),
]
```

## U7. Large casualty

```python
V17_POPULATION_NUMBER_TESTS = [
    ("超过千万级别的人员伤亡", "thương vong vượt mức hàng chục triệu người"),
    ("近百艘战舰", "gần trăm chiến hạm"),
]
```

## U8. Chapter title

```python
V17_TITLE_TESTS = [
    ("第101章 【漫威】世界", "Chương 101: Thế giới [Marvel]"),
    ("第106章 【黯星】和帝国舰队", "Chương 106: [Ám Tinh] và Hạm đội Đế Quốc"),
    ("第197章 好猛，好爽！", "Chương 197: Mạnh dữ, đã quá!"),
]
```

---

# PART V — Rule Priority cập nhật sau v17

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

# PART W — Acceptance Metrics v17

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

# PART X — Merge Strategy

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

# END OF v17
