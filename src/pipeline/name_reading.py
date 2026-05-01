#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Han-Viet target resolution for proper-name entities."""

from __future__ import annotations

import re

from src.core.runtime_support import DictionaryRecord, RuntimeDictionaryAccessor
from src.pipeline.term_bank import PROPER_ENTITY_TYPES, TermBank


READING_SPLIT_RE = re.compile(r"[|,;/]")
TARGET_VARIANT_SPLIT_RE = re.compile(r"[|;/]")
LATIN_TARGET_VARIANT_SPLIT_RE = re.compile(r"[|;/]")
CEDICT_NAME_MARKER_RE = re.compile(r"\b(name|proper name)\b", re.IGNORECASE)
ASCII_LATIN_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ._'’\\-]*$")
ASCII_LETTER_RE = re.compile(r"[A-Za-z]")
PAREN_RE = re.compile(r"\s*\([^)]*\)")

# The phien_am table currently contains some VietPhrase glosses before the
# actual Sino-Vietnamese reading. These overrides keep generated proper names
# in Han-Viet form until the dictionary data is cleaned at source.
NAME_CONTEXT_READING_OVERRIDES = {
    "何": "hà",
    "为": "vi",
    "国": "quốc",
    "起": "khởi",
    "长": "trường",
    "山": "sơn",
    "海": "hải",
    "河": "hà",
    "江": "giang",
    "湖": "hồ",
    "门": "môn",
    "天": "thiên",
    "日": "nhật",
    "月": "nguyệt",
    "星": "tinh",
    "人": "nhân",
    "大": "đại",
    "小": "tiểu",
    "卧": "ngọa",
    "雷": "lôi",
    "采": "thái",
    "胖": "bàn",
    "麻": "ma",
    "卡": "tạp",
    "劳": "lao",
    "内": "nội",
    "魔": "ma",
    "赤": "xích",
    "虹": "hồng",
    "约": "ước",
    "方": "phương",
    "母": "mẫu",
    "父": "phụ",
    "广": "quảng",
    "锦": "cẩm",
    "米": "mễ",
    "拉": "lạp",
    "佳": "giai",
    "谷": "cốc",
    "翔": "tường",
    "宝": "bảo",
    "混": "hỗn",
    "空": "không",
    "座": "tọa",
    "銮": "loan",
    "真": "chân",
    "实": "thực",
    "虚": "hư",
    "幻": "huyễn",
    "浮": "phù",
    "洛": "lạc",
    "阳": "dương",
}
LATIN_EXACT_OVERRIDES = {
    "米迦勒": "Michael",
}
LATIN_STRONG_CHARS = set("阿安奥欧伊艾埃卡凯莉杰森西维普罗克提夫寇拉斯哈特齐尤瑟金汤姆米迦勒尔")
LATIN_PREFIXES = ("阿", "安", "奥", "欧", "伊", "艾", "埃", "卡", "凯", "莉", "杰", "寇", "尤", "米", "汤", "普", "西")
LATIN_SUFFIXES = ("斯", "尔", "瑟", "姆", "金", "夫", "特", "克", "森", "欧", "恩", "拉")
LATIN_DIGRAPHS = {
    "普罗": "pro",
    "克提": "kti",
    "卡西": "casi",
}
LATIN_CHAR_PARTS = {
    "阿": "a",
    "安": "an",
    "奥": "o",
    "欧": "o",
    "伊": "i",
    "艾": "ai",
    "埃": "ai",
    "卡": "ka",
    "凯": "kai",
    "莉": "li",
    "杰": "je",
    "森": "sen",
    "西": "si",
    "维": "vi",
    "普": "pu",
    "罗": "ro",
    "克": "k",
    "提": "ti",
    "夫": "f",
    "寇": "ko",
    "拉": "la",
    "斯": "s",
    "哈": "ha",
    "特": "t",
    "齐": "qi",
    "祺": "ki",
    "尤": "yu",
    "瑟": "se",
    "金": "jin",
    "汤": "tom",
    "姆": "",
    "米": "mi",
    "迦": "ka",
    "勒": "el",
    "利": "li",
    "尔": "er",
    "尼": "ni",
    "恩": "en",
    "德": "de",
    "布": "bu",
    "莱": "lai",
}


