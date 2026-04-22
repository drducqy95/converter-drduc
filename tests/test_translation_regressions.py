#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for translation workflow issues found in manual chapter runs."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.core.trie_engine import TrieEngine
from src.eapee.emotion_detector import EmotionDetector
from src.engine.rbmt_translator import RBMTTranslator
from src.engine.sentence_segmenter import SentenceSegmenter
from src.pipeline.chapter_splitter import ChapterSplitter
from src.pipeline.config_generator import ConfigGenerator
from src.pipeline.entity_scanner import EntityScanner, EntitySuggestion
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline
from src.qa.emotion_consistency_checker import EmotionConsistencyChecker
from src.qa.length_checker import LengthChecker
from src.qa.pronoun_checker import PronounChecker
from src.qa.terminology_checker import TerminologyChecker


def test_trie_skips_reference_gloss_runtime_rows():
    trie = TrieEngine(enable_number_converter=False)
    trie.load_from_sqlite(Path("data/dictionaries/_compiled/trie_cache.db"))

    chapter_term = trie.lookup_exact("\u7ae0")
    assert chapter_term is not None
    assert chapter_term.target == "ch\u01b0\u01a1ng"
    assert "U+" not in chapter_term.target


def test_runtime_accessor_hides_reference_gloss_runtime_rows():
    accessor = RuntimeDictionaryAccessor()
    try:
        assert accessor.lookup_runtime("\u7ae0") is None
        assert accessor.lookup_runtime("\u8fea") is None
        assert accessor.lookup_runtime("\u4e4b\u6240\u4ee5") is not None
    finally:
        accessor.close()


def test_shared_trie_and_pinyin_caches_reuse_loaded_resources():
    db_path = Path("data/dictionaries/_compiled/trie_cache.db")
    trie_a = TrieEngine.from_shared_sqlite(db_path, enable_number_converter=False)
    trie_b = TrieEngine.from_shared_sqlite(db_path, enable_number_converter=False)
    assert trie_a is trie_b

    accessor_a = RuntimeDictionaryAccessor(db_path)
    accessor_b = RuntimeDictionaryAccessor(db_path)
    try:
        assert accessor_a.build_pinyin_index() is accessor_b.build_pinyin_index()
    finally:
        accessor_a.close()
        accessor_b.close()


def test_trie_loads_concise_reference_fallback_for_brands():
    trie = TrieEngine(enable_number_converter=False)
    trie.load_from_sqlite(Path("data/dictionaries/_compiled/trie_cache.db"))

    brand = trie.lookup_exact("\u5965\u8fea")
    assert brand is not None
    assert brand.target == "Audi"


def test_entity_scanner_heuristic_detects_name_without_function_word_noise():
    scanner = EntityScanner()
    text = "\u4e0d\u8fc7\u590f\u5929\u9a90\u90fd\u6ca1\u6709\u7f13\u8fc7\u795e\u6765\u3002\u590f\u5929\u9a90\u8bf4\u9053\uff1a\u201c\u4f60\u597d\u3002\u201d"
    entities = scanner.scan(text)
    sources = {entity.source for entity in entities}

    assert "\u590f\u5929\u9a90" in sources
    assert "\u4e0d\u8fc7" not in sources
    assert "\u5929\u9a90\u90fd" not in sources


def test_entity_scanner_rejects_partial_and_embedded_name_false_positives():
    scanner = EntityScanner()
    text = (
        "\u9752\u5e74\u53eb\u505a\u5f20\u5c0f\u987a\u3002\u590f\u5929\u9a90\u90fd\u6ca1\u6709\u4ece\u4e4b\u524d\u7684\u60ca\u559c\u4e2d\u7f13\u8fc7\u795e\u6765\u3002"
        "\u590f\u5929\u9a90\u8bf4\u9053\uff1a\u201c\u4f60\u597d\u3002\u201d"
        "\u8fd8\u7ed9\u914d\u4e00\u53f0\u5965\u8feaA6\uff0c\u811a\u6b65\u58f0\u54cd\u4e86\u8d77\u6765\u3002"
    )
    entities = scanner.scan(text)
    heuristic_sources = {entity.source for entity in entities if entity.source_dict == "heuristic_name_mining"}

    assert "\u590f\u5929\u9a90" in heuristic_sources
    assert "\u5f20\u5c0f\u987a" in heuristic_sources
    assert "\u5f20\u5c0f" not in heuristic_sources
    assert "\u90fd\u6ca1" not in heuristic_sources
    assert "\u4ece\u4e4b" not in heuristic_sources
    assert "\u53f0\u5965" not in heuristic_sources
    assert "\u6b65\u58f0" not in heuristic_sources


