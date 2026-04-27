#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Safe noise filtering with hard keep rules and reviewable decisions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from src.core.trace import TraceEvent
from src.pipeline.packet import SegmentPacket, SegmentType


class NoiseAction(Enum):
    KEEP = "keep"
    DROP = "drop"
    REVIEW = "review"
    METADATA = "metadata"


@dataclass(slots=True)
class NoiseDecision:
    action: NoiseAction
    confidence: float
    reason: str
    matched_patterns: list[str] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)


HARD_KEEP_PATTERNS = {
    "system_ui": [
        r"^【(?:系统|面板|任务|属性|技能|奖励|提示).*】$",
        r"^系统提示[:：].+",
    ],
    "narrative_bracket_entity": [
        r"【[^】]{2,30}】.*(?:启动|获得|激活|完成|开启|关闭|出现)",
        r".*(?:获得|激活|装备|使用)了?【[^】]{2,30}】",
    ],
    "chapter_title": [
        r"^第[零〇一二三四五六七八九十百千万两\d]+[章节回卷篇]",
    ],
}

AUTHOR_NOTE_PATTERNS = [
    r"(?:^|[（(【\[])\s*PS[:：]",
    r"作者有话说",
    r"本章完",
    r"求月票",
    r"求推荐",
    r"求收藏",
    r"新书上传",
]

AD_PATTERNS = [
    r"最新网址",
    r"手机用户请到",
    r"加入书架",
    r"点击.*收藏",
]

FORUM_PATTERNS = [
    r"楼主",
    r"顶一下",
    r"\b\d+楼\b",
]


class NoiseFilter:
    """Classify removable boilerplate without dropping protected content."""

    def decide(self, packet_or_text: SegmentPacket | str) -> NoiseDecision:
        packet = packet_or_text if isinstance(packet_or_text, SegmentPacket) else None
        text = packet.normalized_text if packet else str(packet_or_text).strip()
        segment_id = packet.segment_id if packet else ""

        keep_matches = self._matching_patterns(text, HARD_KEEP_PATTERNS)
        if keep_matches:
            return self._decision(segment_id, NoiseAction.KEEP, 1.0, "hard_whitelist", keep_matches)

        if packet and any(span.lock_level == "HARD_LOCK" for span in packet.protected_spans):
            return self._decision(segment_id, NoiseAction.KEEP, 1.0, "hard_protected_span", [])

        if packet and packet.seg_type in {SegmentType.SYSTEM_PROMPT, SegmentType.CHAPTER_TITLE}:
            return self._decision(segment_id, NoiseAction.KEEP, 0.98, f"segment_type:{packet.seg_type.value}", [])

        score = 0.0
        matched: list[str] = []
        score += self._score_patterns(text, AUTHOR_NOTE_PATTERNS, 0.65, matched)
        score += self._score_patterns(text, AD_PATTERNS, 0.70, matched)
        score += self._score_patterns(text, FORUM_PATTERNS, 0.35, matched)
        if packet and packet.seg_type == SegmentType.AUTHOR_NOTE:
            score += 0.35
        if packet and packet.seg_type == SegmentType.ADVERTISEMENT:
            score += 0.45

        if re.search(r"【[^】]{2,30}】", text):
            score -= 0.25
        if re.search(r"(说道|问道|喊道|冷声道)[:：]", text):
            score -= 0.30
        if re.search(r"(获得|激活|开启|完成|出现|进入|看见)", text):
            score -= 0.25

        if score >= 0.80:
            action = NoiseAction.DROP
            confidence = min(score, 0.99)
            reason = "weighted_noise_drop"
        elif score >= 0.45:
            action = NoiseAction.REVIEW
            confidence = min(score, 0.79)
            reason = "weighted_noise_review"
        elif matched and any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in AUTHOR_NOTE_PATTERNS):
            action = NoiseAction.METADATA
            confidence = 0.70
            reason = "author_note_metadata"
        else:
            action = NoiseAction.KEEP
            confidence = max(0.55, 1.0 - max(score, 0.0))
            reason = "below_noise_threshold"

        return self._decision(segment_id, action, confidence, reason, matched)

    @staticmethod
    def _matching_patterns(text: str, grouped_patterns: dict[str, list[str]]) -> list[str]:
        matched: list[str] = []
        for group, patterns in grouped_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    matched.append(f"{group}:{pattern}")
        return matched

    @staticmethod
    def _score_patterns(text: str, patterns: list[str], weight: float, matched: list[str]) -> float:
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                matched.append(pattern)
                score += weight
        return score

    @staticmethod
    def _decision(
        segment_id: str,
        action: NoiseAction,
        confidence: float,
        reason: str,
        matched_patterns: list[str],
    ) -> NoiseDecision:
        trace = TraceEvent(
            segment_id=segment_id,
            stage="noise_filter",
            rule_id=reason,
            action=action.value,
            confidence=confidence,
            metadata={"matched_patterns": matched_patterns},
        )
        return NoiseDecision(
            action=action,
            confidence=confidence,
            reason=reason,
            matched_patterns=matched_patterns,
            trace=[trace],
        )

