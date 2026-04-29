#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for Trie Engine, Dictionary Compiler, and LuatNhan Engine."""

import sys
import os
import json
import pytest
import sqlite3
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.trie_engine import TrieEngine, TrieMatch
from src.core.md_dictionary_compiler import (
    DictionaryCompiler,
    DictEntry,
    GrammarPattern,
    parse_bulk_md,
    parse_rich_md,
    parse_grammar_md,
    _parse_yaml_frontmatter,
    _parse_md_table,
)
from src.core.luat_nhan_engine import LuatNhanEngine


# ─────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "dictionaries" / "_compiled" / "trie_cache.db"


@pytest.fixture
def loaded_trie():
    """Load Trie from compiled DB (skip if DB doesn't exist)."""
    if not DB_PATH.exists():
        pytest.skip("Compiled DB not found — run compiler first")
    trie = TrieEngine()
    trie.load_from_sqlite(str(DB_PATH))
    return trie


@pytest.fixture
def loaded_luatnhan():
    """Load LuatNhan from compiled DB."""
    if not DB_PATH.exists():
        pytest.skip("Compiled DB not found — run compiler first")
    engine = LuatNhanEngine()
    engine.load_from_sqlite(str(DB_PATH))
    return engine


@pytest.fixture
def sample_bulk_md(tmp_path):
    """Create a sample Bulk MD file."""
    content = """---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: test
entries_count: 3
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target | one_mean | notes |
| --- | --- | --- | --- |
| 修为 | tu vi | true | |
| 境界 | cảnh giới;ranh giới | false | |
| 突破 | đột phá | true | |
"""
    filepath = tmp_path / "_bulk_test.md"
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


@pytest.fixture
def sample_rich_md(tmp_path):
    """Create a sample Rich MD file."""
    content = """---
source: "林动"
target: "Lâm Động"
priority: 5
category: "character"
one_mean: true
locked: true
notes: "Main character"
---

## Description
Lâm Động is the protagonist.
"""
    filepath = tmp_path / "lin_dong.md"
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


@pytest.fixture
def sample_grammar_md(tmp_path):
    """Create a sample Grammar MD file."""
    content = """---
type: grammar_patterns
category: luat_nhan_primary
patterns_count: 3
compiled_from: "test"
last_compiled: "2026-01-01"
---

| pattern | replacement |
| --- | --- |
| {0}军团 | quân đoàn {0} |
| {0}大人 | {0} đại nhân |
| {0}宗 | {0} tông |
"""
    filepath = tmp_path / "luat_nhan_test.md"
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


# ─────────────────────────────────────────────────
# Test: YAML Frontmatter Parser
# ─────────────────────────────────────────────────

class TestYAMLFrontmatter:
    def test_parse_valid(self):
        content = "---\ntype: test\npriority: 3\n---\n\nBody text"
        meta, body = _parse_yaml_frontmatter(content)
        assert meta["type"] == "test"
        assert meta["priority"] == 3
        assert "Body text" in body

    def test_parse_no_frontmatter(self):
        content = "Just regular text"
        meta, body = _parse_yaml_frontmatter(content)
        assert meta == {}
        assert body == content

    def test_parse_empty(self):
        meta, body = _parse_yaml_frontmatter("")
        assert meta == {}


# ─────────────────────────────────────────────────
# Test: MD Table Parser
# ─────────────────────────────────────────────────

class TestMDTable:
    def test_parse_simple_table(self):
        body = """| source | target |
| --- | --- |
| 修为 | tu vi |
| 境界 | cảnh giới |"""
        rows = _parse_md_table(body)
        assert len(rows) == 2
        assert rows[0]["source"] == "修为"
        assert rows[0]["target"] == "tu vi"

    def test_parse_with_escaped_pipe(self):
        body = """| source | target |
| --- | --- |
| test | a\\|b |"""
        rows = _parse_md_table(body)
        assert len(rows) == 1
        assert rows[0]["target"] == "a|b"


# ─────────────────────────────────────────────────
# Test: Bulk MD Parser
# ─────────────────────────────────────────────────

