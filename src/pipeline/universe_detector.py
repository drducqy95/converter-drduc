#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Standalone universe detection with fingerprint-based scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from src.pipeline.han_variants import han_variants

if TYPE_CHECKING:
    from src.pipeline.term_bank import TermBank


DEFAULT_FINGERPRINTS_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "term_bank" / "universes" / "fingerprints.json"
)
DEFAULT_CONFIG = {
    "multi_universe_threshold": 0.65,
    "min_confidence_for_active": 0.4,
    "fingerprint_base_divisor": 2.0,
    "canonical_char_boost": 3.0,
    "co_occurrence_pair_boost": 5.0,
}


@dataclass(frozen=True)
class UniverseSignal:
    """Detection result for one universe."""

    universe_id: str
    confidence: float
    matched_fingerprints: list[str] = field(default_factory=list)
    matched_characters: list[str] = field(default_factory=list)
    work: str = ""
    franchise: str = ""


@dataclass
class UniverseContext:
    """Aggregated universe detection result."""

    active_universes: list[str]
    signals: list[UniverseSignal]
    primary_universe: str | None
    is_multi_universe: bool
    is_unknown: bool


class UniverseDetector:
    """Detect active story universes from weighted fingerprints."""

    def __init__(
        self,
        fingerprints_path: Path | str | None = None,
        *,
        term_bank: "TermBank | None" = None,
    ):
        self._fp_path = Path(fingerprints_path or DEFAULT_FINGERPRINTS_PATH)
        self._fingerprints: dict[str, dict] | None = None
        self._config: dict = dict(DEFAULT_CONFIG)
        self._term_bank = term_bank

    @property
    def fingerprints(self) -> dict[str, dict]:
        if self._fingerprints is None:
            self._fingerprints, self._config = self._load_fingerprints()
        return self._fingerprints

    @property
    def config(self) -> dict:
        if self._fingerprints is None:
            self._fingerprints, self._config = self._load_fingerprints()
        return self._config

    def detect(self, text: str) -> UniverseContext:
        """Detect universe signals in full text using weighted fingerprints."""

        if not text:
            return UniverseContext([], [], None, False, True)

        signals = [
            self._score_universe(text, universe_id, fp_data)
            for universe_id, fp_data in self.fingerprints.items()
        ]
        signals = [signal for signal in signals if signal.confidence > 0.0]
        signals.sort(key=lambda signal: signal.confidence, reverse=True)

        active_threshold = float(self.config.get("min_confidence_for_active") or 0.4)
        multi_threshold = float(self.config.get("multi_universe_threshold") or 0.65)
        active_universes = [signal.universe_id for signal in signals if signal.confidence >= active_threshold]
        strong_universes = [signal.universe_id for signal in signals if signal.confidence >= multi_threshold]
        primary = signals[0].universe_id if signals and signals[0].confidence >= active_threshold else None
        return UniverseContext(
            active_universes=active_universes,
            signals=signals,
            primary_universe=primary,
            is_multi_universe=len(strong_universes) >= 2,
            is_unknown=primary is None,
        )

    def detect_sentence_level(
        self,
        sentences: list[str],
        *,
        context_radius: int = 1,
    ) -> list[UniverseContext]:
        """Detect universe context for each sentence using a local sentence window."""

        radius = max(int(context_radius), 0)
        results: list[UniverseContext] = []
        for index, _sentence in enumerate(sentences):
            start = max(0, index - radius)
            end = min(len(sentences), index + radius + 1)
            results.append(self.detect("".join(sentences[start:end])))
        return results

    def get_universe_info(self, universe_id: str) -> dict | None:
        return self.fingerprints.get(universe_id)

    def _score_universe(self, text: str, universe_id: str, fp_data: dict) -> UniverseSignal:
        score = 0.0
        matched_fingerprints: list[str] = []
        matched_characters: list[str] = []

        for item in fp_data.get("fingerprint_terms") or []:
            if not isinstance(item, dict):
                continue
            term = str(item.get("term") or "").strip()
            variants = self._variants_for_item(item)
            if not term or not variants:
                continue
            if self._matches_any(text, variants):
                weight = float(item.get("weight") or 1.0)
                score += weight
                matched_fingerprints.append(term)

        canonical_boost = float(self.config.get("canonical_char_boost") or 3.0)
        for character in fp_data.get("canonical_chars") or []:
            character_text = str(character or "").strip()
            if not character_text:
                continue
            if self._matches_any(text, han_variants(character_text)):
                score += canonical_boost
                matched_characters.append(character_text)

        pair_boost = float(self.config.get("co_occurrence_pair_boost") or 5.0)
        for seed in fp_data.get("co_occurrence_seeds") or []:
            if not isinstance(seed, dict):
                continue
            pair = seed.get("pair") or []
            if len(pair) != 2:
                continue
            left, right = str(pair[0] or ""), str(pair[1] or "")
            if self._matches_any(text, han_variants(left)) and self._matches_any(text, han_variants(right)):
                score += float(seed.get("confidence") or 0.8) * pair_boost

        for exclusion in fp_data.get("exclusion_terms") or []:
            term = str(exclusion or "").strip()
            if term and self._matches_any(text, han_variants(term)):
                score = max(0.0, score - 1.0)

        base_divisor = float(self.config.get("fingerprint_base_divisor") or 2.0)
        confidence = round(score / (score + base_divisor), 4) if score > 0 else 0.0
        return UniverseSignal(
            universe_id=universe_id,
            confidence=confidence,
            matched_fingerprints=list(dict.fromkeys(matched_fingerprints)),
            matched_characters=list(dict.fromkeys(matched_characters)),
            work=str(fp_data.get("work") or ""),
            franchise=str(fp_data.get("franchise") or ""),
        )

    def _load_fingerprints(self) -> tuple[dict[str, dict], dict]:
        if not self._fp_path.exists():
            return {}, dict(DEFAULT_CONFIG)
        payload = json.loads(self._fp_path.read_text(encoding="utf-8"))
        universes = payload.get("universes") if isinstance(payload, dict) else {}
        config = dict(DEFAULT_CONFIG)
        if isinstance(payload, dict) and isinstance(payload.get("config"), dict):
            config.update(payload["config"])
        if not isinstance(universes, dict):
            return {}, config
        return universes, config

    @staticmethod
    def _variants_for_item(item: dict) -> list[str]:
        variants = [str(variant or "").strip() for variant in (item.get("variants") or []) if str(variant or "").strip()]
        term = str(item.get("term") or "").strip()
        variants.extend(han_variants(term))
        return list(dict.fromkeys(variant for variant in variants if len(variant) >= 2))

    @staticmethod
    def _matches_any(text: str, variants: list[str]) -> bool:
        return any(variant and variant in text for variant in variants)
