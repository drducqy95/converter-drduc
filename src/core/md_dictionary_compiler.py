#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
md_dictionary_compiler.py — Parse Markdown Dictionary files and compile to SQLite.

Supports:
- Bulk MD: YAML frontmatter + Markdown table (for 728K+ entries)
- Rich MD: YAML frontmatter + body content (for important terms)
- Grammar MD: Pattern templates with {0} placeholders

Compiles all entries into a unified SQLite database with priority levels.
"""

import hashlib
import os
import re
import sqlite3
import json
import yaml
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator

from src.core.dictionary_entry_filters import looks_like_reference_gloss


# ─────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────

@dataclass
class DictEntry:
    """A single dictionary entry."""
    source: str          # Source text (e.g., 修为)
    target: str          # Target text (e.g., tu vi)
    priority: int = 2    # 1=lowest (PhienAm) → 5=highest (project names)
    category: str = ""   # e.g., vietphrase_general, names_general
    one_mean: bool = False  # If True, take first meaning before ';'
    locked: bool = False    # If True, cannot be overridden
    notes: str = ""
    source_file: str = ""
    source_language: str = "zh"
    target_language: str = "vi"
    entry_role: str = "translation"
    metadata_json: str = ""
    # Phase 09 Metadata
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
    def effective_target(self) -> str:
        """Return effective translation, applying one_mean if needed."""
        if self.one_mean and ';' in self.target:
            return self.target.split(';')[0].strip()
        return self.target


@dataclass
class GrammarPattern:
    """A LuatNhan grammar pattern with {0} placeholder."""
    pattern: str         # e.g., {0}军团
    replacement: str     # e.g., quân đoàn {0}
    category: str = ""   # luat_nhan_primary or luat_nhan_extended
    source_file: str = ""


@dataclass
class NormalizationRule:
    """A normalization rule used before/after translation."""
    source_text: str
    target_text: str
    rule_type: str = "replace"
    notes: str = ""
    source_file: str = ""


@dataclass
class AuditEvent:
    """A history/audit event imported from QT history files."""
    entry: str
    action: str
    user_name: str
    updated_at: str
    source_dict: str
    source_file: str = ""


# ─────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────

def _parse_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Split Markdown content into YAML frontmatter and body."""
    if not content.startswith('---'):
        return {}, content
    
    end_idx = content.find('\n---', 3)
    if end_idx == -1:
        return {}, content
    
    yaml_str = content[4:end_idx].strip()
    body = content[end_idx + 4:].strip()
    
    try:
        metadata = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError:
        metadata = {}
    
    return metadata, body