class TestBulkMDParser:
    def test_parse_entries(self, sample_bulk_md):
        entries = list(parse_bulk_md(sample_bulk_md))
        assert len(entries) == 3
        assert entries[0].source == "修为"
        assert entries[0].target == "tu vi"
        assert entries[0].priority == 2
        assert entries[0].one_mean == True

    def test_parse_priority_from_yaml(self, sample_bulk_md):
        entries = list(parse_bulk_md(sample_bulk_md))
        assert all(e.priority == 2 for e in entries)

    def test_parse_extra_metadata_columns(self, tmp_path):
        filepath = tmp_path / "_bulk_reference.md"
        filepath.write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 1
category: reference_test
entry_role: reference
entries_count: 1
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target | pinyin | han_viet_readings | full_explanation |
| --- | --- | --- | --- | --- |
| 阿 | A | a1 | A | rich explanation |
""", encoding='utf-8')

        entries = list(parse_bulk_md(str(filepath)))
        assert len(entries) == 1
        assert entries[0].entry_role == "reference"
        meta = json.loads(entries[0].metadata_json)
        assert meta["pinyin"] == "a1"
        assert meta["han_viet_readings"] == "A"


# ─────────────────────────────────────────────────
# Test: Rich MD Parser
# ─────────────────────────────────────────────────

class TestRichMDParser:
    def test_parse_character(self, sample_rich_md):
        entry = parse_rich_md(sample_rich_md)
        assert entry is not None
        assert entry.source == "林动"
        assert entry.target == "Lâm Động"
        assert entry.priority == 5
        assert entry.locked == True


# ─────────────────────────────────────────────────
# Test: Grammar MD Parser
# ─────────────────────────────────────────────────

class TestGrammarMDParser:
    def test_parse_patterns(self, sample_grammar_md):
        patterns = list(parse_grammar_md(sample_grammar_md))
        assert len(patterns) == 3
        assert patterns[0].pattern == "{0}军团"
        assert patterns[0].replacement == "quân đoàn {0}"


# ─────────────────────────────────────────────────
# Test: Trie Engine (Unit)
# ─────────────────────────────────────────────────

class TestTrieEngineUnit:
    def test_insert_and_lookup(self):
        trie = TrieEngine()
        trie.insert("修为", "tu vi", priority=2)
        result = trie.lookup_exact("修为")
        assert result is not None
        assert result.target == "tu vi"
        assert result.priority == 2

    def test_longest_prefix(self):
        trie = TrieEngine()
        trie.insert("大", "đại", priority=1)
        trie.insert("大道", "đại đạo", priority=2)
        trie.insert("大道至简", "đại đạo chí giản", priority=2)

        result = trie.lookup("大道至简之理", 0)
        assert result is not None
        assert result.source == "大道至简"
        assert result.length == 4

    def test_priority_override(self):
        trie = TrieEngine()
        trie.insert("修为", "tu vi (low)", priority=1)
        trie.insert("修为", "tu vi (high)", priority=3)
        result = trie.lookup_exact("修为")
        assert result.target == "tu vi (high)"

    def test_not_found(self):
        trie = TrieEngine()
        result = trie.lookup_exact("不存在")
        assert result is None

    def test_cjk_detection(self):
        assert TrieEngine._is_cjk('修') == True
        assert TrieEngine._is_cjk('A') == False
        assert TrieEngine._is_cjk('ö') == False

    def test_translate_text(self):
        trie = TrieEngine()
        trie.insert("修为", "tu vi")
        trie.insert("突破", "đột phá")
        result = trie.translate_text("修为突破")
        assert "tu vi" in result
        assert "đột phá" in result

    def test_translate_text_uses_reading_fallback(self):
        trie = TrieEngine(enable_number_converter=False)
        trie._reading_fallbacks["㚻"] = "kê"
        result = trie.translate_text("㚻")
        assert result == "kê"


# ─────────────────────────────────────────────────
# Test: Trie Engine (Integration with compiled DB)
# ─────────────────────────────────────────────────

class TestTrieEngineIntegration:
    def test_load_from_sqlite(self, loaded_trie):
        assert loaded_trie.size > 700000

    def test_common_terms(self, loaded_trie):
        """Test that common VietPhrase terms are found."""
        must_find = {
            "修为": "tu vi",
            "丹田": "đan điền",
            "炼丹": "luyện đan",
        }
        for source, expected_start in must_find.items():
            result = loaded_trie.lookup_exact(source)
            assert result is not None, f"{source} not found"
            assert expected_start in result.target, f"{source}: expected '{expected_start}' in '{result.target}'"

    def test_names_priority(self, loaded_trie):
        """Names (P4) should be findable."""
        # Names from Names.txt should be priority 4
        # Check a few common names
        pass  # Will be populated when we know specific names

    def test_phienam_fallback(self, loaded_trie):
        """Single characters should fall back to PhienAm (P1)."""
        # Most single CJK characters should have a PhienAm reading
        result = loaded_trie.lookup_exact("人")
        assert result is not None

    def test_lookup_performance(self, loaded_trie):
        """Lookup should be < 1ms."""
        import time
        start = time.time()
        for _ in range(10000):
            loaded_trie.lookup_exact("修为")
        elapsed = time.time() - start
        per_lookup_us = (elapsed / 10000) * 1_000_000
        assert per_lookup_us < 100, f"Lookup too slow: {per_lookup_us:.1f} µs"


# ─────────────────────────────────────────────────
# Test: LuatNhan Engine
# ─────────────────────────────────────────────────

class TestLuatNhanEngine:
    def test_load_rules(self, loaded_luatnhan):
        stats = loaded_luatnhan.get_stats()
        assert stats["total_rules"] > 16000
        assert stats["primary_rules"] > 200
        assert stats["extended_rules"] > 15000

    def test_apply_pattern(self):
        engine = LuatNhanEngine()
        engine.rules = [
            __import__('src.core.luat_nhan_engine', fromlist=['LuatNhanRule']).LuatNhanRule(
                pattern="{0}军团",
                replacement="quân đoàn {0}",
                pattern_key="军团",
                category="primary",
            )
        ]
        engine.set_entity_pairs([("天狼", "Thiên Lang")])
        result = engine.apply("天狼军团出发了")
        assert "quân đoàn Thiên Lang" in result


# ─────────────────────────────────────────────────
# Test: Dictionary Compiler
# ─────────────────────────────────────────────────

class TestDictionaryCompiler:
    def test_compile_sample(self, tmp_path):
        """Test compiling from sample MD files."""
        # Create directory structure
        vp_dir = tmp_path / "global" / "vietphrase"
        vp_dir.mkdir(parents=True)
        names_dir = tmp_path / "global" / "names"
        names_dir.mkdir(parents=True)
        grammar_dir = tmp_path / "global" / "grammar"
        grammar_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"
        
        # Write sample bulk VietPhrase
        (vp_dir / "_bulk_test.md").write_text("""---
