#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Aggregate latest manual evaluation artifacts by chapter range."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean


CHAPTER_PATTERNS = (
    re.compile(r"chapter[_-](\d{3})", re.IGNORECASE),
    re.compile(r"(?:^|[_-])ch(\d{3})(?:[_-]|$)", re.IGNORECASE),
)


def main():
    parser = argparse.ArgumentParser(description="Aggregate latest chapter evaluation artifacts")
    parser.add_argument("--artifact-base", default="artifacts/manual_sidecar_tests", help="Artifact root to scan")
    parser.add_argument("--start", type=int, default=1, help="First chapter number to include")
    parser.add_argument("--end", type=int, default=50, help="Last chapter number to include")
    parser.add_argument("--mismatch-word-threshold", type=float, default=0.08, help="Flag likely reference mismatch below this word similarity")
    parser.add_argument("--mismatch-qa-threshold", type=int, default=1, help="Only flag likely reference mismatch when QA is at or below this threshold")
    parser.add_argument("--output-dir", default="", help="Optional output directory")
    args = parser.parse_args()

    artifact_base = Path(args.artifact_base)
    if not artifact_base.exists():
        raise FileNotFoundError(f"Artifact base not found: {artifact_base}")

    latest_by_chapter = _collect_latest_chapter_runs(
        artifact_base=artifact_base,
        start=args.start,
        end=args.end,
    )
    aggregate = _build_aggregate(
        latest_by_chapter=latest_by_chapter,
        start=args.start,
        end=args.end,
        mismatch_word_threshold=args.mismatch_word_threshold,
        mismatch_qa_threshold=args.mismatch_qa_threshold,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir) if args.output_dir else artifact_base / f"aggregate_ch{args.start:03d}_to{args.end:03d}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "summary.md").write_text(_render_markdown_summary(aggregate), encoding="utf-8")
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))


def _collect_latest_chapter_runs(*, artifact_base: Path, start: int, end: int) -> dict[str, dict]:
    latest_by_chapter: dict[str, dict] = {}
    for summary_path in sorted(artifact_base.glob("*/summary.json")):
        if summary_path.parent.name.startswith("aggregate_"):
            continue
        payload = _read_json(summary_path)
        if not isinstance(payload, dict):
            continue
        if "range" in payload and "metrics_all" in payload:
            continue
        for chapter in _extract_chapter_entries(payload, summary_path):
            chapter_id = chapter["chapter_id"]
            chapter_number = _chapter_number(chapter_id)
            if chapter_number is None or not (start <= chapter_number <= end):
                continue
            existing = latest_by_chapter.get(chapter_id)
            if existing is None or chapter["summary_mtime"] >= existing["summary_mtime"]:
                latest_by_chapter[chapter_id] = chapter
    return latest_by_chapter


def _extract_chapter_entries(payload: dict, summary_path: Path) -> list[dict]:
    summary_mtime = summary_path.stat().st_mtime
    if isinstance(payload.get("chapters"), list):
        artifact_root = str(payload.get("artifact_root") or summary_path.parent)
        chapters: list[dict] = []
        for chapter in payload["chapters"]:
            chapter_id = str(chapter.get("chapter_id") or "").strip()
            if not chapter_id:
                continue
            chapters.append(
                {
                    "chapter_id": chapter_id,
                    "artifact_root": artifact_root,
                    "source_path": chapter.get("source_path"),
                    "reference_path": chapter.get("reference_path"),
                    "prepare_seconds": float(chapter.get("prepare_seconds") or 0.0),
                    "translate_seconds": float(chapter.get("translate_seconds") or 0.0),
                    "qa_seconds": float(chapter.get("qa_seconds") or 0.0),
                    "total_seconds": float(chapter.get("total_seconds") or 0.0),
                    "qa_total": int(chapter.get("qa_total") or 0),
                    "qa_issue_counts": dict(chapter.get("qa_issue_counts") or {}),
                    "word_similarity": _float_or_none(chapter.get("word_similarity")),
                    "char_similarity": _float_or_none(chapter.get("char_similarity")),
                    "line_similarity": _float_or_none(chapter.get("line_similarity")),
                    "style_profile": chapter.get("style_profile"),
                    "auto_applied": list(chapter.get("auto_applied") or []),
                    "recommendations": list(chapter.get("recommendations") or []),
                    "summary_path": str(summary_path),
                    "summary_mtime": summary_mtime,
                }
            )
        return chapters

    chapter_id = _infer_chapter_id(payload, summary_path)
    if not chapter_id:
        return []
    return [
        {
            "chapter_id": chapter_id,
            "artifact_root": str(payload.get("artifact_dir") or summary_path.parent),
            "source_path": payload.get("source_file"),
            "reference_path": payload.get("reference_file"),
            "prepare_seconds": float(payload.get("prepare_seconds") or 0.0),
            "translate_seconds": float(payload.get("translate_seconds") or 0.0),
            "qa_seconds": float(payload.get("qa_seconds") or 0.0),
            "total_seconds": float(payload.get("total_seconds") or 0.0),
            "qa_total": int(payload.get("qa_total") or 0),
            "qa_issue_counts": dict(payload.get("qa_issue_counts") or {}),
            "word_similarity": _float_or_none(payload.get("word_similarity")),
            "char_similarity": _float_or_none(payload.get("char_similarity")),
            "line_similarity": _float_or_none(payload.get("line_similarity")),
            "style_profile": payload.get("style_profile"),
            "auto_applied": list(payload.get("auto_applied") or []),
            "recommendations": list(payload.get("recommendations") or []),
            "summary_path": str(summary_path),
            "summary_mtime": summary_mtime,
        }
    ]


