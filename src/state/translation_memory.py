#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SQLite-backed translation memory with exact and fuzzy lookup."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


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
    """Persist translation segments and retrieve them by similarity."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tm_entries (
                source_text TEXT PRIMARY KEY,
                target_text TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT DEFAULT '',
                status TEXT DEFAULT 'verified',
                hit_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

    def store(self, source_text: str, target_text: str, *, confidence: float = 1.0, source: str = "manual", status: str = "verified"):
        self.conn.execute(
            """
            INSERT INTO tm_entries (source_text, target_text, confidence, source, status, hit_count)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(source_text) DO UPDATE SET
                target_text = excluded.target_text,
                confidence = excluded.confidence,
                source = excluded.source,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (source_text, target_text, confidence, source, status),
        )
        self.conn.commit()

    def store_many(self, entries: list[tuple[str, str, float, str, str]]):
        if not entries:
            return
        self.conn.executemany(
            """
            INSERT INTO tm_entries (source_text, target_text, confidence, source, status, hit_count)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(source_text) DO UPDATE SET
                target_text = excluded.target_text,
                confidence = excluded.confidence,
                source = excluded.source,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            entries,
        )
        self.conn.commit()

    def exact_match(self, source_text: str) -> TMEntry | None:
        row = self.conn.execute(
            """
            SELECT source_text, target_text, confidence, source, status, hit_count
            FROM tm_entries
            WHERE source_text = ?
            """,
            (source_text,),
        ).fetchone()
        if row is None:
            return None
        self.conn.execute("UPDATE tm_entries SET hit_count = hit_count + 1 WHERE source_text = ?", (source_text,))
        self.conn.commit()
        return TMEntry(**dict(row))

    def fuzzy_match(self, source_text: str, threshold: float = 0.85) -> FuzzyMatchResult | None:
        rows = self.conn.execute(
            """
            SELECT source_text, target_text, confidence, source, status, hit_count
            FROM tm_entries
            """
        ).fetchall()
        best: FuzzyMatchResult | None = None
        for row in rows:
            score = SequenceMatcher(a=source_text, b=row["source_text"]).ratio()
            if score < threshold:
                continue
            candidate = FuzzyMatchResult(score=score, **dict(row))
            if best is None or candidate.score > best.score:
                best = candidate
        return best