type: bulk_dictionary
priority: 2
category: vietphrase
entries_count: 2
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修为 | tu vi |
| 境界 | cảnh giới |
""", encoding='utf-8')
        
        # Write sample names
        (names_dir / "_bulk_names.md").write_text("""---
type: bulk_dictionary
priority: 4
category: names
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 林动 | Lâm Động |
""", encoding='utf-8')
        
        # Write sample grammar
        (grammar_dir / "luat_nhan.md").write_text("""---
type: grammar_patterns
category: luat_nhan_primary
patterns_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| pattern | replacement |
| --- | --- |
| {0}大人 | {0} đại nhân |
""", encoding='utf-8')
        
        # Compile
        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()
        
        assert stats["entries_unique"] == 3  # 2 VP + 1 name
        assert stats["grammar_patterns"] == 1
        assert (compiled_dir / "trie_cache.db").exists()

    def test_source_manifest_marks_cache_stale_after_source_change(self, tmp_path):
        """Compiled SQLite metadata should identify stale Markdown sources."""
        vp_dir = tmp_path / "global" / "vietphrase"
        vp_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"
        source_file = vp_dir / "_bulk_test.md"
        source_file.write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: vietphrase
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修为 | tu vi |
""", encoding="utf-8")

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()

        assert stats["source_files_hashed"] == 1
        assert stats["source_manifest_hash"]
        assert compiler.source_cache_status()["stale"] is False

        conn = sqlite3.connect(str(compiled_dir / "trie_cache.db"))
        c = conn.cursor()
        c.execute("SELECT value FROM metadata WHERE key = 'source_manifest_json'")
        manifest = json.loads(c.fetchone()[0])
        conn.close()
        assert "global/vietphrase/_bulk_test.md" in manifest

        source_file.write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: vietphrase
