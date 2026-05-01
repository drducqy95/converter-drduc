# Phase 13: E2E Integration & Release Candidate

Status: ⬜ Pending
Priority: P1
Duration: 1-2 tuần
Dependencies: Phase 12

## Objective
Full E2E integration tests, release documentation, production validation. Target: v24.0 Production Release.

---

## Tasks

### P13-T1 — E2E Test Scenarios
File: `tests/test_e2e/test_cross_universe_translation.py`

| # | Scenario | Focus | Key assertions |
|---|----------|-------|----------------|
| 1 | Single xianxia chapter | tu_tien universe, entity translation | 韩立→Hàn Lập, 灵根→linh căn, no residual Hanzi |
| 2 | Sci-fi / system panel | 系统 brackets, LitRPG panels | 【系统】 kept, 【面板】 kept, ads dropped |
| 3 | Chư Thiên multi-universe | Cross-universe names | Same-name disambiguated, no [universe_tag] in output |
| 4 | Dialogue-heavy chapter | Speaker tracking | Speaker correctly attributed, pronouns consistent |
| 5 | Author-note / noise-heavy | Noise filter | Noise dropped, content kept, false drop ≤ 0.02 |
| 6 | Mixed-script names | Latin + CJK | Klein detected, Sequence 9 kept, M829A3 kept |

**Test structure per scenario:**
```python
class TestXianxiaChapter:
    def test_entity_translation(self):
        """Canon character names translated correctly."""

    def test_no_residual_hanzi(self):
        """No untranslated Chinese except protected spans."""

    def test_grammar_patterns(self):
        """Grammar P0 patterns handled correctly."""

    def test_noise_filtered(self):
        """Author notes and solicitations removed."""

    def test_trace_complete(self):
        """Every segment has trace events."""

    def test_tm_separation(self):
        """Machine output in tm_machine, NOT in tm_approved."""
```

### P13-T2 — Full chapter regression test
File: `tests/test_e2e/test_full_chapter_regression.py`

```python
class TestFullChapterRegression:
    """Run full translation pipeline on gold chapters, compare output."""

    @pytest.mark.parametrize("chapter", [
        "xianxia_sample",
        "scifi_sample",
        "dialogue_sample",
    ])
    def test_chapter_output_matches_expected(self, chapter):
        source = load_gold(f"data/tests_gold/full_chapter_regression/{chapter}.txt")
        expected = load_gold(f"data/tests_gold/full_chapter_regression/{chapter}_expected.txt")
        actual = translator.translate_chapter(source)
        similarity = compute_similarity(actual, expected)
        assert similarity >= 0.90, f"Chapter {chapter} similarity {similarity:.2f} < 0.90"
```

### P13-T3 — Release checks checklist
```python
RELEASE_CHECKS = {
    "no_universe_tag_in_output": "No [universe_tag] appears in any translation output",
    "no_residual_hanzi": "No untranslated Hanzi except protected intentional spans",
    "entity_consistency": "Same entity translated consistently across chapter",
    "tm_approved_clean": "tm_approved contains only human-reviewed entries (A5)",
    "grammar_p0_pass": "All 15 grammar P0 rules pass",
    "noise_false_drop_threshold": "Noise false drop ≤ 0.02",
    "performance_acceptable": "Average chapter < 2000ms",
    "all_tests_green": "pytest + regression gate pass",
    "documentation_complete": "All 7 docs exist",
}
```

### P13-T4 — Documentation files
All in `docs/` directory:

| # | File | Content |
|---|------|---------|
| 1 | `ARCHITECTURE_STATUS.md` | Current module map, dependency graph, tech stack |
| 2 | `CROSS_UNIVERSE_GUIDE.md` | How universe detection works, fingerprints, disambiguation |
| 3 | `GRAMMAR_PATTERN_SCANNER.md` | How to add grammar patterns, scanner usage, report format |
| 4 | `GRAMMAR_TRANSFER_PLANNER.md` | Clause/relation/rule system, priority table, how to add rules |
| 5 | `LEARNING_LOOP.md` | Review diff → candidate miner → promotion gate flow |
| 6 | `REGRESSION_POLICY.md` | Metrics, thresholds, CI pipeline, gold data format |
| 7 | `PROMOTION_POLICY.md` | 5 conditions for promotion, regression gate requirement |

