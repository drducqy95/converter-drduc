#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for post-run learning and project-level auto-tuning."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.rbmt_translator import SegmentTranslation, TranslationResult
from src.engine.style_profiles import default_style_preferences
from src.learning.project_learning_engine import ProjectLearningEngine
from src.state.project_manager import ProjectManager
from src.ui.command_protocol import CommandRequest
from src.ui.sidecar_bridge import handle_request


def test_project_learning_engine_auto_upgrades_style_for_length_only_issues(tmp_path):
    manager = ProjectManager(tmp_path)
    project = manager.create_project("learning-style")
    project_dir = Path(project.project_dir)
    config = _build_config(style_profile="balanced_novel")
    _write_project_config(project_dir, config)

    result = _build_result(
        source_text="你好",
        clean_text="Xin chào các bạn thân mến ở đây",
        config=config,
    )
    report = {
        "summary": {"issues": 1, "segments": 1},
        "issues": [
            {
                "severity": "low",
                "checker": "length",
                "segment_id": "seg-0001",
                "message": "Suspicious source/target ratio: 8.00",
            }
        ],
    }

    learning = ProjectLearningEngine().record_run(
        project_dir=project_dir,
        manager=manager,
        project_id="learning-style",
        chapter_id="chapter-001",
        translation_result=result,
        qa_report=report,
        config=config,
        runtime_metrics={"translate_seconds": 5.5},
    )

    updated = json.loads((project_dir / "working" / "config" / "translation_config.json").read_text(encoding="utf-8"))
    assert updated["style_preferences"]["chapter_overrides"]["chapter-001"]["style_profile"] == "modern_novel_adaptive"
    assert any(item["setting"] == "style_profile" for item in learning["auto_applied"])
    assert (project_dir / "reports" / "learning_report_chapter-001.json").exists()


def test_project_learning_engine_enables_compact_sentences_for_persistent_length_issues(tmp_path):
    manager = ProjectManager(tmp_path)
    project = manager.create_project("learning-compact")
    project_dir = Path(project.project_dir)
    config = _build_config(style_profile="modern_novel_adaptive")
    _write_project_config(project_dir, config)

    result = _build_result(
        source_text="你好",
        clean_text="Xin chào các bạn thân mến ở đây",
        config=config,
    )
    report = {
        "summary": {"issues": 1, "segments": 1},
        "issues": [
            {
                "severity": "low",
                "checker": "length",
                "segment_id": "seg-0001",
                "message": "Suspicious source/target ratio: 8.00",
            }
        ],
    }

    learning = ProjectLearningEngine().record_run(
        project_dir=project_dir,
        manager=manager,
        project_id="learning-compact",
        chapter_id="chapter-001",
        translation_result=result,
        qa_report=report,
        config=config,
        runtime_metrics={"translate_seconds": 5.5},
    )

    updated = json.loads((project_dir / "working" / "config" / "translation_config.json").read_text(encoding="utf-8"))
    chapter_override = updated["style_preferences"]["chapter_overrides"]["chapter-001"]
    assert chapter_override["naturalization"]["compact_sentences"] is True
    assert any(item["setting"] == "naturalization.compact_sentences" for item in learning["auto_applied"])


