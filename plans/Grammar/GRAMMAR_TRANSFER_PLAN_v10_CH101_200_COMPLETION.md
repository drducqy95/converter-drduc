# GRAMMAR_TRANSFER_PLAN_v10 — Ch101–200 Corpus Completion

**Repo:** `converter-drduc`  
**Corpus:** `Hồng Hoang Lịch_Zhttty.html` — chương 101 đến 200  
**Ngày cập nhật:** 2026-04-25  
**Mục tiêu:** tiếp tục hoàn thiện thuật toán Grammar Transfer ZH→VI dựa trên 100 chương tiếp theo, bổ sung các cấu trúc còn thiếu sau v9.

---

## 0. Phạm vi phân tích

Đã đọc và tách nội dung từ:

- `chapter-101` — `第十六章：设想`
- đến `chapter-200` — `第二十八章：夜晚`

Thống kê nội bộ:

```text
Chapters analyzed: 100
Chinese text size: ~348,408 chars
Sentence-like units: ~5,625
```

100 chương này mở rộng mạnh so với 100 chương đầu ở các mảng:

1. **Logic nghị luận / giải thích dài**: `所谓`, `也就是说`, `换句话说`, `之所以...是因为`, `以...为`.
2. **Câu điều kiện nhiều tầng**: `若是`, `如果`, `一旦`, `只有...才`, `只要...就`, `除非...否则`, `无论/不管...都`.
3. **Bị động/cấu trúc cổ văn**: `由...所...`, `为...所...`, `被...所...`, `受到/遭到`.
4. **Danh ngữ thuật ngữ dài không có 的**: tên thế lực, pháp môn, đạo cụ, hệ thống, công trình, chủng tộc.
5. **Dạng “system/game/strategy”**: `副本`, `玩家`, `BOSS`, `奖励点数`, `支线剧情`, `首测资格`, `血族转职`, `公众副本`.
6. **Số dạng kỹ thuật/quân sự/game**: thế hệ máy bay, thời hạn đếm ngược, cấp bậc, số nhiều chương gộp, tỷ lệ, thời lượng, phạm vi địa lý/chiến trường.

---

## 1. Kết quả tần suất các cấu trúc nổi bật

### logical_condition
| Pattern | Count in ch101–200 |
|---|---:|
| `若是/若/如果` | 456 |
| `一旦` | 75 |
| `只要...就` | 68 |
| `只有...才` | 61 |
| `除非...否则` | 8 |
| `无论/不管...都/也` | 73 |

### contrast_concession
| Pattern | Count in ch101–200 |
|---|---:|
| `即便/即使/哪怕...也` | 21 |
| `虽然/虽...但/却` | 260 |
| `不是/并非...而是` | 58 |
| `与其...不如` | 4 |
| `倒不如/反倒` | 70 |

### scope_quant
| Pattern | Count in ch101–200 |
|---|---:|
| `凡是...都` | 6 |
| `每当/每次` | 12 |
| `所有/一切/全部` | 640 |
| `任何` | 175 |
| `其余/剩下` | 188 |

### formal_classical
| Pattern | Count in ch101–200 |
|---|---:|
| `所谓` | 73 |
| `名为` | 20 |
| `称为/叫做` | 43 |
| `之所以...是因为` | 7 |
| `以...为` | 323 |
| `由...所` | 22 |
| `为...所` | 162 |
| `非...不可/不得` | 12 |

### modal_eval
| Pattern | Count in ch101–200 |
|---|---:|
| `足以` | 53 |
| `难以` | 7 |
| `得以` | 4 |
| `不得不` | 25 |
| `没必要/不必` | 27 |
| `可以说` | 18 |
| `看起来/似乎/仿佛` | 353 |

### disposal_conversion
| Pattern | Count in ch101–200 |
|---|---:|
| `将...化为/变成/视为/当成` | 36 |
| `把...当成/变成/化为` | 5 |
| `化为/转化为` | 85 |

### dialogue_rhetoric
| Pattern | Count in ch101–200 |
|---|---:|
| `不是吗` | 10 |
| `难道/莫非` | 47 |
| `呢?` | 143 |
| `省略号` | 985 |
| `内心括号` | 68 |


---

## 2. Ví dụ thực tế rút ra từ chương 101–200

### 凡是...都
- Ch101 `第十六章：设想`: 凡是欺骗，凡是离间，凡是挑拨都必有理由，而我的提议与做法，并没有任何如此做的理由，不是吗？
- Ch121 `第三十六章：军队纵横`: 而职业者去到高阶，从三阶开始，就具备着一种特殊能力，可以在一定范围内，一定限度下，将一股力量细微化进行攻击，用战士的话来说，这可以称为隔山打牛，用刺客的话来说，这叫做心眼刺击，每个职业都有不同的解释，但是究其根本，这就是传奇四阶的入微之始啊，凡是去到了四阶职业者的强者们，他们都可以本能的将自己的力量入微到极精细层面上，有点类似高等地精科学家们提到的矢量操纵，…
- Ch155 `第二十八章：领地琐事与布局开始`: 抹去了洪荒万族中第六，第七，第八，第九一共四个种族，更是连可能出现的第三皇都给抹去，甚至因为某种特殊异常，凡是被一起玩完吧抹去的族群或者个人，连信息都会被从记忆中抹除消失，这简直像是神话一样。

