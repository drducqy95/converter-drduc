#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for v23 core hardening foundations."""

from __future__ import annotations

import pytest

from src.engine.rbmt_translator import RBMTTranslator
from src.grammar.clause_segmenter import ClauseBoundary, ClauseSegmenter
from src.grammar.relation_detector import RelationDetector, RelationType
from src.pipeline.noise_filter import NoiseAction, NoiseFilter
from src.pipeline.packet import LockLevel, ProtectedSpan, SegmentType
from src.pipeline.protected_span_registry import ProtectedSpanRegistry
from src.pipeline.segment_classifier import SegmentClassifier
from src.state.translation_memory import TranslationMemory


def test_rbmt_output_never_goes_to_approved_tm(tmp_path):
    tm_path = tmp_path / "tm.sqlite"
    translator = RBMTTranslator(tm_db_path=tm_path)
    try:
        translator.translate_text("他说道：“浪漫！”", config={"genre_hints": ["general"]})
    finally:
        translator.close()

    tm = TranslationMemory(tm_path)
    try:
        assert tm.exists_in_machine("他说道：“浪漫！”")
        assert not tm.exists_in_approved("他说道：“浪漫！”")
    finally:
        tm.close()


def test_only_reviewed_output_can_promote_to_approved(tmp_path):
    tm = TranslationMemory(tmp_path / "tm.sqlite")
    try:
        tm.store_machine("他走了。", "Hắn đi rồi.", quality_score=0.82)
        pending_id = tm.save_human_review(
            "他走了。",
            machine_target="Hắn đi rồi.",
            edited_target="Hắn đã đi.",
            reviewer="tester",
            review_status="pending",
        )
        with pytest.raises(ValueError):
            tm.promote_to_approved(pending_id)

        review_id = tm.save_human_review(
            "他走了。",
            machine_target="Hắn đi rồi.",
            edited_target="Hắn đã đi.",
            reviewer="tester",
            review_status="approved",
        )
        tm.promote_to_approved(review_id)
        assert tm.exists_in_approved("他走了。")
        assert tm.lookup("他走了。").target_text == "Hắn đã đi."
    finally:
        tm.close()


def test_tm_lookup_prefers_approved_before_machine(tmp_path):
    tm = TranslationMemory(tmp_path / "tm.sqlite")
    try:
        tm.store_machine("林动突破。", "Machine target", quality_score=0.80)
        tm.store_approved("林动突破。", "Approved target", reviewer="tester")
        hit = tm.lookup("林动突破。")
        assert hit is not None
        assert hit.target_text == "Approved target"
        assert hit.status == "approved"
    finally:
        tm.close()


def test_tm_tracks_last_accessed_and_evicts_machine_lru(tmp_path):
    tm = TranslationMemory(tmp_path / "tm.sqlite")
    try:
        tm.store_machine("甲", "Machine A", quality_score=0.50)
        tm.store_machine("乙", "Machine B", quality_score=0.50)
        tm.store_machine("丙", "Machine C", quality_score=0.50)
        assert tm.machine_suggestion("乙").target_text == "Machine B"

        removed = tm.evict_machine_entries(2)
        assert removed == 1
        assert not tm.exists_in_machine("甲")
        assert tm.exists_in_machine("乙")
        assert tm.exists_in_machine("丙")

        row = tm.conn.execute(
            "SELECT hit_count, last_accessed FROM tm_machine WHERE source_text = ?",
            ("乙",),
        ).fetchone()
        assert row["hit_count"] == 1
        assert row["last_accessed"]
    finally:
        tm.close()


def test_tm_auto_evicts_machine_entries_when_capacity_is_configured(tmp_path):
    tm = TranslationMemory(tmp_path / "tm.sqlite", max_machine_entries=1)
    try:
        tm.store_machine("甲", "Machine A")
        tm.store_machine("乙", "Machine B")
        count = tm.conn.execute("SELECT COUNT(*) AS count FROM tm_machine").fetchone()["count"]
        assert count == 1
        assert tm.exists_in_machine("乙")
    finally:
        tm.close()


def test_segment_classifier_required_cases():
    classifier = SegmentClassifier()
    cases = [
        ("【面板未开启】", SegmentType.SYSTEM_PROMPT),
        ("第三百二十一章 黑夜之心", SegmentType.CHAPTER_TITLE),
        ("（PS：明天中午12点更新）", SegmentType.AUTHOR_NOTE),
        ("求月票！感谢大家支持！", SegmentType.AUTHOR_NOTE),
        ("【奇迹之冠冕号】启动完成。", SegmentType.NARRATION),
        ("他激活了【蜘蛛感应】技能。", SegmentType.NARRATION),
        ("李宇冷声道：'你走吧。'", SegmentType.DIALOGUE),
        ("他心中暗道：这人到底是谁？", SegmentType.THOUGHT),
        ("【本章完】", SegmentType.AUTHOR_NOTE),
        ("楼主说得对！顶一下！", SegmentType.FORUM_POST),
    ]
    for text, expected in cases:
        assert classifier.classify(text).segment_type == expected


def test_protected_span_registry_resolves_overlaps_by_priority():
    registry = ProtectedSpanRegistry()
    registry.claim(ProtectedSpan(0, 4, "系统面板", "BRACKET_ITEM", 50, "pattern"))
    registry.claim(ProtectedSpan(0, 4, "系统面板", "SYSTEM_UI", 100, "system", LockLevel.HARD_LOCK.value))
    registry.claim(ProtectedSpan(2, 6, "面板打开", "ENTITY", 90, "entity"))

    resolved = registry.resolve_overlap()
    assert len(resolved) == 1
    assert resolved[0].span_type == "SYSTEM_UI"
    assert registry.is_protected(1, 3)


def test_noise_filter_false_drop_prevention_and_author_noise():
    classifier = SegmentClassifier()
    noise = NoiseFilter()
    keep_cases = [
        "【奇迹之冠冕号】启动完成。",
        "他获得了【龙之心脏基因链】。",
        "系统提示：任务完成。",
        "【面板未开启】",
    ]
    for text in keep_cases:
        packet = classifier.build_packet(text, chapter_id="chapter-001", position=0)
        assert noise.decide(packet).action == NoiseAction.KEEP

    drop_cases = [
        "PS：明天中午12点更新。",
        "求月票！",
        "【新书上传，求收藏推荐】",
        "本章完",
        "作者有话说",
    ]
    for text in drop_cases:
        packet = classifier.build_packet(text, chapter_id="chapter-001", position=0)
        assert noise.decide(packet).action in {NoiseAction.DROP, NoiseAction.REVIEW, NoiseAction.METADATA}


def test_clause_segmenter_respects_protected_spans_and_detects_boundaries():
    text = "他获得了【龙之心脏，基因链】，如果敌人靠近，就会启动。"
    protected = [ProtectedSpan(4, 14, "【龙之心脏，基因链】", "ENTITY", 90, "test")]
    clauses = ClauseSegmenter().segment(text, protected)
    assert all("【龙之心脏" in clause.text or "基因链】" not in clause.text for clause in clauses)
    assert any(clause.boundary == ClauseBoundary.CONDITIONAL for clause in clauses)


def test_relation_detector_marker_map():
    clauses = ClauseSegmenter().segment("只要你回来，我就出手。哪怕失败，也要试。")
    relations = RelationDetector().detect(clauses)
    relation_types = {item.relation_type for item in relations}
    assert RelationType.CONDITION in relation_types
    assert RelationType.CONCESSION in relation_types
