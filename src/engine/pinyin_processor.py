#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resolve pinyin spans to Chinese text when confidence is high."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.core.runtime_support import RuntimeDictionaryAccessor, normalize_pinyin_key


PINYIN_TOKEN_RE = re.compile(r"[A-Za-zÀ-ỹ0-9']+")


@dataclass(slots=True)
class PinyinResolution:
    source: str
    target: str
    confidence: float


class PinyinProcessor:
    """Greedy pinyin resolver backed by entry_readings from SQLite."""

    def __init__(
        self,
        db_path: str | None = None,
        custom_lexicon: dict[str, str] | None = None,
    ):
        self._accessor = RuntimeDictionaryAccessor(db_path) if db_path else None
        self.custom_lexicon = {
            normalize_pinyin_key(key): value
            for key, value in (custom_lexicon or {}).items()
        }

    def close(self):
        if self._accessor:
            self._accessor.close()

    def resolve_with_trace(self, text: str, protected_terms: set[str] | None = None) -> tuple[str, list[PinyinResolution]]:
        protected_terms = protected_terms or set()
        if not text:
            return "", []

        traces: list[PinyinResolution] = []
        tokens = list(PINYIN_TOKEN_RE.finditer(text))
        if not tokens:
            return text, traces

        resolved: list[str] = []
        cursor = 0
        idx = 0

        while idx < len(tokens):
            match = tokens[idx]
            if cursor < match.start():
                resolved.append(text[cursor:match.start()])

            best_value = None
            best_end = idx + 1
            best_source = match.group(0)
            best_confidence = 0.0

            for end_idx in range(min(len(tokens), idx + 6), idx, -1):
                chunk = text[match.start():tokens[end_idx - 1].end()]
                key = normalize_pinyin_key(chunk)
                if not key:
                    continue
                source, confidence = self._lookup(key)
                if source and source not in protected_terms:
                    best_value = source
                    best_end = end_idx
                    best_source = chunk
                    best_confidence = confidence
                    break

            if best_value:
                resolved.append(best_value)
                traces.append(PinyinResolution(source=best_source, target=best_value, confidence=best_confidence))
                cursor = tokens[best_end - 1].end()
                idx = best_end
            else:
                resolved.append(text[match.start():match.end()])
                cursor = match.end()
                idx += 1

        if cursor < len(text):
            resolved.append(text[cursor:])

        return "".join(resolved), traces

    def resolve(self, text: str, protected_terms: set[str] | None = None) -> str:
        return self.resolve_with_trace(text, protected_terms=protected_terms)[0]

    def _lookup(self, key: str) -> tuple[str | None, float]:
        if key in self.custom_lexicon:
            return self.custom_lexicon[key], 1.0

        if self._accessor is None:
            return None, 0.0

        matches = self._accessor.lookup_by_pinyin(key)
        if len(matches) == 1:
            return matches[0], 0.95
        return None, 0.0