def _infer_chapter_id(payload: dict, summary_path: Path) -> str | None:
    for key in ("source_file", "reference_file", "source_path", "reference_path"):
        value = payload.get(key)
        if not value:
            continue
        number = _extract_chapter_number(str(value))
        if number is not None:
            return f"chapter_{number:03d}"
    number = _extract_chapter_number(summary_path.parent.name)
    if number is not None:
        return f"chapter_{number:03d}"
    return None


def _build_aggregate(
    *,
    latest_by_chapter: dict[str, dict],
    start: int,
    end: int,
    mismatch_word_threshold: float,
    mismatch_qa_threshold: int,
) -> dict:
    chapters = [latest_by_chapter[key] for key in sorted(latest_by_chapter)]
    chapter_ids = {item["chapter_id"] for item in chapters}
    expected = [f"chapter_{number:03d}" for number in range(start, end + 1)]
    missing = [chapter_id for chapter_id in expected if chapter_id not in chapter_ids]

    issue_totals: Counter[str] = Counter()
    issue_chapters: dict[str, list[str]] = defaultdict(list)
    style_profiles: Counter[str] = Counter()
    for chapter in chapters:
        style_profiles[str(chapter.get("style_profile") or "unknown")] += 1
        for issue_type, count in chapter["qa_issue_counts"].items():
            if not count:
                continue
            issue_totals[issue_type] += int(count)
            issue_chapters[issue_type].append(chapter["chapter_id"])

    probable_reference_mismatches = [
        {
            "chapter_id": chapter["chapter_id"],
            "artifact_root": chapter["artifact_root"],
            "word_similarity": chapter["word_similarity"],
            "qa_total": chapter["qa_total"],
            "reference_path": chapter.get("reference_path"),
        }
        for chapter in chapters
        if chapter.get("word_similarity") is not None
        and chapter["word_similarity"] <= mismatch_word_threshold
        and chapter["qa_total"] <= mismatch_qa_threshold
    ]
    mismatch_ids = {item["chapter_id"] for item in probable_reference_mismatches}
    stable_chapters = [chapter for chapter in chapters if chapter["chapter_id"] not in mismatch_ids]

    return {
        "range": {
            "start": start,
            "end": end,
            "expected_chapters": len(expected),
            "covered_chapters": len(chapters),
            "missing_chapters": missing,
        },
        "latest_artifacts": [
            {
                "chapter_id": chapter["chapter_id"],
                "artifact_root": chapter["artifact_root"],
                "summary_path": chapter["summary_path"],
            }
            for chapter in chapters
        ],
        "metrics_all": _summarize_metrics(chapters),
        "metrics_excluding_reference_mismatches": _summarize_metrics(stable_chapters),
        "issue_totals": dict(issue_totals),
        "issue_chapters": {issue_type: sorted(chapters_for_issue) for issue_type, chapters_for_issue in issue_chapters.items()},
        "style_profile_counts": dict(style_profiles),
        "chapters_with_qa": [
            _chapter_snapshot(chapter)
            for chapter in sorted(chapters, key=lambda item: (-item["qa_total"], item["chapter_id"]))
            if chapter["qa_total"] > 0
        ],
        "lowest_similarity_chapters": [
            _chapter_snapshot(chapter)
            for chapter in sorted(
                chapters,
                key=lambda item: (
                    float("inf") if item.get("word_similarity") is None else item["word_similarity"],
                    item["chapter_id"],
                ),
            )[:10]
        ],
        "slowest_chapters": [
            _chapter_snapshot(chapter)
            for chapter in sorted(chapters, key=lambda item: (-item["total_seconds"], item["chapter_id"]))[:10]
        ],
        "probable_reference_mismatches": probable_reference_mismatches,
    }


