#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for EN-VI baseline and desktop sidecar protocol."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.md_dictionary_compiler import DictionaryCompiler
from src.en_vi.en_vi_translator import EnglishVietnameseTranslator
from src.ui.command_protocol import CommandRequest
from src.ui.sidecar_bridge import handle_request


def test_en_vi_translator_phrase_first_and_rules():
    translator = EnglishVietnameseTranslator()
    assert translator.translate("the young girl").text == "cô gái trẻ"
    assert translator.translate("new world").text == "thế giới mới"
    assert translator.translate("will walk").text == "sẽ đi bộ"


def test_sidecar_bridge_project_workflow_and_candidate_review(tmp_path):
    create_response = handle_request(CommandRequest(
        command="create_project",
        payload={
            "base_dir": str(tmp_path),
            "project_id": "desktop-demo",
        },
    ))
    assert create_response.ok

    project_dir = Path(create_response.data["project_dir"])
    source_path = tmp_path / "source.md"
    source_path.write_text(
        "第1章 Khoi dau\n林动说道：“浪漫！”\n\n第2章 Gap go\n秦云问道：“明天？”",
        encoding="utf-8",
    )

    import_response = handle_request(CommandRequest(
        command="import_file",
        payload={
            "project_dir": str(project_dir),
            "filepath": str(source_path),
        },
    ))
    assert import_response.ok
    assert import_response.data["overview"]["counts"]["chapters"] >= 2

    translate_response = handle_request(CommandRequest(
        command="translate",
        payload={
            "project_dir": str(project_dir),
            "config": {
                "genre_hints": ["general"],
                "locked_entities": [{"source": "林动", "target": "Lam Dong", "entity_type": "person"}],
                "high_ambiguity_terms": ["浪漫"],
            },
        },
    ))
    assert translate_response.ok
    assert "Lam Dong" in translate_response.data["clean_text"]
    assert (project_dir / "output" / "translated.txt").exists()

    overview_response = handle_request(CommandRequest(
        command="get_project_overview",
        payload={"project_dir": str(project_dir)},
    ))
    assert overview_response.ok
    assert overview_response.data["counts"]["segments"] >= 1

    artifacts_response = handle_request(CommandRequest(
        command="load_translation_artifacts",
        payload={"project_dir": str(project_dir)},
    ))
    assert artifacts_response.ok
    assert artifacts_response.data["segments"]

    candidates_response = handle_request(CommandRequest(
        command="list_candidate_entries",
        payload={"project_dir": str(project_dir)},
    ))
    assert candidates_response.ok
    assert any(entry["fallback_level"] == "ambiguous" for entry in candidates_response.data["entries"])

    candidate_id = candidates_response.data["entries"][0]["id"]
    review_response = handle_request(CommandRequest(
        command="review_candidate_entry",
        payload={
            "project_dir": str(project_dir),
            "candidate_id": candidate_id,
            "status": "verified",
            "reason": "approved from desktop review",
        },
    ))
    assert review_response.ok
    assert review_response.data["entry"]["status"] == "verified"

    chapter_response = handle_request(CommandRequest(
        command="set_active_chapter",
        payload={
            "project_dir": str(project_dir),
            "chapter_id": "chapter-002",
        },
    ))
    assert chapter_response.ok
    assert chapter_response.data["project"]["active_chapter"] == "chapter-002"

    second_translate = handle_request(CommandRequest(
        command="translate",
        payload={
            "project_dir": str(project_dir),
            "config": {
                "genre_hints": ["general"],
                "locked_entities": [{"source": "秦云", "target": "Tan Van", "entity_type": "person"}],
            },
        },
    ))
    assert second_translate.ok
    assert second_translate.data["chapter_id"] == "chapter-002"
    assert (project_dir / "output" / "chapter-002.txt").exists()

    qa_response = handle_request(CommandRequest(
        command="run_qa",
        payload={"project_dir": str(project_dir)},
    ))
    assert qa_response.ok
    assert qa_response.data["report"]["summary"]["segments"] >= 1

    qa_load_response = handle_request(CommandRequest(
        command="load_qa_report",
        payload={"project_dir": str(project_dir)},
    ))
    assert qa_load_response.ok
    assert qa_load_response.data["report"]["summary"]["segments"] >= 1


def test_sidecar_bridge_dictionary_search_returns_metadata():
    response = handle_request(CommandRequest(
        command="search_dictionary_entries",
        payload={
            "query": "一",
            "limit": 5,
        },
    ))
    assert response.ok
    assert response.data["entries"]
    first = response.data["entries"][0]
    assert first["source"]
    assert "target_vi" in first
    assert "source_dict" in first
    assert "priority" in first
    assert "full_explanation" in first


