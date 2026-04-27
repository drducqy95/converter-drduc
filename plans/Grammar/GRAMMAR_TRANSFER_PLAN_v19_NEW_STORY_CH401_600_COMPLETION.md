# GRAMMAR_TRANSFER_PLAN_v19_NEW_STORY_CH401_600_COMPLETION

**Repo:** `converter-drduc`  
**Kế thừa:** `v14 + v15 + v16 + v17 + v18`  
**Corpus:** `Còn Tốt Phân Thân Có Thể Đưa Lên Vạn Giới_Đoàn Hựu Viên.txt`  
**Phạm vi:** chương 401–600  
**Ngày:** 2026-04-25  
**Phiên bản:** v19.0 — Cosmic Artifact / Faction War / Symbiote-BioTech / Name Scanner Completion  

---

## 0. Executive Summary

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

## 1. Corpus Signals chương 401–600

### 1.1 Tần suất và domain signals

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

### 1.2 Chương tiêu đề có nhiều entity seed

Chương 401–600 có mật độ tiêu đề chứa entity rất cao. Vì vậy **ChapterTitleEntitySeeder** phải được nâng cấp thành nguồn glossary chính, không chỉ là phụ trợ.

---

# PART A — Cosmic Artifact Scanner

## A1. Problem

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

## A2. Ontology

```json
{
  "cosmic_artifact": ["无限手套", "力量宝石", "现实宝石", "火种源碎片", "昆塔莎的生命权杖"],
  "super_weapon": ["死星", "帝死星", "特殊图纸死星"],
  "divine_weapon": ["弑神手枪", "冈戈尔之刃", "邪恶王冠"],
  "ability_item": ["蜘蛛感应", "伤害无效化", "混沌魔法", "物品打造"],
  "character_item_alias": ["黑寡妇"]
}
```

## A3. Translation policy

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

## A4. Scanner rule

```python
if bracketed_item:
    exact_glossary_first()
    if contains artifact suffix: classify ARTIFACT
    if contains ability suffix: classify ABILITY
    if contains "死星": link to DeathStarEntity
```

---

# PART B — Artifact Lifecycle Grammar

## B1. Patterns

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

## B2. Rule mapping

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

## B3. Lifecycle state record

```python
@dataclass
class EntityLifecycle:
    entity_id: str
    states: list[str]  # created, awakened, upgraded, unlocked, deployed, destroyed
    first_seen_chapter: int
    last_seen_chapter: int
```

## B4. Example

```text
点化【死星】
→ điểm hóa [Death Star]

【帝死星】
→ [Đế Tử Tinh]  # alias/evolved form of Death Star
```

---

# PART C — Symbiote / BioTech Entity Chain

## C1. Patterns

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

## C2. Ontology

```json
{
  "symbiote": ["共生殖装", "殖装", "共生体"],
  "gene_chain": ["血雷龙基因链", "天神基因链", "灰烬之泰坦基因链"],
  "evolution": ["进化", "三次进化", "变异", "强化"],
  "bio_mech": ["异形机械军团", "机械章鱼", "泰坦殖装"]
}
```

## C3. Translation

| ZH | VI |
|---|---|
| `共生殖装` | thực trang cộng sinh / giáp sinh thể cộng sinh |
| `血雷龙基因链` | chuỗi gen Huyết Lôi Long |
| `天神基因链` | chuỗi gen Thiên Thần |
| `灰烬之泰坦基因链` | chuỗi gen Titan Tro Tàn |
| `异形机械军团` | quân đoàn cơ giới Dị Hình |
| `三次进化` | tiến hóa lần ba |

## C4. Rule

```python
if span.endswith("基因链"):
    classify BIO_GENE_CHAIN
elif span.endswith("殖装"):
    classify SYMBIOTE_EQUIPMENT
elif span.endswith("军团") and contains bio/mech term:
    classify BIOMECH_ARMY
```

---

# PART D — War-scale Faction Composition

## D1. Patterns

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

## D2. Faction composition rule

```python
Pattern: [modifier/faction] + [联合] + [舰队/军团/小队]
```