Each doc should include:
- Overview (what it does)
- Architecture diagram (Mermaid)
- Configuration files (paths, format)
- How to extend (add new rules/patterns/universes)
- Troubleshooting (common issues)

### P13-T5 — Version tag & changelog
```
Tag: v24.0-rc1
Branch: converter-drduc-v24-production-hardening
```

**CHANGELOG.md entry:**
```markdown
## v24.0 — Production Release Candidate

### Added
- SegmentPacket + TraceEvent governance (Phase 01)
- Segment typing with 9 types (Phase 02)
- ProtectedSpanRegistry with priority system (Phase 02)
- NoiseFilter with hard whitelist (Phase 02)
- Non-LLM Grammar Pattern Scanner (Phase 03)
- Cross-Universe Term Bank (12 MD → JSONL) (Phase 04)
- TermBankRecord with universe/context/versioning (Phase 05)
- UniverseDetector with fingerprint + co-occurrence (Phase 06)
- Context-aware entity resolution chain (Phase 07)
- Grammar Transfer Planner with 15 P0 rules (Phase 08)
- Entity Enrichment & User Review workflow (Phase 09)
- Context Resolver + Zero-Pronoun + EAPEE integration (Phase 10)
- Metadata DB + Learning Loop with promotion gate (Phase 11)
- Regression gate + CI + performance benchmark (Phase 12)

### Changed
- TM split into machine/reviewed/approved (A5)
- EntityScanner uses TermBank before Trie (A4)
- All decisions have trace (A7)

### Security
- No auto-promotion without human review (A12)
- Regression gate blocks promotion on failure (A13)
```

### P13-T6 — Production validation script
File: `scripts/validate_production_ready.py`

Runs all release checks programmatically:
```python
def validate():
    checks = {}
    checks["tests"] = run_pytest()
    checks["regression"] = run_regression_gate()
    checks["docs"] = verify_docs_exist()
    checks["tm_clean"] = verify_tm_separation()
    checks["no_universe_tag"] = verify_no_universe_tags()

    passed = all(checks.values())
    print_report(checks)
    return passed
```

## Files to Create/Modify
- `tests/test_e2e/__init__.py` — [NEW]
- `tests/test_e2e/test_cross_universe_translation.py` — [NEW]
- `tests/test_e2e/test_full_chapter_regression.py` — [NEW]
- `docs/ARCHITECTURE_STATUS.md` — [NEW] (or update from Phase 00)
- `docs/CROSS_UNIVERSE_GUIDE.md` — [NEW]
- `docs/GRAMMAR_PATTERN_SCANNER.md` — [NEW]
- `docs/GRAMMAR_TRANSFER_PLANNER.md` — [NEW]
- `docs/LEARNING_LOOP.md` — [NEW]
- `docs/REGRESSION_POLICY.md` — [NEW]
- `docs/PROMOTION_POLICY.md` — [NEW]
- `CHANGELOG.md` — [MODIFY] Add v24.0 entry
- `scripts/validate_production_ready.py` — [NEW]

## Definition of Done
```
[ ] All 6 E2E test scenarios implemented and passing
[ ] Full chapter regression tests pass (similarity ≥ 0.90)
[ ] All 9 release checks pass
[ ] All 7 documentation files complete with diagrams
[ ] CHANGELOG.md updated with v24.0 entry
[ ] validate_production_ready.py runs green
[ ] Release version tag v24.0-rc1 applied
[ ] Production v24 DoD checklist ALL GREEN
```

---
🏁 Plan Complete. Target: **v24.0 Production Release Candidate**
