#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sliding context manager compatible with the removed JavaScript module."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass, field
from time import time
from uuid import uuid4


@dataclass(slots=True)
class ContextSentence:
    text: str
    timestamp: float
    metadata: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"ctx_{uuid4().hex[:12]}")

    def to_dict(self) -> dict:
        return asdict(self)


class ContextManager:
    """Maintain recent sentences plus character/entity/topic counters."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.context_window: deque[ContextSentence] = deque(maxlen=window_size)
        self.character_tracking: Counter[str] = Counter()
        self.entity_tracking: Counter[str] = Counter()
        self.topic_tracking: deque[str] = deque(maxlen=window_size)

    def add_sentence(self, sentence: str, metadata: dict | None = None):
        metadata = metadata or {}
        self.context_window.append(ContextSentence(text=sentence, timestamp=time(), metadata=metadata))
        self.update_tracking(sentence, metadata)

    def update_tracking(self, sentence: str, metadata: dict):
        for character in metadata.get("characters", []) or []:
            self.character_tracking[str(character)] += 1
        for entity in metadata.get("entities", []) or []:
            self.entity_tracking[str(entity)] += 1
        topic = metadata.get("topic")
        if topic:
            self.topic_tracking.append(str(topic))

    def get_context_window(self) -> list[dict]:
        return [item.to_dict() for item in self.context_window]

    def get_sentence_context(self, position: int = -1) -> dict:
        window = list(self.context_window)
        if position == -1:
            position = len(window) - 1
        before = window[max(0, position - self.window_size):position]
        after = window[position + 1:position + 1 + self.window_size]
        current = window[position] if 0 <= position < len(window) else None
        return {
            "before": [item.to_dict() for item in before],
            "current": current.to_dict() if current else None,
            "after": [item.to_dict() for item in after],
            "characterTracking": self.get_character_tracking(),
            "entityTracking": self.get_entity_tracking(),
            "topicTracking": self.get_topic_tracking(),
        }

    def get_character_tracking(self) -> dict[str, int]:
        return dict(self.character_tracking)

    def get_entity_tracking(self) -> dict[str, int]:
        return dict(self.entity_tracking)

    def get_topic_tracking(self) -> list[str]:
        return list(self.topic_tracking)

    def clear(self):
        self.context_window.clear()
        self.character_tracking.clear()
        self.entity_tracking.clear()
        self.topic_tracking.clear()

    def serialize(self) -> dict:
        return {
            "windowSize": self.window_size,
            "contextWindow": self.get_context_window(),
            "characterTracking": list(self.character_tracking.items()),
            "entityTracking": list(self.entity_tracking.items()),
            "topicTracking": self.get_topic_tracking(),
        }

    def deserialize(self, data: dict):
        self.window_size = int(data.get("windowSize") or self.window_size)
        self.context_window = deque(
            [
                ContextSentence(
                    text=str(item.get("text") or ""),
                    timestamp=float(item.get("timestamp") or time()),
                    metadata=dict(item.get("metadata") or {}),
                    id=str(item.get("id") or f"ctx_{uuid4().hex[:12]}"),
                )
                for item in data.get("contextWindow", []) or []
                if isinstance(item, dict)
            ],
            maxlen=self.window_size,
        )
        self.character_tracking = Counter(dict(data.get("characterTracking", []) or []))
        self.entity_tracking = Counter(dict(data.get("entityTracking", []) or []))
        self.topic_tracking = deque([str(item) for item in data.get("topicTracking", []) or []], maxlen=self.window_size)
