#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Coach-only grammar pattern scanner for Chinese source corpora.

This module is intentionally outside the RBMT translation path. It reads source
TXT files, detects known grammar constructions, mines reviewable unknown
patterns, and emits learning-coach reports/backlog candidates.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from src.pipeline.entity_scanner import (
    COMMON_NON_PERSON_NAME_TERMS,
    COMMON_SURNAMES,
    COMPOUND_SURNAMES,
    ENTITY_SUFFIX_FRAGMENTS,
    INVALID_NAME_CHARS,
)


SUPPORTED_ENCODINGS = ("utf-8", "utf-8-sig", "gb18030", "gbk", "big5", "utf-16")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PUNCT_RE = re.compile(r"[，。！？；、,.!?:;：\s]")


CHAPTER_HEADING_RE = re.compile(
    r"(?m)^\s*(?:"
    r"第[零〇一二三四五六七八九十百千万两\d]+[章节回卷篇].*|"
    r"卷[零〇一二三四五六七八九十百千万两\d]+.*|"
    r"番外.*|序章.*|楔子.*|"
    r"Chapter\s+\d+.*|CHAPTER\s+\d+.*"
    r")\s*$"
)

SENTENCE_END = set("。！？!?")
CLAUSE_END = set("，；;")

NOISE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("author_note", re.compile(r"(?:^|\n)\s*(?:PS|P\.S\.|作者有话说|本章完|未完待续|今天.*更新|明天.*更新)[:：]?", re.I)),
    ("advertisement", re.compile(r"(?:求收藏|求推荐|求月票|求订阅|推荐票|月票|打赏|新书上传)")),
    ("forum", re.compile(r"(?:楼主|顶一下|沙发|板凳|水帖)")),
)

HARD_KEEP_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^【(?:系统|面板|属性|任务|技能|奖励|提示|状态).{0,80}】$"),
    re.compile(r"【[^】]{2,80}】.*(?:启动|获得|激活|完成|开启|关闭|出现|绑定)"),
    re.compile(r"(?:获得|激活|启动|绑定).*【[^】]{2,80}】"),
)


@dataclass(slots=True)
class TextSource:
    path: str
    encoding: str
    chars: int
    truncated: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class CorpusChapter:
    chapter_id: str
    title: str
    text: str
    start: int
    end: int
    source_path: str = ""


@dataclass(frozen=True, slots=True)
class ProtectedSpan:
    start: int
    end: int
    text: str
    span_type: str
    priority: int

    def overlaps(self, start: int, end: int) -> bool:
        return start < self.end and self.start < end


@dataclass(frozen=True, slots=True)
class GrammarPattern:
    rule_id: str
    category: str
    name: str
    regex: str
    priority: int = 70
    description: str = ""
    examples: tuple[str, ...] = ()

    def compile(self) -> re.Pattern[str]:
        return re.compile(self.regex, flags=re.DOTALL)


@dataclass(slots=True)
class GrammarMatch:
    rule_id: str
    category: str
    name: str
    matched_text: str
    start: int
    end: int
    confidence: float
    source_sentence: str
    chapter_id: str | None = None
    paragraph_index: int | None = None
    sentence_index: int | None = None
    source_path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class UnknownPatternCandidate:
    candidate_id: str
    pattern_text: str
    pattern_type: str
    frequency: int
    chapter_count: int
    confidence: float
    examples: list[str] = field(default_factory=list)
    guessed_category: str | None = None
    suggested_regex: str | None = None
    status: str = "review"
    source_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class _CandidateHit:
    pattern_text: str
    pattern_type: str
    confidence: float
    guessed_category: str | None = None
    suggested_regex: str | None = None
    span: tuple[int, int] | None = None


@dataclass(slots=True)
class _RuleStat:
    rule_id: str
    category: str
    name: str
    count: int = 0
    chapter_ids: set[str] = field(default_factory=set)
    examples: list[dict] = field(default_factory=list)


@dataclass(slots=True)
class NameCandidate:
    candidate_id: str
    source: str
    entity_type: str
    frequency: int
    chapter_count: int
    source_count: int
    confidence: float
    examples: list[str] = field(default_factory=list)
    source_paths: list[str] = field(default_factory=list)
    status: str = "review"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class _NameStat:
    source: str
    entity_type: str
    count: int = 0
    chapter_ids: set[str] = field(default_factory=set)
    source_paths: set[str] = field(default_factory=set)
    examples: list[str] = field(default_factory=list)
    strong_contexts: int = 0


@dataclass(slots=True)
class _SourceStat:
    source_path: str
    encoding: str = ""
    chars: int = 0
    truncated: bool = False
    chapters: int = 0
    paragraphs: int = 0
    sentences: int = 0
    clauses: int = 0
    known_matches: int = 0

    def to_dict(self) -> dict:
        density = (self.known_matches / self.chars * 10000) if self.chars else 0.0
        return {
            "source_path": self.source_path,
            "encoding": self.encoding,
            "chars": self.chars,
            "truncated": self.truncated,
            "chapters": self.chapters,
            "paragraphs": self.paragraphs,
            "sentences": self.sentences,
            "clauses": self.clauses,
            "known_matches": self.known_matches,
            "known_match_density_per_10k_chars": round(density, 3),
        }


NAME_BOUNDARY_CHARS = set(
    "\uff0c\u3002\uff01\uff1f\uff1b\uff1a\u3001\u201c\u201d\u2018\u2019"
    "\uff08\uff09\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u300c\u300d"
    ",.!?;:()[]{}<>\"' \n\r\t"
)
PERSON_INTRO_PREFIXES = (
    "\u53eb\u505a",
    "\u53eb\u4f5c",
    "\u540d\u53eb",
    "\u540d\u4e3a",
    "\u59d3",
    "\u53eb",
)
PERSON_FOLLOW_CHARS = set(
    "\u8bf4\u95ee\u9053\u770b\u671b\u542c\u60f3\u7b11\u558a\u9a82\u70b9"
    "\u8d70\u5750\u7ad9\u8d77\u62ff\u6253\u627e\u6293\u653e\u6447\u95ea\u8f6c"
)
LOCATION_SUFFIXES = set(
    "\u57ce\u53bf\u9547\u6751\u5e02\u7701\u90e1\u8857\u5c71\u6cb3\u6c5f\u6e56"
    "\u6d77\u8c37\u5c9b\u5dde\u5d16\u6865\u8def\u533a\u56fd\u754c\u5cad\u5cf0"
)
LOCATION_MARKERS_BEFORE = set(
    "\u5728\u53bb\u56de\u5230\u79bb\u8d74\u5165\u51fa\u5411\u4ece\u7531\u5f80"
    "\u8fc7\u7ecf\u81f3"
)
ORGANIZATION_SUFFIXES = (
    "\u5b66\u9662",
    "\u5b66\u6821",
    "\u5927\u5b66",
    "\u4e2d\u5b66",
    "\u5c0f\u5b66",
    "\u533b\u9662",
    "\u516c\u53f8",
    "\u96c6\u56e2",
    "\u94f6\u884c",
    "\u7814\u7a76\u6240",
    "\u59d4\u5458\u4f1a",
    "\u534f\u4f1a",
    "\u5b97\u95e8",
    "\u95e8\u6d3e",
    "\u5e2e\u6d3e",
    "\u957f\u8001\u4f1a",
    "\u5546\u4f1a",
    "\u519b",
)
ORGANIZATION_SINGLE_SUFFIXES = set("\u5b97\u6d3e\u95e8\u5bab\u9601\u5e9c\u6bbf\u5e2e")
ENTITY_STOP_SUFFIXES = tuple(ENTITY_SUFFIX_FRAGMENTS)
ORGANIZATION_CANDIDATE_PATTERNS = tuple(
    re.compile(rf"[\u4e00-\u9fff]{{1,6}}{re.escape(suffix)}")
    for suffix in sorted(ORGANIZATION_SUFFIXES + ENTITY_STOP_SUFFIXES, key=len, reverse=True)
)


