#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resolve overlapping grammar rule claims."""

from __future__ import annotations

from src.core.trace import TraceEvent
from src.grammar.rule_claim import RuleClaim


SOURCE_WEIGHTS: dict[str, int] = {
    "user": 300,
    "project": 260,
    "runtime": 240,
    "builtin": 200,
    "learned": 150,
    "candidate": 100,
    "unknown": 0,
}


class ConflictResolver:
    """Keep highest-ranked non-overlapping claims with deterministic traces."""

    def resolve(self, claims: list[RuleClaim]) -> list[RuleClaim]:
        accepted, _trace = self.resolve_with_trace(claims)
        return accepted

    def resolve_with_trace(self, claims: list[RuleClaim]) -> tuple[list[RuleClaim], list[TraceEvent]]:
        accepted: list[RuleClaim] = []
        traces: list[TraceEvent] = []

        for claim in sorted(claims, key=self._sort_key):
            if claim.protected:
                traces.append(self._trace(claim, "skipped_protected"))
                continue

            conflicting = [
                existing
                for existing in accepted
                if self._overlap(claim.source_span, existing.source_span)
            ]
            if conflicting:
                traces.append(
                    self._trace(
                        claim,
                        "rejected_conflict",
                        winner_rule_ids=[item.rule_id for item in conflicting],
                    )
                )
                continue

            claim.trace = self._trace(claim, "accepted")
            traces.append(claim.trace)
            accepted.append(claim)

        return sorted(accepted, key=lambda item: item.source_span), traces

    @classmethod
    def _sort_key(cls, claim: RuleClaim) -> tuple:
        start, end = claim.source_span
        return (
            -int(claim.priority),
            -cls._specificity(claim),
            -cls._source_weight(claim.source),
            -float(claim.confidence),
            start,
            end,
            claim.rule_id,
        )

    @staticmethod
    def _specificity(claim: RuleClaim) -> int:
        if claim.specificity > 0:
            return int(claim.specificity)
        start, end = claim.source_span
        return max(0, int(end) - int(start))

    @staticmethod
    def _source_weight(source: str) -> int:
        normalized = str(source or "unknown").lower().strip()
        return SOURCE_WEIGHTS.get(normalized, SOURCE_WEIGHTS["unknown"])

    @classmethod
    def _trace(cls, claim: RuleClaim, action: str, **metadata) -> TraceEvent:
        return TraceEvent(
            segment_id="grammar",
            stage="grammar_conflict_resolver",
            rule_id=claim.rule_id,
            input_span=claim.source_span,
            action=action,
            confidence=claim.confidence,
            metadata={
                "priority": claim.priority,
                "specificity": cls._specificity(claim),
                "source": claim.source,
                "source_weight": cls._source_weight(claim.source),
                **metadata,
            },
        )

    @staticmethod
    def _overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
        return left[0] < right[1] and right[0] < left[1]
