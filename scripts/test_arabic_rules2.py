import re
from dataclasses import dataclass

@dataclass
class ConversionResult:
    text: str
    consumed: int
    conv_type: str

ARABIC_UNIT_TEMPLATES = {
    "米长": "dài {n} mét",
    "米高": "cao {n} mét",
    "公分长": "dài {n} cm",
    "公分高": "cao {n} cm",
    "米": "{n} mét",
    "公分": "{n} cm",
    "厘米": "{n} cm",
    "里": "{n} dặm",
    "斤重": "nặng {n} cân",
    "公斤重": "nặng {n} kg",
    "吨重": "nặng {n} tấn",
    "斤": "{n} cân",
    "公斤": "{n} kg",
    "吨": "{n} tấn",
    "两": "{n} lượng",
    "月底": "cuối tháng {n}",
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
    "W": "{n}0 ngàn",
    "万多": "hơn {n} vạn",
    "万": "{n} vạn",
    "级": "cấp {n}",
    "只": "{n} con",
    "张": "{n} tấm",
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

ARABIC_PREFIX_TEMPLATES = {
    "群": "nhóm {n}",
    "第": "thứ {n}",
    "区": "khu {n}", 
    "室": "phòng {n}",
    "房": "phòng {n}",
    "座": "tòa {n}",
    "号": "số {n}",
    "楼": "tầng {n}",
}

DATE_PATTERN = re.compile(r'^(\d+)\s*月\s*(\d+)\s*[号日]')
NUMBER_START_PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*')

class ArabicUnitConverter:
    def try_convert(self, text: str, pos: int) -> ConversionResult | None:
        prefix_used = None
        start_pos = pos
        
        # Check if the current character is a known prefix
        prefix_cand = text[pos:pos+1]
        if prefix_cand in ARABIC_PREFIX_TEMPLATES:
            # Look ahead to see if it's followed by a number
            temp_pos = pos + 1
            while temp_pos < len(text) and text[temp_pos].isspace():
                temp_pos += 1
            if temp_pos < len(text) and text[temp_pos].isdigit():
                prefix_used = prefix_cand
                start_pos = temp_pos
                
        if start_pos >= len(text) or not text[start_pos].isdigit():
            return None
            
        remaining = text[start_pos:]
        
        # 1. Date Pattern (only if NO prefix)
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
            
        # 2. Number + Unit Pattern (or Prefix + Number)
        np = NUMBER_START_PATTERN.match(remaining)
        if np:
            num_str = np.group(1)
            num_clean = str(float(num_str)) if '.' in num_str else str(int(num_str))
            
            consumed_after_num = np.end()
            text_after = remaining[consumed_after_num:]
            
            # If we had a prefix, we don't strictly *need* a suffix. But what if it has both? 
            # Example: "第 1 楼" -> "tầng thứ 1"? For now, just consume prefix + number.
            
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
                        consumed=consumed_local, # pos == start_pos when no prefix
                        conv_type="arabic_unit"
                    )
                    
        return None

if __name__ == '__main__':
    conv = ArabicUnitConverter()
    cases = [
        "9月底",
        "4万多",
        "5月底",
        "群 5",
        "群5",
        "区 12",
        "12 区",
        "第 1"
    ]
    for c in cases:
        res = conv.try_convert(c, 0)
        print(f"'{c}' ->", res)