### 只有...才
- Ch101 `第十六章：设想`: ” 众人都是不言语，但是也并没有多说什么，阿莫尔依然笑着说道：“我这些天所观察到的，各位是人类仅存的精英了，而你们所听到的信息是，这个世界正在腐化，只有打败并且封印三魔神，这个世界才会得救，对吗？
- Ch102 `第十七章：签了`: 直到这次他与一群魔法师发生激战，同时使用出了八卦符文中的三枚，分别是震，艮，巽三枚，其爆发出来的威力直接将五层魔法塔给轰平了，而那群魔法师中，只有三阶亚龙魔法师，及两个魔法学徒幸运的活了下来，其余魔法师连个渣都没剩下，吴明这才恍然惊觉自己的八卦符文使用威力实在是太大了，按道理来说，估计他需要去到金丹期，不管是真元力，还是计算力，逻辑力，解析力等等，才能够爆发…
- Ch102 `第十七章：签了`: 我拥有解析力魔法天赋，这是亿万魔法学徒中都无一人的超级天赋，而逻辑族最出名的就是解析力，诞生于这一族的奥术师道路，也只有拥有解析力的人才可以走上，这些信息应该都不是隐秘信息才对，你作为金河城唯二的三阶魔法师，我不信你就不知道。

### 除非...否则
- Ch113 `第二十八章：感官`: ” 说到这里，骷髅魔法师的声音变得了高昂而尖锐，她说道：“可是除非他能够走到尽头，走到终点，半神都才只是起点而已，除非他能够成为圣位，永恒而不朽，否则在他身旁越是接近的人越是危险，万一他失败了，在他身边的所有人都被埋没，被葬送，所以……我想离他远一些，再远一些就好了。
- Ch129 `第二章：不疯魔不成活`: 除非是有某披风光头的血统，否则他怎么可能兑换？
- Ch145 `第十八章：轮回世界倒计时`: 娱乐这个词对于这个时代来说真的是超级奢侈品，从吴明所知道的一些社会分析文中，所谓的娱乐，必然是需要和平环境下才会诞生的东西，这并不要求一定是高科技时代，古代照样有娱乐，甚至奴隶社会都有娱乐，娱乐的必要条件只有一个，那就是活得下去，而且活得不错，若是放到古代的农民身上，除非是大统一的强大盛世，而且经济还不错，风调雨顺，否则那个时代的农民那来什么娱乐，晚上关灯后…

### 即便/哪怕...也
- Ch102 `第十七章：签了`: 什么嘛，不就是打了个响指做提示，顺便出力大了一些罢了…… 吴明现在可以一次性操纵八卦符文中的三枚，而其中威力最大的乾坤两枚符文还无法操纵，但是即便如此，吴明也没想到八卦符文的威力会如此之大，或者说他用出来的威力会如此之大。
- Ch104 `第十九章：地底裂缝`: 倒不是飞行器的速度太慢，按照吴明估计，这飞行器的速度大约和地球世界的飞机差不多，而且可持续飞行时间更长了几倍，中途根本不必加油什么的，一天一夜的飞行，在地球上足以绕地球两圈了，但是洪荒大陆实在太大了，即便是这样的速度，吴明要到目的地也需要一天一夜，二十多个小时。
- Ch108 `第二十三章：目标`: 这液体一落入地面，立刻就化为烟气消失不见，但是就在这液体出现的一瞬间，在场的所有死亡骑士全都狂咽口水，本能的，他们全部都想要这液体，哪怕一滴也可以，这液体似乎对他们来说是极大极大的补品，甚至是天财地宝。

### 与其...不如
- Ch122 `第三十七章：下一个战场`: ” 这一次是战争回答道：“英灵骑士普遍都是传奇，也有极弱小的英灵骑士是三阶巅峰，也有极强的英灵骑士是半神，而英灵骑士对所在地点的要求极大，若是在其成名战与死亡战的地方，其实力会得到大幅度的增长，或者在其传说最为盛行的地方也同样如此，与其说英灵骑士是不死诸族之一，倒不如说英灵骑士更像是圣位身边的圣灵，是通过战争本源，混合着人们的愿力而生成的特殊种。
- Ch131 `第四章：起始`: 与其怕着等死，等待不知道什么时候会落到头顶上的核平，倒不如奋勇而起，将可以伤害我的敌人全部杀死，你觉得呢？
- Ch141 `第十四章：奖励点数约定与三大灾`: ） 吴明在机舱中，拿了一只笔和一张纸，开始不停的在上面写着什么，而整个贵宾机舱里，也只有路西法一个人敢留在这里，不过与其说是敢，倒不如说她和其余所有人的世界观中，也唯有传奇才有资格与传奇结交，路西法是一个强大的传奇强者，而吴明能够打败并且俘虏她，同时还击杀了另一个传奇，那怕他的位阶不是传奇，所有人也依然会将他当成传奇看待。

### 以...为
- Ch101 `第十六章：设想`: ” “而另一个提议，那‘外人’的提议，则是世界已经危急到了最后关头，即将被腐化，所以你们必须抛弃人民，孤身立刻前进，以自己的生命去硬拼三魔神，最好的结果自然是你们获胜，三魔神都被杀死，但是最大的可能则是你们和三魔神同归于尽……我想，这也是你们为什么在这地狱门口暂且停下来的原因，谁获利，谁就嫌疑重大，你们也有自己的疑惑，不是吗？
- Ch101 `第十六章：设想`: ” 阿莫尔说道：“你们可以击杀真名魔物，或者高等魔物，然后凝聚它们的灵魂，化为各种武器，铠甲，魔法器具，虽然数量不多，而且品质相差不齐，但那些正是我们需要的，我们提供你们人民所需要的一切必需品，而你们则付给我们这些，这场交易才可以长期实行下来，你们觉得如何？
- Ch102 `第十七章：签了`: 所以唯一的答案就只有一个了，吴明所修行的功法有问题，这个名为中央戊土厚德诀的功法有问题。

