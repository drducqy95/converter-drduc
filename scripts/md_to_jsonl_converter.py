#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert name_project markdown glossaries into term-bank JSONL records."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.pipeline.universe import slugify_universe_id


SECTION_TYPE_HINTS = [
    (("nhan vat", "character", "person"), "person"),
    (("dia danh", "ban do", "location", "place"), "location"),
    (("to chuc", "the luc", "faction", "organization", "group"), "organization"),
    (("gia toc", "clan", "squad", "team"), "organization"),
    (("canh gioi", "cap bac", "tu luyen", "realm"), "realm"),
    (("cong phap", "ky nang", "phap thuat", "thuat", "jutsu", "skill"), "technique"),
    (("vu khi", "weapon"), "weapon"),
    (("vat pham", "bao vat", "artifact", "item", "bao boi"), "item"),
    (("chuc vu", "title"), "title"),
    (("sinh vat", "creature"), "creature"),
]

SKIP_LINE_HINTS = ("tac gia", "nguon", "source:")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CJK_TERM_RE = re.compile(r"[\u4e00-\u9fff][\u4e00-\u9fff·・\-\s]*[\u4e00-\u9fff]|[\u4e00-\u9fff]")
ENTITY_TYPE_PRIORITY = {
    "person": 10,
    "location": 9,
    "organization": 8,
    "realm": 7,
    "technique": 6,
    "weapon": 6,
    "item": 6,
    "creature": 5,
    "title": 4,
    "term": 1,
}

FILE_UNIVERSE_HINTS = {
    # === ChinaWebNovel (12 files) ===
    "Dau_Pha_Thuong_Khung": ("dau_pha_thuong_khung", "Đấu Phá Thương Khung", "Đấu Khí"),
    "Vu_Dong_Can_Khon": ("vu_dong_can_khon", "Vũ Động Càn Khôn", "Đấu Khí"),
    "Dau_La_Dai_Luc": ("dau_la_dai_luc", "Đấu La Đại Lục", "Đấu La"),
    "Phan_Nhan_Tu_Tien": ("pham_nhan_tu_tien", "Phàm Nhân Tu Tiên", "Tu Tiên"),
    "Tien_Nghich": ("tien_nghich", "Tiên Nghịch", "Tu Tiên"),
    "Tru_Tien": ("tru_tien", "Tru Tiên", "Tu Tiên"),
    "Gia_Thien": ("gia_thien", "Già Thiên", "Thần Đông"),
    "Hoan_My_The_Gioi": ("hoan_my_the_gioi", "Hoàn Mỹ Thế Giới", "Thần Đông"),
    "Kiem_Lai": ("kiem_lai", "Kiếm Lai", "Kiếm Lai"),
    "Tuyet_Trung_Han_Dao_Hanh": ("tuyet_trung_han_dao_hanh", "Tuyết Trung Hãn Đao Hành", "Tuyết Trung"),
    "Quy_Bi_Chi_Chu": ("quy_bi_chi_chu", "Quỷ Bí Chi Chủ", "Quỷ Bí"),
    "Than_An_Vuong_Toa": ("than_an_vuong_toa", "Thần Ấn Vương Tọa", "Thần Ấn"),
    # === World (1 file) ===
    "Name_Doithuc": ("real_world", "Real World", "Real World"),
    # === Comic (1 file) ===
    "Name_Marvel": ("marvel", "Marvel", "Marvel"),
    # === FilmHollywood (3 files) ===
    "Name_HarryPotter": ("harry_potter", "Harry Potter", "Harry Potter"),
    "Name_Hollywood": ("hollywood", "Hollywood", "Hollywood"),
    "Name_TheOneRing": ("the_one_ring", "The Lord of the Rings", "Middle-earth"),
    # === Manga (6 files) ===
    "Name_Bleach": ("bleach", "Bleach", "Bleach"),
    "Name_Doremon": ("doremon", "Doraemon", "Doraemon"),
    "Name_Manga": ("manga_shared", "Manga Shared", "Manga"),
    "Name_Naruto": ("naruto", "Naruto", "Naruto"),
    "Name_OnePiece": ("one_piece", "One Piece", "One Piece"),
    "Name_OnePuchman": ("one_punch_man", "One Punch Man", "One Punch Man"),
}


