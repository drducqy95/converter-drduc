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

            if lower in TENSE_MARKERS:
                pending_tense = TENSE_MARKERS[lower]
                trace.append({"source": token, "target": pending_tense, "reason": "tense_marker"})
                i += 1
                continue

            if lower in ARTICLES:
                trace.append({"source": token, "target": "", "reason": "article_removed"})
                i += 1
                continue

            phrase_translation, phrase_len = self._match_phrase(tokens, i)
            if phrase_translation:
                if pending_tense:
                    output.append(pending_tense)
                    pending_tense = ""
                output.append(phrase_translation)
                trace.append({"source": " ".join(tokens[i:i + phrase_len]), "target": phrase_translation, "reason": "phrase_match"})
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

    def _match_phrase(self, tokens: list[str], pos: int) -> tuple[str | None, int]:
        max_len = min(4, len(tokens) - pos)
        for size in range(max_len, 1, -1):
            phrase = " ".join(token.lower() for token in tokens[pos:pos + size])
            if phrase in self.lexicon:
                return self.lexicon[phrase], size
        return None, 0

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
