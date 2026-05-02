from pathlib import Path

from scripts.md_to_jsonl_converter import FILE_UNIVERSE_HINTS, parse_markdown_file


def test_md_to_jsonl_converter_parses_bullets_aliases_and_sections(tmp_path):
    source = tmp_path / "Dau_Pha_Thuong_Khung.md"
    source.write_text(
        """# Đấu Phá Thương Khung

### Nhân vật
* 萧炎 / 炎帝 = Tiêu Viêm (nhân vật chính)

### Bản đồ
- 中州 = Trung Châu
""",
        encoding="utf-8",
    )

    records = parse_markdown_file(source)
    by_source = {record.source: record for record in records}

    assert by_source["萧炎"].entity_type == "person"
    assert by_source["萧炎"].aliases == ["炎帝"]
    assert by_source["萧炎"].notes == "nhân vật chính"
    assert by_source["萧炎"].universe == "dau_pha_thuong_khung"
    assert by_source["中州"].entity_type == "location"


def test_parse_all_23_source_files():
    all_records = []
    for md_file in Path("name_project").rglob("*.md"):
        all_records.extend(parse_markdown_file(md_file))

    assert len(all_records) >= 800


def test_real_world_count():
    records = parse_markdown_file("name_project/World/Name_Doithuc.md")

    assert len(records) >= 80


def test_bleach_is_largest():
    records = parse_markdown_file("name_project/Manga/Name_Bleach.md")

    assert len(records) >= 100


def test_no_duplicate_primary_keys():
    for md_file in Path("name_project").rglob("*.md"):
        records = parse_markdown_file(md_file)
        keys = [(record.source, record.universe) for record in records]
        assert len(keys) == len(set(keys)), f"Duplicates in {md_file.name}"


def test_file_universe_hints_complete():
    assert len(FILE_UNIVERSE_HINTS) >= 23


def test_than_an_vuong_toa_separate_universe():
    records = parse_markdown_file("name_project/ChinaWebNovel/Than_An_Vuong_Toa.md")

    assert records
    assert all(record.universe == "than_an_vuong_toa" for record in records)
