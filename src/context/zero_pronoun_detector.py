#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Heuristic zero-pronoun insertion candidates."""

from __future__ import annotations

from dataclasses import dataclass

from src.context.entity_salience import EntitySalienceMemory


SUBJECT_TAKING_VERBS = (
    "走",
    "来",
    "去",
    "看",
    "望",
    "听",
    "想",
    "说",
    "问",
    "答",
    "笑",
    "怒",
    "喝",
    "喊",
    "叫",
    "坐",
    "站",
    "拿",
    "取",
    "放",
    "打",
    "抓",
    "修炼",
    "催动",
    "施展",
    "发动",
    "进入",
    "离开",
    "回头",
    "点头",
    "摇头",
    "皱眉",
    "沉默",
    "叹息",
    "转身",
    "冲",
)
SUBJECT_BOUNDARIES = set("，。！？；：、“”‘’「」『』（）()[]{} \n\r\t")


@dataclass(slots=True)
class ZeroPronounCandidate:
    insertion_pos: int
    entity_id: str
    verb: str
    confidence: float
    reason: str = "zero_pronoun_salience"


class ZeroPronounDetector:
    """Detect low-risk subject elision positions."""

    def __init__(self, verbs: tuple[str, ...] | None = None):
        self.verbs = tuple(sorted(verbs or SUBJECT_TAKING_VERBS, key=len, reverse=True))

    def detect(
        self,
        sentence: str,
        memory: EntitySalienceMemory,
        *,
        segment_id: str = "",
        is_dialogue: bool = False,
        ambiguity_level: str = "low",
    ) -> list[ZeroPronounCandidate]:
        if is_dialogue or ambiguity_level not in {"low", "none"}:
            return []
        salient = memory.get_most_salient()
        if salient is None or salient.salience_score <= 0.6:
            return []

        candidates: list[ZeroPronounCandidate] = []
        for pos, verb in self._verb_positions(sentence):
            if not self._subject_position_empty(sentence, pos):
                continue
            candidates.append(
                ZeroPronounCandidate(
                    insertion_pos=pos,
                    entity_id=salient.entity_id,
                    verb=verb,
                    confidence=round(min(salient.salience_score, 0.95), 3),
                )
            )
        _ = segment_id
        return candidates

    def _verb_positions(self, sentence: str) -> list[tuple[int, str]]:
        positions: list[tuple[int, str]] = []
        for pos in range(len(sentence)):
            for verb in self.verbs:
                if sentence.startswith(verb, pos):
                    positions.append((pos, verb))
                    break
        return positions

    @staticmethod
    def _subject_position_empty(sentence: str, verb_pos: int) -> bool:
        prefix = sentence[:verb_pos].rstrip()
        if not prefix:
            return True
        return prefix[-1] in SUBJECT_BOUNDARIES
