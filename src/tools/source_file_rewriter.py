#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for syncing compiled dictionary edits back to Markdown source files."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import yaml

from src.core.md_dictionary_compiler import _TABLE_ROW_RE, _SEPARATOR_RE, _read_md_file, _split_md_row


DEFAULT_DICT_ROOT = Path(__file__).resolve().parents[2] / "data" / "dictionaries"


def resolve_dictionary_source_path(
    source_file: str,
    *,
    dict_root: str | Path | None = None,
    category: str | None = None,
) -> Path | None:
    normalized_name = str(source_file or "").strip()
    if not normalized_name:
        return None

    root = Path(dict_root or DEFAULT_DICT_ROOT).expanduser().resolve()
    direct = root / normalized_name
    if direct.exists():
        return direct

    candidates = sorted(root.rglob(normalized_name))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    category_tokens = [token for token in str(category or "").lower().split("_") if token]

    def score(path: Path) -> tuple[int, int, str]:
        path_text = str(path.relative_to(root)).lower()
        token_hits = sum(1 for token in category_tokens if token in path_text)
        depth = len(path.parts)
        return (-token_hits, depth, path_text)

    return sorted(candidates, key=score)[0]


def build_entry_metadata_payload(entry: dict) -> dict[str, object]:
    metadata: dict[str, object] = {}
    for key in (
        "pos_sub",
        "entity_type",
        "is_function_word",
        "luat_nhan_trigger",
        "reorder_role",
        "cultural_origin",
        "genre_affinity",
        "register_level",
        "full_explanation",
        "hit_count",
        "han_viet_readings",
    ):
        value = entry.get(key)
        if value is None or value == "" or value == []:
            continue
        metadata[key] = value
    return metadata


def update_dictionary_source_entry(
    *,
    dict_root: str | Path | None,
    source_file: str,
    source_text: str,
    entry: dict,
) -> Path | None:
    source_path = resolve_dictionary_source_path(source_file, dict_root=dict_root, category=entry.get("source_dict"))
    if source_path is None or not source_path.exists():
        return None

    metadata, body = _read_md_file(str(source_path))
    if metadata.get("type") == "bulk_dictionary":
        changed = _update_bulk_dictionary_row(source_path, source_text, entry)
    else:
        changed = _update_rich_dictionary_file(source_path, source_text, metadata, body, entry)
    return source_path if changed else source_path


def _update_bulk_dictionary_row(filepath: Path, source_text: str, entry: dict) -> bool:
    lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    rewritten: list[str] = []
    data_started = False
    changed = False

    for line in lines:
        stripped = line.strip()
        match = _TABLE_ROW_RE.match(stripped)
        if not match:
            rewritten.append(line)
            continue
        if _SEPARATOR_RE.match(stripped):
            rewritten.append(line)
            continue

        cells = _split_md_row(match.group(1))
        if not cells:
            rewritten.append(line)
            continue

        first_cell = cells[0].strip()
        if not data_started:
            data_started = True
            rewritten.append(line)
            continue

        if first_cell != source_text:
            rewritten.append(line)
            continue

        new_line = _render_bulk_dictionary_row(entry)
        rewritten.append(new_line)
        changed = changed or (new_line != line)
    if changed:
        filepath.write_text("".join(rewritten), encoding="utf-8")
    return changed


def _render_bulk_dictionary_row(entry: dict) -> str:
    metadata_json = json.dumps(build_entry_metadata_payload(entry), ensure_ascii=False, separators=(",", ":"))
    cells = [
        entry.get("source", ""),
        entry.get("target_vi", ""),
        entry.get("priority", ""),
        entry.get("source_dict", ""),
        entry.get("pos_tag", "") or "",
        entry.get("pinyin", "") or "",
        entry.get("traditional", "") or "",
        metadata_json if metadata_json != "{}" else "",
    ]
    escaped = [_escape_md_cell(cell) for cell in cells]
    return f"| {' | '.join(escaped)} |\n"