def _read_md_file(filepath: str) -> tuple[dict, str]:
    """Read an MD file once and return metadata + body."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return _parse_yaml_frontmatter(f.read())


_TABLE_ROW_RE = re.compile(r'^\|(.+)\|$')
_SEPARATOR_RE = re.compile(r'^[\|\s\-:]+$')


def _split_md_row(row_content: str) -> list[str]:
    """Split a Markdown table row, preserving escaped pipes."""
    cells: list[str] = []
    current: list[str] = []
    i = 0

    while i < len(row_content):
        ch = row_content[i]

        if ch == '\\' and i + 1 < len(row_content):
            next_ch = row_content[i + 1]
            if next_ch in {'|', '\\'}:
                current.append(next_ch)
                i += 2
                continue

        if ch == '|':
            cells.append(''.join(current).strip())
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    cells.append(''.join(current).strip())
    return cells


def _parse_md_table(body: str) -> list[dict[str, str]]:
    """Parse a Markdown table into list of dicts."""
    lines = body.strip().split('\n')
    
    # Find header row
    headers = []
    data_start = 0
    for i, line in enumerate(lines):
        line = line.strip()
        match = _TABLE_ROW_RE.match(line)
        if match and not _SEPARATOR_RE.match(line):
            if not headers:
                # This is the header row
                headers = _split_md_row(match.group(1))
                data_start = i + 1
                continue
            elif i == data_start and _SEPARATOR_RE.match(line):
                # Skip separator row
                data_start = i + 1
                continue
    
    if not headers:
        return []
    
    rows = []
    for line in lines[data_start:]:
        line = line.strip()
        if _SEPARATOR_RE.match(line):
            continue
        match = _TABLE_ROW_RE.match(line)
        if match:
            cells = _split_md_row(match.group(1))
            row = {}
            for j, header in enumerate(headers):
                head_key = header.lower().replace(' ', '_')
                row[head_key] = cells[j] if j < len(cells) else ""
            if 'metadata' in row and row['metadata']:
                try:
                    import json
                    meta = json.loads(row['metadata'])
                    for k, v in meta.items():
                        if k not in row or not row[k]:
                            row[k] = str(v) if isinstance(v, (int, bool)) else v
                except Exception:
                    pass
            rows.append(row)
    
    return rows


def parse_bulk_md(filepath: str, metadata: dict | None = None, body: str | None = None) -> Iterator[DictEntry]:
    """Parse a Bulk MD dictionary file, yielding DictEntry objects."""
    if metadata is None or body is None:
        metadata, body = _read_md_file(filepath)

    priority = metadata.get('priority', 2)
    category = metadata.get('category', '')
    source_language = metadata.get('source_language', 'zh')
    target_language = metadata.get('target_language', 'vi')
    entry_role = metadata.get('entry_role')
    if not entry_role:
        entry_role = "translation" if source_language == "zh" and target_language == "vi" else "reference"
    
    rows = _parse_md_table(body)
    
    for row in rows:
        source = row.get('source', '').strip()
        target = row.get('target', '').strip()
        if not source or not target:
            continue
        
        one_mean = row.get('one_mean', '').lower() in ('true', '1', 'yes')
        notes = row.get('notes', '')
        locked = row.get('locked', '').lower() in ('true', '1', 'yes')
        pos_tag = row.get('pos_tag', '').strip() or None
        pos_sub = row.get('pos_sub', '').strip() or None
        entity_type = row.get('entity_type', '').strip() or None
        pinyin = row.get('pinyin', '').strip() or None
        traditional = row.get('traditional', '').strip() or None
        is_function_word = 1 if row.get('is_function_word', '').lower() in ('true', '1', 'yes') else 0
        luat_nhan_trigger = 1 if row.get('luat_nhan_trigger', '').lower() in ('true', '1', 'yes') else 0
        reorder_role = row.get('reorder_role', '').strip() or None
        cultural_origin = row.get('cultural_origin', '').strip() or None
        genre_affinity = row.get('genre_affinity', '').strip() or None
        register_level = row.get('register_level', '').strip() or None

        extra_meta = {}
        for key, value in row.items():
            if key in {
                'source', 'target', 'one_mean', 'locked', 'notes',
                'pos_tag', 'pos_sub', 'entity_type', 'is_function_word',
                'luat_nhan_trigger', 'reorder_role', 'cultural_origin',
                'genre_affinity', 'register_level'
            }:
                continue
            if value != "":
                extra_meta[key] = value
        
        yield DictEntry(
            source=source,
            target=target,
            priority=priority,
            category=category,
            one_mean=one_mean,
            locked=locked,
            notes=notes,
            source_file=os.path.basename(filepath),
            source_language=source_language,
            target_language=target_language,
            entry_role=entry_role,
            metadata_json=json.dumps(extra_meta, ensure_ascii=False, separators=(',', ':')) if extra_meta else "",
            pos_tag=pos_tag,
            pos_sub=pos_sub,
            entity_type=entity_type,
            pinyin=pinyin,
            traditional=traditional,
            is_function_word=is_function_word,
            luat_nhan_trigger=luat_nhan_trigger,
            reorder_role=reorder_role,
            cultural_origin=cultural_origin,
            genre_affinity=genre_affinity,
            register_level=register_level,
        )


def parse_rich_md(filepath: str, metadata: dict | None = None, body: str | None = None) -> DictEntry | None:
    """Parse a Rich MD dictionary file (single entry per file)."""
    if metadata is None or body is None:
        metadata, body = _read_md_file(filepath)
    
    source = metadata.get('source', '')
    target = metadata.get('target', '')
    if not source or not target:
        return None

    source_language = metadata.get('source_language', 'zh')
    target_language = metadata.get('target_language', 'vi')
    entry_role = metadata.get('entry_role')
    if not entry_role:
        entry_role = "translation" if source_language == "zh" and target_language == "vi" else "reference"
    
    return DictEntry(
        source=source,
        target=target,
        priority=metadata.get('priority', 3),
        category=metadata.get('category', ''),
        one_mean=metadata.get('one_mean', False),
        locked=metadata.get('locked', False),
        notes=metadata.get('notes', ''),
        source_file=os.path.basename(filepath),
        source_language=source_language,
        target_language=target_language,
        entry_role=entry_role,
        metadata_json=json.dumps({"body": body}, ensure_ascii=False, separators=(',', ':')) if body else "",
    )


def parse_grammar_md(filepath: str, metadata: dict | None = None, body: str | None = None) -> Iterator[GrammarPattern]:
    """Parse a Grammar/Pattern MD file, yielding GrammarPattern objects."""
    if metadata is None or body is None:
        metadata, body = _read_md_file(filepath)

    category = metadata.get('category', '')
    
    rows = _parse_md_table(body)
    
    for row in rows:
        pattern = row.get('pattern', '').strip()
        replacement = row.get('replacement', '').strip()
        if not pattern or not replacement:
            continue
        
        yield GrammarPattern(
            pattern=pattern,
            replacement=replacement,
            category=category,
            source_file=os.path.basename(filepath),
        )


def parse_normalization_md(filepath: str, metadata: dict | None = None, body: str | None = None) -> Iterator[NormalizationRule]:
    """Parse normalization rules such as punctuation mappings."""
    if metadata is None or body is None:
        metadata, body = _read_md_file(filepath)

    default_rule_type = metadata.get('rule_type', 'replace')
    rows = _parse_md_table(body)

    for row in rows:
        source_text = row.get('source', row.get('raw_pattern', '')).strip()
        target_text = row.get('target', row.get('clean_text', ''))
        rule_type = row.get('rule_type', '').strip() or default_rule_type
        notes = row.get('notes', '').strip()
        if not source_text:
            continue

        yield NormalizationRule(
            source_text=source_text,
            target_text=target_text,
            rule_type=rule_type,
            notes=notes,
            source_file=os.path.basename(filepath),
        )


def parse_ignored_phrases_md(filepath: str, metadata: dict | None = None, body: str | None = None) -> Iterator[NormalizationRule]:
    """Parse ignored phrases into normalization rules."""
    if metadata is None or body is None:
        metadata, body = _read_md_file(filepath)

    rows = _parse_md_table(body)
    for row in rows:
        raw_pattern = row.get('raw_pattern', '').strip()
        clean_text = row.get('clean_text', '')
        if not raw_pattern:
            continue

        yield NormalizationRule(
            source_text=raw_pattern,
            target_text=clean_text,
            rule_type='ignored_phrase',
            notes=metadata.get('notes', ''),
            source_file=os.path.basename(filepath),
        )


def parse_audit_md(filepath: str, metadata: dict | None = None, body: str | None = None) -> Iterator[AuditEvent]:
    """Parse audit event Markdown files."""
    if metadata is None or body is None:
        metadata, body = _read_md_file(filepath)

    default_source_dict = metadata.get('source_dict', '')
    rows = _parse_md_table(body)
    for row in rows:
        entry = row.get('entry', '').strip()
        if not entry:
            continue
        yield AuditEvent(
            entry=entry,
            action=row.get('action', '').strip(),
            user_name=row.get('user_name', '').strip(),
            updated_at=row.get('updated_at', '').strip(),
            source_dict=row.get('source_dict', '').strip() or default_source_dict,
            source_file=os.path.basename(filepath),
        )


# ─────────────────────────────────────────────────
# Compiler
# ─────────────────────────────────────────────────

class DictionaryCompiler:
    """
    Compiles Markdown dictionary files into a unified SQLite database.
    
    Handles 5 priority tiers:
        P5: projects/{name}/names_rieng.md      (highest - project-specific names)
        P4: global/names/_bulk_names.md          (global names)
        P3: projects/{name}/vietphrase_rieng.md  (project-specific VietPhrase)
        P2: global/vietphrase/_bulk_vietphrase.md (global VietPhrase)
        P1: global/phien_am/_bulk_phienam.md     (lowest - single char fallback)
    """
    
    def __init__(self, dict_root: str, compiled_dir: str | None = None):
        self.dict_root = Path(dict_root)
        self.compiled_dir = Path(compiled_dir or (self.dict_root / "_compiled"))
        self.compiled_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.compiled_dir / "trie_cache.db"
        self.index_path = self.compiled_dir / "lookup_index.json"
    
    def compile(self, project_name: str | None = None) -> dict:
        """
        Compile all dictionary sources into SQLite.
        
        Args:
            project_name: If provided, include project-specific dictionaries.
        
        Returns:
            Statistics dict.
        """
        start_time = time.time()
        
        # Collect all entries
        entries: dict[str, DictEntry] = {}  # key=source, value=highest priority runtime entry
        reference_entries: list[DictEntry] = []
        reading_seed_entries: list[DictEntry] = []
        grammar_patterns: list[GrammarPattern] = []
        normalization_rules: list[NormalizationRule] = []
        audit_events: list[AuditEvent] = []
        stats = {
            "files_processed": 0,
            "entries_total": 0,
            "entries_unique": 0,
            "reference_entries": 0,
            "grammar_patterns": 0,
            "normalization_rules": 0,
            "audit_events": 0,
            "entry_readings": 0,
            "phienam_runtime_before_reduction": 0,
            "phienam_runtime_after_reduction": 0,
            "phienam_runtime_pruned": 0,
            "priority_breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }
        
        # Phase 1: Scan all dictionary files
        scan_dirs = self._get_scan_dirs(project_name)
        source_manifest = self._build_source_manifest(scan_dirs)
        stats["source_files_hashed"] = len(source_manifest)
        stats["source_manifest_hash"] = self._source_manifest_hash(source_manifest)
        
        for scan_dir, default_priority in scan_dirs:
            if not scan_dir.exists():
                continue
            
            for filepath in sorted(scan_dir.rglob("*.md")):
                stats["files_processed"] += 1
                metadata, body = _read_md_file(str(filepath))
                md_type = metadata.get("type", "")

                if md_type == "bulk_dictionary":
                    for entry in parse_bulk_md(str(filepath), metadata=metadata, body=body):
                        if self._should_materialize_reading(entry):
                            reading_seed_entries.append(entry)
                        if self._is_runtime_entry(entry):
                            self._merge_entry(entries, entry, stats)
                        else:
                            reference_entries.append(entry)
                            stats["reference_entries"] += 1

                elif md_type == "grammar_patterns":
                    for pattern in parse_grammar_md(str(filepath), metadata=metadata, body=body):
                        grammar_patterns.append(pattern)
                        stats["grammar_patterns"] += 1

                elif md_type == "ignored_phrases":
                    for rule in parse_ignored_phrases_md(str(filepath), metadata=metadata, body=body):
                        normalization_rules.append(rule)
                        stats["normalization_rules"] += 1

                elif md_type == "normalization_rules":
                    for rule in parse_normalization_md(str(filepath), metadata=metadata, body=body):
                        normalization_rules.append(rule)
                        stats["normalization_rules"] += 1

                elif md_type == "audit_events":
                    for event in parse_audit_md(str(filepath), metadata=metadata, body=body):
                        audit_events.append(event)
                        stats["audit_events"] += 1

                else:
                    entry = parse_rich_md(str(filepath), metadata=metadata, body=body)
                    if entry:
                        if self._should_materialize_reading(entry):
                            reading_seed_entries.append(entry)
                        if self._is_runtime_entry(entry):
                            self._merge_entry(entries, entry, stats)
                        else:
                            reference_entries.append(entry)
                            stats["reference_entries"] += 1

        stats["entries_unique"] = len(entries)
        phienam_stats = self._reduce_phienam_runtime(entries, reference_entries)
        stats.update(phienam_stats)
        stats["entries_unique"] = len(entries)
        
        # Phase 2: Write to SQLite
        stats["entry_readings"] = self._write_sqlite(
            entries,
            grammar_patterns,
            reference_entries,
            normalization_rules,
            audit_events,
            reading_seed_entries,
            source_manifest,
        )
        
        # Phase 3: Build lookup index
        self._write_lookup_index(entries)
        
        elapsed = time.time() - start_time
        stats["compile_time_seconds"] = round(elapsed, 2)
        
        return stats

    def _is_runtime_entry(self, entry: DictEntry) -> bool:
        """Only zh -> vi entries belong to the current runtime Trie."""
        return (
            entry.entry_role == "translation"
            and entry.source_language == "zh"
            and entry.target_language == "vi"
            and not looks_like_reference_gloss(entry.category, entry.target)
        )

    def _should_materialize_reading(self, entry: DictEntry) -> bool:
        """Decide whether an entry should contribute to entry_readings."""
        return bool(entry.metadata_json) or entry.category == "phien_am"

    def _reduce_phienam_runtime(
        self,
        entries: dict[str, DictEntry],
        reference_entries: list[DictEntry],
    ) -> dict:
        """Prune runtime PhienAm entries that are already covered by richer references."""
        rich_reference_sources: set[str] = set()
        for entry in reference_entries:
            if entry.category in {"thieuchuu_reference", "lacviet_reference", "cedict_reference"}:
                rich_reference_sources.add(entry.source)

        phienam_keys = [
            key for key, entry in entries.items()
            if entry.category == "phien_am"
        ]
        before = len(phienam_keys)

        pruned = 0
        for key in phienam_keys:
            if key in rich_reference_sources:
                del entries[key]
                pruned += 1

        return {
            "phienam_runtime_before_reduction": before,
            "phienam_runtime_after_reduction": before - pruned,
            "phienam_runtime_pruned": pruned,
        }
    
    def _get_scan_dirs(self, project_name: str | None) -> list[tuple[Path, int]]:
        """Return list of (directory, default_priority) to scan, in order."""
        dirs = [
            # P1: PhienAm (lowest)
            (self.dict_root / "global" / "phien_am", 1),
            # P2: VietPhrase general
            (self.dict_root / "global" / "vietphrase", 2),
            # P2: Idioms (same priority as VietPhrase)
            (self.dict_root / "global" / "idioms", 2),
            # P3: Numbers (Pronouns.txt data)
            (self.dict_root / "global" / "numbers", 3),
            # P4: Names global
            (self.dict_root / "global" / "names", 4),
            # Grammar patterns (LuatNhan) — scanned for grammar_patterns table
            (self.dict_root / "global" / "grammar", 0),
            # Normalization resources (Mark, ignored phrases, punctuation maps)
            (self.dict_root / "global" / "normalization", 0),
            # Audit/provenance imported from QT history files
            (self.dict_root / "global" / "audit", 0),
            # ZH-VI reference dictionaries with rich metadata
            (self.dict_root / "global" / "reference_vi", 1),
            # EN-VI reference (CEDICT, LacViet)
            (self.dict_root / "global" / "en_vi", 1),
            # Expressions (EAPEE data)
            (self.dict_root / "global" / "expressions", 0),
        ]
        
        if project_name:
            project_dir = self.dict_root / "projects" / project_name
            dirs.extend([
                # P3: Project VietPhrase
                (project_dir, 3),
                # P5: Project names (highest)
                (project_dir / "characters", 5),
                (project_dir / "factions", 5),
                (project_dir / "locations", 5),
                (project_dir / "weapons", 5),
                (project_dir / "techniques", 5),
                (project_dir / "items", 5),
                (project_dir / "cultivation", 5),
            ])
        
        return dirs

    def current_source_manifest(self, project_name: str | None = None) -> dict[str, dict[str, object]]:
        """Return a content manifest for the Markdown sources used by this cache."""
        return self._build_source_manifest(self._get_scan_dirs(project_name))

    def load_cached_source_manifest(self) -> dict[str, dict[str, object]]:
        """Load the source manifest embedded in the compiled SQLite metadata."""
        payload = self._load_metadata().get("source_manifest_json", "")
        if not payload:
            return {}
        try:
            manifest = json.loads(payload)
        except json.JSONDecodeError:
            return {}
        if not isinstance(manifest, dict):
            return {}
        return {
            str(path): dict(value)
            for path, value in manifest.items()
            if isinstance(value, dict)
        }

    def source_cache_status(self, project_name: str | None = None) -> dict[str, object]:
        """Compare current dictionary sources with the manifest stored in SQLite."""
        current_manifest = self.current_source_manifest(project_name)
        current_hash = self._source_manifest_hash(current_manifest)

        if not self.db_path.exists():
            return {
                "stale": True,
                "reason": "missing_db",
                "cached_hash": "",
                "current_hash": current_hash,
                "cached_files": 0,
                "current_files": len(current_manifest),
                "added_files": sorted(current_manifest),
                "removed_files": [],
                "changed_files": [],
            }

        metadata = self._load_metadata()
        cached_manifest = self.load_cached_source_manifest()
        cached_hash = metadata.get("source_manifest_hash") or (
            self._source_manifest_hash(cached_manifest) if cached_manifest else ""
        )

        cached_paths = set(cached_manifest)
        current_paths = set(current_manifest)
        added_files = sorted(current_paths - cached_paths)
        removed_files = sorted(cached_paths - current_paths)
        changed_files = sorted(
            path
            for path in cached_paths & current_paths
            if self._manifest_digest_tuple(cached_manifest[path])
            != self._manifest_digest_tuple(current_manifest[path])
        )

        if not cached_hash:
            reason = "missing_source_manifest"
        elif cached_hash != current_hash:
            reason = "source_changed"
        else:
            reason = "fresh"

        return {
            "stale": reason != "fresh",
            "reason": reason,
            "cached_hash": cached_hash,
            "current_hash": current_hash,
            "cached_files": len(cached_manifest),
            "current_files": len(current_manifest),
            "added_files": added_files,
            "removed_files": removed_files,
            "changed_files": changed_files,
        }

    def is_cache_stale(self, project_name: str | None = None) -> bool:
        """Return True when trie_cache.db no longer matches dictionary sources."""
        return bool(self.source_cache_status(project_name)["stale"])

    def _load_metadata(self) -> dict[str, str]:
        if not self.db_path.exists():
            return {}
        conn: sqlite3.Connection | None = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            rows = conn.execute("SELECT key, value FROM metadata").fetchall()
        except sqlite3.Error:
            return {}
        finally:
            if conn is not None:
                conn.close()
        return {str(key): str(value or "") for key, value in rows}

    def _build_source_manifest(
        self,
        scan_dirs: list[tuple[Path, int]],
    ) -> dict[str, dict[str, object]]:
        manifest: dict[str, dict[str, object]] = {}
        for filepath in self._iter_manifest_source_files(scan_dirs):
            stat = filepath.stat()
            relpath = self._manifest_relpath(filepath)
            manifest[relpath] = {
                "size": stat.st_size,
                "modified_ns": stat.st_mtime_ns,
                "sha256": self._file_sha256(filepath),
            }
        return dict(sorted(manifest.items()))

    def _iter_manifest_source_files(self, scan_dirs: list[tuple[Path, int]]) -> Iterator[Path]:
        seen: set[Path] = set()
        for scan_dir, _priority in scan_dirs:
            if not scan_dir.exists():
                continue
            for filepath in sorted(scan_dir.rglob("*.md")):
                resolved = filepath.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                yield filepath

    def _manifest_relpath(self, filepath: Path) -> str:
        try:
            return filepath.resolve().relative_to(self.dict_root.resolve()).as_posix()
        except ValueError:
            return filepath.resolve().as_posix()

    @staticmethod
    def _file_sha256(filepath: Path) -> str:
        digest = hashlib.sha256()
        with open(filepath, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _source_manifest_hash(manifest: dict[str, dict[str, object]]) -> str:
        digest_payload = {
            path: DictionaryCompiler._manifest_digest_tuple(item)
            for path, item in sorted(manifest.items())
        }
        payload = json.dumps(digest_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _manifest_digest_tuple(item: dict[str, object]) -> tuple[int, str]:
        return (
            int(item.get("size", 0) or 0),
            str(item.get("sha256", "") or ""),
        )
    
    def _merge_entry(self, entries: dict, entry: DictEntry, stats: dict):
        """Merge entry into entries dict, respecting priority and locked status."""
        stats["entries_total"] += 1
        stats["priority_breakdown"][entry.priority] = stats["priority_breakdown"].get(entry.priority, 0) + 1
        
        existing = entries.get(entry.source)
        
        if existing is None:
            entries[entry.source] = entry
        elif existing.locked:
            # Locked entries cannot be overridden
            pass
        elif entry.priority > existing.priority:
            # Higher priority wins
            entries[entry.source] = entry
        elif entry.priority == existing.priority and entry.locked:
            # Same priority but new entry is locked → it wins
            entries[entry.source] = entry
    
    def _write_sqlite(
        self,
        entries: dict[str, DictEntry],
        patterns: list[GrammarPattern],
        reference_entries: list[DictEntry],
        normalization_rules: list[NormalizationRule],
        audit_events: list[AuditEvent],
        reading_seed_entries: list[DictEntry],
        source_manifest: dict[str, dict[str, object]],
    ) -> int:
        """Write compiled data to SQLite database."""
        # Remove old DB
        if self.db_path.exists():
            self._remove_existing_db_with_retry()
        
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        # Create tables
        c.execute("""
            CREATE TABLE entries (
                source TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 2,
                category TEXT DEFAULT '',
                one_mean INTEGER DEFAULT 0,
                locked INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                source_file TEXT DEFAULT '',
                source_language TEXT DEFAULT 'zh',
                target_language TEXT DEFAULT 'vi',
                entry_role TEXT DEFAULT 'translation',
                metadata_json TEXT DEFAULT '',
                -- Phase 09 Metadata
                pos_tag TEXT DEFAULT NULL,
                pos_sub TEXT DEFAULT NULL,
                entity_type TEXT DEFAULT NULL,
                pinyin TEXT DEFAULT NULL,
                traditional TEXT DEFAULT NULL,
                is_function_word INTEGER DEFAULT 0,
                luat_nhan_trigger INTEGER DEFAULT 0,
                reorder_role TEXT DEFAULT NULL,
                cultural_origin TEXT DEFAULT NULL,
                genre_affinity TEXT DEFAULT NULL,
                register_level TEXT DEFAULT NULL
            )
        """)

        c.execute("""
            CREATE TABLE reference_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 1,
                category TEXT DEFAULT '',
                one_mean INTEGER DEFAULT 0,
                locked INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                source_file TEXT DEFAULT '',
                source_language TEXT DEFAULT '',
                target_language TEXT DEFAULT '',
                entry_role TEXT DEFAULT 'reference',
                metadata_json TEXT DEFAULT '',
                -- Phase 09 Metadata
                pos_tag TEXT DEFAULT NULL,
                pos_sub TEXT DEFAULT NULL,
                entity_type TEXT DEFAULT NULL,
                pinyin TEXT DEFAULT NULL,
                traditional TEXT DEFAULT NULL,
                is_function_word INTEGER DEFAULT 0,
                luat_nhan_trigger INTEGER DEFAULT 0,
                reorder_role TEXT DEFAULT NULL,
                cultural_origin TEXT DEFAULT NULL,
                genre_affinity TEXT DEFAULT NULL,
                register_level TEXT DEFAULT NULL
            )
        """)
        
        c.execute("""
            CREATE TABLE grammar_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                replacement TEXT NOT NULL,
                category TEXT DEFAULT '',
                source_file TEXT DEFAULT '',
                pattern_key TEXT NOT NULL
            )
        """)
        
        c.execute("""
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        c.execute("""
            CREATE TABLE normalization_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                target_text TEXT DEFAULT '',
                rule_type TEXT DEFAULT 'replace',
                notes TEXT DEFAULT '',
                source_file TEXT DEFAULT ''
            )
        """)

        c.execute("""
            CREATE TABLE entry_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                pinyin TEXT DEFAULT '',
                han_viet_readings TEXT DEFAULT '',
                category TEXT DEFAULT '',
                source_file TEXT DEFAULT '',
                entry_role TEXT DEFAULT ''
            )
        """)

        c.execute("""
            CREATE TABLE audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry TEXT NOT NULL,
                action TEXT DEFAULT '',
                user_name TEXT DEFAULT '',
                updated_at TEXT DEFAULT '',
                source_dict TEXT DEFAULT '',
                source_file TEXT DEFAULT ''
            )
        """)
        
        # Insert entries
        c.executemany(
            "INSERT INTO entries (source, target, priority, category, one_mean, locked, notes, source_file, source_language, target_language, entry_role, metadata_json, pos_tag, pos_sub, entity_type, pinyin, traditional, is_function_word, luat_nhan_trigger, reorder_role, cultural_origin, genre_affinity, register_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    e.source, e.target, e.priority, e.category,
                    int(e.one_mean), int(e.locked), e.notes, e.source_file,
                    e.source_language, e.target_language, e.entry_role, e.metadata_json,
                    e.pos_tag, e.pos_sub, e.entity_type, e.pinyin, e.traditional,
                    e.is_function_word, e.luat_nhan_trigger, e.reorder_role, e.cultural_origin, e.genre_affinity, e.register_level,
                )
                for e in entries.values()
            ]
        )

        c.executemany(
            "INSERT INTO reference_entries (source, target, priority, category, one_mean, locked, notes, source_file, source_language, target_language, entry_role, metadata_json, pos_tag, pos_sub, entity_type, pinyin, traditional, is_function_word, luat_nhan_trigger, reorder_role, cultural_origin, genre_affinity, register_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    e.source, e.target, e.priority, e.category,
                    int(e.one_mean), int(e.locked), e.notes, e.source_file,
                    e.source_language, e.target_language, e.entry_role, e.metadata_json,
                    e.pos_tag, e.pos_sub, e.entity_type, e.pinyin, e.traditional,
                    e.is_function_word, e.luat_nhan_trigger, e.reorder_role, e.cultural_origin, e.genre_affinity, e.register_level,
                )
                for e in reference_entries
            ]
        )
        
        # Insert grammar patterns
        for p in patterns:
            # Extract the key part (the Chinese text without {0})
            pattern_key = p.pattern.replace('{0}', '')
            c.execute(
                "INSERT INTO grammar_patterns (pattern, replacement, category, source_file, pattern_key) VALUES (?, ?, ?, ?, ?)",
                (p.pattern, p.replacement, p.category, p.source_file, pattern_key)
            )

        c.executemany(
            "INSERT INTO normalization_rules (source_text, target_text, rule_type, notes, source_file) VALUES (?, ?, ?, ?, ?)",
            [
                (r.source_text, r.target_text, r.rule_type, r.notes, r.source_file)
                for r in normalization_rules
            ]
        )

        reading_rows = self._collect_entry_readings(reading_seed_entries)
        c.executemany(
            "INSERT INTO entry_readings (source, pinyin, han_viet_readings, category, source_file, entry_role) VALUES (?, ?, ?, ?, ?, ?)",
            reading_rows
        )

        c.executemany(
            "INSERT INTO audit_events (entry, action, user_name, updated_at, source_dict, source_file) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (e.entry, e.action, e.user_name, e.updated_at, e.source_dict, e.source_file)
                for e in audit_events
            ]
        )
        
        # Create indices
        c.execute("CREATE INDEX idx_source ON entries(source)")
        c.execute("CREATE INDEX idx_priority ON entries(priority)")
        c.execute("CREATE INDEX idx_reference_source ON reference_entries(source)")
        c.execute("CREATE INDEX idx_reference_langs ON reference_entries(source_language, target_language)")
        c.execute("CREATE INDEX idx_pattern_key ON grammar_patterns(pattern_key)")
        c.execute("CREATE INDEX idx_normalization_type ON normalization_rules(rule_type)")
        c.execute("CREATE INDEX idx_normalization_source ON normalization_rules(source_text)")
        c.execute("CREATE INDEX idx_entry_readings_source ON entry_readings(source)")
        c.execute("CREATE INDEX idx_audit_entry ON audit_events(entry)")
        c.execute("CREATE INDEX idx_audit_source_dict ON audit_events(source_dict)")
        
        # Store metadata
        import datetime
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("compiled_at", datetime.datetime.now().isoformat()))
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("entries_count", str(len(entries))))
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("reference_entries_count", str(len(reference_entries))))
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("patterns_count", str(len(patterns))))
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("normalization_rules_count", str(len(normalization_rules))))
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("audit_events_count", str(len(audit_events))))
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("entry_readings_count", str(len(reading_rows))))
        c.execute(
            "INSERT INTO metadata VALUES (?, ?)",
            (
                "source_manifest_json",
                json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            ),
        )
        c.execute("INSERT INTO metadata VALUES (?, ?)", ("source_manifest_hash", self._source_manifest_hash(source_manifest)))
        
        conn.commit()
        conn.close()
        return len(reading_rows)

    def _collect_entry_readings(
        self,
        reading_seed_entries: list[DictEntry],
    ) -> list[tuple[str, str, str, str, str, str]]:
        """Collect reading rows from runtime and reference entries."""
        rows: list[tuple[str, str, str, str, str, str]] = []

        def add_entry(entry: DictEntry):
            pinyin = ""
            han_viet = ""

            if entry.metadata_json:
                try:
                    meta = json.loads(entry.metadata_json)
                except json.JSONDecodeError:
                    meta = {}
                pinyin = str(meta.get("pinyin", "") or "").strip()
                han_viet = str(meta.get("han_viet_readings", "") or "").strip()

            if not pinyin and entry.pinyin:
                pinyin = entry.pinyin.strip()

            if not han_viet and entry.category == "phien_am":
                han_viet = entry.target.strip()

            if not pinyin and not han_viet:
                return

            rows.append((
                entry.source,
                pinyin,
                han_viet,
                entry.category,
                entry.source_file,
                entry.entry_role,
            ))

        for entry in reading_seed_entries:
            add_entry(entry)

        return rows

    def _remove_existing_db_with_retry(self, attempts: int = 10, delay_seconds: float = 0.5):
        """Remove existing DB file with retries for transient Windows file locks."""
        last_error = None
        for attempt in range(attempts):
            try:
                os.remove(self.db_path)
                return
            except PermissionError as exc:
                last_error = exc
                if attempt == attempts - 1:
                    raise
                time.sleep(delay_seconds)
        if last_error:
            raise last_error
    
    def _write_lookup_index(self, entries: dict[str, DictEntry]):
        """Write a JSON lookup index for UI fast search."""
        # Only include first 50K entries sorted by priority desc, then alphabetically
        sorted_entries = sorted(
            entries.values(),
            key=lambda e: (-e.priority, e.source),
        )[:50000]
        
        index = [
            {"s": e.source, "t": e.effective_target, "p": e.priority}
            for e in sorted_entries
        ]
        
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, separators=(',', ':'))