class HanVietNameResolver:
    """Resolve proper-name targets without leaking glossary alternatives."""

    def __init__(self, accessor: RuntimeDictionaryAccessor, term_bank: TermBank | None = None):
        self.accessor = accessor
        self.term_bank = term_bank or TermBank()
        self._name_reading_cache: dict[str, str] = {}

    def set_term_bank(self, term_bank: TermBank | None) -> None:
        self.term_bank = term_bank

    def resolve_stored_keyword(self, source: str, entity_type: str | None = None) -> str:
        """Return exact stored-name target when the dictionary already has one."""

        normalized_type = (entity_type or "").strip().lower()
        bank_record = self._lookup_term_bank(source, normalized_type)
        if bank_record:
            return title_case_latin_or_words(bank_record.target)

        for record in self.accessor.lookup_all(source):
            if not self._is_trusted_stored_name_record(record, normalized_type):
                continue
            value = pick_best_stored_target(record.target)
            if value and not has_cjk(value):
                return title_case_latin_or_words(value)
        return ""

    def resolve_latin_target(
        self,
        source: str,
        *,
        allow_phonetic: bool = False,
        entity_type: str | None = None,
    ) -> str:
        """Resolve a Latin-script target for Western-style transliterated names."""

        override = LATIN_EXACT_OVERRIDES.get(source)
        if override:
            return override

        normalized_type = (entity_type or "").strip().lower()
        bank_record = (
            self._lookup_term_bank(source, normalized_type)
            or self._lookup_term_bank(source, "person")
            or self._lookup_term_bank(source, "")
        )
        if bank_record and is_ascii_latin_phrase(bank_record.target):
            return title_case_latin_or_words(bank_record.target)

        for record in self.accessor.lookup_all(source):
            value = self._latin_value_from_record(record, normalized_type)
            if value:
                return title_case_latin_or_words(value)

        if allow_phonetic and looks_like_latin_transliteration_source(source):
            return transliterate_western_source(source)
        return ""

    def resolve_word_by_word(self, source: str) -> str:
        """Generate Han-Viet reading one CJK character at a time."""

        parts: list[str] = []
        has_cjk_text = False
        for char in source:
            if is_cjk_char(char):
                has_cjk_text = True
                reading = self.pick_han_viet_reading(char, name_context=True)
                parts.append(reading or char)
            elif char.isspace():
                continue
            else:
                parts.append(char)
        if not has_cjk_text:
            return ""
        return title_case_words(" ".join(parts))

    def resolve_entity_target(
        self,
        source: str,
        *,
        entity_type: str,
        source_dict: str = "",
        current_target: str = "",
    ) -> str:
        """Resolve target for a scanned proper-name entity."""

        if entity_type not in PROPER_ENTITY_TYPES:
            return current_target

        current = current_target.strip()
        bank_record = self._lookup_term_bank(source, entity_type)
        if bank_record:
            return title_case_latin_or_words(bank_record.target)

        if current and source_dict.startswith(("global_term_bank", "private_term_bank", "heuristic_latin_")):
            return title_case_latin_or_words(current)

        if source_dict.startswith("names_person_west"):
            latin = self.resolve_latin_target(source, allow_phonetic=True, entity_type=entity_type)
            if latin:
                return latin

        stored = self.resolve_stored_keyword(source, entity_type)
        if stored and not source_dict.startswith("heuristic_"):
            return stored

        latin = self.resolve_latin_target(
            source,
            allow_phonetic=source_dict.startswith("heuristic_latin_"),
            entity_type=entity_type,
        )
        if latin and (source_dict.startswith("heuristic_latin_") or source_dict.startswith("names_person_west")):
            return latin

        generated = self.resolve_word_by_word(source)
        return generated or current_target

    def pick_han_viet_reading(self, source: str, *, name_context: bool = False) -> str:
        override = NAME_CONTEXT_READING_OVERRIDES.get(source) if name_context and len(source) == 1 else None
        if override:
            return override

        for record in self.accessor.get_entry_readings(source):
            candidates = normalize_reading_candidates(record.han_viet_readings)
            if not candidates:
                continue
            if name_context:
                contextual = self._pick_name_context_reading(source, candidates)
                if contextual:
                    return contextual
            return candidates[0]
        return ""

    def _pick_name_context_reading(self, source: str, candidates: list[str]) -> str:
        if len(source) != 1:
            return ""
        if source in self._name_reading_cache:
            cached = self._name_reading_cache[source]
            return cached if cached.lower() in {item.lower() for item in candidates} else ""

        candidate_map = {item.lower(): item for item in candidates}
        votes: dict[str, int] = {}
        rows = self.accessor._get_conn().execute(
            """
            SELECT source, target
            FROM entries
            WHERE source LIKE ?
              AND (entity_type = 'person' OR category LIKE 'names_person%')
            LIMIT 250
            """,
            (f"%{source}%",),
        ).fetchall()
        for row in rows:
            name_source = str(row["source"] or "")
            target_words = str(row["target"] or "").split()
            if len(name_source) != len(target_words):
                continue
            for index, char in enumerate(name_source):
                if char != source:
                    continue
                target_word = target_words[index].strip(" ,.;:()[]{}").lower()
                if target_word in candidate_map:
                    votes[target_word] = votes.get(target_word, 0) + 1

        if not votes:
            self._name_reading_cache[source] = ""
            return ""
        best = max(votes.items(), key=lambda item: item[1])[0]
        self._name_reading_cache[source] = candidate_map[best]
        return candidate_map[best]

    def _lookup_term_bank(self, source: str, entity_type: str) -> object | None:
        if self.term_bank is None:
            return None
        normalized_type = entity_type if entity_type in PROPER_ENTITY_TYPES else None
        return self.term_bank.best(source, entity_type=normalized_type)

    @staticmethod
    def _latin_value_from_record(record: DictionaryRecord, entity_type: str | None = None) -> str:
        if _looks_like_western_name_record(record):
            first = clean_latin_reference_target(first_target_variant(record.target))
            if first and is_ascii_latin_phrase(first):
                return first
            if record.target and not has_cjk(record.target) and looks_like_latin_transliteration_source(record.source):
                return transliterate_western_source(record.source)

        if record.table_name == "reference_entries":
            if entity_type == "person":
                return ""
            if not looks_like_latin_transliteration_source(record.source) and entity_type != "location":
                return ""
            value = clean_latin_reference_target(record.target)
            if value:
                return value
        return ""

    @staticmethod
    def _is_trusted_stored_name_record(record: DictionaryRecord, entity_type: str) -> bool:
        category = (record.category or "").lower()
        record_entity_type = (record.entity_type or "").lower()
        if "names" in category:
            return True
        if record_entity_type in PROPER_ENTITY_TYPES:
            return True
        if entity_type in PROPER_ENTITY_TYPES and record.priority >= 4:
            return True
        return False


