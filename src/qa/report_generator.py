#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate Markdown QA reports and orchestrate checkers."""

from __future__ import annotations

import json
from pathlib import Path

from src.qa.emotion_consistency_checker import EmotionConsistencyChecker
from src.qa.length_checker import LengthChecker
from src.qa.pronoun_checker import PronounChecker
from src.qa.structure_checker import StructureChecker
from src.qa.terminology_checker import TerminologyChecker
from src.qa.untranslated_detector import UntranslatedDetector


class QAReportGenerator:
    """Run QA checks and export Markdown/JSON reports."""

    def __init__(self):
        self.checkers = [
            TerminologyChecker(),
            PronounChecker(),
            EmotionConsistencyChecker(),
            StructureChecker(),
            UntranslatedDetector(),
            LengthChecker(),
        ]

    def run(self, *, source_text: str, translation_result, config: dict) -> dict:
        issues: list[dict] = []
        for checker in self.checkers:
            if isinstance(checker, StructureChecker):
                issues.extend(checker.run(source_text, translation_result))
            elif isinstance(checker, TerminologyChecker):
                issues.extend(checker.run(translation_result, config))
            else:
                issues.extend(checker.run(translation_result))
        return {
            "summary": {
                "issues": len(issues),
                "segments": len(translation_result.segments),
            },
            "issues": issues,
        }

    def write(self, report: dict, project_dir: str | Path, report_stem: str = "qa_report"):
        project_path = Path(project_dir)
        reports_dir = project_path / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        md_lines = [
            "# QA Report",
            "",
            f"- Issues: {report['summary']['issues']}",
            f"- Segments: {report['summary']['segments']}",
            "",
            "## Findings",
        ]
        for issue in report["issues"]:
            md_lines.append(
                f"- [{issue['severity']}] {issue['checker']} @ {issue['segment_id']}: {issue['message']}"
            )
        if not report["issues"]:
            md_lines.append("- No issues detected.")
        (reports_dir / f"{report_stem}.md").write_text("\n".join(md_lines), encoding="utf-8")
        (reports_dir / f"{report_stem}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
