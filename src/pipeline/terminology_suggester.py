#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate terminology hints for reviewer confirmation before translation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.pipeline.name_reading import HanVietNameResolver, is_ascii_latin_phrase
from src.pipeline.entity_scanner import COMMON_WORD_PREFIXES, INVALID_NAME_CHARS, EntitySuggestion


@dataclass(slots=True)
class TerminologySuggestion:
    source: str
    current_target: str
    han_viet: str
    pinyin: str
    ambiguity: bool
    recommendation: str

    def to_dict(self) -> dict:
        return asdict(self)


class TerminologySuggester:
    """Attach reading and ambiguity hints to entity suggestions."""

    def __init__(self, db_path: str | None = None):
        self.accessor = RuntimeDictionaryAccessor(db_path)
        self.name_resolver = HanVietNameResolver(self.accessor)

    def close(self):
        self.accessor.close()

    def suggest(self, entities: list[EntitySuggestion]) -> list[TerminologySuggestion]:
        suggestions: list[TerminologySuggestion] = []
        for entity in entities:
            # Filter out common word prefixes and invalid chars
            if any(entity.source.startswith(prefix) for prefix in COMMON_WORD_PREFIXES):
                continue
            if any(ch in INVALID_NAME_CHARS for ch in entity.source):
                continue

            han_viet = ""
            pinyin = ""
            refs = self.accessor.lookup_reference(entity.source)
            for ref in refs:
                if not han_viet:
                    hv = str(ref.metadata.get("han_viet_readings", "") or "").split("|", 1)[0].strip()
                    if hv:
                        han_viet = hv
                if not pinyin:
                    py = str(ref.metadata.get("pinyin", "") or "").split("|", 1)[0].strip()
                    if py:
                        pinyin = py
                if han_viet and pinyin:
                    break

            if not han_viet:
                if entity.entity_type in {"person", "location", "organization"} and (
                    entity.source_dict.startswith("heuristic_latin_")
                    or "term_bank" in entity.source_dict
                    or is_ascii_latin_phrase(entity.target)
                ):
                    han_viet = entity.target
                elif entity.entity_type in {"person", "location", "organization"}:
                    han_viet = self.name_resolver.resolve_word_by_word(entity.source)
                else:
                    han_viet = self.accessor.get_han_viet_for_text(entity.source)
            if not pinyin:
                pinyin = self.accessor.get_pinyin_for_text(entity.source)

            recommendation = "lock"
            if entity.ambiguity_flag:
                recommendation = "review"
            elif entity.entity_type in {"person", "location", "organization"}:
                recommendation = "prioritize"

            suggestions.append(
                TerminologySuggestion(
                    source=entity.source,
                    current_target=entity.target,
                    han_viet=han_viet,
                    pinyin=pinyin,
                    ambiguity=entity.ambiguity_flag,
                    recommendation=recommendation,
                )
            )
        return suggestions
