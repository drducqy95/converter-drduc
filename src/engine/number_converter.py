#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
number_converter.py — Algorithmic Chinese Number → Arabic/Vietnamese converter.

Replaces 12,062 hardcoded dictionary entries with a ~300-line algorithm that
handles ANY Chinese number (零 to 兆+), plus weekday/lunar date patterns.

Design:
    - No lookup tables for numbers — pure algorithmic parsing
    - Weekday/Lunar patterns detected by prefix matching
    - Integrates with TrieEngine via try_convert() interface
    - Longest-match semantics: consumes as many number chars as valid

Usage:
    converter = NumberConverter()
    result = converter.try_convert("三千四百五十六个人", 0)
    # → ConversionResult(text='3456', consumed=6, type='number')
"""

from dataclasses import dataclass
import re
from typing import Optional

# ─────────────────────────────────────────────────
# Arabic Unit and Date Templates
# ─────────────────────────────────────────────────

ARABIC_UNIT_TEMPLATES = {
    "月底": "cuối tháng {n}",
    "千万美元": "{n:scale_qianwan} đô la Mỹ",
    "万美元": "{n:scale_wan} đô la Mỹ",
    "千万元": "{n:scale_qianwan} nguyên",
    "万元": "{n:scale_wan} nguyên",
    "万欧元": "{n:scale_wan} Euro",
    "万英镑": "{n:scale_wan} bảng Anh",
    "万像素": "{n:/100} MP",
    "万多": "hơn {n} vạn",
    "区": "khu {n}",
    "米左右的距离": "khoảng cách xấp xỉ {n} mét",
    "米的距离左右": "khoảng cách xấp xỉ {n} mét",
    "米的距离": "cự ly {n} mét",
    "米左右的距离": "cự ly khoảng {n} mét",
    "米的距离左右": "cự ly khoảng {n} mét",
    "平米大": "lớn {n} m2",
    "平米": "{n} m2",
    "平方米": "{n} m2",
    "百分之": "{n}%",
    "％": "{n}%",
    "%": "{n}%",
    "尺左右": "khoảng {n} thước",
    "尺": "{n} thước",
    "公里左右": "khoảng {n} km",
    "公里": "{n} km",
    "分": "{n} phút",
    "秒": "{n} giây",
    "折": "giảm còn {n:zhe}%",
    "级": "cấp {n}",
    "米距离": "khoảng cách {n} mét",
    "多米高度": "độ cao hơn {n} mét",
    "米高度": "độ cao {n} mét",
    "多米长": "dài hơn {n} mét",
    "米长": "dài {n} mét",
    "多米高": "cao hơn {n} mét",
    "米高": "cao {n} mét",
    "公分来长": "dài {n} centimet",
    "公分多长": "dài hơn {n} centimet",
    "公分长": "dài {n} centimet",
    "公分来高": "cao {n} centimet",
    "公分多高": "cao hơn {n} centimet",
    "公分高": "cao {n} centimet",
    "米": "{n} mét",
    "cm 左右": "khoảng {n}cm",
    "cm": "{n}cm",
    "mm": "{n}mm",
    "公分": "{n} cm",
    "厘米": "{n} cm",
    "里": "{n} dặm",
    "吨重": "nặng {n} tấn",
    "多公斤重": "nặng hơn {n} kg",
    "公斤重": "nặng {n} kg",
    "多斤重": "nặng hơn {n} cân",
    "斤重": "nặng {n} cân",
    "斤": "{n} cân",
    "公斤": "{n} kg",
    "吨": "{n} tấn",
    "两": "{n} lượng",
    "周岁": "{n} tuổi",
    "日岁": "{n} tuổi",
    "月岁": "{n} tuổi",
    "岁": "{n} tuổi",
    "天": "{n} ngày",
    "号": "số {n}",
        "米多长": "dài hơn {n} mét",
    "米来长": "dài {n} mét",
    "米多高": "cao hơn {n} mét",
    "米来高": "cao {n} mét",
    "分钟之内": "trong vòng {n} phút",
    "小时之内": "trong vòng {n} giờ",
    "点多": "hơn {n} giờ",
        "多码": "hơn {n} yard",
    "天之内": "trong vòng {n} ngày",
    "点到了": "đến {n} giờ rồi",
    "中队": "trung đội {n}",
    "胜": "thắng {n}",
        "%": "{n}%",
    "％": "{n}%",
    "的距离": "cự ly {n}", 
    "W": "{n}0 ngàn",
    "万": "{n} vạn",
    "寸": "{n} tấc",
    "码": "{n} yard",
    "年左右": "khoảng {n} năm",
    "年多": "hơn {n} năm",
    "年内": "trong khoảng {n} năm",
    "级": "cấp {n}",
    "只": "{n} con",
    "张": "{n} tấm",
    "余米": "hơn {n} mét",
    "多米": "hơn {n} mét",
    "多公分": "hơn {n} cm",
    "多公斤": "hơn {n} kg",
    "多斤": "hơn {n} cân",
    "多张": "hơn {n} tấm",
    "多亿": "hơn {n:scale_wan} tỷ",
    "多万": "hơn {n} vạn",
    "多只": "hơn {n} con",
    "多天": "hơn {n} ngày",
    "多度": "hơn {n} độ",
    "多": "hơn {n}",
    "米余长": "dài hơn {n} mét",
    "丈多长": "dài hơn {n} trượng",
    "寸余长": "dài hơn {n} tấc",
    "寸多高": "cao hơn {n} tấc",
    "多寸高": "cao hơn {n} tấc",
    "米外": "bên ngoài {n} mét",
    "米内": "trong phạm vi {n} mét",
    "日之内": "trong vòng {n} ngày",
    "万7千多": "hơn {n} vạn bảy ngàn",
    "米 9": "{n}m9",
    "米 8": "{n}m8",
    "米 7": "{n}m7",
    "米 6": "{n}m6",
    "米 5": "{n}m5",
    "米 4": "{n}m4",
    "米 3": "{n}m3",
    "米 2": "{n}m2",
    "米 1": "{n}m1",
    "寸宽": "rộng {n} tấc",
    "米宽": "rộng {n} mét",
    "丈宽": "rộng {n} trượng",
    "厘米长": "dài {n} cm",
    "寸长": "dài {n} tấc",
    "丈长": "dài {n} trượng",
    "米宽": "rộng {n} mét",
    "寸高": "cao {n} tấc",
    "丈高": "cao {n} trượng",
    "丈来长": "dài khoảng {n} trượng",
    "丈来高": "cao khoảng {n} trượng",
    "寸来长": "dài khoảng {n} tấc",
    "寸来高": "cao khoảng {n} tấc",
    "寸多长": "dài hơn {n} tấc",
    "多寸长": "dài hơn {n} tấc",
    "丈多高": "cao hơn {n} trượng",
    "多丈长": "dài hơn {n} trượng",
    "多丈高": "cao hơn {n} trượng",
    "年多里": "trong hơn {n:spell_year} năm",
    "分钟多": "hơn {n} phút",
    "分钟": "{n} phút",
    "度": "{n} độ",
    "年前": "{n} năm trước",
}

ARABIC_PREFIX_TEMPLATES = {
    "百分之": "{n}%",
        "于": "vào {n}",
    "生于": "sinh {n}",
    "高": "cao {n}",
    "打": "giảm còn {n:zhe}%",
    "差了": "kém {n}",
    "高了": "cao hơn {n}",
    "在": "ở {n}",
    "身高": "người cao {n}",
    "群": "nhóm {n}",
    "第": "thứ {n}",
    "区": "khu {n}", 
    "室": "phòng {n}",
    "房": "phòng {n}",
    "座": "tòa {n}",
    "号": "số {n}",
    "楼": "tầng {n}",
    "乘以": "nhân với {n}",
    "乘以": "nhân với {n}",
}

CH_NUM_CHARS = "0123456789零〇一壹二贰貳两兩三叁參四肆五伍六陆陸七柒八捌九玖十拾百佰千仟万萬"
HYBRID_DATE_PATTERN = re.compile(
    rf'^((?:\d+|[{CH_NUM_CHARS}]+)\s*年\s*)?'
    rf'((?:腊|正|冬|端)?(?:\d+|[{CH_NUM_CHARS}]+)?)\s*月\s*'
    rf'(初?\s*(?:\d+|[{CH_NUM_CHARS}]+))\s*(?:号|日)?'
    rf'(?:\s*(早上|早晨|上午|中午|下午|傍晚|晚上|深夜|凌晨|半夜))?'
    rf'(?:\s*((?:\d+|[{CH_NUM_CHARS}]+))\s*[点时])?(?:\s*((?:\d+|[{CH_NUM_CHARS}]+))\s*分)?(?:\s*((?:\d+|[{CH_NUM_CHARS}]+))\s*秒)?'
)
NUMBER_START_PATTERN = re.compile(r'^([0-9lL]+(?:\.\s*[0-9lL]+)?(?:(?:\s*[-~,，、]\s*|\s*(?:以至|至|到|和|vs|或)\s*)[0-9lL]+(?:\.\s*[0-9lL]+)?)*)\s*')


# ─────────────────────────────────────────────────
# Result
# ─────────────────────────────────────────────────

@dataclass
class ConversionResult:
    """Result of a successful conversion."""
    text: str        # Output text (e.g., "3456" or "thứ Hai")
    consumed: int    # Number of input characters consumed
    conv_type: str   # 'number', 'weekday', 'lunar'


# ─────────────────────────────────────────────────
# Character Classification  (frozen sets for O(1) lookup)
# ─────────────────────────────────────────────────

# Digit characters → value
DIGIT_MAP: dict[str, int] = {
    '零': 0, '〇': 0,
    '一': 1, '壹': 1,
    '二': 2, '贰': 2, '貳': 2,
    '两': 2, '兩': 2,
    '三': 3, '叁': 3, '參': 3,
    '四': 4, '肆': 4,
    '五': 5, '伍': 5,
    '六': 6, '陆': 6, '陸': 6,
    '七': 7, '柒': 7,
    '八': 8, '捌': 8,
    '九': 9, '玖': 9,
}

# Intra-section multipliers (十 百 千)
MULTI_MAP: dict[str, int] = {
    '十': 10,  '拾': 10,
    '百': 100, '佰': 100,
    '千': 1000, '仟': 1000,
}

# Section-level multipliers (万 亿 兆)
SECTION_MAP: dict[str, int] = {
    '万': 10_000,          '萬': 10_000,
    '亿': 100_000_000,     '億': 100_000_000,
    '兆': 1_000_000_000_000,  # 10^12 (modern standard)
}

# All characters that can appear in a Chinese number
NUMBER_CHARS: frozenset[str] = frozenset(
    set(DIGIT_MAP) | set(MULTI_MAP) | set(SECTION_MAP)
)


def format_numeric_sequence(num_str: str) -> str:
    import re
    s = num_str.replace('l', '1').replace('L', '1')
    s = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', s)
    s = re.sub(r'\s*([-~,，、])\s*', r'\1', s)
    s = re.sub(r'\s*(以至|至|到)\s*', r' đến ', s)
    s = re.sub(r'\s*和\s*', r' và ', s)
    s = re.sub(r'\s*(vs|或)\s*', r' \1 ', s)
    return s.strip()

def scale_vietnamese_number(value: float) -> str:
    if value >= 1_000_000_000:
        v = value / 1_000_000_000
        return f"{v:g} tỉ"
    elif value >= 1_000_000:
        v = value / 1_000_000
        return f"{v:g} triệu"
    elif value >= 1_000:
        v = value / 1_000
        return f"{v:g} ngàn"
    else:
        return f"{value:g}"

def format_arabic_template(template: str, num_str: str) -> str:
    if "{n:zhe}" in template:
        try:
            val = float(num_str.replace(' ', '')) * 10
            return template.replace("{n:zhe}", f"{val:g}")
        except: pass
    if "{n:scale_wan}" in template:
        try:
            val = float(num_str.replace(' ', '')) * 10_000
            return template.replace("{n:scale_wan}", scale_vietnamese_number(val))
        except: pass
    if "{n:scale_qianwan}" in template:
        try:
            val = float(num_str.replace(' ', '')) * 10_000_000
            return template.replace("{n:scale_qianwan}", scale_vietnamese_number(val))
        except: pass
    if "{n:/100}" in template:
        try:
            val = float(num_str.replace(' ', '')) / 100
            return template.replace("{n:/100}", f"{val:g}")
        except: pass
    if "{n:spell_year}" in template:
        try:
            val = int(float(num_str.replace(' ', '')))
            spelled = spell_vietnamese_number(val)
            return template.replace("{n:spell_year}", spelled)
        except: pass
    return template.replace("{n}", num_str)

def spell_vietnamese_number(n: int) -> str:
    """Spell an integer (0-99) into Vietnamese text."""
    if n == 0: return "không"
    if n == 1: return "một"
    if n == 2: return "hai"
    if n == 3: return "ba"
    if n == 4: return "bốn"
    if n == 5: return "năm"
    if n == 6: return "sáu"
    if n == 7: return "bảy"
    if n == 8: return "tám"
    if n == 9: return "chín"
    if n == 10: return "mười"
    
    if n < 20:
        unit = n % 10
        if unit == 5: return "mười lăm"
        return "mười " + spell_vietnamese_number(unit)
        
    tens = n // 10
    unit = n % 10
    res = spell_vietnamese_number(tens) + " mươi"
    if unit == 1: res += " mốt"
    elif unit == 4: res += " tư"
    elif unit == 5: res += " lăm"
    elif unit > 0: res += " " + spell_vietnamese_number(unit)
    return res


# ─────────────────────────────────────────────────
# Algorithmic Number Parser
# ─────────────────────────────────────────────────

def _parse_section(chars: str) -> int:
    """
    Parse a sub-万 section: sequence of digits + 千/百/十.

    Examples:
        三千四百五十六 → 3456
        零三           → 3
        一百零三       → 103
        十三           → 13       (implicit 一 before 十)
        二百十         → 210      (implicit 一 before isolated 十)
    """
    if not chars:
        return 0

    result = 0
    current = 0       # accumulator for the digit before a multiplier
    has_digit = False  # whether we've seen a digit for `current`

    for ch in chars:
        if ch in DIGIT_MAP:
            current = DIGIT_MAP[ch]
            has_digit = True
        elif ch in MULTI_MAP:
            mult = MULTI_MAP[ch]
            if not has_digit:
                # Implicit 一: 十三 → 1×10+3, or 二百十 → 200 + 1×10
                current = 1
            result += current * mult
            current = 0
            has_digit = False
        # SECTION_MAP chars shouldn't appear here (handled upstream)

    # Add leftover ones-digit
    result += current
    return result


def _split_by_section_char(s: str, sep_chars: set[str]) -> tuple[str, str, str | None]:
    """
    Split string at the FIRST occurrence of any char in sep_chars.
    Returns (before, after, found_char) or (s, '', None).
    """
    for i, ch in enumerate(s):
        if ch in sep_chars:
            return s[:i], s[i + 1:], ch
    return s, '', None


def parse_chinese_number(s: str) -> int | None:
    """
    Parse a sequence of Chinese number characters into an integer.

    Returns None if the string doesn't form a valid number.

    Handles the hierarchical structure:
        [兆 section] × 10^12  +  [亿 section] × 10^8  +  [万 section] × 10^4  +  [base section]
    """
    if not s:
        return None

    # Validate: all characters must be number-related
    if not all(ch in NUMBER_CHARS for ch in s):
        return None

    value = 0

    # --- 兆 level ---
    zhao_chars = {'兆'}
    before, after, found = _split_by_section_char(s, zhao_chars)
    if found:
        zhao_part = _parse_sub_wan(before) if before else 1
        value += zhao_part * 1_000_000_000_000
        s = after

    # --- 亿 level ---
    yi_chars = {'亿', '億'}
    before, after, found = _split_by_section_char(s, yi_chars)
    if found:
        yi_part = _parse_sub_wan(before) if before else 1
        value += yi_part * 100_000_000
        s = after

    # --- 万 level and below ---
    value += _parse_sub_wan(s)

    return value


def _parse_sub_wan(s: str) -> int:
    """Parse a string that may contain 万 but nothing higher."""
    if not s:
        return 0

    wan_chars = {'万', '萬'}
    before, after, found = _split_by_section_char(s, wan_chars)
    if found:
        wan_part = _parse_section(before) if before else 1
        remainder = _parse_section(after) if after else 0
        return wan_part * 10_000 + remainder

    return _parse_section(s)


# ─────────────────────────────────────────────────
# NumberConverter — public interface
# ─────────────────────────────────────────────────

class NumberConverter:
    """
    Algorithmic converter: Chinese number / weekday / lunar date → text.

    Usage with TrieEngine:
        converter = NumberConverter()
        # In translate_text loop:
        result = converter.try_convert(text, pos)
        if result and result.consumed > trie_match_length:
            use result
    """

    # Minimum chars to trigger number conversion (avoids false positives on
    # single-digit chars like 一 that may be part of compound words).
    MIN_NUMBER_CHARS = 2

    def try_convert(self, text: str, pos: int) -> ConversionResult | None:
        """
        Try to convert starting at `pos`. Returns the best match or None.

        Priority order:
            1. Weekday pattern  (星期一, 周三, 礼拜天, 周末)
            2. Lunar date       (初一 ... 初十)
            3. Pure number      (三千四百五十六)
        """
        result = self._try_date_expression(text, pos)
        if result:
            return result

        result = self._try_arabic_unit(text, pos)
        if result:
            return result

        result = self._try_time_expression(text, pos)
        if result:
            return result

        result = self._try_weekday(text, pos)
        if result:
            return result

        result = self._try_lunar(text, pos)
        if result:
            return result

        result = self._try_number(text, pos)
        if result:
            return result

        return None

    # ─── Weekday ───

    def _try_weekday(self, text: str, pos: int) -> ConversionResult | None:
        """
        Match weekday patterns algorithmically.

        Prefixes: 星期, 周, 礼拜
        Suffixes: 一..六 → thứ Hai..Bảy, 天/日 → Chủ nhật
        Special:  周末 → cuối tuần
        """
        remaining = text[pos:]

        # 周末 special case
        if remaining.startswith('周末'):
            return ConversionResult(text='cuối tuần', consumed=2, conv_type='weekday')

        # Try each prefix
        for prefix in ('星期', '礼拜', '周'):
            if not remaining.startswith(prefix):
                continue
            plen = len(prefix)
            if pos + plen >= len(text):
                continue
            
            suffix = text[pos + plen]
            
            if suffix in ('天', '日'):
                return ConversionResult(
                    text='Chủ nhật',
                    consumed=plen + 1,
                    conv_type='weekday',
                )
            elif suffix in NUMBER_CHARS:
                # Need to verify it evaluates to 1-6
                val = parse_chinese_number(suffix)
                if val and 1 <= val <= 6:
                    day_name = "Tư" if val == 3 else spell_vietnamese_number(val + 1).capitalize()
                    return ConversionResult(
                        text=f'thứ {day_name}',
                        consumed=plen + 1,
                        conv_type='weekday',
                    )

        return None

    # ─── Lunar Date ───

    def _try_lunar(self, text: str, pos: int) -> ConversionResult | None:
        """
        Match lunar date pattern algorithmically: 初 + number chars.
        
        Lunar prefix 初 applies to the first 10 days of a month (初一 to 初十).
        Some texts might misuse it up to 初三十. This algorithm handles valid ranges.
        """
        if pos >= len(text) or text[pos] != '初':
            return None
            
        # Scan forward for Chinese numbers after 初
        start = pos + 1
        end = start
        while end < len(text) and text[end] in NUMBER_CHARS:
            end += 1
            
        if end == start:
            return None
            
        num_str = text[start:end]
        val = parse_chinese_number(num_str)
        
        if val is None or val < 1 or val > 30:
            return None
            
        vn_word = spell_vietnamese_number(val)
        
        if val == 5:
            # 初五 traditionally uses "mồng"
            prefix_word = 'mồng'
        elif val <= 10:
            prefix_word = 'mùng'
        else:
            # Beyond 10, typically "ngày Mười một", "ngày Hai mươi"
            prefix_word = 'ngày'
            vn_word = vn_word.capitalize()
            
        return ConversionResult(
            text=f'{prefix_word} {vn_word}',
            consumed=(end - pos),
            conv_type='lunar',
        )


    # ─── Date Expression ───
    
    def _try_date_expression(self, text: str, pos: int) -> 'ConversionResult | None':
        rem = text[pos:]
        
        year_prefixes = [
            ("生于", "sinh năm {n}", True),
            ("在于", "vào năm {n}", True),
            ("于", "vào năm {n}", True),
            ("在", "vào năm {n}", True),
            ("公元前", "năm {n} trước công nguyên", True),
            ("公元", "công nguyên năm {n}", True),
            ("世纪中叶", "giữa thế kỷ {n}", False),
            ("年代末", "cuối thập niên {n}", False),
            ("年代后", "sau thập niên {n}", False),
            ("年代初", "đầu thập niên {n}", False),
            ("世纪", "thế kỷ {n}", False),
            ("年代", "thập niên {n}", False),
            ("年多里", "trong hơn {n:spell_year} năm", False),
            ("年底", "cuối năm {n}", False),
            ("年末", "cuối năm {n}", False),
            ("年初", "đầu năm {n}", False),
            ("年中", "giữa năm {n}", False),
            ("年冬", "mùa đông năm {n}", False),
            ("年春", "mùa xuân năm {n}", False),
            ("年秋", "mùa thu năm {n}", False),
            ("年度", "niên độ {n}", False),
            ("年前", "{n} năm trước", False),
            ("年", "năm {n}", False),
        ]
        
        dp = HYBRID_DATE_PATTERN.match(rem)
        if dp:
            opt_year_raw = dp.group(1) 
            opt_year = opt_year_raw.replace("年", "").strip() if opt_year_raw else ""
            raw_month = dp.group(2).strip()
            raw_day = dp.group(3).strip()
            time_of_day_prefix = dp.group(4).strip() if dp.group(4) else ""
            raw_hour = dp.group(5).strip() if dp.group(5) else ""
            raw_min = dp.group(6).strip() if dp.group(6) else ""
            raw_sec = dp.group(7).strip() if dp.group(7) else ""
            
            month_val = 0
            lunar_month = ""
            if raw_month.startswith("腊"):
                month_val = 12
                lunar_month = "chạp"
            elif raw_month.startswith("正") or raw_month.startswith("端"):
                month_val = 1
                lunar_month = "giêng"
            elif raw_month.startswith("冬"):
                month_val = 11
            else:
                if raw_month.isdigit(): month_val = int(raw_month)
                else: month_val = parse_chinese_number(raw_month) or 0
            
            is_mung = False
            if raw_day.startswith("初"):
                is_mung = True
                raw_day = raw_day[1:].strip()
            
            if raw_day.isdigit(): day_val = int(raw_day)
            else: day_val = parse_chinese_number(raw_day) or 0

            if is_mung:
                day_spelled = spell_vietnamese_number(day_val)
                final_day = f"mùng {day_spelled}"
            else:
                final_day = f"ngày {day_val}"
            
            if lunar_month:
                month_spelled = lunar_month
            else:
                month_spelled = str(month_val)
                
            TIME_PREFIX_MAP = {
                "早晨": "sáng", "早上": "sáng", "上午": "sáng", "中午": "trưa",
                "下午": "chiều", "傍晚": "chiều tối", "晚上": "đêm", "深夜": "đêm",
                "凌晨": "sáng", "半夜": "đêm",
            }
            time_str = ""
            if raw_hour:
                h_val = int(raw_hour) if raw_hour.isdigit() else (parse_chinese_number(raw_hour) or 0)
                time_str = f"{h_val} giờ"
                if raw_min:
                    m_val = int(raw_min) if raw_min.isdigit() else (parse_chinese_number(raw_min) or 0)
                    time_str += f" {m_val} phút"
                if raw_sec:
                    s_val = int(raw_sec) if raw_sec.isdigit() else (parse_chinese_number(raw_sec) or 0)
                    time_str += f" {s_val} giây"
                period = TIME_PREFIX_MAP.get(time_of_day_prefix, "")
                if h_val >= 11 and time_of_day_prefix in ("早晨", "上午", "中午"):
                    period = "trưa"
                if h_val <= 3 and time_of_day_prefix in ("早晨", "早上"):
                    period = "sáng"
                if period:
                    time_str += f" {period}"
            elif time_of_day_prefix:
                time_str = TIME_PREFIX_MAP.get(time_of_day_prefix, "")
                
            y_spelled = ""
            if opt_year:
                if opt_year.isdigit():
                    y_spelled = opt_year
                else:
                    y_spelled = "".join([str(DIGIT_MAP.get(ch, ch)) for ch in opt_year])
                    
            parts = []
            if time_str:
                parts.append(time_str)
            if final_day:
                parts.append(final_day)
            parts.append(f"tháng {month_spelled}")
            if y_spelled:
                parts.append(f"năm {y_spelled}")

            return ConversionResult(
                text=" ".join(parts),
                consumed=dp.end(),
                conv_type="date_hybrid"
            )
            
        # Year + Month Pattern
        ym_pattern = re.compile(r'^(\d{2,4})\s*年\s*(1[0-2]|0?[1-9])\s*月')
        m = ym_pattern.match(rem)
        if m:
            return ConversionResult(text=f"tháng {m.group(2)} năm {m.group(1)}", consumed=m.end(), conv_type="year_month")
            
        # Year + Month Pattern
        ym_pattern = re.compile(r'^(\d{2,4})\s*年\s*(1[0-2]|0?[1-9])\s*月')
        m = ym_pattern.match(rem)
        if m:
            return ConversionResult(text=f"tháng {m.group(2)} năm {m.group(1)}", consumed=m.end(), conv_type="year_month")
            
        for prefix, template, is_prefix in year_prefixes:
            if is_prefix:
                if rem.startswith(prefix):
                    rem_stripped = rem[len(prefix):].lstrip()
                    np = NUMBER_START_PATTERN.match(rem_stripped)
                    if np:
                        num_str = np.group(1)
                        rem_after_num = rem_stripped[np.end():].lstrip()
                        consumed_extra = 1 if rem_after_num.startswith('年') else 0
                        if prefix in ("生于", "在于", "于", "在") and consumed_extra == 0:
                            pass
                        else:
                            return ConversionResult(
                            text=format_arabic_template(template, num_str),
                            consumed=len(prefix) + (len(rem[len(prefix):]) - len(rem_stripped)) + np.end() + (len(rem_stripped[np.end():]) - len(rem_after_num)) + consumed_extra,
                            conv_type="year_prefix"
                        )
            else:
                np = NUMBER_START_PATTERN.match(rem)
                if np:
                    num_str = np.group(1)
                    rem_after = rem[np.end():]
                    if rem_after.startswith(prefix):
                        return ConversionResult(
                            text=format_arabic_template(template, num_str),
                            consumed=np.end() + len(prefix),
                            conv_type="year_suffix"
                        )
        return None

    # ─── Arabic Unit / Date ───

    def _try_arabic_unit(self, text: str, pos: int) -> ConversionResult | None:
        prefix_used = None
        start_pos = pos
        for max_len in (3, 2, 1):
            prefix_cand = text[pos:pos+max_len]
            if prefix_cand in ARABIC_PREFIX_TEMPLATES:
                temp_pos = pos + max_len
                while temp_pos < len(text) and text[temp_pos].isspace():
                    temp_pos += 1
                if temp_pos < len(text) and (text[temp_pos].isdigit() or text[temp_pos] in NUMBER_CHARS):
                    prefix_used = prefix_cand
                    start_pos = temp_pos
                    break
                
        if start_pos >= len(text) or not text[start_pos].isdigit():
            return None
            
        remaining = text[start_pos:]
        
        # 1. Number + Unit Pattern (or Prefix + Number)
        np = NUMBER_START_PATTERN.match(remaining)
        if np:
            num_str = np.group(1)
            try:
                num_clean = format_numeric_sequence(num_str)
            except ValueError:
                num_clean = num_str
            
            consumed_after_num = np.end()
            text_after = remaining[consumed_after_num:]
            
            if prefix_used:
                # Special cases for prefix + suffix combination
                template = ARABIC_PREFIX_TEMPLATES[prefix_used]
                
                best_match_unit = None
                for unit in sorted(ARABIC_UNIT_TEMPLATES.keys(), key=len, reverse=True):
                    if text_after.startswith(unit):
                        best_match_unit = unit
                        break
                        
                if best_match_unit:
                    if prefix_used == "打" and best_match_unit == "折":
                        formatted_text = format_arabic_template(template, num_clean)
                    elif prefix_used in ("差了", "高了") and best_match_unit in ("级", "级 "):
                        import re
                        raw_prefix = template.replace(' {n}', '')
                        raw_unit = ARABIC_UNIT_TEMPLATES[best_match_unit].replace(' {n}', '').replace('{n} ', '')
                        formatted_text = f"{raw_prefix} {num_clean} {raw_unit}".strip()
                    else:
                        unit_template = ARABIC_UNIT_TEMPLATES[best_match_unit]
                        formatted_unit = format_arabic_template(unit_template, num_clean)
                        formatted_text = format_arabic_template(template, formatted_unit)
                        
                    consumed_total = (start_pos - pos) + consumed_after_num + len(best_match_unit)
                    # Check trailing modifiers after unit
                    trailing = remaining[consumed_after_num + len(best_match_unit):]
                    if trailing.startswith("左右"):
                        formatted_text = "khoảng " + formatted_text
                        consumed_total += 2
                    elif trailing.startswith("以内") or trailing.startswith("内"):
                        sz = 2 if trailing.startswith("以内") else 1
                        formatted_text = "trong vòng " + formatted_text
                        consumed_total += sz
                    elif trailing.startswith("以外") or trailing.startswith("外"):
                        sz = 2 if trailing.startswith("以外") else 1
                        formatted_text = "bên ngoài " + formatted_text
                        consumed_total += sz
                    elif trailing.startswith("以上"):
                        formatted_text = "trên " + formatted_text
                        consumed_total += 2
                    elif trailing.startswith("以下"):
                        formatted_text = "dưới " + formatted_text
                        consumed_total += 2
                    return ConversionResult(
                        text=formatted_text,
                        consumed=consumed_total,
                        conv_type="arabic_prefix_suffix"
                    )
                
                if prefix_used == "第" and text_after.startswith("号"):
                    formatted_text = f"số {num_clean}"
                    consumed_total = (start_pos - pos) + consumed_after_num + 1
                    return ConversionResult(
                        text=formatted_text,
                        consumed=consumed_total,
                        conv_type="arabic_prefix_suffix"
                    )
                formatted_text = format_arabic_template(template, num_clean)
                consumed_total = (start_pos - pos) + consumed_after_num
                # Check trailing modifiers after number (no unit)
                trailing_pref = remaining[consumed_after_num:]
                if trailing_pref.startswith("左右"):
                    formatted_text = "khoảng " + formatted_text
                    consumed_total += 2
                elif trailing_pref.startswith("以内") or trailing_pref.startswith("内"):
                    sz = 2 if trailing_pref.startswith("以内") else 1
                    formatted_text = "trong vòng " + formatted_text
                    consumed_total += sz
                return ConversionResult(
                    text=formatted_text,
                    consumed=consumed_total,
                    conv_type="arabic_prefix"
                )
            else:
                best_match_unit = None
                for unit in sorted(ARABIC_UNIT_TEMPLATES.keys(), key=len, reverse=True):
                    if text_after.startswith(unit):
                        best_match_unit = unit
                        break
                        
                if best_match_unit:
                    template = ARABIC_UNIT_TEMPLATES[best_match_unit]
                    formatted_text = format_arabic_template(template, num_clean)
                    
                    consumed_local = consumed_after_num + len(best_match_unit)
                    trailing = remaining[consumed_local:]
                    
                    if trailing.startswith("左右"):
                        formatted_text = "khoảng " + formatted_text
                        consumed_local += 2
                    elif trailing.startswith("以内") or trailing.startswith("内"):
                        sz = 2 if trailing.startswith("以内") else 1
                        formatted_text = "trong vòng " + formatted_text
                        consumed_local += sz
                    elif trailing.startswith("之后") or trailing.startswith("后"):
                        sz = 2 if trailing.startswith("之后") else 1
                        formatted_text = "sau " + formatted_text
                        consumed_local += sz
                    elif trailing.startswith("以外") or trailing.startswith("外"):
                        sz = 2 if trailing.startswith("以外") else 1
                        formatted_text = "bên ngoài " + formatted_text
                        consumed_local += sz
                    elif trailing.startswith("以上"):
                        formatted_text = "trên " + formatted_text
                        consumed_local += 2
                    elif trailing.startswith("以下"):
                        formatted_text = "dưới " + formatted_text
                        consumed_local += 2
                        
                    return ConversionResult(
                        text=formatted_text,
                        consumed=consumed_local,
                        conv_type="arabic_unit"
                    )
                
        return None


    # ─── Time Expression ───
    
    def _try_time_expression(self, text: str, pos: int) -> ConversionResult | None:
        TIME_PREFIX_MAP = {
            "早晨": "sáng",
            "早上": "sáng",
            "上午": "sáng",
            "中午": "trưa",
            "下午": "chiều",
            "傍晚": "chiều tối",
            "晚上": "đêm",
            "深夜": "đêm",
            "凌晨": "sáng",
            "半夜": "sáng",
        }
        
        rem = text[pos:]
        
        import re
        m_time = re.match(r'^(\d{1,2})\s*:\s*(\d{2})\s*(分?)', rem)
        if m_time:
            h, min_val, f = m_time.groups()
            return ConversionResult(text=f"{h} giờ {min_val}{' phút' if f else ''}", consumed=m_time.end(), conv_type="time_digital")
            
        # Standalone "小时 X 分" pattern
        m_hour_min = re.match(r'^小时\s*(\d+)\s*分', rem)
        if m_hour_min:
            return ConversionResult(text=f"giờ {m_hour_min.group(1)} phút", consumed=m_hour_min.end(), conv_type="time_standalone")
        
        if rem.startswith("点") or rem.startswith("分") or rem.startswith("快"):
            import re
            m = re.match(r'^点\s*(\d+)\s*分', rem)
            if m:
                return ConversionResult(text=f"giờ {m.group(1)} phút", consumed=m.end(), conv_type="time_standalone")
            m = re.match(r'^点\s*(\d+)\s*多', rem)
            if m:
                return ConversionResult(text=f"giờ {m.group(1)} hơn", consumed=m.end(), conv_type="time_standalone")
            m = re.match(r'^分\s*(\d+)\s*秒', rem)
            if m:
                return ConversionResult(text=f"phút {m.group(1)} giây", consumed=m.end(), conv_type="time_standalone")
                
        match_prefix = None
        for p, v in TIME_PREFIX_MAP.items():
            if rem.startswith(p):
                match_prefix = (p, v)
                break
                
        start_idx = len(match_prefix[0]) if match_prefix else 0
        # Skip whitespace between prefix and number
        while start_idx < len(rem) and rem[start_idx].isspace():
            start_idx += 1
        rem_after_prefix = rem[start_idx:]
        
        np = NUMBER_START_PATTERN.match(rem_after_prefix)
        if not np:
            return None
            
        num_str = np.group(1)
        consumed_num = start_idx + np.end()
        rem_after_num = rem[consumed_num:]
        
        time_suffixes = {
            "快点半钟的时候": "lúc sắp {n:spell} giờ rưỡi",
            "快点钟的时候": "lúc sắp {n:spell} giờ",
            "快点半的时候": "lúc sắp {n:spell} giờ rưỡi",
            "点半钟左右多": "khoảng hơn {n:spell} giờ rưỡi",
            "点半钟左右": "khoảng {n:spell} giờ rưỡi",
            "点半钟多": "hơn {n:spell} giờ rưỡi",
            "点半左右多": "khoảng hơn {n:spell} giờ rưỡi",
            "点半左右": "khoảng {n:spell} giờ rưỡi",
            "点钟左右多": "khoảng hơn {n:spell} giờ",
            "点钟左右": "khoảng {n:spell} giờ",
            "点左右多": "khoảng hơn {n:spell} giờ",
            "点左右": "khoảng {n:spell} giờ",
            "快点半钟": "sắp {n:spell} giờ rưỡi",
            "点半钟的时候": "lúc {n:spell} giờ rưỡi",
            "点种的时候": "lúc {n:spell} giờ",
            "快点的时候": "lúc sắp {n:spell} giờ",
            "分钟多": "hơn {n:spell} phút",
            "快点钟": "sắp {n:spell} giờ",
            "快点半": "sắp {n:spell} giờ rưỡi",
            "快点": "sắp {n:spell} giờ",
            "点钟的时候": "lúc {n:spell} giờ", 
            "点半的时候": "lúc {n:spell} giờ rưỡi",
            "点半钟": "{n:spell} giờ rưỡi",
            "点钟多": "hơn {n:spell} giờ",
            "点多钟": "hơn {n:spell} giờ đồng hồ",
            "点半多": "hơn {n:spell} giờ rưỡi",
            "点半": "{n:spell} giờ rưỡi",
            "点的时候": "lúc {n:spell} giờ",
            "点钟": "{n:spell} giờ",
            "点多": "hơn {n:spell} giờ",
            "点": "{n:spell} giờ",
        }
        
        for suf, template in time_suffixes.items():
            if rem_after_num.startswith(suf):
                val = int(float(num_str.replace(" ", "")))
                spelled = spell_vietnamese_number(val)
                formatted = template.replace("{n:spell}", spelled)
                
                consumed_full = consumed_num + len(suf)
                rem_after_suf = rem[consumed_full:]
                
                if suf == "点" and rem_after_suf.lstrip().startswith(tuple(str(d) for d in range(10))):
                    min_match = NUMBER_START_PATTERN.match(rem_after_suf.lstrip())
                    if min_match:
                        min_str = min_match.group(1)
                        rem_after_min = rem_after_suf.lstrip()[min_match.end():]
                        
                        formatted = formatted.replace(spelled, str(val))
                        if rem_after_min.startswith("分"):
                            formatted += f" {min_str} phút"
                            consumed_full += (len(rem_after_suf) - len(rem_after_suf.lstrip())) + min_match.end() + 1
                        elif rem_after_min.startswith("多"):
                            formatted += f" {min_str} hơn"
                            consumed_full += (len(rem_after_suf) - len(rem_after_suf.lstrip())) + min_match.end() + 1
                        else:
                            formatted += f" {min_str}"
                            consumed_full += (len(rem_after_suf) - len(rem_after_suf.lstrip())) + min_match.end()
                            
                if match_prefix:
                    period = match_prefix[1]
                    if val >= 11 and match_prefix[0] in ("早晨", "上午", "中午"):
                        period = "trưa"
                    if val <= 3 and match_prefix[0] in ("早晨", "早上"):
                        period = "sáng"
                    
                    if period and period not in formatted.split():
                        formatted += f" {period}"
                    
                return ConversionResult(
                    text=formatted,
                    consumed=consumed_full,
                    conv_type="time_expression"
                )
                
        return None

    # ─── Pure Number ───

    # Chinese range connectors → Vietnamese
    _RANGE_CONNECTORS = [
        ('vs', 'vs'), ('VS', 'vs'),
        ('到', 'đến'), ('至', 'đến'), ('以至', 'đến'),
        ('和', 'và'), ('或', 'hoặc'),
    ]

    def _try_number(self, text: str, pos: int) -> ConversionResult | None:
        """
        Consume the longest valid Chinese number from position `pos`.

        Rules:
            - Must consume >= MIN_NUMBER_CHARS characters (default 2)
            - Exception: 十 at start counts (十三 = 2 chars = 13)
            - Single digits (一, 三) are NOT converted (let Trie handle)
            - Supports ranges: 二十到三十 → 20 đến 30, 二十 vs 二十 → 20 vs 20
        """
        # Scan forward to find consecutive number chars
        end = pos
        while end < len(text) and text[end] in NUMBER_CHARS:
            end += 1

        consumed = end - pos
        if consumed < self.MIN_NUMBER_CHARS:
            return None

        num_str = text[pos:end]

        # Parse
        value = parse_chinese_number(num_str)
        if value is None:
            return None

        result_text = str(value)
        total_consumed = consumed

        # Check for range connector after the first number
        rem_after = text[end:]
        for conn, vn_conn in self._RANGE_CONNECTORS:
            pattern = re.compile(r'^\s*' + re.escape(conn) + r'\s*')
            m = pattern.match(rem_after)
            if m:
                after_connector = rem_after[m.end():]
                end2 = 0
                while end2 < len(after_connector) and after_connector[end2] in NUMBER_CHARS:
                    end2 += 1
                if end2 >= 1:
                    val2 = parse_chinese_number(after_connector[:end2])
                    if val2 is not None:
                        result_text = f"{value} {vn_conn} {val2}"
                        total_consumed = consumed + m.end() + end2
                break

        return ConversionResult(
            text=result_text,
            consumed=total_consumed,
            conv_type='number',
        )


# ─────────────────────────────────────────────────
# CLI for standalone testing
# ─────────────────────────────────────────────────

def main():
    import sys

    converter = NumberConverter()

    test_cases = [
        # (input, expected)
        ("三千四百五十六", "3456"),
        ("一千零三", "1003"),
        ("一万二千", "12000"),
        ("两千", "2000"),
        ("十三", "13"),
        ("五亿三千万", "530000000"),
        ("一百", "100"),
        ("一千九百九十九", "1999"),
        ("三千万", "30000000"),
        ("一兆", "1000000000000"),
        ("星期一", "thứ Hai"),
        ("周日", "Chủ nhật"),
        ("周末", "cuối tuần"),
        ("礼拜天", "Chủ nhật"),
        ("初一", "mùng một"),
        ("初五", "mồng năm"),
    ]

    print("🧪 Number Converter Self-Test\n")
    passed = 0
    failed = 0

    for input_text, expected in test_cases:
        result = converter.try_convert(input_text, 0)
        actual = result.text if result else "None"
        ok = actual == expected
        status = "✅" if ok else "❌"
        print(f"  {status} {input_text:15s} → {actual:20s} {'(expected: ' + expected + ')' if not ok else ''}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n📊 {passed}/{passed + failed} passed")

    # Interactive mode
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            result = converter.try_convert(arg, 0)
            if result:
                print(f"  {arg} → {result.text} ({result.conv_type}, {result.consumed} chars)")
            else:
                print(f"  {arg} → (no match)")


if __name__ == "__main__":
    main()
