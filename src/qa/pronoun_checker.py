#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pronoun consistency checks for dialogue segments."""

from __future__ import annotations


class PronounChecker:
    """Flag inconsistent or unresolved pronoun traces."""

    def run(self, translation_result) -> list[dict]:
        issues: list[dict] = []
        for segment in translation_result.segments:
            pronoun_traces = [trace for trace in segment.trace if trace.get("fallback_level") == "pronoun"]
            if "我" in segment.source_text and not pronoun_traces and not self._has_first_person_phrase_trace(segment.trace):
                issues.append({
                    "severity": "medium",
                    "checker": "pronoun",
                    "segment_id": segment.sentence_id,
                    "message": "First-person pronoun present but no pronoun-resolution trace found",
                })
        return issues

    @staticmethod
    def _has_first_person_phrase_trace(traces: list[dict]) -> bool:
        for trace in traces:
            source = str(trace.get("source", ""))
            if "我" in source:
                return True
        return False
