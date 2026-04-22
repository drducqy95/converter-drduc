#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

def patch_file():
    fp = Path("d:/Converter by DrDuc/src/engine/number_converter.py")
    if not fp.exists(): return
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
        
    repl1_target = """ARABIC_UNIT_TEMPLATES = {"""
    repl1_source = """ARABIC_UNIT_TEMPLATES = {
    "月底": "cuối tháng {n}",
    "万多": "hơn {n} vạn",
    "区": "khu {n}","""
    
    content = content.replace(repl1_target, repl1_source)
    
    repl2_target = """DATE_PATTERN = re.compile(r'^(\\d+)\\s*月\\s*(\\d+)\\s*[号日]')"""
    repl2_source = """ARABIC_PREFIX_TEMPLATES = {
    "群": "nhóm {n}",
    "第": "thứ {n}",
    "区": "khu {n}", 
    "室": "phòng {n}",
    "房": "phòng {n}",
    "座": "tòa {n}",
    "号": "số {n}",
    "楼": "tầng {n}",
}

DATE_PATTERN = re.compile(r'^(\\d+)\\s*月\\s*(\\d+)\\s*[号日]')"""

    content = content.replace(repl2_target, repl2_source)
    
    repl3_target = """    def _try_arabic_unit(self, text: str, pos: int) -> ConversionResult | None:
        if not text[pos].isdigit():
            return None
            
        remaining = text[pos:]
        
        # 1. Date Pattern"""
    
    repl3_source = """    def _try_arabic_unit(self, text: str, pos: int) -> ConversionResult | None:
        prefix_used = None
        start_pos = pos
        
        # Check if the current character is a known prefix
        prefix_cand = text[pos:pos+1]
        if prefix_cand in ARABIC_PREFIX_TEMPLATES:
            temp_pos = pos + 1
            while temp_pos < len(text) and text[temp_pos].isspace():
                temp_pos += 1
            if temp_pos < len(text) and text[temp_pos].isdigit():
                prefix_used = prefix_cand
                start_pos = temp_pos
                
        if start_pos >= len(text) or not text[start_pos].isdigit():
            return None
            
        remaining = text[start_pos:]
        
        # 1. Date Pattern"""

    content = content.replace(repl3_target, repl3_source)
    
    repl4_target = """        # 1. Date Pattern
        dp = DATE_PATTERN.match(remaining)
        if dp:
            month_str = dp.group(1).lstrip('0') or "0"
            day_str = dp.group(2).lstrip('0') or "0"
            day_num = int(day_str)
            day_viet = f"mùng {day_num}" if 1 <= day_num <= 10 else str(day_num)
            return ConversionResult(
                text=f"ngày {day_viet} tháng {month_str}",
                consumed=dp.end(),
                conv_type="arabic_date"
            )
            
        # 2. Number + Unit Pattern"""
        
    repl4_source = """        # 1. Date Pattern (only if NO prefix)
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
                )
            
        # 2. Number + Unit Pattern (or Prefix + Number)"""
        
    content = content.replace(repl4_target, repl4_source)
    
    repl5_target = """            consumed_chars = np.end()
            text_after = remaining[consumed_chars:]
            
            best_match_unit = None
            for unit in sorted(ARABIC_UNIT_TEMPLATES.keys(), key=len, reverse=True):
                if text_after.startswith(unit):
                    best_match_unit = unit
                    break
                    
            if best_match_unit:
                template = ARABIC_UNIT_TEMPLATES[best_match_unit]
                formatted_text = template.replace("{n}", num_clean)
                
                consumed = consumed_chars + len(best_match_unit)
                trailing = remaining[consumed:]
                
                if trailing.startswith("左右"):
                    formatted_text = "khoảng " + formatted_text
                    consumed += 2
                elif trailing.startswith("以内") or trailing.startswith("内"):
                    sz = 2 if trailing.startswith("以内") else 1
                    formatted_text = "trong vòng " + formatted_text
                    consumed += sz
                elif trailing.startswith("之后") or trailing.startswith("后"):
                    sz = 2 if trailing.startswith("之后") else 1
                    formatted_text = "sau " + formatted_text
                    consumed += sz
                    
                return ConversionResult(
                    text=formatted_text,
                    consumed=consumed,
                    conv_type="arabic_unit"
                )"""
    
    repl5_source = """            consumed_after_num = np.end()
            text_after = remaining[consumed_after_num:]
            
            if prefix_used:
                template = ARABIC_PREFIX_TEMPLATES[prefix_used]
                formatted_text = template.replace("{n}", num_clean)
                consumed_total = (start_pos - pos) + consumed_after_num
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
                    formatted_text = template.replace("{n}", num_clean)
                    
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
                        
                    return ConversionResult(
                        text=formatted_text,
                        consumed=consumed_local,
                        conv_type="arabic_unit"
                    )"""
                    
    content = content.replace(repl5_target, repl5_source)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Patched prefix capabilities into {fp}")

if __name__ == '__main__':
    patch_file()
