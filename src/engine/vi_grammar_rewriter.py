#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post-translation Vietnamese grammar rewriter.

Applies structural transformations to translated text to conform
to Vietnamese word order (e.g., Noun + Adj instead of Adj + Noun).
"""

from __future__ import annotations

import re

# ━━━ 1. Adj-Noun reordering ━━━
# Chinese:  Adj + Noun  →  Vietnamese: Noun + Adj
# E.g.: "màu đen áo gió" → "áo gió màu đen"

_COLOR_WORDS = (
    "đen", "trắng", "đỏ", "xanh", "vàng", "tím", "hồng", "nâu", "xám",
    "bạc", "cam", "lam", "lục", "xanh lá", "xanh dương",
)
_COLOR_PATTERN = "|".join(re.escape(c) for c in sorted(_COLOR_WORDS, key=len, reverse=True))

_CLOTHING_NOUNS = (
    "áo gió", "áo liệm", "áo choàng", "áo khoác", "áo dài", "áo vest", "áo sơ mi",
    "giày cao gót", "giày", "dép", "quần", "váy", "mũ", "khăn", "găng tay",
    "tất", "bít tất", "nón", "mũ lưỡi trai",
)
_CLOTHING_PATTERN = "|".join(re.escape(n) for n in sorted(_CLOTHING_NOUNS, key=len, reverse=True))

# Pattern: "màu X noun" → "noun màu X"
_ADJ_NOUN_COLOR_CLOTHING = re.compile(
    rf"\b(màu\s+(?:{_COLOR_PATTERN}))\s+({_CLOTHING_PATTERN})\b",
    flags=re.IGNORECASE,
)

# Pattern: "màu X noun" for body parts
_BODY_PARTS = (
    "nhãn cầu", "mắt", "tóc", "da", "môi", "lưỡi", "răng",
    "bột phấn", "xương", "hạt châu",
)
_BODY_PATTERN = "|".join(re.escape(n) for n in sorted(_BODY_PARTS, key=len, reverse=True))

_ADJ_NOUN_COLOR_BODY = re.compile(
    rf"\b(màu\s+(?:{_COLOR_PATTERN}))\s+({_BODY_PATTERN})\b",
    flags=re.IGNORECASE,
)

# General adjectives before nouns
_GENERAL_ADJ = (
    "nhỏ bé", "to lớn", "cao lớn", "thấp bé", "mập mạp", "gầy gò",
    "xinh đẹp", "xấu xí", "cũ kỹ", "mới mẻ",
)
_GENERAL_ADJ_PATTERN = "|".join(re.escape(a) for a in sorted(_GENERAL_ADJ, key=len, reverse=True))

_GENERAL_NOUNS = (
    "ngôi nhà", "tòa nhà", "cánh cửa", "chiếc xe", "con đường",
    "ngọn núi", "dòng sông", "toà cầu",
)
_GENERAL_NOUN_PATTERN = "|".join(re.escape(n) for n in sorted(_GENERAL_NOUNS, key=len, reverse=True))

_ADJ_NOUN_GENERAL = re.compile(
    rf"\b({_GENERAL_ADJ_PATTERN})\s+({_GENERAL_NOUN_PATTERN})\b",
    flags=re.IGNORECASE,
)


# ━━━ 2. Common mistranslation patterns ━━━
# Patterns where the word-by-word translation produces wrong Vietnamese

_REORDER_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # "mặc màu X áo Y" → "mặc áo Y màu X"
    (re.compile(r"\bmặc (màu\s+\S+)\s+(áo\s+\S+)", re.IGNORECASE), r"mặc \2 \1"),
    # "người mặc màu X áo Y" → "người mặc áo Y màu X"
    (re.compile(r"\bngười mặc (màu\s+\S+)\s+(áo\s+\S+)", re.IGNORECASE), r"người mặc \2 \1"),
    # "đôi X cm màu Y giày Z" → "đôi giày Z màu Y X cm"
    (re.compile(r"\bđôi\s+(?:chí\s+ít\s+)?(\d+)\s*cm\s+(màu\s+\S+)\s+(giày\s+cao\s+gót)", re.IGNORECASE), r"đôi \3 \2 \1 cm"),
    # "một đầu bị bỏng cuốn cuốn trong tóc" → "một đầu tóc bị bỏng cuốn cuốn"
    (re.compile(r"\bmột đầu bị bỏng cuốn cuốn trong tóc\b", re.IGNORECASE), "một đầu tóc cuốn xoăn"),
]


# ━━━ 3. Measure word correction ━━━
# Chinese measure words often translate literally; Vietnamese uses different classifiers

_MEASURE_WORD_MAP: dict[str, dict[str, str]] = {
    # "一座山" → trie gives "một tòa núi", should be "một ngọn núi"
    "tòa": {
        "núi": "ngọn",
        "cầu": "cây",
    },
    "cái": {
        "giờ": "",  # "nửa cái giờ" → "nửa giờ"
    },
    "khối": {
        "bia mộ": "tấm",
    },
}

_MEASURE_PATTERNS: list[tuple[re.Pattern[str], str]] = []
for _mw, _noun_map in _MEASURE_WORD_MAP.items():
    for _noun, _replacement in _noun_map.items():
        if _replacement:
            _MEASURE_PATTERNS.append((
                re.compile(rf"\b{re.escape(_mw)}\s+{re.escape(_noun)}\b", re.IGNORECASE),
                f"{_replacement} {_noun}",
            ))
        else:
            _MEASURE_PATTERNS.append((
                re.compile(rf"\b{re.escape(_mw)}\s+{re.escape(_noun)}\b", re.IGNORECASE),
                _noun,
            ))


# ━━━ 4. Misc grammar fixes ━━━
_MISC_FIXES: list[tuple[re.Pattern[str], str]] = [
    # "nửa cái giờ" → "nửa giờ"
    (re.compile(r"\bnửa cái giờ\b", re.IGNORECASE), "nửa tiếng"),
    # "bản tọa" in internal monologue context — keep as-is for now (complex to detect)
    # "lạng ghế ngồi" → "lạnh lẽo" (specific mis-compound, handled by phrase override)
    # "Liên Mang" → "vội vàng" (handled by terminology blacklist)
    # Double-adjective patterns like "mập lùn mập lùn" → "mập lùn"
    (re.compile(r"\b(mập lùn)\s+\1\b", re.IGNORECASE), r"\1"),
    # "nhìn chằm chằm" duplication fix
    # "tiếp lấy" → "tiếp đó"  
    (re.compile(r"\btiếp lấy\b", re.IGNORECASE), "tiếp đó"),
    # "tự nhiên" (overuse when meaning "đương nhiên")
    # "theo trong" → "từ trong"
    (re.compile(r"\btheo trong\b", re.IGNORECASE), "từ trong"),
    # "hướng phía" → "về phía"
    (re.compile(r"\bhướng phía\b", re.IGNORECASE), "về phía"),
    # "thì ra" should stay, but "thì đi" patterns
    # "so với thẳng" → "thẳng tắp" (posture)
    (re.compile(r"\bso với thẳng\b", re.IGNORECASE), "thẳng tắp"),
    # "ngay lập tức" duplicate cleanup
    (re.compile(r"\b(ngay lập tức)\s+\1\b", re.IGNORECASE), r"\1"),
    # "của mình" vs possessive handling
    # "chằm chằm vào" standardization
    (re.compile(r"\bchằm chằm vào\b"), "nhìn chằm chằm"),
    # "không nhúc nhích" → "bất động"
    (re.compile(r"\bkhông nhúc nhích\b", re.IGNORECASE), "bất động"),
    # "cực kỳ" placement — already correct in Vietnamese
    # "tả hữu" → "khoảng" (for age/number approximation)
    (re.compile(r"\b(\d+)\s+tả hữu\b"), r"khoảng \1"),
    # "đình chỉ" → "ngừng" (in flow context)
    (re.compile(r"\bđình chỉ\b", re.IGNORECASE), "ngừng"),
    # "thầm nói" → "thầm nghĩ" or "lẩm bẩm"
    (re.compile(r"\bthầm nói\b", re.IGNORECASE), "lẩm bẩm"),
    # "liên phát" → "cả" (连...都)
    (re.compile(r"\bliên phát\b", re.IGNORECASE), "cả"),
    # "lão thái thái" → "bà lão"
    (re.compile(r"\blão thái thái\b", re.IGNORECASE), "bà lão"),
    (re.compile(r"\blão thái\b", re.IGNORECASE), "bà lão"),
    # "đại cổ đại cổ" → "từng ngụm từng ngụm"
    (re.compile(r"\bđại cổ đại cổ\b", re.IGNORECASE), "từng ngụm từng ngụm"),
    # "tiểu gia băng" → "nhóc con"
    (re.compile(r"\btiểu gia băng\b", re.IGNORECASE), "nhóc con"),
    # "hung hăng" when meaning "liều mạng/hết sức"
    (re.compile(r"\bhung hăng cự tuyệt\b", re.IGNORECASE), "kiên quyết từ chối"),
    (re.compile(r"\bhung hăng địa\b", re.IGNORECASE), "hết sức"),
    # "sử thi thần khí" → "thần khí sử thi" (adj-noun)
    (re.compile(r"\bsử thi thần khí\b", re.IGNORECASE), "thần khí cấp sử thi"),
]


# ━━━ 5. Location Reordering ━━━
# "Thiên Phủ Thị Kim Khê Huyền" → "Huyện Kim Khê, Thành phố Thiên Phủ"
# Uses lazy matching for city names to handle multi-word titles
_LOCATION_REORDER = re.compile(
    r"\b([A-Z\xC0-\u1EF9][a-z\xC0-\u1EF9]+(?:\s+[A-Z\xC0-\u1EF9][a-z\xC0-\u1EF9]+)*)\s+Thị\s+([A-Z\xC0-\u1EF9][a-z\xC0-\u1EF9]+(?:\s+[A-Z\xC0-\u1EF9][a-z\xC0-\u1EF9]+)*)\s+Huyền\b"
)

# ━━━ 6. Modern Dialogue Pronouns ━━━
_MODERN_PRONOUNS = [
    (re.compile(r"\bbản tọa nhóm\b", re.IGNORECASE), "chúng tôi"),
    (re.compile(r"\bbản tọa\b", re.IGNORECASE), "ta"),
    (re.compile(r"\blão mụ\b", re.IGNORECASE), "mẹ"),
    (re.compile(r"\blão ba\b", re.IGNORECASE), "ba"),
    (re.compile(r"\bcô gái tử\b", re.IGNORECASE), "đám con gái"),
]

# ━━━ 7. Possession "của" ━━━
_PRONOUNS_OWNER = r"[Bb]à lão|[Ôô]ng già|[Hh]ắn|[Nn]àng|[Tt]a|[Nn]gươi|[Nn]ó|[Cc]ô ấy|[Aa]nh ấy"
_PROPER_NAME = r"[A-Z\xC0-\u1EF9][a-z\xC0-\u1EF9]+"

# Rule 1: "Noun [Name/Pronoun]" -> "Noun của [Name/Pronoun]"
_POSSESSION_NOUN_OWNER = re.compile(
    rf"\b({_CLOTHING_PATTERN}|{_BODY_PATTERN}|thân thể|mộ phần|ánh mắt|nước mắt|nhãn cầu|cơ thể|bàn tay|bắp chân|yết hầu)\s+({_PRONOUNS_OWNER}|{_PROPER_NAME})\b"
)

# Rule 2: "[Name/Pronoun] Noun" -> "Noun của [Name/Pronoun]"
_POSSESSION_OWNER_NOUN = re.compile(
    rf"\b({_PRONOUNS_OWNER}|{_PROPER_NAME})\s+({_BODY_PATTERN}|thân thể|mộ phần|bia mộ|ghế ngồi|bắp chân|yết hầu)\b"
)

# ━━━ 8. Distance & Prepositions ━━━
_PREPOSITION_FIXES = [
    (re.compile(r"\bly\s+(.+?)\s+cách đó không xa\b", re.IGNORECASE), r"cách \1 không xa"),
    (re.compile(r"\bđối diện\s+((?:nàng|hắn|ta|ngươi|[A-Z\xC0-\u1EF9][a-z\xC0-\u1EF9]+))\b", re.IGNORECASE), r"đối diện với \1"),
]


# ━━━ 9. Section Headings & Titles ━━━
# "# Thiên thứ nhất thấm nước trẻ sơ sinh chương thứ nhất" -> "# Quyển 1: Thấm nước trẻ sơ sinh - Chương 1"
_ORDINAL_MAP = {
    "nhất": "1", "hai": "2", "ba": "3", "bốn": "4", "năm": "5",
    "sáu": "6", "bảy": "7", "tám": "8", "chín": "9", "mười": "10",
}

_SECTION_HEADING = re.compile(
    r"(#+)\s+Thiên\s+(?:thứ\s+)?([a-z\d\xC0-\u1EF9]+)\s+(.+?)\s+chương\s+(?:thứ\s+)?([a-z\d\xC0-\u1EF9]+)",
    re.IGNORECASE
)

def _heading_format(match: re.Match) -> str:
    hashes, vol, title, chap = match.groups()
    vol = _ORDINAL_MAP.get(vol.lower(), vol)
    chap = _ORDINAL_MAP.get(chap.lower(), chap)
    return f"{hashes} Quyển {vol}: {title.strip(' :')} - Chương {chap}"

# ━━━ 10. Character / NP Possession ━━━
# "móng vuốt nhãn cầu" pattern (rare) or specific NPC possessives
_NP_POSSESSION = re.compile(
    rf"\b({_BODY_PATTERN}|thân thể|hơi lạnh|tiếng thét|móng vuốt)\s+({_PRONOUNS_OWNER}|{_PROPER_NAME}(?:\s+{_PROPER_NAME})*)\b"
)

def rewrite_vietnamese_grammar(text: str, genre: str = "general") -> str:
    """Apply Vietnamese grammar reordering rules to translated text."""
    
    # 0. Section headings
    text = _SECTION_HEADING.sub(_heading_format, text)

    # 1. Location reorder
    text = _LOCATION_REORDER.sub(r"Huyện \2, Thành phố \1", text)

    # 2. Color + clothing reorder
    text = _ADJ_NOUN_COLOR_CLOTHING.sub(r"\2 \1", text)
    text = _ADJ_NOUN_COLOR_BODY.sub(r"\2 \1", text)

    # 3. General adj + noun reorder
    text = _ADJ_NOUN_GENERAL.sub(r"\2 \1", text)

    # 4. Possession (NP/Character)
    text = _POSSESSION_OWNER_NOUN.sub(r"\2 của \1", text)
    text = _NP_POSSESSION.sub(r"\1 của \2", text)
    text = _POSSESSION_NOUN_OWNER.sub(r"\1 của \2", text)

    # 5. Modern pronouns & vocab naturalization
    if genre in {"modern", "horror", "suspense", "general"}:
        for pattern, replacement in _MODERN_PRONOUNS:
            text = pattern.sub(replacement, text)

    # 6. Specific reorder patterns
    for pattern, replacement in _REORDER_PATTERNS:
        text = pattern.sub(replacement, text)

    # 7. Measure word corrections
    for pattern, replacement in _MEASURE_PATTERNS:
        text = pattern.sub(replacement, text)

    # 8. Distance & Prepositions
    for pattern, replacement in _PREPOSITION_FIXES:
        text = pattern.sub(replacement, text)

    # 9. Misc grammar fixes
    for pattern, replacement in _MISC_FIXES:
        text = pattern.sub(replacement, text)

    return text
