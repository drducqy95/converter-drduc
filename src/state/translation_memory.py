#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SQLite-backed translation memory with machine/approved governance."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


APPROVED_STATUSES = {"approved", "verified", "human_verified", "accepted"}
MACHINE_STATUSES = {"machine", "draft", "rbmt", "suggestion"}
MACHINE_TO_APPROVED_POLICY = {
    "requires_user_action": True,
    "auto_promote_reuse_count": None,
    "allowed_review_statuses": sorted(APPROVED_STATUSES),
}
TIER_WEIGHTS = {
    "approved": 0.15,
    "reviewed": 0.08,
    "machine": 0.0,
}


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


@dataclass(slots=True)
class TieredFuzzyMatchResult(FuzzyMatchResult):
    tier: str
    raw_score: float
    weighted_score: float


class TranslationMemory:
    """Persist approved translations separately from machine suggestions."""

    MACHINE_TO_APPROVED_POLICY = MACHINE_TO_APPROVED_POLICY
    TIER_WEIGHTS = TIER_WEIGHTS

    def __init__(self, db_path: str | Path, *, max_machine_entries: int | None = None):
        self.db_path = Path(db_path)
        self.max_machine_entries = max_machine_entries
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
                hit_count INTEGER DEFAULT 0,
                last_accessed TEXT DEFAULT ''
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
                hit_count INTEGER DEFAULT 0,
                last_accessed TEXT DEFAULT ''
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
            "last_accessed": "TEXT DEFAULT ''",
        })
        self._ensure_columns("tm_approved", {
            "hit_count": "INTEGER DEFAULT 0",
            "provenance": "TEXT DEFAULT ''",
            "last_accessed": "TEXT DEFAULT ''",
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
        if self.max_machine_entries is not None:
            self.evict_machine_entries(self.max_machine_entries)
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
            SELECT id, source_hash, source_text, approved_target AS target_text, confidence,
                   provenance AS source, 'approved' AS status, hit_count
            FROM tm_approved
            WHERE source_hash = ?
            """,
            (source_hash,),
        ).fetchone()
        if row is not None:
            self._touch_row("tm_approved", int(row["id"]))
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
            SELECT id, source_hash, source_text, approved_target AS target_text, confidence,
                   provenance AS source, 'approved' AS status, hit_count
            FROM tm_approved
            """
        ).fetchall()
        best = self._best_fuzzy(source_text, rows, threshold, table_name="tm_approved")
        if best is not None or not include_machine:
            return best

        machine_rows = self.conn.execute(
            """
            SELECT id, source_hash, source_text, machine_target AS target_text, quality_score AS confidence,
                   engine_version AS source, 'machine' AS status, hit_count
            FROM tm_machine
            """
        ).fetchall()
        return self._best_fuzzy(source_text, machine_rows, threshold, table_name="tm_machine")

    def tiered_fuzzy_search(
        self,
        source_text: str,
        threshold: float = 0.75,
        *,
        include_reviewed: bool = True,
        include_machine: bool = True,
        limit: int = 10,
    ) -> list[TieredFuzzyMatchResult]:
        """Rank TM matches by source similarity plus explicit tier weight.

        Runtime `lookup()` keeps the stricter policy: approved exact/fuzzy
        matches first, then exact machine suggestions only. This broader search
        is intended for review/export tooling where lower-tier ambiguity should
        stay visible.
        """

        if limit < 1:
            return []

        results: list[TieredFuzzyMatchResult] = []
        for tier, row in self._tiered_rows(include_reviewed=include_reviewed, include_machine=include_machine):
            raw_score = self.similarity(source_text, row["source_text"])
            if raw_score < threshold:
                continue
            weighted_score = min(1.0, raw_score + self.TIER_WEIGHTS.get(tier, 0.0))
            results.append(
                TieredFuzzyMatchResult(
                    **self._entry_kwargs(row),
                    score=weighted_score,
                    tier=tier,
                    raw_score=raw_score,
                    weighted_score=weighted_score,
                )
            )

        return sorted(
            results,
            key=lambda item: (
                -item.weighted_score,
                -item.raw_score,
                -self.TIER_WEIGHTS.get(item.tier, 0.0),
                item.source_text,
                item.target_text,
            ),
        )[:limit]

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
        self._touch_row("tm_machine", int(row["id"]))
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
        *,
        table_name: str,
    ) -> FuzzyMatchResult | None:
        best: FuzzyMatchResult | None = None
        best_row_id: int | None = None
        for row in rows:
            score = self.similarity(source_text, row["source_text"])
            if score < threshold:
                continue
            candidate = FuzzyMatchResult(score=score, **self._entry_kwargs(row))
            if best is None or candidate.score > best.score:
                best = candidate
                best_row_id = int(row["id"])
        if best_row_id is not None:
            self._touch_row(table_name, best_row_id)
        return best

    def _tiered_rows(
        self,
        *,
        include_reviewed: bool,
        include_machine: bool,
    ) -> list[tuple[str, sqlite3.Row]]:
        tiered: list[tuple[str, sqlite3.Row]] = [
            ("approved", row)
            for row in self.conn.execute(
                """
                SELECT id, source_hash, source_text, approved_target AS target_text, confidence,
                       provenance AS source, 'approved' AS status, hit_count
                FROM tm_approved
                """
            ).fetchall()
        ]

        if include_reviewed:
            tiered.extend(
                ("reviewed", row)
                for row in self.conn.execute(
                    """
                    SELECT id, source_hash, source_text,
                           COALESCE(NULLIF(edited_target, ''), machine_target) AS target_text,
                           CASE
                               WHEN LOWER(review_status) IN ('approved', 'verified', 'human_verified', 'accepted')
                               THEN 0.90
                               ELSE 0.65
                           END AS confidence,
                           reviewer AS source,
                           review_status AS status,
                           0 AS hit_count
                    FROM tm_reviewed
                    WHERE COALESCE(NULLIF(edited_target, ''), machine_target) != ''
                    """
                ).fetchall()
            )

        if include_machine:
            tiered.extend(
                ("machine", row)
                for row in self.conn.execute(
                    """
                    SELECT id, source_hash, source_text, machine_target AS target_text,
                           quality_score AS confidence, engine_version AS source,
                           'machine' AS status, hit_count
                    FROM tm_machine
                    """
                ).fetchall()
            )

        return tiered

    def evict_machine_entries(self, max_entries: int) -> int:
        if max_entries < 0:
            raise ValueError("max_entries must be >= 0")
        row = self.conn.execute("SELECT COUNT(*) AS count FROM tm_machine").fetchone()
        count = int(row["count"] if row else 0)
        overflow = count - max_entries
        if overflow <= 0:
            return 0

        victims = self.conn.execute(
            """
            SELECT id
            FROM tm_machine
            ORDER BY hit_count ASC, COALESCE(NULLIF(last_accessed, ''), created_at) ASC, id ASC
            LIMIT ?
            """,
            (overflow,),
        ).fetchall()
        victim_ids = [int(row["id"]) for row in victims]
        if not victim_ids:
            return 0

        placeholders = ",".join("?" for _ in victim_ids)
        self.conn.execute(f"DELETE FROM tm_machine WHERE id IN ({placeholders})", victim_ids)
        self.conn.commit()
        return len(victim_ids)

    def snapshot(self, tag: str = "manual", directory: str | Path | None = None) -> Path:
        self.conn.commit()
        snapshot_dir = Path(directory) if directory is not None else self.db_path.parent / "tm_snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        safe_tag = re.sub(r"[^A-Za-z0-9_.-]+", "-", tag.strip() or "manual").strip("-") or "manual"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        snapshot_path = snapshot_dir / f"{safe_tag}_{timestamp}.sqlite"
        shutil.copy2(self.db_path, snapshot_path)
        return snapshot_path

    def rollback(self, snapshot_path: str | Path) -> None:
        snapshot = Path(snapshot_path)
        if not snapshot.exists():
            raise FileNotFoundError(f"TM snapshot not found: {snapshot}")
        self.conn.commit()
        self.conn.close()
        shutil.copy2(snapshot, self.db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    @classmethod
    def similarity(cls, left: str, right: str) -> float:
        if cls._contains_cjk(left) or cls._contains_cjk(right):
            return max(cls.cjk_similarity(left, right), SequenceMatcher(a=left, b=right).ratio())
        return SequenceMatcher(a=left, b=right).ratio()

    @staticmethod
    def cjk_similarity(left: str, right: str, n: int = 2) -> float:
        def normalize(value: str) -> str:
            return "".join(str(value or "").split())

        def ngrams(value: str) -> set[str]:
            if len(value) < n:
                return {value} if value else set()
            return {value[idx:idx + n] for idx in range(len(value) - n + 1)}

        left_norm = normalize(left)
        right_norm = normalize(right)
        if not left_norm or not right_norm:
            return 1.0 if left_norm == right_norm else 0.0

        left_ngrams = ngrams(left_norm)
        right_ngrams = ngrams(right_norm)
        if not left_ngrams or not right_ngrams:
            return 0.0
        return len(left_ngrams & right_ngrams) / len(left_ngrams | right_ngrams)

    @staticmethod
    def _contains_cjk(value: str) -> bool:
        return any("\u4e00" <= ch <= "\u9fff" for ch in str(value or ""))

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

    def _touch_row(self, table_name: str, row_id: int):
        if table_name not in {"tm_machine", "tm_approved"}:
            raise ValueError(f"Unsupported TM table: {table_name}")
        self.conn.execute(
            f"UPDATE {table_name} SET hit_count = hit_count + 1, last_accessed = ? WHERE id = ?",
            (self._now(), row_id),
        )
        self.conn.commit()

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