## D3. Examples

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

## D4. Hierarchy link

```python
EntityHierarchy.link("金狮军团", parent="星耀帝国", type="military_unit")
EntityHierarchy.link("黑瞳舰队", parent="黯星/议会?", type="fleet")
```

---

# PART E — Cosmic Battle Action Grammar

## E1. Combat verbs

```python
COSMIC_COMBAT_VERBS = [
    "围攻", "镇压", "碾压", "俘获", "袭杀", "伏击", "总攻",
    "撕裂", "崩掉", "攻破", "夺取", "屠杀", "轰击", "扫荡",
    "点化", "封锁", "锁定", "反向锁定", "压制", "偷袭"
]
```

## E2. Pattern: `一枪/一拳/一击 + result`

```text
一枪崩掉万神殿
→ một phát súng bắn sập Vạn Thần Điện

一拳，你拿什么挡
→ một quyền này, ngươi lấy gì mà đỡ?

一击秒杀
→ một đòn miểu sát
```

## E3. Rule

```python
Pattern: 一 + weapon/action_measure + V_RESULT + O
Output: một + unit_vi + V_RESULT_vi + O
```

## E4. Special idiom

```text
认真一拳
→ Một Quyền Nghiêm Túc / cú đấm nghiêm túc
```

If chapter-title or known meme from One Punch style → protect as meme ability.

---

# PART F — Transformation / Form State

## F1. Patterns

```text
沙巴克形态
红莲状态
赛亚状态
混沌爆发
帝死星
机械神通
```

## F2. Rule

```python
if span.endswith(("形态", "状态")):
    classify FORM_STATE
elif span.endswith("爆发"):
    classify BURST_STATE
elif span.endswith("神通"):
    classify ABILITY_TECHNIQUE
```

## F3. Translation

```text
沙巴克形态
→ hình thái Shabak

混沌爆发
→ Hỗn Độn bộc phát

机械神通显威
→ thần thông cơ giới hiển uy
```

---

# PART G — Mythic/Divine Title Scanner

## G1. Patterns

```text
清虚道德天尊
万神殿
弑神手枪
恐虐
恐虐意识体
渊首
伊斯特拉
```

## G2. Rule

```python
if span contains ["天尊", "神", "神殿", "弑神", "意识体"]:
    classify MYTHIC_DIVINE
```

## G3. Translation

| ZH | VI |
|---|---|
| `清虚道德天尊` | Thanh Hư Đạo Đức Thiên Tôn |
| `万神殿` | Vạn Thần Điện / Pantheon |
| `弑神手枪` | Súng Ngắn Thí Thần |
| `恐虐` | Khorne / Khủng Ngược |
| `恐虐意识体` | ý thức thể Khorne |
| `渊首` | Uyên Thủ |
| `伊斯特拉` | Istra / Y Tư Đặc Lạp |

## G4. Franchise-sensitive name style

Nếu `恐虐` thuộc Warhammer, dùng glossary `Khorne`. Nếu không có glossary, fallback Hán Việt.

---

# PART H — Force/Cosmic Identity Grammar

## H1. Pattern

```text
我，即是原力！
```

## H2. Rule

```python
Pattern: 我，即是 X
Output: Ta, chính là X!
```

## H3. Related

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

# PART I — Progress Bar / Build System Grammar

## I1. Patterns

```text
进度条堆满
基因链进度又要拉满了
纲要解锁
物品打造
系统升级
功能解锁
```

## I2. Translation

| ZH | VI |
|---|---|
| `进度条堆满` | thanh tiến độ được lấp đầy |
| `进度拉满` | kéo tiến độ đầy |
| `又要拉满了` | lại sắp được kéo đầy |
| `纲要解锁` | cương yếu được mở khóa |
| `物品打造` | chế tạo vật phẩm |
| `功能解锁` | mở khóa chức năng |

## I3. Rule

```python
if span contains "进度" and "满":
    classify PROGRESS_BAR
```

---

# PART J — Strategy/Intrigue Script Grammar

## J1. Patterns

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

