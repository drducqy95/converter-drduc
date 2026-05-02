#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dialogue speaker/listener tracking."""

from __future__ import annotations

import re


class SpeakerTracker:
    """Track explicit and implicit speaker/listener pairs across dialogue turns."""

    SPEECH_VERBS = (
        "说道",
        "说",
        "道",
        "问道",
        "问",
        "喊道",
        "叫道",
        "笑道",
        "怒道",
        "喝道",
        "答道",
        "冷声道",
        "低声道",
        "大声道",
        "沉声道",
        "轻声道",
        "厉声道",
        "淡淡道",
        "心中暗道",
        "心想",
        "暗想",
        "开口道",
        "接口道",
        "回答道",
        "叹道",
        "喃喃道",
        "传音道",
        "嘀咕道",
    )
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
        verb_pattern = "|".join(re.escape(verb) for verb in sorted(self.SPEECH_VERBS, key=len, reverse=True))
        for entity in sorted(active_entities, key=len, reverse=True):
            if not entity:
                continue
            for verb in self.SPEECH_VERBS:
                if f"{entity}{verb}" in sentence:
                    return entity
            pattern = re.compile(re.escape(entity) + rf".{{0,4}}(?:{verb_pattern})")
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
