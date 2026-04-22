#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export project state into simple Markdown notes for Obsidian-like workflows."""

from __future__ import annotations

import json
from pathlib import Path


class ObsidianSync:
    """Baseline export only; no watch mode yet."""

    def export_project_summary(self, project_dir: str | Path):
        project_path = Path(project_dir)
        state_path = project_path / "state" / "project_state.json"
        output_path = project_path / "reports" / "project_summary.md"
        state = {}
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))

        content = [
            f"# Project {state.get('project_id', project_path.name)}",
            "",
            f"- Source language: {state.get('source_language', 'unknown')}",
            f"- Target language: {state.get('target_language', 'unknown')}",
            f"- Active chapter: {state.get('active_chapter', 'n/a')}",
        ]
        output_path.write_text("\n".join(content), encoding="utf-8")
        return output_path
