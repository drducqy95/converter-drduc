from scripts.md_to_jsonl_converter import parse_markdown_file


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
