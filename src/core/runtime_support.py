#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for querying the compiled SQLite dictionary at runtime."""

from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from src.core.dictionary_entry_filters import looks_like_reference_gloss


DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "_compiled" / "trie_cache.db"


@dataclass(slots=True)
class DictionaryRecord:
    source: str
    target: str
    priority: int
    category: str
    one_mean: bool
    locked: bool
    notes: str
    source_language: str
    target_language: str
    entry_role: str
    metadata: dict

    @property
    def alternatives(self) -> list[str]:
        parts = [part.strip() for part in re.split(r"[;/]", self.target) if part.strip()]
        return parts or [self.target]


@dataclass(slots=True)
class NormalizationRuleRecord:
    source_text: str
    target_text: str
    rule_type: str
    notes: str


@dataclass(slots=True)
class EntryReadingRecord:
    source: str
    pinyin: str
    han_viet_readings: str
    category: str
    entry_role: str


def normalize_pinyin_key(value: str) -> str:
    """Normalize pinyin strings so tone-marked and plain forms match."""
    if not value:
        return ""

    normalized = unicodedata.normalize("NFD", value.strip().lower())
    chars: list[str] = []
    for ch in normalized:
        if unicodedata.category(ch) == "Mn":
            continue
        if ch.isdigit():
            continue
        if ch in {"'", "-", "_", "/", "\\"}:
            chars.append(" ")
            continue
        chars.append(ch)
    return " ".join("".join(chars).split())


