#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Heuristic pronoun and dialogue context resolver."""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "global" / "expressions" / "pronoun_matrix.json"


class PronounResolver:
    """Map source pronouns to Vietnamese forms using genre and scene hints."""

    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path or DEFAULT_DATA_PATH)
        self.matrix = self._load()

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

    def detect_dialogue_context(self, text: str, active_entities: list[str] | None = None) -> dict:
        active_entities = active_entities or []
        speaker = next((entity for entity in active_entities if entity in text), None)
        return {
            "is_dialogue": "“" in text or "\"" in text or "「" in text,
            "speaker": speaker,
            "listener": None,
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
