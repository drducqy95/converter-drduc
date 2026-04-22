import re

file_path = "src/engine/number_converter.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update NUMBER_START_PATTERN to support "75. 5"
old_number = r"NUMBER_START_PATTERN = re.compile(r'^(\d+(?:\.\d+)?(?:(?:\s*[-~,，、]\s*|\s*(?:以至|至|到|和|vs)\s*)\d+(?:\.\d+)?)*)\s*')"
new_number = r"NUMBER_START_PATTERN = re.compile(r'^(\d+(?:\.\s*\d+)?(?:(?:\s*[-~,，、]\s*|\s*(?:以至|至|到|和|vs)\s*)\d+(?:\.\s*\d+)?)*)\s*')"
text = text.replace(old_number, new_number)

# 2. Add 端月 to HYBRID_DATE_PATTERN
old_hybrid = r"HYBRID_DATE_PATTERN = re.compile(rf'^((?:腊|正|冬)?(?:\d+|[{CH_NUM_CHARS}]+)?)\s*月\s*(初?\s*(?:\d+|[{CH_NUM_CHARS}]+))\s*(?:号|日)?')"
new_hybrid = r"HYBRID_DATE_PATTERN = re.compile(rf'^((?:腊|正|冬|端)?(?:\d+|[{CH_NUM_CHARS}]+)?)\s*月\s*(初?\s*(?:\d+|[{CH_NUM_CHARS}]+))\s*(?:号|日)?')"
text = text.replace(old_hybrid, new_hybrid)

# 3. Add 端月 logic & day spelled check
old_lunar = """            elif raw_month.startswith("冬"):
                month_val = 11"""
new_lunar = """            elif raw_month.startswith("冬"):
                month_val = 11
            elif raw_month.startswith("端"):
                month_val = 1"""
text = text.replace(old_lunar, new_lunar)

# 4. Add "百分之\s*X" prefix
old_arabic_prefix = """ARABIC_PREFIX_TEMPLATES = {
    "群": "nhóm {n}","""
new_arabic_prefix = """ARABIC_PREFIX_TEMPLATES = {
    "百分之": "{n}%",
    "群": "nhóm {n}","""
text = text.replace(old_arabic_prefix, new_arabic_prefix)

# 5. Add "多码", "天之内", etc.
additions = """    "多码": "hơn {n} yard",
    "天之内": "trong vòng {n} ngày",
    "点到了": "đến {n} giờ rồi",
    "中队": "trung đội {n}",
    "胜": "thắng {n}","""
text = text.replace('"W": "{n}0 ngàn",', additions + '\n    "W": "{n}0 ngàn",')

# 6. Time Expression standalone minutes
time_standalone = """        if rem.startswith("点") or rem.startswith("分"):
            import re
            m = re.match(r'^点\s*(\d+)\s*分', rem)
            if m:
                return ConversionResult(text=f"giờ {m.group(1)} phút", consumed=m.end(), conv_type="time_standalone")
            m = re.match(r'^分\s*(\d+)\s*秒', rem)
            if m:
                return ConversionResult(text=f"phút {m.group(1)} giây", consumed=m.end(), conv_type="time_standalone")
                
        match_prefix = None"""

text = text.replace('        match_prefix = None', time_standalone)

# 7. Add 快点钟 and trưa 11 rules in time suffixes
old_am_pm = """if val == 12 and match_prefix[0] in ("早晨", "上午", "中午"):
                        period = "trưa"
                    formatted += f" {period}\""""
new_am_pm = """if val >= 11 and match_prefix[0] in ("早晨", "上午", "中午"):
                        period = "trưa"
                    if val <= 3 and match_prefix[0] in ("早晨", "早上"):
                        period = "sáng"
                    formatted += f" {period}\""""
text = text.replace(old_am_pm, new_am_pm)

time_additions = """            "快点钟": "sắp {n:spell} giờ",
            "快点半": "sắp {n:spell} giờ rưỡi",
            "快点": "sắp {n:spell} giờ",
            "点钟的时候": "lúc {n:spell} giờ", """
text = text.replace('"点钟的时候": "lúc {n:spell} giờ",', time_additions)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Patch 5 applied.")