def _update_rich_dictionary_file(
    filepath: Path,
    source_text: str,
    metadata: dict,
    body: str,
    entry: dict,
) -> bool:
    if str(metadata.get("source", "")).strip() != source_text:
        return False

    next_metadata = dict(metadata)
    next_metadata["source"] = entry.get("source", source_text)
    next_metadata["target"] = entry.get("target_vi", "")
    next_metadata["priority"] = int(entry.get("priority", metadata.get("priority", 0)) or 0)
    next_metadata["category"] = entry.get("source_dict", metadata.get("category", ""))
    if entry.get("notes"):
        next_metadata["notes"] = entry.get("notes")
    elif "notes" in next_metadata:
        next_metadata.pop("notes")

    for key in (
        "pos_tag",
        "pos_sub",
        "entity_type",
        "pinyin",
        "traditional",
        "reorder_role",
        "cultural_origin",
        "genre_affinity",
        "register_level",
    ):
        value = entry.get(key)
        if value is None or value == "":
            next_metadata.pop(key, None)
        else:
            next_metadata[key] = value

    if entry.get("luat_nhan_trigger"):
        next_metadata["luat_nhan_trigger"] = True
    else:
        next_metadata.pop("luat_nhan_trigger", None)

    if entry.get("is_function_word"):
        next_metadata["is_function_word"] = True
    else:
        next_metadata.pop("is_function_word", None)

    yaml_text = yaml.safe_dump(next_metadata, allow_unicode=True, sort_keys=False).strip()
    rendered = f"---\n{yaml_text}\n---\n"
    if body.strip():
        rendered = f"{rendered}\n{body.lstrip()}"

    current = filepath.read_text(encoding="utf-8")
    if current == rendered:
        return False
    filepath.write_text(rendered, encoding="utf-8")
    return True


def _escape_md_cell(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace("|", "\\|")
    text = text.replace("\n", "<br>")
    return text


def rewrite_file(filepath: str, db_cursor: sqlite3.Cursor):
    with open(filepath, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    rewritten_lines: list[str] = []
    changes_made = 0
    header_found = False

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            rewritten_lines.append(line)
            continue

        if "---" in stripped and stripped.count("|") >= 2:
            separator = "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            if line != separator:
                rewritten_lines.append(separator)
                changes_made += 1
            else:
                rewritten_lines.append(line)
            continue

        stripped_lower = stripped.lower()
        if "source" in stripped_lower and "target" in stripped_lower:
            if not header_found:
                header = "| Source | Target | Priority | Category | POS_Tag | Pinyin | Traditional | Metadata |\n"
                if line != header:
                    rewritten_lines.append(header)
                    changes_made += 1
                else:
                    rewritten_lines.append(line)
                header_found = True
            continue

        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if not parts or not parts[0]:
            rewritten_lines.append(line)
            continue

        source = parts[0]
        db_cursor.execute(
            """
            SELECT source, target, priority, category, pos_tag, pos_sub, entity_type,
                   pinyin, traditional, is_function_word, luat_nhan_trigger, reorder_role,
                   cultural_origin, register_level, notes, metadata_json
            FROM entries WHERE source = ?
            """,
            (source,),
        )
        row = db_cursor.fetchone()
        if not row:
            rewritten_lines.append(line)
            continue

        metadata_json = row[15] or ""
        try:
            metadata = json.loads(metadata_json) if metadata_json else {}
        except json.JSONDecodeError:
            metadata = {}
        metadata.update({
            "pos_sub": row[5],
            "entity_type": row[6],
            "is_function_word": row[9],
            "luat_nhan_trigger": row[10],
            "reorder_role": row[11],
            "cultural_origin": row[12],
            "register_level": row[13],
        })
        metadata = {key: value for key, value in metadata.items() if value not in (None, "", 0)}
        row_payload = {
            "source": row[0],
            "target_vi": row[1],
            "priority": row[2],
            "source_dict": row[3],
            "pos_tag": row[4],
            "pinyin": row[7],
            "traditional": row[8],
            "notes": row[14],
            "metadata": metadata,
            **metadata,
        }
        new_line = _render_bulk_dictionary_row(row_payload)
        if new_line != line:
            changes_made += 1
        rewritten_lines.append(new_line)

    if changes_made > 0:
        with open(filepath, "w", encoding="utf-8") as handle:
            handle.writelines(rewritten_lines)
    return changes_made


def run():
    db_path = DEFAULT_DICT_ROOT / "_compiled" / "trie_cache.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    md_files = list(DEFAULT_DICT_ROOT.rglob("*.md"))
    print(f"Discovered {len(md_files)} Markdown files. Rewriting to 8-column format...")

    total_changes = 0
    files_changed = 0
    for markdown_file in md_files:
        try:
            changes = rewrite_file(str(markdown_file), cursor)
            if changes > 0:
                print(f"  [MODIFIED] {markdown_file.name}: {changes} rows rewritten.")
                files_changed += 1
                total_changes += changes
        except Exception as exc:
            print(f"  [ERROR] Failed to rewrite {markdown_file.name}: {exc}")

    conn.close()
    print("\nFinished Rewriting!")
    print(f"Modified {files_changed} files, {total_changes} total rows updating to final metadata format.")


if __name__ == "__main__":
    run()