def test_entity_scanner_rejects_shifted_preposition_and_demonstrative_prefixes():
    scanner = EntityScanner()
    text = (
        "\u8fd9\u4e00\u665a\u5bf9\u4e8e\u590f\u5929\u9a90\u6765\u8bf4\u683c\u5916\u96be\u71ac\uff0c\u5bf9\u4e8e\u590f\u5929\u9a90\u6765\u8bf4\u7b80\u76f4\u50cf\u5669\u68a6\u3002"
        "\u90a3\u7ea2\u8863\u9b3c\u5df2\u7ecf\u8ffd\u4e86\u4e0a\u6765\uff0c\u90a3\u7ea2\u8863\u9b3c\u53c8\u53d1\u51fa\u4e86\u5c16\u53eb\u3002"
        "\u590f\u5929\u9a90\u8bf4\u9053\uff1a\u201c\u5feb\u8dd1\uff01\u201d\u590f\u5929\u9a90\u8f6c\u8eab\u5c31\u8dd1\u3002"
    )
    entities = scanner.scan(text)
    sources = {entity.source for entity in entities}
    heuristic_sources = {entity.source for entity in entities if entity.source_dict == "heuristic_name_mining"}

    assert "\u590f\u5929\u9a90" in sources
    assert "\u590f\u5929\u9a90" in heuristic_sources
    assert "\u4e8e\u590f\u5929" not in heuristic_sources
    assert "\u90a3\u7ea2\u8863" not in heuristic_sources


def test_config_generator_does_not_lock_singleton_heuristic_entities():
    config = ConfigGenerator().generate(
        text="\u590f\u5929\u9a90\u8bf4\u9053\uff1a\u201c\u4f60\u597d\u3002\u201d \u4e0d\u8fc7\u4ed6\u6ca1\u6709\u56de\u7b54\u3002",
        entities=[
            EntitySuggestion(
                source="\u590f\u5929\u9a90",
                target="\u590f\u5929\u9a90",
                entity_type="person",
                confidence=0.72,
                source_dict="heuristic_name_mining",
                ambiguity_flag=False,
                count=2,
                positions=[2, 11],
            ),
            EntitySuggestion(
                source="\u4e0d\u8fc7",
                target="\u4e0d\u8fc7",
                entity_type="person",
                confidence=0.72,
                source_dict="heuristic_name_mining",
                ambiguity_flag=False,
                count=1,
                positions=[16],
            ),
        ],
        relationships=[],
        terminology=[],
    )

    locked_sources = {item["source"] for item in config["locked_entities"]}
    assert "\u590f\u5929\u9a90" in locked_sources
    assert "\u4e0d\u8fc7" not in locked_sources


def test_config_generator_transliterates_person_locked_entities():
    config = ConfigGenerator().generate(
        text="\u590f\u5929\u9a90\u548c\u5f20\u5c0f\u987a\u8d70\u8fdb\u516c\u53f8\u3002",
        entities=[
            EntitySuggestion(
                source="\u590f\u5929\u9a90",
                target="\u590f\u5929\u9a90",
                entity_type="person",
                confidence=0.72,
                source_dict="heuristic_name_mining",
                ambiguity_flag=False,
                count=2,
                positions=[0, 6],
            ),
            EntitySuggestion(
                source="\u5f20\u5c0f\u987a",
                target="\u5f20\u5c0f\u987a",
                entity_type="person",
                confidence=0.72,
                source_dict="heuristic_name_mining",
                ambiguity_flag=False,
                count=2,
                positions=[4, 10],
            ),
        ],
        relationships=[],
        terminology=[],
    )

    locked_targets = {item["source"]: item["target"] for item in config["locked_entities"]}
    assert locked_targets["\u590f\u5929\u9a90"] == "H\u1ea1 Thi\u00ean K\u1ef3"
    assert locked_targets["\u5f20\u5c0f\u987a"] == "Tr\u01b0\u01a1ng Ti\u1ec3u Thu\u1eadn"


