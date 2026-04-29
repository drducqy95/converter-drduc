#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Phrase-first EN -> VI baseline translator."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.core.md_dictionary_compiler import parse_bulk_md


DEFAULT_LEXICON_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "global" / "en_vi" / "_baseline_en_vi.md"
TOKEN_RE = re.compile(r"[A-Za-z']+|[^\w\s]")
ARTICLES = {"a", "an", "the"}
TENSE_MARKERS = {"will": "sẽ", "did": "đã", "was": "đã", "were": "đã", "have": "đã", "has": "đã", "had": "đã"}
PASSIVE_AUXILIARIES = {"am", "is", "are", "was", "were", "be", "been", "being"}
PAST_PASSIVE_AUXILIARIES = {"was", "were", "had"}
AGENT_PRONOUNS = {
    "i": "tôi",
    "me": "tôi",
    "you": "bạn",
    "he": "anh ấy",
    "him": "anh ấy",
    "she": "cô ấy",
    "her": "cô ấy",
    "it": "nó",
    "we": "chúng tôi",
    "us": "chúng tôi",
    "they": "họ",
    "them": "họ",
}
PHRASAL_VERBS = {
    "come across": "tình cờ gặp",
    "find out": "phát hiện",
    "give up": "từ bỏ",
    "go on": "tiếp tục",
    "look for": "tìm kiếm",
    "look into": "điều tra",
    "pick up": "nhặt lên",
    "set up": "thiết lập",
    "take off": "cất cánh",
    "turn off": "tắt",
    "turn on": "bật",
    "wake up": "thức dậy",
}
PASSIVE_VERB_FORMS = {
    "built": "xây dựng",
    "called": "gọi",
    "created": "tạo ra",
    "discovered": "phát hiện",
    "found": "tìm thấy",
    "given": "đưa",
    "helped": "giúp đỡ",
    "made": "làm",
    "opened": "mở",
    "said": "nói",
    "seen": "nhìn thấy",
    "taken": "lấy",
    "written": "viết",
}
IRREGULAR_PARTICIPLES = {
    "built": "build",
    "found": "find",
    "given": "give",
    "made": "make",
    "said": "say",
    "seen": "see",
    "taken": "take",
    "written": "write",
}
CLAUSE_BOUNDARIES = {",", ".", "!", "?", ";", ":"}


@dataclass(slots=True)
class ENTranslationResult:
    text: str
    trace: list[dict]


