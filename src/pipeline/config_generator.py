#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate translation_config.json from pre-translation analysis."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.engine.cultural_origin_detector import CulturalOriginDetector
from src.engine.style_profiles import default_style_preferences
from src.pipeline.entity_scanner import EntitySuggestion
from src.pipeline.relationship_builder import RelationshipEdge
from src.pipeline.name_reading import HanVietNameResolver, title_case_words
from src.pipeline.terminology_suggester import TerminologySuggestion


class ConfigGenerator:
    """Create a reviewable project configuration for runtime ranking."""

    def __init__(self, db_path: str | None = None):
        self.origin_detector = CulturalOriginDetector()
        self.accessor = RuntimeDictionaryAccessor(db_path)
        self.name_resolver = HanVietNameResolver(self.accessor)

    def close(self):
        self.accessor.close()

    def generate(
        self,
        *,
        text: str,
        entities: list[EntitySuggestion],
        relationships: list[RelationshipEdge],
        terminology: list[TerminologySuggestion],
    ) -> dict:
        genre_hints = self._detect_genre(text)
        cultural_origin = self.origin_detector.detect(text)
        high_ambiguity_terms = [term.source for term in terminology if term.ambiguity]
        style_preferences = default_style_preferences(genre_hints, cultural_origin)

        locked_entities: list[dict] = []
        seen_sources: set[str] = set()
        for entity in entities:
            if entity.entity_type not in {"person", "location", "organization"}:
                continue
            if entity.source in seen_sources:
                continue
            if entity.source_dict == "heuristic_name_mining" and entity.count < 2:
                continue

            locked_entities.append(
                {
                    "source": entity.source,
                    "target": self._resolve_locked_target(entity),
                    "entity_type": entity.entity_type,
                }
            )
            seen_sources.add(entity.source)

        return {
            "genre_hints": genre_hints,
            "cultural_origin_hint": cultural_origin,
            "style_profile": style_preferences["project_profile"],
            "style_context": style_preferences["project_context"],
            "style_preferences": style_preferences,
            "high_ambiguity_terms": high_ambiguity_terms,
            "naming_policy": {
                "prefer_locked_entities": True,
                "capitalize_western_names": True,
                "keep_han_viet_style": cultural_origin == "han_viet",
            },
            "locked_entities": locked_entities,
            "terminology_review": [asdict(item) for item in terminology],
            "relationships": [asdict(edge) for edge in relationships],
        }

    def write(self, config: dict, project_dir: str | Path):
        target = Path(project_dir) / "working" / "config"
        target.mkdir(parents=True, exist_ok=True)
        (target / "translation_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    def _resolve_locked_target(self, entity: EntitySuggestion) -> str:
        return self.name_resolver.resolve_entity_target(
            entity.source,
            entity_type=entity.entity_type,
            source_dict=entity.source_dict,
            current_target=entity.target,
        )

    def _resolve_han_viet_name(self, source: str) -> str:
        return self.name_resolver.resolve_stored_keyword(source, "person") or self.name_resolver.resolve_word_by_word(source)

    def _pick_han_viet_reading(self, source: str, *, name_context: bool = False) -> str:
        return self.name_resolver.pick_han_viet_reading(source, name_context=name_context)

    @staticmethod
    def _title_case_words(value: str) -> str:
        return title_case_words(value)

    @staticmethod
    def _is_cjk_text(value: str) -> bool:
        return bool(value) and all("\u4e00" <= ch <= "\u9fff" for ch in value)

    def _detect_genre(self, text: str) -> list[str]:
        hints: list[str] = []
        if any(marker in text for marker in ("\u4fee\u4e3a", "\u7075\u6c14", "\u5b97\u95e8", "\u9053\u53cb", "\u4e39\u7530")):
            hints.append("xianxia")
        if any(marker in text for marker in ("\u516c\u53f8", "\u7535\u8111", "\u624b\u673a", "\u603b\u88c1")):
            hints.append("modern")
        if any(marker in text for marker in ("\u9b3c", "\u6076\u9b3c", "\u5c38", "\u9ed1\u6697", "\u6050\u60e7", "\u60ca\u53eb", "\u60ca\u6050", "\u6b7b", "\u51f6\u5b85")):
            hints.append("horror")
        if any(marker in text for marker in ("\u538b\u6291", "\u7d27\u5f20", "\u8ffd", "\u9003", "\u5371\u9669", "\u7aa5\u89c6", "\u8be1\u5f02")):
            hints.append("suspense")
        if any(marker in text.lower() for marker in ("king", "queen", "sir")):
            hints.append("western_fantasy")
        return list(dict.fromkeys(hints)) or ["general"]