def test_luat_nhan_keeps_locked_entity_whole_for_late_override():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            "\u8fd9\u811a\u6b65\u58f0\u76f4\u63a5\u5c06\u590f\u5929\u9a90\u5413\u5f97\u4e00\u6fc0\u7075\u3002",
            config={
                "locked_entities": [
                    {
                        "source": "\u590f\u5929\u9a90",
                        "target": "H\u1ea1 Thi\u00ean K\u1ef3",
                        "entity_type": "person",
                    }
                ]
            },
        )
    finally:
        translator.close()

    assert "H\u1ea1 Thi\u00ean K\u1ef3" in result.clean_text
    assert "H \u1ea1 T h i \u00ea n K \u1ef3" not in result.clean_text
    assert "\u5f97" not in result.clean_text


def test_trie_match_does_not_consume_prefix_of_locked_entity():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            "\u4e0d\u8fc7\u590f\u5929\u9a90\u5176\u5b9e\u5012\u86ee\u60f3\u95ee\u4ed6\u4e00\u53e5\u3002",
            config={
                "locked_entities": [
                    {
                        "source": "\u590f\u5929\u9a90",
                        "target": "H\u1ea1 Thi\u00ean K\u1ef3",
                        "entity_type": "person",
                    }
                ]
            },
        )
    finally:
        translator.close()

    assert "H\u1ea1 Thi\u00ean K\u1ef3" in result.clean_text
    assert "m\u1eb7t tr\u1eddi k\u1ef3" not in result.clean_text


def test_chapter_splitter_handles_markdown_prefixed_heading():
    splitter = ChapterSplitter()
    chapters = splitter.split("# 1.\u7b2c1\u7ae0 C\u00f4ng vi\u1ec7c \u0111\u1ea7u ti\u00ean\n\n\u590f\u5929\u9a90\u5750\u8fdb\u8f66\u91cc\u3002")

    assert len(chapters) == 1
    assert chapters[0].chapter_id == "chapter-001"
    assert chapters[0].title == "# 1.\u7b2c1\u7ae0 C\u00f4ng vi\u1ec7c \u0111\u1ea7u ti\u00ean"


def test_sentence_segmenter_splits_heading_and_dialogue_paragraphs():
    segmenter = SentenceSegmenter()
    spans = segmenter.split(
        "# 1.\u7b2c1\u7ae0 \u7b2c\u4e00\u4efd\u5de5\u4f5c\n\n"
        "\u201c\u8bd5\u7528\u671f\u6708\u85aa2\u4e07\uff0c\u8fd8\u7ed9\u914d\u4e00\u53f0\u5965\u8feaA6\u2026\u2026\u201d\n\n"
        "\u76f4\u5230\u5750\u8fdb\u8f66\u91cc\uff0c\u590f\u5929\u9a90\u90fd\u6ca1\u6709\u4ece\u4e4b\u524d\u7684\u60ca\u559c\u4e2d\u7f13\u8fc7\u795e\u6765\u3002"
    )

    assert [span.text for span in spans] == [
        "# 1.\u7b2c1\u7ae0 \u7b2c\u4e00\u4efd\u5de5\u4f5c",
        "\u201c\u8bd5\u7528\u671f\u6708\u85aa2\u4e07\uff0c\u8fd8\u7ed9\u914d\u4e00\u53f0\u5965\u8feaA6\u2026\u2026\u201d",
        "\u76f4\u5230\u5750\u8fdb\u8f66\u91cc\uff0c\u590f\u5929\u9a90\u90fd\u6ca1\u6709\u4ece\u4e4b\u524d\u7684\u60ca\u559c\u4e2d\u7f13\u8fc7\u795e\u6765\u3002",
    ]


