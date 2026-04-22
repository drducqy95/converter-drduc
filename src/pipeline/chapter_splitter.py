#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Split normalized documents into chapters with fallbacks."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


HEADING_RE = re.compile(
    r"(?m)^(?:#{1,6}\s*)?(?:\d+[.)、:\-]\s*)?(?:"
    r"第[零〇一二三四五六七八九十百千万两\d]+[章节回卷篇].*|"
    r"Chapter\s+\d+.*|"
    r"CHAPTER\s+\d+.*|"
    r"Ch(?:ương|uong)\s+\d+.*"
    r")$"
)


@dataclass(slots=True)
class Chapter:
    chapter_id: str
    title: str
    text: str
    start: int
    end: int


class ChapterSplitter:
    """Split by headings first, then by safe-size fallback."""

    def split(self, text: str) -> list[Chapter]:
        matches = list(HEADING_RE.finditer(text))
        if not matches:
            return self._fallback_split(text)

        chapters: list[Chapter] = []
        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            block = text[start:end].strip()
            lines = block.splitlines()
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            chapters.append(
                Chapter(
                    chapter_id=f"chapter-{idx+1:03d}",
                    title=title,
                    text=body,
                    start=start,
                    end=end,
                )
            )
        return chapters

    def write(self, chapters: list[Chapter], project_dir: str | Path):
        project_path = Path(project_dir)
        chapter_dir = project_path / "source" / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        index_path = chapter_dir / "chapters_index.json"

        index_payload = []
        for chapter in chapters:
            target = chapter_dir / f"{chapter.chapter_id}.txt"
            target.write_text(chapter.text, encoding="utf-8")
            index_payload.append(asdict(chapter))

        index_path.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _fallback_split(self, text: str, max_chars: int = 2200) -> list[Chapter]:
        paragraphs = [block.strip() for block in text.split("\n\n") if block.strip()]
        chapters: list[Chapter] = []
        current: list[str] = []
        start = 0
        cursor = 0

        for paragraph in paragraphs:
            if sum(len(part) for part in current) + len(paragraph) > max_chars and current:
                block = "\n\n".join(current)
                chapters.append(
                    Chapter(
                        chapter_id=f"chapter-{len(chapters)+1:03d}",
                        title=f"Auto Split {len(chapters)+1}",
                        text=block,
                        start=start,
                        end=cursor,
                    )
                )
                current = []
                start = cursor

            current.append(paragraph)
            cursor += len(paragraph) + 2

        if current:
            block = "\n\n".join(current)
            chapters.append(
                Chapter(
                    chapter_id=f"chapter-{len(chapters)+1:03d}",
                    title=f"Auto Split {len(chapters)+1}",
                    text=block,
                    start=start,
                    end=len(text),
                )
            )
        return chapters
