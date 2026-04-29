#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Syntax-transfer rule registry used by the Python pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class SyntaxRule:
    category: str
    rule_id: str
    description: str
    confidence: float = 0.75

    def to_dict(self) -> dict:
        return asdict(self)


class SyntaxTransferRules:
    """Small rule registry for syntax inspection and future transfer passes."""

    DEFAULT_CATEGORIES = (
        "adjective_reordering",
        "possessive_handling",
        "relative_clause_handling",
        "adverbial_repositioning",
        "complement_handling",
    )

    def __init__(self):
        self.rules: dict[str, list[SyntaxRule]] = {category: [] for category in self.DEFAULT_CATEGORIES}
        self.load_default_rules()

    def load_default_rules(self):
        self.add_rule(
            "adjective_reordering",
            SyntaxRule("adjective_reordering", "zh_modifier_before_head", "Chinese modifiers before head map to Vietnamese head before modifier."),
        )
        self.add_rule(
            "possessive_handling",
            SyntaxRule("possessive_handling", "de_possessive", "Owner + 的 + noun maps to noun + của + owner when possessive."),
        )
        self.add_rule(
            "adverbial_repositioning",
            SyntaxRule("adverbial_repositioning", "adverb_before_verb", "Keep short adverbs before the Vietnamese verb phrase unless style rules override."),
        )

    def apply(self, parsed_text: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        dependencies = list(parsed_text.get("dependencies") or [])
        tokens = list(parsed_text.get("tokens") or [])
        applied = self._infer_applicable_rules(tokens, dependencies)
        result = dict(parsed_text)
        result.update(
            {
                "transformed": bool(applied),
                "syntax_rules_applied": [rule.to_dict() for rule in applied],
                "notes": "Syntax transfer inspection completed",
                "context": context,
            }
        )
        return result

    def get_rule_count(self) -> int:
        return sum(len(items) for items in self.rules.values())

    def add_rule(self, category: str, rule: SyntaxRule | dict[str, Any]):
        if isinstance(rule, dict):
            rule = SyntaxRule(
                category=category,
                rule_id=str(rule.get("rule_id") or rule.get("id") or "custom_rule"),
                description=str(rule.get("description") or rule.get("notes") or ""),
                confidence=float(rule.get("confidence", 0.75)),
            )
        self.rules.setdefault(category, []).append(rule)

    def _infer_applicable_rules(self, tokens: list[str], dependencies: list[dict]) -> list[SyntaxRule]:
        applied: list[SyntaxRule] = []
        if "的" in tokens and self.rules.get("possessive_handling"):
            applied.append(self.rules["possessive_handling"][0])
        if any(item.get("relation") == "advmod" for item in dependencies) and self.rules.get("adverbial_repositioning"):
            applied.append(self.rules["adverbial_repositioning"][0])
        if len(tokens) >= 2 and self.rules.get("adjective_reordering"):
            applied.append(self.rules["adjective_reordering"][0])
        return applied