class CorpusNameScanner:
    """Lightweight review-only entity miner for corpus reports.

    This deliberately avoids the compiled runtime DB. It is used by Template
    Book style scans where the report needs probable names/places/orgs even
    before a project dictionary exists.
    """

    def __init__(self, *, max_examples: int = 5):
        self.max_examples = max_examples
        self.stats: dict[tuple[str, str], _NameStat] = {}

    def scan_text(self, text: str, *, chapter_id: str, source_path: str) -> None:
        compact = re.sub(r"\s+", "", text or "")
        if len(compact) < 2 or not CJK_RE.search(compact):
            return
        seen_spans: set[tuple[int, int, str]] = set()
        for source, entity_type, start, end, strong in self._iter_person_candidates(compact):
            span_key = (start, end, entity_type)
            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)
            self._record(source, entity_type, compact, start, end, chapter_id, source_path, strong)
        for source, entity_type, start, end, strong in self._iter_location_candidates(compact):
            span_key = (start, end, entity_type)
            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)
            self._record(source, entity_type, compact, start, end, chapter_id, source_path, strong)
        for source, entity_type, start, end, strong in self._iter_organization_candidates(compact):
            span_key = (start, end, entity_type)
            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)
            self._record(source, entity_type, compact, start, end, chapter_id, source_path, strong)

    def finalize(self, *, min_count: int = 2, limit: int = 200) -> list[NameCandidate]:
        candidates: list[NameCandidate] = []
        for (source, entity_type), stat in self.stats.items():
            if stat.count < min_count and stat.strong_contexts == 0:
                continue
            confidence = self._confidence(stat)
            if confidence < 0.55:
                continue
            candidates.append(
                NameCandidate(
                    candidate_id=stable_id(f"{entity_type}:{source}", prefix="entity"),
                    source=source,
                    entity_type=entity_type,
                    frequency=stat.count,
                    chapter_count=len(stat.chapter_ids),
                    source_count=len(stat.source_paths),
                    confidence=confidence,
                    examples=stat.examples,
                    source_paths=sorted(stat.source_paths),
                )
            )
        return sorted(
            candidates,
            key=lambda item: (-item.confidence, -item.frequency, -item.chapter_count, item.entity_type, item.source),
        )[:limit]

    def _iter_person_candidates(self, text: str) -> Iterable[tuple[str, str, int, int, bool]]:
        for idx in range(len(text)):
            surname_len = self._surname_prefix_length(text, idx)
            if surname_len == 0:
                continue
            if self._is_bad_start(text, idx):
                continue

            lengths = (4, 3) if surname_len == 2 else (3, 2)
            best: tuple[str, int, int, bool] | None = None
            for length in lengths:
                end = idx + length
                candidate = text[idx:end]
                if len(candidate) != length:
                    continue
                if not self._looks_like_person_name(candidate, surname_len):
                    continue
                next_char = text[end:end + 1]
                end_score = self._score_person_end(next_char)
                if end_score == 0:
                    continue
                start_score = self._score_name_start(text, idx)
                if start_score == 0 and end_score < 2:
                    continue
                strong = start_score >= 2 or end_score >= 2
                score = start_score + end_score + length
                if best is None or score > best[1] or (score == best[1] and length < len(best[0])):
                    best = (candidate, score, end, strong)
            if best:
                candidate, _, end, strong = best
                yield candidate, "person", idx, end, strong

    def _iter_location_candidates(self, text: str) -> Iterable[tuple[str, str, int, int, bool]]:
        for idx, ch in enumerate(text):
            if ch not in LOCATION_SUFFIXES and ch not in ORGANIZATION_SINGLE_SUFFIXES:
                continue
            entity_type = "organization" if ch in ORGANIZATION_SINGLE_SUFFIXES else "location"
            best: tuple[str, int, bool] | None = None
            for prefix_len in (4, 3, 2, 1):
                start = idx - prefix_len
                if start < 0:
                    continue
                candidate = text[start:idx + 1]
                if not self._looks_like_named_place_or_group(candidate):
                    continue
                before = text[start - 1:start] if start > 0 else ""
                strong = before in LOCATION_MARKERS_BEFORE
                boundary = not before or before in NAME_BOUNDARY_CHARS or strong
                if not boundary:
                    continue
                score = prefix_len + (2 if strong else 0)
                if best is None or score > best[1]:
                    best = (candidate, score, strong)
            if best:
                candidate, _, strong = best
                yield candidate, entity_type, idx + 1 - len(candidate), idx + 1, strong

    def _iter_organization_candidates(self, text: str) -> Iterable[tuple[str, str, int, int, bool]]:
        for pattern in ORGANIZATION_CANDIDATE_PATTERNS:
            for match in pattern.finditer(text):
                candidate = match.group(0)
                if len(candidate) > 10 or not self._looks_like_named_place_or_group(candidate):
                    continue
                before = text[match.start() - 1:match.start()] if match.start() > 0 else ""
                strong = before in LOCATION_MARKERS_BEFORE or before in NAME_BOUNDARY_CHARS or not before
                yield candidate, "organization", match.start(), match.end(), strong

    def _record(
        self,
        source: str,
        entity_type: str,
        text: str,
        start: int,
        end: int,
        chapter_id: str,
        source_path: str,
        strong: bool,
    ) -> None:
        key = (source, entity_type)
        stat = self.stats.get(key)
        if stat is None:
            stat = _NameStat(source=source, entity_type=entity_type)
            self.stats[key] = stat
        stat.count += 1
        stat.chapter_ids.add(corpus_chapter_key(source_path, chapter_id))
        stat.source_paths.add(source_path)
        if strong:
            stat.strong_contexts += 1
        if len(stat.examples) < self.max_examples:
            stat.examples.append(self._context(text, start, end))

    @staticmethod
    def _context(text: str, start: int, end: int, radius: int = 24) -> str:
        left = max(0, start - radius)
        right = min(len(text), end + radius)
        return text[left:right]

    @staticmethod
    def _surname_prefix_length(text: str, idx: int) -> int:
        if idx + 1 < len(text) and text[idx:idx + 2] in COMPOUND_SURNAMES:
            return 2
        return 1 if text[idx:idx + 1] in COMMON_SURNAMES else 0

    @staticmethod
    def _looks_like_person_name(candidate: str, surname_len: int) -> bool:
        if len(candidate) <= surname_len or len(candidate) > surname_len + 2:
            return False
        if candidate in COMMON_NON_PERSON_NAME_TERMS:
            return False
        if any(candidate.endswith(suffix) for suffix in ("\u9053", "\u6c14", "\u754c", "\u6cd5", "\u529b")):
            return False
        if not all("\u4e00" <= ch <= "\u9fff" for ch in candidate):
            return False
        given_name = candidate[surname_len:]
        return not any(ch in INVALID_NAME_CHARS for ch in given_name)

    @staticmethod
    def _looks_like_named_place_or_group(candidate: str) -> bool:
        if len(candidate) < 2 or len(candidate) > 10:
            return False
        if candidate in COMMON_NON_PERSON_NAME_TERMS:
            return False
        if not all("\u4e00" <= ch <= "\u9fff" for ch in candidate):
            return False
        stem = candidate[:-1]
        return bool(stem) and not any(ch in INVALID_NAME_CHARS for ch in stem)

    @staticmethod
    def _score_name_start(text: str, idx: int) -> int:
        if idx == 0:
            return 1
        if any(text[max(0, idx - len(prefix)):idx] == prefix for prefix in PERSON_INTRO_PREFIXES):
            return 2
        if text[idx - 1:idx] in NAME_BOUNDARY_CHARS:
            return 1
        return 0

    @staticmethod
    def _score_person_end(next_char: str) -> int:
        if not next_char:
            return 1
        if next_char in PERSON_FOLLOW_CHARS:
            return 2
        if next_char in NAME_BOUNDARY_CHARS:
            return 1
        return 0

    @staticmethod
    def _is_bad_start(text: str, idx: int) -> bool:
        if idx > 0 and text[idx - 1:idx + 1] in {"\u5bf9\u4e8e", "\u5728\u4e8e"}:
            return True
        return text[idx:idx + 1] in {"\u90a3", "\u8fd9", "\u67d0", "\u8be5", "\u6b64", "\u672c"}

    @staticmethod
    def _confidence(stat: _NameStat) -> float:
        base = {"person": 0.58, "location": 0.56, "organization": 0.57}.get(stat.entity_type, 0.52)
        base += min(math.log10(stat.count + 1) * 0.16, 0.24)
        base += min(len(stat.chapter_ids) * 0.015, 0.12)
        base += min(len(stat.source_paths) * 0.02, 0.10)
        if stat.strong_contexts:
            base += min(stat.strong_contexts * 0.025, 0.10)
        return round(min(base, 0.96), 3)


