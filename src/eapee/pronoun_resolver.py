#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Heuristic pronoun and dialogue context resolver."""

from __future__ import annotations

import json
import re
from pathlib import Path


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "global" / "expressions" / "pronoun_matrix.json"
THIRD_PERSON_PRONOUNS = {"\u4ed6", "\u5979", "\u5b83"}
PLURAL_THIRD_PERSON_PRONOUNS = {"\u4ed6\u4eec", "\u5979\u4eec"}
ENTITY_TYPE_ALIASES = {
    "character": "person",
    "name": "person",
    "person_name": "person",
    "place": "location",
    "loc": "location",
    "org": "organization",
    "organisation": "organization",
    "faction": "organization",
}


class SpeakerTracker:
    """Track explicit and implicit speaker/listener pairs across dialogue turns."""

    SPEECH_VERBS = ("说道", "说", "道", "问道", "问", "喊道", "叫道", "笑道", "怒道", "喝道", "答道")
    LISTENER_PREFIXES = ("对", "向", "朝", "冲", "问")

    def __init__(self):
        self.last_speaker: str | None = None
        self.last_listener: str | None = None
        self.conversation_stack: list[tuple[str | None, str | None]] = []

    def update_from_sentence(
        self,
        sentence: str,
        active_entities: list[str],
        *,
        is_dialogue: bool,
    ) -> tuple[str | None, str | None]:
        if not is_dialogue:
            return None, None

        speaker = self._explicit_speaker(sentence, active_entities)
        if speaker:
            listener = self._explicit_listener(sentence, active_entities, speaker)
            if listener is None and self.last_speaker and self.last_speaker != speaker:
                listener = self.last_speaker
            self._remember(speaker, listener)
            return speaker, listener

        if self.last_speaker and self.last_listener:
            speaker, listener = self.last_listener, self.last_speaker
            self._remember(speaker, listener)
            return speaker, listener

        return None, None

    def _explicit_speaker(self, sentence: str, active_entities: list[str]) -> str | None:
        for entity in sorted(active_entities, key=len, reverse=True):
            if not entity:
                continue
            for verb in self.SPEECH_VERBS:
                if f"{entity}{verb}" in sentence:
                    return entity
            pattern = re.compile(re.escape(entity) + r".{0,4}(?:说|道|问|喊|叫|笑|怒|喝|答)")
            if pattern.search(sentence):
                return entity
        return None

    def _explicit_listener(self, sentence: str, active_entities: list[str], speaker: str) -> str | None:
        for entity in sorted(active_entities, key=len, reverse=True):
            if not entity or entity == speaker:
                continue
            if any(f"{prefix}{entity}" in sentence for prefix in self.LISTENER_PREFIXES):
                return entity
        return None

    def _remember(self, speaker: str | None, listener: str | None):
        self.last_speaker = speaker
        self.last_listener = listener
        self.conversation_stack.append((speaker, listener))
        if len(self.conversation_stack) > 12:
            self.conversation_stack = self.conversation_stack[-12:]


