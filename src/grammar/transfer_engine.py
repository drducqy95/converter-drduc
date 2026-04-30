#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Source-side grammar transfer for high-value ZH -> VI constructions.

The engine rewrites only construction markers and keeps Chinese content in place
so the existing Trie/LuatNhan/RBMT path can still translate lexical material.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class GrammarTransferTrace:
    rule_id: str
    source: str
    selected: str
    source_span: tuple[int, int]
    priority: int
    confidence: float = 0.86

    def to_candidate_trace(self) -> dict:
        return {
            "source": self.source,
            "selected": self.selected,
            "candidates": [self.selected],
            "priority": self.priority,
            "fallback_level": "grammar_transfer",
            "reason": self.rule_id,
            "source_span": self.source_span,
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class GrammarTransferResult:
    text: str
    traces: list[dict]


@dataclass(frozen=True, slots=True)
class _TransferRule:
    rule_id: str
    pattern: re.Pattern[str]
    replacement: Callable[[re.Match[str]], str]
    priority: int
    confidence: float = 0.86


_CLAUSE = r"([^，。！？；\n]{1,60}?)"
_SHORT_CLAUSE = r"([^，。！？；\n]{1,30}?)"
_POSITIVE_PASSIVE_VERBS = {
    "知",
    "知道",
    "见",
    "称",
    "承认",
    "认可",
    "铭记",
    "记住",
    "接受",
    "理解",
}
_NEGATIVE_PASSIVE_VERBS = {
    "杀",
    "困",
    "压",
    "压迫",
    "俘",
    "俘获",
    "捉弄",
    "侵染",
    "污染",
    "控制",
    "摧毁",
    "封印",
    "吞噬",
    "攻击",
    "伤害",
    "入侵",
}


class GrammarTransferEngine:
    """Apply a conservative P0/P1 grammar-transfer pack before lexical decode."""

    def __init__(self):
        self._rules = self._build_rules()

    def rewrite_source(self, text: str, *, protected_terms: list[str] | tuple[str, ...] | None = None) -> GrammarTransferResult:
        current = text
        traces: list[dict] = []
        protected = tuple(sorted({term for term in (protected_terms or []) if term}, key=len, reverse=True))
        for rule in self._rules:
            current, rule_traces = self._apply_rule(current, rule, protected_terms=protected)
            traces.extend(rule_traces)
        return GrammarTransferResult(current, traces)

    def _apply_rule(
        self,
        text: str,
        rule: _TransferRule,
        *,
        protected_terms: tuple[str, ...] = (),
    ) -> tuple[str, list[dict]]:
        protected_ranges = self._protected_ranges(text, protected_terms=protected_terms)
        pieces: list[str] = []
        traces: list[dict] = []
        last = 0
        for match in rule.pattern.finditer(text):
            if match.start() < last:
                continue
            if self._overlaps_protected(match.span(), protected_ranges):
                continue

            replacement = rule.replacement(match)
            if replacement == match.group(0):
                continue

            pieces.append(text[last:match.start()])
            pieces.append(replacement)
            traces.append(
                GrammarTransferTrace(
                    rule_id=rule.rule_id,
                    source=match.group(0),
                    selected=replacement,
                    source_span=match.span(),
                    priority=rule.priority,
                    confidence=rule.confidence,
                ).to_candidate_trace()
            )
            last = match.end()

        if not traces:
            return text, []
        pieces.append(text[last:])
        return "".join(pieces), traces

    @staticmethod
    def _protected_ranges(text: str, *, protected_terms: tuple[str, ...] = ()) -> list[tuple[int, int]]:
        patterns = (
            r"【[^】]{1,80}】",
            r"《[^》]{1,80}》",
            r"\[\d{1,2}:\d{2}(?::\d{2})?\]",
            r"\b\d{1,2}:\d{2}:\d{2}\b",
            r"\b\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?\b",
            r"[\"“”][零〇一二三四五六七八九十百千万亿兆\d]{1,16}[\"“”]",
        )
        ranges: list[tuple[int, int]] = []
        for pattern in patterns:
            ranges.extend(match.span() for match in re.finditer(pattern, text))
        for term in protected_terms:
            ranges.extend(match.span() for match in re.finditer(re.escape(term), text))
        return sorted(ranges)

    @staticmethod
    def _overlaps_protected(span: tuple[int, int], protected_ranges: list[tuple[int, int]]) -> bool:
        start, end = span
        return any(start < protected_end and protected_start < end for protected_start, protected_end in protected_ranges)

    @classmethod
    def _build_rules(cls) -> list[_TransferRule]:
        def repl(template: str) -> Callable[[re.Match[str]], str]:
            return lambda match: template.format(*match.groups())

        def paired(prefix: str, bridge: str) -> Callable[[re.Match[str]], str]:
            def _replace(match: re.Match[str]) -> str:
                clause = match.group(1)
                subject = match.group(2) if len(match.groups()) >= 2 else ""
                if subject:
                    return f"{prefix} {clause}, {subject}{bridge}"
                return f"{prefix} {clause} {bridge}"

            return _replace

        def passive(match: re.Match[str]) -> str:
            marker, agent, verb = match.groups()
            passive_marker = "được" if any(verb.startswith(item) for item in _POSITIVE_PASSIVE_VERBS) else "bị"
            if marker == "由" and not any(verb.startswith(item) for item in _NEGATIVE_PASSIVE_VERBS):
                passive_marker = "do"
            return f"{passive_marker} {agent}{verb}"

        def preference_ningke(match: re.Match[str]) -> str:
            clause, connector = match.groups()
            tail = "cũng phải" if connector == "也要" else "cũng không"
            return f"thà {clause} {tail}"

        def concession_suiran(match: re.Match[str]) -> str:
            clause, connector = match.groups()
            bridge = "v\u1eabn" if connector in {"\u4ecd\u7136", "\u8fd8\u662f"} else "nh\u01b0ng"
            return f"tuy {clause} {bridge}"

        fixed_map = {
            "有鉴于此": "vì vậy",
            "不管怎么说": "dù nói thế nào thì",
            "无论如何": "dù thế nào đi nữa",
            "不管怎样": "dù sao đi nữa",
            "相比之下": "so sánh mà xem",
            "对比之下": "khi so sánh",
            "以备不时之需": "phòng khi cần thiết",
            "以防万一": "đề phòng vạn nhất",
            "以防": "đề phòng",
            "据报道": "theo báo cáo",
            "据了解": "theo tìm hiểu",
            "据说": "nghe nói",
            "据悉": "được biết",
            "所谓的": "cái gọi là",
            "所谓": "cái gọi là",
            "换句话说": "nói cách khác",
            "也就是说": "tức là",
            "说白了": "nói thẳng ra",
            "说到底": "suy cho cùng",
            "说实话": "nói thật",
            "说起来": "nói đến thì",
            "虽说": "tuy rằng",
            "话说": "nói đến thì",
            "说不定": "biết đâu",
            "也许": "có lẽ",
            "或许": "có lẽ",
            "多半": "phần lớn là",
            "想必": "chắc hẳn",
            "估计": "ước chừng",
            "大概": "đại khái",
            "恰好": "vừa hay",
            "刚好": "vừa vặn",
            "正好": "vừa hay",
            "恰巧": "tình cờ",
            "碰巧": "tình cờ",
            "凑巧": "tình cờ",
            "罢了": "thôi",
            "而已": "thôi",
            "不过如此": "chỉ vậy thôi",
            "如此而已": "chỉ như vậy thôi",
            "何况": "huống chi",
            "更何况": "huống chi là",
            "反而": "ngược lại",
            "乃至": "thậm chí đến",
            "甚至": "thậm chí",
            "并非": "không phải",
            "未必": "chưa chắc",
            "何尝": "đâu phải",
            "与此同时": "cùng lúc đó",
            "不至于": "không đến mức",
            "否则": "nếu không thì",
            "因此": "vì vậy",
            "因而": "cho nên",
            "由于": "do",
            "随着": "theo",
            "至于": "còn về",
            "关于": "về",
            "对于": "đối với",
            "作为": "với tư cách",
        }

        rules: list[_TransferRule] = [
            _TransferRule("conditional_jiran_jiu", re.compile(f"\u65e2\u7136{_SHORT_CLAUSE}(?:\uff0c)?\u5c31"), paired("\u0111\u00e3", " th\u00ec"), 82),
            _TransferRule("cause_yinwei_suoyi", re.compile(f"\u56e0\u4e3a{_SHORT_CLAUSE}(?:\uff0c)?(?:\u6240\u4ee5|\u4fbf|\u5c31)"), repl("v\u00ec {0} n\u00ean"), 80),
            _TransferRule("concession_suiran_dan", re.compile(f"(?:\u867d\u7136|\u867d\u8bf4|\u5c3d\u7ba1){_SHORT_CLAUSE}(?:\uff0c)?(\u4f46\u662f|\u4f46|\u5374|\u4ecd\u7136|\u8fd8\u662f)"), concession_suiran, 80),
            _TransferRule("additive_bujin_ye", re.compile(f"(?:\u4e0d\u4f46|\u4e0d\u4ec5){_SHORT_CLAUSE}(?:\uff0c)?(?:\u4e5f|\u66f4)"), repl("kh\u00f4ng ch\u1ec9 {0} m\u00e0 c\u00f2n"), 76),
            _TransferRule("concurrent_yimian", re.compile(f"\u4e00\u9762{_SHORT_CLAUSE}(?:\uff0c)?\u4e00\u9762"), repl("v\u1eeba {0} v\u1eeba"), 78),
            _TransferRule("emphatic_lian", re.compile(f"(?<!\u5c31)\u8fde{_SHORT_CLAUSE}(?:\u4e5f|\u90fd)"), repl("ngay c\u1ea3 {0} c\u0169ng"), 78),
            _TransferRule("temporal_xian_zai", re.compile(f"\u5148{_SHORT_CLAUSE}(?:\uff0c)?(?:\u518d|\u7136\u540e|\u624d)"), repl("tr\u01b0\u1edbc ti\u00ean {0}, r\u1ed3i"), 76),
            _TransferRule("conditional_zhiyao_jiu", re.compile(rf"只要{_SHORT_CLAUSE}(?:，)?([^，。！？；\n]{{0,16}}?)就"), paired("chỉ cần", " thì"), 82),
            _TransferRule("conditional_ruguo_jiu", re.compile(rf"如果{_SHORT_CLAUSE}(?:，)?([^，。！？；\n]{{0,16}}?)就"), paired("nếu", " thì"), 82),
            _TransferRule("conditional_yidan_jiu", re.compile(rf"一旦{_SHORT_CLAUSE}(?:，)?([^，。！？；\n]{{0,16}}?)就"), paired("một khi", " thì"), 82),
            _TransferRule("conditional_chufei_fouze", re.compile(rf"除非{_CLAUSE}(?:，)?否则"), repl("trừ phi {0}, nếu không thì"), 82),
            _TransferRule("concession_napa", re.compile(rf"哪怕(?:是)?{_SHORT_CLAUSE}(?:，)?(?:也|都|仍然|还是)"), repl("dù {0} cũng"), 80),
            _TransferRule("concession_jiusuan", re.compile(rf"就算(?:是)?{_SHORT_CLAUSE}(?:，)?(?:也|都|仍然|还是)"), repl("dù cho {0} cũng"), 80),
            _TransferRule("concession_jibian", re.compile(rf"(?:即便|即使|尽管){_SHORT_CLAUSE}(?:，)?(?:也|都|仍然|还是)"), repl("dù {0} vẫn"), 80),
            _TransferRule("regardless_wulun", re.compile(rf"(?:无论|不管){_SHORT_CLAUSE}(?:，)?(?:也|都)"), repl("dù {0} cũng"), 80),
            _TransferRule("contrast_bushi_ershi", re.compile(rf"不是{_SHORT_CLAUSE}而是"), repl("không phải {0} mà là"), 78),
            _TransferRule("additive_budan_erqie", re.compile(rf"(?:不但|不仅){_SHORT_CLAUSE}(?:而且|还)"), repl("không chỉ {0} mà còn"), 76),
            _TransferRule("preference_yuqi_buru", re.compile(rf"与其{_SHORT_CLAUSE}(?:，)?不如"), repl("thà {0} chẳng bằng"), 82),
            _TransferRule("preference_ningke", re.compile(rf"(?:宁可|宁愿){_SHORT_CLAUSE}(?:，)?(也不|也要)"), preference_ningke, 80),
            _TransferRule("parallel_ji_you", re.compile(rf"既{_SHORT_CLAUSE}(?:，)?又"), repl("vừa {0} vừa"), 78),
            _TransferRule("progressive_yue_yue", re.compile(rf"越{_SHORT_CLAUSE}越"), repl("càng {0} càng"), 78),
            _TransferRule("concession_zaizenme", re.compile(rf"再怎么{_SHORT_CLAUSE}(?:，)?(?:也|都)"), repl("dù {0} thế nào cũng"), 78),
            _TransferRule("reason_zhisuoyi_shiyinwei", re.compile(rf"之所以{_CLAUSE}(?:，)?是因为"), repl("sở dĩ {0} là vì"), 80),
            _TransferRule("exclusive_zhiyou_cai", re.compile(rf"只有{_SHORT_CLAUSE}(?:，)?才"), repl("chỉ khi {0} mới"), 80),
            _TransferRule("hypothesis_ruoshi", re.compile(rf"(?:倘若|假如|若是){_SHORT_CLAUSE}(?:，)?"), repl("nếu {0}"), 76),
            _TransferRule("avoidance_miande", re.compile(rf"(?:免得|以免){_SHORT_CLAUSE}"), repl("để tránh {0}"), 76),
            _TransferRule("cause_youyu_yinci", re.compile(rf"由于{_SHORT_CLAUSE}(?:，)?(?:因此|因而|所以)"), repl("do {0} nên"), 78),
            _TransferRule("concurrent_yibian", re.compile(rf"一边{_SHORT_CLAUSE}(?:，)?一边"), repl("vừa {0} vừa"), 78),
            _TransferRule("concurrent_bian", re.compile(rf"边([^边，。！？；\n]{{1,20}}?)边"), repl("vừa {0} vừa"), 76),
            _TransferRule("formal_passive_suo", re.compile(rf"(为|被|由){_SHORT_CLAUSE}所([^，。！？；\n]{{1,6}})"), passive, 84),
            _TransferRule("emphatic_jiulian", re.compile(rf"就连{_SHORT_CLAUSE}(?:也|都)"), repl("ngay cả {0} cũng"), 80),
            _TransferRule("viewpoint_dui_laishuo", re.compile(rf"对{_SHORT_CLAUSE}(?:来说|而言)"), repl("đối với {0} mà nói"), 76),
            _TransferRule("viewpoint_zuowei_eryan", re.compile(rf"作为{_SHORT_CLAUSE}(?:来说|而言)"), repl("với tư cách {0}"), 76),
            _TransferRule("comparison_yu_x_xiangbi", re.compile(rf"(?:与|和){_SHORT_CLAUSE}相(?:比|比较)"), repl("so với {0}"), 76),
            _TransferRule("comparison_biqi", re.compile(rf"比起{_SHORT_CLAUSE}来"), repl("so với {0}"), 76),
            _TransferRule("evidential_ju_x", re.compile(rf"据{_SHORT_CLAUSE}(?:称|说|所说)"), repl("theo {0}"), 76),
            _TransferRule("necessity_fei_buke", re.compile(rf"非{_SHORT_CLAUSE}不可"), repl("nhất định phải {0}"), 76),
        ]

        for source, target in sorted(fixed_map.items(), key=lambda item: len(item[0]), reverse=True):
            rules.append(
                _TransferRule(
                    f"marker_{source}",
                    re.compile(re.escape(source)),
                    lambda _match, target=target: target,
                    64,
                    0.78,
                )
            )
        return sorted(rules, key=lambda item: item.priority, reverse=True)