class EnglishVietnameseTranslator:
    """Translate short English sentences using phrase-first matching and simple grammar rules."""

    def __init__(self, lexicon_path: str | Path | None = None):
        self.lexicon_path = Path(lexicon_path or DEFAULT_LEXICON_PATH)
        self.lexicon, self.pos_map = self._load_lexicon()

    def _load_lexicon(self) -> tuple[dict[str, str], dict[str, str]]:
        lexicon: dict[str, str] = {}
        pos_map: dict[str, str] = {}
        if self.lexicon_path.exists():
            for entry in parse_bulk_md(str(self.lexicon_path)):
                key = entry.source.lower()
                lexicon[key] = entry.target
                pos = entry.pos_tag or ""
                if entry.metadata_json:
                    import json
                    meta = json.loads(entry.metadata_json)
                    pos = pos or meta.get("pos", "") or meta.get("pos_tag", "")
                    legacy_priority = str(meta.get("priority", "")).strip().lower()
                    if not pos and legacy_priority in {"noun", "adj", "verb", "phrase"}:
                        pos = legacy_priority
                pos_map[key] = pos
        return lexicon, pos_map

    def translate(self, text: str) -> ENTranslationResult:
        tokens = TOKEN_RE.findall(text)
        trace: list[dict] = []
        output: list[str] = []
        i = 0
        pending_tense = ""

        while i < len(tokens):
            token = tokens[i]
            lower = token.lower()

            passive_translation, passive_len = self._try_passive_voice(tokens, i, pending_tense)
            if passive_translation:
                output.append(passive_translation)
                trace.append({
                    "source": " ".join(tokens[i:i + passive_len]),
                    "target": passive_translation,
                    "reason": "passive_voice",
                })
                pending_tense = ""
                i += passive_len
                continue

            if lower in TENSE_MARKERS:
                pending_tense = TENSE_MARKERS[lower]
                trace.append({"source": token, "target": pending_tense, "reason": "tense_marker"})
                i += 1
                continue

            if lower in ARTICLES:
                trace.append({"source": token, "target": "", "reason": "article_removed"})
                i += 1
                continue

            phrase_translation, phrase_len, phrase_reason = self._match_phrase(tokens, i)
            if phrase_translation:
                if pending_tense:
                    output.append(pending_tense)
                    pending_tense = ""
                output.append(phrase_translation)
                trace.append({"source": " ".join(tokens[i:i + phrase_len]), "target": phrase_translation, "reason": phrase_reason})
                i += phrase_len
                continue

            if i + 1 < len(tokens):
                adj = lower
                noun = tokens[i + 1].lower()
                if self.pos_map.get(adj) == "adj" and self.pos_map.get(noun) == "noun":
                    noun_target = self.lexicon.get(self._singular(noun), noun)
                    adj_target = self.lexicon.get(adj, adj)
                    if pending_tense:
                        output.append(pending_tense)
                        pending_tense = ""
                    prefix = "những " if noun.endswith("s") and noun == self._singular(noun) + "s" else ""
                    combined = f"{prefix}{noun_target} {adj_target}".strip()
                    output.append(combined)
                    trace.append({"source": f"{tokens[i]} {tokens[i + 1]}", "target": combined, "reason": "adj_noun_rule"})
                    i += 2
                    continue

            if lower.endswith("'s") and len(lower) > 2:
                owner = self.lexicon.get(lower[:-2], lower[:-2])
                output.append(f"của {owner}")
                trace.append({"source": token, "target": f"của {owner}", "reason": "possessive"})
                i += 1
                continue

            base = self._singular(lower)
            if base in self.lexicon:
                if pending_tense:
                    output.append(pending_tense)
                    pending_tense = ""
                translated = self.lexicon[base]
                if lower.endswith("s") and base != lower and self.pos_map.get(base) == "noun":
                    translated = f"những {translated}"
                output.append(translated)
                trace.append({"source": token, "target": translated, "reason": "lexicon"})
            else:
                output.append(token)
                trace.append({"source": token, "target": token, "reason": "fallback"})
            i += 1

        normalized = self._normalize(" ".join(output))
        return ENTranslationResult(text=normalized, trace=trace)

    def _match_phrase(self, tokens: list[str], pos: int) -> tuple[str | None, int, str]:
        max_len = min(4, len(tokens) - pos)
        for size in range(max_len, 1, -1):
            phrase = " ".join(token.lower() for token in tokens[pos:pos + size])
            if phrase in self.lexicon:
                return self.lexicon[phrase], size, "phrase_match"
            if phrase in PHRASAL_VERBS:
                return PHRASAL_VERBS[phrase], size, "phrasal_verb"
        return None, 0, ""

    def _try_passive_voice(
        self,
        tokens: list[str],
        pos: int,
        pending_tense: str = "",
    ) -> tuple[str | None, int]:
        aux = tokens[pos].lower()
        if aux not in PASSIVE_AUXILIARIES:
            return None, 0

        verb_pos = pos + 1
        negative = False
        if verb_pos < len(tokens) and tokens[verb_pos].lower() == "not":
            negative = True
            verb_pos += 1
        if verb_pos >= len(tokens):
            return None, 0

        verb_token = tokens[verb_pos]
        if not self._looks_like_participle(verb_token):
            return None, 0

        tense = pending_tense
        if not tense and aux in PAST_PASSIVE_AUXILIARIES:
            tense = "đã"

        marker = "không được" if negative else "được"
        passive_prefix = f"{tense} {marker}".strip()
        passive_text = f"{passive_prefix} {self._translate_passive_verb(verb_token)}".strip()

        agent_text, agent_len = self._translate_passive_agent(tokens, verb_pos + 1)
        if agent_text:
            passive_text = f"{passive_text} {agent_text}"

        return passive_text, (verb_pos + 1 - pos) + agent_len

    def _looks_like_participle(self, token: str) -> bool:
        lower = token.lower()
        return lower in PASSIVE_VERB_FORMS or lower in IRREGULAR_PARTICIPLES or lower.endswith("ed")

    def _translate_passive_verb(self, token: str) -> str:
        lower = token.lower()
        if lower in PASSIVE_VERB_FORMS:
            return PASSIVE_VERB_FORMS[lower]
        base = self._verb_base(lower)
        return self.lexicon.get(base) or self.lexicon.get(lower) or base

    def _verb_base(self, token: str) -> str:
        if token in IRREGULAR_PARTICIPLES:
            return IRREGULAR_PARTICIPLES[token]
        if token.endswith("ied") and len(token) > 3:
            return token[:-3] + "y"
        if token.endswith("ed") and len(token) > 2:
            if token[:-1] in self.lexicon:
                return token[:-1]
            stem = token[:-2]
            if len(stem) > 2 and stem[-1] == stem[-2]:
                return stem[:-1]
            return stem
        return token

    def _translate_passive_agent(self, tokens: list[str], pos: int) -> tuple[str, int]:
        if pos >= len(tokens) or tokens[pos].lower() != "by":
            return "", 0

        agent_parts: list[str] = []
        i = pos + 1
        while i < len(tokens) and len(agent_parts) < 4:
            token = tokens[i]
            lower = token.lower()
            if token in CLAUSE_BOUNDARIES or lower in {"and", "but", "or"}:
                break
            translated = self._translate_agent_token(token)
            if translated:
                agent_parts.append(translated)
            i += 1

        if not agent_parts:
            return "", 0
        return f"bởi {' '.join(agent_parts)}", i - pos

    def _translate_agent_token(self, token: str) -> str:
        lower = token.lower()
        if lower in ARTICLES:
            return ""
        if lower in AGENT_PRONOUNS:
            return AGENT_PRONOUNS[lower]
        base = self._singular(lower)
        if base in self.lexicon:
            return self.lexicon[base]
        return token

    def _singular(self, token: str) -> str:
        if token.endswith("ies") and len(token) > 3:
            return token[:-3] + "y"
        if token.endswith("s") and len(token) > 3:
            return token[:-1]
        return token

    def _normalize(self, text: str) -> str:
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
