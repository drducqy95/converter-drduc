#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Heuristic emotion detector for dialogue-heavy text."""

from __future__ import annotations

from dataclasses import dataclass


CONTEXT_SCORE_THRESHOLDS = {
    "dialogue": 0.45,
    "inner_monologue": 1.01,
    "narrative": 1.01,
}
NEGATION_MARKERS = ("并非", "不是", "没有", "沒", "没", "非", "不")

EMOTION_MARKERS = {
    "anger": (
        ("怒吼", 0.7),
        ("咆哮", 0.7),
        ("愤怒", 0.7),
        ("恨", 0.45),
        ("吼", 0.45),
        ("骂", 0.45),
        ("该死", 0.55),
        ("混账", 0.55),
        ("怒", 0.35),
    ),
    "joy": (
        ("开心", 0.7),
        ("高兴", 0.7),
        ("欢喜", 0.65),
        ("喜悦", 0.65),
        ("哈哈", 0.7),
        ("笑道", 0.55),
        ("笑了", 0.55),
        ("乐呵", 0.55),
    ),
    "sadness": (
        ("痛哭", 0.75),
        ("伤心", 0.7),
        ("悲伤", 0.7),
        ("流泪", 0.55),
        ("哭", 0.45),
        ("叹", 0.35),
    ),
    "fear": (
        ("害怕", 0.8),
        ("恐惧", 0.8),
        ("惊恐", 0.75),
        ("惊慌", 0.7),
        ("毛骨悚然", 0.9),
        ("胆寒", 0.75),
        ("慌", 0.35),
        ("怕", 0.3),
    ),
    "respect": (
        ("前辈", 0.75),
        ("阁下", 0.75),
        ("大人", 0.6),
        ("请", 0.35),
    ),
}


@dataclass(slots=True)
class EmotionPrediction:
    label: str
    score: float
    evidence: list[str]


class SentenceContextClassifier:
    """Classify source sentence context before applying dialogue emotion rules."""

    QUOTE_MARKERS = ("“", "”", '"', "「", "」", "『", "』", "'", "‘", "’")
    SPEECH_MARKERS = (
        "说道",
        "问道",
        "喊道",
        "叫道",
        "笑道",
        "怒道",
        "喝道",
        "答道",
        "低声道",
        "喃喃道",
    )
    INNER_MONOLOGUE_MARKERS = (
        "他的心里",
        "她的心里",
        "心里",
        "内心",
        "心中",
        "脑海中",
        "脑海",
        "暗想",
        "心道",
        "心中想",
        "想到",
        "想着",
    )

    def classify(self, sentence: str) -> str:
        text = str(sentence or "")
        if not text.strip():
            return "narrative"

        has_speech = any(marker in text for marker in self.SPEECH_MARKERS)
        has_quote = any(marker in text for marker in self.QUOTE_MARKERS)
        has_inner = any(marker in text for marker in self.INNER_MONOLOGUE_MARKERS)

        if has_speech or has_quote:
            return "dialogue"
        if has_inner:
            return "inner_monologue"
        return "narrative"


class EmotionDetector:
    """Score simple emotions from lexical and punctuation cues."""

    def detect(self, text: str, *, context_type: str | None = None) -> list[EmotionPrediction]:
        normalized = str(text or "")
        threshold = CONTEXT_SCORE_THRESHOLDS.get(context_type or "", 0.0)
        predictions: list[EmotionPrediction] = []
        for label, markers in EMOTION_MARKERS.items():
            evidence: list[str] = []
            score = 0.0
            for marker, weight in markers:
                marker_hits = self._marker_hits(normalized, marker)
                active_hits = 0
                for hit_pos in marker_hits:
                    if self._is_negated(normalized, hit_pos):
                        continue
                    active_hits += 1
                if active_hits:
                    evidence.extend([marker] * active_hits)
                    score += weight * active_hits
            if "!" in normalized or "！" in normalized:
                if label == "anger":
                    score += 0.08
                elif label in {"fear", "joy"}:
                    score += 0.05
            if evidence and score >= threshold:
                predictions.append(
                    EmotionPrediction(
                        label=label,
                        score=min(1.0, score),
                        evidence=evidence,
                    )
                )
        if not predictions:
            predictions.append(EmotionPrediction(label="neutral", score=0.5, evidence=[]))
        return sorted(predictions, key=lambda item: item.score, reverse=True)

    def detect_label(self, text: str, *, context_type: str | None = None) -> str:
        return self.detect(text, context_type=context_type)[0].label

    @staticmethod
    def _marker_hits(text: str, marker: str) -> list[int]:
        positions: list[int] = []
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx < 0:
                return positions
            positions.append(idx)
            start = idx + len(marker)

    @staticmethod
    def _is_negated(text: str, marker_pos: int, window: int = 5) -> bool:
        left_context = text[max(0, marker_pos - window):marker_pos]
        negation_count = 0
        cursor = 0
        while cursor < len(left_context):
            matched = False
            for negation in NEGATION_MARKERS:
                if left_context.startswith(negation, cursor):
                    negation_count += 1
                    cursor += len(negation)
                    matched = True
                    break
            if not matched:
                cursor += 1
        return negation_count % 2 == 1
