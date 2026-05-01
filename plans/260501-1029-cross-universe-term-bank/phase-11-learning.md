# Phase 11: Metadata DB & Learning Loop

Status: ⬜ Pending
Priority: P0/P1
Duration: 2 tuần
Dependencies: Phase 01 + Phase 08 + Phase 09 + Phase 10

## Objective
Hệ tự học có kiểm duyệt. Human review + regression gate bắt buộc (A12, A13).

---

## Tasks

### P11-T1 — Database tables
File: `src/state/migrations/004_learning_loop.sql`

```sql
-- Human review records
CREATE TABLE human_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text TEXT NOT NULL,
    machine_target TEXT NOT NULL,
    edited_target TEXT,
    diff_json TEXT,                    -- JSON diff between machine and edited
    error_tags TEXT,                   -- comma-separated ErrorTag values
    segment_id TEXT,
    chapter_id TEXT,
    reviewer TEXT DEFAULT 'user',
    created_at TEXT DEFAULT (datetime('now')),
    status TEXT DEFAULT 'pending'      -- pending|reviewed|applied
);

-- Rule candidates mined from human corrections
CREATE TABLE rule_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    proposed_action TEXT NOT NULL,     -- "rewrite", "protect", "skip"
    evidence_count INTEGER DEFAULT 0,
    positive_examples TEXT,            -- JSON array of example pairs
    negative_examples TEXT,            -- JSON array of counter-examples
    precision_estimate REAL DEFAULT 0.0,
    false_positive_rate REAL DEFAULT 1.0,
    mined_from TEXT,                   -- "grammar"|"entity"|"noise"|"tm"
    created_at TEXT DEFAULT (datetime('now')),
    review_status TEXT DEFAULT 'candidate',  -- candidate|approved|rejected|promoted
    status TEXT DEFAULT 'active'
);

-- Noise patterns learned from false drops
CREATE TABLE noise_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    category TEXT NOT NULL,            -- "author_note"|"solicitation"|"forum"|"ad"
    action TEXT DEFAULT 'drop',        -- "drop"|"metadata"|"keep"
    confidence REAL DEFAULT 0.5,
    false_drop_count INTEGER DEFAULT 0,
    total_eval_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    status TEXT DEFAULT 'candidate'    -- candidate|approved|rejected
);

-- Evaluation run history
CREATE TABLE evaluation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    engine_version TEXT NOT NULL,
    corpus_id TEXT NOT NULL,
    metrics_json TEXT NOT NULL,        -- Full RegressionThresholds as JSON
    failed_cases_json TEXT,            -- JSON array of failing test IDs
    passed BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Term bank versioning
CREATE TABLE term_bank_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    universe TEXT NOT NULL,
    file_path TEXT NOT NULL,
    record_count INTEGER,
    checksum TEXT,                     -- SHA256 of file content
    version INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### P11-T2 — ErrorTag enum
File: `src/learning/error_classifier.py`

```python
class ErrorTag(Enum):
    ENTITY_ERROR = "entity_error"           # Wrong entity translation
    ALIAS_ERROR = "alias_error"             # Wrong alias selected
    GRAMMAR_ERROR = "grammar_error"         # Grammar pattern mis-applied
    CONTEXT_ERROR = "context_error"         # Wrong context/universe chosen
    PRONOUN_ERROR = "pronoun_error"         # Wrong pronoun
    NOISE_FALSE_KEEP = "noise_false_keep"   # Should have been dropped
    NOISE_FALSE_DROP = "noise_false_drop"   # Should have been kept
    REGISTER_ERROR = "register_error"       # Wrong register (formal/casual)
    NUMBER_ERROR = "number_error"           # Number conversion wrong
    IDIOM_ERROR = "idiom_error"             # Idiom mistranslated

class ErrorClassifier:
    def classify(self, diff: ReviewDiff) -> list[ErrorTag]:
        """Auto-classify error type from diff analysis."""

    def suggest_fix_type(self, tags: list[ErrorTag]) -> str:
        """Suggest which subsystem needs the fix: grammar|entity|noise|tm."""
```

### P11-T3 — ReviewDiff
File: `src/learning/review_diff.py`

```python
@dataclass
class ReviewDiff:
    source_text: str
    machine_target: str
    edited_target: str
    diff_ops: list[DiffOp]         # list of insert/delete/replace ops
    changed_spans: list[tuple[int, int]]  # positions that changed

class DiffOp:
    op_type: str                   # "insert"|"delete"|"replace"
    position: int
    old_text: str
    new_text: str

def compute_diff(machine: str, edited: str) -> ReviewDiff:
    """Compute structured diff between machine and human-edited text."""
