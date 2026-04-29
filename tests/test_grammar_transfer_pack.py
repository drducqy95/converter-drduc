#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for grammar-plan additions from plans/Grammar."""

from src.engine.number_converter import NumberConverter
from src.engine.rbmt_translator import RBMTTranslator
from src.grammar.clause_segmenter import ClauseSegmenter
from src.grammar.transfer_engine import GrammarTransferEngine


def test_source_grammar_transfer_rewrites_core_discourse_frames():
    result = GrammarTransferEngine().rewrite_source("只要你回来，我就出手。哪怕失败，也要试。")

    assert "chỉ cần" in result.text
    assert "thì" in result.text
    assert "dù" in result.text
    assert "cũng" in result.text
    assert "只要" not in result.text
    assert "哪怕" not in result.text
    assert {trace["fallback_level"] for trace in result.traces} == {"grammar_transfer"}


def test_source_grammar_transfer_handles_passive_parallel_and_protected_spans():
    engine = GrammarTransferEngine()

    passive = engine.rewrite_source("终为天下人所承认。")
    assert passive.text.startswith("终được 天下人承认")
    assert "所" not in passive.text

    parallel = engine.rewrite_source("一边扫描一边传输数据。")
    assert "vừa 扫描 vừa" in parallel.text

    protected = engine.rewrite_source("【如果失败】一边扫描一边传输数据。")
    assert "【如果失败】" in protected.text
    assert "vừa 扫描 vừa" in protected.text


def test_source_grammar_transfer_rewrites_mined_template_book_frames():
    engine = GrammarTransferEngine()

    text = (
        "\u4e0e\u5176\u5750\u7b49\uff0c\u4e0d\u5982\u51fa\u624b\u3002"
        "\u65e2\u80fd\u653b\u51fb\uff0c\u53c8\u80fd\u9632\u5b88\u3002"
        "\u8d8a\u60f3\u8d8a\u89c9\u5f97\u4e0d\u5bf9\u3002"
        "\u4e4b\u6240\u4ee5\u5931\u8d25\uff0c\u662f\u56e0\u4e3a\u4ed6\u8f7b\u654c\u3002"
        "\u53ea\u6709\u8fdb\u5165\u5c71\u95e8\uff0c\u624d\u80fd\u901a\u8fc7\u8003\u9a8c\u3002"
    )
    result = engine.rewrite_source(text)

    assert "thà" in result.text
    assert "chẳng bằng" in result.text
    assert "vừa" in result.text
    assert "càng" in result.text
    assert "sở dĩ" in result.text
    assert "chỉ khi" in result.text
    assert {trace["fallback_level"] for trace in result.traces} == {"grammar_transfer"}


def test_clause_segmenter_auto_protects_bracket_commas():
    text = "他获得了【龙之心脏，基因链】，如果敌人靠近，就会启动。"
    clauses = ClauseSegmenter().segment(text)

    assert all("【龙之心脏" not in clause.text or "基因链】" in clause.text for clause in clauses)
    assert any("如果敌人靠近" in clause.text for clause in clauses)


def test_number_converter_semantic_percent_fraction_countdown_and_rating():
    converter = NumberConverter()
    cases = {
        "百分之九十八": ("98%", "percent"),
        "百分之九十八点几": ("hơn 98%", "percent_decimal_approx"),
        "百分之七八十": ("khoảng 70-80%", "percent_approx"),
        "百分之一百二十": ("120%", "percent_over_100"),
        "三分之一": ("một phần ba", "fraction"),
        "二分之一": ("một nửa", "fraction"),
        "倒计时30秒": ("đếm ngược 30 giây", "countdown"),
        "T-30秒": ("T-30 giây", "countdown_t"),
        "持续时间-720小时": ("thời gian duy trì: 720 giờ", "duration_dash"),
        "SSS评价": ("đánh giá SSS", "rating"),
        "第七秒": ("giây thứ 7", "ordinal_time"),
        "第一分二十八秒": ("1 phút 28 giây", "elapsed_time"),
        "三次方": ("lũy thừa 3", "power"),
    }

    for source, (expected, conv_type) in cases.items():
        result = converter.try_convert(source, 0)
        assert result is not None, source
        assert result.text == expected
        assert result.conv_type == conv_type


def test_rbmt_attaches_grammar_transfer_trace_before_lexical_decode():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text("哪怕失败，也要试。")
    finally:
        translator.close()

    assert "Dù" in result.clean_text
    assert "cũng" in result.clean_text
    assert any(trace["stage"] == "grammar_transfer" for trace in result.segments[0].trace)
