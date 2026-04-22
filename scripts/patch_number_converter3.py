#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

def patch_file():
    fp = Path("d:/Converter by DrDuc/src/engine/number_converter.py")
    if not fp.exists(): return
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Expand the ARABIC_UNIT_TEMPLATES to remove `年` and add new suffixes.
    repl1_target = """    "两": "{n} lượng",
    "月底": "cuối tháng {n}",
    "年": "năm {n}",
    "点半钟": "{n} giờ rưỡi","""
    repl1_source = """    "两": "{n} lượng",
    "月底": "cuối tháng {n}",
    "年多": "hơn {n} năm",
    "年左右": "khoảng {n} năm",
    "点多": "hơn {n} giờ",
    "寸": "{n} tấc",
    "码": "{n} yard",
    "点半钟": "{n} giờ rưỡi","""
    if repl1_target in content:
        content = content.replace(repl1_target, repl1_source)
    else:
        print("Could not find repl1_target")

    # 2. Add `乘以` to Prefix Templates
    repl2_target = """    "楼": "tầng {n}",
}"""
    repl2_source = """    "楼": "tầng {n}",
    "乘以": "nhân với {n}",
}"""
    if repl2_target in content:
        content = content.replace(repl2_target, repl2_source)
    else:
        print("Could not find repl2_target")

    # 3. Replace DATE_PATTERN regex and logic
    # Find the DATE_PATTERN regex line:
    repl3_target = """DATE_PATTERN = re.compile(r'^(\\d+)\\s*月\\s*(\\d+)\\s*[号日]')"""
    repl3_source = """CH_NUM_CHARS = "0123456789零〇一壹二贰貳两兩三叁參四肆五伍六陆陸七柒八捌九玖十拾百佰千仟万萬"
HYBRID_DATE_PATTERN = re.compile(rf'^((?:腊|正|冬)?(?:[{CH_NUM_CHARS}]+)?)\\s*月\\s*(初?[{CH_NUM_CHARS}]+)\\s*(?:号|日)?')"""
    if repl3_target in content:
        content = content.replace(repl3_target, repl3_source)
    else:
        print("Could not find repl3_target")

    # 4. Replace parsing logic inside _try_arabic_unit
    repl4_target = """        # 1. Date Pattern (only if NO prefix)
        if not prefix_used:
            dp = DATE_PATTERN.match(remaining)
            if dp:
                month_str = dp.group(1).lstrip('0') or "0"
                day_str = dp.group(2).lstrip('0') or "0"
                day_num = int(day_str)
                day_viet = f"mùng {day_num}" if 1 <= day_num <= 10 else str(day_num)
                return ConversionResult(
                    text=f"ngày {day_viet} tháng {month_str}",
                    consumed=start_pos - pos + dp.end(),
                    conv_type="arabic_date"
                )"""
    repl4_source = """        # 1. Date Pattern (only if NO prefix)
        if not prefix_used:
            dp = HYBRID_DATE_PATTERN.match(remaining)
            if dp:
                raw_month = dp.group(1).strip()
                raw_day = dp.group(2).strip()
                
                # Evaluate Month
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
                
                # Evaluate Day
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
                    elif month_val == 1: month_spelled = "một"  # January
                    else: month_spelled = spell_vietnamese_number(month_val)
                    
                return ConversionResult(
                    text=f"{final_day} tháng {month_spelled}",
                    consumed=start_pos - pos + dp.end(),
                    conv_type="arabic_date"
                )"""
    if repl4_target in content:
        content = content.replace(repl4_target, repl4_source)
    else:
        print("Could not find repl4_target")

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Successfully patched hybrid dates and specific requirements.")

if __name__ == '__main__':
    patch_file()
