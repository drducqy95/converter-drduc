#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Universe id helpers.

In v24, a universe is one concrete work/book/project, not a genre bucket.
The persisted id is a stable slug derived from the story title.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


def slugify_universe_id(value: str | None) -> str:
    """Return a stable universe id from a book or project title."""

    raw = str(value or "").strip()
    if not raw:
        return ""
    normalized = unicodedata.normalize("NFD", raw)
    without_marks = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    without_marks = without_marks.replace("đ", "d").replace("Đ", "D")
    chars: list[str] = []
    for char in without_marks:
        if char.isascii() and char.isalnum():
            chars.append(char.lower())
        elif "\u4e00" <= char <= "\u9fff":
            chars.append(char)
        else:
            chars.append("_")
    slug = re.sub(r"_+", "_", "".join(chars)).strip("_")
    return slug or "unknown"


def resolve_project_universe_id(
    *,
    project_id: str | None = None,
    project_dir: str | Path | None = None,
    title: str | None = None,
    config: dict | None = None,
) -> str:
    """Resolve the active story universe for a project.

    Priority: explicit title/config -> project state/config files -> project id
    or project directory name.
    """

    candidates: list[str] = []
    if title:
        candidates.append(title)
    if config:
        candidates.extend(_title_candidates_from_config(config))

    path = Path(project_dir) if project_dir else None
    if path:
        candidates.extend(_title_candidates_from_file(path / "working" / "config" / "translation_config.json"))
        candidates.extend(_title_candidates_from_file(path / "state" / "project_state.json"))
        candidates.append(path.name)
    if project_id:
        candidates.append(project_id)

    for candidate in candidates:
        slug = slugify_universe_id(candidate)
        if slug:
            return slug
    return "unknown"


def _title_candidates_from_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return _title_candidates_from_config(payload) if isinstance(payload, dict) else []


def _title_candidates_from_config(payload: dict) -> list[str]:
    keys = (
        "universe_id",
        "universe",
        "book_title",
        "story_title",
        "project_title",
        "work",
        "title",
        "project_id",
    )
    return [str(payload.get(key) or "").strip() for key in keys if str(payload.get(key) or "").strip()]
