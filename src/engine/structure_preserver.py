#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Preserve and restore non-translatable structures with stable placeholders."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


PLACEHOLDER_PREFIX = "__PRESERVE_"


@dataclass(slots=True)
class PlaceholderEntry:
    token: str
    original: str
    kind: str


@dataclass(slots=True)
class PreservationResult:
    text: str
    placeholders: list[PlaceholderEntry] = field(default_factory=list)


class StructurePreserver:
    """Protect Markdown/HTML/code/LaTeX fragments before translation."""

    _PATTERNS: list[tuple[str, re.Pattern[str]]] = [
        ("code_block", re.compile(r"```[\s\S]*?```", re.MULTILINE)),
        ("latex_block", re.compile(r"\$\$[\s\S]*?\$\$")),
        ("html_comment", re.compile(r"<!--[\s\S]*?-->")),
        ("markdown_image", re.compile(r"!\[[^\]]*\]\([^)]+\)")),
        ("markdown_link", re.compile(r"\[[^\]]+\]\([^)]+\)")),
        ("html_tag", re.compile(r"</?[^>\n]+?>")),
        ("table_block", re.compile(r"(?m)(?:^\|.*\|\s*$\n?){2,}")),
        ("inline_code", re.compile(r"`[^`\n]+`")),
        ("latex_inline", re.compile(r"\$(?:\\.|[^$\n])+\$")),
    ]

    def preserve(self, text: str) -> PreservationResult:
        if not text:
            return PreservationResult(text="")

        placeholders: list[PlaceholderEntry] = []
        working = text
        counter = 0

        def replacer(kind: str):
            def _replace(match: re.Match[str]) -> str:
                nonlocal counter
                token = f"{PLACEHOLDER_PREFIX}{counter:04d}__"
                counter += 1
                placeholders.append(PlaceholderEntry(token=token, original=match.group(0), kind=kind))
                return token

            return _replace

        for kind, pattern in self._PATTERNS:
            working = pattern.sub(replacer(kind), working)

        return PreservationResult(text=working, placeholders=placeholders)

    def restore(self, text: str, placeholders: list[PlaceholderEntry]) -> str:
        restored = text
        for entry in reversed(placeholders):
            restored = restored.replace(entry.token, entry.original)
        return restored

    def compare_integrity(self, source: str, restored: str) -> dict[str, int | bool]:
        source_result = self.preserve(source)
        restored_result = self.preserve(restored)
        return {
            "source_placeholders": len(source_result.placeholders),
            "restored_placeholders": len(restored_result.placeholders),
            "all_restored": PLACEHOLDER_PREFIX not in restored,
            "same_count": len(source_result.placeholders) == len(restored_result.placeholders),
        }
