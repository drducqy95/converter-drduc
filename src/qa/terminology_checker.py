#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Terminology consistency checks for translated segments."""

from __future__ import annotations


class TerminologyChecker:
    """Check locked entity renderings and ambiguity annotations."""

    def run(self, translation_result, config: dict) -> list[dict]:
        issues: list[dict] = []
        locked_entities = [
            item
            for item in config.get("locked_entities", [])
            if item.get("source") and item.get("target")
        ]
        for entity in locked_entities:
            expected = entity["target"]
            expected_normalized = self._normalize(expected)
            source = entity["source"]
            for segment in translation_result.segments:
                if source not in segment.source_text:
                    continue
                if expected_normalized in self._normalize(segment.clean_text):
                    continue
                if self._is_shadowed_by_longer_entity(
                    source=source,
                    expected=expected_normalized,
                    segment=segment,
                    locked_entities=locked_entities,
                ):
                    continue
                issues.append({
                    "severity": "high",
                    "checker": "terminology",
                    "segment_id": segment.sentence_id,
                    "message": f"Locked entity '{source}' expected '{expected}'",
                })
        return issues

    def _is_shadowed_by_longer_entity(self, *, source: str, expected: str, segment, locked_entities: list[dict]) -> bool:
        normalized_output = self._normalize(segment.clean_text)
        for other in locked_entities:
            other_source = other["source"]
            if len(other_source) <= len(source):
                continue
            if source not in other_source:
                continue
            if other_source not in segment.source_text:
                continue
            other_expected = self._normalize(other["target"])
            if other_expected == expected:
                continue
            if other_expected in normalized_output:
                return True
        return False

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.split()).casefold()
