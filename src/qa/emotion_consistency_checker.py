#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Emotion continuity checks for translated dialogue."""

from __future__ import annotations


class EmotionConsistencyChecker:
    """Detect abrupt emotion flips in adjacent segments."""

    def run(self, translation_result) -> list[dict]:
        issues: list[dict] = []
        previous = None
        for segment in translation_result.segments:
            if previous and previous.emotion and segment.emotion:
                if self._is_dialogue(previous.source_text) != self._is_dialogue(segment.source_text):
                    previous = segment
                    continue
                if previous.emotion == "joy" and segment.emotion == "anger":
                    issues.append({
                        "severity": "low",
                        "checker": "emotion",
                        "segment_id": segment.sentence_id,
                        "message": "Abrupt joy -> anger transition detected",
                    })
            previous = segment
        return issues

    @staticmethod
    def _is_dialogue(text: str) -> bool:
        stripped = str(text or "").strip()
        return stripped.startswith(("\"", "'", "“", "”", "‘", "’", "「", "『"))
