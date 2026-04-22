#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared filters for separating runtime translation entries from reference glosses."""

from __future__ import annotations

import re


def looks_like_reference_gloss(category: str, target: str) -> bool:
    """Return True when a row looks like reference/help text, not a runtime translation."""
    if not category or not target:
        return False

    if category.endswith("_reference"):
        return True

    normalized = " ".join(target.split())
    if category == "trichdan_idioms":
        if (
            normalized.startswith("✚")
            or " U+" in normalized
            or " Bộ " in normalized
            or "Giản thể của chữ" in normalized
        ):
            return True

    return False


def extract_concise_reference_fallback(category: str, target: str) -> str:
    """Return a short safe fallback target from reference rows, or an empty string."""
    if not category or not target:
        return ""

    normalized = " ".join(target.split())
    if not normalized or len(normalized) > 48:
        return ""

    if category in {"thieuchuu_reference", "lacviet_reference"}:
        if any(token in normalized for token in ("CL:", "[", "]", "(", ")")):
            return ""
        value = _first_reference_token(normalized)
        if not value:
            return ""
        if value.isupper() and any(ch.isalpha() for ch in value):
            value = value.title()
        return value

    if category == "cedict_reference":
        if any(token in normalized for token in (";", "[", "]", "(", ")", "CL:")):
            return ""
        if not normalized[:1].isupper():
            return ""
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .&'/-]*", normalized):
            return ""
        return normalized

    return ""


def _first_reference_token(value: str) -> str:
    first = value
    for separator in (";", "|", "/", ","):
        if separator in first:
            first = first.split(separator, 1)[0]
    return first.strip()
