import re

file_path = "src/engine/number_converter.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Patterns
ch_num_chars = 'CH_NUM_CHARS = "0123456789零〇一壹二贰貳两兩三叁參四肆五伍六陆陸七柒八捌九玖十拾百佰千仟万萬"'
old_hybrid = r"HYBRID_DATE_PATTERN = re.compile(rf'^((?:腊|正|冬)?(?:[{CH_NUM_CHARS}]+)?)\s*月\s*(初?[{CH_NUM_CHARS}]+)\s*(?:号|日)?')"
new_hybrid = r"HYBRID_DATE_PATTERN = re.compile(rf'^((?:腊|正|冬)?(?:\d+|[{CH_NUM_CHARS}]+)?)\s*月\s*(初?(?:\d+|[{CH_NUM_CHARS}]+))\s*(?:号|日)?')"

old_number = r"NUMBER_START_PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*')"
new_number = r"NUMBER_START_PATTERN = re.compile(r'^(\d+(?:\.\d+)?(?:(?:\s*[-~,，、]\s*|\s*(?:以至|至|到|和|vs)\s*)\d+(?:\.\d+)?)*)\s*')"

text = text.replace(old_hybrid, new_hybrid)
text = text.replace(old_number, new_number)

# 2. Extract Date Expression
# Delete from "        # 1. Date Pattern (only if NO prefix)" until "            # 2. Number + Unit Pattern (or Prefix + Number)"
date_block_pattern = r'        # 1\. Date Pattern \(only if NO prefix\)\n.*?# 2\. Number \+ Unit Pattern \(or Prefix \+ Number\)'
text = re.sub(date_block_pattern, '        # 1. Number + Unit Pattern (or Prefix + Number)', text, flags=re.DOTALL)

# Inject _try_date_expression
date_engine_logic = """
    # ─── Date Expression ───
    
    def _try_date_expression(self, text: str, pos: int) -> 'ConversionResult | None':
        rem = text[pos:]
        
        year_prefixes = [
            ("公元前", "năm {n} trước công nguyên", True),
            ("公元", "công nguyên năm {n}", True),
            ("世纪中叶", "giữa thế kỷ {n}", False),
            ("世纪", "thế kỷ {n}", False),
            ("年代", "thập niên {n}", False),
            ("年底", "cuối năm {n}", False),
            ("年末", "cuối năm {n}", False),
            ("年初", "đầu năm {n}", False),
            ("年中", "giữa năm {n}", False)
        ]
        
        dp = HYBRID_DATE_PATTERN.match(rem)
        if dp:
            raw_month = dp.group(1).strip()
            raw_day = dp.group(2).strip()
            
            month_val = 0
            lunar_month = ""
            if raw_month.startswith("腊"):
                month_val = 12
                lunar_month = "chạp"
            elif raw_month.startswith("正"):
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
                raw_day = raw_day[1:]
            
            if raw_day.isdigit(): day_val = int(raw_day)
            else: day_val = parse_chinese_number(raw_day) or 0

            day_spelled = spell_vietnamese_number(day_val)
            if day_val <= 10 or is_mung:
                final_day = f"mùng {day_spelled}"
            else:
                final_day = f"ngày {day_spelled}"
            
            if lunar_month:
                month_spelled = lunar_month
            else:
                if month_val == 4: month_spelled = "tư"
                elif month_val == 1: month_spelled = "một"
                else: month_spelled = spell_vietnamese_number(month_val)
                
            return ConversionResult(
                text=f"{final_day} tháng {month_spelled}",
                consumed=dp.end(),
                conv_type="date_hybrid"
            )
            
        for prefix, template, is_prefix in year_prefixes:
            if is_prefix:
                if rem.startswith(prefix):
                    np = NUMBER_START_PATTERN.match(rem[len(prefix):])
                    if np:
                        num_str = np.group(1)
                        consumed_extra = 1 if rem[len(prefix) + np.end():].startswith('年') else 0
                        return ConversionResult(
                            text=template.replace("{n}", num_str),
                            consumed=len(prefix) + np.end() + consumed_extra,
                            conv_type="year_prefix"
                        )
            else:
                np = NUMBER_START_PATTERN.match(rem)
                if np:
                    num_str = np.group(1)
                    rem_after = rem[np.end():]
                    if rem_after.startswith(prefix):
                        return ConversionResult(
                            text=template.replace("{n}", num_str),
                            consumed=np.end() + len(prefix),
                            conv_type="year_suffix"
                        )
        return None
"""
text = text.replace('    # ─── Arabic Unit / Date ───', date_engine_logic + '\n    # ─── Arabic Unit / Date ───')

new_try_convert = """        result = self._try_date_expression(text, pos)
        if result:
            return result

        result = self._try_arabic_unit(text, pos)"""
text = text.replace('        result = self._try_arabic_unit(text, pos)', new_try_convert)

# 3. Add to ARABIC_UNIT_TEMPLATES
additions = """    "米多长": "dài hơn {n} mét",
    "米来长": "dài {n} mét",
    "米多高": "cao hơn {n} mét",
    "米来高": "cao {n} mét",
    "分钟之内": "trong vòng {n} phút",
    "小时之内": "trong vòng {n} giờ",
    "点多": "hơn {n} giờ","""
text = text.replace('"W": "{n}0 ngàn",', additions + '\n    "W": "{n}0 ngàn",')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("NumberConverter advanced range & date parser injected.")
