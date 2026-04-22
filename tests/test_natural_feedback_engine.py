#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for natural-language feedback analysis and rule application."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.learning.natural_feedback_engine import NaturalFeedbackEngine
from src.ui.command_protocol import CommandRequest
from src.ui.sidecar_bridge import handle_request


def test_natural_feedback_engine_extracts_phrase_and_style_suggestions():
    analysis = NaturalFeedbackEngine().analyze(
        feedback_text='Đổi "夏天骐" -> "Hạ Thiên Kỳ", đồng thời xưng hô cần tự nhiên hơn và câu nên ngắn gọn.',
        scope="chapter",
        chapter_id="chapter-003",
    )

    rule_types = {item["rule_type"] for item in analysis["suggestions"]}
    assert "locked_entity" in rule_types
    assert "style_profile" in rule_types
    assert "naturalization" in rule_types


def test_sidecar_feedback_rule_review_updates_learned_terms_and_style_config(tmp_path):
    create_response = handle_request(CommandRequest(
        command="create_project",
        payload={
            "base_dir": str(tmp_path),
            "project_id": "feedback-demo",
        },
    ))
    assert create_response.ok
    project_dir = Path(create_response.data["project_dir"])

    submit_response = handle_request(CommandRequest(
        command="submit_natural_feedback",
        payload={
            "project_dir": str(project_dir),
            "feedback_text": 'Đổi "24小时" -> "24 giờ" và văn phong hội thoại tự nhiên hơn, câu gọn hơn.',
            "scope": "project",
        },
    ))
    assert submit_response.ok
    rules = submit_response.data["rules"]
    assert rules

    phrase_rule = next(rule for rule in rules if rule["rule_type"] == "phrase_override")
    style_rule = next(rule for rule in rules if rule["rule_type"] == "style_profile")
    naturalization_rule = next(rule for rule in rules if rule["rule_type"] == "naturalization")

    phrase_review = handle_request(CommandRequest(
        command="review_candidate_rule",
        payload={
            "project_dir": str(project_dir),
            "rule_id": phrase_rule["id"],
            "status": "verified",
            "reason": "approved",
        },
    ))
    assert phrase_review.ok
    learned_terms = json.loads((project_dir / "working" / "config" / "learned_terms.json").read_text(encoding="utf-8"))
    assert any(item["source"] == "24小时" and item["target"] == "24 giờ" for item in learned_terms["phrase_overrides"])

    style_review = handle_request(CommandRequest(
        command="review_candidate_rule",
        payload={
            "project_dir": str(project_dir),
            "rule_id": style_rule["id"],
            "status": "verified",
            "reason": "approved",
        },
    ))
    assert style_review.ok

    naturalization_review = handle_request(CommandRequest(
        command="review_candidate_rule",
        payload={
            "project_dir": str(project_dir),
            "rule_id": naturalization_rule["id"],
            "status": "verified",
            "reason": "approved",
        },
    ))
    assert naturalization_review.ok

    config = json.loads((project_dir / "working" / "config" / "translation_config.json").read_text(encoding="utf-8"))
    assert config["style_preferences"]["project_profile"] == "dialogue_natural"
    assert config["naturalization"]["compact_sentences"] is True
