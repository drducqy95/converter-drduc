#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for EAPEE, RBMT, QA, state management, and TM."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.rbmt_translator import RBMTTranslator, SegmentTranslation, TranslationResult
from src.qa.report_generator import QAReportGenerator
from src.state.project_manager import ProjectManager
from src.state.translation_memory import TranslationMemory


def test_project_manager_and_translation_memory(tmp_path):
    manager = ProjectManager(tmp_path)
    project = manager.create_project("demo-project")
    manager.set_active_chapter("demo-project", "chapter-001")
    manager.add_candidate_entry("demo-project", "道友", "đạo hữu")
    manager.review_candidate_entry("demo-project", 1, "verified", "approved for xianxia")
    manager.record_runtime_stat("demo-project", "fallback_rate", 0.1, "chapter-001")

    state_path = Path(project.project_dir) / "state" / "project_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["active_chapter"] == "chapter-001"

    tm = TranslationMemory(Path(project.project_dir) / "state" / "tm.sqlite")
    tm.store("林动突破", "Lâm Động đột phá", confidence=0.95, source="test")
    assert tm.exact_match("林动突破").target_text == "Lâm Động đột phá"
    assert tm.fuzzy_match("林动 đột phá", threshold=0.2) is not None
    assert TranslationMemory.cjk_similarity("林动突破境界", "林动已经突破境界") >= 0.5
    tm.close()


def test_translation_memory_store_many(tmp_path):
    tm = TranslationMemory(tmp_path / "tm.sqlite")
    try:
        tm.store_many(
            [
                ("甲", "Giáp", 0.91, "test", "verified"),
                ("乙", "Ất", 0.92, "test", "verified"),
            ]
        )
        assert tm.exact_match("甲").target_text == "Giáp"
        assert tm.exact_match("乙").target_text == "Ất"
    finally:
        tm.close()


def test_rbmt_translation_and_qa_report(tmp_path):
    project_dir = tmp_path / "project"
    ProjectManager(tmp_path).create_project("project")
    translator = RBMTTranslator(tm_db_path=project_dir / "state" / "tm.sqlite")
    config = {
        "genre_hints": ["general"],
        "locked_entities": [{"source": "林动", "target": "Lâm Động", "entity_type": "person"}],
        "high_ambiguity_terms": ["境界"],
    }

    config["high_ambiguity_terms"] = ["浪漫"]
    result = translator.translate_text('林动说道：“浪漫！”', config=config)
    translator.export(result, project_dir)
    translator.close()

    assert "Lâm Động" in result.clean_text
    assert "lãng mạn" in result.clean_text
    assert "[[AMBIG:浪漫=>" in result.draft_text

    report = QAReportGenerator().run(
        source_text='林动说道：“浪漫！”',
        translation_result=result,
        config=config,
    )
    QAReportGenerator().write(report, project_dir)
    assert report["summary"]["issues"] >= 1
    assert any(issue["checker"] == "ambiguity" for issue in report["issues"])
    assert (project_dir / "reports" / "qa_report.md").exists()


def test_rbmt_export_writes_segment_checkpoint_and_atomic_outputs(tmp_path):
    result = TranslationResult(
        clean_text="Lâm Động đột phá.",
        draft_text="Lâm Động đột phá.",
        segments=[
            SegmentTranslation(
                sentence_id="seg-0001",
                source_text="林动突破。",
                clean_text="Lâm Động đột phá.",
                draft_text="Lâm Động đột phá.",
                emotion=None,
                trace=[],
                trace_id="trace-1",
            )
        ],
        config={},
    )

    translator = RBMTTranslator()
    try:
        translator.export(result, tmp_path, artifact_stem="chapter-001")
    finally:
        translator.close()

    output_path = tmp_path / "output" / "chapter-001.txt"
    draft_path = tmp_path / "drafts" / "chapter-001_draft.txt"
    checkpoint_path = tmp_path / "drafts" / "chapter-001_checkpoint.jsonl"

    assert output_path.read_text(encoding="utf-8") == "Lâm Động đột phá."
    assert draft_path.read_text(encoding="utf-8") == "Lâm Động đột phá."
    assert not (tmp_path / "output" / "chapter-001.txt.partial").exists()
    checkpoint_rows = [json.loads(line) for line in checkpoint_path.read_text(encoding="utf-8").splitlines()]
    assert checkpoint_rows[0]["sentence_id"] == "seg-0001"
    assert checkpoint_rows[0]["trace_id"] == "trace-1"