class RuntimeDictionaryAccessor:
    """Thin accessor layer over the compiled SQLite database."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Compiled dictionary DB not found: {self.db_path}")
        self._conn: sqlite3.Connection | None = None
        self._normalization_rules: list[NormalizationRuleRecord] | None = None
        self._pinyin_index: dict[str, list[str]] | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    @staticmethod
    def _row_to_record(row: sqlite3.Row | None) -> DictionaryRecord | None:
        if row is None:
            return None
        metadata_json = row["metadata_json"] or ""
        try:
            metadata = json.loads(metadata_json) if metadata_json else {}
        except json.JSONDecodeError:
            metadata = {}
        return DictionaryRecord(
            source=row["source"],
            target=row["target"],
            priority=int(row["priority"]),
            category=row["category"] or "",
            one_mean=bool(row["one_mean"]),
            locked=bool(row["locked"]),
            notes=row["notes"] or "",
            source_language=row["source_language"] or "",
            target_language=row["target_language"] or "",
            entry_role=row["entry_role"] or "",
            metadata=metadata,
        )

    @lru_cache(maxsize=50000)
    def lookup_runtime(self, source: str) -> DictionaryRecord | None:
        cur = self._get_conn().execute(
            """
            SELECT source, target, priority, category, one_mean, locked, notes,
                   source_language, target_language, entry_role, metadata_json
            FROM entries
            WHERE source = ?
            """,
            (source,),
        )
        record = self._row_to_record(cur.fetchone())
        if record and looks_like_reference_gloss(record.category, record.target):
            return None
        return record

    @lru_cache(maxsize=50000)
    def lookup_reference(self, source: str) -> list[DictionaryRecord]:
        cur = self._get_conn().execute(
            """
            SELECT source, target, priority, category, one_mean, locked, notes,
                   source_language, target_language, entry_role, metadata_json
            FROM reference_entries
            WHERE source = ?
            ORDER BY priority DESC, id ASC
            """,
            (source,),
        )
        return [record for row in cur.fetchall() if (record := self._row_to_record(row))]

    def lookup_all(self, source: str) -> list[DictionaryRecord]:
        records: list[DictionaryRecord] = []
        runtime = self.lookup_runtime(source)
        if runtime is not None:
            records.append(runtime)
        records.extend(self.lookup_reference(source))
        return records

    @lru_cache(maxsize=50000)
    def get_entry_readings(self, source: str) -> list[EntryReadingRecord]:
        cur = self._get_conn().execute(
            """
            SELECT source, pinyin, han_viet_readings, category, entry_role
            FROM entry_readings
            WHERE source = ?
            ORDER BY id ASC
            """,
            (source,),
        )
        return [
            EntryReadingRecord(
                source=row["source"],
                pinyin=row["pinyin"] or "",
                han_viet_readings=row["han_viet_readings"] or "",
                category=row["category"] or "",
                entry_role=row["entry_role"] or "",
            )
            for row in cur.fetchall()
        ]

    def get_han_viet_for_text(self, text: str) -> str:
        parts = []
        for ch in text:
            ch_hv = ""
            for r in self.get_entry_readings(ch):
                if r.han_viet_readings:
                    ch_hv = r.han_viet_readings.split(",")[0].strip().title()
                    break
            parts.append(ch_hv or ch)
        return " ".join(parts).strip()

    def get_pinyin_for_text(self, text: str) -> str:
        parts = []
        for ch in text:
            ch_py = ""
            for r in self.get_entry_readings(ch):
                if r.pinyin:
                    ch_py = r.pinyin.split(",")[0].strip().capitalize()
                    break
            parts.append(ch_py or ch)
        return " ".join(parts).strip()


    def get_normalization_rules(self) -> list[NormalizationRuleRecord]:
        if self._normalization_rules is not None:
            return self._normalization_rules

        cache_key = _shared_db_cache_key(self.db_path)
        cached = _SHARED_NORMALIZATION_RULES.get(cache_key)
        if cached is not None:
            self._normalization_rules = cached
            return cached

        cur = self._get_conn().execute(
            """
            SELECT source_text, target_text, rule_type, notes
            FROM normalization_rules
            ORDER BY LENGTH(source_text) DESC, id ASC
            """
        )
        self._normalization_rules = [
            NormalizationRuleRecord(
                source_text=row["source_text"],
                target_text=row["target_text"] or "",
                rule_type=row["rule_type"] or "replace",
                notes=row["notes"] or "",
            )
            for row in cur.fetchall()
        ]
        _SHARED_NORMALIZATION_RULES[cache_key] = self._normalization_rules
        return self._normalization_rules

    def build_pinyin_index(self) -> dict[str, list[str]]:
        if self._pinyin_index is not None:
            return self._pinyin_index

        cache_key = _shared_db_cache_key(self.db_path)
        cached = _SHARED_PINYIN_INDEX.get(cache_key)
        if cached is not None:
            self._pinyin_index = cached
            return cached

        index: dict[str, list[str]] = {}
        cur = self._get_conn().execute(
            """
            SELECT source, pinyin
            FROM entry_readings
            WHERE pinyin IS NOT NULL AND pinyin != ''
            ORDER BY LENGTH(source) DESC, id ASC
            """
        )
        for row in cur.fetchall():
            key = normalize_pinyin_key(row["pinyin"] or "")
            if not key:
                continue
            index.setdefault(key, [])
            if row["source"] not in index[key]:
                index[key].append(row["source"])
        self._pinyin_index = index
        _SHARED_PINYIN_INDEX[cache_key] = index
        return index

    def lookup_by_pinyin(self, pinyin: str) -> list[str]:
        return self.build_pinyin_index().get(normalize_pinyin_key(pinyin), [])

    def search_reference_entries(
        self,
        *,
        source_language: str | None = None,
        target_language: str | None = None,
        category_prefix: str | None = None,
    ) -> Iterable[DictionaryRecord]:
        conditions: list[str] = []
        params: list[str] = []
        if source_language:
            conditions.append("source_language = ?")
            params.append(source_language)
        if target_language:
            conditions.append("target_language = ?")
            params.append(target_language)
        if category_prefix:
            conditions.append("category LIKE ?")
            params.append(f"{category_prefix}%")

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        cur = self._get_conn().execute(
            f"""
            SELECT source, target, priority, category, one_mean, locked, notes,
                   source_language, target_language, entry_role, metadata_json
            FROM reference_entries
            {where}
            ORDER BY LENGTH(source) DESC, priority DESC, id ASC
            """,
            params,
        )
        for row in cur.fetchall():
            record = self._row_to_record(row)
            if record is not None:
                yield record

    def search_entries(self, query: str, *, limit: int = 25) -> list[DictionaryRecord]:
        normalized = query.strip()
        if not normalized:
            return []

        source_prefix = f"{normalized}%"
        source_contains = f"%{normalized}%"
        target_contains = f"%{normalized}%"
        cur = self._get_conn().execute(
            """
            SELECT source, target, priority, category, one_mean, locked, notes,
                   source_language, target_language, entry_role, metadata_json,
                   scope_rank, match_rank
            FROM (
                SELECT source, target, priority, category, one_mean, locked, notes,
                       source_language, target_language, entry_role, metadata_json,
                       0 AS scope_rank,
                       CASE
                           WHEN source = ? THEN 0
                           WHEN source LIKE ? THEN 1
                           WHEN target LIKE ? THEN 2
                           WHEN source LIKE ? THEN 3
                           ELSE 4
                       END AS match_rank
                FROM entries
                WHERE source = ? OR source LIKE ? OR target LIKE ? OR source LIKE ?
                UNION ALL
                SELECT source, target, priority, category, one_mean, locked, notes,
                       source_language, target_language, entry_role, metadata_json,
                       1 AS scope_rank,
                       CASE
                           WHEN source = ? THEN 0
                           WHEN source LIKE ? THEN 1
                           WHEN target LIKE ? THEN 2
                           WHEN source LIKE ? THEN 3
                           ELSE 4
                       END AS match_rank
                FROM reference_entries
                WHERE source = ? OR source LIKE ? OR target LIKE ? OR source LIKE ?
            )
            ORDER BY match_rank ASC, scope_rank ASC, priority DESC, LENGTH(source) ASC, source ASC
            LIMIT ?
            """,
            (
                normalized,
                source_prefix,
                target_contains,
                source_contains,
                normalized,
                source_prefix,
                target_contains,
                source_contains,
                normalized,
                source_prefix,
                target_contains,
                source_contains,
                normalized,
                source_prefix,
                target_contains,
                source_contains,
                limit,
            ),
        )

        results: list[DictionaryRecord] = []
        seen: set[tuple[str, str, int, str, str]] = set()
        for row in cur.fetchall():
            record = self._row_to_record(row)
            if record is None:
                continue
            if row["scope_rank"] == 0 and looks_like_reference_gloss(record.category, record.target):
                continue
            key = (
                record.source,
                record.target,
                record.priority,
                record.category,
                record.entry_role,
            )
            if key in seen:
                continue
            seen.add(key)
            results.append(record)
        return results


_SHARED_PINYIN_INDEX: dict[str, dict[str, list[str]]] = {}
_SHARED_NORMALIZATION_RULES: dict[str, list[NormalizationRuleRecord]] = {}


def _shared_db_cache_key(db_path: Path) -> str:
    path = db_path.resolve()
    stat = path.stat()
    return f"{path}:{stat.st_mtime_ns}:{stat.st_size}"
