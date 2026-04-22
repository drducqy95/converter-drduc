#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Heuristic emotion detector for dialogue-heavy text."""

from __future__ import annotations

from dataclasses import dataclass


EMOTION_MARKERS = {
    "anger": (
        ("怒吼", 0.7),
        ("咆哮", 0.7),
        ("愤怒", 0.7),
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


class EmotionDetector:
    """Score simple emotions from lexical and punctuation cues."""

    def detect(self, text: str) -> list[EmotionPrediction]:
        normalized = str(text or "")
        predictions: list[EmotionPrediction] = []
        for label, markers in EMOTION_MARKERS.items():
            evidence: list[str] = []
            score = 0.0
            for marker, weight in markers:
                if marker in normalized:
                    evidence.append(marker)
                    score += weight
            if "!" in normalized or "！" in normalized:
                if label == "anger":
                    score += 0.08
                elif label in {"fear", "joy"}:
                    score += 0.05
            if evidence:
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

    def detect_label(self, text: str) -> str:
        return self.detect(text)[0].label
