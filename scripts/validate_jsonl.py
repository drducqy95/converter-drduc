#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate and optionally fix term-bank JSONL files."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.pipeline.term_bank import ENTITY_TYPES


REQUIRED_FIELDS = ("source", "target", "entity_type")
ALLOWED_TYPES = set(ENTITY_TYPES)


@dataclass(slots=True)
class FileValidation:
    path: Path
    records: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fixed: bool = False


def iter_jsonl_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(path for path in root.rglob("*.jsonl") if path.is_file())


def validate_file(path: Path, *, fix: bool = False) -> FileValidation:
    result = FileValidation(path=path)
    rows: list[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if fix and stripped != line:
                result.fixed = True
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            result.errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(payload, dict):
            result.errors.append(f"line {line_no}: record is not an object")
            continue

        normalized, changed = normalize_record(payload)
        if changed:
            result.fixed = True
        validate_record(normalized, line_no=line_no, result=result)

        key = (str(normalized.get("source") or ""), str(normalized.get("universe") or ""))
        if key in seen_keys:
            message = f"line {line_no}: duplicate primary key {key[0]}|{key[1]}"
            if fix:
                result.warnings.append(message + " (removed)")
                result.fixed = True
                continue
            result.errors.append(message)
        seen_keys.add(key)
        rows.append(normalized)

    result.records = len(rows)
    if fix and result.fixed and not result.errors:
        write_rows(path, rows)
    return result


def normalize_record(row: dict) -> tuple[dict, bool]:
    fixed = dict(row)
    changed = False
    for key in ("source", "target", "entity_type", "scope", "universe", "status"):
        if key in fixed and isinstance(fixed[key], str):
            stripped = fixed[key].strip()
            if stripped != fixed[key]:
                fixed[key] = stripped
                changed = True
    if "confidence" not in fixed:
        fixed["confidence"] = 0.86
        changed = True
    else:
        try:
            confidence = float(fixed.get("confidence") or 0.86)
        except (TypeError, ValueError):
            confidence = 0.86
        clamped = min(max(confidence, 0.0), 1.0)
        if fixed.get("confidence") != clamped:
            fixed["confidence"] = clamped
            changed = True
    if "entity_type" in fixed:
        entity_type = str(fixed.get("entity_type") or "term").strip() or "term"
        if entity_type != fixed.get("entity_type"):
            fixed["entity_type"] = entity_type
            changed = True
    return fixed, changed


def validate_record(row: dict, *, line_no: int, result: FileValidation) -> None:
    for field_name in REQUIRED_FIELDS:
        if not str(row.get(field_name) or "").strip():
            result.errors.append(f"line {line_no}: missing required field {field_name}")
    entity_type = str(row.get("entity_type") or "")
    if entity_type and entity_type not in ALLOWED_TYPES:
        result.errors.append(f"line {line_no}: invalid entity_type {entity_type}")
    confidence = row.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        result.errors.append(f"line {line_no}: confidence out of range")
    if str(row.get("scope") or "") == "universe" and not str(row.get("universe") or "").strip():
        result.errors.append(f"line {line_no}: universe scope requires universe")


def write_rows(path: Path, rows: list[dict]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp_path, path)


def validate_root(root: Path, *, fix: bool = False) -> tuple[list[FileValidation], list[str]]:
    results = [validate_file(path, fix=fix) for path in iter_jsonl_files(root)]
    cross_seen: dict[tuple[str, str], Path] = {}
    cross_warnings: list[str] = []
    for result in results:
        if result.errors:
            continue
        for line in result.path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            row = json.loads(stripped)
            key = (str(row.get("source") or ""), str(row.get("universe") or ""))
            if not key[0]:
                continue
            previous = cross_seen.get(key)
            if previous and previous != result.path:
                cross_warnings.append(
                    f"duplicate primary key across files {key[0]}|{key[1]}: {previous} and {result.path}"
                )
            else:
                cross_seen[key] = result.path
    return results, cross_warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate term-bank JSONL files")
    parser.add_argument("path", type=Path)
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()

    results, cross_warnings = validate_root(args.path, fix=args.fix)
    total_records = sum(item.records for item in results)
    total_errors = sum(len(item.errors) for item in results)
    total_warnings = sum(len(item.warnings) for item in results) + len(cross_warnings)

    for item in results:
        rel = item.path
        if item.errors:
            print(f"ERROR {rel}: {item.records} records, {len(item.errors)} errors")
            for error in item.errors[:8]:
                print(f"  - {error}")
        elif item.warnings:
            print(f"WARN  {rel}: {item.records} records, {len(item.warnings)} warnings")
        else:
            fixed = " fixed" if item.fixed else ""
            print(f"OK    {rel}: {item.records} records{fixed}")

    for warning in cross_warnings[:20]:
        print(f"WARN  {warning}")
    if len(cross_warnings) > 20:
        print(f"WARN  ... {len(cross_warnings) - 20} more cross-file duplicate warnings")

    print("\nSummary:")
    print(f"  Total files: {len(results)}")
    print(f"  Total records: {total_records}")
    print(f"  Warnings: {total_warnings}")
    print(f"  Errors: {total_errors}")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
