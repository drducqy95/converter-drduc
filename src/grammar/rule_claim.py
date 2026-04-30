#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Grammar rule claim model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.trace import TraceEvent
from src.grammar.relation_detector import RelationType


@dataclass(slots=True)
class RuleClaim:
    rule_id: str
    relation_type: RelationType
    source_span: tuple[int, int]
    priority: int
    confidence: float
    replacement_plan: dict[str, Any] = field(default_factory=dict)
    protected: bool = False
    specificity: int = 0
    source: str = "builtin"
    trace: TraceEvent | None = None
