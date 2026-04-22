#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check placeholder and structural integrity after translation."""

from __future__ import annotations

from src.engine.structure_preserver import PLACEHOLDER_PREFIX, StructurePreserver


class StructureChecker:
    """Verify preserved structures were restored correctly."""

    def __init__(self):
        self.preserver = StructurePreserver()

    def run(self, source_text: str, translation_result) -> list[dict]:
        issues: list[dict] = []
        if PLACEHOLDER_PREFIX in translation_result.clean_text or PLACEHOLDER_PREFIX in translation_result.draft_text:
            issues.append({
                "severity": "critical",
                "checker": "structure",
                "segment_id": "document",
                "message": "Unrestored placeholder token remains in output",
            })
        integrity = self.preserver.compare_integrity(source_text, translation_result.clean_text)
        if not integrity["same_count"]:
            issues.append({
                "severity": "high",
                "checker": "structure",
                "segment_id": "document",
                "message": "Preserved structure count changed after translation",
            })
        return issues