### 由/为...所
- Ch101 `第十六章：设想`: ” 那个穿着铠甲的男性就说道：“正是如此，这不单单是由‘外人’所告诉我们的，我们中的预言师，智者，以及我们自己都发现，这个世界正在被腐化，而其根源就来自于三魔神，而打败和封印他们，才能够拯救这个世界，这是事实。
- Ch101 `第十六章：设想`: 我总结一下，你们的办法却是可行，打败三魔神，并且封印起来，若是做不到彻底杀死，这算是目前为止最好的治本办法，但是问题就在于这个，目前世界正在被腐朽，你们的人民，你们所守护的人，他们被各地蜂拥出现的怪物所袭击，所以生产也已经停止，那怕没停止，其实也消耗得差不多了……所以我的办法是暂时治标，那就是由我们提供粮食与治疗药物，各种物资，而你们暂停下用尽一切去打败三魔…
- Ch101 `第十六章：设想`: ” 阿莫尔说道：“你们可以击杀真名魔物，或者高等魔物，然后凝聚它们的灵魂，化为各种武器，铠甲，魔法器具，虽然数量不多，而且品质相差不齐，但那些正是我们需要的，我们提供你们人民所需要的一切必需品，而你们则付给我们这些，这场交易才可以长期实行下来，你们觉得如何？

### 足以/难以/得以
- Ch102 `第十七章：签了`: ” 亚龙人魔法师脸色一僵，好半天后才说道：“奥术师这么厉害吗……难怪是超凡道路第一了……这且不说，你要禁锢我到什么时候，杀又不杀，放又不放，我可以用我的魔法本源起誓，绝对不会说出你与袭击者的关系，放了我，我会付出足以匹配我俘虏的财富与知识来！
- Ch104 `第十九章：地底裂缝`: 倒不是飞行器的速度太慢，按照吴明估计，这飞行器的速度大约和地球世界的飞机差不多，而且可持续飞行时间更长了几倍，中途根本不必加油什么的，一天一夜的飞行，在地球上足以绕地球两圈了，但是洪荒大陆实在太大了，即便是这样的速度，吴明要到目的地也需要一天一夜，二十多个小时。
- Ch105 `第二十章：天启`: ” 四名死亡骑士的眼神略微有了些波动，其中一个看起来是银色发丝，模样很是英俊的死亡骑士道：“十年前，奥兰里就是三阶魔法师了，十年时间虽然不足以让他升阶，但是他至少也算是资深的三阶魔法师，而你……如果那魔法长袍没骗人，你估计是二阶魔法师吧？

### 看起来/似乎/仿佛
- Ch101 `第十六章：设想`: ” 阿莫尔点点头，继续说道：“确实，这是事实，而这腐化其实是深渊化，三魔神来自于一个叫做无底深渊的地方，那里才是它们的家乡，而离开无底深渊后，它们的实力大幅度下降，连最核心的能力似乎都无法使用，所以它们要么回归深渊，要么就将所处之地变成深渊，这就是它们的做法，而这个世界正在逐渐的深渊化。
- Ch101 `第十六章：设想`: ” 那名仿佛骷髅一样的男子沉默了半响，这才说道：“那你们能够提供的粮食有多少？
- Ch101 `第十六章：设想`: ” 众人默然无语半响，仿佛骷髅的男子拿出了他的骷髅法杖，魔法长袍女性拿出了魔法长杖，野蛮人举起了他的双手巨斧，铠甲男则拿出了他的剑盾…… “那不妨一起吧，异界来客，我们早就看那熔炉不顺眼了，就让我们陪同你们一起去捣毁这个鬼东西好了！

### 将...化为/视为
- Ch101 `第十六章：设想`: ” 阿莫尔点点头，继续说道：“确实，这是事实，而这腐化其实是深渊化，三魔神来自于一个叫做无底深渊的地方，那里才是它们的家乡，而离开无底深渊后，它们的实力大幅度下降，连最核心的能力似乎都无法使用，所以它们要么回归深渊，要么就将所处之地变成深渊，这就是它们的做法，而这个世界正在逐渐的深渊化。
- Ch108 `第二十三章：目标`: ” 四人接着都签下了契约，一旦签下，上面的符文都开始了闪烁，最夸张的是八枚八卦符文同时具现，将这羊皮纸化为了颗颗光粒，就此消失在了虚无之中，一瞬间，吴明与四名死亡骑士，甚至是那些被代表的死亡骑士，都有了一种奇特的感觉，那就是多了一道枷锁，一道契印。
- Ch113 `第二十八章：感官`: 父亲并没有回来，我们的父亲就这样消失了，明明说好回来时，会带回来我们最喜欢吃的生命树果，可是父亲就这样一去不回了，我们只听到亲眷旁支们的话语，说什么我们的父亲冒险成性，说什么我们的父亲害了一整个团的人，说什么我们的父亲引来了灾祸，说什么我们父亲害了一整个家族……” “我们的财富被剥夺了，我们的母亲被逼死了，甚至连父亲留下的魔法法式都被抢走，父亲留下的魔法器具…


---

# 3. Các cấu trúc ngữ pháp còn thiếu cần bổ sung

## 3.1 `凡是...都...` — universal conditional / scope

### Dạng ZH

```text
凡是 X 都 Y
凡是 X, Y
凡是 A，凡是 B，凡是 C 都 Y
```

