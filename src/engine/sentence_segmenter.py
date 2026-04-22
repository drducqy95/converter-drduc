#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sentence segmentation for Chinese-centric text."""

from __future__ import annotations

from dataclasses import dataclass
import re


BOUNDARY_CHARS = set("。！？!?；;…")
RIGHT_QUOTES = set("\"”』」》】）)")
HEADING_LINE_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\d+[.)、:\-]\s*)?(?:"
    r"第[零〇一二三四五六七八九十百千万两\d]+[章节回卷篇].*|"
    r"Chapter\s+\d+.*|"
    r"CHAPTER\s+\d+.*|"
    r"Ch(?:ương|uong)\s+\d+.*"
    r")$"
)


@dataclass(slots=True)
class SentenceSpan:
    sentence_id: str
    text: str
    start: int
    end: int


class SentenceSegmenter:
    """Split text into sentence spans while keeping quote boundaries stable."""

    def split(self, text: str, prefix: str = "seg") -> list[SentenceSpan]:
        spans: list[SentenceSpan] = []
        buffer: list[str] = []
        start = 0

        def flush(end_idx: int):
            nonlocal buffer, start
            sentence = "".join(buffer).strip()
            if sentence:
                spans.append(SentenceSpan(sentence_id=f"{prefix}-{len(spans)+1:04d}", text=sentence, start=start, end=end_idx))
            buffer = []

        for idx, ch in enumerate(text):
            if not buffer:
                start = idx
            buffer.append(ch)

            if ch in BOUNDARY_CHARS:
                if ch == "…" and idx + 1 < len(text) and text[idx + 1] == "…":
                    continue
                if idx + 1 < len(text) and text[idx + 1] in RIGHT_QUOTES:
                    continue
                flush(idx + 1)
                continue

            prev = text[idx - 1] if idx > 0 else ""
            if ch in RIGHT_QUOTES and prev in BOUNDARY_CHARS:
                flush(idx + 1)
                continue

            if ch != "\n":
                continue

            current = "".join(buffer).strip()
            if current and HEADING_LINE_RE.match(current):
                flush(idx + 1)
                continue

            next_char = text[idx + 1] if idx + 1 < len(text) else ""
            if next_char == "\n":
                flush(idx + 1)
                continue

            if prev in BOUNDARY_CHARS or prev in RIGHT_QUOTES:
                flush(idx + 1)

        if buffer:
            flush(len(text))

        return spans
