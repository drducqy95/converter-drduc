#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Heuristic pronoun and dialogue context resolver."""

from __future__ import annotations

import json
import re
from pathlib import Path


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "global" / "expressions" / "pronoun_matrix.json"


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
        if speaker is None and is_dialogue:
            speaker = next((entity for entity in active_entities if entity in text), None)
        return {
            "is_dialogue": is_dialogue,
            "context_type": context_type or ("dialogue" if is_dialogue else "narrative"),
            "speaker": speaker,
            "listener": listener,
        }

    def resolve_token(self, text: str, pos: int, dialogue_context: dict, *, emotion: str | None, genre: str) -> dict | None:
        candidates = self.matrix.get(genre) or self.matrix.get("general", {})
        for key in sorted(candidates.keys(), key=len, reverse=True):
            if text.startswith(key, pos):
                target = candidates[key]
                if key == "我" and emotion == "respect":
                    target = "tại hạ" if genre == "xianxia" else "tôi"
                return {
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
        return None
