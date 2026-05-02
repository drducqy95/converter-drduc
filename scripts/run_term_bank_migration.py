#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import all name_project markdown glossaries into the JSONL term bank."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.md_to_jsonl_converter import FILE_UNIVERSE_HINTS, MigratedTerm, parse_markdown_file

DEFAULT_SOURCE_ROOT = REPO_ROOT / "name_project"
DEFAULT_TERM_BANK_ROOT = REPO_ROOT / "data" / "term_bank"


def discover_source_files(source_root: Path) -> list[Path]:
    return sorted(path for path in source_root.rglob("*.md") if path.is_file())


def route_record(record: MigratedTerm, term_bank_root: Path) -> Path:
    if record.scope == "global" and record.universe == "real_world":
        return term_bank_root / "global" / "real_world.jsonl"
    if record.scope == "global":
        category = record.entity_type or "terms"
        return term_bank_root / "global" / f"{category}.jsonl"
    return term_bank_root / "universes" / record.universe / "terms.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def primary_key(row: dict) -> tuple[str, str]:
    return str(row.get("source") or "").strip(), str(row.get("universe") or "").strip()


def is_generated(row: dict) -> bool:
    return str(row.get("source_dict") or "").startswith("md_to_jsonl:")


def merge_records(existing: list[dict], new: list[dict]) -> list[dict]:
    """Merge records by (source, universe), preserving manual curated rows."""

    by_key: dict[tuple[str, str], dict] = {}
    order: list[tuple[str, str]] = []
    for row in existing:
        if is_generated(row):
            continue
        key = primary_key(row)
        if not key[0]:
            continue
        if key not in by_key:
            order.append(key)
        by_key[key] = row

    for row in new:
        key = primary_key(row)
        if not key[0]:
            continue
        current = by_key.get(key)
        if current is None:
            order.append(key)
            by_key[key] = row
            continue
        current_conf = float(current.get("confidence") or 0.0)
        new_conf = float(row.get("confidence") or 0.0)
        if is_generated(current) or current_conf < new_conf:
            by_key[key] = row

    return [by_key[key] for key in order if key in by_key]


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda row: (str(row.get("source") or ""), str(row.get("universe") or "")))
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in ordered) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp_path, path)
    return len(ordered)


def run_migration(
    *,
    source_root: Path = DEFAULT_SOURCE_ROOT,
    term_bank_root: Path = DEFAULT_TERM_BANK_ROOT,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    source_files = discover_source_files(source_root)
    grouped: dict[Path, list[dict]] = defaultdict(list)
    per_file: dict[str, int] = {}
    warnings: list[str] = []

    for path in source_files:
        records = parse_markdown_file(path)
        per_file[str(path.relative_to(REPO_ROOT))] = len(records)
        for record in records:
            grouped[route_record(record, term_bank_root)].append(asdict(record))
        if path.stem not in FILE_UNIVERSE_HINTS:
            warnings.append(f"No explicit universe hint for {path.relative_to(REPO_ROOT)}")

    written: dict[str, int] = {}
    preserved = 0
    added_or_replaced = 0
    for path, new_rows in sorted(grouped.items(), key=lambda item: str(item[0])):
        existing = load_jsonl(path)
        merged = merge_records(existing, new_rows)
        existing_keys = {primary_key(row) for row in existing if not is_generated(row)}
        new_keys = {primary_key(row) for row in new_rows}
        preserved += len(existing_keys - new_keys)
        added_or_replaced += len(new_keys)
        if not dry_run:
            written[str(path.relative_to(REPO_ROOT))] = write_jsonl(path, merged)
        else:
            written[str(path.relative_to(REPO_ROOT))] = len(merged)

    report = {
        "source_files_scanned": len(source_files),
        "records_parsed": sum(per_file.values()),
        "outputs": written,
        "per_file": per_file,
        "existing_records_preserved": preserved,
        "records_added_or_replaced": added_or_replaced,
        "warnings": warnings,
        "dry_run": dry_run,
    }

    if verbose:
        print("=== Term Bank Migration Report ===")
        print(f"Source files scanned: {report['source_files_scanned']}")
        print(f"Total records parsed: {report['records_parsed']}")
        print("\nPer-file breakdown:")
        for name, count in per_file.items():
            print(f"  {name}: {count}")
        print("\nOutput files:")
        for name, count in written.items():
            print(f"  {name}: {count}")
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Import all name_project markdown files into data/term_bank")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--term-bank-root", type=Path, default=DEFAULT_TERM_BANK_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    run_migration(
        source_root=args.source_root,
        term_bank_root=args.term_bank_root,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