def test_project_learning_engine_tracks_history_and_reference_similarity(tmp_path):
    manager = ProjectManager(tmp_path)
    project = manager.create_project("learning-history")
    project_dir = Path(project.project_dir)
    external_root = tmp_path / "external-project"
    (external_root / "output").mkdir(parents=True)
    (external_root / "output" / "chapter_002.txt").write_text("Xin chào", encoding="utf-8")
    config = _build_config(
        style_profile="balanced_novel",
        external_root=external_root,
        source_basename="chapter_002.txt",
    )
    _write_project_config(project_dir, config)
    engine = ProjectLearningEngine()

    first_result = _build_result(
        source_text="你好",
        clean_text="Xin chào các bạn",
        config=config,
    )
    first_report = {
        "summary": {"issues": 2, "segments": 1},
        "issues": [
            {"severity": "low", "checker": "length", "segment_id": "seg-0001", "message": "ratio"},
            {"severity": "low", "checker": "length", "segment_id": "seg-0001", "message": "ratio"},
        ],
    }
    engine.record_run(
        project_dir=project_dir,
        manager=manager,
        project_id="learning-history",
        chapter_id="chapter-001",
        translation_result=first_result,
        qa_report=first_report,
        config=config,
        runtime_metrics={"translate_seconds": 6.0},
    )

    second_result = _build_result(
        source_text="你好",
        clean_text="Xin chào",
        config=config,
    )
    second_report = {
        "summary": {"issues": 0, "segments": 1},
        "issues": [],
    }
    second_learning = engine.record_run(
        project_dir=project_dir,
        manager=manager,
        project_id="learning-history",
        chapter_id="chapter-001",
        translation_result=second_result,
        qa_report=second_report,
        config=config,
        runtime_metrics={"translate_seconds": 3.0},
    )

    history = json.loads((project_dir / "state" / "learning_history.json").read_text(encoding="utf-8"))
    assert len(history["chapters"]["chapter-001"]) == 2
    assert second_learning["delta"]["qa_total"] == -2
    assert second_learning["delta"]["runtime_metrics"]["translate_seconds"] == -3.0
    assert second_learning["current_run"]["reference_comparison"]["path"].endswith("chapter_002.txt")
    assert second_learning["current_run"]["reference_comparison"]["word_similarity"] == 1.0


def test_sidecar_review_candidate_syncs_learned_terms_for_future_translations(tmp_path):
    manager = ProjectManager(tmp_path)
    project = manager.create_project("learned-term-demo")
    project_dir = Path(project.project_dir)
    candidate_id = manager.add_candidate_entry(
        "learned-term-demo",
        "道友",
        "bạn tu tiên",
        chapter_id="chapter-001",
        segment_id="chapter-001:seg-0001",
        fallback_level="ambiguous",
        reason="reviewed_xianxia_term",
    )

    review_response = handle_request(CommandRequest(
        command="review_candidate_entry",
        payload={
            "project_dir": str(project_dir),
            "candidate_id": candidate_id,
            "status": "verified",
            "reason": "approved",
        },
    ))
    assert review_response.ok
    assert review_response.data["learning_sync"]["verified_candidates"] == 1

    learned_terms = json.loads((project_dir / "working" / "config" / "learned_terms.json").read_text(encoding="utf-8"))
    assert learned_terms["phrase_overrides"][0]["source"] == "道友"
    assert learned_terms["phrase_overrides"][0]["target"] == "bạn tu tiên"

    translate_response = handle_request(CommandRequest(
        command="translate",
        payload={
            "project_dir": str(project_dir),
            "text": "道友",
            "config": {
                "genre_hints": ["xianxia"],
            },
        },
    ))
    assert translate_response.ok
    assert translate_response.data["clean_text"] == "Bạn tu tiên"


def _build_config(*, style_profile: str, external_root: Path | None = None, source_basename: str | None = None) -> dict:
    preferences = default_style_preferences(["modern"], None)
    preferences["project_profile"] = style_profile
    config = {
        "genre_hints": ["modern"],
        "style_profile": style_profile,
        "style_context": preferences["project_context"],
        "style_preferences": preferences,
        "naturalization": {"enabled": style_profile != "source_faithful"},
        "style_resolution": {
            "effective_profile": style_profile,
            "resolved_from": "project_profile",
            "effective_context": preferences["project_context"],
            "naturalization": {"enabled": style_profile != "source_faithful"},
        },
    }
    if external_root is not None:
        config["external_project_metadata"] = {
            "root_dir": str(external_root),
        }
        if source_basename is not None:
            config["external_project_metadata"]["source_basename"] = source_basename
    return config


def _build_result(*, source_text: str, clean_text: str, config: dict) -> TranslationResult:
    segment = SegmentTranslation(
        sentence_id="seg-0001",
        source_text=source_text,
        clean_text=clean_text,
        draft_text=clean_text,
        emotion=None,
        trace=[{"fallback_level": "runtime"}],
    )
    return TranslationResult(
        clean_text=clean_text,
        draft_text=clean_text,
        segments=[segment],
        config=config,
    )


def _write_project_config(project_dir: Path, config: dict):
    config_path = project_dir / "working" / "config" / "translation_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
