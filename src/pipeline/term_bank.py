#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cross-project and cross-universe proper-name and terminology knowledge base."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from src.pipeline.universe import slugify_universe_id


DEFAULT_TERM_BANK_ROOT = Path(__file__).resolve().parents[2] / "data" / "term_bank"
ENTITY_TYPES = {
    "person",
    "location",
    "organization",
    "realm",
    "technique",
    "weapon",
    "item",
    "title",
    "creature",
    "faction",
    "term",
}
PROPER_ENTITY_TYPES = {"person", "location", "organization"}
ACTIVE_STATUSES = {"approved", "locked", "active"}


@dataclass(slots=True)
class TermBankRecord:
    source: str
    target: str
    entity_type: str = "term"
    scope: str = "global"
    category: str = ""
    confidence: float = 0.9
    status: str = "approved"
    source_dict: str = "term_bank"
    universe: str = ""
    work: str = ""
    franchise: str = ""
    notes: str = ""
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    context_markers: list[str] = field(default_factory=list)
    co_occurring_entities: list[str] = field(default_factory=list)
    version: int = 1

    def __post_init__(self) -> None:
        self.universe = slugify_universe_id(self.universe)

    @property
    def active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    @property
    def rank(self) -> tuple[int, float, int]:
        scope_rank = {"private": 3, "global": 2, "universe": 1}.get(self.scope, 0)
        return scope_rank, self.confidence, len(self.source)