# ─────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Compile MD dictionaries to SQLite")
    parser.add_argument("--dict-root", default=str(Path(__file__).resolve().parents[2] / "data" / "dictionaries"))
    parser.add_argument("--project", default=None, help="Project name for project-specific dictionaries")
    
    args = parser.parse_args()
    
    compiler = DictionaryCompiler(args.dict_root)
    stats = compiler.compile(project_name=args.project)
    
    print("\nCompilation Stats:")
    print(f"   Files processed: {stats['files_processed']}")
    print(f"   Total entries: {stats['entries_total']:,}")
    print(f"   Unique entries: {stats['entries_unique']:,}")
    print(f"   Reference entries: {stats['reference_entries']:,}")
    print(f"   Grammar patterns: {stats['grammar_patterns']:,}")
    print(f"   Normalization rules: {stats['normalization_rules']:,}")
    print(f"   Audit events: {stats['audit_events']:,}")
    print(f"   Entry readings: {stats['entry_readings']:,}")
    print(f"   PhienAm runtime before reduction: {stats['phienam_runtime_before_reduction']:,}")
    print(f"   PhienAm runtime after reduction: {stats['phienam_runtime_after_reduction']:,}")
    print(f"   PhienAm runtime pruned: {stats['phienam_runtime_pruned']:,}")
    print(f"   Priority breakdown: {stats['priority_breakdown']}")
    print(f"   Time: {stats['compile_time_seconds']}s")
    print(f"   DB: {compiler.db_path}")


if __name__ == "__main__":
    main()
