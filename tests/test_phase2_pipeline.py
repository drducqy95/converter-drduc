#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for Phase 02 pre-translation pipeline artifacts."""

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.pinyin_processor import PinyinProcessor
from src.engine.structure_preserver import StructurePreserver
from src.engine.traditional_to_simplified import TraditionalToSimplifiedConverter
from src.pipeline.document_importer import DocumentImporter
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline


def _create_docx(path: Path, text: str):
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "")
        archive.writestr("word/document.xml", xml)


def test_document_importer_handles_html_and_docx(tmp_path):
    importer = DocumentImporter()

    html_path = tmp_path / "sample.html"
    html_path.write_text("<html><body><p>林动</p><script>bad()</script><p>突破</p></body></html>", encoding="utf-8")
    html_import = importer.import_file(html_path)
    assert "林动" in html_import.normalized_text
    assert "bad()" not in html_import.normalized_text

    docx_path = tmp_path / "sample.docx"
    _create_docx(docx_path, "第1章 林动突破")
    docx_import = importer.import_file(docx_path)
    assert "林动突破" in docx_import.normalized_text


def test_structure_preserver_and_converters():
    preserver = StructurePreserver()
    text = "文本 `code` 和 ```js\nconst x = 1;\n``` 以及 $a+b$"
    preserved = preserver.preserve(text)
    restored = preserver.restore(preserved.text, preserved.placeholders)
    assert restored == text

    converter = TraditionalToSimplifiedConverter()
    assert converter.convert("後來臺灣開門") == "后来台湾开门"

    pinyin = PinyinProcessor(custom_lexicon={"lin dong": "林动"})
    assert pinyin.resolve("lin dong xuất hiện") == "林动 xuất hiện"


def test_pretranslation_pipeline_creates_project_artifacts(tmp_path):
    source_path = tmp_path / "input.md"
    source_path.write_text(
        "# 第1章 开始\n林动後來突破。\n\n# 第2章 继续\n林动在宗门。",
        encoding="utf-8",
    )
    project_dir = tmp_path / "project"

    pipeline = PreTranslationPipeline()
    result = pipeline.prepare(source_path, project_dir)
    pipeline.close()

    assert "后来" in result.normalized_text
    assert len(result.chapters) >= 1
    assert any(entity["source"] == "林动" for entity in result.entities)

    config_path = project_dir / "working" / "config" / "translation_config.json"
    entities_path = project_dir / "working" / "entities" / "entities_suggested.json"
    assert config_path.exists()
    assert entities_path.exists()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert "locked_entities" in config
    assert config["style_profile"] == "han_viet_balanced"
    assert "style_preferences" in config
    assert config["style_preferences"]["project_profile"] == "han_viet_balanced"


def test_config_generator_detects_suspense_horror_for_modern_ghost_story(tmp_path):
    source_path = tmp_path / "ghost_story.md"
    source_path.write_text(
        "# 第8章 被黑暗笼罩着\n公司里突然传来惨叫声，恶鬼在黑暗中追了过来，所有人都很恐惧。",
        encoding="utf-8",
    )
    project_dir = tmp_path / "ghost_project"

    pipeline = PreTranslationPipeline()
    result = pipeline.prepare(source_path, project_dir)
    pipeline.close()

    config = result.config
    assert "modern" in config["genre_hints"]
    assert "horror" in config["genre_hints"]
    assert config["style_profile"] == "suspense_horror"
    assert config["style_preferences"]["project_profile"] == "suspense_horror"


def test_external_glossary_prunes_partial_heuristic_name_prefixes(tmp_path):
    project_root = tmp_path / "external_project"
    source_dir = project_root / "source"
    source_dir.mkdir(parents=True)
    source_path = source_dir / "chapter_014.md"
    source_path.write_text(
        "# 第14章 第二份试岗\n后天早上八点，你要准时去齐河女子学院报道。",
        encoding="utf-8",
    )
    (project_root / "glossary.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "source": "齐河女子学院",
                        "target": "Học viện nữ sinh Tề Hà",
                        "category": "proper_names_cn",
                        "context": "Location: school setting",
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    pipeline = PreTranslationPipeline()
    result = pipeline.prepare(source_path, project_root / "workspace")
    pipeline.close()

    locked = {item["source"]: item for item in result.config["locked_entities"]}
    assert "齐河女子学院" in locked
    assert locked["齐河女子学院"]["entity_type"] == "organization"
    assert "齐河女" not in locked


def test_pretranslation_pipeline_imports_source_directory_as_multiple_chapters(tmp_path):
    source_dir = tmp_path / "external_source"
    source_dir.mkdir(parents=True)
    (source_dir / "chapter_001.md").write_text(
        "# 第1章 开始\n夏天骐说道：“你好。”",
        encoding="utf-8",
    )
    (source_dir / "chapter_002.md").write_text(
        "# 第2章 继续\n红衣鬼已经追了上来。",
        encoding="utf-8",
    )

    pipeline = PreTranslationPipeline()
    result = pipeline.prepare(source_dir, tmp_path / "project")
    pipeline.close()

    assert result.imported.detected_format == "directory"
    assert len(result.chapters) == 2
    assert [chapter.chapter_id for chapter in result.chapters] == ["chapter-001", "chapter-002"]
    assert [chapter.title for chapter in result.chapters] == ["# 第1章 开始", "# 第2章 继续"]

    index_path = tmp_path / "project" / "source" / "chapters" / "chapters_index.json"
    index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert [item["chapter_id"] for item in index_payload] == ["chapter-001", "chapter-002"]
