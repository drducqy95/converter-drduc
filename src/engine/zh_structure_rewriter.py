#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pre-translation Chinese Structure Rewriter.

Applies structural transformations on the Chinese source string *before* Trie lookup,
converting Left-Branching Chinese grammar (Modifier + Head) to Right-Branching
Vietnamese grammar (Head + Modifier) implicitly by reversing Chinese tokens and
injecting Vietnamese linking markers.
"""

from __future__ import annotations
import re

# ==========================================
# Category 1: Modifier + 的 + HeadNoun
# ==========================================

# 1A: Specific Verb-Prefix Modifiers (身穿...的, 穿着...的)
_ZH_C1A_RCM = re.compile(
    r"((?:身穿|穿着?|戴着?|背着?|拿着?|带着?|披着?)(?:[\u4e00-\u9fff\d]{1,8}))的"
    r"(男子|女子|少年|老太|老人|男孩|女孩|男人|女人|大汉|少女|青年|人|保安|学生|孩子|婴儿)(?!的)"
)

# 1B: Adjectives + 的 + Noun (Expanded)
_ZH_C1B_ADJ_NOUN = re.compile(r"(惨白腐烂|白发|黑色|白色|红色|蓝色|极其微小|瘦骨嶙峋|棱角分明|惨白)(?:的?)(双手|老太|眼球|风衣|寿衣|瞳孔|手|脸|粉末|大痣|珠子|白骨)")

# 1C: Specific Relative Clauses (Shielded from generic rules)
_ZH_C1C_CLAUSE = re.compile(r"(跪在那里|来不及收手|微微挺起|被烫|拿着|穿黑色风衣|穿着白色寿衣)(?:的?)(黑衣男子|白衣老太|老人|门|张陈|男子|老太)")

# 1D: Aggressive Generic Modifier (But exclude Locative/Correlatives)
# Exclude phrases starting with 传|从|在|向|朝 or ending with 传|传出|传来
_ZH_C1D_GENERIC_DE = re.compile(
    r"(?<!从)(?<!在)(?<!向)(?<!对)(?<!朝)"     # Negative Lookbehind (don't break prepositions)
    r"([\u4e00-\u9fff\d]{1,8})"              # Modifier
    r"(?<!传)(?<!传出)(?<!传来)"             # Negative Lookbehind inside mod? No.
    r"的"                                     # Linker
    r"([\u4e00-\u9fff]{2,8})"                # Head Noun
    r"(?![传来|传出|传响起])"                # Negative Lookahead
)

def apply_cat1_modifiers(text: str) -> str:
    # Order: Specific -> Generic
    text = _ZH_C1C_CLAUSE.sub(r"\2 \1", text)
    text = _ZH_C1A_RCM.sub(r"\2 \1", text)
    text = _ZH_C1B_ADJ_NOUN.sub(r"\2 \1", text)
    text = _ZH_C1D_GENERIC_DE.sub(r"\2 \1", text)
    return text

# ==========================================
# Category 2: Possessive Owner + 的 + Noun
# ==========================================
_ZH_C2_OWNER = r"(?:(?<!其)他|她|我|你|自己|老太|老人|男子|张陈|男孩|女孩|胖子)"
_ZH_C2_NOUN = r"身躯|身体|腿|屁股|脚|手|手腕|脖子|勃颈处|脸|面部|眼睛|眼球|头发|心脏|胸膛|情绪|坟|影子|速度|嘴巴"
_ZH_C2_POSSESSIVE = re.compile(f"({_ZH_C2_OWNER})的({_ZH_C2_NOUN})")

def apply_cat2_possessive(text: str) -> str:
    # 老太的身躯 -> 身躯 của 老太
    # The literal " của " will pass straight through the RBMT engine.
    return _ZH_C2_POSSESSIVE.sub(r"\2 của \1", text)


# ==========================================
# Category 3: Color + Noun Swap
# ==========================================
_ZH_C3_COLORS = r"黑色|白色|红色|蓝色|黄色|灰色|金色|银色"
_ZH_C3_NOUNS = r"风衣|寿衣|高跟鞋|粉末|大痣|珠子|眼球|白骨"

_ZH_C3_COLOR_NOUN = re.compile(f"({_ZH_C3_COLORS})(?:偏?)({_ZH_C3_NOUNS})")

def apply_cat3_colors(text: str) -> str:
    # 黑色风衣 -> 风衣黑色 -> trie writes `áo gió màu đen`
    return _ZH_C3_COLOR_NOUN.sub(r"\2\1", text)


# ==========================================
# Category 4 & 5: 把 / 被
# ==========================================
# 4. Object Fronting (把你给抓 -> mẹ bắt mày)
# 5. Passive (被一下咬断 -> bị cắn đứt)

def apply_cat45_babei(text: str) -> str:
    # 把 Object Verb
    text = re.compile(r"把你给抓").sub("抓你", text)
    text = re.compile(r"把屁股给(.*?)看看").sub(r"给\1看看屁股", text)
    text = re.compile(r"把话(说清楚)").sub(r"\1话", text)
    
    # 被 Agent Verb -> We just convert `被` to `bị ` and let trie handle translation
    text = re.compile(r"被([^了断过\s]+)([咬断抓杀打骂])").sub(r"bị \1\2", text)
    
    return text


# ==========================================
# Category 6: Result Complements
# ==========================================
_ZH_C6_COMPLEMENTS = [
    (re.compile(r"([\u4e00-\u9fff])了下来"), r"\1 ra đây"),
    (re.compile(r"吓出(.*)一身冷汗"), r"dọa \1 toát một thân mồ hôi lạnh"),
    (re.compile(r"站起身"), r"đứng dậy"),
    (re.compile(r"转过身(的?)"), r"xoay người \1"),
    (re.compile(r"停住(了?)车"), r"dừng xe \1 lại"),
]
def apply_cat6_complements(text: str) -> str:
    for pat, rep in _ZH_C6_COMPLEMENTS:
        text = pat.sub(rep, text)
    return text


# ==========================================
# Category 7: Classifiers Map
# ==========================================
_ZH_NUM_MAP = {
    "一": "một", "两": "hai", "三": "ba", "五": "năm", "十": "mười"
}

_ZH_C7_CLASSIFIERS = [
    (re.compile(r"([一两三四五六七八九十百千万0-9]+)座(小?山)"), "ngọn"),
    (re.compile(r"([一两三四五六七八九十百千万0-9]+)座(墓碑)"), "tấm"),
    (re.compile(r"([一两三四五六七八九十百千万0-9]+)块(墓碑)"), "tấm"),
    (re.compile(r"([一两三四五六七八九十百千万0-9]+)根(中?性?笔)"), "cây"),
    (re.compile(r"([一两三四五六七八九十百千万0-9]+)只([\u4e00-\u9fff]{0,3}手)"), "bàn"),
    (re.compile(r"([一两三四五六七八九十百千万0-9]+)个(小时)"), "tiếng"),
]

def apply_cat7_classifiers(text: str) -> str:
    for pat, cl_vi in _ZH_C7_CLASSIFIERS:
        def replacer(m):
            num_zh = m.group(1)
            vi_num = _ZH_NUM_MAP.get(num_zh, num_zh)
            noun_zh = m.group(2)
            # Fix duplicate unit for temporal (e.g. 6年 -> 6 năm 年)
            if cl_vi == "năm" and noun_zh == "年":
                 return f"{vi_num} năm"
            return f"{vi_num} {cl_vi} {noun_zh}"
        text = pat.sub(replacer, text)
    return text


# ==========================================
# Category 8: Demonstrative Reordering
# ==========================================
import re

_ZH_C8_DEMONSTRATIVE = re.compile(
    r"(这|那)([一两三四五六七八九十百千万]+)(个|名|位|只|条|件|双|套|声|张|块|座|具)([\u4e00-\u9fff]{1,6}?(?=[\s，。、！？：；]|$|的|了|在|被))"
)
_ZH_C8_CURSE = re.compile(r"这(死)(女人|男人|胖子|老头|老太)")

def apply_cat8_demonstrative(text: str) -> str:
    # 这两个死党 -> 两个死党这 -> hai cái đồng đảng này
    text = _ZH_C8_DEMONSTRATIVE.sub(r"\2\3\4\1", text)
    # 这死女人 -> 死女人这
    text = _ZH_C8_CURSE.sub(r"\1\2这", text)
    return text

# ==========================================
# Category 9: Multi-level Possessive
# ==========================================
# A的B的C -> C 的 B 的 A -> C của B A (e.g. 声音 của 高跟鞋 清脆)
_ZH_C9_MULTI_POSS = re.compile(r"([^\s的，。？！]{1,6})的([^\s的，。？！]{1,6})的([^\s的，。？！]{1,6})")

def apply_cat9_multiposs(text: str) -> str:
    return _ZH_C9_MULTI_POSS.sub(r"\3 của \2 \1", text)

# ==========================================
# Category 10: Generic Adjective + Noun
# ==========================================
_ZH_C10_ANCHOR_NOUNS = r"鼻子|脸|嘴巴|眼睛|耳朵|脸颊|额头|门|张陈|男子|女子|老板|老太|老人|男孩|女孩|女鬼|鬼"
_ZH_C10_GENERIC_ADJ = re.compile(f"([^\\s的，。？！]{{2,8}}?)(?:的?)({_ZH_C10_ANCHOR_NOUNS})")

def apply_cat10_generic_adj(text: str) -> str:
    # 棱角分明的脸 -> 脸棱角分明
    return _ZH_C10_GENERIC_ADJ.sub(r"\2 \1", text)

def apply_phase3(text: str) -> str:
    text = apply_cat8_demonstrative(text)
    text = apply_cat9_multiposs(text)
    text = apply_cat10_generic_adj(text)
    return text

# ==========================================
# Phase 4: Locative & Spatial Hierarchy
# ==========================================
# Exclude demonstratives 那/这/哪 from being treated as stand-alone nouns to prevent breaking '那里/这里'
_ZH_C11_POSTPOS = re.compile(r"([^\s的，。？！在被向走这那哪]{1,8})(面前|前面|后面|上面|下面|里面|外面|里|外|上|下)(?=[，。？！\s]|$)")
_ZH_C12_NESTED_LOC = re.compile(r"在([^\s。，？！]{1,10})的([^\s。，？！]{1,10})(上|下|里|外)")
_ZH_C13_TIME = re.compile(r"(?<!最)(?<!然)([^\s。，？！在]{2,15})(之后|之前|后(?!面|来|悔))")
_ZH_C14_SPATIAL = re.compile(r"([\u4e00-\u9fff]{2,8}?)(省|市|国|县|镇|村|区)\s*([\u4e00-\u9fff]{2,8}?)(中学|小学|大学|高中|初中|公司)\s*([\u4e00-\u9fff0-9A-Za-z]{1,8}?)(班|级|年级)\s*(教室|办公室|宿舍|房间)?")

def apply_phase4(text: str) -> str:
    text = _ZH_C12_NESTED_LOC.sub(r"在\3 \2 \1", text)
    text = _ZH_C11_POSTPOS.sub(r"\2 \1", text)
    text = _ZH_C13_TIME.sub(r"\2 \1", text)
    text = _ZH_C14_SPATIAL.sub(r"\7 \5\6 \3\4 \1\2", text)
    return text

# ==========================================
# Phase 5: Template-Based Syntax
# ==========================================
_ZH_C15_CORRELATIVE = re.compile(r"除了([^\s，。？！]{1,15})(还|也)([^\s，。？！]{1,15})")
_ZH_C16_PREP_ACT = re.compile(r"(向|对|朝|向着)([^\s，。？！]{1,10})([\u4e00-\u9fff]{2,10})(了|着)?")
_ZH_C17_LOC_ACT = re.compile(r"在([^\s，。？！]{1,15})([\u4e00-\u9fff]{2,10})(着|了)?")

def apply_phase5(text: str) -> str:
    text = _ZH_C15_CORRELATIVE.sub(r"ngoài \1 ra \2 \3", text)
    text = _ZH_C16_PREP_ACT.sub(r"\3\4 \1 \2", text)
    text = _ZH_C17_LOC_ACT.sub(r"\2\3 \1", text)
    return text

# ==========================================
# Phase 6: Titles & Chapters
# ==========================================
# (张|王|...) + (妈妈|大叔|...) -> (妈妈|大叔|...) + (张|王|...)
# Remove lookahead to catch all occurrences
_ZH_C18_TITLE_INV = re.compile(r"([张王李赵陈周吴郑孙马刘胡谭谢老小]{1})(妈妈|爸爸|大叔|大婶|老师|同学|医生|护士|师傅|校工|叔叔|阿姨|大伯|大娘|妈|爸|兄|弟|姐|妹|婆婆|老太|鬼|女鬼)")
_ZH_C19_APPROX_QTY = re.compile(r"(\d+|[一二三四五六七八九十百]+)多(岁|年|个|月|块|米|斤|里|次|层|人)")
_ZH_C20_CHAPTER = re.compile(r"第([一二三四五六七八九十0-9]+)(章|篇|节|回)")
_ZH_C21_PREP_PROP = re.compile(r"从([^\s。，？！\d]{1,15})(传来|传出|响起|爆发|跳出|走来)")

def apply_phase6(text: str) -> str:
    text = _ZH_C18_TITLE_INV.sub(r"\2 \1", text)
    text = _ZH_C19_APPROX_QTY.sub(r"hơn \1 \2", text)
    text = _ZH_C20_CHAPTER.sub(r"\2 \1", text)
    text = _ZH_C21_PREP_PROP.sub(r"\2 từ \1", text)
    return text

# ==========================================
# Phase 7: Simulative Syntax (Cat 23)
# ==========================================
_ZH_C23_SIMULATIVE = re.compile(r"([^\s，。？！的]{1,10})(似的|一样|一般)")

def apply_phase7(text: str) -> str:
    text = _ZH_C23_SIMULATIVE.sub(r"như \1", text)
    return text

def rewrite_chinese_structure(text: str) -> str:
    """Entry point for structural rewriting pipeline."""
    # Priority 0: Simulative Syntax
    text = apply_phase7(text)
    
    # Priority 1: Specific Appellations & Complex Modifiers (Precision)
    text = apply_phase6(text)  # Titles & Chapters
    text = _ZH_C1A_RCM.sub(r"\2 \1", text) # Specific modifiers (Cat 1A)
    
    # Priority 2: Macro Structures
    text = apply_phase4(text)  # Locatives
    text = apply_phase5(text)  # Correlatives
    text = apply_phase3(text)  # Cat 8, 9
    
    # Priority 3: Hardcoded Modifiers
    text = _ZH_C1B_ADJ_NOUN.sub(r"\2 \1", text)
    text = _ZH_C1C_CLAUSE.sub(r"\2 \1", text)
    
    # Priority 4: Generic Mappings & Injections (Final)
    text = apply_cat2_possessive(text)
    text = apply_cat10_generic_adj(text) # Generic Adj near end
    text = apply_cat3_colors(text)
    text = apply_cat45_babei(text)
    text = apply_cat6_complements(text)
    text = apply_cat7_classifiers(text)
    return text
