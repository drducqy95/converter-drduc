#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Detect untranslated residual source fragments."""

from __future__ import annotations

import re


RESIDUAL_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


class UntranslatedDetector:
    """Find untranslated CJK characters and unresolved markers."""

    def run(self, translation_result) -> list[dict]:
        issues: list[dict] = []
        for segment in translation_result.segments:
            if "[[AMBIG:" in segment.draft_text:
                issues.append({
                    "severity": "medium",
                    "checker": "ambiguity",
                    "segment_id": segment.sentence_id,
                    "message": "Annotated draft still contains unresolved ambiguity",
                })
            if "[[UNRESOLVED]]" in segment.draft_text:
                issues.append({
                    "severity": "high",
                    "checker": "untranslated",
                    "segment_id": segment.sentence_id,
                    "message": "Unresolved source character remains in draft",
                })
            elif RESIDUAL_CJK_RE.search(segment.clean_text):
                issues.append({
                    "severity": "medium",
                    "checker": "untranslated",
                    "segment_id": segment.sentence_id,
                    "message": "Residual CJK character remains in clean output",
                })
        return issues
