#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate that the repository is ready for the v24 release candidate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_regression_gate import evaluate_gate


def validate(*, run_pytest: bool = False) -> dict:
    checks: dict[str, object] = {}
    if run_pytest:
        checks["tests"] = _run_pytest()
    metrics = evaluate_gate(run_pytest=False)
    checks["regression_gate"] = {
        "passed": all(metric.passed for metric in metrics),
        "metrics": [metric.name for metric in metrics if not metric.passed],
    }
    checks["docs"] = _docs_exist()
    checks["changelog"] = _file_contains("CHANGELOG.md", "v24.0")
    checks["ci"] = _file_contains(".github/workflows/test.yml", "run_regression_gate.py")
    checks["term_bank"] = _term_bank_has_universes()
    checks["passed"] = all(
        item is True or (isinstance(item, dict) and item.get("passed") is True)
        for key, item in checks.items()
        if key != "passed"
    )
    return checks


def _run_pytest() -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--tb=short"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {"passed": completed.returncode == 0, "tail": completed.stdout[-2000:]}


def _docs_exist() -> bool:
    required = [
        "ARCHITECTURE_STATUS.md",
        "CROSS_UNIVERSE_GUIDE.md",
        "GRAMMAR_PATTERN_SCANNER.md",
        "GRAMMAR_TRANSFER_PLANNER.md",
        "LEARNING_LOOP.md",
        "REGRESSION_POLICY.md",
        "PROMOTION_POLICY.md",
    ]
    return all((REPO_ROOT / "docs" / name).exists() for name in required)


def _file_contains(path: str, needle: str) -> bool:
    target = REPO_ROOT / path
    return target.exists() and needle in target.read_text(encoding="utf-8")


def _term_bank_has_universes() -> bool:
    universe_dir = REPO_ROOT / "data" / "term_bank" / "universes"
    return universe_dir.exists() and any(path.glob("*.jsonl") for path in universe_dir.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate v24 production readiness")
    parser.add_argument("--run-pytest", action="store_true", help="Include full pytest run")
    parser.add_argument("--out", default="reports/production_ready_report.json")
    args = parser.parse_args()

    report = validate(run_pytest=args.run_pytest)
    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
