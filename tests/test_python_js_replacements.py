#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.learning.rule_induction_engine import RuleInductionEngine
from src.learning.sliding_context_manager import ContextManager
from src.learning.translation_memory import TranslationMemory
from src.parser.dependency_parser import DependencyParser
from src.parser.morphological_analyzer import MorphologicalAnalyzer
from src.rules.syntax_transfer_rules import SyntaxTransferRules


def test_python_parser_and_syntax_transfer_replaces_legacy_js():
    morphology = MorphologicalAnalyzer().analyze("他不说话。")
    assert morphology["tokens"]
    assert len(morphology["tokens"]) == len(morphology["posTags"])

    parsed = DependencyParser().parse(morphology)
    assert parsed["root"] is not None
    assert parsed["dependencies"]

    transferred = SyntaxTransferRules().apply(parsed)
    assert "syntax_rules_applied" in transferred


def test_python_learning_compatibility_replaces_legacy_js():
    memory = TranslationMemory()
    memory.store("原文", "bản dịch")
    assert memory.retrieve("原文") == "bản dịch"
    assert memory.find_similar("原文")

    induction = RuleInductionEngine()
    rules = induction.induce_from_edit("原文", "dịch máy", "bản dịch đã sửa")
    assert rules
    assert induction.get_learned_rule_count() == len(rules)

    context = ContextManager(window_size=2)
    context.add_sentence("A", {"entities": ["林动"], "topic": "intro"})
    context.add_sentence("B", {"characters": ["林动"]})
    snapshot = context.get_sentence_context()
    assert snapshot["entityTracking"]["林动"] == 1
