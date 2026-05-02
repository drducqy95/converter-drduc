#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recent mention memory for pronoun graph resolution."""

from __future__ import annotations


class MentionMemory:
    """Maintain a bounded, de-duplicated list of recent entity mentions."""

    def __init__(self, *, limit: int = 24):
        self.limit = max(int(limit), 1)
        self._items: list[str] = []

    def remember(self, mentions: list[str]) -> None:
        for source in mentions:
            source = str(source or "").strip()
            if not source:
                continue
            if source in self._items:
                self._items.remove(source)
            self._items.append(source)
        if len(self._items) > self.limit:
            self._items = self._items[-self.limit :]

    def recent(self, *, reverse: bool = False) -> list[str]:
        items = list(self._items)
        return list(reversed(items)) if reverse else items

    def reset(self) -> None:
        self._items.clear()

    @property
    def items(self) -> list[str]:
        return self._items
