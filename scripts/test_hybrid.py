import re
import sys
from pathlib import Path

# Add project root to path so we can import src
PROJECT_ROOT = Path("d:/Converter by DrDuc")
sys.path.insert(0, str(PROJECT_ROOT))
from src.engine.number_converter import parse_chinese_number, spell_vietnamese_number

# Build a robust regex component for numbers (Arabic + Chinese combinations)
CH_NUM_CHARS = "0123456789零〇一壹二贰貳两兩三叁參四肆五伍六陆陸七柒八捌九玖十拾百佰千仟万萬"

# Match month: Optional Lunar prefix (腊|正|冬) + Optional Chinese/Arabic digits + 月
# e.g., 6月, 九月, 腊月, 正月, 11月
MONTH_PATTERN = re.compile(rf'^((?:腊|正|冬)?([{CH_NUM_CHARS}]+)?)\s*月')

# Match day: Optional Lunar prefix (初) + Chinese/Arabic digits + 号|日
# e.g., 六日, 8日, 初六, 十二, 6
# Wait! sometimes it's just `初六` without 号/日 (like 4月初六)
# So if it has 初, the 号/日 is optional.
# Let's match a date string completely:
# [Month]月[Day](号|日)?
HYBRID_DATE_PATTERN = re.compile(rf'^((?:腊|正|冬)?(?:[{CH_NUM_CHARS}]+)?)\s*月\s*(初?[{CH_NUM_CHARS}]+)\s*(?:号|日)?')

def parse_hybrid_number(s: str) -> int:
    """Parse a string that might be Arabic '12' or Chinese '十二'."""
    if not s: return 0
    if s.isdigit(): return int(s)
    # Could be '10' and '十二' mixed? Let's just strip and try to parse
    val = parse_chinese_number(s)
    if val is not None:
        return val
    return 0

def try_hybrid_date(text: str) -> str | None:
    dp = HYBRID_DATE_PATTERN.match(text)
    if not dp:
        return None
        
    raw_month = dp.group(1).strip()
    raw_day = dp.group(2).strip()
    
    # 1. Evaluate Month
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
        month_val = parse_hybrid_number(raw_month)
        
    month_str = lunar_month if lunar_month else str(month_val)
    if month_val == 0: month_str = "0" # fallback
    
    # 2. Evaluate Day
    is_mung = False
    if raw_day.startswith("初"):
        is_mung = True
        raw_day = raw_day[1:]
        
    day_val = parse_hybrid_number(raw_day)
    
    if day_val <= 10 or is_mung:
        day_str = f"mùng {spell_vietnamese_number(day_val)}" if is_mung else f"mùng {day_val}"
        # Often mùng is printed in text instead of numbers? The user examples: "mùng sáu", "mùng tám"
        # We can either use numbers "mùng 6" or text "mùng sáu". Let's use written text for "mùng" to match user examples.
        # Wait, the user examples were: "mùng sáu tháng tư", "mười hai tháng năm".
        # Let's output spelled vietnamese number for day if it's lunar! 
        day_str = f"mùng {spell_vietnamese_number(day_val)}" if (day_val <= 10 or is_mung) else spell_vietnamese_number(day_val)
        if day_val > 10 and not is_mung:
            day_str = f"ngày {spell_vietnamese_number(day_val)}"
    else:
        # standard day
        day_str = f"ngày {spell_vietnamese_number(day_val)}"
    
    # wait, user example "6月六日" -> "ngày sáu tháng sáu"
    # "九月8日" -> "ngày tám tháng chín"
    
    # So the month is ALSO spelled out!
    month_spelled = lunar_month if lunar_month else spell_vietnamese_number(month_val)
    
    if day_val <= 10 or is_mung:
        final_day = f"mùng {spell_vietnamese_number(day_val)}"
    else:
        final_day = f"ngày {spell_vietnamese_number(day_val)}"
        
    # Wait, the user examples don't have exactly consistent spelling vs numbers, but let's spell them both.
    
    return f"{final_day} tháng {month_spelled}"

if __name__ == '__main__':
    cases = [
        "6月六日",
        "九月8日",
        "4月初六",
        "腊月初8",
        "5月十二",
        "2月初三",
        "9月初七",
        "十月2日",
        "6月初6",
        "七月初5",
        "1月十一"
    ]
    for c in cases:
        print(f"{c:10} -> {try_hybrid_date(c)}")
