#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Small phrase-first Traditional Chinese -> Simplified Chinese converter."""

from __future__ import annotations

from dataclasses import dataclass


PHRASE_MAP = {
    "臺灣": "台湾",
    "後來": "后来",
    "開門": "开门",
    "發現": "发现",
    "龍門客棧": "龙门客栈",
    "說道": "说道",
    "對於": "对于",
}

CHAR_MAP = {
    "臺": "台",
    "灣": "湾",
    "後": "后",
    "來": "来",
    "開": "开",
    "門": "门",
    "發": "发",
    "現": "现",
    "說": "说",
    "對": "对",
    "於": "于",
    "國": "国",
    "體": "体",
    "學": "学",
    "習": "习",
    "這": "这",
    "個": "个",
    "風": "风",
    "雲": "云",
    "萬": "万",
    "與": "与",
    "愛": "爱",
    "麼": "么",
    "將": "将",
    "鐘": "钟",
    "壞": "坏",
    "陰": "阴",
    "陽": "阳",
}


@dataclass(slots=True)
class ConversionTrace:
    source: str
    target: str
    kind: str


class TraditionalToSimplifiedConverter:
    """Deterministic phrase-first baseline converter."""

    def __init__(self, phrase_map: dict[str, str] | None = None, char_map: dict[str, str] | None = None):
        self.phrase_map = dict(PHRASE_MAP)
        self.char_map = dict(CHAR_MAP)
        if phrase_map:
            self.phrase_map.update(phrase_map)
        if char_map:
            self.char_map.update(char_map)
        self._sorted_phrases = sorted(self.phrase_map.keys(), key=len, reverse=True)

    def convert_with_trace(self, text: str) -> tuple[str, list[ConversionTrace]]:
        traces: list[ConversionTrace] = []
        result: list[str] = []
        i = 0
        while i < len(text):
            matched = False
            for phrase in self._sorted_phrases:
                if text.startswith(phrase, i):
                    converted = self.phrase_map[phrase]
                    result.append(converted)
                    traces.append(ConversionTrace(source=phrase, target=converted, kind="phrase"))
                    i += len(phrase)
                    matched = True
                    break
            if matched:
                continue

            ch = text[i]
            converted = self.char_map.get(ch, ch)
            if converted != ch:
                traces.append(ConversionTrace(source=ch, target=converted, kind="char"))
            result.append(converted)
            i += 1

        return "".join(result), traces

    def convert(self, text: str) -> str:
        return self.convert_with_trace(text)[0]