### Chuyển VI

```text
Phàm là X thì đều Y
Hễ X thì đều Y
Bất cứ X nào cũng Y
```

### Rule đề xuất

```python
class RuleUniversalFanshi:
    trigger = "凡是"

    def transform(span):
        # if repeated 凡是 A，凡是 B，凡是 C 都...
        # keep rhetorical parallelism:
        # "phàm là A, phàm là B, phàm là C đều..."
        if repeated_fanshi(span):
            return parallel_translate("phàm là", "đều")
        return "hễ/phàm là" + X + "thì đều" + Y
```

### Test bắt buộc

```python
("凡是欺骗，凡是离间，凡是挑拨都必有理由",
 "Phàm là lừa gạt, phàm là ly gián, phàm là xúi giục thì đều tất có lý do")
```

---

## 3.2 `只有...才...` và `只要...就...` — phân biệt điều kiện cần / đủ

### Vấn đề

Hai cấu trúc này có bề mặt gần giống, nhưng nghĩa khác:

```text
只有 A 才 B  →  chỉ khi A thì mới B      # necessary condition
只要 A 就 B  →  chỉ cần A thì B          # sufficient condition
```

### Rule

```python
if pattern == "只有...才":
    insert_before_A("chỉ khi")
    insert_before_B("thì mới")
elif pattern == "只要...就":
    insert_before_A("chỉ cần")
    insert_before_B("thì")
```

### Anti-confusion

Không dịch cả hai thành “chỉ cần”.

### Test

```python
("只有打败并且封印三魔神，这个世界才会得救",
 "Chỉ khi đánh bại và phong ấn Tam Ma Thần, thế giới này mới được cứu")

("只要当他们不存在不就好了吗？",
 "Chỉ cần xem như họ không tồn tại chẳng phải là được rồi sao?")
```

---

## 3.3 `除非...否则...` — unless / otherwise

### Dạng

```text
除非 A，否则 B
除非 A，不然 B
除非 A，要不然 B
```

### Chuyển VI

```text
Trừ phi A, nếu không thì B
Trừ khi A, bằng không B
```

### Rule

```python
detect 除非 as condition_start
detect 否则/不然/要不然 as else_marker
return "Trừ phi/trừ khi" + A + ", nếu không thì" + B
```

### Test

```python
("除非他能够成为圣位，否则在他身旁越是接近的人越是危险",
 "Trừ phi hắn có thể trở thành Thánh vị, nếu không thì người càng ở gần bên hắn càng nguy hiểm")
```

---

## 3.4 `无论/不管...都/也...` — no matter / regardless

### Dạng

```text
无论如何都...
无论 A 还是 B 都...
不管 A 还是 B 都...
不管怎么样，也...
```

### Chuyển VI

```text
Dù thế nào cũng...
Bất kể A hay B đều...
Cho dù A hay B thì cũng...
```

### Rule

```python
if marker in ["无论", "不管"]:
    if has_or_pair("还是", "或者"):
        return "bất kể" + A + "hay" + B + "thì đều/cũng" + C
    else:
        return "dù/bất kể" + X + "cũng" + C
```

---

## 3.5 `即便/即使/哪怕...也...` — concessive even if

### Dạng

```text
即便如此，X 也 Y
即使 A，也 B
哪怕 A，也 B
```

### VI

```text
Cho dù như vậy, X vẫn/cũng Y
Ngay cả khi A, cũng B
Dù chỉ A, cũng B
```

### Rule chọn “vẫn” hay “cũng”

```python
if main_clause_has_adversative_or_negative:
    use "vẫn"
else:
    use "cũng"
```

### Test

```python
("即便如此，吴明也没想到八卦符文的威力会如此之大",
 "Dù vậy, Ngô Minh cũng không ngờ uy lực của Bát Quái phù văn lại lớn đến thế")
```

---

## 3.6 `虽然/虽...但/却/但是...` — concessive contrast

### Dạng

```text
虽然 A，但是 B
虽 A，却 B
虽然 A，但 B
```

### VI

```text
Tuy A, nhưng B
Dù A, nhưng B
```

### Rule

- Nếu `虽然` đứng đầu câu: dùng “Tuy/Dù”.
- Nếu `却` trong vế B: ưu tiên “lại/vậy mà”.
- Không lặp “nhưng nhưng”.

```python
if has_suiran and has_danshi:
    drop literal "但是" if already inserted "nhưng"
if has_que:
    render_que = "lại" or "vậy mà"
```

---

## 3.7 `不是/并非...而是...` — correction contrast

### Dạng

```text
不是 A，而是 B
并不是 A，而是 B
并非 A，而是 B
```

### VI

```text
Không phải A, mà là B
Chẳng phải A, mà là B
```

### Rule

```python
negated_part = span_between(不是/并非, 而是)
corrected_part = span_after(而是)
return "không phải" + A + ", mà là" + B
```

### Test

```python
("不是他要闹事，而是事情太多太乱向他涌来",
 "Không phải hắn muốn gây chuyện, mà là quá nhiều chuyện hỗn loạn ập đến với hắn")
```

---

## 3.8 `与其...不如...` — preference contrast

### Dạng

```text
与其 A，不如 B
与其说 A，倒不如说 B
```

### VI

```text
Thà B còn hơn A
Nói là A, chẳng bằng nói là B
```

### Rule

```python
if pattern == "与其说 A 不如说 B":
    return "Nói là A, chẳng bằng nói là B"
else:
    return "Thà" + B + "còn hơn" + A
```

### Test