class PronounResolver:
    """Map source pronouns to Vietnamese forms using genre and scene hints."""

    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path or DEFAULT_DATA_PATH)
        self.matrix = self._load()
        self.speaker_tracker = SpeakerTracker()
        self._entity_signature = ""
        self._entity_records: dict[str, dict] = {}
        self._relationships: list[dict] = []
        self._recent_mentions: list[str] = []

    def _load(self) -> dict:
        if self.data_path.exists():
            return json.loads(self.data_path.read_text(encoding="utf-8"))
        return {
            "general": {
                "我": "ta",
                "你": "ngươi",
                "他": "hắn",
                "她": "nàng",
                "他们": "bọn họ",
                "她们": "các nàng",
                "我们": "chúng ta",
                "你们": "các ngươi",
            },
            "modern": {
                "我": "tôi",
                "你": "cậu",
                "他": "anh",
                "她": "cô ấy",
                "他们": "họ",
                "她们": "họ",
                "我们": "chúng tôi",
                "你们": "các cậu",
            },
            "xianxia": {"我": "bản tọa", "你": "ngươi", "他": "hắn", "她": "nàng"},
            "royal": {"我": "trẫm", "你": "khanh", "他": "hắn", "她": "nàng"},
        }

    def detect_dialogue_context(
        self,
        text: str,
        active_entities: list[str] | None = None,
        *,
        context_type: str | None = None,
    ) -> dict:
        active_entities = active_entities or []
        is_dialogue = context_type == "dialogue" if context_type else ("“" in text or "\"" in text or "「" in text)
        speaker, listener = self.speaker_tracker.update_from_sentence(
            text,
            active_entities,
            is_dialogue=is_dialogue,
        )
        sentence_mentions = self._mentions_in_text(text, active_entities)
        self._remember_mentions(sentence_mentions)
        if speaker is None and is_dialogue:
            speaker = next((entity for entity in active_entities if entity in text), None)
        return {
            "is_dialogue": is_dialogue,
            "context_type": context_type or ("dialogue" if is_dialogue else "narrative"),
            "speaker": speaker,
            "listener": listener,
            "sentence_mentions": sentence_mentions,
        }

    def set_entity_graph(self, entities: list[dict] | None, relationships: list[dict] | None):
        """Register entity metadata and relationship edges for third-person pronouns."""
        entities = entities or []
        relationships = relationships or []
        signature = json.dumps(
            {"entities": entities, "relationships": relationships},
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        if signature == self._entity_signature:
            return
        self._entity_signature = signature
        self._entity_records = {}
        for item in entities:
            source = str(item.get("source") or "").strip()
            if not source:
                continue
            self._entity_records[source] = {
                "source": source,
                "target": str(item.get("target") or source).strip(),
                "entity_type": self._normalize_entity_type(str(item.get("entity_type") or item.get("type") or "")),
                "gender": str(item.get("gender") or item.get("sex") or "").strip().lower(),
            }
        self._relationships = [dict(edge) for edge in relationships if isinstance(edge, dict)]
        self._recent_mentions = []

    def resolve_token(self, text: str, pos: int, dialogue_context: dict, *, emotion: str | None, genre: str) -> dict | None:
        candidates = self.matrix.get(genre) or self.matrix.get("general", {})
        for key in sorted(candidates.keys(), key=len, reverse=True):
            if text.startswith(key, pos):
                target = candidates[key]
                if key == "我" and emotion == "respect":
                    target = "tại hạ" if genre == "xianxia" else "tôi"
                payload = {
                    "source": key,
                    "selected": target,
                    "candidates": [target],
                    "priority": 70,
                    "fallback_level": "pronoun",
                    "reason": f"pronoun_matrix:{genre}",
                    "target": target,
                    "length": len(key),
                    "speaker": dialogue_context.get("speaker"),
                    "listener": dialogue_context.get("listener"),
                }
                graph_candidate = self._resolve_graph_candidate(key, text, pos, dialogue_context)
                if graph_candidate:
                    payload.update(graph_candidate)
                    payload["priority"] = 78
                    payload["reason"] = f"pronoun_graph:{graph_candidate.get('relation_type') or 'context'}"
                return payload
        return None

    def _resolve_graph_candidate(self, pronoun: str, text: str, pos: int, dialogue_context: dict) -> dict | None:
        if pronoun not in THIRD_PERSON_PRONOUNS and pronoun not in PLURAL_THIRD_PERSON_PRONOUNS:
            return None
        if not self._entity_records:
            return None

        mentions_before = self._mentions_before(text, pos)
        search_order = [*mentions_before, *reversed(self._recent_mentions)]
        seen: set[str] = set()
        ranked: list[tuple[float, str, str, float]] = []
        speaker = dialogue_context.get("speaker")
        listener = dialogue_context.get("listener")

        for index, source in enumerate(search_order):
            if source in seen or source not in self._entity_records:
                continue
            seen.add(source)
            if source == speaker and any(candidate != speaker for candidate in search_order):
                continue
            if source == listener and any(candidate not in {speaker, listener} for candidate in search_order):
                continue
            record = self._entity_records[source]
            if not self._pronoun_matches_entity(pronoun, record):
                continue
            relation_type, relation_confidence = self._relationship_to_context(source, speaker, listener)
            score = 1.0 / (index + 1)
            if relation_type:
                score += relation_confidence
            if source in mentions_before:
                score += 0.5
            ranked.append((score, source, relation_type, relation_confidence))

        if not ranked:
            return None

        ranked.sort(key=lambda item: item[0], reverse=True)
        _score, source, relation_type, relation_confidence = ranked[0]
        record = self._entity_records[source]
        return {
            "resolved_entity": source,
            "resolved_target": record.get("target") or source,
            "resolved_entity_type": record.get("entity_type") or "",
            "relation_type": relation_type or "recent_mention",
            "relation_confidence": round(float(relation_confidence or 0.0), 3),
        }

    def _mentions_in_text(self, text: str, active_entities: list[str]) -> list[str]:
        candidates = set(active_entities) | set(self._entity_records)
        spans: list[tuple[int, str]] = []
        for source in candidates:
            if not source:
                continue
            start = text.find(source)
            while start != -1:
                spans.append((start, source))
                start = text.find(source, start + len(source))
        return [source for _pos, source in sorted(spans, key=lambda item: (item[0], -len(item[1])))]

    def _mentions_before(self, text: str, pos: int) -> list[str]:
        mentions = []
        for source in self._entity_records:
            start = text.rfind(source, 0, pos)
            if start != -1:
                mentions.append((start, source))
        return [source for _start, source in sorted(mentions, key=lambda item: item[0], reverse=True)]

    def _remember_mentions(self, mentions: list[str]):
        for source in mentions:
            if source in self._recent_mentions:
                self._recent_mentions.remove(source)
            self._recent_mentions.append(source)
        if len(self._recent_mentions) > 24:
            self._recent_mentions = self._recent_mentions[-24:]

    def _relationship_to_context(self, source: str, speaker: str | None, listener: str | None) -> tuple[str, float]:
        best_relation = ""
        best_confidence = 0.0
        anchors = {item for item in (speaker, listener) if item}
        if not anchors:
            return best_relation, best_confidence
        for edge in self._relationships:
            left = str(edge.get("source") or "").strip()
            right = str(edge.get("target") or "").strip()
            if not left or not right:
                continue
            if (source == left and right in anchors) or (source == right and left in anchors):
                confidence = float(edge.get("confidence") or 0.0)
                if confidence >= best_confidence:
                    best_confidence = confidence
                    best_relation = str(edge.get("relation_type") or "related")
        return best_relation, best_confidence

    def _pronoun_matches_entity(self, pronoun: str, record: dict) -> bool:
        entity_type = self._normalize_entity_type(record.get("entity_type", ""))
        gender = str(record.get("gender") or "").lower()
        if pronoun == "\u5b83":
            return entity_type not in {"person", "organization"}
        if pronoun == "\u5979":
            return entity_type in {"", "person"} and gender in {"", "female", "f", "woman", "girl"}
        if pronoun in {"\u4ed6", "\u4ed6\u4eec", "\u5979\u4eec"}:
            return entity_type in {"", "person", "organization"}
        return False

    @staticmethod
    def _normalize_entity_type(value: str) -> str:
        normalized = (value or "").strip().lower().replace("-", "_")
        return ENTITY_TYPE_ALIASES.get(normalized, normalized)
