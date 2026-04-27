#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SQLite-backed translation memory with machine/approved governance."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


APPROVED_STATUSES = {"approved", "verified", "human_verified", "accepted"}
MACHINE_STATUSES = {"machine", "draft", "rbmt", "suggestion"}


@dataclass(slots=True)
class TMEntry:
    source_text: str
    target_text: str
    confidence: float
    source: str
    status: str
    hit_count: int


@dataclass(slots=True)
class FuzzyMatchResult(TMEntry):
    score: float


class TranslationMemory:
    """Persist approved translations separately from machine suggestions."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tm_machine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_hash TEXT NOT NULL,
                source_text TEXT NOT NULL,
                machine_target TEXT NOT NULL,
                engine_version TEXT DEFAULT '',
                rule_version TEXT DEFAULT '',
                quality_score REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                trace_json TEXT DEFAULT '',
                hit_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS tm_approved (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_hash TEXT NOT NULL UNIQUE,
                source_text TEXT NOT NULL,
                approved_target TEXT NOT NULL,
                domain TEXT DEFAULT '',
                register TEXT DEFAULT '',
                reviewer TEXT DEFAULT '',
                approved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                confidence REAL DEFAULT 1.0,
                provenance TEXT DEFAULT '',
                hit_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS tm_reviewed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_hash TEXT NOT NULL,
                source_text TEXT NOT NULL,
                machine_target TEXT DEFAULT '',
                edited_target TEXT DEFAULT '',
                reviewer TEXT DEFAULT '',
                review_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self._ensure_columns("tm_machine", {
            "hit_count": "INTEGER DEFAULT 0",
            "trace_json": "TEXT DEFAULT ''",
        })
        self._ensure_columns("tm_approved", {
            "hit_count": "INTEGER DEFAULT 0",
            "provenance": "TEXT DEFAULT ''",
        })
        self._migrate_legacy_tm_entries()
        self.conn.commit()

    def close(self):
        self.conn.close()

    def store(
        self,
        source_text: str,
        target_text: str,
        *,
        confidence: float = 1.0,
        source: str = "manual",
        status: str = "verified",
    ):
        """Backward-compatible store.

        Human/manual verified data goes to `tm_approved`; RBMT/machine data is
        forced into `tm_machine` even if a caller passes a verified status.
        """

        normalized_status = status.lower().strip()
        normalized_source = source.lower().strip()
        if normalized_source == "rbmt" or normalized_status in MACHINE_STATUSES:
            self.store_machine(
                source_text,
                target_text,
                quality_score=confidence,
                engine_version=source,
            )
            return

        self.store_approved(
            source_text,
            target_text,
            confidence=confidence,
            reviewer=source,
            provenance=status,
        )

    def store_many(self, entries: list[tuple[str, str, float, str, str]]):
        for source_text, target_text, confidence, source, status in entries:
            self.store(source_text, target_text, confidence=confidence, source=source, status=status)

    def store_machine(
        self,
        source_text: str,
        machine_target: str,
        *,
        engine_version: str = "rbmt",
        rule_version: str = "",
        quality_score: float = 0.0,
        trace_json: str | list[dict] | dict = "",
    ) -> int:
        trace_payload = self._json_payload(trace_json)
        cursor = self.conn.execute(
            """
            INSERT INTO tm_machine (
                source_hash, source_text, machine_target, engine_version,
                rule_version, quality_score, created_at, trace_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.source_hash(source_text),
                source_text,
                machine_target,
                engine_version,
                rule_version,
                quality_score,
                self._now(),
                trace_payload,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def store_approved(
        self,
        source_text: str,
        approved_target: str,
        *,
        confidence: float = 1.0,
        reviewer: str = "",
        domain: str = "",
        register: str = "",
        provenance: str = "manual",
    ) -> int:
        source_hash = self.source_hash(source_text)
        cursor = self.conn.execute(
            """
            INSERT INTO tm_approved (
                source_hash, source_text, approved_target, domain, register,
                reviewer, approved_at, confidence, provenance
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_hash) DO UPDATE SET
                source_text = excluded.source_text,
                approved_target = excluded.approved_target,
                domain = excluded.domain,
                register = excluded.register,
                reviewer = excluded.reviewer,
                approved_at = excluded.approved_at,
                confidence = excluded.confidence,
                provenance = excluded.provenance
            """,
            (
                source_hash,
                source_text,
                approved_target,
                domain,
                register,
                reviewer,
                self._now(),
                confidence,
                provenance,
            ),
        )
        self.conn.commit()
        row = self.conn.execute("SELECT id FROM tm_approved WHERE source_hash = ?", (source_hash,)).fetchone()
        return int(row["id"] if row else cursor.lastrowid)

    def save_human_review(
        self,
        source_text: str,
        *,
        machine_target: str = "",
        edited_target: str = "",
        reviewer: str = "",
        review_status: str = "approved",
    ) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO tm_reviewed (
                source_hash, source_text, machine_target, edited_target,
                reviewer, review_status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.source_hash(source_text),
                source_text,
                machine_target,
                edited_target,
                reviewer,
                review_status,
                self._now(),
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def promote_to_approved(
        self,
        review_id: int,
        *,
        domain: str = "",
        register: str = "",
        confidence: float = 1.0,
    ) -> int:
        row = self.conn.execute(
            "SELECT * FROM tm_reviewed WHERE id = ?",
            (review_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Review id not found: {review_id}")
        if str(row["review_status"]).lower() not in APPROVED_STATUSES:
            raise ValueError("Only approved human reviews can be promoted")
        edited_target = str(row["edited_target"] or "").strip()
        if not edited_target:
            raise ValueError("Cannot promote a review without edited_target")
        return self.store_approved(
            row["source_text"],
            edited_target,
            confidence=confidence,
            reviewer=row["reviewer"],
            domain=domain,
            register=register,
            provenance=f"human_review:{review_id}",
        )

    def lookup(self, source_text: str, threshold: float = 0.88) -> TMEntry | FuzzyMatchResult | None:
        exact = self.exact_match(source_text, include_machine=False)
        if exact:
            return exact
        fuzzy = self.fuzzy_match(source_text, threshold=threshold, include_machine=False)
        if fuzzy:
            return fuzzy
        return self.machine_suggestion(source_text)

    def exact_match(self, source_text: str, include_machine: bool = True) -> TMEntry | None:
        source_hash = self.source_hash(source_text)
        row = self.conn.execute(
            """
            SELECT source_text, approved_target AS target_text, confidence,
                   provenance AS source, 'approved' AS status, hit_count
            FROM tm_approved
            WHERE source_hash = ?
            """,
            (source_hash,),
        ).fetchone()
        if row is not None:
            self.conn.execute("UPDATE tm_approved SET hit_count = hit_count + 1 WHERE source_hash = ?", (source_hash,))
            self.conn.commit()
            return self._entry_from_row(row)
        if include_machine:
            return self.machine_suggestion(source_text)
        return None

    def fuzzy_match(
        self,
        source_text: str,
        threshold: float = 0.85,
        include_machine: bool = False,
    ) -> FuzzyMatchResult | None:
        rows = self.conn.execute(
            """
            SELECT source_text, approved_target AS target_text, confidence,
                   provenance AS source, 'approved' AS status, hit_count
            FROM tm_approved
            """
        ).fetchall()
        best = self._best_fuzzy(source_text, rows, threshold)
        if best is not None or not include_machine:
            return best

        machine_rows = self.conn.execute(
            """
            SELECT source_text, machine_target AS target_text, quality_score AS confidence,
                   engine_version AS source, 'machine' AS status, hit_count
            FROM tm_machine
            """
        ).fetchall()
        return self._best_fuzzy(source_text, machine_rows, threshold)

    def machine_suggestion(self, source_text: str) -> TMEntry | None:
        source_hash = self.source_hash(source_text)
        row = self.conn.execute(
            """
            SELECT id, source_text, machine_target AS target_text,
                   quality_score AS confidence, engine_version AS source,
                   'machine' AS status, hit_count
            FROM tm_machine
            WHERE source_hash = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (source_hash,),
        ).fetchone()
        if row is None:
            return None
        self.conn.execute("UPDATE tm_machine SET hit_count = hit_count + 1 WHERE id = ?", (row["id"],))
        self.conn.commit()
        return self._entry_from_row(row)

    def exists_in_machine(self, source_text: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM tm_machine WHERE source_hash = ? LIMIT 1",
            (self.source_hash(source_text),),
        ).fetchone()
        return row is not None

    def exists_in_approved(self, source_text: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM tm_approved WHERE source_hash = ? LIMIT 1",
            (self.source_hash(source_text),),
        ).fetchone()
        return row is not None

    def _best_fuzzy(
        self,
        source_text: str,
        rows: list[sqlite3.Row],
        threshold: float,
    ) -> FuzzyMatchResult | None:
        best: FuzzyMatchResult | None = None
        for row in rows:
            score = SequenceMatcher(a=source_text, b=row["source_text"]).ratio()
            if score < threshold:
                continue
            candidate = FuzzyMatchResult(score=score, **self._entry_kwargs(row))
            if best is None or candidate.score > best.score:
                best = candidate
        return best

    def _migrate_legacy_tm_entries(self):
        legacy = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'tm_entries'"
        ).fetchone()
        if legacy is None:
            return
        rows = self.conn.execute(
            """
            SELECT source_text, target_text, confidence, source, status
            FROM tm_entries
            """
        ).fetchall()
        for row in rows:
            source = str(row["source"] or "")
            status = str(row["status"] or "")
            if source.lower() == "rbmt" or status.lower() in MACHINE_STATUSES:
                if self.exists_in_machine(row["source_text"]):
                    continue
                self.store_machine(
                    row["source_text"],
                    row["target_text"],
                    engine_version=source or "legacy",
                    quality_score=float(row["confidence"] or 0.0),
                )
            else:
                self.store_approved(
                    row["source_text"],
                    row["target_text"],
                    confidence=float(row["confidence"] or 1.0),
                    reviewer=source,
                    provenance=status or "legacy",
                )

    def _ensure_columns(self, table_name: str, columns: dict[str, str]):
        existing = {
            row["name"]
            for row in self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        for column_name, ddl in columns.items():
            if column_name not in existing:
                self.conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")

    @staticmethod
    def source_hash(source_text: str) -> str:
        normalized = " ".join(source_text.strip().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _json_payload(payload: str | list[dict] | dict) -> str:
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    def _entry_from_row(self, row: sqlite3.Row) -> TMEntry:
        return TMEntry(**self._entry_kwargs(row))

    @staticmethod
    def _entry_kwargs(row: sqlite3.Row) -> dict:
        return {
            "source_text": row["source_text"],
            "target_text": row["target_text"],
            "confidence": float(row["confidence"] or 0.0),
            "source": row["source"] or "",
            "status": row["status"] or "",
            "hit_count": int(row["hit_count"] or 0),
        }
