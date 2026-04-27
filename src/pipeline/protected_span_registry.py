#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Priority-aware protected span registry."""

from __future__ import annotations

from src.pipeline.packet import LockLevel, ProtectedSpan


DEFAULT_SPAN_PRIORITIES = {
    "SYSTEM_UI": 100,
    "CHAPTER_TITLE": 100,
    "APPROVED_ENTITY": 90,
    "ENTITY": 90,
    "QUOTE": 80,
    "NUMBER": 70,
    "RANK": 70,
    "TIME": 70,
    "DATE": 70,
    "IDIOM": 60,
    "BRACKET_ITEM": 50,
}


class ProtectedSpanRegistry:
    """Collect claims and resolve overlaps by priority, lock level, and length."""

    def __init__(self, spans: list[ProtectedSpan] | None = None):
        self._claims: list[ProtectedSpan] = []
        self._resolved: list[ProtectedSpan] | None = None
        for span in spans or []:
            self.claim(span)

    def claim(self, span: ProtectedSpan) -> None:
        if span.end < span.start:
            raise ValueError(f"Invalid protected span: {span}")
        if span.start == span.end:
            return
        self._claims.append(span)
        self._resolved = None

    def claim_text(
        self,
        text: str,
        *,
        start: int,
        end: int,
        span_type: str,
        source: str,
        lock_level: str = LockLevel.HARD_LOCK.value,
        priority: int | None = None,
    ) -> None:
        self.claim(
            ProtectedSpan(
                start=start,
                end=end,
                text=text[start:end],
                span_type=span_type,
                priority=priority if priority is not None else DEFAULT_SPAN_PRIORITIES.get(span_type, 50),
                source=source,
                lock_level=lock_level,
            )
        )

    def resolve_overlap(self) -> list[ProtectedSpan]:
        if self._resolved is not None:
            return list(self._resolved)

        chosen: list[ProtectedSpan] = []
        lock_rank = {
            LockLevel.HARD_LOCK.value: 3,
            LockLevel.SOFT_LOCK.value: 2,
            LockLevel.REVIEW.value: 1,
        }
        ranked = sorted(
            self._claims,
            key=lambda item: (
                -item.priority,
                -lock_rank.get(item.lock_level, 0),
                -(item.end - item.start),
                item.start,
            ),
        )
        for span in ranked:
            if any(span.overlaps(existing) for existing in chosen):
                continue
            chosen.append(span)

        self._resolved = sorted(chosen, key=lambda item: (item.start, item.end))
        return list(self._resolved)

    def is_protected(self, start: int, end: int) -> bool:
        return any(span.contains(start, end) for span in self.resolve_overlap())

    def is_inside(self, index: int) -> bool:
        return self.is_protected(index, index + 1)

