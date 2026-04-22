#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_number_converter.py — Unit tests for the algorithmic NumberConverter.

Tests cover:
    - Core number parsing (零 to 兆+)
    - Edge cases (两, implicit 十, 零 placeholder, nested 万)
    - Weekday pattern matching
    - Lunar date pattern matching
    - Integration with TrieEngine (NumberConverter vs Trie priority)
"""

import sys
import os
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.number_converter import (
    NumberConverter,
    ConversionResult,
    parse_chinese_number,
    _parse_section,
)


# ─────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────

@pytest.fixture
def converter():
    return NumberConverter()


# ─────────────────────────────────────────────────
# Core Number Parsing (_parse_section)
# ─────────────────────────────────────────────────

class TestParseSection:
    """Test the sub-万 section parser."""

    def test_single_digit(self):
        assert _parse_section("三") == 3

    def test_tens(self):
        assert _parse_section("三十") == 30

    def test_tens_with_ones(self):
        assert _parse_section("三十五") == 35

    def test_implicit_one_before_ten(self):
        """十三 = 13 (implicit 一 before 十)"""
        assert _parse_section("十三") == 13

    def test_implicit_ten_alone(self):
        """十 = 10"""
        assert _parse_section("十") == 10

    def test_hundreds(self):
        assert _parse_section("三百") == 300

    def test_hundreds_with_tens_and_ones(self):
        assert _parse_section("三百四十五") == 345

    def test_hundreds_zero_ones(self):
        """一百零三 = 103 (零 as placeholder)"""
        assert _parse_section("一百零三") == 103

    def test_thousands(self):
        assert _parse_section("三千") == 3000

    def test_full_section(self):
        assert _parse_section("三千四百五十六") == 3456

    def test_thousand_zero_hundred(self):
        """一千零三 = 1003"""
        assert _parse_section("一千零三") == 1003

    def test_thousand_zero_ten(self):
        """一千零一十 = 1010"""
        assert _parse_section("一千零一十") == 1010

    def test_liang_thousand(self):
        """两千 = 2000"""
        assert _parse_section("两千") == 2000

    def test_empty(self):
        assert _parse_section("") == 0

    def test_zero_alone(self):
        assert _parse_section("零") == 0


# ─────────────────────────────────────────────────
# Full Number Parsing (parse_chinese_number)
# ─────────────────────────────────────────────────

class TestParseChineseNumber:
    """Test the full hierarchical parser (兆/亿/万/base)."""

    def test_simple_numbers(self):
        assert parse_chinese_number("一百") == 100
        assert parse_chinese_number("二百五十") == 250
        assert parse_chinese_number("九百九十九") == 999

    def test_thousands(self):
        assert parse_chinese_number("一千") == 1000
        assert parse_chinese_number("一千一百") == 1100
        assert parse_chinese_number("一千九百九十九") == 1999

    def test_wan(self):
        """万 = 10,000"""
        assert parse_chinese_number("一万") == 10000
        assert parse_chinese_number("一万二千") == 12000
        assert parse_chinese_number("一万二千三百四十五") == 12345

    def test_wan_with_zero(self):
        """一万零三 = 10003"""
        assert parse_chinese_number("一万零三") == 10003

    def test_nested_wan(self):
        """三千万 = 30,000,000 (3000 × 万)"""
        assert parse_chinese_number("三千万") == 30000000
        assert parse_chinese_number("五千三百万") == 53000000

    def test_yi(self):
        """亿 = 100,000,000"""
        assert parse_chinese_number("一亿") == 100000000
        assert parse_chinese_number("五亿") == 500000000

    def test_yi_with_wan(self):
        """五亿三千万 = 530,000,000"""
        assert parse_chinese_number("五亿三千万") == 530000000

    def test_yi_with_remainder(self):
        """一亿二千三百万四千五百六十七 = 123,004,567"""
        assert parse_chinese_number("一亿二千三百万四千五百六十七") == 123004567

    def test_zhao(self):
        """兆 = 10^12"""
        assert parse_chinese_number("一兆") == 1000000000000
        assert parse_chinese_number("三兆") == 3000000000000

    def test_liang_variants(self):
        """两 = 2 (used before multipliers)"""
        assert parse_chinese_number("两千") == 2000
        assert parse_chinese_number("两百") == 200
        assert parse_chinese_number("两万") == 20000
        assert parse_chinese_number("两亿") == 200000000

    def test_traditional_chars(self):
        """Traditional Chinese number characters"""
        assert parse_chinese_number("壹佰") == 100
        assert parse_chinese_number("貳仟") == 2000
        assert parse_chinese_number("萬") == 10000  # implicit 1

    def test_ten_alone(self):
        assert parse_chinese_number("十三") == 13
        assert parse_chinese_number("十") == 10

    def test_invalid(self):
        assert parse_chinese_number("") is None
        assert parse_chinese_number("abc") is None

    def test_zero(self):
        assert parse_chinese_number("零零") == 0


# ─────────────────────────────────────────────────
# NumberConverter.try_convert (full interface)
# ─────────────────────────────────────────────────

class TestTryConvert:
    """Test the public try_convert interface."""

    def test_number_basic(self, converter):
        r = converter.try_convert("三千四百五十六", 0)
        assert r is not None
        assert r.text == "3456"
        assert r.consumed == 7
        assert r.conv_type == "number"

    def test_number_in_context(self, converter):
        """Number embedded in text: should only consume number chars."""
        text = "他有三千个苹果"
        r = converter.try_convert(text, 2)  # starts at 三
        assert r is not None
        assert r.text == "3000"
        assert r.consumed == 2  # 三千 (个 is not a number char)

    def test_single_digit_rejected(self, converter):
        """Single digits should NOT be converted (let Trie handle)."""
        assert converter.try_convert("三个", 0) is None
        assert converter.try_convert("一定", 0) is None

    def test_weekday_xingqi(self, converter):
        r = converter.try_convert("星期一", 0)
        assert r.text == "thứ Hai"
        assert r.consumed == 3

    def test_weekday_xingqi_sunday(self, converter):
        r = converter.try_convert("星期天", 0)
        assert r.text == "Chủ nhật"
        assert r.consumed == 3

    def test_weekday_zhou(self, converter):
        r = converter.try_convert("周三", 0)
        assert r.text == "thứ Tư"
        assert r.consumed == 2

    def test_weekday_zhoumo(self, converter):
        r = converter.try_convert("周末", 0)
        assert r.text == "cuối tuần"
        assert r.consumed == 2

    def test_weekday_libai(self, converter):
        r = converter.try_convert("礼拜天", 0)
        assert r.text == "Chủ nhật"
        assert r.consumed == 3

    def test_all_weekdays(self, converter):
        expected = {
            '星期一': 'thứ Hai', '星期二': 'thứ Ba', '星期三': 'thứ Tư',
            '星期四': 'thứ Năm', '星期五': 'thứ Sáu', '星期六': 'thứ Bảy',
            '星期天': 'Chủ nhật', '星期日': 'Chủ nhật',
            '周一': 'thứ Hai', '周二': 'thứ Ba', '周三': 'thứ Tư',
            '周四': 'thứ Năm', '周五': 'thứ Sáu', '周六': 'thứ Bảy',
            '周日': 'Chủ nhật', '周末': 'cuối tuần',
        }
        for src, exp in expected.items():
            r = converter.try_convert(src, 0)
            assert r is not None, f"Failed to match: {src}"
            assert r.text == exp, f"{src}: expected '{exp}', got '{r.text}'"

    def test_lunar_basic(self, converter):
        r = converter.try_convert("初一", 0)
        assert r.text == "mùng một"
        assert r.consumed == 2

    def test_lunar_five_special(self, converter):
        """初五 uses 'mồng' (not 'mùng')."""
        r = converter.try_convert("初五", 0)
        assert r.text == "mồng năm"

    def test_all_lunar_dates(self, converter):
        expected = {
            '初一': 'mùng một', '初二': 'mùng hai', '初三': 'mùng ba',
            '初四': 'mùng bốn', '初五': 'mồng năm', '初六': 'mùng sáu',
            '初七': 'mùng bảy', '初八': 'mùng tám', '初九': 'mùng chín',
            '初十': 'mùng mười',
        }
        for src, exp in expected.items():
            r = converter.try_convert(src, 0)
            assert r is not None, f"Failed to match: {src}"
            assert r.text == exp, f"{src}: expected '{exp}', got '{r.text}'"

    def test_no_match(self, converter):
        assert converter.try_convert("abcdef", 0) is None
        assert converter.try_convert("你好", 0) is None

    def test_position_offset(self, converter):
        """try_convert at non-zero position."""
        text = "abc星期五xyz"
        r = converter.try_convert(text, 3)
        assert r.text == "thứ Sáu"
        assert r.consumed == 3


# ─────────────────────────────────────────────────
# Integration with TrieEngine
# ─────────────────────────────────────────────────

class TestTrieIntegration:
    """Test that NumberConverter integrates correctly with TrieEngine."""

    def test_trie_with_number_converter(self):
        from src.core.trie_engine import TrieEngine

        trie = TrieEngine(enable_number_converter=True)
        # Insert some dictionary entries
        trie.insert("一定", "nhất định", priority=2)
        trie.insert("三角", "tam giác", priority=2)
        trie.insert("一", "nhất", priority=1)

        # 一定 should use Trie (2 chars > 1 char number match)
        result = trie.translate_text("一定")
        assert result == "nhất định"

        # 三角 should use Trie (2 chars > 1 char number match)
        result = trie.translate_text("三角")
        assert result == "tam giác"

    def test_trie_number_wins_over_short_trie(self):
        from src.core.trie_engine import TrieEngine

        trie = TrieEngine(enable_number_converter=True)
        trie.insert("一", "nhất", priority=1)

        # 一千二百 → NumberConverter matches 4 chars, Trie matches 一=1 char
        # NumberConverter should win
        result = trie.translate_text("一千二百")
        assert result == "1200"

    def test_trie_without_number_converter(self):
        from src.core.trie_engine import TrieEngine

        trie = TrieEngine(enable_number_converter=False)
        trie.insert("一", "nhất", priority=1)
        trie.insert("千", "thiên", priority=1)

        # Without NumberConverter, falls back to Trie entry by entry
        result = trie.translate_text("一千")
        assert result == "nhấtthiên"

    def test_weekday_in_sentence(self):
        from src.core.trie_engine import TrieEngine

        trie = TrieEngine(enable_number_converter=True)
        trie.insert("我", "ta", priority=2)
        trie.insert("在", "tại", priority=2)

        result = trie.translate_text("我在星期一")
        assert "thứ Hai" in result


# ─────────────────────────────────────────────────
# Regression: verify original data coverage
# ─────────────────────────────────────────────────

class TestRegression:
    """Spot-check that algorithm matches original hardcoded entries."""

    @pytest.fixture
    def converter(self):
        return NumberConverter()

    @pytest.mark.parametrize("chinese,expected_value", [
        ("一千一百一十一", 1111),
        ("一千九百九十九", 1999),
        ("二千", 2000),
        ("三千三百三十三", 3333),
        ("四千四百四十四", 4444),
        ("一万一千", 11000),
        ("七十一万七千", 717000),
        ("九百九十九", 999),
        ("一千零一", 1001),
        ("一千一百零一", 1101),
        ("四百零四", 404),
        ("一千八百八十八", 1888),
    ])
    def test_original_entries(self, converter, chinese, expected_value):
        r = converter.try_convert(chinese, 0)
        assert r is not None, f"Failed to convert: {chinese}"
        assert r.text == str(expected_value), f"{chinese}: expected {expected_value}, got {r.text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