def _summarize_metrics(chapters: list[dict]) -> dict:
    if not chapters:
        return {
            "chapter_count": 0,
            "avg_prepare_seconds": 0.0,
            "avg_translate_seconds": 0.0,
            "avg_total_seconds": 0.0,
            "avg_qa_total": 0.0,
            "avg_word_similarity": None,
            "avg_char_similarity": None,
            "avg_line_similarity": None,
            "total_qa_issues": 0,
        }

    prepare_values = [chapter["prepare_seconds"] for chapter in chapters]
    translate_values = [chapter["translate_seconds"] for chapter in chapters]
    total_values = [chapter["total_seconds"] for chapter in chapters]
    qa_totals = [chapter["qa_total"] for chapter in chapters]
    word_values = [chapter["word_similarity"] for chapter in chapters if chapter.get("word_similarity") is not None]
    char_values = [chapter["char_similarity"] for chapter in chapters if chapter.get("char_similarity") is not None]
    line_values = [chapter["line_similarity"] for chapter in chapters if chapter.get("line_similarity") is not None]

    return {
        "chapter_count": len(chapters),
        "avg_prepare_seconds": round(mean(prepare_values), 4),
        "avg_translate_seconds": round(mean(translate_values), 4),
        "avg_total_seconds": round(mean(total_values), 4),
        "avg_qa_total": round(mean(qa_totals), 4),
        "avg_word_similarity": round(mean(word_values), 4) if word_values else None,
        "avg_char_similarity": round(mean(char_values), 4) if char_values else None,
        "avg_line_similarity": round(mean(line_values), 4) if line_values else None,
        "total_qa_issues": int(sum(qa_totals)),
    }


def _chapter_snapshot(chapter: dict) -> dict:
    return {
        "chapter_id": chapter["chapter_id"],
        "artifact_root": chapter["artifact_root"],
        "qa_total": chapter["qa_total"],
        "qa_issue_counts": chapter["qa_issue_counts"],
        "word_similarity": chapter.get("word_similarity"),
        "char_similarity": chapter.get("char_similarity"),
        "total_seconds": chapter["total_seconds"],
        "style_profile": chapter.get("style_profile"),
    }


def _chapter_number(chapter_id: str) -> int | None:
    return _extract_chapter_number(chapter_id or "")


def _extract_chapter_number(text: str) -> int | None:
    for pattern in CHAPTER_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def _float_or_none(value) -> float | None:
    if value is None:
        return None
    return float(value)


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _render_markdown_summary(summary: dict) -> str:
    metrics_all = summary["metrics_all"]
    metrics_stable = summary["metrics_excluding_reference_mismatches"]
    lines = [
        "# Aggregate Evaluation Summary",
        "",
        f"- Range: chapter_{summary['range']['start']:03d} to chapter_{summary['range']['end']:03d}",
        f"- Covered chapters: {summary['range']['covered_chapters']}/{summary['range']['expected_chapters']}",
        f"- Missing chapters: {', '.join(summary['range']['missing_chapters']) if summary['range']['missing_chapters'] else 'none'}",
        f"- Avg translate seconds: {metrics_all['avg_translate_seconds']}",
        f"- Avg total seconds: {metrics_all['avg_total_seconds']}",
        f"- Avg QA issues: {metrics_all['avg_qa_total']}",
        f"- Avg word similarity: {metrics_all['avg_word_similarity']}",
        f"- Avg char similarity: {metrics_all['avg_char_similarity']}",
        f"- Total QA issues: {metrics_all['total_qa_issues']}",
        "",
        "## Stable Metrics",
        "",
        f"- Excluding probable reference mismatches: {metrics_stable['chapter_count']} chapters",
        f"- Avg QA issues: {metrics_stable['avg_qa_total']}",
        f"- Avg word similarity: {metrics_stable['avg_word_similarity']}",
        f"- Avg char similarity: {metrics_stable['avg_char_similarity']}",
        "",
        "## Issue Totals",
        "",
    ]
    if summary["issue_totals"]:
        for issue_type, count in sorted(summary["issue_totals"].items()):
            chapters = ", ".join(summary["issue_chapters"].get(issue_type, []))
            lines.append(f"- {issue_type}: {count} ({chapters})")
    else:
        lines.append("- none")

    lines.extend(["", "## Highest QA", ""])
    qa_chapters = summary["chapters_with_qa"][:10]
    if qa_chapters:
        for chapter in qa_chapters:
            lines.append(
                f"- {chapter['chapter_id']}: qa={chapter['qa_total']} "
                f"word_sim={chapter['word_similarity']} issues={chapter['qa_issue_counts']}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Lowest Similarity", ""])
    for chapter in summary["lowest_similarity_chapters"]:
        lines.append(
            f"- {chapter['chapter_id']}: word_sim={chapter['word_similarity']} "
            f"qa={chapter['qa_total']} artifact={chapter['artifact_root']}"
        )

    lines.extend(["", "## Probable Reference Mismatches", ""])
    mismatches = summary["probable_reference_mismatches"]
    if mismatches:
        for item in mismatches:
            lines.append(
                f"- {item['chapter_id']}: word_sim={item['word_similarity']} "
                f"qa={item['qa_total']} reference={item['reference_path']}"
            )
    else:
        lines.append("- none")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
