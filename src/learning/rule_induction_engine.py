#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rule induction from post-edit feedback for the Python learning path."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from uuid import uuid4


@dataclass(slots=True)
class InducedRule:
    id: str
    source_pattern: str
    target_pattern: str
    condition: str
    confidence: float
    created_from: str
    timestamp: str
    difference: dict

    def to_dict(self) -> dict:
        return asdict(self)


class RuleInductionEngine:
    """Generate reviewable rule candidates from human edits."""

    def __init__(self):
        self.learned_rules: list[InducedRule] = []

    def induce_from_edit(self, original_source: str, original_translation: str, edited_translation: str) -> list[dict]:
        alignments = self.align_translations(original_translation, edited_translation)
        differences = self.identify_differences(original_translation, edited_translation, alignments)
        patterns = self.extract_patterns(original_source, edited_translation, differences)
        new_rules = self.generate_rules(patterns)
        self.learned_rules.extend(new_rules)
        return [rule.to_dict() for rule in new_rules]

    def align_translations(self, original: str, edited: str, alignments: list[dict] | None = None) -> list[dict]:
        if alignments:
            return alignments
        return [
            {
                "original": original,
                "edited": edited,
                "confidence": round(SequenceMatcher(None, original, edited).ratio(), 3),
            }
        ]

    def identify_differences(self, original: str, edited: str, alignments: list[dict]) -> list[dict]:
        matcher = SequenceMatcher(None, original, edited)
        differences = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            differences.append(
                {
                    "type": tag,
                    "originalFragment": original[i1:i2],
                    "editedFragment": edited[j1:j2],
                    "position": i1,
                }
            )
        return differences or [{"type": "equal", "originalFragment": original, "editedFragment": edited, "position": 0}]

    def extract_patterns(self, source: str, target: str, differences: list[dict]) -> list[dict]:
        return [
            {
                "sourcePattern": source,
                "targetPattern": target,
                "difference": difference,
                "frequency": 1,
            }
            for difference in differences
        ]

    def generate_rules(self, patterns: list[dict]) -> list[InducedRule]:
        timestamp = datetime.now(timezone.utc).isoformat()
        rules = []
        for pattern in patterns:
            rules.append(
                InducedRule(
                    id=f"rule_{uuid4().hex[:12]}",
                    source_pattern=str(pattern.get("sourcePattern") or ""),
                    target_pattern=str(pattern.get("targetPattern") or ""),
                    condition="always",
                    confidence=0.8,
                    created_from="post_editing",
                    timestamp=timestamp,
                    difference=dict(pattern.get("difference") or {}),
                )
            )
        return rules

    def get_learned_rule_count(self) -> int:
        return len(self.learned_rules)

    def get_learned_rules(self) -> list[dict]:
        return [rule.to_dict() for rule in self.learned_rules]

    def clear_learned_rules(self):
        self.learned_rules = []
