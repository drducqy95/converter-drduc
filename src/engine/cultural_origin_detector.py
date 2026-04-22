#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Detect coarse cultural-origin hints used by ranking and config generation."""

from __future__ import annotations


class CulturalOriginDetector:
    """Simple heuristic detector for naming/output policy."""

    HAN_VIET_MARKERS = ("宗", "门", "派", "宫", "帝", "仙", "道", "尊", "真人")
    WESTERN_MARKERS = ("Mr.", "Mrs.", "John", "Mary", "king", "queen", "sir")
    MODERN_MARKERS = ("公司", "电脑", "软件", "网络", "手机")

    def detect(self, text: str) -> str:
        lowered = text.lower()
        if any(marker.lower() in lowered for marker in self.WESTERN_MARKERS):
            return "western"
        if any(marker in text for marker in self.MODERN_MARKERS):
            return "modern_cn"
        if any(marker in text for marker in self.HAN_VIET_MARKERS):
            return "han_viet"
        if any("A" <= ch <= "Z" or "a" <= ch <= "z" for ch in text):
            return "mixed"
        return "neutral"
