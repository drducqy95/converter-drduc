#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run a warm-cache batch evaluation across external chapters."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.rbmt_translator import RBMTTranslator
from src.learning.project_learning_engine import ProjectLearningEngine
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline
from src.qa.report_generator import QAReportGenerator
from src.state.project_manager import ProjectManager
from src.ui.sidecar_bridge import _resolve_translation_config


def main():
    parser = argparse.ArgumentParser(description="Run warm-cache batch evaluation for external chapters")
    parser.add_argument("--source-dir", required=True, help="External source directory containing chapter_XXX.md")
    parser.add_argument("--start", type=int, default=3, help="Starting chapter number")
    parser.add_argument("--count", type=int, default=10, help="Number of chapters to run")
    parser.add_argument("--workspace-base", default="workspace_projects", help="Base workspace directory")
    parser.add_argument("--artifact-base", default="artifacts/manual_sidecar_tests", help="Artifact output base")
    parser.add_argument("--project-id", default="", help="Optional workspace project id")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chapter_start = args.start
    chapter_end = args.start + args.count - 1
    artifact_root = Path(args.artifact_base) / f"aclinhquocgia_batch{args.count}_ch{chapter_start:03d}_to{chapter_end:03d}_{timestamp}"
    artifact_root.mkdir(parents=True, exist_ok=True)

    manager = ProjectManager(args.workspace_base)
    project_id = args.project_id.strip() or f"aclinh-batch-{chapter_start:03d}-{chapter_end:03d}-{timestamp}"
    project = manager.create_project(project_id)
    project_dir = Path(project.project_dir)

    pipeline = PreTranslationPipeline()
    translator = RBMTTranslator(tm_db_path=project_dir / "state" / "tm.sqlite")
    qa_generator = QAReportGenerator()
    learning = ProjectLearningEngine()

    batch_started_at = perf_counter()
    chapter_summaries: list[dict] = []
    failures: list[dict] = []

    try:
        for chapter_number in range(chapter_start, chapter_start + args.count):
            chapter_stem = f"chapter_{chapter_number:03d}"
            source_path = source_dir / f"{chapter_stem}.md"
            chapter_started_at = perf_counter()
            if not source_path.exists():
                failures.append({"chapter_id": chapter_stem, "error": "source_not_found", "source_path": str(source_path)})
                continue

            chapter_output_dir = artifact_root / chapter_stem
            (chapter_output_dir / "output").mkdir(parents=True, exist_ok=True)
            (chapter_output_dir / "reports").mkdir(parents=True, exist_ok=True)

            prepare_started_at = perf_counter()
            prepare_result = pipeline.prepare(source_path, project_dir)
            prepare_seconds = perf_counter() - prepare_started_at

            internal_chapter_id = prepare_result.chapters[0].chapter_id if prepare_result.chapters else "chapter-001"
            manager.set_active_chapter(project_id, internal_chapter_id)
            source_text = _resolve_source_text(prepare_result, source_path)
            config = _resolve_translation_config(project_dir, prepare_result.config, internal_chapter_id)

            translate_started_at = perf_counter()
            translation_result = translator.translate_text(source_text, config=config)
            translate_seconds = perf_counter() - translate_started_at
            translator.export(translation_result, project_dir, artifact_stem=chapter_stem)

            qa_started_at = perf_counter()
            qa_report = qa_generator.run(
                source_text=source_text,
                translation_result=translation_result,
                config=config,
            )
            qa_seconds = perf_counter() - qa_started_at
            qa_generator.write(qa_report, project_dir, report_stem=f"qa_report_{chapter_stem}")

            runtime_metrics = {
                "prepare_seconds": prepare_seconds,
                "translate_seconds": translate_seconds,
                "qa_seconds": qa_seconds,
                "total_seconds": perf_counter() - chapter_started_at,
                "source_chars": len(source_text),
                "output_chars": len(translation_result.clean_text),
            }
            learning_report = learning.record_run(
                project_dir=project_dir,
                manager=manager,
                project_id=project_id,
                chapter_id=chapter_stem,
                translation_result=translation_result,
                qa_report=qa_report,
                config=config,
                runtime_metrics=runtime_metrics,
            )

            _copy_if_exists(project_dir / "output" / f"{chapter_stem}.txt", chapter_output_dir / "output" / f"{chapter_stem}.txt")
            _copy_if_exists(project_dir / "drafts" / f"{chapter_stem}_draft.txt", chapter_output_dir / "output" / f"{chapter_stem}_draft.txt")
            _copy_if_exists(project_dir / "reports" / f"qa_report_{chapter_stem}.json", chapter_output_dir / "reports" / f"qa_report_{chapter_stem}.json")
            _copy_if_exists(project_dir / "reports" / f"qa_report_{chapter_stem}.md", chapter_output_dir / "reports" / f"qa_report_{chapter_stem}.md")
            _copy_if_exists(project_dir / "reports" / f"learning_report_{chapter_stem}.json", chapter_output_dir / "reports" / f"learning_report_{chapter_stem}.json")
            _copy_if_exists(project_dir / "reports" / f"learning_report_{chapter_stem}.md", chapter_output_dir / "reports" / f"learning_report_{chapter_stem}.md")

            summary = _build_chapter_summary(
                chapter_id=chapter_stem,
                source_path=source_path,
                runtime_metrics=runtime_metrics,
                qa_report=qa_report,
                learning_report=learning_report,
            )
            (chapter_output_dir / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            chapter_summaries.append(summary)
            print(
                f"{chapter_stem}: total={summary['total_seconds']:.3f}s "
                f"translate={summary['translate_seconds']:.3f}s "
                f"qa={summary['qa_total']} "
                f"word_sim={summary.get('word_similarity', 0.0):.4f}"
            )
    finally:
        pipeline.close()
        translator.close()

    aggregate = _build_aggregate_summary(
        project_id=project_id,
        project_dir=project_dir,
        artifact_root=artifact_root,
        chapter_summaries=chapter_summaries,
        failures=failures,
        batch_seconds=perf_counter() - batch_started_at,
    )
    (artifact_root / "summary.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    (artifact_root / "summary.md").write_text(_render_markdown_summary(aggregate), encoding="utf-8")
    _copy_if_exists(project_dir / "working" / "config" / "translation_config.json", artifact_root / "translation_config.json")
    _copy_if_exists(project_dir / "working" / "config" / "learned_terms.json", artifact_root / "learned_terms.json")
    _copy_if_exists(project_dir / "state" / "learning_history.json", artifact_root / "learning_history.json")

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))


