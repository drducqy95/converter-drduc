#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""In-memory translation memory compatibility layer for legacy JS removal."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(slots=True)
class SimilarTranslation:
    source: str
    target: str
    similarity: float

    def to_dict(self) -> dict:
        return {"source": self.source, "target": self.target, "similarity": self.similarity}


class TranslationMemory:
    """Small in-memory TM; production persistence lives in src.state.translation_memory."""

    def __init__(self):
        self.memory: dict[str, str] = {}
        self.total_translations = 0
        self.access_count: dict[str, int] = {}

    def store(self, source: str, target: str):
        self.memory[source] = target
        self.total_translations += 1
        self.access_count.setdefault(source, 0)

    def retrieve(self, source: str) -> str | None:
        translation = self.memory.get(source)
        if translation is not None:
            self.access_count[source] = self.access_count.get(source, 0) + 1
        return translation

    def find_similar(self, source: str, threshold: float = 0.8) -> list[dict]:
        results = []
        source_key = source.casefold()
        for stored_source, target in self.memory.items():
            similarity = self.calculate_similarity(source_key, stored_source.casefold())
            if similarity >= threshold:
                results.append(SimilarTranslation(stored_source, target, similarity).to_dict())
        return sorted(results, key=lambda item: item["similarity"], reverse=True)

    def calculate_similarity(self, left: str, right: str) -> float:
        return SequenceMatcher(None, left, right).ratio()

    def levenshtein_distance(self, left: str, right: str) -> int:
        if left == right:
            return 0
        if not left:
            return len(right)
        if not right:
            return len(left)
        previous = list(range(len(right) + 1))
        for i, left_char in enumerate(left, start=1):
            current = [i]
            for j, right_char in enumerate(right, start=1):
                cost = 0 if left_char == right_char else 1
                current.append(min(current[j - 1] + 1, previous[j] + 1, previous[j - 1] + cost))
            previous = current
        return previous[-1]

    def get_size(self) -> int:
        return len(self.memory)

    def get_total_translations(self) -> int:
        return self.total_translations

    def clear(self):
        self.memory.clear()
        self.access_count.clear()
        self.total_translations = 0
