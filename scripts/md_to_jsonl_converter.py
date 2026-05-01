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
    (("canh gioi", "cap bac", "tu luyen", "realm"), "realm"),
    (("cong phap", "ky nang", "phap thuat", "technique"), "technique"),
    (("vu khi", "weapon"), "weapon"),
    (("vat pham", "bao vat", "artifact", "item"), "item"),
    (("chuc vu", "title"), "title"),
    (("sinh vat", "creature"), "creature"),
]

FILE_UNIVERSE_HINTS = {
    "Dau_Pha_Thuong_Khung": ("dau_pha_thuong_khung", "Đấu Phá Thương Khung", "Đấu Khí"),
    "Vu_Dong_Can_Khon": ("vu_dong_can_khon", "Vũ Động Càn Khôn", "Đấu Khí"),
    "Dau_La_Dai_Luc": ("dau_la_dai_luc", "Đấu La Đại Lục", "Đấu La"),
    "Phan_Nhan_Tu_Tien": ("pham_nhan_tu_tien", "Phàm Nhân Tu Tiên", "Tu Tiên"),
    "Tien_Nghich": ("tien_nghich", "Tiên Nghịch", "Tu Tiên"),
    "Tru_Tien": ("tru_tien", "Tru Tiên", "Tu Tiên"),
    "Gia_Thien": ("gia_thien", "Già Thiên", "Thần Đông"),
    "Hoan_My_The_Gioi": ("hoan_my_the_gioi", "Hoàn Mỹ Thế Giới", "Thần Đông"),
    "Kiem_Lai": ("kiem_lai", "Kiếm Lai", "Kiếm Lai"),
    "Tuyet_Trung_Han_Dao_Hanh": ("kiem_lai", "Tuyết Trung Hãn Đao Hành", "Tuyết Trung"),
    "Quy_Bi_Chi_Chu": ("quy_bi_chi_chu", "Quỷ Bí Chi Chủ", "Quỷ Bí"),
    "Name_Doithuc": ("real_world", "Real World", "Real World"),
    "Name_Marvel": ("marvel", "Marvel", "Marvel"),
    "Name_HarryPotter": ("harry_potter", "Harry Potter", "Harry Potter"),
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
        records[(primary, universe)] = record
    return list(records.values())


def parse_term_line(line: str) -> tuple[list[str], str, str] | None:
    line = re.sub(r"^[*\-•]\s*", "", line).strip()
    if "=" not in line:
        return None
    parts = [part.strip() for part in line.split("=")]
    if len(parts) < 2:
        return None
    source_part = parts[0]
    if not any("\u4e00" <= char <= "\u9fff" for char in source_part):
        return None
    target = parts[-1] or parts[1]
    notes = ""
    note_match = re.search(r"\(([^()]*)\)\s*$", target)
    if note_match:
        notes = note_match.group(1).strip()
        target = target[:note_match.start()].strip()
    sources = [
        item.strip()
        for item in re.split(r"\s*/\s*|[()（）]", source_part)
        if item.strip() and any("\u4e00" <= char <= "\u9fff" for char in item)
    ]
    if not sources or not target:
        return None
    return sources, target, notes


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