## J2. Translation

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

## J3. Idiom guard

Protect as idiom before word-level grammar.

---

# PART K — Media / Public Opinion / Spotlight

## K1. Patterns

```text
舆论影响
星际震动
聚光灯下的黑瞳舰队
演讲
采访
声明
事件纷沓
```

## K2. Translation

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

# PART L — Proper-name Scanner 401–600

## L1. New personal names / aliases

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

## L2. Organization / faction / group names

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

## L3. Artifact / ability / item names

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

## L4. Entity scanner upgrades

### Stage order

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

### Scoring additions

```python
if appears in chapter title: +5
if bracketed: +5
if has artifact suffix 宝石/手套/权杖/之刃/手枪: +4
if has faction suffix 方舟/舰队/军团/圣殿/研究所: +4
if appears near verbs 说/道/皱眉/看向/沉默: +2
if appears near lifecycle verbs 点化/出世/解锁/诞生: +3
if entity has evolved alias pattern X -> 帝X: +3
```

## L5. Alias collision examples

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

# PART M — Bracketed Possessive Item Parser

## M1. Patterns

```text
【昆塔莎的生命权杖】
【冈戈尔之刃】
【钢铁侠的装备升级卡】
【灰烬之泰坦基因链】
```

## M2. Rule

```python
if bracketed and contains 的/之:
    parse internal possessive but keep item as one protected span
```

## M3. Translation

```text
【昆塔莎的生命权杖】
→ [Quyền Trượng Sinh Mệnh của Quintessa]

【冈戈尔之刃】
→ [Lưỡi Dao Gongor]

【灰烬之泰坦基因链】
→ [Chuỗi gen Titan Tro Tàn]
```

---

# PART N — Dramatic Imperative / Combat Speech

## N1. Patterns

```text
出来吧，【帝死星】
给我去杀！
向您问好
拿下，镇压
开打开打
```

## N2. Translation

| ZH | VI |
|---|---|
| `出来吧，X` | ra đây đi, X |
| `给我去杀` | đi giết cho ta |
| `向您问好` | gửi lời chào đến ngài |
| `拿下，镇压` | bắt lấy, trấn áp |
| `开打开打` | đánh thôi, đánh thôi |

## N3. Rule

Imperative detection:

```python
if sentence startswith imperative verb or contains "给我去":
    tone = COMMAND
```

---

# PART O — Contrast Retort Rule

## O1. Pattern

```text
我知道，但我不同意
```

## O2. Translation

```text
Ta biết, nhưng ta không đồng ý.
```

## O3. Generalization

```python
Pattern: 我知道/我明白/我懂 + 但/但是/不过 + 我不...
```

---

# PART P — Counterfactual / Role Swap Frame

## P1. Pattern

```text
如果我俩角色互换
```

## P2. Translation

```text
nếu hai chúng ta đổi vai cho nhau
```

## P3. Rule

```python
Pattern: 如果/若是 + A/B + 角色互换
→ nếu A và B đổi vai cho nhau
```

---

# PART Q — Idiom Guard Additions

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

# PART R — Author-note-in-title stripping

## R1. Problem

Một số tiêu đề có phần tác giả xen vào:

```text
第476章 徒手撕裂世界壁垒！（感谢本草纲目...
第504章 申饬（月初求月票，对了，好像能说...
第587章 信任基础（呜呜呜，不好意思，迟到...
```

## R2. Rule

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

# PART S — Data files cần bổ sung

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

# PART T — Implementation Roadmap v19

## Sprint V19-A — Cosmic Artifact + Lifecycle

- [ ] `cosmic_artifact_scanner.py`
- [ ] `artifact_lifecycle_tracker.py`
- [ ] `bracketed_possessive_item_parser.py`
- [ ] data: `cosmic_artifact_glossary.json`
- [ ] Tests: 120 cases.

## Sprint V19-B — Symbiote/BioTech + Transformation

- [ ] `symbiote_biotech_parser.py`
- [ ] `gene_chain_state_tracker.py`
- [ ] `transformation_state_rule.py`
- [ ] Tests: 100 cases.

