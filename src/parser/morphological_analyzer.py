#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lightweight morphology/POS analyzer for pipeline-side syntax artifacts."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass


TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[A-Za-z][A-Za-z0-9'_-]*|\d+(?:[.,]\d+)*|[^\s]")
PUNCTUATION = set("，。！？；：、,.!?;:\"'“”‘’（）()[]{}《》<>")
PARTICLES = {"的", "地", "得", "了", "着", "过", "吗", "呢", "吧", "啊"}
PRONOUNS = {"我", "你", "他", "她", "它", "们", "咱", "俺"}
PREPOSITIONS = {"在", "从", "向", "对", "把", "被", "给", "跟", "和", "为"}
CONJUNCTIONS = {"和", "与", "并", "而", "但", "却", "或"}
COMMON_VERBS = {"是", "有", "说", "道", "看", "去", "来", "走", "想", "听", "问", "答", "做", "拿", "给", "把", "被"}
COMMON_ADVERBS = {"不", "没", "很", "更", "最", "又", "再", "才", "就", "都", "也", "已", "已经"}


@dataclass(slots=True)
class MorphToken:
    text: str
    pos: str
    lemma: str
    start: int
    end: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class MorphologicalAnalysis:
    text: str
    tokens: list[str]
    pos_tags: list[str]
    lemmas: list[str]
    token_details: list[MorphToken]
    dependencies: list[dict]

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "tokens": self.tokens,
            "posTags": self.pos_tags,
            "lemmas": self.lemmas,
            "tokenDetails": [token.to_dict() for token in self.token_details],
            "dependencies": self.dependencies,
        }


class MorphologicalAnalyzer:
    """Deterministic analyzer used by the non-LLM learning/pipeline path."""

    def analyze(self, text: str) -> dict:
        token_details = self.tokenize_with_spans(text)
        tokens = [token.text for token in token_details]
        pos_tags = [token.pos for token in token_details]
        lemmas = [token.lemma for token in token_details]
        analysis = MorphologicalAnalysis(
            text=text,
            tokens=tokens,
            pos_tags=pos_tags,
            lemmas=lemmas,
            token_details=token_details,
            dependencies=self.parse_dependencies(tokens, pos_tags),
        )
        return analysis.to_dict()

    def tokenize(self, text: str) -> list[str]:
        return [match.group(0) for match in TOKEN_RE.finditer(text or "")]

    def tokenize_with_spans(self, text: str) -> list[MorphToken]:
        tokens: list[MorphToken] = []
        for match in TOKEN_RE.finditer(text or ""):
            token = match.group(0)
            tokens.append(
                MorphToken(
                    text=token,
                    pos=self.tag_token(token),
                    lemma=token.lower() if token.isascii() else token,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return tokens

    def tag_pos(self, tokens: list[str]) -> list[str]:
        return [self.tag_token(token) for token in tokens]

    def lemmatize(self, tokens: list[str]) -> list[str]:
        return [token.lower() if token.isascii() else token for token in tokens]

    def parse_dependencies(self, tokens: list[str], pos_tags: list[str] | None = None) -> list[dict]:
        pos_tags = pos_tags or self.tag_pos(tokens)
        root = self._root_index(tokens, pos_tags)
        dependencies = []
        for index, token in enumerate(tokens):
            pos = pos_tags[index] if index < len(pos_tags) else "unknown"
            dependencies.append(
                {
                    "id": index,
                    "form": token,
                    "pos": pos,
                    "head": -1 if index == root else root,
                    "relation": self._relation(index, root, pos),
                }
            )
        return dependencies

    @staticmethod
    def tag_token(token: str) -> str:
        if not token:
            return "unknown"
        if token in PUNCTUATION:
            return "punctuation"
        if token.isdigit() or re.fullmatch(r"\d+(?:[.,]\d+)*", token):
            return "number"
        if token in PARTICLES:
            return "particle"
        if token in PRONOUNS:
            return "pronoun"
        if token in PREPOSITIONS:
            return "preposition"
        if token in CONJUNCTIONS:
            return "conjunction"
        if token in COMMON_ADVERBS:
            return "adverb"
        if token in COMMON_VERBS:
            return "verb"
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9'_-]*", token):
            return "latin"
        if re.fullmatch(r"[\u4e00-\u9fff]", token):
            return "unknown"
        return "symbol"

    @staticmethod
    def _root_index(tokens: list[str], pos_tags: list[str]) -> int:
        for index, pos in enumerate(pos_tags):
            if pos == "verb":
                return index
        for index, pos in enumerate(pos_tags):
            if pos not in {"punctuation", "particle", "symbol"}:
                return index
        return 0 if tokens else -1

    @staticmethod
    def _relation(index: int, root: int, pos: str) -> str:
        if root < 0:
            return "root"
        if index == root:
            return "root"
        if pos == "punctuation":
            return "punct"
        if pos == "particle":
            return "mark"
        if pos == "preposition":
            return "case"
        if index < root:
            return "nsubj"
        if pos in {"number", "adverb"}:
            return "advmod"
        return "obj" if index == root + 1 else "dep"