```python
("与其怕着等死，倒不如奋勇而起",
 "Thà dũng cảm đứng lên còn hơn sợ hãi chờ chết")
```

---

## 3.9 `既...又... / 既是...又非是...` — dual attribute / paradox

### Dạng

```text
既像是狼，又像是熊
既是生命，又非是生命
既 A 又 B
```

### VI

```text
vừa A, vừa B
vừa là A, lại vừa không phải A
```

### Rule

```python
if has_negative_second_part:
    return "vừa là" + A + ", lại vừa không phải" + A
else:
    return "vừa" + A + ", vừa" + B
```

### Test

```python
("满是既是生命，又非是生命的存在",
 "đầy những tồn tại vừa là sinh mệnh, lại vừa không phải sinh mệnh")
```

---

## 3.10 `以...为...` — take X as Y / use X as Y / regard X as Y

### Dạng trong corpus

```text
以吴明为中心
以自己的生命去硬拼
以天皇那样的圣位顶端
以...为基础
以...为目标
以...为代价
```

### Phân loại

| Pattern | VI |
|---|---|
| `以 X 为中心` | lấy X làm trung tâm |
| `以 X 为基础` | lấy X làm nền tảng |
| `以 X 为目标` | lấy X làm mục tiêu |
| `以 X 为代价` | lấy X làm cái giá / với cái giá là X |
| `以 X 去/来 V` | dùng/lấy X để V |
| `以 X 之名` | nhân danh X |

### Rule

```python
class RuleYiWei:
    def classify(y_object):
        if y_object in ["中心", "基础", "目标", "核心"]:
            return "lấy X làm Y"
        if y_object in ["代价", "牺牲"]:
            return "với cái giá là X"
        if next_verb_after_span:
            return "dùng/lấy X để V"
```

### Test

```python
("以吴明为中心，八卦符文开始浮现在了地面上",
 "Lấy Ngô Minh làm trung tâm, Bát Quái phù văn bắt đầu hiện lên trên mặt đất")
```

---

## 3.11 `由/为...所...` — formal passive

### Dạng

```text
由 A 所 V
为 A 所 V
被 A 所 V
```

### VI

```text
do A V
bị/được A V
```

### Rule chọn “do / bị / được”

```python
if marker == "由":
    return "do" + agent + verb
elif verb_sentiment_negative:
    return "bị" + agent + verb
elif verb_sentiment_positive:
    return "được" + agent + verb
else:
    return "do/bị" depending context
```

### Quan trọng

Không được dịch máy móc:

```text
为人所知 → được mọi người biết đến
为...所困 → bị ... vây khốn
为...所用 → được/bị ... sử dụng
```

Thêm vào `sentiment_lexicon.json`:

```json
{
  "positive": ["认可", "接纳", "拯救", "保护", "信任", "重用", "赏识"],
  "negative": ["困", "困住", "袭击", "腐化", "污染", "控制", "吞噬", "杀死", "俘虏"],
  "neutral_passive": ["称为", "视为", "认为", "记载", "发现", "提及"]
}
```

---

## 3.12 `受到/遭到 + N/V` — event passive

### Dạng

```text
受到影响
受到控制
遭到侵袭
遭到攻击
遭到压制
```

### VI

```text
chịu ảnh hưởng
bị khống chế
bị xâm kích
bị tấn công
bị áp chế
```

### Rule

```python
if verb in neutral_effect:
    "chịu" + N
elif verb in negative:
    "bị" + V/N
else:
    "chịu/bị"
```

### Test

```python
("似乎受到了某些程序的控制",
 "dường như bị một số chương trình nào đó khống chế")
```

---

## 3.13 `足以/难以/得以/可以说` — modal evaluation

### Mapping

| ZH | VI |
|---|---|
| `足以 V` | đủ để V |
| `难以 V` | khó mà V / khó V |
| `得以 V` | có thể / được V |
| `可以说` | có thể nói là |

### Rule

```python
if token == "足以":
    insert "đủ để"
elif token == "难以":
    insert "khó mà"
elif token == "得以":
    insert "có thể/được"
elif phrase == "可以说":
    insert "có thể nói là"
```

### Test

```python
("光是文字就足以让人感觉到热血沸腾",
 "chỉ riêng chữ viết thôi cũng đủ khiến người ta cảm thấy nhiệt huyết sôi trào")
```

---

## 3.14 `不得不 / 不由得 / 忍不住` — involuntary / forced action

### Mapping

| ZH | VI |
|---|---|
| `不得不 V` | không thể không V / đành phải V |
| `不由得 V` | bất giác V |
| `忍不住 V` | không nhịn được mà V |

### Rule

```python
if context_formal_or_strategy:
    "không thể không"
elif context_narrative_action:
    "đành phải"
elif token == "不由得":
    "bất giác"
elif token == "忍不住":
    "không nhịn được mà"
```

---

## 3.15 `看起来/听起来/似乎/仿佛/好像` — evidential / seeming

### Mapping

| ZH | VI |
|---|---|
| `看起来` | trông có vẻ / nhìn qua |
| `听起来` | nghe có vẻ |
| `似乎` | dường như |
| `仿佛` | như thể |
| `好像` | hình như / giống như |

### Rule

Cần tách 2 loại:

```text
看起来 + NP/ADJ      → trông có vẻ ...
看起来 + clause     → xem ra ...
似乎 + clause       → dường như ...
仿佛 + NP/clause    → như thể ...
```

### Test

```python
("看起来似乎受到的影响不大",
 "trông có vẻ như ảnh hưởng phải chịu không lớn")
```

