#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cross-project proper-name and terminology knowledge base."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


DEFAULT_TERM_BANK_ROOT = Path(__file__).resolve().parents[2] / "data" / "term_bank"
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

    @property
    def active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    @property
    def rank(self) -> tuple[int, float, int]:
        scope_rank = 2 if self.scope == "private" else 1
        return scope_rank, self.confidence, len(self.source)


class TermBank:
    """Load Global and project-private proper-name/term records from JSONL files."""

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

    def lookup(self, source: str, *, entity_type: str | None = None, include_inactive: bool = False) -> list[TermBankRecord]:
        normalized = source.strip()
        if not normalized:
            return []
        records = list(self._source_index().get(normalized, []))
        if entity_type:
            records = [record for record in records if record.entity_type == entity_type]
        if not include_inactive:
            records = [record for record in records if record.active]
        return sorted(records, key=lambda record: record.rank, reverse=True)

    def best(self, source: str, *, entity_type: str | None = None) -> TermBankRecord | None:
        records = self.lookup(source, entity_type=entity_type)
        return records[0] if records else None

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
        )
