#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Segment packet and protected span models for the v23 hardening pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.trace import TraceEvent, make_trace_id


class SegmentType(Enum):
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    THOUGHT = "thought"
    SYSTEM_PROMPT = "system_ui"
    CHAPTER_TITLE = "chapter_title"
    AUTHOR_NOTE = "author_note"
    FORUM_POST = "forum"
    ADVERTISEMENT = "ad"


class LockLevel(Enum):
    HARD_LOCK = "HARD_LOCK"
    SOFT_LOCK = "SOFT_LOCK"
    REVIEW = "REVIEW"


@dataclass(slots=True)
class ProtectedSpan:
    start: int
    end: int
    text: str
    span_type: str
    priority: int
    source: str
    lock_level: str = LockLevel.HARD_LOCK.value
    metadata: dict[str, Any] = field(default_factory=dict)

    def overlaps(self, other: "ProtectedSpan") -> bool:
        return self.start < other.end and other.start < self.end

    def contains(self, start: int, end: int) -> bool:
        return self.start <= start and end <= self.end


@dataclass(slots=True)
class SegmentPacket:
    segment_id: str
    chapter_id: str
    position: int
    raw_text: str
    normalized_text: str
    seg_type: SegmentType
    confidence: float
    protected_spans: list[ProtectedSpan] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace: list[TraceEvent] = field(default_factory=list)
    trace_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        chapter_id: str,
        position: int,
        raw_text: str,
        normalized_text: str | None = None,
        seg_type: SegmentType = SegmentType.NARRATION,
        confidence: float = 1.0,
        protected_spans: list[ProtectedSpan] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "SegmentPacket":
        normalized = raw_text if normalized_text is None else normalized_text
        trace_id = make_trace_id(chapter_id, position, raw_text)
        return cls(
            segment_id=trace_id,
            chapter_id=chapter_id,
            position=position,
            raw_text=raw_text,
            normalized_text=normalized,
            seg_type=seg_type,
            confidence=confidence,
            protected_spans=protected_spans or [],
            metadata=metadata or {},
            trace_id=trace_id,
        )