---

## 3.16 `将...化为/变成/视为/作为/当成` — conversion / regard-as disposal

### Dạng

```text
将 X 化为 Y
将 X 变成 Y
将 X 视为 Y
将 X 作为 Y
把 X 当成 Y
```

### VI

```text
biến X thành Y
xem X là Y
coi X như Y
lấy X làm Y
```

### Rule

```python
if verb in ["化为", "变成", "转化为"]:
    return "biến" + X + "thành" + Y
elif verb in ["视为", "当成"]:
    return "xem/coi" + X + "là/như" + Y
elif verb == "作为":
    return "lấy" + X + "làm" + Y
```

### Test

```python
("凝聚它们的灵魂，化为各种武器，铠甲，魔法器具",
 "ngưng tụ linh hồn của chúng, biến thành các loại vũ khí, áo giáp, pháp khí ma pháp")
```

---

## 3.17 `所谓 / 名为 / 称为 / 叫做` — definition/name construction

### Mapping

| ZH | VI |
|---|---|
| `所谓 X` | cái gọi là X |
| `名为 X` | tên là X / được gọi là X |
| `称为 X` | gọi là X |
| `叫做 X` | gọi là X |

### Rule

```python
if "所谓" before technical noun:
    "cái gọi là" + term
elif "名为" in NP:
    "mang tên" + term
elif "称为/叫做":
    "gọi là" + term
```

### Entity interaction

Nếu sau `名为/称为/叫做` là protected entity, không tách token:

```text
名为中央戊土厚德诀的功法
→ công pháp mang tên Trung Ương Mậu Thổ Hậu Đức Quyết
```

---

## 3.18 `对于/对...来说` — topic frame

### Dạng

```text
对于 A 来说，B
对 A 来说，B
对于 A 而言，B
```

### VI

```text
Đối với A, B
Với A mà nói, B
```

### Rule

```python
extract frame_span between 对于/对 and 来说/而言
move to sentence front as "Đối với X,"
```

---

## 3.19 `从...到... / 由...到...` — range and transition

### Dạng

```text
从 A 到 B
由 A 到 B
从三阶开始
从地面到天空
从普通到超凡
```

### VI

```text
từ A đến B
bắt đầu từ A
từ A chuyển sang B
```

### Rule

```python
if has_two_endpoints:
    "từ A đến B"
elif pattern == "从 X 开始":
    "bắt đầu từ X"
elif semantic_transition:
    "từ A chuyển thành/đến B"
```

### Number interaction

`从三阶开始` phải giữ `三阶` là level/rank, không dịch thành “ba bậc” chung chung:

```text
从三阶开始 → bắt đầu từ tam giai / cấp ba
```

Tùy register:
- xianxia/classical: `tam giai`
- modern/game: `cấp 3`

---

# 4. Bổ sung thuật toán số cho chương 101–200

## 4.1 Số thứ tự dạng chapter/subtitle gộp

Trong file có tiêu đề dạng:

```text
第三十四，三十五章
第四十五，六章
第五十，五十一章
```

### Rule

```python
detect_chapter_range_title:
    第 + NUM_A + ， + NUM_B + 章
    第 + NUM_A + ， + SHORT_NUM_B + 章
```

### VI

```text
Chương 34, 35
Chương 45, 46
Chương 50, 51
```

Nếu `SHORT_NUM_B` là `六` sau `四十五`, suy ra `四十六`.

---

## 4.2 Số thế hệ / đời máy / military generation

Các chương sau 100 có nhiều cụm như:

```text
第五代主战斗机
一代机
二代机
第几代
```

### Rule

```python
if NUM + 代 + 机/战斗机/产品:
    translate as "thế hệ NUM" or "đời NUM"
```

### VI

```text
第五代主战斗机 → chiến đấu cơ chủ lực thế hệ thứ năm
一代机兑换开放 → mở đổi máy thế hệ đầu
```

---

## 4.3 Số cấp bậc/rank: 阶 / 级 / 位 / 层

### Context-aware mapping

| ZH | Domain | VI |
|---|---|---|
| `三阶魔法师` | magic/rpg | ma pháp sư tam giai / cấp ba |
| `一阶基因锁` | infinite/game | khóa gen tầng một / nhất giai gene lock |
| `四阶职业者` | professional rank | chức nghiệp giả tứ giai |
| `半神` | cultivation/divine | bán thần |
| `圣位` | cosmology | Thánh vị |

### Rule

```python
if suffix in ["阶", "级", "层", "位"]:
    domain = infer_domain(neighbor_terms)
    if domain in ["xianxia", "cultivation", "fantasy"]:
        use Sino-Vietnamese rank
    elif domain in ["game", "system"]:
        use "cấp"
```

---

## 4.4 Countdown / time deadline / dungeon schedule

Patterns xuất hiện nhiều từ ch101–200:

```text
倒计时
十天之后
二十四小时
每二十四小时
五分钟内
一天一夜
二十多个小时
```

### Rule

```python
if has 倒计时:
    render as "đếm ngược"
if NUM + 时间单位 + 内:
    "trong vòng NUM unit"
if 每 + NUM + 时间单位:
    "mỗi NUM unit"
if NUM + 多 + 时间单位:
    "hơn NUM unit"
```

### VI

```text
二十多个小时 → hơn hai mươi giờ
五分钟内 → trong vòng năm phút
每二十四小时 → mỗi hai mươi bốn giờ
一天一夜 → một ngày một đêm
```

---

## 4.5 Approximation and uncertainty

### Patterns