def summarize_name_candidates(candidates: list[NameCandidate]) -> dict:
    by_type: Counter[str] = Counter()
    mentions_by_type: Counter[str] = Counter()
    total_mentions = 0
    for candidate in candidates:
        by_type[candidate.entity_type] += 1
        mentions_by_type[candidate.entity_type] += candidate.frequency
        total_mentions += candidate.frequency
    return {
        "total_candidates": len(candidates),
        "total_mentions": total_mentions,
        "high_confidence_candidates": sum(1 for item in candidates if item.confidence >= 0.75),
        "by_entity_type": dict(sorted(by_type.items())),
        "mentions_by_entity_type": dict(sorted(mentions_by_type.items())),
        "top_candidates": [
            {
                "source": item.source,
                "entity_type": item.entity_type,
                "frequency": item.frequency,
                "chapter_count": item.chapter_count,
                "confidence": item.confidence,
            }
            for item in candidates[:20]
        ],
    }


KNOWN_GRAMMAR_PATTERNS: tuple[GrammarPattern, ...] = (
    GrammarPattern("condition_ruguo_jiu", "condition", "如果...就...", r"如果(?P<a>[^。！？；]{1,120}?)(?:，)?[^。！？；]{0,24}?(?:就|便|则)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("condition_zhiyao_jiu", "condition", "只要...就...", r"只要(?P<a>[^。！？；]{1,120}?)(?:，)?[^。！？；]{0,24}?(?:就|便)(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("condition_yidan_jiu", "condition", "一旦...就/便...", r"一旦(?P<a>[^。！？；]{1,120}?)(?:，)?[^。！？；]{0,24}?(?:就|便|则)(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("condition_chufei_fouze", "condition", "除非...否则...", r"除非(?P<a>[^。！？；]{1,120}?)(?:，)?否则(?P<b>[^。！？；]{1,120})", 86),
    GrammarPattern("concession_suiran_danshi", "concession", "虽然...但是/但/却...", r"(?:虽然|虽说|尽管)(?P<a>[^。！？；]{1,120}?)(?:，)?(?:但是|但|却|仍然|还是)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("concession_jibian_ye", "concession", "即便/即使...也...", r"(?:即便|即使)(?P<a>[^。！？；]{1,120}?)(?:，)?(?:也|都|仍然|还是)(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("concession_napa_ye", "concession", "哪怕...也...", r"哪怕(?P<a>[^。！？；]{1,120}?)(?:，)?(?:也|都|仍然|还是)(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("concession_jiusuan_ye", "concession", "就算...也...", r"就算(?P<a>[^。！？；]{1,120}?)(?:，)?(?:也|都|仍然|还是)(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("regardless_wulun_dou", "regardless", "无论/不管...都/也...", r"(?:无论|不管)(?P<a>[^。！？；]{1,120}?)(?:，)?(?:都|也)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("contrast_bushi_ershi", "contrast_correction", "不是...而是...", r"不是(?P<a>[^。！？；]{1,120}?)而是(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("additive_budan_erqie", "additive", "不但/不仅...而且/还...", r"(?:不但|不仅)(?P<a>[^。！？；]{1,120}?)(?:而且|还)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("preference_yuqi_buru", "preference", "与其...不如...", r"与其(?P<a>[^。！？；]{1,120}?)(?:，)?不如(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("preference_ningke_yebu", "preference", "宁可/宁愿...也不/也要...", r"(?:宁可|宁愿)(?P<a>[^。！？；]{1,120}?)(?:，)?(?:也不|也要)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("parallel_ji_you", "parallel_attribute", "既...又...", r"既(?P<a>[^。！？；，]{1,80}?)(?:，)?又(?P<b>[^。！？；]{1,100})", 82),
    GrammarPattern("progressive_yue_yue", "progressive_comparison", "越...越...", r"越(?P<a>[^。！？；，]{1,60}?)越(?P<b>[^。！？；]{1,100})", 84),
    GrammarPattern("concession_zaizenme_ye", "concession_limit", "再怎么...也/都...", r"再怎么(?P<a>[^。！？；]{1,100}?)(?:，)?(?:也|都)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("reason_zhisuoyi_shiyinwei", "cause_reason", "之所以...是因为...", r"之所以(?P<a>[^。！？；]{1,120}?)(?:，)?是因为(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("condition_zhiyou_cai", "condition", "只有...才...", r"只有(?P<a>[^。！？；]{1,120}?)(?:，)?才(?P<b>[^。！？；]{1,120})", 84),
    GrammarPattern("hypothesis_ruoshi", "condition", "倘若/假如/若是...", r"(?:倘若|假如|若是)(?P<a>[^。！？；]{1,120})", 78),
    GrammarPattern("cause_youyu_yinci", "cause_reason", "由于...因此/因而/所以...", r"由于(?P<a>[^。！？；]{1,120}?)(?:，)?(?:因此|因而|所以)(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("precaution_miande", "precaution", "免得/以免...", r"(?:免得|以免)(?P<a>[^，。！？；]{1,80})", 78),
    GrammarPattern("parallel_yibian_yibian", "parallel_action", "一边...一边...", r"一边(?P<a>[^。！？；，]{1,50}?)一边(?P<b>[^。！？；]{1,80})", 84),
    GrammarPattern("parallel_yimian_yimian", "parallel_action", "一面...一面...", r"一面(?P<a>[^。！？；，]{1,50}?)一面(?P<b>[^。！？；]{1,80})", 82),
    GrammarPattern("passive_wei_suo", "passive", "为...所...", r"为(?P<a>[^，。！？；]{1,40}?)所(?P<b>[^，。！？；]{1,40})", 86),
    GrammarPattern("passive_bei_suo", "passive", "被...所...", r"被(?P<a>[^，。！？；]{1,40}?)所(?P<b>[^，。！？；]{1,40})", 86),
    GrammarPattern("passive_bei", "passive", "被 passive", r"被(?P<a>[^，。！？；]{1,40})", 74),
    GrammarPattern("ba_construction", "disposal", "把 construction", r"把(?P<a>[^，。！？；]{1,60})", 76),
    GrammarPattern("jiang_construction", "disposal", "将 construction", r"将(?P<a>[^，。！？；]{1,60})", 72),
    GrammarPattern("viewpoint_zuowei", "viewpoint", "作为...", r"作为(?P<a>[^，。！？；]{1,60})(?:而言|来说|来讲)?", 80),
    GrammarPattern("viewpoint_dui_laishuo", "viewpoint", "对...来说/而言", r"对(?P<a>[^，。！？；]{1,60})(?:来说|而言|来讲)", 80),
    GrammarPattern("definition_suowei", "definition", "所谓...", r"所谓(?:的)?(?P<a>[^，。！？；]{1,60})", 78),
    GrammarPattern("minimizing_bale", "minimizing", "X罢了", r"[^，。！？；]{1,60}罢了", 76),
    GrammarPattern("minimizing_eryi", "minimizing", "X而已", r"[^，。！？；]{1,60}而已", 76),
    GrammarPattern("evidential_jushuo", "evidential", "据说/据悉/据了解", r"(?:据说|据悉|据了解|据报道)", 72),
    GrammarPattern("comparison_yu_x_xiangbi", "comparison", "与/和X相比", r"(?:与|和)(?P<a>[^，。！？；]{1,60})相(?:比|比较)", 78),
    GrammarPattern("comparison_biqi", "comparison", "比起X来", r"比起(?P<a>[^，。！？；]{1,60})来", 78),
    GrammarPattern("marker_shenzhi", "emphasis", "甚至/乃至...", r"(?:甚至|乃至)(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_faner", "contrast", "反而...", r"反而(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_hekuang", "addition", "何况/更何况...", r"(?:更何况|何况)(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_zhiyu", "topic_shift", "至于...", r"至于(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_guanyu_duiyu", "topic_scope", "关于/对于...", r"(?:关于|对于)(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_bingfei_weibi", "negation_modal", "并非/未必...", r"(?:并非|未必)(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_fouze", "condition", "否则...", r"否则(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("marker_zhibuguo", "minimizing", "只不过/不过是...", r"(?:只不过|不过是)(?P<a>[^，。！？；]{1,80})", 72),
    GrammarPattern("precaution_yifang", "precaution", "以防...", r"以防(?P<a>[^，。！？；]{1,60})", 76),
    GrammarPattern("emphatic_jiulian_ye", "emphatic_even", "就连X也/都Y", r"就连(?P<a>[^，。！？；]{1,60})(?:也|都)(?P<b>[^，。！？；]{1,80})", 82),
    GrammarPattern("enumeration_yilai_erlai", "enumeration", "一来...二来...", r"一来(?P<a>[^。！？；]{1,120}?)二来(?P<b>[^。！？；]{1,120})", 82),
    GrammarPattern("necessity_fei_buke", "necessity", "非X不可", r"非(?P<a>[^，。！？；]{1,60})不可", 82),
)

UNKNOWN_MARKER_SEED: tuple[str, ...] = (
    "偏偏", "索性", "竟是", "竟然", "倒也", "反倒", "终究", "毕竟",
    "说到底", "换句话说", "与其", "不如", "宁可", "也不",
    "不是", "而是", "既", "又", "越", "再怎么", "也",
    "莫非", "难不成", "何况", "更何况", "只不过", "不过是",
    "反而", "乃至", "甚至", "并非", "未必", "何尝", "倘若",
    "否则", "免得", "以免", "至于", "关于", "对于", "由于",
)

PAIRED_MARKERS: tuple[tuple[str, str, str], ...] = (
    ("与其", "不如", "preference"),
    ("宁可", "也不", "preference"),
    ("宁愿", "也不", "preference"),
    ("不是", "而是", "contrast_correction"),
    ("并非", "而是", "contrast_correction"),
    ("既", "又", "parallel_attribute"),
    ("越", "越", "progressive_comparison"),
    ("再怎么", "也", "concession_limit"),
    ("无论", "都", "regardless"),
    ("不管", "都", "regardless"),
    ("哪怕", "也", "concession"),
    ("即使", "也", "concession"),
    ("即便", "也", "concession"),
    ("不但", "而且", "additive"),
    ("不仅", "还", "additive"),
)

SINGLE_MARKER_CATEGORY: dict[str, str] = {
    "偏偏": "counter_expectation",
    "索性": "decision",
    "竟然": "surprise",
    "反而": "contrast",
    "毕竟": "reasoning",
    "终究": "conclusion",
    "说到底": "summary",
    "换句话说": "definition",
    "何况": "addition",
    "更何况": "addition",
    "只不过": "minimizing",
    "不过是": "minimizing",
    "莫非": "rhetorical_question",
    "难不成": "rhetorical_question",
    "否则": "condition",
    "以免": "precaution",
    "免得": "precaution",
}

GRAMMAR_LIKE_NGRAM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:而已|罢了|来说|而言|来讲|之中|之下|之上|之内|之前|之后)$"),
    re.compile(r"^(?:无论|不管|即使|即便|哪怕|虽然|如果|只要|一旦|除非|否则|以免)"),
    re.compile(r"(?:并非|未必|莫非|难道|何况|况且|反而|偏偏|索性|竟然|乃至|甚至)"),
)

WEAK_SINGLE_MARKERS = {"也", "又", "越", "既", "不是", "而是", "也不", "不如"}


def stable_id(value: str, prefix: str = "grammar") -> str:
    digest = hashlib.sha1(value.encode("utf-8", errors="ignore")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def corpus_chapter_key(source_path: str, chapter_id: str) -> str:
    return f"{source_path}::{chapter_id}" if source_path else chapter_id


def read_text_file(path: str | Path, *, max_bytes: int | None = None) -> tuple[str, TextSource]:
    source_path = Path(path)
    file_size = source_path.stat().st_size
    truncated = False
    if max_bytes and max_bytes > 0 and file_size > max_bytes:
        with source_path.open("rb") as handle:
            full_content = handle.read(max_bytes)
        truncated = True
    else:
        full_content = source_path.read_bytes()

    encoding = "utf-8-replace"
    for candidate_encoding in SUPPORTED_ENCODINGS:
        try:
            full_content.decode(candidate_encoding)
            encoding = candidate_encoding
            break
        except UnicodeDecodeError:
            continue

    content = full_content
    errors = "ignore" if truncated else "strict"
    try:
        text = content.decode(encoding, errors=errors)
    except UnicodeDecodeError:
        text = content.decode("utf-8", errors="replace")
        encoding = "utf-8-replace"
    return text, TextSource(str(source_path), encoding, len(text), truncated)


def normalize_text(text: str) -> str:
    replacements = {
        "\ufeff": "",
        "\u3000": " ",
        "\xa0": " ",
        "\r\n": "\n",
        "\r": "\n",
        "﹐": "，",
        "﹑": "、",
        "﹔": "；",
        "﹕": "：",
        "﹗": "！",
        "﹖": "？",
    }
    normalized = str(text or "")
    for src, dst in replacements.items():
        normalized = normalized.replace(src, dst)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def split_chapters(text: str, *, source_path: str = "") -> list[CorpusChapter]:
    matches = list(CHAPTER_HEADING_RE.finditer(text))
    if not matches:
        return [
            CorpusChapter(
                chapter_id="chapter-001",
                title="Full Text",
                text=text.strip(),
                start=0,
                end=len(text),
                source_path=source_path,
            )
        ]

    chapters: list[CorpusChapter] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        lines = block.splitlines()
        title = lines[0].strip() if lines else f"Chapter {index + 1}"
        body = "\n".join(lines[1:]).strip()
        chapters.append(
            CorpusChapter(
                chapter_id=f"chapter-{index + 1:03d}",
                title=title,
                text=body,
                start=start,
                end=end,
                source_path=source_path,
            )
        )
    return chapters


def split_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    for block in re.split(r"\n{1,}", text):
        stripped = block.strip()
        if stripped:
            paragraphs.append(stripped)
    return paragraphs


def classify_segment(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "empty"
    if any(pattern.search(stripped) for pattern in HARD_KEEP_PATTERNS):
        return "system_prompt"
    if CHAPTER_HEADING_RE.match(stripped):
        return "chapter_title"
    for segment_type, pattern in NOISE_PATTERNS:
        if pattern.search(stripped):
            return segment_type
    if stripped.startswith(("“", "「", "『", "\"", "'")):
        return "dialogue"
    if stripped.startswith("【") and stripped.endswith("】"):
        return "system_prompt"
    return "narration"


def is_noise_segment(text: str, segment_type: str) -> bool:
    if segment_type in {"empty", "chapter_title"}:
        return True
    if any(pattern.search(text.strip()) for pattern in HARD_KEEP_PATTERNS):
        return False
    return segment_type in {"author_note", "advertisement", "forum"}


def detect_protected_spans(text: str) -> list[ProtectedSpan]:
    patterns: tuple[tuple[str, str, int], ...] = (
        (r"【[^】]{1,120}】", "system_panel", 100),
        (r"《[^》]{1,120}》", "book_title", 85),
        (r"“[^”]{1,300}”", "quote", 80),
        (r"‘[^’]{1,300}’", "quote", 80),
        (r"「[^」]{1,300}」", "quote", 80),
        (r"『[^』]{1,300}』", "quote", 80),
        (r"\d{1,2}[:：]\d{2}(?::\d{2})?", "time", 75),
        (r"[A-Z]{1,4}[+-]?级", "rank", 70),
        (r"v\d+(?:\.\d+)+", "version", 70),
        (r"\d+(?:\.\d+)?(?:万|亿|千|百|米|公里|岁|年|天|小时|分钟|秒)", "number_unit", 65),
    )
    claims: list[ProtectedSpan] = []
    for pattern, span_type, priority in patterns:
        for match in re.finditer(pattern, text):
            claims.append(
                ProtectedSpan(
                    start=match.start(),
                    end=match.end(),
                    text=match.group(0),
                    span_type=span_type,
                    priority=priority,
                )
            )
    return resolve_protected_spans(claims)


def resolve_protected_spans(spans: Iterable[ProtectedSpan]) -> list[ProtectedSpan]:
    chosen: list[ProtectedSpan] = []
    for span in sorted(spans, key=lambda item: (-item.priority, -(item.end - item.start), item.start)):
        if any(span.overlaps(existing.start, existing.end) for existing in chosen):
            continue
        chosen.append(span)
    return sorted(chosen, key=lambda item: (item.start, item.end))


def overlaps_protected(start: int, end: int, spans: list[ProtectedSpan]) -> bool:
    return any(span.overlaps(start, end) for span in spans)


def split_sentences(text: str, protected_spans: list[ProtectedSpan] | None = None) -> list[str]:
    protected = protected_spans or detect_protected_spans(text)
    sentences: list[str] = []
    start = 0
    quote_depth = 0
    for index, ch in enumerate(text):
        if overlaps_protected(index, index + 1, protected):
            continue
        if ch in "“「『":
            quote_depth += 1
        elif ch in "”」』":
            quote_depth = max(0, quote_depth - 1)
        if quote_depth:
            continue
        if ch in SENTENCE_END:
            chunk = text[start:index + 1].strip()
            if chunk:
                sentences.append(chunk)
            start = index + 1
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def split_clauses(text: str, protected_spans: list[ProtectedSpan] | None = None) -> list[str]:
    protected = protected_spans or detect_protected_spans(text)
    clauses: list[str] = []
    start = 0
    quote_depth = 0
    for index, ch in enumerate(text):
        if overlaps_protected(index, index + 1, protected):
            continue
        if ch in "“「『":
            quote_depth += 1
        elif ch in "”」』":
            quote_depth = max(0, quote_depth - 1)
        if quote_depth:
            continue
        if ch in CLAUSE_END or ch in SENTENCE_END:
            chunk = text[start:index + 1].strip()
            if chunk:
                clauses.append(chunk)
            start = index + 1
    tail = text[start:].strip()
    if tail:
        clauses.append(tail)
    return clauses or [text.strip()] if text.strip() else []


class GrammarPatternScanner:
    """Scan known grammar rules and resolve overlapping matches."""

    def __init__(self, patterns: Iterable[GrammarPattern] | None = None):
        self.patterns = sorted(tuple(patterns or KNOWN_GRAMMAR_PATTERNS), key=lambda item: item.priority, reverse=True)
        self._compiled = [(pattern, pattern.compile()) for pattern in self.patterns]

    def scan(
        self,
        text: str,
        protected_spans: list[ProtectedSpan] | None = None,
        *,
        source_sentence: str | None = None,
        chapter_id: str | None = None,
        paragraph_index: int | None = None,
        sentence_index: int | None = None,
        source_path: str = "",
    ) -> list[GrammarMatch]:
        spans = protected_spans or detect_protected_spans(text)
        matches: list[GrammarMatch] = []
        for pattern, compiled in self._compiled:
            for match in compiled.finditer(text):
                if overlaps_protected(match.start(), match.end(), spans):
                    continue
                matched_text = match.group(0).strip()
                if not matched_text or not CJK_RE.search(matched_text):
                    continue
                matches.append(
                    GrammarMatch(
                        rule_id=pattern.rule_id,
                        category=pattern.category,
                        name=pattern.name,
                        matched_text=matched_text,
                        start=match.start(),
                        end=match.end(),
                        confidence=self._confidence(pattern, matched_text),
                        source_sentence=source_sentence or text,
                        chapter_id=chapter_id,
                        paragraph_index=paragraph_index,
                        sentence_index=sentence_index,
                        source_path=source_path,
                    )
                )
        return self.resolve_overlaps(matches)

    @staticmethod
    def resolve_overlaps(matches: list[GrammarMatch]) -> list[GrammarMatch]:
        chosen: list[GrammarMatch] = []
        ranked = sorted(matches, key=lambda item: (-item.confidence, -(item.end - item.start), item.start))
        for match in ranked:
            if any(match.start < existing.end and existing.start < match.end for existing in chosen):
                continue
            chosen.append(match)
        return sorted(chosen, key=lambda item: (item.start, item.end))

    @staticmethod
    def _confidence(pattern: GrammarPattern, matched_text: str) -> float:
        base = 0.62 + min(pattern.priority / 200, 0.25)
        if "..." in pattern.name:
            base += 0.05
        if len(matched_text) >= 4:
            base += 0.03
        return min(base, 0.96)


class UnknownGrammarPatternMiner:
    """Mine reviewable unknown grammar candidates from residual source text."""

    def __init__(self):
        self.counter: Counter[tuple[str, str]] = Counter()
        self.examples: dict[tuple[str, str], list[str]] = defaultdict(list)
        self.chapter_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
        self.source_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
        self.category_guess: dict[tuple[str, str], str | None] = {}
        self.regex_guess: dict[tuple[str, str], str | None] = {}
        self.base_confidence: dict[tuple[str, str], float] = {}

    def scan_sentence(
        self,
        sentence: str,
        *,
        known_matches: list[GrammarMatch],
        chapter_id: str,
        source_path: str,
    ) -> list[_CandidateHit]:
        hits: list[_CandidateHit] = []
        hits.extend(self._mine_paired_markers(sentence, known_matches))
        hits.extend(self._mine_marker_sequence_frames(sentence, known_matches))

        if not known_matches:
            hits.extend(self._mine_clause_anomaly(sentence))
            hits.extend(self._mine_seed_markers(sentence))
            hits.extend(self._mine_high_value_ngrams(sentence))

        for hit in hits:
            self._record(hit, sentence, chapter_id=chapter_id, source_path=source_path)
        return hits

    def scan_clause(
        self,
        clause: str,
        *,
        known_matches: list[GrammarMatch],
        chapter_id: str,
        source_sentence: str,
        source_path: str,
    ) -> list[_CandidateHit]:
        local_known = [
            match
            for match in known_matches
            if match.matched_text and match.matched_text in clause
        ]
        if local_known:
            return []
        hits = self._mine_clause_anomaly(clause)
        if len(clause) <= 80:
            hits.extend(self._mine_seed_markers(clause))
            hits.extend(self._mine_high_value_ngrams(clause))
        for hit in hits:
            self._record(hit, source_sentence, chapter_id=chapter_id, source_path=source_path)
        return hits

    def finalize(self, *, min_count: int = 5, limit: int = 200) -> list[UnknownPatternCandidate]:
        candidates: list[UnknownPatternCandidate] = []
        for key, count in self.counter.items():
            if count < min_count:
                continue
            pattern_text, pattern_type = key
            chapter_count = len(self.chapter_sets[key])
            confidence = self._score(count, chapter_count, self.base_confidence.get(key, 0.5), pattern_type)
            candidates.append(
                UnknownPatternCandidate(
                    candidate_id=stable_id(f"{pattern_type}:{pattern_text}", prefix="unknown"),
                    pattern_text=pattern_text,
                    pattern_type=pattern_type,
                    frequency=count,
                    chapter_count=chapter_count,
                    confidence=confidence,
                    examples=self.examples[key][:10],
                    guessed_category=self.category_guess.get(key) or guess_category_from_pattern(pattern_text),
                    suggested_regex=self.regex_guess.get(key) or suggest_regex_from_pattern_text(pattern_text),
                    status="review",
                    source_paths=sorted(self.source_sets[key])[:10],
                )
            )
        return sorted(candidates, key=lambda item: (-item.confidence, -item.frequency, item.pattern_text))[:limit]

    def _record(self, hit: _CandidateHit, example: str, *, chapter_id: str, source_path: str) -> None:
        key = (hit.pattern_text, hit.pattern_type)
        self.counter[key] += 1
        self.chapter_sets[key].add(corpus_chapter_key(source_path, chapter_id))
        if source_path:
            self.source_sets[key].add(source_path)
        if hit.guessed_category is not None:
            self.category_guess[key] = hit.guessed_category
        if hit.suggested_regex is not None:
            self.regex_guess[key] = hit.suggested_regex
        self.base_confidence[key] = max(hit.confidence, self.base_confidence.get(key, 0.0))
        if len(self.examples[key]) < 10 and example not in self.examples[key]:
            self.examples[key].append(example)

    @staticmethod
    def _mine_paired_markers(sentence: str, known_matches: list[GrammarMatch]) -> list[_CandidateHit]:
        hits: list[_CandidateHit] = []
        for left, right, category in PAIRED_MARKERS:
            start = sentence.find(left)
            if start < 0:
                continue
            search_from = start + len(left)
            end_marker = sentence.find(right, search_from)
            if end_marker < 0:
                continue
            end = end_marker + len(right)
            if end_marker - search_from > 120:
                continue
            if _overlaps_known(start, end, known_matches):
                continue
            pattern_text = f"{left}...{right}"
            hits.append(
                _CandidateHit(
                    pattern_text=pattern_text,
                    pattern_type="paired_marker",
                    confidence=0.76,
                    guessed_category=category,
                    suggested_regex=suggest_regex_from_pattern_text(pattern_text),
                    span=(start, end),
                )
            )
        return hits

    @staticmethod
    def _mine_marker_sequence_frames(sentence: str, known_matches: list[GrammarMatch]) -> list[_CandidateHit]:
        positions: list[tuple[int, str]] = []
        for marker in sorted(set(UNKNOWN_MARKER_SEED), key=len, reverse=True):
            for match in re.finditer(re.escape(marker), sentence):
                positions.append((match.start(), marker))
        positions = sorted(positions)
        paired_lookup = {(left, right) for left, right, _category in PAIRED_MARKERS}
        hits: list[_CandidateHit] = []
        for index, (left_pos, left) in enumerate(positions):
            for right_pos, right in positions[index + 1:index + 5]:
                if (left, right) in paired_lookup:
                    continue
                if left in WEAK_SINGLE_MARKERS or right in WEAK_SINGLE_MARKERS:
                    continue
                if left == right and left != "越":
                    continue
                if right_pos <= left_pos or right_pos - left_pos > 80:
                    continue
                end = right_pos + len(right)
                if _overlaps_known(left_pos, end, known_matches):
                    continue
                pattern_text = f"{left}...{right}"
                hits.append(
                    _CandidateHit(
                        pattern_text=pattern_text,
                        pattern_type="frame_template",
                        confidence=0.62,
                        guessed_category=guess_category_from_pattern(pattern_text),
                        suggested_regex=suggest_regex_from_pattern_text(pattern_text),
                        span=(left_pos, end),
                    )
                )
        return hits

    @staticmethod
    def _mine_clause_anomaly(clause: str) -> list[_CandidateHit]:
        markers = [marker for marker in UNKNOWN_MARKER_SEED if marker in clause]
        strong_markers = [marker for marker in markers if marker not in WEAK_SINGLE_MARKERS]
        if len(clause) < 18 or not markers:
            return []
        if not strong_markers:
            return []
        key_markers = sorted(set(strong_markers), key=lambda item: clause.find(item))[:4]
        return [
            _CandidateHit(
                pattern_text=" / ".join(key_markers),
                pattern_type="clause_anomaly",
                confidence=0.52 + min(len(key_markers) * 0.04, 0.18),
                guessed_category=None,
                suggested_regex=None,
                span=None,
            )
        ]

    @staticmethod
    def _mine_seed_markers(text: str) -> list[_CandidateHit]:
        hits: list[_CandidateHit] = []
        for marker in sorted(set(UNKNOWN_MARKER_SEED), key=len, reverse=True):
            if marker not in text:
                continue
            if marker in WEAK_SINGLE_MARKERS:
                continue
            hits.append(
                _CandidateHit(
                    pattern_text=marker,
                    pattern_type="marker",
                    confidence=0.56,
                    guessed_category=SINGLE_MARKER_CATEGORY.get(marker),
                    suggested_regex=re.escape(marker),
                )
            )
        return hits

    @staticmethod
    def _mine_high_value_ngrams(text: str) -> list[_CandidateHit]:
        hits: list[_CandidateHit] = []
        seen: set[str] = set()
        cleaned = re.sub(r"[^\u4e00-\u9fff]", "", text)
        if len(cleaned) < 4:
            return []
        for n in range(2, 7):
            for index in range(0, len(cleaned) - n + 1):
                gram = cleaned[index:index + n]
                if gram in seen or not should_keep_ngram(gram):
                    continue
                if not looks_like_grammar_marker(gram):
                    continue
                seen.add(gram)
                hits.append(
                    _CandidateHit(
                        pattern_text=gram,
                        pattern_type="ngram",
                        confidence=0.48,
                        guessed_category=guess_category_from_pattern(gram),
                        suggested_regex=re.escape(gram),
                    )
                )
        return hits[:40]

    @staticmethod
    def _score(frequency: int, chapter_count: int, base: float, pattern_type: str) -> float:
        score = base
        score += min(math.log10(max(frequency, 1)) * 0.14, 0.25)
        score += min(chapter_count / 30, 0.16)
        if pattern_type in {"paired_marker", "frame_template"}:
            score += 0.06
        if pattern_type == "ngram":
            score -= 0.04
        return round(min(max(score, 0.35), 0.96), 3)


def should_keep_ngram(gram: str) -> bool:
    if len(gram) < 2:
        return False
    if PUNCT_RE.search(gram):
        return False
    if re.fullmatch(r"\d+", gram):
        return False
    if not CJK_RE.search(gram):
        return False
    if len(set(gram)) == 1:
        return False
    return True


def looks_like_grammar_marker(gram: str) -> bool:
    if gram in WEAK_SINGLE_MARKERS:
        return False
    if gram in UNKNOWN_MARKER_SEED or gram in SINGLE_MARKER_CATEGORY:
        return True
    return any(pattern.search(gram) for pattern in GRAMMAR_LIKE_NGRAM_PATTERNS)


def guess_category_from_pattern(pattern_text: str) -> str | None:
    for left, right, category in PAIRED_MARKERS:
        if pattern_text == f"{left}...{right}" or (left in pattern_text and right in pattern_text):
            return category
    for marker, category in SINGLE_MARKER_CATEGORY.items():
        if marker in pattern_text:
            return category
    if "不如" in pattern_text or "宁可" in pattern_text:
        return "preference"
    if "而是" in pattern_text or "反而" in pattern_text:
        return "contrast"
    if "也" in pattern_text and ("哪怕" in pattern_text or "即使" in pattern_text or "再怎么" in pattern_text):
        return "concession"
    return None


def suggest_regex_from_pattern_text(pattern_text: str) -> str | None:
    if "..." in pattern_text:
        left, right = pattern_text.split("...", 1)
        if left and right:
            return f"{re.escape(left)}(?P<a>.+?){re.escape(right)}(?P<b>.+)"
    if " / " in pattern_text:
        parts = [part.strip() for part in pattern_text.split(" / ") if part.strip()]
        if len(parts) >= 2:
            return "(?P<a>.+?)".join(re.escape(part) for part in parts)
    if pattern_text and not PUNCT_RE.search(pattern_text):
        return re.escape(pattern_text)
    return None


def _overlaps_known(start: int, end: int, known_matches: list[GrammarMatch]) -> bool:
    return any(start < match.end and match.start < end for match in known_matches)


class GrammarAnalysisStats:
    """Aggregate known-match and corpus statistics for reports."""

    def __init__(self):
        self.by_rule: dict[str, _RuleStat] = {}
        self.by_category: Counter[str] = Counter()
        self.by_chapter: Counter[str] = Counter()
        self.by_source: dict[str, _SourceStat] = {}
        self.noise_counts: Counter[str] = Counter()
        self.total_matches = 0
        self.total_sentences = 0
        self.total_clauses = 0
        self.total_paragraphs = 0
        self.total_chapters = 0
        self.total_sources = 0
        self.source_chars = 0

    def add_source(self, source: TextSource) -> None:
        self.total_sources += 1
        self.source_chars += source.chars
        self.by_source[source.path] = _SourceStat(
            source_path=source.path,
            encoding=source.encoding,
            chars=source.chars,
            truncated=source.truncated,
        )

    def add_chapter(self, chapter: CorpusChapter) -> None:
        self.total_chapters += 1
        self.by_chapter.setdefault(chapter.chapter_id, 0)
        self._source_stat(chapter.source_path).chapters += 1

    def add_paragraph(self, source_path: str) -> None:
        self.total_paragraphs += 1
        self._source_stat(source_path).paragraphs += 1

    def add_sentence(self, source_path: str) -> None:
        self.total_sentences += 1
        self._source_stat(source_path).sentences += 1

    def add_clauses(self, source_path: str, count: int) -> None:
        self.total_clauses += count
        self._source_stat(source_path).clauses += count

    def add_noise(self, segment_type: str) -> None:
        self.noise_counts[segment_type] += 1

    def add_known_matches(self, matches: list[GrammarMatch]) -> None:
        for match in matches:
            self.total_matches += 1
            self.by_category[match.category] += 1
            if match.chapter_id:
                self.by_chapter[match.chapter_id] += 1
            if match.source_path:
                self._source_stat(match.source_path).known_matches += 1
            stat = self.by_rule.get(match.rule_id)
            if stat is None:
                stat = _RuleStat(match.rule_id, match.category, match.name)
                self.by_rule[match.rule_id] = stat
            stat.count += 1
            if match.chapter_id:
                stat.chapter_ids.add(corpus_chapter_key(match.source_path, match.chapter_id))
            if len(stat.examples) < 5:
                stat.examples.append(
                    {
                        "source_sentence": match.source_sentence,
                        "matched_text": match.matched_text,
                        "chapter_id": match.chapter_id,
                        "source_path": match.source_path,
                    }
                )

    def known_rule_rows(self) -> list[dict]:
        rows: list[dict] = []
        for stat in self.by_rule.values():
            rows.append(
                {
                    "rule_id": stat.rule_id,
                    "category": stat.category,
                    "name": stat.name,
                    "count": stat.count,
                    "chapter_count": len(stat.chapter_ids),
                    "examples": stat.examples,
                }
            )
        return sorted(rows, key=lambda item: (-item["count"], item["rule_id"]))

    def source_rows(self) -> list[dict]:
        return sorted(
            (stat.to_dict() for stat in self.by_source.values()),
            key=lambda item: (-int(item["known_matches"]), item["source_path"]),
        )

    def summary(
        self,
        unknown_candidates: list[UnknownPatternCandidate],
        name_candidates: list[NameCandidate] | None = None,
    ) -> dict:
        names = name_candidates or []
        match_density = (self.total_matches / self.source_chars * 10000) if self.source_chars else 0.0
        return {
            "total_sources": self.total_sources,
            "total_chapters": self.total_chapters,
            "total_paragraphs": self.total_paragraphs,
            "total_sentences": self.total_sentences,
            "total_clauses": self.total_clauses,
            "source_chars": self.source_chars,
            "total_rules_matched": len(self.by_rule),
            "total_matches": self.total_matches,
            "by_category": dict(sorted(self.by_category.items(), key=lambda item: (-item[1], item[0]))),
            "by_chapter": dict(sorted(self.by_chapter.items())),
            "noise_counts": dict(sorted(self.noise_counts.items())),
            "unknown_candidate_count": len(unknown_candidates),
            "name_candidate_count": len(names),
            "name_mentions": sum(candidate.frequency for candidate in names),
            "known_match_density_per_10k_chars": round(match_density, 3),
        }

    def _source_stat(self, source_path: str) -> _SourceStat:
        key = source_path or "<unknown>"
        stat = self.by_source.get(key)
        if stat is None:
            stat = _SourceStat(source_path=key)
            self.by_source[key] = stat
        return stat


class GrammarLearningPatternScanner:
    """End-to-end scanner used by translator learning coach."""

    def __init__(self, known_scanner: GrammarPatternScanner | None = None):
        self.known_scanner = known_scanner or GrammarPatternScanner()

    def analyze_paths(
        self,
        paths: Iterable[str | Path],
        *,
        unknown_min_count: int = 5,
        max_files: int | None = None,
        max_bytes_per_file: int | None = None,
        max_sentences: int | None = None,
        candidate_limit: int = 200,
        include_name_scan: bool = True,
        name_min_count: int = 2,
        name_candidate_limit: int = 200,
    ) -> dict:
        resolved_files = self._resolve_input_files(paths, max_files=max_files)
        stats = GrammarAnalysisStats()
        miner = UnknownGrammarPatternMiner()
        name_scanner = CorpusNameScanner() if include_name_scan else None
        sources: list[TextSource] = []
        warnings: list[str] = []

        for filepath in resolved_files:
            try:
                raw_text, source = read_text_file(filepath, max_bytes=max_bytes_per_file)
            except OSError as exc:
                warnings.append(f"Could not read {filepath}: {exc}")
                continue
            sources.append(source)
            stats.add_source(source)
            self._analyze_text_into_stats(
                normalize_text(raw_text),
                source_path=source.path,
                stats=stats,
                miner=miner,
                name_scanner=name_scanner,
                max_sentences=max_sentences,
            )
            if max_sentences and stats.total_sentences >= max_sentences:
                break

        unknown_candidates = miner.finalize(min_count=unknown_min_count, limit=candidate_limit)
        name_candidates = (
            name_scanner.finalize(min_count=name_min_count, limit=name_candidate_limit)
            if name_scanner is not None
            else []
        )
        report = {
            "summary": stats.summary(unknown_candidates, name_candidates),
            "sources": [source.to_dict() for source in sources],
            "source_statistics": stats.source_rows(),
            "warnings": warnings,
            "known_rules": stats.known_rule_rows(),
            "unknown_candidates": [candidate.to_dict() for candidate in unknown_candidates],
            "name_statistics": summarize_name_candidates(name_candidates),
            "name_candidates": [candidate.to_dict() for candidate in name_candidates],
            "rule_backlog": generate_rule_backlog(stats, unknown_candidates),
            "metadata": {
                "engine": "GrammarLearningPatternScanner",
                "pipeline_scope": "translator_learning_coach_only",
                "non_llm": True,
            },
        }
        return report

    def analyze_text(
        self,
        text: str,
        *,
        source_path: str = "",
        unknown_min_count: int = 2,
        max_sentences: int | None = None,
        candidate_limit: int = 200,
        include_name_scan: bool = True,
        name_min_count: int = 2,
        name_candidate_limit: int = 200,
    ) -> dict:
        stats = GrammarAnalysisStats()
        miner = UnknownGrammarPatternMiner()
        name_scanner = CorpusNameScanner() if include_name_scan else None
        source = TextSource(source_path or "<memory>", "memory", len(text), False)
        stats.add_source(source)
        self._analyze_text_into_stats(
            normalize_text(text),
            source_path=source.path,
            stats=stats,
            miner=miner,
            name_scanner=name_scanner,
            max_sentences=max_sentences,
        )
        unknown_candidates = miner.finalize(min_count=unknown_min_count, limit=candidate_limit)
        name_candidates = (
            name_scanner.finalize(min_count=name_min_count, limit=name_candidate_limit)
            if name_scanner is not None
            else []
        )
        return {
            "summary": stats.summary(unknown_candidates, name_candidates),
            "sources": [source.to_dict()],
            "source_statistics": stats.source_rows(),
            "warnings": [],
            "known_rules": stats.known_rule_rows(),
            "unknown_candidates": [candidate.to_dict() for candidate in unknown_candidates],
            "name_statistics": summarize_name_candidates(name_candidates),
            "name_candidates": [candidate.to_dict() for candidate in name_candidates],
            "rule_backlog": generate_rule_backlog(stats, unknown_candidates),
            "metadata": {
                "engine": "GrammarLearningPatternScanner",
                "pipeline_scope": "translator_learning_coach_only",
                "non_llm": True,
            },
        }

    def _analyze_text_into_stats(
        self,
        text: str,
        *,
        source_path: str,
        stats: GrammarAnalysisStats,
        miner: UnknownGrammarPatternMiner,
        name_scanner: CorpusNameScanner | None,
        max_sentences: int | None,
    ) -> None:
        for chapter in split_chapters(text, source_path=source_path):
            if max_sentences and stats.total_sentences >= max_sentences:
                return
            stats.add_chapter(chapter)
            for paragraph_index, paragraph in enumerate(split_paragraphs(chapter.text)):
                if max_sentences and stats.total_sentences >= max_sentences:
                    return
                stats.add_paragraph(source_path)
                segment_type = classify_segment(paragraph)
                if is_noise_segment(paragraph, segment_type):
                    stats.add_noise(segment_type)
                    continue
                if name_scanner is not None:
                    name_scanner.scan_text(paragraph, chapter_id=chapter.chapter_id, source_path=source_path)
                paragraph_spans = detect_protected_spans(paragraph)
                for sentence_index, sentence in enumerate(split_sentences(paragraph, paragraph_spans)):
                    if max_sentences and stats.total_sentences >= max_sentences:
                        return
                    if not CJK_RE.search(sentence):
                        continue
                    stats.add_sentence(source_path)
                    sentence_spans = detect_protected_spans(sentence)
                    known_matches = self.known_scanner.scan(
                        sentence,
                        sentence_spans,
                        source_sentence=sentence,
                        chapter_id=chapter.chapter_id,
                        paragraph_index=paragraph_index,
                        sentence_index=sentence_index,
                        source_path=source_path,
                    )
                    stats.add_known_matches(known_matches)
                    miner.scan_sentence(
                        sentence,
                        known_matches=known_matches,
                        chapter_id=chapter.chapter_id,
                        source_path=source_path,
                    )
                    clauses = split_clauses(sentence, sentence_spans)
                    stats.add_clauses(source_path, len(clauses))
                    for clause in clauses:
                        miner.scan_clause(
                            clause,
                            known_matches=known_matches,
                            chapter_id=chapter.chapter_id,
                            source_sentence=sentence,
                            source_path=source_path,
                        )

    @staticmethod
    def _resolve_input_files(paths: Iterable[str | Path], *, max_files: int | None = None) -> list[Path]:
        files: list[Path] = []
        for raw_path in paths:
            path = Path(raw_path)
            if path.is_dir():
                files.extend(sorted(child for child in path.rglob("*.txt") if child.is_file()))
            elif path.is_file():
                files.append(path)
        unique: list[Path] = []
        seen: set[str] = set()
        for file_path in files:
            key = str(file_path.resolve())
            if key in seen:
                continue
            seen.add(key)
            unique.append(file_path)
            if max_files and len(unique) >= max_files:
                break
        return unique


def generate_rule_backlog(
    stats: GrammarAnalysisStats,
    unknown_candidates: list[UnknownPatternCandidate],
    *,
    known_min_count: int = 20,
    unknown_min_count: int = 10,
) -> list[dict]:
    backlog: list[dict] = []
    for stat in stats.by_rule.values():
        if stat.count < known_min_count:
            continue
        backlog.append(
            {
                "type": "known_rule_optimization",
                "rule_id": stat.rule_id,
                "category": stat.category,
                "count": stat.count,
                "priority": min(100, 40 + stat.count + len(stat.chapter_ids) * 2),
                "reason": "high_frequency_known_pattern",
                "examples": stat.examples[:3],
            }
        )

    for candidate in unknown_candidates:
        if candidate.frequency < unknown_min_count or candidate.confidence < 0.62:
            continue
        backlog.append(
            {
                "type": "new_rule_candidate",
                "candidate_id": candidate.candidate_id,
                "pattern_text": candidate.pattern_text,
                "pattern_type": candidate.pattern_type,
                "guessed_category": candidate.guessed_category,
                "count": candidate.frequency,
                "chapter_count": candidate.chapter_count,
                "confidence": candidate.confidence,
                "priority": estimate_unknown_priority(candidate),
                "reason": "frequent_unknown_grammar_frame",
                "suggested_regex": candidate.suggested_regex,
                "examples": candidate.examples[:3],
            }
        )
    return sorted(backlog, key=lambda item: (-int(item["priority"]), item.get("type", "")))


def estimate_unknown_priority(candidate: UnknownPatternCandidate) -> int:
    base = 35
    base += min(candidate.frequency * 2, 35)
    base += min(candidate.chapter_count * 2, 20)
    base += int(candidate.confidence * 10)
    if candidate.pattern_type in {"paired_marker", "frame_template"}:
        base += 8
    return min(base, 100)


def render_markdown_report(report: dict) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Grammar Learning Pattern Report",
        "",
        "## Summary",
        "",
        f"- Sources: {summary.get('total_sources', 0)}",
        f"- Chapters: {summary.get('total_chapters', 0)}",
        f"- Sentences: {summary.get('total_sentences', 0)}",
        f"- Known rules matched: {summary.get('total_rules_matched', 0)}",
        f"- Total known matches: {summary.get('total_matches', 0)}",
        f"- Unknown candidates: {summary.get('unknown_candidate_count', 0)}",
        f"- Name candidates: {summary.get('name_candidate_count', 0)}",
        f"- Known match density / 10k chars: {summary.get('known_match_density_per_10k_chars', 0)}",
        "",
        "## Known Categories",
        "",
    ]
    by_category = summary.get("by_category") or {}
    if by_category:
        for category, count in by_category.items():
            lines.append(f"- `{category}`: {count}")
    else:
        lines.append("- No known category matches.")

    lines.extend(["", "## Source Statistics", "", "| Source | Chars | Chapters | Sentences | Known Matches | Density / 10k |", "|---|---:|---:|---:|---:|---:|"])
    for source in report.get("source_statistics", [])[:50]:
        lines.append(
            "| `{path}` | {chars} | {chapters} | {sentences} | {matches} | {density} |".format(
                path=str(source.get("source_path", "")).replace("|", "\\|"),
                chars=source.get("chars", 0),
                chapters=source.get("chapters", 0),
                sentences=source.get("sentences", 0),
                matches=source.get("known_matches", 0),
                density=source.get("known_match_density_per_10k_chars", 0),
            )
        )

    lines.extend(["", "## Name Candidates", "", "| Source | Type | Frequency | Chapters | Confidence |", "|---|---|---:|---:|---:|"])
    for candidate in report.get("name_candidates", [])[:50]:
        lines.append(
            "| `{source}` | {etype} | {freq} | {chapters} | {conf:.2f} |".format(
                source=str(candidate.get("source", "")).replace("|", "\\|"),
                etype=candidate.get("entity_type", ""),
                freq=int(candidate.get("frequency", 0)),
                chapters=int(candidate.get("chapter_count", 0)),
                conf=float(candidate.get("confidence", 0.0)),
            )
        )

    lines.extend(["", "## Unknown Candidates", "", "| Candidate | Type | Frequency | Chapters | Confidence | Guess |", "|---|---|---:|---:|---:|---|"])
    for candidate in report.get("unknown_candidates", [])[:50]:
        lines.append(
            "| `{pattern}` | {ptype} | {freq} | {chapters} | {conf:.2f} | {guess} |".format(
                pattern=str(candidate.get("pattern_text", "")).replace("|", "\\|"),
                ptype=candidate.get("pattern_type", ""),
                freq=int(candidate.get("frequency", 0)),
                chapters=int(candidate.get("chapter_count", 0)),
                conf=float(candidate.get("confidence", 0.0)),
                guess=candidate.get("guessed_category") or "",
            )
        )

    lines.extend(["", "## Top Known Rules", "", "| Rule | Category | Count | Chapters |", "|---|---|---:|---:|"])
    for rule in report.get("known_rules", [])[:50]:
        lines.append(
            f"| `{rule.get('rule_id', '')}` | {rule.get('category', '')} | {rule.get('count', 0)} | {rule.get('chapter_count', 0)} |"
        )
    return "\n".join(lines) + "\n"


def render_unknown_candidates_csv(report: dict) -> str:
    output = io.StringIO()
    fieldnames = [
        "candidate_id",
        "pattern_text",
        "pattern_type",
        "frequency",
        "chapter_count",
        "confidence",
        "guessed_category",
        "suggested_regex",
        "status",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for candidate in report.get("unknown_candidates", []):
        writer.writerow({field: candidate.get(field, "") for field in fieldnames})
    return output.getvalue()


def render_known_rules_csv(report: dict) -> str:
    output = io.StringIO()
    fieldnames = ["rule_id", "category", "name", "count", "chapter_count"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for rule in report.get("known_rules", []):
        writer.writerow({field: rule.get(field, "") for field in fieldnames})
    return output.getvalue()


def render_name_candidates_csv(report: dict) -> str:
    output = io.StringIO()
    fieldnames = [
        "candidate_id",
        "source",
        "entity_type",
        "frequency",
        "chapter_count",
        "source_count",
        "confidence",
        "status",
        "source_paths",
        "examples",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for candidate in report.get("name_candidates", []):
        row = {field: candidate.get(field, "") for field in fieldnames}
        row["source_paths"] = ";".join(candidate.get("source_paths", []) or [])
        row["examples"] = " | ".join(candidate.get("examples", []) or [])
        writer.writerow(row)
    return output.getvalue()


def render_source_statistics_csv(report: dict) -> str:
    output = io.StringIO()
    fieldnames = [
        "source_path",
        "encoding",
        "chars",
        "truncated",
        "chapters",
        "paragraphs",
        "sentences",
        "clauses",
        "known_matches",
        "known_match_density_per_10k_chars",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for source in report.get("source_statistics", []):
        writer.writerow({field: source.get(field, "") for field in fieldnames})
    return output.getvalue()


def write_grammar_learning_report(report: dict, out_dir: str | Path, *, stem: str = "grammar_learning_report") -> dict:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / f"{stem}.json"
    md_path = target_dir / f"{stem}.md"
    unknown_csv_path = target_dir / f"{stem}_unknown_candidates.csv"
    known_csv_path = target_dir / f"{stem}_known_rules.csv"
    name_csv_path = target_dir / f"{stem}_name_candidates.csv"
    source_csv_path = target_dir / f"{stem}_source_statistics.csv"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(report), encoding="utf-8")
    unknown_csv_path.write_text(render_unknown_candidates_csv(report), encoding="utf-8")
    known_csv_path.write_text(render_known_rules_csv(report), encoding="utf-8")
    name_csv_path.write_text(render_name_candidates_csv(report), encoding="utf-8")
    source_csv_path.write_text(render_source_statistics_csv(report), encoding="utf-8")

    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "unknown_candidates_csv": str(unknown_csv_path),
        "known_rules_csv": str(known_csv_path),
        "name_candidates_csv": str(name_csv_path),
        "source_statistics_csv": str(source_csv_path),
    }
