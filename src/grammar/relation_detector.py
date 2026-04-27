#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Detect high-level grammar relations from Chinese clauses."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from src.grammar.clause_segmenter import Clause


class RelationType(Enum):
    CONDITION = "condition"
    CONCESSION = "concession"
    CAUSE_EFFECT = "cause_effect"
    CONTRAST = "contrast"
    TEMPORAL = "temporal"
    PURPOSE = "purpose"
    VIEWPOINT = "viewpoint"
    PASSIVE = "passive"
    DISPOSAL = "ba_construction"
    PARALLEL_ACTION = "parallel_action"
    DEFINITION = "definition"
    EVIDENTIAL = "evidential"
    COMPARISON = "comparison"
    PRECAUTION = "precaution"
    EMPHATIC_EVEN = "emphatic_even"
    NECESSITY = "necessity"
    REGARDLESS = "regardless"
    PROBABILITY = "probability"
    CORRECTION = "correction"


@dataclass(slots=True)
class Relation:
    relation_type: RelationType
    marker: str
    clause_indexes: list[int] = field(default_factory=list)
    confidence: float = 0.80


MARKER_MAP: dict[RelationType, tuple[str, ...]] = {
    RelationType.CONDITION: ("如果", "若", "若是", "只要", "一旦", "除非", "倘若", "假如"),
    RelationType.CONCESSION: ("虽然", "虽说", "即便", "即使", "哪怕", "就算", "尽管"),
    RelationType.CAUSE_EFFECT: ("因为", "由于", "鉴于", "基于", "所以", "因此", "于是", "导致", "使得"),
    RelationType.VIEWPOINT: ("作为", "从", "就", "对于", "对", "至于", "关于"),
    RelationType.PARALLEL_ACTION: ("一边", "一面", "边"),
    RelationType.DEFINITION: ("所谓", "所谓的", "也就是说", "换言之", "换句话说"),
    RelationType.EVIDENTIAL: ("据说", "据悉", "据了解", "据报道", "据", "称"),
    RelationType.PRECAUTION: ("以防", "以防万一", "以备不时之需"),
    RelationType.EMPHATIC_EVEN: ("就连", "连"),
    RelationType.PASSIVE: ("被", "为", "所"),
    RelationType.DISPOSAL: ("把", "将"),
    RelationType.COMPARISON: ("比", "不如", "胜过"),
    RelationType.NECESSITY: ("必须", "需要", "不得不"),
    RelationType.REGARDLESS: ("无论如何", "不管怎样", "不管怎么说", "无论", "不管"),
    RelationType.PROBABILITY: ("说不定", "也许", "或许", "大概", "估计", "想必", "多半"),
    RelationType.CORRECTION: ("不是", "而是", "并非", "不但", "不仅"),
}


class RelationDetector:
    """Marker-based relation detector used before rule claims."""

    def detect(self, clauses: list[Clause] | list[str]) -> list[Relation]:
        normalized = [
            clause.text if isinstance(clause, Clause) else str(clause)
            for clause in clauses
        ]
        relations: list[Relation] = []
        for idx, text in enumerate(normalized):
            for relation_type, markers in MARKER_MAP.items():
                marker = self._find_marker(text, relation_type, markers)
                if not marker:
                    continue
                confidence = 0.90 if relation_type in {
                    RelationType.CONDITION,
                    RelationType.CONCESSION,
                    RelationType.CAUSE_EFFECT,
                    RelationType.PARALLEL_ACTION,
                    RelationType.DEFINITION,
                } else 0.78
                relations.append(Relation(relation_type, marker, [idx], confidence))
        return self._dedupe(relations)

    @staticmethod
    def _find_marker(text: str, relation_type: RelationType, markers: tuple[str, ...]) -> str:
        if relation_type == RelationType.VIEWPOINT:
            viewpoint_patterns = [
                r"作为.+?而言",
                r"从.+?角度来看",
                r"就.+?而言",
                r"对.+?来说",
            ]
            for pattern in viewpoint_patterns:
                if re.search(pattern, text):
                    return pattern
        if relation_type == RelationType.PASSIVE and re.search(r"(?:被|为).{1,12}所", text):
            return "为...所"
        if relation_type == RelationType.PARALLEL_ACTION and re.search(r"一[边面].+?一[边面]", text):
            return "一边...一边"
        if relation_type == RelationType.CONDITION and re.search(r"(?:如果|只要|一旦).+?就", text):
            return "condition...就"
        if relation_type == RelationType.CONCESSION and re.search(r"(?:哪怕|就算|即便|即使).+?(?:也|都|仍然|还是)", text):
            return "concession...也"
        if relation_type == RelationType.REGARDLESS and re.search(r"(?:无论|不管).+?(?:也|都)", text):
            return "无论/不管...都"
        if relation_type == RelationType.CORRECTION and re.search(r"不是.+?而是", text):
            return "不是...而是"
        for marker in sorted(markers, key=len, reverse=True):
            if marker in text:
                return marker
        return ""

    @staticmethod
    def _dedupe(relations: list[Relation]) -> list[Relation]:
        seen: set[tuple[RelationType, str, tuple[int, ...]]] = set()
        deduped: list[Relation] = []
        for relation in relations:
            key = (relation.relation_type, relation.marker, tuple(relation.clause_indexes))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(relation)
        return deduped
