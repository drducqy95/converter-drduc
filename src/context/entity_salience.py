#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entity salience memory for local pronoun decisions."""

from __future__ import annotations

from dataclasses import dataclass


ROLE_BOOSTS = {
    "subject": 1.0,
    "vocative": 0.95,
    "object": 0.82,
    "possessive": 0.72,
}


@dataclass(slots=True)
class EntitySalience:
    entity_id: str
    last_seen_segment: str
    last_role: str
    salience_score: float
    gender: str | None
    register: str | None
    mention_count: int = 0


class EntitySalienceMemory:
    """Track recently salient entities with deterministic decay."""

    def __init__(self, *, decay_factor: float = 0.85):
        self.decay_factor = decay_factor
        self._entities: dict[str, EntitySalience] = {}

    def update(
        self,
        entity_id: str,
        role: str,
        segment_id: str,
        *,
        gender: str | None = None,
        register: str | None = None,
    ) -> None:
        entity_id = str(entity_id or "").strip()
        if not entity_id:
            return
        role = role if role in ROLE_BOOSTS else "object"
        score = ROLE_BOOSTS[role]
        current = self._entities.get(entity_id)
        if current is None:
            self._entities[entity_id] = EntitySalience(
                entity_id=entity_id,
                last_seen_segment=str(segment_id),
                last_role=role,
                salience_score=score,
                gender=gender,
                register=register,
                mention_count=1,
            )
            return
        current.last_seen_segment = str(segment_id)
        current.last_role = role
        current.salience_score = min(1.0, max(current.salience_score, score) + 0.08)
        current.gender = gender or current.gender
        current.register = register or current.register
        current.mention_count += 1

    def decay(self, segment_id: str) -> None:
        for entity in self._entities.values():
            if entity.last_seen_segment != str(segment_id):
                entity.salience_score *= self.decay_factor

    def get_most_salient(self, *, gender: str | None = None) -> EntitySalience | None:
        candidates = list(self._entities.values())
        if gender:
            normalized = gender.strip().lower()
            candidates = [entity for entity in candidates if (entity.gender or "").lower() in {"", normalized}]
        if not candidates:
            return None
        return sorted(candidates, key=lambda entity: (entity.salience_score, entity.mention_count), reverse=True)[0]

    def reset_chapter(self) -> None:
        self._entities.clear()

    @property
    def entities(self) -> dict[str, EntitySalience]:
        return self._entities