entries_count: 2
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修为 | tu vi |
| 突破 | đột phá |
""", encoding="utf-8")

        status = compiler.source_cache_status()
        assert status["stale"] is True
        assert status["reason"] == "source_changed"
        assert status["changed_files"] == ["global/vietphrase/_bulk_test.md"]

    def test_priority_merge(self, tmp_path):
        """Higher priority should override lower."""
        vp_dir = tmp_path / "global" / "vietphrase"
        vp_dir.mkdir(parents=True)
        names_dir = tmp_path / "global" / "names"
        names_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"
        
        # 修为 at P2
        (vp_dir / "_bulk_vp.md").write_text("""---
type: bulk_dictionary
priority: 2
category: vp
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修为 | tu vi low |
""", encoding='utf-8')
        
        # 修为 at P4 (higher)
        (names_dir / "_bulk_names.md").write_text("""---
type: bulk_dictionary
priority: 4
category: names
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修为 | tu vi high |
""", encoding='utf-8')
        
        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        compiler.compile()
        
        # Verify in SQLite
        conn = sqlite3.connect(str(compiled_dir / "trie_cache.db"))
        c = conn.cursor()
        c.execute("SELECT target, priority FROM entries WHERE source = '修为'")
        row = c.fetchone()
        conn.close()
        
        assert row[0] == "tu vi high"
        assert row[1] == 4

    def test_compile_split_bulk_files(self, tmp_path):
        """Split bulk files without _bulk_ prefix should still compile."""
        vp_dir = tmp_path / "global" / "vietphrase"
        vp_dir.mkdir(parents=True)
        names_dir = tmp_path / "global" / "names"
        names_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"

        (vp_dir / "_vietphrase_1char.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: vietphrase_1char
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修 | tu |
""", encoding='utf-8')

        (names_dir / "_names_person_east.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 4
category: names_person_east
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 林动 | Lâm Động |
""", encoding='utf-8')

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()

        assert stats["entries_unique"] == 2

        conn = sqlite3.connect(str(compiled_dir / "trie_cache.db"))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM entries")
        count = c.fetchone()[0]
        conn.close()

        assert count == 2

    def test_reference_and_normalization_are_separated(self, tmp_path):
        """Reference EN entries and normalization rules must not enter runtime entries."""
        vp_dir = tmp_path / "global" / "vietphrase"
        vp_dir.mkdir(parents=True)
        ref_dir = tmp_path / "global" / "en_vi"
        ref_dir.mkdir(parents=True)
        norm_dir = tmp_path / "global" / "normalization"
        norm_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"

        (vp_dir / "_bulk_vp.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: vietphrase
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 修为 | tu vi |
""", encoding='utf-8')

        (ref_dir / "_bulk_babylon.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: en
priority: 1
category: babylon_reference
entries_count: 1
compiled_from: test
last_compiled: "2026-01-01"
---

| source | target | pinyin |
| --- | --- | --- |
| 修为 | cultivation | xiu1 wei2 |
""", encoding='utf-8')

        (norm_dir / "mark_normalization.md").write_text("""---
type: normalization_rules
rule_type: punctuation_map
rules_count: 1
compiled_from: "Mark.txt"
last_compiled: "2026-01-01"
---

| source | target | rule_type |
| --- | --- | --- |
| ， | , | punctuation_map |
""", encoding='utf-8')

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()

        assert stats["entries_unique"] == 1
        assert stats["reference_entries"] == 1
        assert stats["normalization_rules"] == 1

        conn = sqlite3.connect(str(compiled_dir / "trie_cache.db"))
        c = conn.cursor()

        c.execute("SELECT target FROM entries WHERE source = '修为'")
        runtime_row = c.fetchone()
        assert runtime_row[0] == "tu vi"

        c.execute("SELECT target, target_language, metadata_json FROM reference_entries WHERE source = '修为'")
        reference_row = c.fetchone()
        assert reference_row[0] == "cultivation"
        assert reference_row[1] == "en"
        assert json.loads(reference_row[2])["pinyin"] == "xiu1 wei2"

        c.execute("SELECT source_text, target_text, rule_type FROM normalization_rules WHERE source_text = '，'")
        norm_row = c.fetchone()

        c.execute("SELECT source, pinyin, han_viet_readings, entry_role FROM entry_readings WHERE source = '修为' ORDER BY id")
        reading_rows = c.fetchall()
        conn.close()

        assert norm_row[0] == "，"
        assert norm_row[1] == ","
        assert norm_row[2] == "punctuation_map"
        assert ("修为", "xiu1 wei2", "", "reference") in reading_rows

    def test_audit_events_are_compiled(self, tmp_path):
        audit_dir = tmp_path / "global" / "audit"
        audit_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"

        (audit_dir / "vietphrase_history.md").write_text("""---
type: audit_events
source_dict: "vietphrase"
events_count: 1
compiled_from: "VietPhraseHistory.txt"
last_compiled: "2026-01-01"
---

| entry | action | user_name | updated_at | source_dict |
| --- | --- | --- | --- | --- |
| 修为 | Updated | Polaris1844 | 2021-04-06T00:07:35 | vietphrase |
""", encoding='utf-8')

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()

        assert stats["audit_events"] == 1

        conn = sqlite3.connect(str(compiled_dir / "trie_cache.db"))
        c = conn.cursor()
        c.execute("SELECT entry, action, user_name, source_dict FROM audit_events")
        row = c.fetchone()
        conn.close()

        assert row == ("修为", "Updated", "Polaris1844", "vietphrase")

    def test_trie_loads_entry_reading_fallbacks(self, tmp_path):
        ref_dir = tmp_path / "global" / "reference_vi"
        ref_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"

        (ref_dir / "_bulk_ref.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 1
category: thieuchuu_reference
entry_role: reference
entries_count: 1
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target | han_viet_readings |
| --- | --- | --- |
| 㚻 | kê | kê |
""", encoding='utf-8')

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        compiler.compile()

        trie = TrieEngine(enable_number_converter=False)
        trie.load_from_sqlite(str(compiled_dir / "trie_cache.db"))

        exact = trie.lookup_exact("㚻")
        assert exact is not None
        assert exact.target == "kê"
        assert trie.lookup_reading("㚻") == "kê"
        assert trie.translate_text("㚻") == "kê"

    def test_entry_readings_keep_phienam_even_when_runtime_is_overridden(self, tmp_path):
        phienam_dir = tmp_path / "global" / "phien_am"
        phienam_dir.mkdir(parents=True)
        vp_dir = tmp_path / "global" / "vietphrase"
        vp_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"

        (phienam_dir / "_bulk_phienam.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 1
category: phien_am
entries_count: 1
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 阿 | a |
""", encoding='utf-8')

        (vp_dir / "_bulk_vp.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: vietphrase
entries_count: 1
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 阿 | a-prefix |
""", encoding='utf-8')

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()
        assert stats["entry_readings"] == 1

        conn = sqlite3.connect(str(compiled_dir / "trie_cache.db"))
        c = conn.cursor()
        c.execute("SELECT target FROM entries WHERE source = '阿'")
        runtime_target = c.fetchone()[0]
        c.execute("SELECT han_viet_readings, category FROM entry_readings WHERE source = '阿'")
        reading_row = c.fetchone()
        conn.close()

        assert runtime_target == "a-prefix"
        assert reading_row == ("a", "phien_am")

    def test_phienam_runtime_pruned_when_reference_covers_source(self, tmp_path):
        phienam_dir = tmp_path / "global" / "phien_am"
        phienam_dir.mkdir(parents=True)
        ref_dir = tmp_path / "global" / "reference_vi"
        ref_dir.mkdir(parents=True)
        compiled_dir = tmp_path / "_compiled"

        (phienam_dir / "_bulk_phienam.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 1
category: phien_am
entries_count: 1
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target |
| --- | --- |
| 㚻 | kê |
""", encoding='utf-8')

        (ref_dir / "_bulk_ref.md").write_text("""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 1
category: thieuchuu_reference
entry_role: reference
entries_count: 1
compiled_from: "test"
last_compiled: "2026-01-01"
---

| source | target | han_viet_readings |
| --- | --- | --- |
| 㚻 | kê | kê |
""", encoding='utf-8')

        compiler = DictionaryCompiler(str(tmp_path), str(compiled_dir))
        stats = compiler.compile()

        assert stats["phienam_runtime_before_reduction"] == 1
        assert stats["phienam_runtime_after_reduction"] == 0
        assert stats["phienam_runtime_pruned"] == 1

        trie = TrieEngine(enable_number_converter=False)
        trie.load_from_sqlite(str(compiled_dir / "trie_cache.db"))

        result = trie.lookup_exact("㚻")
        assert result is not None
        assert result.target == "kê"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