## Sprint V19-C — War/Faction + Cosmic Combat

- [ ] `war_faction_composition_parser.py`
- [ ] `cosmic_combat_action_rule.py`
- [ ] `dramatic_imperative_rule.py`
- [ ] Tests: 120 cases.

## Sprint V19-D — Proper-name Scanner Expansion

- [ ] Add chapter 401–600 seed names.
- [ ] Add alias lifecycle resolver.
- [ ] Add faction hierarchy links.
- [ ] Add evolved artifact alias.
- [ ] Export candidate review report.
- [ ] Tests: 150 cases.

## Sprint V19-E — Discourse/Idiom/Title Cleanup

- [ ] `strategy_intrigue_idiom_guard.py`
- [ ] `media_public_opinion_rule.py`
- [ ] `counterfactual_role_swap_rule.py`
- [ ] `author_note_title_filter.py`
- [ ] Tests: 100 cases.

---

# PART U — Test Matrix v19

## U1. Cosmic artifact

```python
V19_ARTIFACT_TESTS = [
    ("【无限手套】", "[Găng Tay Vô Cực]"),
    ("【力量宝石】", "[Viên đá Sức Mạnh]"),
    ("【现实宝石】", "[Viên đá Hiện Thực]"),
    ("【帝死星】", "[Đế Tử Tinh]"),
    ("【昆塔莎的生命权杖】", "[Quyền Trượng Sinh Mệnh của Quintessa]"),
]
```

## U2. Lifecycle

```python
V19_LIFECYCLE_TESTS = [
    ("点化【死星】", "điểm hóa [Death Star]"),
    ("【死星】出世", "[Death Star] xuất thế"),
    ("【共生殖装】诞生", "[Thực Trang Cộng Sinh] ra đời"),
    ("冈戈尔之刃的进阶形态", "hình thái tiến giai của Lưỡi Dao Gongor"),
]
```

## U3. Symbiote/BioTech

```python
V19_BIOTECH_TESTS = [
    ("【共生殖装】", "[Thực Trang Cộng Sinh]"),
    ("血雷龙基因链", "chuỗi gen Huyết Lôi Long"),
    ("天神基因链", "chuỗi gen Thiên Thần"),
    ("灰烬之泰坦基因链", "chuỗi gen Titan Tro Tàn"),
]
```

## U4. War/faction

```python
V19_FACTION_TESTS = [
    ("反抗组织联合舰队", "hạm đội liên hợp của tổ chức phản kháng"),
    ("金狮军团", "Quân đoàn Kim Sư"),
    ("使徒小队", "tiểu đội Sứ Đồ"),
    ("异形机械军团", "quân đoàn cơ giới Dị Hình"),
]
```

## U5. Combat action

```python
V19_COMBAT_TESTS = [
    ("一枪崩掉万神殿", "một phát súng bắn sập Vạn Thần Điện"),
    ("一击秒杀", "một đòn miểu sát"),
    ("认真一拳", "Một Quyền Nghiêm Túc"),
    ("拿下，镇压", "bắt lấy, trấn áp"),
]
```

## U6. Identity / dramatic speech

```python
V19_SPEECH_TESTS = [
    ("我，即是原力！", "Ta, chính là Force!"),
    ("出来吧，【帝死星】", "ra đây đi, [Đế Tử Tinh]"),
    ("我知道，但我不同意", "Ta biết, nhưng ta không đồng ý"),
    ("如果我俩角色互换", "nếu hai chúng ta đổi vai cho nhau"),
]
```

## U7. Idiom/title

```python
V19_IDIOM_TESTS = [
    ("一举三得", "một công ba việc"),
    ("一脉相承", "cùng một mạch truyền thừa"),
    ("弄巧成拙", "khéo quá hóa vụng"),
    ("人赃俱获", "bắt được cả người lẫn tang vật"),
]
```

## U8. Name scanner

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

# PART V — Rule Priority cập nhật sau v19

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

# PART W — Acceptance Metrics v19

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

# PART X — Merge Strategy

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

# END OF v19
