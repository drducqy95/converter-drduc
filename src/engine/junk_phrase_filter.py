#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User-controlled junk phrase filtering for the translation pipeline."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class JunkPhraseRule:
    source: str
    target: str = ""
    clean_text: str = ""
    origin: str = "user_review"


@dataclass(frozen=True, slots=True)
class JunkPhraseFilterResult:
    text: str
    traces: list[dict]


class JunkPhraseFilter:
    """Remove or rewrite user-marked boilerplate outside lexical translation."""

    CONFIG_KEYS = ("ignored_phrases", "junk_phrases", "user_noise_phrases")

    def apply_source(
        self,
        text: str,
        config: dict | None,
        *,
        normalizer: Callable[[str], str] | None = None,
    ) -> JunkPhraseFilterResult:
        rules = self._collect_rules(config, normalizer=normalizer)
        current = str(text or "")
        traces: list[dict] = []
        for rule in rules:
            if not rule.source or rule.source not in current:
                continue
            before = current
            current = current.replace(rule.source, rule.clean_text)
            count = before.count(rule.source)
            if count:
                traces.append(self._trace(rule.source, rule.clean_text, count, "source", rule.origin))
        return JunkPhraseFilterResult(self._cleanup_source(current), traces)

    def apply_target(self, text: str, config: dict | None) -> JunkPhraseFilterResult:
        rules = self._collect_rules(config)
        current = str(text or "")
        traces: list[dict] = []
        for rule in rules:
            target_phrase = rule.target.strip()
            if not target_phrase or target_phrase not in current:
                continue
            before = current
            current = current.replace(target_phrase, rule.clean_text)
            count = before.count(target_phrase)
            if count:
                traces.append(self._trace(target_phrase, rule.clean_text, count, "target", rule.origin))
        return JunkPhraseFilterResult(self._cleanup_target(current), traces)

    def _collect_rules(
        self,
        config: dict | None,
        *,
        normalizer: Callable[[str], str] | None = None,
    ) -> list[JunkPhraseRule]:
        if not isinstance(config, dict):
            return []

        raw_entries: list[object] = []
        for key in self.CONFIG_KEYS:
            value = config.get(key)
            if isinstance(value, list):
                raw_entries.extend(value)

        filters = config.get("translation_filters")
        if isinstance(filters, dict):
            for key in self.CONFIG_KEYS:
                value = filters.get(key)
                if isinstance(value, list):
                    raw_entries.extend(value)

        rules: dict[tuple[str, str], JunkPhraseRule] = {}
        for entry in raw_entries:
            rule = self._normalize_rule(entry)
            if not rule:
                continue
            candidates = [rule]
            if normalizer:
                normalized_source = normalizer(rule.source).strip()
                if normalized_source and normalized_source != rule.source:
                    candidates.append(
                        JunkPhraseRule(
                            source=normalized_source,
                            target=rule.target,
                            clean_text=rule.clean_text,
                            origin=rule.origin,
                        )
                    )
            for candidate in candidates:
                rules[(candidate.source, candidate.target)] = candidate

        return sorted(rules.values(), key=lambda item: max(len(item.source), len(item.target)), reverse=True)

    @staticmethod
    def _normalize_rule(entry: object) -> JunkPhraseRule | None:
        if isinstance(entry, str):
            source = entry.strip()
            return JunkPhraseRule(source=source) if source else None
        if not isinstance(entry, dict):
            return None
        if entry.get("enabled") is False:
            return None

        source = str(
            entry.get("source")
            or entry.get("raw_pattern")
            or entry.get("phrase")
            or entry.get("text")
            or ""
        ).strip()
        target = str(entry.get("target") or entry.get("target_vi") or "").strip()
        clean_text = str(entry.get("clean_text") or entry.get("replacement") or "").strip()
        origin = str(entry.get("origin") or entry.get("source_dict") or "user_review").strip() or "user_review"
        if not source and not target:
            return None
        return JunkPhraseRule(source=source, target=target, clean_text=clean_text, origin=origin)

    @staticmethod
    def _trace(source: str, selected: str, count: int, side: str, origin: str) -> dict:
        return {
            "source": source,
            "selected": selected,
            "candidates": [selected],
            "priority": 88,
            "fallback_level": "junk_phrase_filter",
            "reason": f"user_junk_phrase:{side}:{origin}",
            "occurrences": count,
        }

    @staticmethod
    def _cleanup_source(text: str) -> str:
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\s+([，。！？；：、,.!?:;])", r"\1", text)
        return text.strip()

    @staticmethod
    def _cleanup_target(text: str) -> str:
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def filter_source_junk_phrases(
    text: str,
    config: dict | None,
    *,
    normalizer: Callable[[str], str] | None = None,
) -> JunkPhraseFilterResult:
    return JunkPhraseFilter().apply_source(text, config, normalizer=normalizer)


def filter_target_junk_phrases(text: str, config: dict | None) -> JunkPhraseFilterResult:
    return JunkPhraseFilter().apply_target(text, config)