@dataclass(slots=True)
class MigratedTerm:
    source: str
    target: str
    entity_type: str = "term"
    scope: str = "universe"
    status: str = "approved"
    confidence: float = 0.86
    source_dict: str = "md_to_jsonl_converter"
    universe: str = ""
    work: str = ""
    franchise: str = ""
    notes: str = ""
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    context_markers: list[str] = field(default_factory=list)
    co_occurring_entities: list[str] = field(default_factory=list)
    version: int = 1


def parse_markdown_file(path: str | Path) -> list[MigratedTerm]:
    path = Path(path)
    universe, work, franchise = infer_file_metadata(path)
    current_type = "term"
    records: dict[tuple[str, str], MigratedTerm] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            current_type = infer_entity_type(line) or current_type
            continue
        subsection_type = infer_entity_type(line)
        if subsection_type and "=" not in line and "," not in line:
            current_type = subsection_type
            continue
        if should_skip_line(line):
            continue
        parsed = parse_term_line(line)
        if not parsed:
            continue
        sources, target, notes = parsed
        primary = sources[0]
        record = MigratedTerm(
            source=primary,
            target=target,
            entity_type=current_type,
            scope="global" if universe in {"real_world"} else "universe",
            source_dict=f"md_to_jsonl:{path.name}",
            universe=universe,
            work=work,
            franchise=franchise,
            notes=notes,
            aliases=sources[1:],
            tags=[universe, current_type],
            context_markers=[primary, *sources[1:]][:8],
        )
        key = (primary, universe)
        existing = records.get(key)
        if existing is not None:
            record.entity_type = preferred_entity_type(existing.entity_type, record.entity_type)
            record.aliases = merge_unique([*existing.aliases, *record.aliases])
            record.context_markers = merge_unique([*existing.context_markers, *record.context_markers])
            record.tags = merge_unique([universe, record.entity_type, *existing.tags, *record.tags])
        records[key] = record
    return list(records.values())


def parse_term_line(line: str) -> tuple[list[str], str, str] | None:
    line = normalize_markdown_line(line)
    if "=" in line:
        return _parse_equals_line(line)
    if "," in line and looks_like_structured_csv(line):
        return _parse_csv_line(line)
    return None


def _parse_equals_line(line: str) -> tuple[list[str], str, str] | None:
    parts = [part.strip() for part in line.split("=")]
    if len(parts) < 2:
        return None
    source_part = clean_source_part(parts[0])
    comma_sources = [clean_source_part(item) for item in re.split(r"[,，]", source_part) if has_cjk(item)]
    if len(comma_sources) > 1:
        source_part = comma_sources[-1]
    if not has_cjk(source_part):
        return None
    target = parts[-1] or parts[1]
    notes = ""
    note_match = re.search(r"\(([^()]*)\)\s*$", target)
    if note_match:
        notes = note_match.group(1).strip()
        target = target[:note_match.start()].strip()
    sources = extract_source_terms(source_part)
    if not sources or not target:
        return None
    return sources, target, notes


def _parse_csv_line(line: str) -> tuple[list[str], str, str] | None:
    """Parse comma-separated table rows like: Category,漢字,Hán Việt,Romaji."""
    fields = [clean_source_part(f.strip()) for f in line.split(",")]
    # Find the first field containing CJK characters; that is the source.
    cjk_idx = -1
    for i, f in enumerate(fields):
        if f and has_cjk(f):
            cjk_idx = i
            break
    if cjk_idx < 0 or cjk_idx + 1 >= len(fields):
        return None
    source_part = fields[cjk_idx]
    # Prefer the last non-empty field as the canonical target; many source CSV
    # rows are shaped as "category, Han, Han-Viet, original".
    tail_fields = [field.strip() for field in fields[cjk_idx + 1 :] if field.strip()]
    target = tail_fields[-1] if tail_fields else ""
    if not target:
        return None
    # Keep the intermediate Han-Viet form as notes when there is one.
    notes = ""
    if len(tail_fields) > 1:
        notes = " / ".join(tail_fields[:-1])
    sources = extract_source_terms(source_part)
    if not sources or not target:
        return None
    return sources, target, notes


def normalize_markdown_line(line: str) -> str:
    line = re.sub(r"^[*\-\u2022]\s*", "", line).strip()
    line = re.sub(r"^\d+[.)]\s*", "", line).strip()
    return line.strip()


