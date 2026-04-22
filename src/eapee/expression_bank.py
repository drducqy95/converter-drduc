#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Expression bank for genre and emotion-aware dialogue flavor."""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "global" / "expressions" / "expression_bank.json"


class ExpressionBank:
    """Load a small curated expression dataset."""

    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path or DEFAULT_DATA_PATH)
        self._data = self._load()

    def _load(self) -> dict:
        if self.data_path.exists():
            return json.loads(self.data_path.read_text(encoding="utf-8"))
        return {
            "general": {"anger": ["hừ"], "joy": ["ha"], "respect": ["vâng"], "neutral": []},
            "xianxia": {"anger": ["hừ"], "joy": ["ha ha"], "respect": ["vãn bối xin lĩnh giáo"], "neutral": []},
            "modern": {"anger": ["này"], "joy": ["wow"], "respect": ["xin mời"], "neutral": []},
        }

    def pick_interjection(self, *, genre: str, emotion: str) -> str:
        genre_bucket = self._data.get(genre) or self._data.get("general", {})
        options = genre_bucket.get(emotion) or genre_bucket.get("neutral") or []
        return options[0] if options else ""