def test_sidecar_bridge_applies_project_and_chapter_style_profiles(tmp_path):
    create_response = handle_request(CommandRequest(
        command="create_project",
        payload={
            "base_dir": str(tmp_path),
            "project_id": "style-demo",
        },
    ))
    assert create_response.ok

    project_dir = Path(create_response.data["project_dir"])
    source_path = tmp_path / "style_source.md"
    source_path.write_text(
        "# 第1章 A\n“既然已经签订了工作合同，那现在就去履行你的职责吧。”\n\n"
        "# 第2章 B\n“既然已经签订了工作合同，那现在就去履行你的职责吧。”",
        encoding="utf-8",
    )

    import_response = handle_request(CommandRequest(
        command="import_file",
        payload={
            "project_dir": str(project_dir),
            "filepath": str(source_path),
        },
    ))
    assert import_response.ok

    project_style = handle_request(CommandRequest(
        command="set_translation_style",
        payload={
            "project_dir": str(project_dir),
            "style_profile": "source_faithful",
        },
    ))
    assert project_style.ok
    assert project_style.data["effective_style"]["effective_profile"] == "source_faithful"

    chapter_style = handle_request(CommandRequest(
        command="set_translation_style",
        payload={
            "project_dir": str(project_dir),
            "chapter_id": "chapter-002",
            "style_profile": "modern_novel_adaptive",
        },
    ))
    assert chapter_style.ok
    assert chapter_style.data["effective_style"]["effective_profile"] == "modern_novel_adaptive"

    chapter_one = handle_request(CommandRequest(
        command="translate",
        payload={
            "project_dir": str(project_dir),
            "chapter_id": "chapter-001",
        },
    ))
    assert chapter_one.ok
    assert "Như là đã ký kết làm việc hợp đồng" in chapter_one.data["clean_text"]

    chapter_two = handle_request(CommandRequest(
        command="translate",
        payload={
            "project_dir": str(project_dir),
            "chapter_id": "chapter-002",
        },
    ))
    assert chapter_two.ok
    assert "Đã ký hợp đồng lao động rồi" in chapter_two.data["clean_text"]


def test_sidecar_bridge_lists_and_updates_dictionary_entries_with_source_sync(tmp_path):
    dict_root = tmp_path / "dict"
    source_dir = dict_root / "global" / "vietphrase"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "_bulk_test.md"
    source_file.write_text(
        """---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: vietphrase_test
---

| Source | Target | Priority | Category | POS_Tag | Pinyin | Traditional | Metadata |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 林动 | Lam Dong | 2 | vietphrase_test | NOUN | lin2 dong4 | 林動 | {"pos_sub":"name","entity_type":"person","luat_nhan_trigger":1,"reorder_role":"head"} |
""",
        encoding="utf-8",
    )

    compiler = DictionaryCompiler(str(dict_root), str(dict_root / "_compiled"))
    compiler.compile()
    db_path = dict_root / "_compiled" / "trie_cache.db"

    list_response = handle_request(CommandRequest(
        command="list_dictionary_entries",
        payload={
            "db_path": str(db_path),
            "query": "林动",
            "page": 1,
            "page_size": 10,
        },
    ))
    assert list_response.ok
    assert list_response.data["total"] == 1
    entry = list_response.data["entries"][0]
    assert entry["source_path"].endswith("_bulk_test.md")
    assert entry["table_name"] == "entries"

    update_response = handle_request(CommandRequest(
        command="update_dictionary_entry",
        payload={
            "db_path": str(db_path),
            "table_name": entry["table_name"],
            "record_id": entry["row_id"],
            "target_vi": "Lâm Động",
            "pos_tag": "NOUN",
            "pos_sub": "name",
            "entity_type": "person",
            "pinyin": "lin2 dong4",
            "traditional": "林動",
            "luat_nhan_trigger": True,
            "reorder_role": "head",
            "full_explanation": "Nhan vat chinh da duoc chuan hoa.",
        },
    ))
    assert update_response.ok
    assert update_response.data["entry"]["target_vi"] == "Lâm Động"
    assert "Nhan vat chinh" in update_response.data["entry"]["full_explanation"]

    refreshed = handle_request(CommandRequest(
        command="search_dictionary_entries",
        payload={
            "db_path": str(db_path),
            "query": "林动",
            "limit": 5,
        },
    ))
    assert refreshed.ok
    assert refreshed.data["entries"][0]["target_vi"] == "Lâm Động"
    assert "Lâm Động" in source_file.read_text(encoding="utf-8")


def test_sidecar_bridge_reports_pipeline_status_after_project_workflow(tmp_path):
    create_response = handle_request(CommandRequest(
        command="create_project",
        payload={
            "base_dir": str(tmp_path),
            "project_id": "pipeline-demo",
        },
    ))
    assert create_response.ok

    project_dir = Path(create_response.data["project_dir"])
    source_path = tmp_path / "pipeline_source.md"
    source_path.write_text("第1章 A\n林动说道：“浪漫！”", encoding="utf-8")

    assert handle_request(CommandRequest(
        command="import_file",
        payload={
            "project_dir": str(project_dir),
            "filepath": str(source_path),
        },
    )).ok
    assert handle_request(CommandRequest(
        command="translate",
        payload={"project_dir": str(project_dir)},
    )).ok
    assert handle_request(CommandRequest(
        command="run_qa",
        payload={"project_dir": str(project_dir)},
    )).ok

    pipeline_response = handle_request(CommandRequest(
        command="get_pipeline_status",
        payload={"project_dir": str(project_dir)},
    ))
    assert pipeline_response.ok
    stages = {stage["id"]: stage for stage in pipeline_response.data["stages"]}
    assert stages["import"]["status"] == "completed"
    assert stages["translate"]["status"] == "completed"
    assert stages["qa"]["status"] == "completed"
