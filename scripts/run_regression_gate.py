#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Production regression gate for v24 hardening checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

from src.engine.rbmt_translator import RBMTTranslator
from src.pipeline.term_bank import TermBank


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class GateMetric:
    name: str
    passed: bool
    value: object
    threshold: object
    detail: str = ""


def evaluate_gate(*, run_pytest: bool = False) -> list[GateMetric]:
    metrics: list[GateMetric] = []
    metrics.append(_metric("term_bank_jsonl_valid", *_check_term_bank_jsonl()))
    metrics.append(_metric("term_bank_no_duplicate_keys", *_check_term_bank_duplicates()))
    metrics.append(_metric("universe_detection_accuracy_seed", *_check_universe_detection_seed()))
    metrics.append(_metric("same_name_resolution_seed", *_check_same_name_resolution_seed()))
    metrics.append(_metric("tm_split_available", _path_contains("src/state/translation_memory.py", "tm_machine"), True))
    metrics.append(_metric("trace_foundation_available", _path_contains("src/core/trace.py", "class TraceEvent"), True))
    metrics.append(_metric("segment_packet_available", _path_contains("src/pipeline/packet.py", "class SegmentPacket"), True))
    metrics.append(_metric("grammar_transfer_available", _path_contains("src/grammar/transfer_engine.py", "class GrammarTransferEngine"), True))
    metrics.append(_metric("entity_enrichment_available", (REPO_ROOT / "src/pipeline/entity_enrichment.py").exists(), True))
    metrics.append(_metric("docs_complete", *_check_docs_complete()))
    metrics.append(_metric("ci_regression_step", _path_contains(".github/workflows/test.yml", "run_regression_gate.py"), True))
    metrics.append(_metric("no_universe_tag_seed_output", *_check_no_universe_tag_output()))
    metrics.append(_metric("performance_seed_ms", *_check_seed_performance()))
    if run_pytest:
        metrics.append(_metric("pytest", *_run_pytest()))
    return metrics


def _metric(name: str, value: object, threshold: object, detail: str = "") -> GateMetric:
    if isinstance(threshold, bool):
        passed = bool(value) is threshold
    elif isinstance(value, (int, float)) and isinstance(threshold, (int, float)):
        passed = float(value) <= float(threshold)
    else:
        passed = value == threshold
    return GateMetric(name=name, passed=passed, value=value, threshold=threshold, detail=detail)


def _check_term_bank_jsonl() -> tuple[bool, bool, str]:
    try:
        TermBank().records
    except Exception as exc:
        return False, True, str(exc)
    return True, True, "all JSONL rows loaded"


def _check_term_bank_duplicates() -> tuple[bool, bool, str]:
    seen: set[tuple[str, str, str]] = set()
    duplicates: list[str] = []
    for record in TermBank().records:
        key = (record.source, record.universe, record.scope)
        if key in seen:
            duplicates.append("|".join(key))
        seen.add(key)
    return not duplicates, True, f"{len(duplicates)} duplicate key(s)"


def _check_universe_detection_seed() -> tuple[bool, bool, str]:
    bank = TermBank()
    cases = {
        "dau_pha_thuong_khung": "萧炎收起异火，药尘提醒他斗气不可外泄。",
        "dau_la_dai_luc": "唐三看着小舞，魂环在武魂之后浮现。",
        "pham_nhan_tu_tien": "韩立取出掌天瓶，又想起南宫婉。",
        "quy_bi_chi_chu": "克莱恩记录序列和非凡特性的线索。",
    }
    passed = 0
    for expected, text in cases.items():
        detected = {universe for universe, confidence in bank.detect_universe(text) if confidence >= 0.5}
        if expected in detected:
            passed += 1
    accuracy = passed / len(cases)
    return accuracy >= 0.9, True, f"{passed}/{len(cases)} seed cases; accuracy={accuracy:.4f}"


def _check_same_name_resolution_seed() -> tuple[bool, bool, str]:
    bank = TermBank()
    record = bank.lookup_with_context("雷神", context_window="奥丁召见雷神，复仇者抵达阿斯加德。")[0]
    default_record = bank.lookup_with_context("雷神", context_window="雷神说道。雷神点头。")[0]
    ok = record.target == "Thor" and default_record.target != "Thor"
    return ok, True, f"context={record.target}; default={default_record.target}"


def _check_docs_complete() -> tuple[bool, bool, str]:
    docs = [
        "docs/ARCHITECTURE_STATUS.md",
        "docs/CROSS_UNIVERSE_GUIDE.md",
        "docs/GRAMMAR_PATTERN_SCANNER.md",
        "docs/GRAMMAR_TRANSFER_PLANNER.md",
        "docs/LEARNING_LOOP.md",
        "docs/REGRESSION_POLICY.md",
        "docs/PROMOTION_POLICY.md",
    ]
    missing = [doc for doc in docs if not (REPO_ROOT / doc).exists()]
    return not missing, True, f"missing={missing}"


def _check_no_universe_tag_output() -> tuple[bool, bool, str]:
    translator = RBMTTranslator()
    try:
        result = translator.translate_text("奥丁召见雷神。", config={"locked_entities": [{"source": "雷神", "target": "Thor"}]})
    finally:
        translator.close()
    ok = "[" not in result.clean_text and "]" not in result.clean_text
    return ok, True, result.clean_text


def _check_seed_performance() -> tuple[float, float, str]:
    translator = RBMTTranslator()
    started = perf_counter()
    try:
        translator.translate_text("韩立取出掌天瓶。萧炎看见异火。唐三召出魂环。")
    finally:
        translator.close()
    elapsed_ms = round((perf_counter() - started) * 1000, 3)
    return elapsed_ms, 2000.0, "seed translation wall time"


def _run_pytest() -> tuple[bool, bool, str]:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--tb=short"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, True, completed.stdout[-2000:]


def _path_contains(path: str, needle: str) -> bool:
    target = REPO_ROOT / path
    return target.exists() and needle in target.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run v24 production regression gate")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any metric fails")
    parser.add_argument("--run-pytest", action="store_true", help="Include full pytest run")
    parser.add_argument("--out", default="reports/regression_gate_report.json", help="JSON report path")
    args = parser.parse_args()

    metrics = evaluate_gate(run_pytest=args.run_pytest)
    report = {
        "passed": all(metric.passed for metric in metrics),
        "metrics": [asdict(metric) for metric in metrics],
    }
    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if args.strict and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
