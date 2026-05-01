#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for querying and updating the compiled SQLite dictionary at runtime."""

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


DEFAULT_DICT_ROOT = Path(__file__).resolve().parents[2] / "data" / "dictionaries"
DEFAULT_DB_PATH = DEFAULT_DICT_ROOT / "_compiled" / "trie_cache.db"

RECORD_BASE_COLUMNS = """
    source,
    target,
    priority,
    category,
    one_mean,
    locked,
    notes,
    source_file,
    source_language,
    target_language,
    entry_role,
    metadata_json,
    pos_tag,
    pos_sub,
    entity_type,
    pinyin,
    traditional,
    is_function_word,
    luat_nhan_trigger,
    reorder_role,
    cultural_origin,
    genre_affinity,
    register_level
"""


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
    record_id: int | None = None
    table_name: str = ""
    source_file: str = ""
    pos_tag: str | None = None
    pos_sub: str | None = None
    entity_type: str | None = None
    pinyin: str | None = None
    traditional: str | None = None
    is_function_word: int = 0
    luat_nhan_trigger: int = 0
    reorder_role: str | None = None
    cultural_origin: str | None = None
    genre_affinity: str | None = None
    register_level: str | None = None

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
        self.db_path = Path(db_path or DEFAULT_DB_PATH).expanduser().resolve()
        if not self.db_path.exists():
            raise FileNotFoundError(f"Compiled dictionary DB not found: {self.db_path}")
        self.dict_root = self._resolve_dict_root(self.db_path)
        self._conn: sqlite3.Connection | None = None
        self._normalization_rules: list[NormalizationRuleRecord] | None = None
        self._pinyin_index: dict[str, list[str]] | None = None

    @staticmethod
    def _resolve_dict_root(db_path: Path) -> Path:
        if db_path.parent.name == "_compiled":
            return db_path.parent.parent.resolve()
        return DEFAULT_DICT_ROOT.resolve()

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
        keys = set(row.keys())
        metadata_json = row["metadata_json"] if "metadata_json" in keys else ""
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
            record_id=int(row["id"]) if "id" in keys and row["id"] is not None else None,
            table_name=row["table_name"] if "table_name" in keys and row["table_name"] else "",
            source_file=row["source_file"] if "source_file" in keys else "",
            pos_tag=row["pos_tag"] if "pos_tag" in keys else None,
            pos_sub=row["pos_sub"] if "pos_sub" in keys else None,
            entity_type=row["entity_type"] if "entity_type" in keys else None,
            pinyin=row["pinyin"] if "pinyin" in keys else None,
            traditional=row["traditional"] if "traditional" in keys else None,
            is_function_word=int(row["is_function_word"] or 0) if "is_function_word" in keys else 0,
            luat_nhan_trigger=int(row["luat_nhan_trigger"] or 0) if "luat_nhan_trigger" in keys else 0,
            reorder_role=row["reorder_role"] if "reorder_role" in keys else None,
            cultural_origin=row["cultural_origin"] if "cultural_origin" in keys else None,
            genre_affinity=row["genre_affinity"] if "genre_affinity" in keys else None,
            register_level=row["register_level"] if "register_level" in keys else None,
        )

    @staticmethod
    def _select_columns(table_name: str) -> str:
        record_id = "rowid AS id" if table_name == "entries" else "id"
        return f"SELECT {record_id}, {RECORD_BASE_COLUMNS}, '{table_name}' AS table_name FROM {table_name}"

    def _invalidate_caches(self):
        self.lookup_runtime.cache_clear()
        self.lookup_reference.cache_clear()
        self.get_entry_readings.cache_clear()
        self._normalization_rules = None
        self._pinyin_index = None
        _SHARED_NORMALIZATION_RULES.pop(_shared_db_cache_key(self.db_path), None)
        _SHARED_PINYIN_INDEX.pop(_shared_db_cache_key(self.db_path), None)

    @lru_cache(maxsize=50000)
    def lookup_runtime(self, source: str) -> DictionaryRecord | None:
        cur = self._get_conn().execute(
            f"""
            {self._select_columns("entries")}
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
            f"""
            {self._select_columns("reference_entries")}
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

    def get_record(self, table_name: str, record_id: int) -> DictionaryRecord | None:
        if table_name not in {"entries", "reference_entries"}:
            raise ValueError(f"Unsupported table_name: {table_name}")
        id_column = "rowid" if table_name == "entries" else "id"
        row = self._get_conn().execute(
            f"""
            {self._select_columns(table_name)}
            WHERE {id_column} = ?
            """,
            (record_id,),
        ).fetchone()
        return self._row_to_record(row)

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
            for record in self.get_entry_readings(ch):
                if record.han_viet_readings:
                    ch_hv = re.split(r"[|,;/]", record.han_viet_readings, maxsplit=1)[0].strip().title()
                    break
            parts.append(ch_hv or ch)
        return " ".join(parts).strip()

    def get_pinyin_for_text(self, text: str) -> str:
        parts = []
        for ch in text:
            ch_py = ""
            for record in self.get_entry_readings(ch):
                if record.pinyin:
                    ch_py = record.pinyin.split(",")[0].strip().capitalize()
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
            {self._select_columns("reference_entries")}
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
            f"""
            SELECT *
            FROM (
                SELECT rowid AS id, {RECORD_BASE_COLUMNS}, 'entries' AS table_name,
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
                SELECT id, {RECORD_BASE_COLUMNS}, 'reference_entries' AS table_name,
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
        seen: set[tuple[str, str, int, str, str, str]] = set()
        for row in cur.fetchall():
            record = self._row_to_record(row)
            if record is None:
                continue
            if record.table_name == "entries" and looks_like_reference_gloss(record.category, record.target):
                continue
            key = (
                record.source,
                record.target,
                record.priority,
                record.category,
                record.entry_role,
                record.table_name,
            )
            if key in seen:
                continue
            seen.add(key)
            results.append(record)
        return results

    def list_entries(
        self,
        *,
        query: str = "",
        source_dict: str | None = None,
        pos_tag: str | None = None,
        entity_type: str | None = None,
        table_name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[DictionaryRecord], int]:
        selected_tables = [table_name] if table_name in {"entries", "reference_entries"} else ["entries", "reference_entries"]
        union_sql: list[str] = []
        params: list[object] = []

        for current_table in selected_tables:
            conditions: list[str] = []
            if query.strip():
                like_query = f"%{query.strip()}%"
                source_prefix = f"{query.strip()}%"
                conditions.append("(source = ? OR source LIKE ? OR source LIKE ? OR target LIKE ? OR notes LIKE ?)")
                params.extend([query.strip(), source_prefix, like_query, like_query, like_query])
            if source_dict:
                conditions.append("category = ?")
                params.append(source_dict)
            if pos_tag:
                conditions.append("pos_tag = ?")
                params.append(pos_tag)
            if entity_type:
                conditions.append("entity_type = ?")
                params.append(entity_type)
            where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            union_sql.append(f"{self._select_columns(current_table)} {where}")

        count_sql = f"SELECT COUNT(*) AS total FROM ({' UNION ALL '.join(union_sql)})"
        total = int(self._get_conn().execute(count_sql, params).fetchone()["total"])
        rows = self._get_conn().execute(
            f"""
            SELECT *
            FROM ({' UNION ALL '.join(union_sql)})
            ORDER BY locked DESC, priority DESC, LENGTH(source) ASC, source ASC, record_id ASC
            LIMIT ? OFFSET ?
            """.replace("record_id", "id"),
            [*params, limit, offset],
        ).fetchall()
        return [record for row in rows if (record := self._row_to_record(row))], total

    def get_filter_values(self) -> dict[str, list[str]]:
        conn = self._get_conn()
        categories = [
            row["value"]
            for row in conn.execute(
                """
                SELECT DISTINCT category AS value
                FROM (
                    SELECT category FROM entries
                    UNION
                    SELECT category FROM reference_entries
                )
                WHERE value IS NOT NULL AND TRIM(value) != ''
                ORDER BY value
                """
            ).fetchall()
        ]
        pos_tags = [
            row["value"]
            for row in conn.execute(
                """
                SELECT DISTINCT pos_tag AS value
                FROM (
                    SELECT pos_tag FROM entries
                    UNION
                    SELECT pos_tag FROM reference_entries
                )
                WHERE value IS NOT NULL AND TRIM(value) != ''
                ORDER BY value
                """
            ).fetchall()
        ]
        entity_types = [
            row["value"]
            for row in conn.execute(
                """
                SELECT DISTINCT entity_type AS value
                FROM (
                    SELECT entity_type FROM entries
                    UNION
                    SELECT entity_type FROM reference_entries
                )
                WHERE value IS NOT NULL AND TRIM(value) != ''
                ORDER BY value
                """
            ).fetchall()
        ]
        return {
            "categories": categories,
            "pos_tags": pos_tags,
            "entity_types": entity_types,
            "tables": ["entries", "reference_entries"],
        }

    def get_dictionary_stats(self) -> dict[str, object]:
        conn = self._get_conn()
        runtime_row = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN pos_tag IS NOT NULL AND TRIM(pos_tag) != '' THEN 1 ELSE 0 END) AS pos_total,
                SUM(CASE WHEN pinyin IS NOT NULL AND TRIM(pinyin) != '' THEN 1 ELSE 0 END) AS pinyin_total,
                SUM(CASE WHEN entity_type IS NOT NULL AND TRIM(entity_type) != '' THEN 1 ELSE 0 END) AS entity_total
            FROM entries
            """
        ).fetchone()
        reference_total = int(conn.execute("SELECT COUNT(*) FROM reference_entries").fetchone()[0])
        metadata_rows = conn.execute("SELECT key, value FROM metadata").fetchall()
        metadata = {row["key"]: row["value"] for row in metadata_rows}

        runtime_total = int(runtime_row["total"] or 0)
        pos_total = int(runtime_row["pos_total"] or 0)
        pinyin_total = int(runtime_row["pinyin_total"] or 0)
        entity_total = int(runtime_row["entity_total"] or 0)
        pos_coverage = round((pos_total / runtime_total) * 100, 2) if runtime_total else 0.0
        pinyin_coverage = round((pinyin_total / runtime_total) * 100, 2) if runtime_total else 0.0

        return {
            "runtime_total": runtime_total,
            "reference_total": reference_total,
            "total": runtime_total + reference_total,
            "pos_total": pos_total,
            "pinyin_total": pinyin_total,
            "entity_total": entity_total,
            "pos_coverage_pct": pos_coverage,
            "pinyin_coverage_pct": pinyin_coverage,
            "compiled_at": metadata.get("compiled_at"),
            "entry_readings_total": int(metadata.get("entry_readings_count", "0") or 0),
            "metadata": metadata,
        }

    def update_entry(self, table_name: str, record_id: int, updates: dict[str, object]) -> DictionaryRecord:
        if table_name not in {"entries", "reference_entries"}:
            raise ValueError(f"Unsupported table_name: {table_name}")

        current = self.get_record(table_name, record_id)
        if current is None:
            raise ValueError(f"Dictionary record not found: {table_name}:{record_id}")

        assignments: list[str] = []
        params: list[object] = []
        normalized_updates = self._normalize_updates(updates)
        for key, value in normalized_updates.items():
            assignments.append(f"{key} = ?")
            params.append(value)
        if assignments:
            id_column = "rowid" if table_name == "entries" else "id"
            self._get_conn().execute(
                f"UPDATE {table_name} SET {', '.join(assignments)} WHERE {id_column} = ?",
                [*params, record_id],
            )
            self._get_conn().commit()

        updated = self.get_record(table_name, record_id)
        if updated is None:
            raise ValueError(f"Dictionary record disappeared after update: {table_name}:{record_id}")

        self._sync_entry_reading(current, updated)
        self._invalidate_caches()
        return updated

    @staticmethod
    def _normalize_updates(updates: dict[str, object]) -> dict[str, object]:
        allowed = {
            "source",
            "target",
            "priority",
            "notes",
            "locked",
            "metadata_json",
            "pos_tag",
            "pos_sub",
            "entity_type",
            "pinyin",
            "traditional",
            "is_function_word",
            "luat_nhan_trigger",
            "reorder_role",
            "cultural_origin",
            "genre_affinity",
            "register_level",
        }
        normalized: dict[str, object] = {}
        for key, value in updates.items():
            if key not in allowed:
                continue
            if key in {"priority", "locked", "is_function_word", "luat_nhan_trigger"}:
                normalized[key] = int(value or 0)
                continue
            if key == "metadata_json":
                normalized[key] = value or ""
                continue
            if value is None:
                normalized[key] = None
                continue
            if isinstance(value, str):
                stripped = value.strip()
                normalized[key] = stripped if stripped else None
            else:
                normalized[key] = value
        return normalized

    def _sync_entry_reading(self, previous: DictionaryRecord, current: DictionaryRecord):
        conn = self._get_conn()
        conn.execute(
            """
            DELETE FROM entry_readings
            WHERE source = ? AND source_file = ? AND category = ? AND entry_role = ?
            """,
            (previous.source, previous.source_file, previous.category, previous.entry_role),
        )

        pinyin = (current.pinyin or "").strip()
        han_viet = str(current.metadata.get("han_viet_readings") or "").strip()
        if not han_viet and current.category == "phien_am":
            han_viet = current.target.strip()

        if pinyin or han_viet:
            conn.execute(
                """
                INSERT INTO entry_readings (source, pinyin, han_viet_readings, category, source_file, entry_role)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    current.source,
                    pinyin,
                    han_viet,
                    current.category,
                    current.source_file,
                    current.entry_role,
                ),
            )
        conn.commit()


_SHARED_PINYIN_INDEX: dict[str, dict[str, list[str]]] = {}
_SHARED_NORMALIZATION_RULES: dict[str, list[NormalizationRuleRecord]] = {}


def _shared_db_cache_key(db_path: Path) -> str:
    path = db_path.resolve()
    stat = path.stat()
    return f"{path}:{stat.st_mtime_ns}:{stat.st_size}"
