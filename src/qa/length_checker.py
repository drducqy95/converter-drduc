#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Length sanity checks between source and target segments."""

from __future__ import annotations


class LengthChecker:
    """Flag suspiciously short or long outputs."""

    def run(self, translation_result) -> list[dict]:
        issues: list[dict] = []
        for segment in translation_result.segments:
            source_len = max(1, len(segment.source_text))
            ratio = len(segment.clean_text) / source_len
            if ratio < 0.2 or ratio > self._max_ratio_for_source_length(source_len):
                issues.append({
                    "severity": "low",
                    "checker": "length",
                    "segment_id": segment.sentence_id,
                    "message": f"Suspicious source/target ratio: {ratio:.2f}",
                })
        return issues

    @staticmethod
    def _max_ratio_for_source_length(source_len: int) -> float:
        # Short Chinese dialogue or terse narrative fragments expand sharply in Vietnamese.
        if source_len < 16:
            return 5.2
        if source_len < 28:
            return 4.8
        if source_len < 42:
            return 4.4
        return 4.1