```text
约莫在五百只左右
二十多个小时
几乎
差不多
大约
至少
最多
近三米
```

### Rule

```python
约莫/大约 + NUM + 左右 → khoảng NUM
NUM + 多 → hơn NUM
近 + NUM → gần NUM
至少 NUM → ít nhất NUM
最多 NUM → nhiều nhất NUM
差不多 NUM → xấp xỉ NUM
```

---

## 4.6 Large-scale military/geographic numbers

### Examples

```text
横跨洪荒大陆三分之一的地域
巨大百倍以上
排名前一百
上千年之久
```

### Rule

```python
三分之一 → một phần ba
百倍以上 → hơn gấp trăm lần
前一百 → top 100 / một trăm hạng đầu
上千年 → hơn nghìn năm
```

### Domain rendering

- prose narration: “hơn nghìn năm”
- system/stat: “> 1.000 năm” only if source is UI/stat block.

---

## 4.7 Resource/accounting numbers

Patterns tiếp tục từ v7–v9:

```text
奖励点数
支线剧情
兑换
权限
首测资格
副本
BOSS
NPC
```

### Rule

Không dùng number converter đơn thuần cho toàn cụm. Cần protected compound:

```python
protect_terms = [
    "奖励点数", "支线剧情", "首测资格", "公众副本",
    "副本倒计时", "血族转职", "BOSS", "NPC"
]
```

### VI glossary

| ZH | VI |
|---|---|
| `奖励点数` | điểm thưởng |
| `支线剧情` | tình tiết nhánh |
| `首测资格` | tư cách thử nghiệm đầu tiên / suất thử nghiệm đầu |
| `副本` | phó bản |
| `公众副本` | phó bản công cộng |
| `BOSS` | BOSS |
| `NPC` | NPC |

---

# 5. Bổ sung Entity/Term protection từ chương 101–200

## 5.1 Nhóm term cần protect

```json
{
  "spaces_and_systems": [
    "主神空间", "轮回世界", "试炼空间", "公众副本", "主神"
  ],
  "factions_and_races": [
    "商业联盟", "高等地精", "地灵族", "天蛇族", "血族", "精灵族",
    "远古兽人族", "逻辑族", "四狱联军"
  ],
  "power_system": [
    "圣位", "半神", "传奇", "三阶", "四阶", "奥术师", "魔法师",
    "基因锁", "金丹期", "筑基"
  ],
  "artifacts_and_tech": [
    "先天灵宝", "先天至宝", "轮回盘", "不周山", "缩爆弹", "地爆弹",
    "洪荒级缩爆弹导弹", "八卦符文"
  ],
  "places": [
    "苍白之地", "幽冥地府", "洪荒大陆", "银色大地", "地狱门口"
  ]
}
```

## 5.2 Thuật toán Entity-Aware Nominal Chain

Chương 101–200 có rất nhiều chuỗi dài không dùng `的`:

```text
洪荒级缩爆弹导弹系列
血族转职利弊分析一二帖
奖励点数使用计划白皮书
野外公众副本
阴影之雾
主神空间开启
```

### Rule

```python
def parse_nominal_chain(tokens):
    # 1. protect known entity/term spans
    # 2. detect suffix head:
    #    系列 / 计划 / 白皮书 / 分析 / 副本 / 会议 / 空间 / 世界 / 阵 / 刀 / 镜
    # 3. right-headed conversion for VI:
    #    [modifier chain] + [head]
    #    VI: head + modifier(s)
```

### Ví dụ

```text
奖励点数使用计划白皮书
→ sách trắng về kế hoạch sử dụng điểm thưởng

血族转职利弊分析一二帖
→ bài phân tích một hai điều về lợi hại của việc chuyển chức Huyết tộc

洪荒级缩爆弹导弹系列
→ dòng tên lửa Súc Bạo Đạn cấp Hồng Hoang
```

---

# 6. Tích hợp vào architecture hiện tại

## 6.1 Thêm detector mới

```text
src/grammar/construction_detector.py
```

Bổ sung methods:

```python
detect_universal_fanshi()
detect_only_if_cai()
detect_as_long_as_jiu()
detect_unless_fouze()
detect_no_matter()
detect_concessive_even_if()
detect_not_a_but_b()
detect_yuqi_buru()
detect_ji_you()
detect_yi_wei()
detect_formal_passive_suo()
detect_modal_evaluation()
detect_evidential_seeming()
detect_definition_naming()
detect_topic_frame_duiyu()
detect_range_cong_dao()
```

## 6.2 Thêm transfer rules

```text
src/grammar/transfer_rules/
├── rule_logic_condition.py
├── rule_concession_contrast.py
├── rule_formal_passive_suo.py
├── rule_yi_wei.py
├── rule_modal_evaluation.py
├── rule_evidential.py
├── rule_definition_naming.py
├── rule_range_transition.py
└── rule_nominal_chain_terms.py
```

## 6.3 Thêm number context classifier

```text
src/grammar/number_context.py
```

```python
class NumberContext(Enum):
    CARDINAL = "cardinal"
    ORDINAL = "ordinal"
    RANK_LEVEL = "rank_level"
    GAME_RESOURCE = "game_resource"
    TIME_DURATION = "time_duration"
    DEADLINE = "deadline"
    APPROXIMATION = "approximation"
    FRACTION = "fraction"
    MULTIPLIER = "multiplier"
    GENERATION = "generation"
    CHAPTER_TITLE = "chapter_title"
    MILITARY_TECH = "military_tech"
```

## 6.4 Mở rộng `NumberConverter.try_convert()`

