#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

def patch_file():
    fp = Path("d:/Converter by DrDuc/src/engine/number_converter.py")
    if not fp.exists(): return
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
        
    repl1_target = "from typing import Optional"
    repl1_source = """import re
from typing import Optional

# ─────────────────────────────────────────────────
# Arabic Unit and Date Templates
# ─────────────────────────────────────────────────

ARABIC_UNIT_TEMPLATES = {
    # Length/Height
    "米长": "dài {n} mét",
    "米高": "cao {n} mét",
    "公分长": "dài {n} cm",
    "公分高": "cao {n} cm",
    "米": "{n} mét",
    "公分": "{n} cm",
    "厘米": "{n} cm",
    "里": "{n} dặm",
    
    # Weight
    "斤重": "nặng {n} cân",
    "公斤重": "nặng {n} kg",
    "吨重": "nặng {n} tấn",
    "斤": "{n} cân",
    "公斤": "{n} kg",
    "吨": "{n} tấn",
    "两": "{n} lượng",
    
    # Time/Date
    "年": "năm {n}",
    "点半钟": "{n} giờ rưỡi",
    "点半": "{n} giờ rưỡi",
    "点钟": "{n} giờ",
    "点": "{n} giờ",
    "分钟": "{n} phút",
    "分": "{n} phút",
    "秒钟": "{n} giây",
    "秒": "{n} giây",
    "周岁": "{n} tuổi",
    "日岁": "{n} tuổi",
    "月岁": "{n} tuổi",
    "岁": "{n} tuổi",
    "天": "{n} ngày",
    "号": "số {n}",
    
    # Other
    "W": "{n}0 ngàn",
    "万": "{n} vạn",
    "级": "cấp {n}",
    "只": "{n} con",
    "张": "{n} tấm",
    
    # Range / Approximation
    "多公斤重": "nặng hơn {n} kg",
    "多斤重": "nặng hơn {n} cân",
    "多公分长": "dài hơn {n} cm",
    "多公分高": "cao hơn {n} cm",
    "多米长": "dài hơn {n} mét",
    "多米高": "cao hơn {n} mét",
    
    "余米": "hơn {n} mét",
    "多米": "hơn {n} mét",
    "多公分": "hơn {n} cm",
    "多公斤": "hơn {n} kg",
    "多斤": "hơn {n} cân",
    "多张": "hơn {n} tấm",
    "多万": "hơn {n} vạn",
    "多只": "hơn {n} con",
    "多": "hơn {n}",
}

DATE_PATTERN = re.compile(r'^(\\d+)\\s*月\\s*(\\d+)\\s*[号日]')
NUMBER_START_PATTERN = re.compile(r'^(\\d+(?:\\.\\d+)?)\\s*')"""

    content = content.replace(repl1_target, repl1_source)
    
    repl2_target = """            3. Pure number      (三千四百五十六)
        \"\"\"
        result = self._try_weekday(text, pos)"""
    
    repl2_source = """            3. Pure number      (三千四百五十六)
        \"\"\"
        result = self._try_arabic_unit(text, pos)
        if result:
            return result

        result = self._try_weekday(text, pos)"""
        
    content = content.replace(repl2_target, repl2_source)
    
    repl3_target = """        )

    # ─── Pure Number ───"""
    
    repl3_source = """        )

    # ─── Arabic Unit / Date ───

    def _try_arabic_unit(self, text: str, pos: int) -> ConversionResult | None:
        if not text[pos].isdigit():
            return None
            
        remaining = text[pos:]
        
        # 1. Date Pattern
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
            
        # 2. Number + Unit Pattern
        np = NUMBER_START_PATTERN.match(remaining)
        if np:
            num_str = np.group(1)
            num_clean = str(float(num_str)) if '.' in num_str else str(int(num_str))
            
            consumed_chars = np.end()
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
                )
                
        return None

    # ─── Pure Number ───"""
    
    content = content.replace(repl3_target, repl3_source)
    
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Patched {fp}")

if __name__ == '__main__':
    patch_file()
