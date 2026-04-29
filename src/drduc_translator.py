#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python entrypoint replacing the removed legacy Node translator facade."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.engine.rbmt_translator import RBMTTranslator
from src.learning.rule_induction_engine import RuleInductionEngine
from src.learning.translation_memory import TranslationMemory


@dataclass(slots=True)
class TranslatorOptions:
    db_path: str | None = None
    tm_db_path: str | None = None
    enable_tm_lookup: bool = False
    extra_config: dict[str, Any] = field(default_factory=dict)


class DrDucTranslator:
    """Thin Python facade over the production RBMT pipeline."""

    def __init__(self, options: TranslatorOptions | dict[str, Any] | None = None):
        if isinstance(options, dict):
            options = TranslatorOptions(**{key: value for key, value in options.items() if key in TranslatorOptions.__dataclass_fields__})
        self.options = options or TranslatorOptions()
        self.translation_memory = TranslationMemory()
        self.rule_induction_engine = RuleInductionEngine()
        self._rbmt = RBMTTranslator(
            db_path=self.options.db_path,
            tm_db_path=self.options.tm_db_path,
            enable_tm_lookup=self.options.enable_tm_lookup,
        )

    def close(self):
        self._rbmt.close()

    def translate(self, text: str, context: dict[str, Any] | None = None) -> str:
        config = dict(self.options.extra_config)
        config.update(context or {})
        result = self._rbmt.translate_text(text, config=config)
        self.translation_memory.store(text, result.clean_text)
        return result.clean_text

    def process_post_edit(self, original_text: str, translated_text: str, edited_text: str) -> list[dict]:
        self.translation_memory.store(original_text, edited_text)
        return self.rule_induction_engine.induce_from_edit(original_text, translated_text, edited_text)

    def get_stats(self) -> dict[str, int]:
        return {
            "translationMemorySize": self.translation_memory.get_size(),
            "learnedRuleCount": self.rule_induction_engine.get_learned_rule_count(),
            "totalTranslations": self.translation_memory.get_total_translations(),
        }


def translate_file(source_path: str | Path, target_path: str | Path, options: TranslatorOptions | None = None) -> str:
    source = Path(source_path)
    target = Path(target_path)
    translator = DrDucTranslator(options)
    try:
        translated = translator.translate(source.read_text(encoding="utf-8"))
    finally:
        translator.close()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(translated, encoding="utf-8")
    return translated