class TermBank:
    """Load global, universe-specific, and project-private term records."""

    def __init__(
        self,
        *,
        root: str | Path | None = None,
        project_id: str | None = None,
        project_dir: str | Path | None = None,
    ):
        self.root = Path(root or DEFAULT_TERM_BANK_ROOT)
        self.project_id = (project_id or "").strip()
        self.project_dir = Path(project_dir) if project_dir else None
        self._records: list[TermBankRecord] | None = None
        self._by_source: dict[str, list[TermBankRecord]] | None = None

    def set_project_context(self, *, project_id: str | None = None, project_dir: str | Path | None = None) -> None:
        next_project_id = (project_id or "").strip()
        next_project_dir = Path(project_dir) if project_dir else None
        if next_project_id == self.project_id and next_project_dir == self.project_dir:
            return
        self.project_id = next_project_id
        self.project_dir = next_project_dir
        self._records = None
        self._by_source = None

    def lookup(
        self,
        source: str,
        *,
        entity_type: str | None = None,
        include_inactive: bool = False,
    ) -> list[TermBankRecord]:
        normalized = source.strip()
        if not normalized:
            return []
        records = list(self._source_index().get(normalized, []))
        if entity_type:
            records = [record for record in records if record.entity_type == entity_type]
        if not include_inactive:
            records = [record for record in records if record.active]
        return sorted(records, key=lambda record: record.rank, reverse=True)

    def rank_with_context(
        self,
        source: str,
        *,
        context_window: str = "",
        entity_type: str | None = None,
        active_universes: list[str] | None = None,
        include_inactive: bool = False,
    ) -> list[tuple[TermBankRecord, float]]:
        """Return candidate records with deterministic context scores.

        The score intentionally keeps a global record ahead of a universe record
        when no universe markers are present. Universe-specific records win only
        when the local context or caller-provided active universe supports them.
        """

        candidates = self.lookup(source, entity_type=entity_type, include_inactive=include_inactive)
        if not candidates:
            return []
        active = {slugify_universe_id(item) for item in (active_universes or []) if item}
        ranked = [
            (record, self._context_score(record, context_window=context_window, active_universes=active))
            for record in candidates
        ]
        return sorted(ranked, key=lambda item: (item[1], item[0].rank), reverse=True)

    def lookup_with_context(
        self,
        source: str,
        *,
        context_window: str = "",
        entity_type: str | None = None,
        active_universes: list[str] | None = None,
        include_inactive: bool = False,
    ) -> list[TermBankRecord]:
        """Disambiguate records for a source string using local context."""

        return [
            record
            for record, _score in self.rank_with_context(
                source,
                context_window=context_window,
                entity_type=entity_type,
                active_universes=active_universes,
                include_inactive=include_inactive,
            )
        ]

    def best(self, source: str, *, entity_type: str | None = None) -> TermBankRecord | None:
        records = self.lookup(source, entity_type=entity_type)
        return records[0] if records else None

    def detect_universe(self, text: str, *, threshold: float = 0.12) -> list[tuple[str, float]]:
        """Detect active universes from fingerprints and co-occurrence markers."""

        if not text:
            return []
        scores: dict[str, float] = {}
        for record in self.iter_active():
            if record.scope != "universe":
                continue
            universe = slugify_universe_id(record.universe)
            if not universe:
                continue
            marker_score = self._universe_marker_score(record, text)
            if marker_score <= 0:
                continue
            scores[universe] = scores.get(universe, 0.0) + marker_score

        ranked: list[tuple[str, float]] = []
        for universe, score in scores.items():
            confidence = min(0.99, score / (score + 2.0))
            if confidence >= threshold:
                ranked.append((universe, round(confidence, 4)))
        return sorted(ranked, key=lambda item: item[1], reverse=True)

    def get_universe_glossary(self, universe: str) -> list[TermBankRecord]:
        normalized = slugify_universe_id(universe)
        if not normalized:
            return []
        return sorted(
            (
                record
                for record in self.iter_active()
                if slugify_universe_id(record.universe) == normalized
            ),
            key=lambda record: record.rank,
            reverse=True,
        )

    def suggest_enrichment(self, entity: object, *, context: str = "") -> TermBankRecord:
        """Build a review-ready term-bank record from an entity-like object."""

        detected = self.detect_universe(context, threshold=0.2)
        universe = slugify_universe_id(getattr(entity, "universe", "") or (detected[0][0] if len(detected) == 1 else ""))
        source = str(getattr(entity, "source", "") or "").strip()
        target = str(getattr(entity, "target", "") or "").strip()
        entity_type = str(getattr(entity, "entity_type", "") or "term").strip() or "term"
        confidence = float(getattr(entity, "confidence", 0.75) or 0.75)
        context_markers = self._extract_present_markers(context, universe=universe)
        return TermBankRecord(
            source=source,
            target=target,
            entity_type=entity_type if entity_type in ENTITY_TYPES else "term",
            scope="private",
            confidence=min(max(confidence, 0.0), 1.0),
            status="reviewed",
            source_dict="entity_enrichment",
            universe=universe,
            work=str(getattr(entity, "work", "") or ""),
            notes="Prepared by entity enrichment; requires human approval before promotion.",
            tags=["entity_enrichment", entity_type],
            context_markers=context_markers,
        )

    def reload_universe(self, universe: str | None = None) -> None:
        """Clear cached records after a JSONL update.

        The current loader is lightweight enough to reload the whole bank. The
        optional universe argument is accepted so UI code can use a stable API.
        """

        _ = universe
        self._records = None
        self._by_source = None

    def iter_active(self) -> Iterable[TermBankRecord]:
        return (record for record in self.records if record.active)

    @property
    def records(self) -> list[TermBankRecord]:
        if self._records is None:
            self._records = self._load_records()
        return self._records

    def _source_index(self) -> dict[str, list[TermBankRecord]]:
        if self._by_source is None:
            by_source: dict[str, list[TermBankRecord]] = {}
            for record in self.records:
                by_source.setdefault(record.source, []).append(record)
                for alias in record.aliases:
                    if alias:
                        by_source.setdefault(alias, []).append(record)
            self._by_source = by_source
        return self._by_source

    def _load_records(self) -> list[TermBankRecord]:
        records: list[TermBankRecord] = []
        for path, scope in self._iter_record_files():
            records.extend(self._read_jsonl(path, scope=scope))
        return records

    def _iter_record_files(self) -> Iterable[tuple[Path, str]]:
        global_dir = self.root / "global"
        if global_dir.is_dir():
            for path in sorted(global_dir.glob("*.jsonl")):
                yield path, "global"

        universes_dir = self.root / "universes"
        if universes_dir.is_dir():
            for universe_dir in sorted(path for path in universes_dir.iterdir() if path.is_dir()):
                for path in sorted(universe_dir.glob("*.jsonl")):
                    yield path, "universe"

        if self.project_id:
            project_bank_dir = self.root / "projects" / self.project_id
            if project_bank_dir.is_dir():
                for path in sorted(project_bank_dir.glob("*.jsonl")):
                    yield path, "private"

        if self.project_dir:
            local_bank_dir = self.project_dir / "knowledge"
            if local_bank_dir.is_dir():
                for path in sorted(local_bank_dir.glob("*.jsonl")):
                    yield path, "private"

    @staticmethod
    def _read_jsonl(path: Path, *, scope: str) -> list[TermBankRecord]:
        rows: list[TermBankRecord] = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid term bank JSONL at {path}:{line_no}: {exc}") from exc
            if not isinstance(payload, dict):
                continue
            record = TermBank._record_from_payload(payload, scope=scope, source_file=path.name)
            if record is not None:
                rows.append(record)
        return rows

    @staticmethod
    def _record_from_payload(payload: dict, *, scope: str, source_file: str) -> TermBankRecord | None:
        source = str(payload.get("source") or "").strip()
        target = str(payload.get("target") or "").strip()
        if not source or not target:
            return None
        entity_type = str(payload.get("entity_type") or payload.get("type") or "term").strip() or "term"
        aliases = payload.get("aliases") or []
        tags = payload.get("tags") or []
        context_markers = payload.get("context_markers") or []
        co_occurring_entities = payload.get("co_occurring_entities") or []
        return TermBankRecord(
            source=source,
            target=target,
            entity_type=entity_type,
            scope=str(payload.get("scope") or scope),
            category=str(payload.get("category") or ""),
            confidence=float(payload.get("confidence") or 0.9),
            status=str(payload.get("status") or "approved"),
            source_dict=str(payload.get("source_dict") or f"{scope}_term_bank:{source_file}"),
            universe=str(payload.get("universe") or ""),
            work=str(payload.get("work") or ""),
            franchise=str(payload.get("franchise") or ""),
            notes=str(payload.get("notes") or ""),
            aliases=[str(item).strip() for item in aliases if str(item).strip()] if isinstance(aliases, list) else [],
            tags=[str(item).strip() for item in tags if str(item).strip()] if isinstance(tags, list) else [],
            context_markers=[
                str(item).strip()
                for item in context_markers
                if str(item).strip()
            ] if isinstance(context_markers, list) else [],
            co_occurring_entities=[
                str(item).strip()
                for item in co_occurring_entities
                if str(item).strip()
            ] if isinstance(co_occurring_entities, list) else [],
            version=int(payload.get("version") or 1),
        )

    @staticmethod
    def _context_score(
        record: TermBankRecord,
        *,
        context_window: str,
        active_universes: set[str],
    ) -> float:
        contextual = 0.0
        universe_key = slugify_universe_id(record.universe)
        if universe_key and universe_key in active_universes:
            contextual += 4.0
        if context_window:
            contextual += sum(1.0 for marker in record.context_markers if marker and marker in context_window)
            contextual += sum(2.0 for marker in record.co_occurring_entities if marker and marker in context_window)
            if record.work and record.work in context_window:
                contextual += 1.5
            if record.franchise and record.franchise in context_window:
                contextual += 1.0
            contextual += sum(0.5 for alias in record.aliases if alias and alias in context_window)

        scope_bias = {"private": 0.30, "global": 0.20, "universe": 0.10}.get(record.scope, 0.0)
        status_bias = 0.05 if record.status == "approved" else 0.0
        return contextual * 10.0 + scope_bias + status_bias + record.confidence

    @staticmethod
    def _universe_marker_score(record: TermBankRecord, text: str) -> float:
        score = 0.0
        record_present = record.source in text
        for marker in record.context_markers:
            if marker and marker in text and (record_present or record.entity_type not in PROPER_ENTITY_TYPES):
                score += 1.5
        for marker in record.co_occurring_entities:
            if marker and marker in text and record_present:
                score += 2.0
        if record.entity_type not in PROPER_ENTITY_TYPES and record_present:
            score += 1.0
        elif record_present and (record.context_markers or record.co_occurring_entities):
            score += 0.5
        return score

    def _extract_present_markers(self, text: str, *, universe: str) -> list[str]:
        if not text or not universe:
            return []
        markers: list[str] = []
        for record in self.get_universe_glossary(universe):
            for marker in [record.source, *record.aliases, *record.context_markers, *record.co_occurring_entities]:
                if marker and marker in text and marker not in markers:
                    markers.append(marker)
                if len(markers) >= 8:
                    return markers
        return markers