def normalize_reading_candidates(value: str) -> list[str]:
    if not value:
        return []
    candidates: list[str] = []
    seen: set[str] = set()
    for part in READING_SPLIT_RE.split(value):
        normalized = " ".join(part.strip().split())
        key = normalized.lower()
        if normalized and key not in seen:
            candidates.append(normalized)
            seen.add(key)
    return candidates


def first_target_variant(value: str) -> str:
    return TARGET_VARIANT_SPLIT_RE.split(value or "", maxsplit=1)[0].strip()


def pick_best_stored_target(value: str) -> str:
    return first_target_variant(value)


def pick_latin_target_variant(value: str) -> str:
    for part in LATIN_TARGET_VARIANT_SPLIT_RE.split(value or ""):
        cleaned = clean_latin_reference_target(part)
        if cleaned and is_ascii_latin_phrase(cleaned):
            return cleaned
    return ""


def clean_latin_reference_target(value: str) -> str:
    raw = " ".join((value or "").replace("・", " ").replace("·", " ").split()).strip()
    if not raw or not ASCII_LETTER_RE.search(raw):
        return ""
    if CEDICT_NAME_MARKER_RE.search(raw):
        raw = re.sub(r"^\((?:name|proper name)\)\s*", "", raw, flags=re.IGNORECASE)
        raw = PAREN_RE.sub("", raw).strip()
    elif not is_ascii_latin_phrase(raw):
        return ""
    raw = raw.split(",", 1)[0].strip()
    raw = re.sub(r"\b(?:name|proper name)\b", "", raw, flags=re.IGNORECASE).strip(" -;:")
    return raw if is_ascii_latin_phrase(raw) else ""


def title_case_words(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in value.split() if part)


def title_case_latin_or_words(value: str) -> str:
    return " ".join(_title_case_latin_token(part) for part in value.split() if part)


def _title_case_latin_token(value: str) -> str:
    if not value:
        return value
    if any(ch.isupper() for ch in value[1:]):
        return value
    return value[:1].upper() + value[1:]


def is_cjk_char(value: str) -> bool:
    return "\u4e00" <= value <= "\u9fff"


def has_cjk(value: str) -> bool:
    return any(is_cjk_char(char) for char in value)


def is_ascii_latin_phrase(value: str) -> bool:
    return bool(ASCII_LATIN_NAME_RE.match((value or "").strip()))


def looks_like_latin_transliteration_source(source: str) -> bool:
    if not source or not all(is_cjk_char(char) for char in source):
        return False
    if source in LATIN_EXACT_OVERRIDES:
        return True
    if source.endswith(LATIN_SUFFIXES) and any(char in LATIN_STRONG_CHARS for char in source):
        return True
    if len(source) >= 3 and source.startswith(LATIN_PREFIXES):
        return True
    return False


def transliterate_western_source(source: str) -> str:
    parts: list[str] = []
    idx = 0
    while idx < len(source):
        matched = False
        for size in (3, 2):
            chunk = source[idx:idx + size]
            if chunk in LATIN_DIGRAPHS:
                parts.append(LATIN_DIGRAPHS[chunk])
                idx += size
                matched = True
                break
        if matched:
            continue
        parts.append(LATIN_CHAR_PARTS.get(source[idx], ""))
        idx += 1
    compact = "".join(parts).strip()
    if not compact:
        return ""
    compact = re.sub(r"([aeiou])\1+", r"\1", compact)
    return compact[:1].upper() + compact[1:]


def _looks_like_western_name_record(record: DictionaryRecord) -> bool:
    source_file = (record.source_file or "").casefold()
    category = (record.category or "").casefold()
    cultural_origin = (record.cultural_origin or "").casefold()
    metadata_origin = str(record.metadata.get("cultural_origin") or "").casefold()
    return (
        "west" in source_file
        or "west" in category
        or "latin" in category
        or cultural_origin in {"western", "west", "latin"}
        or metadata_origin in {"western", "west", "latin"}
    )