def should_skip_line(line: str) -> bool:
    normalized = strip_accents(normalize_markdown_line(line)).casefold()
    return any(hint in normalized for hint in SKIP_LINE_HINTS)


def has_cjk(value: str) -> bool:
    return bool(CJK_RE.search(value))


def clean_source_part(value: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(r"\*\*([^*]+):\*\*\s*", "", cleaned)
    cleaned = re.sub(r"^\*\*([^*]+)\*\*:\s*", "", cleaned)
    if ":" in cleaned and has_cjk(cleaned.split(":", 1)[1]):
        cleaned = cleaned.split(":", 1)[1].strip()
    if "：" in cleaned and has_cjk(cleaned.split("：", 1)[1]):
        cleaned = cleaned.split("：", 1)[1].strip()
    return cleaned.strip(" -*\t")


def extract_source_terms(source_part: str) -> list[str]:
    """Extract stable CJK source terms and aliases from the left side of a row."""

    cleaned = clean_source_part(source_part)
    if not has_cjk(cleaned):
        return []

    candidates: list[str] = []
    for item in re.split(r"\s*/\s*|[()（）\[\]【】]", cleaned):
        item = clean_source_part(item)
        if has_cjk(item):
            candidates.append(item)

    for match in CJK_TERM_RE.finditer(cleaned):
        term = re.sub(r"\s+", "", match.group(0)).strip(" -/")
        if has_cjk(term):
            candidates.append(term)
        for piece in re.split(r"\s*-\s*|/", term):
            piece = piece.strip()
            if has_cjk(piece):
                candidates.append(piece)

    normalized: list[str] = []
    for candidate in candidates:
        candidate = candidate.strip(" -*,，;；:：")
        candidate = re.sub(r"\s+", "", candidate)
        if not has_cjk(candidate):
            continue
        if len(candidate) == 1:
            continue
        if candidate not in normalized:
            normalized.append(candidate)
    return normalized


def looks_like_structured_csv(line: str) -> bool:
    """Avoid parsing prose lists as CSV rows unless a field looks like a term cell."""

    fields = [clean_source_part(f) for f in line.split(",")]
    cjk_fields = [field for field in fields if has_cjk(field)]
    if len(cjk_fields) != 1:
        return False
    cjk_index = fields.index(cjk_fields[0])
    return cjk_index + 1 < len(fields) and bool(fields[cjk_index + 1].strip())


def preferred_entity_type(left: str, right: str) -> str:
    return left if ENTITY_TYPE_PRIORITY.get(left, 0) >= ENTITY_TYPE_PRIORITY.get(right, 0) else right


def merge_unique(values: list[str]) -> list[str]:
    return [value for value in dict.fromkeys(str(item).strip() for item in values if str(item).strip())]


def infer_file_metadata(path: Path) -> tuple[str, str, str]:
    stem = path.stem
    for marker, metadata in FILE_UNIVERSE_HINTS.items():
        if marker in stem:
            return metadata
    parent = path.parent.name.casefold()
    if "world" in parent:
        return "real_world", "Real World", "Real World"
    if "marvel" in parent:
        return "marvel", "Marvel", "Marvel"
    work = stem.replace("_", " ")
    return slugify_universe_id(work), work, work


def infer_entity_type(header: str) -> str | None:
    normalized = strip_accents(header).casefold()
    for hints, entity_type in SECTION_TYPE_HINTS:
        if any(hint in normalized for hint in hints):
            return entity_type
    return None


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    stripped = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return stripped.replace("đ", "d").replace("Đ", "D")


def write_jsonl(records: list[MigratedTerm], path: str | Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = {(record.source, record.universe): record for record in records}
    path.write_text(
        "\n".join(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True) for record in unique.values()) + "\n",
        encoding="utf-8",
    )
    return len(unique)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert markdown name glossaries to term-bank JSONL")
    parser.add_argument("inputs", nargs="+", help="Markdown files or directories")
    parser.add_argument("--out", required=True, help="Output JSONL file")
    args = parser.parse_args()

    records: list[MigratedTerm] = []
    for raw_input in args.inputs:
        input_path = Path(raw_input)
        paths = sorted(input_path.rglob("*.md")) if input_path.is_dir() else [input_path]
        for path in paths:
            records.extend(parse_markdown_file(path))
    count = write_jsonl(records, args.out)
    print(json.dumps({"records": count, "out": str(Path(args.out))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
