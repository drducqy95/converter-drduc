#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rule-based segment typing for novel translation inputs."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.core.trace import TraceEvent
from src.pipeline.packet import SegmentPacket, SegmentType


CHAPTER_TITLE_PATTERNS = [
    r"^第[零〇一二三四五六七八九十百千万两\d]+[章节回卷篇]",
    r"^Chapter\s+\d+",
    r"^CHAPTER\s+\d+",
    r"^番外",
]

AUTHOR_NOTE_PATTERNS = [
    r"(?:^|[（(【\[])\s*PS[:：]",
    r"作者有话说",
    r"本章完",
    r"求月票",
    r"求推荐",
    r"求收藏",
    r"新书上传",
]

ADVERTISEMENT_PATTERNS = [
    r"点击.*收藏",
    r"加入书架",
    r"手机用户请到",
    r"最新网址",
]

SYSTEM_PROMPT_PATTERNS = [
    r"^【(?:系统|面板|任务|属性|提示|状态|技能|奖励).{0,40}】$",
]

FORUM_PATTERNS = [
    r"楼主",
    r"顶一下",
    r"\b\d+楼\b",
]

DIALOGUE_RE = re.compile(r"(?:[说道问答喊叫骂笑叹]|冷声道|沉声道|低声道)[:：][“\"'‘]")
THOUGHT_RE = re.compile(r"(?:心中|暗自|心里|脑中).{0,8}(?:暗道|想道|想到|想着)[:：]?")


@dataclass(slots=True)
class ClassificationResult:
    segment_type: SegmentType
    confidence: float
    reason: str


class SegmentClassifier:
    """Classify segments with hard patterns first, then lightweight heuristics."""

    def classify(
        self,
        text: str,
        *,
        position: int = 0,
        chapter_id: str = "",
        total_segments: int | None = None,
    ) -> ClassificationResult:
        raw = text.strip()
        if not raw:
            return ClassificationResult(SegmentType.NARRATION, 0.50, "empty_fallback")

        result = self._hard_pattern(raw)
        if result:
            return result

        if position == 0 and self._matches_any(raw, CHAPTER_TITLE_PATTERNS):
            return ClassificationResult(SegmentType.CHAPTER_TITLE, 0.97, "positional_chapter_title")
        if total_segments is not None and position >= max(total_segments - 2, 0) and self._matches_any(raw, AUTHOR_NOTE_PATTERNS):
            return ClassificationResult(SegmentType.AUTHOR_NOTE, 0.95, "tail_author_note")
        if DIALOGUE_RE.search(raw) or self._is_dialogue_line(raw):
            return ClassificationResult(SegmentType.DIALOGUE, 0.88, "dialogue_marker")
        if THOUGHT_RE.search(raw):
            return ClassificationResult(SegmentType.THOUGHT, 0.86, "thought_marker")
        if self._matches_any(raw, FORUM_PATTERNS):
            return ClassificationResult(SegmentType.FORUM_POST, 0.78, "forum_marker")
        return ClassificationResult(SegmentType.NARRATION, 0.70, "fallback_narration")

    def build_packet(
        self,
        text: str,
        *,
        chapter_id: str,
        position: int,
        total_segments: int | None = None,
    ) -> SegmentPacket:
        result = self.classify(text, position=position, chapter_id=chapter_id, total_segments=total_segments)
        packet = SegmentPacket.create(
            chapter_id=chapter_id,
            position=position,
            raw_text=text,
            normalized_text=text.strip(),
            seg_type=result.segment_type,
            confidence=result.confidence,
            metadata={"classification_reason": result.reason},
        )
        packet.trace.append(
            TraceEvent(
                segment_id=packet.segment_id,
                stage="segment_classifier",
                rule_id=result.reason,
                action=result.segment_type.value,
                confidence=result.confidence,
                metadata={"raw_text": text},
            )
        )
        return packet

    def _hard_pattern(self, raw: str) -> ClassificationResult | None:
        if self._matches_any(raw, AUTHOR_NOTE_PATTERNS):
            return ClassificationResult(SegmentType.AUTHOR_NOTE, 0.98, "author_note_pattern")
        if self._matches_any(raw, ADVERTISEMENT_PATTERNS):
            return ClassificationResult(SegmentType.ADVERTISEMENT, 0.94, "advertisement_pattern")
        if self._matches_any(raw, SYSTEM_PROMPT_PATTERNS):
            return ClassificationResult(SegmentType.SYSTEM_PROMPT, 0.96, "system_prompt_pattern")
        if self._matches_any(raw, CHAPTER_TITLE_PATTERNS):
            return ClassificationResult(SegmentType.CHAPTER_TITLE, 0.96, "chapter_title_pattern")
        return None

    @staticmethod
    def _matches_any(raw: str, patterns: list[str]) -> bool:
        return any(re.search(pattern, raw, flags=re.IGNORECASE) for pattern in patterns)

    @staticmethod
    def _is_dialogue_line(raw: str) -> bool:
        return raw.startswith(("“", "\"", "「", "『")) and raw.endswith(("”", "\"", "」", "』"))

