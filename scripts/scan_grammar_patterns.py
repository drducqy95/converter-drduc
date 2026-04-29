#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run the coach-only grammar pattern scanner on TXT files or directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.learning.grammar_pattern_scanner import (  # noqa: E402
    GrammarLearningPatternScanner,
    write_grammar_learning_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-LLM grammar scanner for translator learning coach")
    parser.add_argument("paths", nargs="+", help="TXT file(s) or directory/directories to scan")
    parser.add_argument("--out-dir", default="reports/grammar_learning", help="Directory for JSON/Markdown/CSV reports")
    parser.add_argument("--unknown-min-count", type=int, default=5, help="Minimum count for unknown candidates")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum number of TXT files to scan")
    parser.add_argument("--max-bytes-per-file", type=int, default=None, help="Optional byte cap per file for quick sampling")
    parser.add_argument("--max-sentences", type=int, default=None, help="Optional global sentence cap for quick sampling")
    parser.add_argument("--candidate-limit", type=int, default=200, help="Maximum unknown candidates in report")
    parser.add_argument("--json-only", action="store_true", help="Print JSON summary to stdout in addition to writing files")
    args = parser.parse_args()

    scanner = GrammarLearningPatternScanner()
    report = scanner.analyze_paths(
        args.paths,
        unknown_min_count=args.unknown_min_count,
        max_files=args.max_files,
        max_bytes_per_file=args.max_bytes_per_file,
        max_sentences=args.max_sentences,
        candidate_limit=args.candidate_limit,
    )
    paths = write_grammar_learning_report(report, args.out_dir)

    if args.json_only:
        print(json.dumps({"summary": report["summary"], "paths": paths}, ensure_ascii=False, indent=2))
    else:
        summary = report["summary"]
        print("Grammar learning scan complete")
        print(f"- Sources: {summary.get('total_sources', 0)}")
        print(f"- Sentences: {summary.get('total_sentences', 0)}")
        print(f"- Known matches: {summary.get('total_matches', 0)}")
        print(f"- Unknown candidates: {summary.get('unknown_candidate_count', 0)}")
        print(f"- Report: {paths['json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
