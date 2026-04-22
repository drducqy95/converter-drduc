import re

_PERSON_NOUNS = r"nam tử|nữ tử|thiếu niên|bà lão|ông già|đàn ông|phụ nữ|nam nhân|nữ nhân|đạo sĩ|hòa thượng|đại hán|sinh viên|thanh niên|cô gái|chàng trai|người"
_ACTION_VERBS = r"mặc|đeo|cầm|đội|cõng|ôm|mang|mang theo"

_INVERSION_PATTERN = re.compile(
    rf"\b((?:một\s+)?(?:người|tên|kẻ|cái|vị)\s+)?({_ACTION_VERBS})\s+((?:[a-z\xC0-\u1EF9A-Z]+\s*){{1,6}}?)({_PERSON_NOUNS})\b",
    re.IGNORECASE
)

def apply_inversion(text: str) -> str:
    def replacer(match):
        prefix = match.group(1) or ""
        verb = match.group(2)
        modifier = match.group(3).strip()
        noun = match.group(4)
        
        # If prefix is "Một người " and noun is "nam tử", we can just say "Một nam tử"
        if prefix.lower() == "một người ":
            prefix = "một "
        elif prefix.lower() == "người ":
            prefix = ""
            
        return f"{prefix}{noun} {verb} {modifier}"

    return _INVERSION_PATTERN.sub(replacer, text)

texts = [
    "Một người mặc màu đen áo gió nam tử quỳ gối lạng ghế ngồi bia mộ trước mặt",
    "người mặc màu đen áo gió thiếu niên đang đứng",
    "Đó là một vị cầm kiếm thiếu niên",
    "kẻ mang khẩu trang nam nhân",
    "mặc áo liệm tóc màu trắng trắng bà lão" 
]

for t in texts:
    print(f"[{t}]\n => {apply_inversion(t)}\n")
