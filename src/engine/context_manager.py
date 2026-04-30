#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sliding context and scene state for translation passes."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(slots=True)
class ContextSnapshot:
    recent_sources: list[str]
    recent_targets: list[str]
    active_entities: list[str]
    scene_emotion: str | None
    genre: str | None


class ContextManager:
    """Maintain 5+5 sentence window and active entity list."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self._recent_sources: deque[str] = deque(maxlen=window_size)
        self._recent_targets: deque[str] = deque(maxlen=window_size)
        self._active_entities: deque[str] = deque(maxlen=20)
        self.scene_emotion: str | None = None
        self.genre: str | None = None

    def update(
        self,
        *,
        source_sentence: str,
        target_sentence: str,
        entities: list[str] | None = None,
        emotion: str | None = None,
        genre: str | None = None,
    ):
        self._recent_sources.append(source_sentence)
        self._recent_targets.append(target_sentence)
        for entity in entities or []:
            if entity in self._active_entities:
                self._active_entities.remove(entity)
            self._active_entities.appendleft(entity)
        if emotion:
            self.scene_emotion = emotion
        if genre:
            self.genre = genre

    def snapshot(self) -> ContextSnapshot:
        return ContextSnapshot(
            recent_sources=list(self._recent_sources),
            recent_targets=list(self._recent_targets),
            active_entities=list(self._active_entities),
            scene_emotion=self.scene_emotion,
            genre=self.genre,
        )

    def reset_for_chapter(self, *, keep_genre: bool = True):
        """Clear sentence/entity/emotion windows at a chapter boundary."""
        current_genre = self.genre
        self._recent_sources.clear()
        self._recent_targets.clear()
        self._active_entities.clear()
        self.scene_emotion = None
        self.genre = current_genre if keep_genre else None
