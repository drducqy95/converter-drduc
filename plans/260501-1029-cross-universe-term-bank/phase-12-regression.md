# Phase 12: Regression Gate, CI, Performance

Status: ⬜ Pending
Priority: P0
Duration: 1 tuần
Dependencies: All functional phases

## Objective
Khóa regression gate, CI pipeline, performance benchmark. Failing metric blocks promotion (A13).

---

## Tasks

### P12-T1 — RegressionThresholds
```python
@dataclass
class RegressionThresholds:
    # Segment & Noise
    segment_macro_f1: float = 0.93
    noise_drop_precision: float = 0.95
    noise_false_drop_rate: float = 0.02

    # Grammar
    grammar_p0_pass_rate: float = 0.92

    # Entity
    entity_span_f1: float = 0.88
    entity_canonical_accuracy: float = 0.90
    transliteration_top1: float = 0.95
    alias_chain_accuracy: float = 0.88

    # Universe
    universe_detection_accuracy: float = 0.90

    # Context & Pronoun
    pronoun_consistency: float = 0.85
    zero_pronoun_false_insert: float = 0.08  # max allowed

    # Hard constraints (zero tolerance)
    residual_hanzi: int = 0               # except protected intentional
    tm_machine_into_approved: int = 0     # A5 violation count
```

### P12-T2 — run_regression_gate.py
File: `scripts/run_regression_gate.py`

```python
"""
Usage: python scripts/run_regression_gate.py [--corpus data/tests_gold/] [--strict]

Steps:
1. Load gold test data from data/tests_gold/
2. Run each test suite:
   - segments_gold.jsonl → segment classifier metrics
   - grammar_patterns_gold.yaml → grammar P0 pass rate
   - entity_gold.jsonl → entity span F1, canonical accuracy
   - coref_miniset.jsonl → pronoun consistency
   - noise_gold.jsonl → noise precision, false drop rate
3. Compare against RegressionThresholds
4. Output JSON report + exit code (0=pass, 1=fail)
5. If --strict: any single metric fail → exit 1
"""

def main():
    thresholds = RegressionThresholds()
    results = {}

    # Segment classifier
    results["segment_macro_f1"] = eval_segment_classifier("data/tests_gold/segments_gold.jsonl")

    # Grammar P0
    results["grammar_p0_pass_rate"] = eval_grammar_p0("data/tests_gold/grammar_patterns_gold.yaml")

    # Entity
    results["entity_span_f1"] = eval_entity_span("data/tests_gold/entity_gold.jsonl")
    results["entity_canonical_accuracy"] = eval_entity_canonical("data/tests_gold/entity_gold.jsonl")

    # Noise
    results["noise_drop_precision"], results["noise_false_drop_rate"] = eval_noise("data/tests_gold/noise_gold.jsonl")

    # Hard constraints
    results["residual_hanzi"] = count_residual_hanzi()
    results["tm_machine_into_approved"] = count_tm_violations()

    # Compare & report
    report = compare_thresholds(results, thresholds)
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["passed"] else 1)
```

### P12-T3 — benchmark_chapter.py
File: `scripts/benchmark_chapter.py`

```python
"""
Usage: python scripts/benchmark_chapter.py --input chapter.txt [--iterations 10]

Measures:
- Total translation time (ms)
- Per-segment avg time (ms)
- Memory peak (MB)
- Entity scan time (ms)
- Grammar transfer time (ms)
- TermBank lookup count
- Cache hit rate
"""

@dataclass
class BenchmarkResult:
    chapter_file: str
    total_time_ms: float
    segment_count: int
    avg_segment_time_ms: float
    peak_memory_mb: float
    entity_scan_time_ms: float
    grammar_transfer_time_ms: float
    term_bank_lookups: int
    cache_hit_rate: float
    timestamp: str
```

Performance targets:
```
- Average chapter (3000 chars): < 2000ms
- Per-segment: < 50ms average
- Memory peak: < 200MB
- Cache hit rate: > 80%
```

### P12-T4 — Gold test data structure
```
data/tests_gold/
├── segments_gold.jsonl           # 100+ labeled segments
├── grammar_patterns_gold.yaml    # 50+ grammar pattern test cases
├── entity_gold.jsonl             # 200+ entity test cases
├── coref_miniset.jsonl           # 30+ coreference test cases
├── noise_gold.jsonl              # 50+ noise keep/drop test cases
└── full_chapter_regression/
    ├── xianxia_sample.txt        # Source
    ├── xianxia_expected.txt      # Expected output
    ├── scifi_sample.txt
    ├── scifi_expected.txt
    ├── dialogue_sample.txt
    └── dialogue_expected.txt
```

### P12-T5 — GitHub Actions CI
File: `.github/workflows/regression.yml`

```yaml
name: converter-drduc-regression

on:
  push:
    branches: [main, develop, 'v24-*']
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .

      - name: Run unit tests
        run: python -m pytest --tb=short -q

      - name: Run regression gate
        run: python scripts/run_regression_gate.py --strict

      - name: Run benchmark (smoke)
        run: |
          python scripts/benchmark_chapter.py \
            --input data/tests_gold/full_chapter_regression/xianxia_sample.txt \
            --iterations 1

      - name: Upload regression report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: regression-report-${{ matrix.python-version }}
          path: reports/regression_*.json
```

### P12-T6 — RegressionRunner module
File: `src/learning/regression_runner.py`

```python
class RegressionRunner:
    """Runs regression suite programmatically for PromotionGate."""

    def run_with_candidate(self, candidate: RuleCandidate) -> bool:
        """
        1. Temporarily apply candidate to engine
        2. Run full regression suite
        3. Compare against thresholds
        4. Revert candidate
        5. Return True if ALL metrics pass
        """

    def run_full_suite(self) -> RegressionReport:
        """Run complete regression without any candidate applied."""
```

## Files to Create/Modify
- `scripts/run_regression_gate.py` — [NEW]
- `scripts/benchmark_chapter.py` — [NEW]
- `.github/workflows/regression.yml` — [NEW]
- `src/learning/regression_runner.py` — [NEW] (or [MODIFY] if skeleton exists)
- `data/tests_gold/segments_gold.jsonl` — [NEW] Gold data
- `data/tests_gold/grammar_patterns_gold.yaml` — [NEW]
- `data/tests_gold/entity_gold.jsonl` — [NEW]
- `data/tests_gold/coref_miniset.jsonl` — [NEW]
- `data/tests_gold/noise_gold.jsonl` — [NEW]
- `data/tests_gold/full_chapter_regression/` — [NEW] 6 test files

## Definition of Done
```
[ ] run_regression_gate.py runs all metric evaluations
[ ] All 13 metric thresholds defined
[ ] Exit code 1 when any metric fails (--strict)
[ ] benchmark_chapter.py measures 7 performance metrics
[ ] Performance targets documented
[ ] GitHub Actions CI runs tests + regression on push/PR
[ ] CI uploads regression report artifact
[ ] RegressionRunner can test candidates before promotion
[ ] Gold test data files created (seed data)
[ ] Failing metric blocks promotion (A13)
```

---
Next Phase: Phase 13 — E2E Release