def test_rbmt_translator_formats_markdown_heading_naturally():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text("# 1.\u7b2c1\u7ae0 \u7b2c\u4e00\u4efd\u5de5\u4f5c")
    finally:
        translator.close()

    assert result.clean_text == "# Ch\u01b0\u01a1ng 1: C\u00f4ng vi\u1ec7c \u0111\u1ea7u ti\u00ean"


def test_rbmt_translator_normalizes_spaces_around_converted_punctuation():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text("\u201c\u5965\u8feaA6\u2026\u2026\u201d")
    finally:
        translator.close()

    assert result.clean_text == "\"Audi A6...\""


def test_rbmt_translator_uses_phrase_and_runtime_regression_overrides():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            "\u4e2d\u5e74\u5927\u53d4\u8bf4\u9053\uff1a\u201c\u8ba9\u6211\u505a\u56fe\u4e66\u7ba1\u7406\u5458\uff1f\u54e6\u4e0d\uff0c\u8fd9\u5e94\u8be5\u53eb\u505a\u6253\u66f4\u7684\u3002\u201d"
            "\u8fd9\u662f\u5bb6\u4ec0\u4e48\u516c\u53f8\uff1f\u8fd9\u5bb6\u516c\u53f8\u6708\u85aa2\u4e07\u3002"
        )
    finally:
        translator.close()

    lowered = result.clean_text.lower()
    assert "\u00f4ng ch\u00fa trung ni\u00ean" in lowered
    assert "nh\u00e2n vi\u00ean th\u1ee7 th\u01b0" in lowered
    assert "ng\u01b0\u1eddi canh \u0111\u00eam" in lowered
    assert "c\u00f4ng ty g\u00ec" in lowered
    assert "c\u00f4ng ty n\u00e0y" in lowered
    assert "l\u01b0\u01a1ng th\u00e1ng" in lowered
    assert "d\u1ee5ng c\u1ee5" not in lowered


def test_rbmt_translator_prefers_modern_pronouns_for_modern_genre():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            "\u4ed6\u4eec\u8bf4\u4f60\u8fd8\u6ca1\u6709\u8ddf\u6211\u8bf4\u3002",
            config={"genre_hints": ["modern"]},
        )
    finally:
        translator.close()

    lowered = result.clean_text.lower()
    assert "h\u1ecd" in lowered
    assert "c\u1eadu" in lowered
    assert "t\u00f4i" in lowered
    assert "h\u1eafn" not in lowered
    assert "ng\u01b0\u01a1i" not in lowered
    assert "ta" not in lowered


def test_rbmt_translator_style_profile_controls_sentence_naturalization():
    source = "\u201c\u65e2\u7136\u5df2\u7ecf\u7b7e\u8ba2\u4e86\u5de5\u4f5c\u5408\u540c\uff0c\u90a3\u73b0\u5728\u5c31\u53bb\u5c65\u884c\u4f60\u7684\u804c\u8d23\u5427\u3002\u201d"
    translator = RBMTTranslator()
    try:
        faithful = translator.translate_text(
            source,
            config={
                "genre_hints": ["modern"],
                "style_profile": "source_faithful",
            },
        )
        adaptive = translator.translate_text(
            source,
            config={
                "genre_hints": ["modern"],
                "style_profile": "modern_novel_adaptive",
            },
        )
    finally:
        translator.close()

    assert "Như là đã ký kết làm việc hợp đồng" in faithful.clean_text
    assert "Đã ký hợp đồng lao động rồi" in adaptive.clean_text


def test_emotion_detector_does_not_treat_xihao_as_joy():
    detector = EmotionDetector()
    assert detector.detect_label("喜好杀人的恶鬼！") != "joy"


def test_emotion_checker_skips_dialogue_to_narration_transition():
    checker = EmotionConsistencyChecker()
    translation_result = SimpleNamespace(
        segments=[
            SimpleNamespace(
                sentence_id="seg-0001",
                source_text="“喜好杀人的恶鬼！”",
                clean_text="\"Ác quỷ thích giết người!\"",
                emotion="joy",
            ),
            SimpleNamespace(
                sentence_id="seg-0002",
                source_text="夏天骐这句话几乎是吼出来的，事实上说的越多他心里面便越害怕。",
                clean_text="Hạ Thiên Kì gần như hét lên, thực ra càng nói anh càng sợ.",
                emotion="anger",
            ),
        ]
    )
    assert checker.run(translation_result) == []