Không thay thế module cũ. Chỉ thêm pre-pass:

```python
span = number_context_detector.detect(sentence, i)
if span:
    return convert_by_context(span)
else:
    return existing_number_converter.try_convert(sentence, i)
```

---

# 7. Test suite bổ sung cho v10

## 7.1 `tests/test_grammar/test_logic_condition_v10.py`

```python
@pytest.mark.parametrize("zh,vi", [
    ("只有打败并且封印三魔神，这个世界才会得救",
     "Chỉ khi đánh bại và phong ấn Tam Ma Thần, thế giới này mới được cứu"),
    ("只要当他们不存在不就好了吗？",
     "Chỉ cần xem như họ không tồn tại chẳng phải là được rồi sao?"),
    ("除非他能够成为圣位，否则他身旁的人越是接近越是危险",
     "Trừ phi hắn có thể trở thành Thánh vị, nếu không thì người bên cạnh hắn càng ở gần càng nguy hiểm"),
    ("无论如何他都不可能放弃他们",
     "Dù thế nào hắn cũng không thể bỏ rơi bọn họ"),
])
```

## 7.2 `tests/test_grammar/test_contrast_v10.py`

```python
@pytest.mark.parametrize("zh,vi", [
    ("不是他要闹事，而是事情太多太乱向他涌来",
     "Không phải hắn muốn gây chuyện, mà là quá nhiều chuyện hỗn loạn ập đến với hắn"),
    ("与其怕着等死，倒不如奋勇而起",
     "Thà dũng cảm đứng lên còn hơn sợ hãi chờ chết"),
    ("既是生命，又非是生命",
     "vừa là sinh mệnh, lại vừa không phải sinh mệnh"),
])
```

## 7.3 `tests/test_grammar/test_formal_passive_v10.py`

```python
@pytest.mark.parametrize("zh,vi", [
    ("他们被各地蜂拥出现的怪物所袭击",
     "Bọn họ bị quái vật từ khắp nơi ùn ùn xuất hiện tập kích"),
    ("似乎受到了某些程序的控制",
     "dường như bị một số chương trình nào đó khống chế"),
    ("为人所知",
     "được mọi người biết đến"),
])
```

## 7.4 `tests/test_grammar/test_number_context_v10.py`

```python
@pytest.mark.parametrize("zh,vi", [
    ("第五代主战斗机", "chiến đấu cơ chủ lực thế hệ thứ năm"),
    ("二十多个小时", "hơn hai mươi giờ"),
    ("五分钟内", "trong vòng năm phút"),
    ("三分之一的地域", "một phần ba khu vực"),
    ("上千年之久", "suốt hơn nghìn năm"),
    ("第三十四，三十五章", "Chương 34, 35"),
])
```

## 7.5 `tests/test_grammar/test_nominal_chain_v10.py`

```python
@pytest.mark.parametrize("zh,vi", [
    ("奖励点数使用计划白皮书",
     "sách trắng về kế hoạch sử dụng điểm thưởng"),
    ("血族转职利弊分析一二帖",
     "bài phân tích một hai điều về lợi hại của việc chuyển chức Huyết tộc"),
    ("洪荒级缩爆弹导弹系列",
     "dòng tên lửa Súc Bạo Đạn cấp Hồng Hoang"),
])
```

---

# 8. Sprint bổ sung sau v9

## Sprint 7 — Logic/Condition Transfer

```text
S7.1 detect_only_if_cai()
S7.2 detect_as_long_as_jiu()
S7.3 detect_unless_fouze()
S7.4 detect_no_matter()
S7.5 detect_fanshi_universal()
S7.6 unit tests 40 câu
```

## Sprint 8 — Formal/Expository Grammar

```text
S8.1 detect_yi_wei()
S8.2 detect_definition_naming()
S8.3 detect_duiyu_frame()
S8.4 detect_range_transition()
S8.5 detect_modal_evaluation()
S8.6 unit tests 40 câu
```

## Sprint 9 — Passive/Conversion/Evidential

```text
S9.1 rule_formal_passive_suo
S9.2 rule_event_passive_shoudao/zaodao
S9.3 rule_conversion_huawei/biancheng/shixwei
S9.4 rule_evidential_seeming
S9.5 unit tests 40 câu
```

## Sprint 10 — Number/Term/Title Hardening

```text
S10.1 number_context_detector
S10.2 generation/military-tech numbers
S10.3 chapter-title grouped ordinal numbers
S10.4 large-scale fraction/multiplier/range
S10.5 nominal chain protected term parser
S10.6 regression: existing NumberConverter tests
```

---

# 9. Acceptance Criteria v10

```text
[ ] Logic condition constructions accuracy >= 85%
[ ] Formal passive `由/为/被...所` accuracy >= 80%
[ ] `以...为` classification accuracy >= 80%
[ ] Number context conversion accuracy >= 90%
[ ] Protected nominal-chain term accuracy >= 85%
[ ] No regression: 98 existing tests pass
[ ] Feature flag off: exact old behavior
[ ] Feature flag on: fallback_safe never crashes on ch101–200
```

---

# 10. Ưu tiên triển khai ngay

Nếu cần chọn ít nhưng hiệu quả cao, ưu tiên:

```text
P0  只有...才 / 只要...就 / 无论...都 / 即便...也
P0  为/由/被...所 passive
P0  以...为 classification
P1  所谓/名为/称为 definition
P1  足以/难以/不得不/忍不住 modal
P1  Number context: 阶/级/代/多/左右/以内/每
P2  Nominal chain parser cho technical title dài
```
