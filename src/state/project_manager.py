#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Project CRUD and persistent translation workspace layout."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path


PROJECT_DIRS = [
    "source/raw",
    "source/chapters",
    "working/entities",
    "working/relationships",
    "working/config",
    "drafts",
    "output",
    "reports",
    "state",
]


@dataclass(slots=True)
class ProjectRecord:
    project_id: str
    project_dir: str
    source_language: str
    target_language: str
    active_chapter: str | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class SegmentRecord:
    segment_id: str
    chapter_id: str
    source_text: str
    target_text: str
    fallback_level: str
    trace: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class CandidateEntryRecord:
    id: int
    source_text: str
    target_text: str
    status: str
    reviewer_reason: str
    chapter_id: str
    segment_id: str
    fallback_level: str
    candidates: list[str] = field(default_factory=list)
    reason: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class CandidateRuleRecord:
    id: int
    rule_type: str
    rule_payload: dict
    status: str
    reviewer_reason: str
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class ProjectManager:
    """Create/open/update translation projects and their state DB."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, project_id: str, *, source_language: str = "zh", target_language: str = "vi") -> ProjectRecord:
        project_dir = self.base_dir / project_id
        for directory in PROJECT_DIRS:
            (project_dir / directory).mkdir(parents=True, exist_ok=True)

        conn = self._connect(project_dir)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO projects (project_id, source_language, target_language, active_chapter)
                VALUES (?, ?, ?, NULL)
                """,
                (project_id, source_language, target_language),
            )
            conn.commit()
        finally:
            conn.close()

        self._write_state_json(project_dir, {
            "project_id": project_id,
            "source_language": source_language,
            "target_language": target_language,
            "active_chapter": None,
        })
        return ProjectRecord(project_id=project_id, project_dir=str(project_dir), source_language=source_language, target_language=target_language, active_chapter=None)

    def list_projects(self) -> list[ProjectRecord]:
        projects: list[ProjectRecord] = []
        for child in sorted(self.base_dir.iterdir()) if self.base_dir.exists() else []:
            if not child.is_dir() or not self._db_path(child).exists():
                continue
            try:
                projects.append(self.open_project(child.name))
            except FileNotFoundError:
                continue
        return projects

    def open_project(self, project_id: str) -> ProjectRecord:
        project_dir = self.base_dir / project_id
        conn = self._connect(project_dir)
        try:
            row = conn.execute(
                "SELECT project_id, source_language, target_language, active_chapter FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise FileNotFoundError(f"Project not found: {project_id}")
        return ProjectRecord(
            project_id=row[0],
            project_dir=str(project_dir),
            source_language=row[1],
            target_language=row[2],
            active_chapter=row[3],
        )

    def get_project_overview(self, project_id: str) -> dict:
        project = self.open_project(project_id)
        project_dir = Path(project.project_dir)
        artifact_paths = self._artifact_paths(project_dir, project.active_chapter)
        conn = self._connect(project_dir)
        try:
            segment_count = conn.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
            candidate_rows = conn.execute(
                """
                SELECT status, COUNT(*) AS total
                FROM candidate_entries
                GROUP BY status
                """
            ).fetchall()
            candidate_rule_rows = conn.execute(
                """
                SELECT status, COUNT(*) AS total
                FROM candidate_rules
                GROUP BY status
                """
            ).fetchall()
        finally:
            conn.close()

        candidate_status = {
            row["status"]: row["total"]
            for row in candidate_rows
        }
        candidate_rule_status = {
            row["status"]: row["total"]
            for row in candidate_rule_rows
        }
        qa_report = self._load_json(project_dir / "reports" / "qa_report.json", {})
        chapters = self._load_json(project_dir / "source" / "chapters" / "chapters_index.json", [])
        for chapter in chapters:
            chapter["source_path"] = str(project_dir / "source" / "chapters" / f"{chapter['chapter_id']}.txt")

        return {
            "project": project.to_dict(),
            "state": self._load_json(project_dir / "state" / "project_state.json", {}),
            "chapters": chapters,
            "config": self._load_json(project_dir / "working" / "config" / "translation_config.json", {}),
            "entities": self._load_json(project_dir / "working" / "entities" / "entities_suggested.json", []),
            "relationships": self._load_json(project_dir / "working" / "relationships" / "relationships_suggested.json", []),
            "terminology_suggestions": self._load_json(project_dir / "working" / "config" / "terminology_suggestions.json", []),
            "counts": {
                "chapters": len(chapters),
                "segments": segment_count,
                "candidates_total": sum(candidate_status.values()),
                "candidate_status": candidate_status,
                "candidate_rules_total": sum(candidate_rule_status.values()),
                "candidate_rule_status": candidate_rule_status,
                "qa_issues": qa_report.get("summary", {}).get("issues", 0),
            },
            "artifacts": artifact_paths,
        }

    def update_state(self, project_id: str, payload: dict):
        self._write_state_json(self.base_dir / project_id, payload, merge=True)

    def set_active_chapter(self, project_id: str, chapter_id: str):
        project_dir = self.base_dir / project_id
        conn = self._connect(project_dir)
        try:
            conn.execute("UPDATE projects SET active_chapter = ?, updated_at = CURRENT_TIMESTAMP WHERE project_id = ?", (chapter_id, project_id))
            conn.commit()
        finally:
            conn.close()
        self._write_state_json(project_dir, {
            "project_id": project_id,
            "active_chapter": chapter_id,
        }, merge=True)

    def record_segment(self, project_id: str, *, segment_id: str, chapter_id: str, source_text: str, target_text: str, trace_json: str | list[dict], fallback_level: str):
        conn = self._connect(self.base_dir / project_id)
        trace_payload = trace_json if isinstance(trace_json, str) else json.dumps(trace_json, ensure_ascii=False, indent=2)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO segments (segment_id, chapter_id, source_text, target_text, trace_json, fallback_level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (segment_id, chapter_id, source_text, target_text, trace_payload, fallback_level),
            )
            conn.commit()
        finally:
            conn.close()

    def list_segments(self, project_id: str, chapter_id: str | None = None) -> list[SegmentRecord]:
        conn = self._connect(self.base_dir / project_id)
        try:
            if chapter_id:
                rows = conn.execute(
                    """
                    SELECT segment_id, chapter_id, source_text, target_text, trace_json, fallback_level
                    FROM segments
                    WHERE chapter_id = ?
                    ORDER BY segment_id
                    """,
                    (chapter_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT segment_id, chapter_id, source_text, target_text, trace_json, fallback_level
                    FROM segments
                    ORDER BY segment_id
                    """
                ).fetchall()
        finally:
            conn.close()

        return [
            SegmentRecord(
                segment_id=row["segment_id"],
                chapter_id=row["chapter_id"],
                source_text=row["source_text"],
                target_text=row["target_text"],
                fallback_level=row["fallback_level"],
                trace=self._safe_json_load(row["trace_json"], []),
            )
            for row in rows
        ]

    def add_candidate_entry(
        self,
        project_id: str,
        source_text: str,
        target_text: str,
        *,
        chapter_id: str = "",
        segment_id: str = "",
        fallback_level: str = "candidate",
        candidates: list[str] | None = None,
        reason: str = "",
    ) -> int:
        conn = self._connect(self.base_dir / project_id)
        candidates_json = json.dumps(candidates or [target_text], ensure_ascii=False)
        try:
            row = conn.execute(
                """
                SELECT id
                FROM candidate_entries
                WHERE source_text = ? AND target_text = ? AND segment_id = ? AND fallback_level = ?
                LIMIT 1
                """,
                (source_text, target_text, segment_id, fallback_level),
            ).fetchone()
            if row is not None:
                conn.execute(
                    """
                    UPDATE candidate_entries
                    SET candidates_json = ?, reason = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (candidates_json, reason, row["id"]),
                )
                conn.commit()
                return int(row["id"])

            cursor = conn.execute(
                """
                INSERT INTO candidate_entries (
                    source_text,
                    target_text,
                    chapter_id,
                    segment_id,
                    fallback_level,
                    candidates_json,
                    reason,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'candidate')
                """,
                (source_text, target_text, chapter_id, segment_id, fallback_level, candidates_json, reason),
            )
            conn.commit()
            return int(cursor.lastrowid)
        finally:
            conn.close()

    def list_candidate_entries(self, project_id: str, status: str | None = None) -> list[CandidateEntryRecord]:
        conn = self._connect(self.base_dir / project_id)
        try:
            if status:
                rows = conn.execute(
                    """
                    SELECT id, source_text, target_text, status, reviewer_reason, chapter_id, segment_id, fallback_level,
                           candidates_json, reason, created_at
                    FROM candidate_entries
                    WHERE status = ?
                    ORDER BY id
                    """,
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, source_text, target_text, status, reviewer_reason, chapter_id, segment_id, fallback_level,
                           candidates_json, reason, created_at
                    FROM candidate_entries
                    ORDER BY id
                    """
                ).fetchall()
        finally:
            conn.close()

        return [
            CandidateEntryRecord(
                id=row["id"],
                source_text=row["source_text"],
                target_text=row["target_text"],
                status=row["status"],
                reviewer_reason=row["reviewer_reason"],
                chapter_id=row["chapter_id"],
                segment_id=row["segment_id"],
                fallback_level=row["fallback_level"],
                candidates=self._safe_json_load(row["candidates_json"], [row["target_text"]]),
                reason=row["reason"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def review_candidate_entry(self, project_id: str, candidate_id: int, status: str, reason: str = ""):
        conn = self._connect(self.base_dir / project_id)
        try:
            conn.execute(
                """
                UPDATE candidate_entries
                SET status = ?, reviewer_reason = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, reason, candidate_id),
            )
            conn.commit()
        finally:
            conn.close()
        for candidate in self.list_candidate_entries(project_id):
            if candidate.id == candidate_id:
                return candidate
        return None

    def add_candidate_rule(
        self,
        project_id: str,
        rule_type: str,
        rule_payload: dict,
        *,
        status: str = "candidate",
    ) -> int:
        conn = self._connect(self.base_dir / project_id)
        payload_json = json.dumps(rule_payload, ensure_ascii=False)
        try:
            row = conn.execute(
                """
                SELECT id
                FROM candidate_rules
                WHERE rule_type = ? AND rule_payload = ?
                LIMIT 1
                """,
                (rule_type, payload_json),
            ).fetchone()
            if row is not None:
                conn.execute(
                    """
                    UPDATE candidate_rules
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status, row["id"]),
                )
                conn.commit()
                return int(row["id"])

            cursor = conn.execute(
                """
                INSERT INTO candidate_rules (rule_type, rule_payload, status, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (rule_type, payload_json, status),
            )
            conn.commit()
            return int(cursor.lastrowid)
        finally:
            conn.close()

    def list_candidate_rules(self, project_id: str, status: str | None = None) -> list[CandidateRuleRecord]:
        conn = self._connect(self.base_dir / project_id)
        try:
            if status:
                rows = conn.execute(
                    """
                    SELECT id, rule_type, rule_payload, status, reviewer_reason, created_at, updated_at
                    FROM candidate_rules
                    WHERE status = ?
                    ORDER BY id
                    """,
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, rule_type, rule_payload, status, reviewer_reason, created_at, updated_at
                    FROM candidate_rules
                    ORDER BY id
                    """
                ).fetchall()
        finally:
            conn.close()

        return [
            CandidateRuleRecord(
                id=row["id"],
                rule_type=row["rule_type"],
                rule_payload=self._safe_json_load(row["rule_payload"], {}),
                status=row["status"],
                reviewer_reason=row["reviewer_reason"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def review_candidate_rule(self, project_id: str, rule_id: int, status: str, reason: str = ""):
        conn = self._connect(self.base_dir / project_id)
        try:
            conn.execute(
                """
                UPDATE candidate_rules
                SET status = ?, reviewer_reason = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, reason, rule_id),
            )
            conn.commit()
        finally:
            conn.close()
        for rule in self.list_candidate_rules(project_id):
            if rule.id == rule_id:
                return rule
        return None

    def record_runtime_stat(self, project_id: str, metric_name: str, metric_value: float, chapter_id: str = ""):
        conn = self._connect(self.base_dir / project_id)
        try:
            conn.execute(
                "INSERT INTO runtime_stats (metric_name, metric_value, chapter_id) VALUES (?, ?, ?)",
                (metric_name, metric_value, chapter_id),
            )
            conn.commit()
        finally:
            conn.close()

    def _connect(self, project_dir: Path) -> sqlite3.Connection:
        (project_dir / "state").mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path(project_dir)))
        conn.row_factory = sqlite3.Row
        self._ensure_schema(conn)
        return conn

    def _ensure_schema(self, conn: sqlite3.Connection):
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                active_chapter TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS chapters (
                chapter_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                output_path TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS segments (
                segment_id TEXT PRIMARY KEY,
                chapter_id TEXT DEFAULT '',
                source_text TEXT NOT NULL,
                target_text TEXT DEFAULT '',
                trace_json TEXT DEFAULT '',
                fallback_level TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS candidate_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                target_text TEXT NOT NULL,
                chapter_id TEXT DEFAULT '',
                segment_id TEXT DEFAULT '',
                fallback_level TEXT DEFAULT 'candidate',
                candidates_json TEXT DEFAULT '[]',
                reason TEXT DEFAULT '',
                status TEXT DEFAULT 'candidate',
                reviewer_reason TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS candidate_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_type TEXT NOT NULL,
                rule_payload TEXT NOT NULL,
                status TEXT DEFAULT 'candidate',
                reviewer_reason TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS runtime_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                chapter_id TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self._ensure_columns(conn, "candidate_entries", {
            "chapter_id": "TEXT DEFAULT ''",
            "segment_id": "TEXT DEFAULT ''",
            "fallback_level": "TEXT DEFAULT 'candidate'",
            "candidates_json": "TEXT DEFAULT '[]'",
            "reason": "TEXT DEFAULT ''",
            "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
        })
        self._ensure_columns(conn, "candidate_rules", {
            "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
        })
        conn.commit()

    @staticmethod
    def _ensure_columns(conn: sqlite3.Connection, table_name: str, columns: dict[str, str]):
        existing = {
            row["name"]
            for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        for column_name, ddl in columns.items():
            if column_name not in existing:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")

    def _db_path(self, project_dir: Path) -> Path:
        return project_dir / "state" / "project_state.db"

    @staticmethod
    def _artifact_paths(project_dir: Path, chapter_id: str | None) -> dict:
        config_path = str(project_dir / "working" / "config" / "translation_config.json")
        if not chapter_id:
            return {
                "config_path": config_path,
                "output_path": "",
                "draft_path": "",
                "trace_path": "",
                "qa_report_path": "",
            }
        return {
            "config_path": config_path,
            "output_path": str(project_dir / "output" / f"{chapter_id}.txt"),
            "draft_path": str(project_dir / "drafts" / f"{chapter_id}_draft.txt"),
            "trace_path": str(project_dir / "drafts" / f"{chapter_id}_trace.json"),
            "qa_report_path": str(project_dir / "reports" / f"qa_report_{chapter_id}.json"),
        }

    @staticmethod
    def _load_json(path: Path, default: object):
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _safe_json_load(payload: str | None, default: object):
        if not payload:
            return default
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return default

    def _write_state_json(self, project_dir: Path, payload: dict, merge: bool = False):
        state_path = project_dir / "state" / "project_state.json"
        if merge and state_path.exists():
            data = json.loads(state_path.read_text(encoding="utf-8"))
            data.update(payload)
        else:
            data = payload
        state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
