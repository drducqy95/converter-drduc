#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deterministic dependency parser for syntax inspection artifacts."""

from __future__ import annotations

from src.parser.morphological_analyzer import MorphologicalAnalyzer


class DependencyParser:
    """Create a conservative dependency tree from morphology output."""

    def __init__(self):
        self._fallback_analyzer = MorphologicalAnalyzer()

    def parse(self, analysis: dict | str) -> dict:
        if isinstance(analysis, str):
            analysis = self._fallback_analyzer.analyze(analysis)

        tokens = list(analysis.get("tokens") or [])
        pos_tags = list(analysis.get("posTags") or analysis.get("pos_tags") or [])
        if len(pos_tags) != len(tokens):
            pos_tags = self._fallback_analyzer.tag_pos(tokens)

        root_index = self._compute_root(pos_tags)
        dependencies = [
            {
                "id": index,
                "form": token,
                "pos": pos_tags[index] if index < len(pos_tags) else "unknown",
                "head": self.compute_head(index, root_index, pos_tags),
                "relation": self.compute_relation(index, root_index, pos_tags),
            }
            for index, token in enumerate(tokens)
        ]
        return {
            "tokens": tokens,
            "posTags": pos_tags,
            "dependencies": dependencies,
            "root": next((item for item in dependencies if item["head"] == -1), None),
        }

    @staticmethod
    def _compute_root(pos_tags: list[str]) -> int:
        for index, pos in enumerate(pos_tags):
            if pos == "verb":
                return index
        for index, pos in enumerate(pos_tags):
            if pos not in {"punctuation", "particle", "symbol"}:
                return index
        return 0 if pos_tags else -1

    @staticmethod
    def compute_head(index: int, root_index: int, pos_tags: list[str] | None = None) -> int:
        if root_index < 0 or index == root_index:
            return -1
        return root_index

    @staticmethod
    def compute_relation(index: int, root_index: int, pos_tags: list[str] | None = None) -> str:
        pos_tags = pos_tags or []
        pos = pos_tags[index] if index < len(pos_tags) else "unknown"
        if root_index < 0 or index == root_index:
            return "root"
        if pos == "punctuation":
            return "punct"
        if pos == "particle":
            return "mark"
        if pos == "preposition":
            return "case"
        if index < root_index:
            return "nsubj"
        if pos == "adverb":
            return "advmod"
        return "obj" if index == root_index + 1 else "dep"