def _resolve_source_text(prepare_result, source_path: Path) -> str:
    if prepare_result.chapters:
        if len(prepare_result.chapters) == 1:
            return prepare_result.chapters[0].text
        return "\n\n".join(chapter.text for chapter in prepare_result.chapters)
    return source_path.read_text(encoding="utf-8")


def _build_chapter_summary(
    *,
    chapter_id: str,
    source_path: Path,
    runtime_metrics: dict,
    qa_report: dict,
    learning_report: dict,
) -> dict:
    reference = (learning_report.get("current_run") or {}).get("reference_comparison") or {}
    auto_applied = learning_report.get("auto_applied") or []
    return {
        "chapter_id": chapter_id,
        "source_path": str(source_path),
        "prepare_seconds": round(float(runtime_metrics["prepare_seconds"]), 4),
        "translate_seconds": round(float(runtime_metrics["translate_seconds"]), 4),
        "qa_seconds": round(float(runtime_metrics["qa_seconds"]), 4),
        "total_seconds": round(float(runtime_metrics["total_seconds"]), 4),
        "qa_total": int(qa_report.get("summary", {}).get("issues", 0)),
        "qa_issue_counts": (learning_report.get("current_run") or {}).get("qa_issue_counts", {}),
        "char_similarity": float(reference.get("char_similarity", 0.0) or 0.0),
        "word_similarity": float(reference.get("word_similarity", 0.0) or 0.0),
        "line_similarity": float(reference.get("line_similarity", 0.0) or 0.0),
        "reference_path": reference.get("path"),
        "style_profile": (learning_report.get("current_run") or {}).get("style_profile"),
        "auto_applied": auto_applied,
        "recommendations": learning_report.get("recommendations", []),
    }


def _build_aggregate_summary(
    *,
    project_id: str,
    project_dir: Path,
    artifact_root: Path,
    chapter_summaries: list[dict],
    failures: list[dict],
    batch_seconds: float,
) -> dict:
    completed = len(chapter_summaries)
    qa_totals = [float(item["qa_total"]) for item in chapter_summaries] or [0.0]
    translate_seconds = [float(item["translate_seconds"]) for item in chapter_summaries] or [0.0]
    total_seconds = [float(item["total_seconds"]) for item in chapter_summaries] or [0.0]
    word_similarity = [float(item["word_similarity"]) for item in chapter_summaries if item.get("word_similarity") is not None]
    char_similarity = [float(item["char_similarity"]) for item in chapter_summaries if item.get("char_similarity") is not None]
    line_similarity = [float(item["line_similarity"]) for item in chapter_summaries if item.get("line_similarity") is not None]

    return {
        "project_id": project_id,
        "project_dir": str(project_dir),
        "artifact_root": str(artifact_root),
        "completed_chapters": completed,
        "failed_chapters": failures,
        "batch_seconds": round(batch_seconds, 4),
        "avg_translate_seconds": round(mean(translate_seconds), 4),
        "avg_total_seconds": round(mean(total_seconds), 4),
        "avg_qa_total": round(mean(qa_totals), 4),
        "avg_word_similarity": round(mean(word_similarity), 4) if word_similarity else None,
        "avg_char_similarity": round(mean(char_similarity), 4) if char_similarity else None,
        "avg_line_similarity": round(mean(line_similarity), 4) if line_similarity else None,
        "chapters": chapter_summaries,
    }


def _render_markdown_summary(summary: dict) -> str:
    lines = [
        "# Batch Summary",
        "",
        f"- Project: {summary['project_id']}",
        f"- Workspace: {summary['project_dir']}",
        f"- Completed chapters: {summary['completed_chapters']}",
        f"- Batch seconds: {summary['batch_seconds']:.4f}",
        f"- Avg translate seconds: {summary['avg_translate_seconds']:.4f}",
        f"- Avg total seconds: {summary['avg_total_seconds']:.4f}",
        f"- Avg QA issues: {summary['avg_qa_total']:.4f}",
        f"- Avg word similarity: {summary['avg_word_similarity']}",
        f"- Avg char similarity: {summary['avg_char_similarity']}",
        "",
        "## Chapters",
    ]
    for chapter in summary["chapters"]:
        lines.append(
            f"- {chapter['chapter_id']}: total={chapter['total_seconds']:.4f}s "
            f"translate={chapter['translate_seconds']:.4f}s "
            f"qa={chapter['qa_total']} word_sim={chapter['word_similarity']:.4f}"
        )
    if summary["failed_chapters"]:
        lines.extend(["", "## Failures"])
        for failure in summary["failed_chapters"]:
            lines.append(f"- {failure['chapter_id']}: {failure['error']}")
    return "\n".join(lines)


def _copy_if_exists(source: Path, target: Path):
    if not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


if __name__ == "__main__":
    main()
