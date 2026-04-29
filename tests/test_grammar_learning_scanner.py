#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for coach-only non-LLM grammar pattern scanning."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.learning.grammar_pattern_scanner import (
    GrammarLearningPatternScanner,
    GrammarPatternScanner,
    detect_protected_spans,
)
from src.ui.command_protocol import CommandRequest
from src.ui.sidecar_bridge import handle_request


def test_known_rules_and_unknown_pair_candidates_are_mined():
    text = """
第1章 测试
只要他愿意，就能离开这里。
如果天气好，我们就出门。
与其坐以待毙，不如主动出击。
与其继续等待，不如现在行动。
与其退缩，不如拼一次。
偏偏他没有停下。
偏偏雨又下大了。
偏偏门打不开。
PS：明天更新，求月票。
"""

    report = GrammarLearningPatternScanner().analyze_text(text, unknown_min_count=2)

    known = {item["rule_id"]: item for item in report["known_rules"]}
    assert known["condition_zhiyao_jiu"]["count"] == 1
    assert known["condition_ruguo_jiu"]["count"] == 1
    assert known["preference_yuqi_buru"]["count"] == 3

    unknown = {item["pattern_text"]: item for item in report["unknown_candidates"]}
    assert unknown["偏偏"]["frequency"] >= 3
    assert unknown["偏偏"]["status"] == "review"
    assert unknown["偏偏"]["guessed_category"] == "counter_expectation"
    assert report["summary"]["noise_counts"]["author_note"] == 1


def test_known_scanner_skips_system_panel_protected_spans():
    text = "【系统提示：只要完成任务就能获得奖励】"
    matches = GrammarPatternScanner().scan(text, detect_protected_spans(text))

    assert matches == []


def test_sidecar_grammar_scan_creates_review_only_candidate_rule(tmp_path):
    create_response = handle_request(
        CommandRequest(
            command="create_project",
            payload={
                "base_dir": str(tmp_path),
                "project_id": "grammar-scan-demo",
            },
        )
    )
    assert create_response.ok
    project_dir = Path(create_response.data["project_dir"])
    sample_path = tmp_path / "sample.txt"
    sample_path.write_text(
        "\n".join(
            [
                "第1章 测试",
                "偏偏他没有停下。",
                "偏偏雨又下大了。",
                "偏偏门打不开。",
            ]
        ),
        encoding="utf-8",
    )

    scan_response = handle_request(
        CommandRequest(
            command="scan_grammar_learning_patterns",
            payload={
                "project_dir": str(project_dir),
                "filepath": str(sample_path),
                "unknown_min_count": 2,
                "max_candidate_rules": 5,
            },
        )
    )
    assert scan_response.ok
    assert scan_response.data["report"]["metadata"]["pipeline_scope"] == "translator_learning_coach_only"

    grammar_rules = [
        rule
        for rule in scan_response.data["rules"]
        if rule["rule_type"] == "grammar_pattern_candidate"
    ]
    assert grammar_rules

    review_response = handle_request(
        CommandRequest(
            command="review_candidate_rule",
            payload={
                "project_dir": str(project_dir),
                "rule_id": grammar_rules[0]["id"],
                "status": "verified",
                "reason": "approved for coach backlog",
            },
        )
    )
    assert review_response.ok
    assert review_response.data["applied"]["updated"] == "grammar_learning_backlog"

    backlog_path = project_dir / "working" / "grammar_learning" / "verified_patterns.json"
    backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
    assert backlog[0]["status"] == "review"
    assert not (project_dir / "working" / "config" / "translation_config.json").exists()
