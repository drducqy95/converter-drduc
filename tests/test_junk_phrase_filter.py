#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for user-maintained junk phrase filtering."""

from src.engine.junk_phrase_filter import JunkPhraseFilter
from src.engine.rbmt_translator import RBMTTranslator


def test_junk_phrase_filter_removes_user_source_boilerplate():
    result = JunkPhraseFilter().apply_source(
        "\u6b63\u6587\u5f00\u59cb\u3002\u6c42\u6708\u7968\uff0c\u6c42\u63a8\u8350\u3002\u7ee7\u7eed\u6545\u4e8b\u3002",
        {"ignored_phrases": ["\u6c42\u6708\u7968\uff0c\u6c42\u63a8\u8350"]},
    )

    assert "\u6c42\u6708\u7968" not in result.text
    assert result.traces[0]["fallback_level"] == "junk_phrase_filter"


def test_junk_phrase_filter_removes_user_target_boilerplate():
    result = JunkPhraseFilter().apply_target(
        "Nội dung chính. cầu nguyệt phiếu. Tiếp tục.",
        {"ignored_phrases": [{"source": "\u6c42\u6708\u7968", "target": "cầu nguyệt phiếu"}]},
    )

    assert "cầu nguyệt phiếu" not in result.text
    assert result.traces[0]["reason"].startswith("user_junk_phrase:target")


def test_rbmt_translation_pipeline_applies_user_junk_phrase_filter():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            "\u6c42\u6708\u7968\u3002\u590f\u5929\u9a90\u8bf4\u9053\uff1a\u201c\u4f60\u597d\u3002\u201d",
            config={"ignored_phrases": ["\u6c42\u6708\u7968"]},
        )
    finally:
        translator.close()

    assert "\u6c42\u6708\u7968" not in result.clean_text
    assert "\u6c42\u6708\u7968" not in "\n".join(segment.source_text for segment in result.segments)
    assert any(trace["stage"] == "junk_filter" for trace in result.segments[0].trace)
