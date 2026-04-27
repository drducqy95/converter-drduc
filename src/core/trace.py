#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Trace event schema shared by pipeline, translation, QA, and review layers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class TraceEvent:
    """A normalized decision record for one pipeline stage."""

    segment_id: str
    stage: str
    rule_id: str | None = None
    input_span: tuple[int, int] | None = None
    output_span: tuple[int, int] | None = None
    action: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_trace_id(chapter_id: str, position: int, raw_text: str) -> str:
    """Create a stable, short trace id for deterministic artifacts."""

    import hashlib

    digest = hashlib.sha1(raw_text.encode("utf-8")).hexdigest()[:12]
    safe_chapter = chapter_id or "chapter"
    return f"{safe_chapter}:{position:05d}:{digest}"