def test_rbmt_translator_suspense_profile_rewrites_common_horror_calques():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            "说话娘娘腔的男人叫做冯伟。然而除却这些意外，他则在没有获得半分有价值的信息。",
            config={
                "genre_hints": ["modern", "horror", "suspense"],
            },
        )
    finally:
        translator.close()

    lowered = result.clean_text.lower()
    assert "ẻo lả" in lowered
    assert "nương nương khang" not in lowered
    assert "nửa phần tin tức có giá trị" in lowered


def test_rbmt_translator_compacts_long_narrative_sentence_below_length_threshold():
    source = "这么做倒不是因为他为人有多善良，多正直，只是单纯的觉得这种事情由四个人承担，无论怎样都是要强过他独自承担的。"
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            source,
            config={
                "genre_hints": ["modern"],
                "style_profile": "modern_novel_adaptive",
                "naturalization": {"enabled": True, "compact_sentences": True},
            },
        )
    finally:
        translator.close()

    issues = LengthChecker().run(result)
    assert issues == []


def test_rbmt_translator_shortens_killer_deduction_sentence_without_length_issue():
    source = "杀人狂的样子他并没有见到，换言之，杀人狂可以是除自己以外的任何人，所以自然也包括张小顺！"
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            source,
            config={"genre_hints": ["modern", "horror", "suspense"]},
        )
    finally:
        translator.close()

    lowered = result.clean_text.lower()
    assert "bộ dạng tên sát nhân" in lowered
    assert "bất kỳ ai ngoài chính anh" in lowered
    assert "trương tiểu thuận cũng không ngoại lệ" in lowered
    assert LengthChecker().run(result) == []


def test_rbmt_translator_shortens_escape_plan_sentence_without_length_issue():
    source = "所以只能先逃出书店，看看是再回黄金写字楼想办法，还是怎么着，总之是不能继续像现在这样坐以待毙。"
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            source,
            config={
                "genre_hints": ["modern", "horror", "suspense"],
                "naturalization": {"enabled": True, "compact_sentences": True},
            },
        )
    finally:
        translator.close()

    lowered = result.clean_text.lower()
    assert "quay về tòa cao ốc văn phòng hoàng kim để nghĩ cách" in lowered
    assert "ngồi chờ chết như bây giờ" in lowered
    assert LengthChecker().run(result) == []


def test_rbmt_translator_shortens_stair_fall_sentence_without_length_issue():
    source = "感觉冰冷的手爪正距离自己的后背越来越近，夏天骐的恐惧彻底从心底爆发出来，这也令他双腿一软，直接从楼梯上滚了下去。"
    translator = RBMTTranslator()
    try:
        result = translator.translate_text(
            source,
            config={"genre_hints": ["modern", "horror", "suspense"]},
        )
    finally:
        translator.close()

    lowered = result.clean_text.lower()
    assert "móng vuốt lạnh băng sau lưng" in lowered
    assert "bùng lên từ đáy lòng" in lowered
    assert "ngã lăn xuống cầu thang" in lowered
    assert LengthChecker().run(result) == []


def test_pronoun_checker_accepts_phrase_trace_with_embedded_first_person():
    translator = RBMTTranslator()
    try:
        result = translator.translate_text("\u201c\u8ba9\u6211\u505a\u56fe\u4e66\u7ba1\u7406\u5458\uff1f\u201d")
    finally:
        translator.close()

    issues = PronounChecker().run(result)
    assert issues == []


def test_terminology_checker_ignores_case_only_difference_for_locked_entities():
    result = SimpleNamespace(
        segments=[
            SimpleNamespace(
                sentence_id="seg-0001",
                source_text="\u5148\u53bb\u5e73\u5b89\u885734\u53f7\u3002",
                clean_text="Tr\u01b0\u1edbc ti\u00ean \u0111\u1ebfn s\u1ed1 34 ph\u1ed1 B\u00ecnh An.",
            )
        ]
    )

    issues = TerminologyChecker().run(
        result,
        {
            "locked_entities": [
                {
                    "source": "\u5e73\u5b89\u8857",
                    "target": "Ph\u1ed1 B\u00ecnh An",
                    "entity_type": "location",
                }
            ]
        },
    )
    assert issues == []


