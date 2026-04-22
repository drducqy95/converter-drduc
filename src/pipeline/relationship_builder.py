#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build lightweight relationship edges from entities and text patterns."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from src.pipeline.entity_scanner import EntitySuggestion


KINSHIP_TERMS = {
    "父亲": "parent",
    "母亲": "parent",
    "师父": "mentor",
    "弟子": "disciple",
    "哥哥": "sibling",
    "妹妹": "sibling",
}


@dataclass(slots=True)
class RelationshipEdge:
    source: str
    target: str
    relation_type: str
    confidence: float
    evidence: str

    def to_dict(self) -> dict:
        return asdict(self)


class RelationshipBuilder:
    """Infer a small graph for EAPEE and context ranking."""

    def build(self, text: str, entities: list[EntitySuggestion]) -> list[RelationshipEdge]:
        edges: list[RelationshipEdge] = []
        entity_names = [entity.source for entity in entities]
        for idx, first in enumerate(entity_names):
            for second in entity_names[idx + 1:]:
                if first not in text or second not in text:
                    continue
                evidence = self._extract_window(text, first, second)
                relation_type = self._infer_relation(evidence)
                confidence = 0.9 if relation_type != "co_occurrence" else 0.55
                edges.append(
                    RelationshipEdge(
                        source=first,
                        target=second,
                        relation_type=relation_type,
                        confidence=confidence,
                        evidence=evidence,
                    )
                )
        return edges

    def _extract_window(self, text: str, first: str, second: str, radius: int = 100) -> str:
        # Tìm các vị trí xuất hiện của first và second
        first_idx = text.find(first)
        second_idx = text.find(second)
        
        # Nếu chúng cách nhau quá xa, có thể chúng không hề liên quan trong cùng ngữ cảnh
        if abs(first_idx - second_idx) > 500:
            return f"{text[max(0, first_idx - 20):first_idx + len(first) + 20]} ... {text[max(0, second_idx - 20):second_idx + len(second) + 20]}"
            
        start = max(0, min(first_idx, second_idx) - radius)
        end = min(len(text), max(first_idx + len(first), second_idx + len(second)) + radius)
        return text[start:end].strip()

    def _infer_relation(self, evidence: str) -> str:
        for marker, relation in KINSHIP_TERMS.items():
            if marker in evidence:
                return relation
        if re.search(r"[说道说问答叫道]", evidence):
            return "dialogue"
        if "宗" in evidence or "门" in evidence or "派" in evidence:
            return "faction"
        return "co_occurrence"
