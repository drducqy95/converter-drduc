#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
migrate_qt_to_md.py — Quick Translator TXT → Markdown Dictionary Format (MDE)

Converts all 22 QT data files into structured Markdown dictionaries:
- Bulk MD format for large files (YAML frontmatter + MD table)
- Grammar MD for LuatNhan patterns
- Rich entries for ThieuChuu (detailed single-char lookups)

Usage:
    python scripts/migrate_qt_to_md.py [--source DIR] [--output DIR] [--validate]
"""

import os
import sys
import argparse
import datetime
import json
import re
from pathlib import Path
from collections import OrderedDict

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ─────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────

DEFAULT_QT_DATA = r"D:\APP\Quick Translator 2020\Data"
DEFAULT_OUTPUT = str(PROJECT_ROOT / "data" / "dictionaries")

TODAY = datetime.date.today().isoformat()

# BOM character to strip
BOM = '\ufeff'


# ─────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────

def read_qt_file(filepath: str) -> list[str]:
    """Read QT data file, auto-strip BOM, return list of non-empty lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Strip BOM from first line
    if lines and lines[0].startswith(BOM):
        lines[0] = lines[0][len(BOM):]
    
    return [line.rstrip('\r\n') for line in lines if line.strip()]


def parse_kv_line(line: str) -> tuple[str, str] | None:
    """Parse a 'key=value' line. Returns (key, value) or None if invalid."""
    idx = line.find('=')
    if idx == -1:
        return None
    key = line[:idx].strip()
    value = line[idx + 1:].strip()
    if not key:
        return None
    return key, value


def escape_pipe(text: str) -> str:
    """Escape pipe characters for MD table cells."""
    return text.replace('|', '\\|').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')


def _yaml_scalar(value) -> str:
    """Format a simple scalar value for YAML frontmatter."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def write_bulk_md(
    filepath: str,
    source_lang: str,
    target_lang: str,
    priority: int,
    category: str,
    compiled_from: str,
    entries: list[tuple[str, str]],
    extra_columns: list[str] | None = None,
    extra_data: list[list[str]] | None = None,
    notes: str = "",
    entry_role: str | None = None,
    extra_frontmatter: dict | None = None,
):
    """Write a Bulk MD dictionary file with YAML frontmatter + MD table."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # YAML frontmatter
        f.write("---\n")
        f.write(f'type: bulk_dictionary\n')
        f.write(f'source_language: {source_lang}\n')
        f.write(f'target_language: {target_lang}\n')
        f.write(f'priority: {priority}\n')
        f.write(f'category: {category}\n')
        f.write(f'entries_count: {len(entries)}\n')
        f.write(f'compiled_from: "{compiled_from}"\n')
        f.write(f'last_compiled: "{TODAY}"\n')
        if entry_role:
            f.write(f'entry_role: {entry_role}\n')
        if extra_frontmatter:
            for key, value in extra_frontmatter.items():
                f.write(f"{key}: {_yaml_scalar(value)}\n")
        if notes:
            f.write(f'notes: "{notes}"\n')
        f.write("---\n\n")
        
        # Table header
        if extra_columns:
            cols = ["source", "target"] + extra_columns
        else:
            cols = ["source", "target"]
        
        f.write("| " + " | ".join(cols) + " |\n")
        f.write("| " + " | ".join(["---"] * len(cols)) + " |\n")
        
        # Table rows
        for i, (src, tgt) in enumerate(entries):
            row = [escape_pipe(src), escape_pipe(tgt)]
            if extra_data and i < len(extra_data):
                row.extend([escape_pipe(d) for d in extra_data[i]])
            elif extra_columns:
                row.extend([""] * len(extra_columns))
            f.write("| " + " | ".join(row) + " |\n")
    
    return len(entries)