def test_terminology_checker_ignores_shorter_partial_entity_when_longer_term_matches():
    result = SimpleNamespace(
        segments=[
            SimpleNamespace(
                sentence_id="seg-0001",
                source_text="后天早上八点，你要准时去齐河女子学院报道。",
                clean_text="Sáng ngày mốt tám giờ, cậu phải đến Học viện nữ sinh Tề Hà để báo danh.",
            )
        ]
    )

    issues = TerminologyChecker().run(
        result,
        {
            "locked_entities": [
                {"source": "齐河女子学院", "target": "Học viện nữ sinh Tề Hà", "entity_type": "organization"},
                {"source": "齐河女", "target": "Tề Hà Nữ", "entity_type": "person"},
            ]
        },
    )
    assert issues == []


def test_rbmt_translator_skips_tm_lookup_by_default(tmp_path):
    translator = RBMTTranslator(tm_db_path=tmp_path / "tm.sqlite")
    try:
        translator.tm.store("\u5f20\u5c0f\u987a\u8bf4\u9053\u3002", "TM c\u0169", confidence=0.99, source="test")
        result = translator.translate_text(
            "\u5f20\u5c0f\u987a\u8bf4\u9053\u3002",
            config={
                "locked_entities": [
                    {
                        "source": "\u5f20\u5c0f\u987a",
                        "target": "Tr\u01b0\u01a1ng Ti\u1ec3u Thu\u1eadn",
                        "entity_type": "person",
                    }
                ]
            },
        )
    finally:
        translator.close()

    assert "TM c\u0169" not in result.clean_text
    assert "Tr\u01b0\u01a1ng Ti\u1ec3u Thu\u1eadn" in result.clean_text


def test_length_checker_allows_short_segments_to_expand_more_in_vietnamese():
    result = SimpleNamespace(
        segments=[
            SimpleNamespace(
                sentence_id="seg-0001",
                source_text="\u201c\u4f60\u662f\u8c01\uff1f\u201d",
                clean_text="\" Ng\u01b0\u01a1i l\u00e0 ai ?\"",
            )
        ]
    )

    assert LengthChecker().run(result) == []


def test_pretranslation_pipeline_merges_external_glossary_and_character_metadata(tmp_path):
    project_root = tmp_path / "external-project"
    source_dir = project_root / "source"
    source_dir.mkdir(parents=True)
    source_path = source_dir / "chapter_001.md"
    source_path.write_text(
        "\u5f90\u5929\u534e\u5e26\u7740\u590f\u5929\u9a90\u53bb\u946b\u534e\u5927\u4e66\u5e97\u3002",
        encoding="utf-8",
    )
    (project_root / "glossary.json").write_text(
        '{'
        '"entries": ['
        '{"source": "\\u946b\\u534e\\u5927\\u4e66\\u5e97", "target": "Hi\\u1ec7u s\\u00e1ch l\\u1edbn T\\u00e2n Hoa", "category": "proper_names_cn"}'
        "]"
        "}",
        encoding="utf-8",
    )
    (project_root / "characters.json").write_text(
        '{'
        '"characters": ['
        '{"name_source": "\\u5f90\\u5929\\u534e", "name_target": "T\\u1eeb Thi\\u00ean Hoa"}'
        "]"
        "}",
        encoding="utf-8",
    )

    pipeline = PreTranslationPipeline()
    try:
        result = pipeline.prepare(source_path, tmp_path / "workspace")
    finally:
        pipeline.close()

    locked = {item["source"]: item["target"] for item in result.config["locked_entities"]}
    assert locked["\u946b\u534e\u5927\u4e66\u5e97"] == "Hi\u1ec7u s\u00e1ch l\u1edbn T\u00e2n Hoa"
    assert locked["\u5f90\u5929\u534e"] == "T\u1eeb Thi\u00ean Hoa"
