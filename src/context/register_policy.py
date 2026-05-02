#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Register-aware Vietnamese pronoun policy."""

from __future__ import annotations

from pathlib import Path

import yaml


DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[2] / "data" / "grammar" / "register_policy.yml"

DEFAULT_MATRIX = {
    "xianxia": {
        "male_subject": "hắn",
        "female_subject": "nàng",
        "neutral_subject": "y",
        "male_object": "hắn",
        "female_object": "nàng",
        "neutral_object": "người ấy",
        "first_subject": "ta",
        "second_subject": "ngươi",
    },
    "modern": {
        "male_subject": "anh ấy",
        "female_subject": "cô ấy",
        "neutral_subject": "họ",
        "male_object": "anh ấy",
        "female_object": "cô ấy",
        "neutral_object": "người đó",
        "first_subject": "tôi",
        "second_subject": "cậu",
    },
    "formal": {
        "male_subject": "ông ấy",
        "female_subject": "bà ấy",
        "neutral_subject": "người ấy",
        "male_object": "ông ấy",
        "female_object": "bà ấy",
        "neutral_object": "người ấy",
        "first_subject": "tôi",
        "second_subject": "ngài",
    },
    "casual": {
        "male_subject": "anh ta",
        "female_subject": "cô ta",
        "neutral_subject": "người ta",
        "male_object": "anh ta",
        "female_object": "cô ta",
        "neutral_object": "người ta",
        "first_subject": "mình",
        "second_subject": "cậu",
    },
}


class RegisterPolicy:
    """Load and query Vietnamese register pronoun choices."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or DEFAULT_POLICY_PATH)
        self.matrix = self._load()

    def select(self, *, register: str = "xianxia", gender: str | None = None, role: str = "subject") -> str:
        register_key = register if register in self.matrix else "xianxia"
        gender_key = self._normalize_gender(gender)
        role_key = role if role in {"subject", "object", "possessive", "vocative"} else "subject"
        candidates = self.matrix.get(register_key, {})
        return (
            candidates.get(f"{gender_key}_{role_key}")
            or candidates.get(f"{gender_key}_subject")
            or candidates.get(f"neutral_{role_key}")
            or candidates.get("neutral_subject")
            or "người ấy"
        )

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return DEFAULT_MATRIX
        payload = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        matrix = payload.get("registers") if isinstance(payload, dict) else None
        if not isinstance(matrix, dict):
            return DEFAULT_MATRIX
        merged = {key: dict(value) for key, value in DEFAULT_MATRIX.items()}
        for register, values in matrix.items():
            if isinstance(values, dict):
                merged[str(register)] = {str(key): str(value) for key, value in values.items()}
        return merged

    @staticmethod
    def _normalize_gender(gender: str | None) -> str:
        normalized = str(gender or "").strip().lower()
        if normalized in {"male", "m", "man", "boy"}:
            return "male"
        if normalized in {"female", "f", "woman", "girl"}:
            return "female"
        if normalized in {"first", "speaker"}:
            return "first"
        if normalized in {"second", "listener"}:
            return "second"
        return "neutral"