def write_grammar_md(
    filepath: str,
    category: str,
    compiled_from: str,
    patterns: list[tuple[str, str]],
    notes: str = "",
):
    """Write a grammar/pattern MD file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f'type: grammar_patterns\n')
        f.write(f'category: {category}\n')
        f.write(f'patterns_count: {len(patterns)}\n')
        f.write(f'compiled_from: "{compiled_from}"\n')
        f.write(f'last_compiled: "{TODAY}"\n')
        if notes:
            f.write(f'notes: "{notes}"\n')
        f.write("---\n\n")
        
        f.write("| pattern | replacement |\n")
        f.write("| --- | --- |\n")
        for pat, rep in patterns:
            f.write(f"| {escape_pipe(pat)} | {escape_pipe(rep)} |\n")
    
    return len(patterns)


def write_normalization_md(
    filepath: str,
    compiled_from: str,
    rules: list[tuple[str, str]],
    rule_type: str,
    notes: str = "",
):
    """Write normalization rules into a Markdown table."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("type: normalization_rules\n")
        f.write(f'rule_type: {rule_type}\n')
        f.write(f'rules_count: {len(rules)}\n')
        f.write(f'compiled_from: "{compiled_from}"\n')
        f.write(f'last_compiled: "{TODAY}"\n')
        if notes:
            f.write(f'notes: "{notes}"\n')
        f.write("---\n\n")

        f.write("| source | target | rule_type |\n")
        f.write("| --- | --- | --- |\n")
        for src, tgt in rules:
            f.write(f"| {escape_pipe(src)} | {escape_pipe(tgt)} | {rule_type} |\n")

    return len(rules)


