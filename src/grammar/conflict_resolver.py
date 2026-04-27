#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resolve overlapping grammar rule claims."""

from __future__ import annotations

from src.grammar.rule_claim import RuleClaim


class ConflictResolver:
    """Keep highest-priority non-overlapping claims."""

    def resolve(self, claims: list[RuleClaim]) -> list[RuleClaim]:
        accepted: list[RuleClaim] = []
        for claim in sorted(claims, key=lambda item: (-item.priority, -item.confidence, item.source_span)):
            if claim.protected:
                continue
            if any(self._overlap(claim.source_span, existing.source_span) for existing in accepted):
                continue
            accepted.append(claim)
        return sorted(accepted, key=lambda item: item.source_span)

    @staticmethod
    def _overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
        return left[0] < right[1] and right[0] < left[1]

