#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Minimal grammar rule registry for priority-ordered rule claims."""

from __future__ import annotations

from typing import Protocol

from src.grammar.clause_segmenter import Clause
from src.grammar.rule_claim import RuleClaim


class GrammarRule(Protocol):
    rule_id: str
    priority: int

    def match(self, clause: Clause) -> RuleClaim | None:
        ...


class RuleRegistry:
    def __init__(self):
        self._rules: list[GrammarRule] = []

    def register(self, rule: GrammarRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda item: item.priority, reverse=True)

    def collect_claims(self, clauses: list[Clause]) -> list[RuleClaim]:
        claims: list[RuleClaim] = []
        for clause in clauses:
            for rule in self._rules:
                claim = rule.match(clause)
                if claim:
                    claims.append(claim)
        return claims