def write_audit_md(
    filepath: str,
    compiled_from: str,
    source_dict: str,
    events: list[tuple[str, str, str, str]],
    notes: str = "",
):
    """Write audit history events into a Markdown table."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("type: audit_events\n")
        f.write(f'source_dict: "{source_dict}"\n')
        f.write(f'events_count: {len(events)}\n')
        f.write(f'compiled_from: "{compiled_from}"\n')
        f.write(f'last_compiled: "{TODAY}"\n')
        if notes:
            f.write(f'notes: "{notes}"\n')
        f.write("---\n\n")

        f.write("| entry | action | user_name | updated_at | source_dict |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for entry, action, user_name, updated_at in events:
            f.write(
                "| "
                + " | ".join([
                    escape_pipe(entry),
                    escape_pipe(action),
                    escape_pipe(user_name),
                    escape_pipe(updated_at),
                    escape_pipe(source_dict),
                ])
                + " |\n"
            )

    return len(events)


def _normalize_embedded_text(value: str) -> str:
    """Normalize embedded QT text markers into a readable single string."""
    text = value.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\t', ' ')
    text = text.replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    return text.strip()


def _unique_preserve_order(items: list[str]) -> list[str]:
    """Return unique non-empty items preserving order."""
    seen = set()
    result = []
    for item in items:
        clean = item.strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _extract_pinyin_tokens(text: str) -> list[str]:
    """Extract pinyin-like tokens from bracket blocks."""
    matches = re.findall(r'\[([^\]]+)\]', text)
    tokens: list[str] = []
    for match in matches:
        parts = [part.strip() for part in match.split('|')]
        for part in parts:
            if part:
                tokens.append(part)
    return _unique_preserve_order(tokens)


def _extract_numbered_meanings(text: str) -> list[str]:
    """Extract numbered meanings from normalized multi-line text."""
    meanings = re.findall(r'(?:^|\n)\d+\.\s*([^\n]+)', text)
    return _unique_preserve_order(meanings)


def _extract_lacviet_han_viet(raw_text: str) -> str:
    """Extract a likely Han-Viet token from LacViet sense text."""
    raw = raw_text.strip()
    upper_match = re.match(r'([A-ZÀ-ỸĐ0-9][A-ZÀ-ỸĐ0-9 ,/\-]*)', raw)
    if upper_match:
        return upper_match.group(1).strip(" ,;/")
    return raw.split(';', 1)[0].strip()


def _extract_thieuchuu_metadata(value: str) -> dict[str, str]:
    """Parse ThieuChuu entry into metadata-rich fields."""
    text = _normalize_embedded_text(value)
    first_line = text.split('\n', 1)[0].strip()
    han_viet = first_line.split('[', 1)[0].strip(' ;,')
    pinyin = '|'.join(_extract_pinyin_tokens(text))
    meanings = _extract_numbered_meanings(text)

    if ']' in text:
        explanation = text.split(']', 1)[1].strip()
    else:
        explanation = text

    primary = han_viet.split(',', 1)[0].strip() if han_viet else ""
    if not primary and meanings:
        primary = meanings[0].split(';', 1)[0].strip()

    return {
        "target": primary or han_viet or text[:80],
        "pinyin": pinyin,
        "han_viet_readings": han_viet,
        "parsed_meanings": " ; ".join(meanings[:8]),
        "full_explanation": text,
        "notes": explanation,
    }


def _extract_lacviet_metadata(value: str) -> dict[str, str]:
    """Parse LacViet entry into metadata-rich fields."""
    text = _normalize_embedded_text(value)
    pinyin = '|'.join(_extract_pinyin_tokens(text))
    han_viet_matches = [
        _extract_lacviet_han_viet(match)
        for match in re.findall(r'Hán Việt:\s*([^\n]+)', text)
    ]
    han_viet_readings = " | ".join(_unique_preserve_order(han_viet_matches))
    meanings = _extract_numbered_meanings(text)

    first_line = text.split('\n', 1)[0].strip()
    first_line = re.sub(r'^✚\s*', '', first_line)
    first_line = re.sub(r'^\[[^\]]+\]\s*', '', first_line).strip()
    first_line = re.sub(r'^Hán Việt:\s*[^\n]+', '', first_line).strip()
    first_line = first_line.lstrip(';:,.- ').strip()

    primary = han_viet_matches[0] if han_viet_matches else ""
    if not primary and first_line:
        primary = first_line.split(';', 1)[0].strip()
    if not primary and meanings:
        primary = meanings[0].split(';', 1)[0].strip()

    return {
        "target": primary or text[:80],
        "pinyin": pinyin,
        "han_viet_readings": han_viet_readings,
        "parsed_meanings": " ; ".join(meanings[:8]),
        "full_explanation": text,
        "notes": first_line,
    }


# ─────────────────────────────────────────────────
# Migration Functions
# ─────────────────────────────────────────────────

def migrate_vietphrase(source_dir: str, output_dir: str) -> dict:
    """Migrate VietPhrase.txt (728K entries) → _bulk_vietphrase.md"""
    filepath = os.path.join(source_dir, "VietPhrase.txt")
    lines = read_qt_file(filepath)
    
    entries = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            entries.append(parsed)
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "vietphrase", "_bulk_vietphrase.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=2,
        category="vietphrase_general",
        compiled_from="VietPhrase.txt",
        entries=entries,
        notes="Main VietPhrase dictionary. Use one_mean=true to take first meaning before semicolon.",
    )
    
    return {"file": "VietPhrase.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_vietphrase2(source_dir: str, output_dir: str) -> dict:
    """Migrate VietPhrase2.txt → append or separate bulk file."""
    filepath = os.path.join(source_dir, "VietPhrase2.txt")
    if not os.path.exists(filepath):
        return {"file": "VietPhrase2.txt", "source_count": 0, "migrated": 0, "skipped": 0, "status": "NOT_FOUND"}
    
    lines = read_qt_file(filepath)
    entries = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            entries.append(parsed)
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "vietphrase", "_bulk_vietphrase2.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=2,
        category="vietphrase_supplement",
        compiled_from="VietPhrase2.txt",
        entries=entries,
        notes="VietPhrase supplement dictionary.",
    )
    
    return {"file": "VietPhrase2.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_names(source_dir: str, output_dir: str) -> dict:
    """Migrate Names.txt + Names2.txt → _bulk_names.md"""
    results = []
    all_entries = []
    
    for fname in ["Names.txt", "Names2.txt"]:
        filepath = os.path.join(source_dir, fname)
        if not os.path.exists(filepath):
            results.append({"file": fname, "status": "NOT_FOUND"})
            continue
        
        lines = read_qt_file(filepath)
        skipped = 0
        for line in lines:
            parsed = parse_kv_line(line)
            if parsed:
                all_entries.append(parsed)
            else:
                skipped += 1
        results.append({"file": fname, "source_count": len(lines), "parsed": len(lines) - skipped, "skipped": skipped})
    
    # Deduplicate: keep last occurrence (Names2 overrides Names)
    seen = {}
    for key, val in all_entries:
        seen[key] = val
    unique_entries = list(seen.items())
    
    out_path = os.path.join(output_dir, "global", "names", "_bulk_names.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=4,
        category="names_general",
        compiled_from="Names.txt + Names2.txt",
        entries=unique_entries,
        notes="Global names dictionary. Priority 4 (high).",
    )
    
    return {
        "files": results,
        "total_unique": len(unique_entries),
        "migrated": count,
        "deduped_from": len(all_entries),
    }


def migrate_phienam(source_dir: str, output_dir: str) -> dict:
    """Migrate ChinesePhienAmWords.txt (12K single-char phonetics) → _bulk_phienam.md"""
    filepath = os.path.join(source_dir, "ChinesePhienAmWords.txt")
    lines = read_qt_file(filepath)
    
    entries = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            entries.append(parsed)
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "phien_am", "_bulk_phienam.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=1,
        category="phien_am",
        compiled_from="ChinesePhienAmWords.txt",
        entries=entries,
        notes="Hán-Việt single character phonetics. Lowest priority (P1), used as fallback.",
    )
    
    return {"file": "ChinesePhienAmWords.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_thieuchuu(source_dir: str, output_dir: str) -> dict:
    """Migrate ThieuChuu.txt into a metadata-rich reference dictionary."""
    filepath = os.path.join(source_dir, "ThieuChuu.txt")
    lines = read_qt_file(filepath)
    
    entries = []
    extra_rows = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            key, value = parsed
            parsed_meta = _extract_thieuchuu_metadata(value)
            entries.append((key, parsed_meta["target"]))
            extra_rows.append([
                parsed_meta["pinyin"],
                parsed_meta["han_viet_readings"],
                parsed_meta["parsed_meanings"],
                parsed_meta["full_explanation"],
                parsed_meta["notes"],
            ])
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "phien_am", "_bulk_thieuchuu.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=1,
        category="thieuchuu_reference",
        compiled_from="ThieuChuu.txt",
        entries=entries,
        extra_columns=["pinyin", "han_viet_readings", "parsed_meanings", "full_explanation", "notes"],
        extra_data=extra_rows,
        notes="ThieuChuu metadata-rich single-character reference dictionary. Reference only; not part of ZH->VI fast-path runtime.",
        entry_role="reference",
    )
    
    return {"file": "ThieuChuu.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_lacviet(source_dir: str, output_dir: str) -> dict:
    """Migrate LacViet.txt into a metadata-rich reference dictionary."""
    filepath = os.path.join(source_dir, "LacViet.txt")
    if not os.path.exists(filepath):
        return {"file": "LacViet.txt", "status": "NOT_FOUND"}

    lines = read_qt_file(filepath)

    entries = []
    extra_rows = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            key, value = parsed
            parsed_meta = _extract_lacviet_metadata(value)
            entries.append((key, parsed_meta["target"]))
            extra_rows.append([
                parsed_meta["pinyin"],
                parsed_meta["han_viet_readings"],
                parsed_meta["parsed_meanings"],
                parsed_meta["full_explanation"],
                parsed_meta["notes"],
            ])
        else:
            skipped += 1

    out_path = os.path.join(output_dir, "global", "reference_vi", "_bulk_lacviet.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=1,
        category="lacviet_reference",
        compiled_from="LacViet.txt",
        entries=entries,
        extra_columns=["pinyin", "han_viet_readings", "parsed_meanings", "full_explanation", "notes"],
        extra_data=extra_rows,
        notes="LacViet metadata-rich reference dictionary. Reference only; not part of ZH->VI fast-path runtime.",
        entry_role="reference",
    )

    return {"file": "LacViet.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_luat_nhan(source_dir: str, output_dir: str) -> dict:
    """Migrate LuatNhan.txt (303 rules) → luat_nhan.md"""
    filepath = os.path.join(source_dir, "LuatNhan.txt")
    lines = read_qt_file(filepath)
    
    patterns = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            patterns.append(parsed)
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "grammar", "luat_nhan.md")
    count = write_grammar_md(
        out_path,
        category="luat_nhan_primary",
        compiled_from="LuatNhan.txt",
        patterns=patterns,
        notes="Primary LuatNhan patterns (303 rules). {0} = entity placeholder.",
    )
    
    return {"file": "LuatNhan.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_luat_nhan_cu(source_dir: str, output_dir: str) -> dict:
    """Migrate LuatNhancu.txt (15K templates) → luat_nhan_cu.md"""
    filepath = os.path.join(source_dir, "LuatNhancu.txt")
    lines = read_qt_file(filepath)
    
    patterns = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            patterns.append(parsed)
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "grammar", "luat_nhan_cu.md")
    count = write_grammar_md(
        out_path,
        category="luat_nhan_extended",
        compiled_from="LuatNhancu.txt",
        patterns=patterns,
        notes="Extended LuatNhan templates (15K+). Lower priority than primary LuatNhan.",
    )
    
    return {"file": "LuatNhancu.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_trichdan(source_dir: str, output_dir: str) -> dict:
    """Migrate TrichDan.txt (23K idiom/reference entries) → _bulk_trichdan.md"""
    filepath = os.path.join(source_dir, "TrichDan.txt")
    lines = read_qt_file(filepath)
    
    entries = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            key, value = parsed
            # TrichDan has very rich multi-line values (with \\n and \\t)
            clean_value = value.replace('\\n', ' ').replace('\\t', ' ').strip()
            entries.append((key, clean_value))
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "idioms", "_bulk_trichdan.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=2,
        category="trichdan_idioms",
        compiled_from="TrichDan.txt",
        entries=entries,
        notes="TrichDan idioms, references, and detailed character definitions.",
    )
    
    return {"file": "TrichDan.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_pronouns(source_dir: str, output_dir: str) -> dict:
    """Migrate Pronouns.txt (12K number conversions) → _bulk_pronouns.md"""
    filepath = os.path.join(source_dir, "Pronouns.txt")
    lines = read_qt_file(filepath)
    
    entries = []
    skipped = 0
    for line in lines:
        # Skip comment lines
        if line.startswith('#'):
            skipped += 1
            continue
        parsed = parse_kv_line(line)
        if parsed:
            entries.append(parsed)
        else:
            skipped += 1
    
    out_path = os.path.join(output_dir, "global", "numbers", "_bulk_pronouns.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="vi",
        priority=3,
        category="number_conversions",
        compiled_from="Pronouns.txt",
        entries=entries,
        notes="Chinese number → Arabic number/Vietnamese conversions. Note: 'Pronouns' is a misnomer, this is mostly number data.",
    )
    
    return {"file": "Pronouns.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_ignored_phrases(source_dir: str, output_dir: str) -> dict:
    """Migrate IgnoredChinesePhrases.txt → ignored_phrases.md"""
    filepath = os.path.join(source_dir, "IgnoredChinesePhrases.txt")
    lines = read_qt_file(filepath)
    
    phrases = []
    for line in lines:
        # These are pipe-separated phrases to ignore (e.g., website watermarks)
        clean = line.replace('|', '').strip()
        if clean:
            phrases.append((line, clean))
    
    os.makedirs(os.path.join(output_dir, "global", "grammar"), exist_ok=True)
    out_path = os.path.join(output_dir, "global", "grammar", "ignored_phrases.md")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("type: ignored_phrases\n")
        f.write(f"phrases_count: {len(phrases)}\n")
        f.write(f'compiled_from: "IgnoredChinesePhrases.txt"\n')
        f.write(f'last_compiled: "{TODAY}"\n')
        f.write('notes: "Phrases to strip from source text (website watermarks, ads)."\n')
        f.write("---\n\n")
        
        f.write("| raw_pattern | clean_text |\n")
        f.write("| --- | --- |\n")
        for raw, clean in phrases:
            f.write(f"| {escape_pipe(raw)} | {escape_pipe(clean)} |\n")
    
    return {"file": "IgnoredChinesePhrases.txt", "source_count": len(lines), "migrated": len(phrases)}


def migrate_cedict(source_dir: str, output_dir: str) -> dict:
    """Migrate cedict_ts.u8 (CC-CEDICT) → _bulk_cedict.md (ZH → EN reference)"""
    filepath = os.path.join(source_dir, "cedict_ts.u8")
    if not os.path.exists(filepath):
        return {"file": "cedict_ts.u8", "status": "NOT_FOUND"}
    
    lines = read_qt_file(filepath)
    
    entries = []
    extra_rows = []
    skipped = 0
    for line in lines:
        if line.startswith('#'):
            skipped += 1
            continue
        # CEDICT format: Traditional Simplified [pinyin] /def1/def2/
        parts = line.split(' ', 2)
        if len(parts) < 3:
            skipped += 1
            continue
        traditional = parts[0]
        simplified = parts[1]
        rest = parts[2]
        
        # Extract pinyin
        pinyin_start = rest.find('[')
        pinyin_end = rest.find(']')
        pinyin = rest[pinyin_start+1:pinyin_end] if pinyin_start >= 0 and pinyin_end > pinyin_start else ""
        
        # Extract definitions
        defs_part = rest[pinyin_end+1:].strip() if pinyin_end >= 0 else rest
        defs = [d.strip() for d in defs_part.strip('/').split('/') if d.strip()]
        definition = "; ".join(defs)
        
        # Use simplified as key
        entries.append((simplified, definition))
        extra_rows.append([pinyin])
    
    out_path = os.path.join(output_dir, "global", "en_vi", "_bulk_cedict.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="en",
        priority=1,
        category="cedict_reference",
        compiled_from="cedict_ts.u8",
        entries=entries,
        extra_columns=["pinyin"],
        extra_data=extra_rows,
        notes="CC-CEDICT Chinese→English reference dictionary. Not used directly for ZH→VI translation, but useful for EN meaning lookup.",
    )
    
    return {"file": "cedict_ts.u8", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_babylon(source_dir: str, output_dir: str) -> dict:
    """Migrate Babylon.txt → _bulk_babylon.md (ZH → EN reference)."""
    filepath = os.path.join(source_dir, "Babylon.txt")
    if not os.path.exists(filepath):
        return {"file": "Babylon.txt", "status": "NOT_FOUND"}

    lines = read_qt_file(filepath)

    entries = []
    skipped = 0
    for line in lines:
        parsed = parse_kv_line(line)
        if parsed:
            entries.append(parsed)
        else:
            skipped += 1

    out_path = os.path.join(output_dir, "global", "en_vi", "_bulk_babylon.md")
    count = write_bulk_md(
        out_path,
        source_lang="zh",
        target_lang="en",
        priority=1,
        category="babylon_reference",
        compiled_from="Babylon.txt",
        entries=entries,
        notes="Babylon Chinese→English reference dictionary. Reference only; not part of ZH→VI fast-path runtime.",
    )

    return {"file": "Babylon.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def _parse_mark_line(line: str) -> tuple[str, str] | None:
    """Parse Mark.txt lines without losing space-replacement rules."""
    idx = line.find('=')
    if idx == -1:
        return None

    key = line[:idx].strip()
    raw_value = line[idx + 1:].rstrip('\r\n')
    if not key:
        return None

    if key == '　':
        value = ' '
    else:
        value = raw_value.strip()

    return key, value


def _parse_history_file(filepath: str) -> list[tuple[str, str, str, str]]:
    """Parse QT history TSV files into audit event rows."""
    rows: list[tuple[str, str, str, str]] = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\r\n') for line in f if line.strip()]

    if not lines:
        return rows

    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) < 4:
            continue
        entry, action, user_name, updated_at = parts[:4]
        rows.append((entry.strip(), action.strip(), user_name.strip(), updated_at.strip()))

    return rows


def migrate_mark_rules(source_dir: str, output_dir: str) -> dict:
    """Migrate Mark.txt → mark_normalization.md."""
    filepath = os.path.join(source_dir, "Mark.txt")
    if not os.path.exists(filepath):
        return {"file": "Mark.txt", "status": "NOT_FOUND"}

    lines = read_qt_file(filepath)

    rules = []
    skipped = 0
    for line in lines:
        parsed = _parse_mark_line(line)
        if parsed:
            rules.append(parsed)
        else:
            skipped += 1

    out_path = os.path.join(output_dir, "global", "normalization", "mark_normalization.md")
    count = write_normalization_md(
        out_path,
        compiled_from="Mark.txt",
        rules=rules,
        rule_type="punctuation_map",
        notes="Punctuation and symbol normalization rules extracted from Quick Translator Mark.txt.",
    )

    return {"file": "Mark.txt", "source_count": len(lines), "migrated": count, "skipped": skipped}


def migrate_history_files(source_dir: str, output_dir: str) -> dict:
    """Migrate QT history TSV files into audit event Markdown files."""
    history_specs = [
        ("VietPhraseHistory.txt", "vietphrase"),
        ("NamesHistory.txt", "names"),
        ("Names2History.txt", "names2"),
        ("ChinesePhienAmWordsHistory.txt", "phien_am"),
    ]

    results = []
    total_events = 0

    for filename, source_dict in history_specs:
        filepath = os.path.join(source_dir, filename)
        if not os.path.exists(filepath):
            results.append({"file": filename, "status": "NOT_FOUND"})
            continue

        events = _parse_history_file(filepath)
        out_path = os.path.join(output_dir, "global", "audit", f"{source_dict}_history.md")
        migrated = write_audit_md(
            out_path,
            compiled_from=filename,
            source_dict=source_dict,
            events=events,
            notes=f"Audit history imported from {filename}.",
        )
        total_events += migrated
        results.append({
            "file": filename,
            "source_count": len(events),
            "migrated": migrated,
        })

    return {
        "files": results,
        "migrated": total_events,
        "source_count": total_events,
    }


# ─────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────

def run_migration(source_dir: str, output_dir: str, validate: bool = False, only: list[str] | None = None) -> dict:
    """Run full migration from QT TXT → MD format."""
    print(f"\n{'='*60}")
    print("  DrDuc Translator - QT to MD Migration")
    print(f"  Source: {source_dir}")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}\n")
    
    results = {}
    migrations = [
        ("VietPhrase",      migrate_vietphrase),
        ("VietPhrase2",     migrate_vietphrase2),
        ("Names",           migrate_names),
        ("PhienAm",         migrate_phienam),
        ("ThieuChuu",       migrate_thieuchuu),
        ("LuatNhan",        migrate_luat_nhan),
        ("LuatNhanCu",      migrate_luat_nhan_cu),
        ("TrichDan",        migrate_trichdan),
        ("Pronouns",        migrate_pronouns),
        ("IgnoredPhrases",  migrate_ignored_phrases),
        ("CEDICT",          migrate_cedict),
        ("Babylon",         migrate_babylon),
        ("LacViet",         migrate_lacviet),
        ("Mark",            migrate_mark_rules),
        ("History",         migrate_history_files),
    ]

    selected = None
    if only:
        selected = {name.lower() for name in only}
        migrations = [(name, func) for name, func in migrations if name.lower() in selected]
        if not migrations:
            raise ValueError(f"No matching migrations for --only: {only}")
    
    total_migrated = 0
    total_source = 0
    
    for name, func in migrations:
        print(f"[MIGRATE] {name}...", end=" ", flush=True)
        try:
            result = func(source_dir, output_dir)
            results[name] = result
            migrated = result.get("migrated", result.get("total_unique", 0))
            source = result.get("source_count", 0)
            total_migrated += migrated
            total_source += source
            print(f"OK {migrated:,} entries")
        except Exception as e:
            results[name] = {"error": str(e)}
            print(f"ERROR: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  MIGRATION COMPLETE")
    print(f"  Total source lines: {total_source:,}")
    print(f"  Total migrated entries: {total_migrated:,}")
    print(f"{'='*60}\n")
    
    # Write migration report
    report_name = "_migration_report.json" if not only else "_migration_report.partial.json"
    report_path = os.path.join(output_dir, report_name)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.datetime.now().isoformat(),
            "source_dir": source_dir,
            "output_dir": output_dir,
            "selected_only": only or [],
            "total_source_lines": total_source,
            "total_migrated_entries": total_migrated,
            "details": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"Report saved: {report_path}")
    
    if validate:
        print("\nRunning validation...")
        validate_migration(source_dir, output_dir, results)
    
    return results


def validate_migration(source_dir: str, output_dir: str, results: dict):
    """Validate that no entries were lost during migration."""
    errors = []
    
    # Check VietPhrase
    vp = results.get("VietPhrase", {})
    if vp and vp.get("source_count", 0) != vp.get("migrated", 0) + vp.get("skipped", 0):
        errors.append(f"VietPhrase: source={vp['source_count']} != migrated({vp['migrated']}) + skipped({vp['skipped']})")
    
    # Check other files similarly
    for name in ["PhienAm", "LuatNhan", "LuatNhanCu", "TrichDan", "Pronouns"]:
        data = results.get(name, {})
        if data and "source_count" in data:
            expected = data.get("migrated", 0) + data.get("skipped", 0)
            if data["source_count"] != expected:
                errors.append(f"{name}: source={data['source_count']} != migrated({data.get('migrated',0)}) + skipped({data.get('skipped',0)})")
    
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("VALIDATION PASSED: All entries accounted for.")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Quick Translator TXT files to Markdown Dictionary Format"
    )
    parser.add_argument(
        "--source", default=DEFAULT_QT_DATA,
        help=f"Path to QT Data directory (default: {DEFAULT_QT_DATA})"
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Run validation after migration"
    )
    parser.add_argument(
        "--only", nargs="+", default=None,
        help="Run only selected migrations, e.g. --only Babylon Mark"
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.source):
        print(f"Source directory not found: {args.source}")
        sys.exit(1)
    
    run_migration(args.source, args.output, args.validate, args.only)


if __name__ == "__main__":
    main()