```

### P11-T4 — CandidateMiner
File: `src/learning/candidate_miner.py`

```python
class CandidateMiner:
    """Mine rule/entity/noise/TM candidates from human reviews."""

    def mine_from_reviews(
        self, reviews: list[HumanReview]
    ) -> list[RuleCandidate]:
        """
        Analyze patterns in human corrections:
        1. Group similar corrections
        2. Extract common patterns
        3. Count evidence (frequency of same correction)
        4. Estimate precision from positive/negative examples
        5. Create candidates with status='candidate' (NOT auto-promote)
        """

    def mine_entity_candidates(self, reviews: list[HumanReview]) -> list[dict]:
        """Find consistently corrected entity translations."""

    def mine_noise_candidates(self, reviews: list[HumanReview]) -> list[dict]:
        """Find patterns that were consistently false-dropped or false-kept."""
```

### P11-T5 — PromotionGate
File: `src/learning/promotion_gate.py`

```python
class PromotionGate:
    """Guards against promoting bad candidates (A12, A13)."""

    def can_promote(self, candidate: RuleCandidate) -> tuple[bool, str]:
        """
        Returns (can_promote, reason).
        ALL conditions must be met:
        """
        checks = [
            (candidate.evidence_count >= 3, "need ≥3 evidence"),
            (candidate.precision_estimate >= 0.95, "need precision ≥0.95"),
            (candidate.false_positive_rate <= 0.02, "need FPR ≤0.02"),
            (candidate.review_status == "approved", "need human approval"),
            (self._regression_passed(candidate), "need regression pass"),
        ]
        failed = [(ok, reason) for ok, reason in checks if not ok]
        if failed:
            return False, "; ".join(r for _, r in failed)
        return True, "all checks passed"

    def promote(self, candidate: RuleCandidate) -> None:
        """
        Promote candidate to active rule/entity/noise/TM.
        Updates status to 'promoted' and applies to relevant subsystem.
        """

    def _regression_passed(self, candidate: RuleCandidate) -> bool:
        """Run regression suite with candidate applied, check if all metrics pass."""
```

### P11-T6 — EvaluationReporter
File: `src/learning/evaluation_reporter.py`

```python
class EvaluationReporter:
    def run_evaluation(
        self, corpus_id: str, engine_version: str
    ) -> EvaluationResult:
        """Run full evaluation on gold corpus, return metrics."""

    def save_run(self, result: EvaluationResult) -> int:
        """Save to evaluation_runs table, return run ID."""

    def compare_runs(self, run_a: int, run_b: int) -> ComparisonReport:
        """Compare two runs, highlight regressions and improvements."""

    def export_report(self, run_id: int) -> str:
        """Export Markdown evaluation report."""
```

### P11-T7 — MetadataDB manager
File: `src/state/metadata_db.py`

```python
class MetadataDB:
    """Central manager for all learning-related database operations."""

    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._run_migrations()

    def save_review(self, review: ReviewDiff, *, reviewer: str) -> int:
    def get_reviews(self, *, status: str = None) -> list[HumanReview]:
    def save_candidate(self, candidate: RuleCandidate) -> int:
    def get_candidates(self, *, status: str = None) -> list[RuleCandidate]:
    def save_evaluation_run(self, run: EvaluationResult) -> int:
    def get_latest_run(self) -> EvaluationResult | None:
```

## Files to Create/Modify
- `src/state/metadata_db.py` — [NEW] Central DB manager
- `src/state/migrations/004_learning_loop.sql` — [NEW] 5 tables
- `src/state/migrations/005_evaluation_runs.sql` — [NEW] (if separate)
- `src/state/migrations/006_term_bank_versioning.sql` — [NEW] (if separate)
- `src/learning/__init__.py` — [NEW]
- `src/learning/review_diff.py` — [NEW]
- `src/learning/error_classifier.py` — [NEW]
- `src/learning/candidate_miner.py` — [NEW]
- `src/learning/promotion_gate.py` — [NEW]
- `src/learning/regression_runner.py` — [NEW]
- `src/learning/evaluation_reporter.py` — [NEW]
- `tests/test_learning/test_promotion_gate.py` — [NEW]
- `tests/test_learning/test_error_classifier.py` — [NEW]
- `tests/test_learning/test_candidate_miner.py` — [NEW]

## Definition of Done
```
[ ] 5 database tables created via migrations
[ ] ReviewDiff computes structured diff from machine vs edited
[ ] ErrorClassifier auto-tags 10 error types
[ ] CandidateMiner extracts patterns from reviews
[ ] PromotionGate: ALL 5 conditions checked
[ ] No auto-promotion without human review (A12)
[ ] No promotion when regression fails (A13)
[ ] EvaluationReporter saves runs + comparison
[ ] MetadataDB manages all CRUD operations
[ ] evaluation_runs saved with metrics_json
[ ] Tests pass
```

---
Next Phase: Phase 12 — Regression Gate + CI
