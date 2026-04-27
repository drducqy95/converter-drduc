#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Clause segmentation that respects quotes and protected spans."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from src.pipeline.packet import ProtectedSpan
from src.pipeline.protected_span_registry import ProtectedSpanRegistry


class ClauseBoundary(Enum):
    SENTENCE_END = "sentence_end"
    CLAUSE_SOFT = "clause_soft"
    CLAUSE_HARD = "clause_hard"
    QUOTE_OPEN = "quote_open"
    QUOTE_CLOSE = "quote_close"
    CONJUNCTION = "conjunction"
    CONDITIONAL = "conditional"
    CONCESSIVE = "concessive"
    CAUSE = "cause"
    RESULT = "result"
    TEMPORAL = "temporal"


@dataclass(slots=True)
class Boundary:
    index: int
    boundary_type: ClauseBoundary
    marker: str = ""


@dataclass(slots=True)
class Clause:
    text: str
    start: int
    end: int
    boundary: ClauseBoundary | None = None


MARKERS: list[tuple[ClauseBoundary, tuple[str, ...]]] = [
    (ClauseBoundary.CONDITIONAL, ("如果", "若", "若是", "只要", "一旦", "除非", "倘若", "假如")),
    (ClauseBoundary.CONCESSIVE, ("虽然", "虽说", "即便", "即使", "哪怕", "就算", "尽管")),
    (ClauseBoundary.CAUSE, ("因为", "由于", "鉴于", "基于")),
    (ClauseBoundary.RESULT, ("所以", "因此", "于是")),
    (ClauseBoundary.TEMPORAL, ("当", "当时", "随后", "然后", "这时", "此时", "随着", "直到")),
]

AUTO_PROTECTED_PATTERNS: tuple[tuple[str, str, int], ...] = (
    (r"【[^】]{1,120}】", "BRACKET_ITEM", 50),
    (r"《[^》]{1,120}》", "TITLE_OR_BOOK", 50),
    (r"\[\d{1,2}:\d{2}(?::\d{2})?\]", "TIMESTAMP", 70),
    (r"\b\d{1,2}:\d{2}:\d{2}\b", "TIMESTAMP", 70),
)


class ClauseSegmenter:
    """Split Chinese text into clauses without cutting protected content."""

    def segment(self, text: str, protected_spans: list[ProtectedSpan] | None = None) -> list[Clause]:
        registry = ProtectedSpanRegistry(self._auto_protected_spans(text) + list(protected_spans or []))
        boundaries: list[Boundary] = []
        quote_depth = 0

        for idx, ch in enumerate(text):
            if registry.is_inside(idx):
                continue
            if ch in "“「『\"'":
                quote_depth += 1
                boundaries.append(Boundary(idx, ClauseBoundary.QUOTE_OPEN, ch))
                continue
            if ch in "”」』\"'":
                quote_depth = max(quote_depth - 1, 0)
                boundaries.append(Boundary(idx, ClauseBoundary.QUOTE_CLOSE, ch))
                continue
            if quote_depth:
                continue

            if ch in "。！？":
                boundaries.append(Boundary(idx, ClauseBoundary.SENTENCE_END, ch))
            elif ch == "；":
                boundaries.append(Boundary(idx, ClauseBoundary.CLAUSE_HARD, ch))
            elif ch == "，":
                marker_boundary = self._detect_marker_around(text, idx)
                if marker_boundary:
                    boundaries.append(marker_boundary)
                elif self._should_soft_split(text, idx):
                    boundaries.append(Boundary(idx, ClauseBoundary.CLAUSE_SOFT, ch))

        return self._build_clauses(text, boundaries)

    @staticmethod
    def _detect_marker_around(text: str, comma_index: int) -> Boundary | None:
        left = text[max(0, comma_index - 14):comma_index]
        right = text[comma_index + 1:comma_index + 15]
        window = left + right
        for boundary_type, markers in MARKERS:
            for marker in markers:
                if marker in window:
                    return Boundary(comma_index, boundary_type, marker)
        return None

    @staticmethod
    def _should_soft_split(text: str, comma_index: int) -> bool:
        left = text[max(0, comma_index - 20):comma_index]
        right = text[comma_index + 1:comma_index + 21]
        return len(left.strip()) >= 8 and len(right.strip()) >= 8

    @staticmethod
    def _build_clauses(text: str, boundaries: list[Boundary]) -> list[Clause]:
        clauses: list[Clause] = []
        start = 0
        for boundary in boundaries:
            if boundary.boundary_type in {ClauseBoundary.QUOTE_OPEN, ClauseBoundary.QUOTE_CLOSE}:
                continue
            end = boundary.index + 1
            chunk = text[start:end].strip()
            if chunk:
                clauses.append(Clause(text=chunk, start=start, end=end, boundary=boundary.boundary_type))
            start = end
        tail = text[start:].strip()
        if tail:
            clauses.append(Clause(text=tail, start=start, end=len(text), boundary=None))
        return clauses or [Clause(text=text, start=0, end=len(text), boundary=None)]

    @staticmethod
    def _auto_protected_spans(text: str) -> list[ProtectedSpan]:
        spans: list[ProtectedSpan] = []
        for pattern, span_type, priority in AUTO_PROTECTED_PATTERNS:
            for match in re.finditer(pattern, text):
                spans.append(
                    ProtectedSpan(
                        start=match.start(),
                        end=match.end(),
                        text=match.group(0),
                        span_type=span_type,
                        priority=priority,
                        source="clause_segmenter_auto",
                    )
                )
        return spans
