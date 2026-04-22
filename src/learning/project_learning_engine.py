#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post-run learning loop for project-level translation tuning."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

from src.engine.style_profiles import STYLE_PROFILES, default_style_preferences


HISTORY_LIMIT = 20


class ProjectLearningEngine:
    """Persist run history, sync verified terms, and auto-apply safe tuning."""

    def sync_verified_candidates(self, *, project_dir: str | Path, manager, project_id: str) -> dict:
        project_path = Path(project_dir)
        target_path = project_path / "working" / "config" / "learned_terms.json"
        existing = self._load_json(target_path, {})

        verified = manager.list_candidate_entries(project_id, status="verified")
        generated_phrases: list[dict] = []
        generated_locked: list[dict] = []
        seen_phrases: set[str] = set()
        seen_locked: set[str] = set()

        for entry in verified:
            source = str(entry.source_text).strip()
            target = str(entry.target_text).strip()
            if not source or not target:
                continue

            if source not in seen_phrases:
                generated_phrases.append(
                    {
                        "source": source,
                        "target": target,
                        "chapter_id": entry.chapter_id,
                        "segment_id": entry.segment_id,
                        "fallback_level": entry.fallback_level,
                        "reason": entry.reason,
                        "origin": "verified_candidate",
                    }
                )
                seen_phrases.add(source)

            if source not in seen_locked and self._should_promote_to_locked_entity(source, target, entry.reason):
                generated_locked.append(
                    {
                        "source": source,
                        "target": target,
                        "entity_type": self._infer_entity_type(entry.reason),
                        "origin": "verified_candidate",
                    }
                )
                seen_locked.add(source)

        payload = {
            "generated_at": self._now_iso(),
            "phrase_overrides": self._merge_generated_items(
                existing.get("phrase_overrides", []),
                generated_phrases,
            ),
            "locked_entities": self._merge_generated_items(
                existing.get("locked_entities", []),
                generated_locked,
            ),
        }
        self._write_json(target_path, payload)
        return {
            "verified_candidates": len(verified),
            "phrase_overrides": len(payload["phrase_overrides"]),
            "locked_entities": len(payload["locked_entities"]),
            "path": str(target_path),
        }

    def record_run(
        self,
        *,
        project_dir: str | Path,
        manager,
        project_id: str,
        chapter_id: str | None,
        translation_result,
        qa_report: dict,
        config: dict,
        runtime_metrics: dict | None = None,
    ) -> dict:
        project_path = Path(project_dir)
        chapter_key = chapter_id or "_project"
        learned_terms = self.sync_verified_candidates(
            project_dir=project_path,
            manager=manager,
            project_id=project_id,
        )

        history_path = project_path / "state" / "learning_history.json"
        history = self._load_json(
            history_path,
            {
                "project_id": project_id,
                "chapters": {},
            },
        )
        chapter_history = list(history.get("chapters", {}).get(chapter_key, []))
        previous_run = chapter_history[-1] if chapter_history else None

        current_run = self._build_run_snapshot(
            chapter_id=chapter_id,
            translation_result=translation_result,
            qa_report=qa_report,
            config=config,
            runtime_metrics=runtime_metrics or {},
            manager=manager,
            project_id=project_id,
        )
        current_run["learned_terms"] = learned_terms

        delta = self._build_delta(previous_run, current_run)
        recommendations = self._build_recommendations(previous_run, current_run)
        updated_config, auto_applied = self._auto_upgrade_config(
            project_path=project_path,
            chapter_id=chapter_id,
            config=config,
            current_run=current_run,
        )

        current_run["auto_applied"] = auto_applied
        current_run["config_path"] = str(project_path / "working" / "config" / "translation_config.json")
        chapter_history.append(current_run)
        chapter_history = chapter_history[-HISTORY_LIMIT:]
        history.setdefault("chapters", {})[chapter_key] = chapter_history
        history["updated_at"] = self._now_iso()
        self._write_json(history_path, history)

        report = {
            "project_id": project_id,
            "chapter_id": chapter_id,
            "generated_at": self._now_iso(),
            "current_run": current_run,
            "previous_run": previous_run,
            "delta": delta,
            "recommendations": recommendations,
            "auto_applied": auto_applied,
            "learned_terms": learned_terms,
            "updated_config": updated_config,
            "history_path": str(history_path),
        }
        self._write_report(project_path, chapter_id, report)
        return report

    def _build_run_snapshot(
        self,
        *,
        chapter_id: str | None,
        translation_result,
        qa_report: dict,
        config: dict,
        runtime_metrics: dict,
        manager,
        project_id: str,
    ) -> dict:
        issue_counts = Counter(str(issue.get("checker", "unknown")) for issue in qa_report.get("issues", []))
        severity_counts = Counter(str(issue.get("severity", "unknown")) for issue in qa_report.get("issues", []))
        fallback_counts = Counter()
        dialogue_segments = 0
        for segment in translation_result.segments:
            if self._looks_like_dialogue(segment.source_text):
                dialogue_segments += 1
            for trace in segment.trace:
                level = str(trace.get("fallback_level", "")).strip()
                if level:
                    fallback_counts[level] += 1

        all_candidates = manager.list_candidate_entries(project_id)
        chapter_candidates = [
            entry
            for entry in all_candidates
            if not chapter_id or entry.chapter_id == chapter_id
        ]
        reference_comparison = self._compare_with_reference(
            chapter_id=chapter_id,
            clean_text=translation_result.clean_text,
            config=config,
        )

        naturalization = dict((config.get("style_resolution") or {}).get("naturalization") or config.get("naturalization") or {})
        style_profile = (
            (config.get("style_resolution") or {}).get("effective_profile")
            or config.get("style_profile")
            or default_style_preferences(config.get("genre_hints"), config.get("cultural_origin_hint"))["project_profile"]
        )
        return {
            "run_id": self._now_iso(),
            "chapter_id": chapter_id,
            "segments": len(translation_result.segments),
            "style_profile": style_profile,
            "style_resolved_from": (config.get("style_resolution") or {}).get("resolved_from", "unknown"),
            "dialogue_ratio": round(dialogue_segments / max(1, len(translation_result.segments)), 4),
            "source_chars": sum(len(segment.source_text) for segment in translation_result.segments),
            "output_chars": len(translation_result.clean_text),
            "qa_total": int(qa_report.get("summary", {}).get("issues", len(qa_report.get("issues", [])))),
            "qa_issue_counts": dict(sorted(issue_counts.items())),
            "qa_severity_counts": dict(sorted(severity_counts.items())),
            "fallback_counts": dict(sorted(fallback_counts.items())),
            "candidate_entries": len(chapter_candidates),
            "verified_candidates": sum(1 for entry in chapter_candidates if entry.status == "verified"),
            "runtime_metrics": {
                key: float(value)
                for key, value in runtime_metrics.items()
                if isinstance(value, (int, float))
            },
            "naturalization": naturalization,
            "reference_comparison": reference_comparison,
        }

    def _build_delta(self, previous_run: dict | None, current_run: dict) -> dict:
        if not previous_run:
            return {}

        delta: dict[str, object] = {
            "qa_total": current_run["qa_total"] - previous_run.get("qa_total", current_run["qa_total"]),
            "candidate_entries": current_run["candidate_entries"] - previous_run.get("candidate_entries", current_run["candidate_entries"]),
        }

        previous_runtime = previous_run.get("runtime_metrics", {})
        current_runtime = current_run.get("runtime_metrics", {})
        runtime_delta = {}
        for metric_name, metric_value in current_runtime.items():
            if metric_name in previous_runtime:
                runtime_delta[metric_name] = round(metric_value - previous_runtime[metric_name], 4)
        if runtime_delta:
            delta["runtime_metrics"] = runtime_delta

        previous_reference = previous_run.get("reference_comparison") or {}
        current_reference = current_run.get("reference_comparison") or {}
        reference_delta = {}
        for metric_name in ("char_similarity", "word_similarity", "line_similarity"):
            if metric_name in previous_reference and metric_name in current_reference:
                reference_delta[metric_name] = round(current_reference[metric_name] - previous_reference[metric_name], 4)
        if reference_delta:
            delta["reference_comparison"] = reference_delta
        return delta

    def _build_recommendations(self, previous_run: dict | None, current_run: dict) -> list[dict]:
        recommendations: list[dict] = []
        issue_counts = current_run.get("qa_issue_counts", {})
        runtime = current_run.get("runtime_metrics", {})
        reference = current_run.get("reference_comparison") or {}

        if issue_counts.get("terminology") or issue_counts.get("untranslated"):
            recommendations.append(
                {
                    "type": "terminology_review",
                    "priority": "high",
                    "message": "Terminology hoặc untranslated vẫn còn. Nên rà glossary/locked entity và review verified candidates trước khi rerun.",
                }
            )

        if issue_counts.get("pronoun") and current_run.get("dialogue_ratio", 0.0) >= 0.35:
            recommendations.append(
                {
                    "type": "dialogue_style",
                    "priority": "medium",
                    "message": "Chương thiên về hội thoại. Nếu pronoun còn lỗi, profile đối thoại tự nhiên sẽ an toàn hơn.",
                }
            )

        if set(issue_counts.keys()) <= {"length"} and issue_counts:
            recommendations.append(
                {
                    "type": "compaction",
                    "priority": "medium",
                    "message": "QA còn chủ yếu là length. Nên tăng naturalization/compact sentences thay vì vá từ đơn lẻ.",
                }
            )

        if runtime.get("translate_seconds", 0.0) > 20.0 and current_run.get("segments", 0) > 20:
            recommendations.append(
                {
                    "type": "runtime_batching",
                    "priority": "medium",
                    "message": "Translate time vẫn cao. Nên chạy batch trong cùng một process để tái sử dụng shared caches.",
                }
            )

        if previous_run and current_run["qa_total"] > previous_run.get("qa_total", current_run["qa_total"]):
            recommendations.append(
                {
                    "type": "regression_check",
                    "priority": "high",
                    "message": "QA tăng so với run trước. Nên kiểm tra lại rule mới hoặc profile override vừa được áp.",
                }
            )

        if reference and reference.get("word_similarity", 0.0) < 0.25:
            recommendations.append(
                {
                    "type": "reference_gap",
                    "priority": "medium",
                    "message": "Độ sát bản tham chiếu còn thấp. Nên ưu tiên phrase ranking hoặc template naturalization theo ngữ cảnh chương.",
                }
            )
        return recommendations

    def _auto_upgrade_config(
        self,
        *,
        project_path: Path,
        chapter_id: str | None,
        config: dict,
        current_run: dict,
    ) -> tuple[dict, list[dict]]:
        config_path = project_path / "working" / "config" / "translation_config.json"
        base_config = self._load_json(config_path, config or {})
        merged_config = json.loads(json.dumps(base_config or {}))
        auto_applied: list[dict] = []

        issue_counts = current_run.get("qa_issue_counts", {})
        profile = current_run.get("style_profile") or "balanced_novel"
        dialogue_ratio = float(current_run.get("dialogue_ratio", 0.0) or 0.0)
        naturalization = dict(current_run.get("naturalization") or {})
        manual_override = False
        if chapter_id:
            chapter_override = (
                (merged_config.get("style_preferences") or {})
                .get("chapter_overrides", {})
                .get(chapter_id, {})
            )
            manual_override = bool(chapter_override.get("style_profile"))

        if issue_counts.get("pronoun") and dialogue_ratio >= 0.35 and not manual_override and profile != "dialogue_natural":
            merged_config = self._apply_style_update(
                merged_config,
                chapter_id=chapter_id,
                style_profile="dialogue_natural",
                naturalization={"enabled": True},
            )
            auto_applied.append(
                {
                    "setting": "style_profile",
                    "chapter_id": chapter_id,
                    "old_value": profile,
                    "new_value": "dialogue_natural",
                    "reason": "pronoun_issues_with_dialogue_heavy_chapter",
                }
            )
            profile = "dialogue_natural"

        only_length = bool(issue_counts) and set(issue_counts.keys()) <= {"length"}
        if only_length and not manual_override and profile not in {"dialogue_natural", "modern_novel_adaptive"}:
            merged_config = self._apply_style_update(
                merged_config,
                chapter_id=chapter_id,
                style_profile="modern_novel_adaptive",
                naturalization={"enabled": True},
            )
            auto_applied.append(
                {
                    "setting": "style_profile",
                    "chapter_id": chapter_id,
                    "old_value": profile,
                    "new_value": "modern_novel_adaptive",
                    "reason": "length_only_issues_need_stronger_naturalization",
                }
            )
            profile = "modern_novel_adaptive"

        if only_length and profile == "modern_novel_adaptive" and not naturalization.get("compact_sentences", False):
            merged_config = self._apply_style_update(
                merged_config,
                chapter_id=chapter_id,
                style_profile=None,
                naturalization={"enabled": True, "compact_sentences": True},
            )
            auto_applied.append(
                {
                    "setting": "naturalization.compact_sentences",
                    "chapter_id": chapter_id,
                    "old_value": naturalization.get("compact_sentences", False),
                    "new_value": True,
                    "reason": "persistent_length_issues_under_novel_profile",
                }
            )

        if auto_applied:
            self._write_json(config_path, merged_config)
        return merged_config, auto_applied

    def _compare_with_reference(self, *, chapter_id: str | None, clean_text: str, config: dict) -> dict | None:
        if not chapter_id:
            return None
        metadata = config.get("external_project_metadata") or {}
        root_dir = metadata.get("root_dir")
        if not root_dir:
            return None
        output_dir = Path(root_dir) / "output"
        reference_path = self._find_reference_path(
            output_dir,
            chapter_id,
            source_basename=str(metadata.get("source_basename", "")).strip() or None,
        )
        if reference_path is None:
            return None
        reference_text = reference_path.read_text(encoding="utf-8")
        return {
            "path": str(reference_path),
            "char_similarity": round(SequenceMatcher(a=clean_text, b=reference_text).ratio(), 4),
            "word_similarity": round(SequenceMatcher(a=self._tokenize_words(clean_text), b=self._tokenize_words(reference_text)).ratio(), 4),
            "line_similarity": round(SequenceMatcher(a=clean_text.splitlines(), b=reference_text.splitlines()).ratio(), 4),
            "reference_chars": len(reference_text),
            "output_chars": len(clean_text),
        }

    @staticmethod
    def _find_reference_path(output_dir: Path, chapter_id: str, source_basename: str | None = None) -> Path | None:
        if not output_dir.exists():
            return None
        if source_basename:
            direct_source_match = output_dir / source_basename
            if direct_source_match.exists():
                return direct_source_match
        base_names = {
            chapter_id,
            chapter_id.replace("-", "_"),
            chapter_id.replace("_", "-"),
        }
        for base_name in sorted(base_names):
            for extension in (".md", ".txt"):
                candidate = output_dir / f"{base_name}{extension}"
                if candidate.exists():
                    return candidate
        return None

    @staticmethod
    def _looks_like_dialogue(text: str) -> bool:
        stripped = str(text or "").strip()
        return stripped.startswith(("\"", "'", "“", "”", "‘", "’"))

    @staticmethod
    def _tokenize_words(text: str) -> list[str]:
        return re.findall(r"\S+", text or "")

    @staticmethod
    def _should_promote_to_locked_entity(source: str, target: str, reason: str) -> bool:
        if not source or not target:
            return False
        if not all("\u4e00" <= char <= "\u9fff" for char in source):
            return False
        lowered_reason = reason.lower()
        if any(marker in lowered_reason for marker in ("person", "name", "location", "organization", "entity")):
            return True
        return bool(target[:1].isupper() and (" " in target or len(source) >= 2))

    @staticmethod
    def _infer_entity_type(reason: str) -> str:
        lowered = (reason or "").lower()
        if "location" in lowered or "street" in lowered or "road" in lowered:
            return "location"
        if "company" in lowered or "organization" in lowered or "org" in lowered:
            return "organization"
        return "project_term"

    def _apply_style_update(
        self,
        config: dict,
        *,
        chapter_id: str | None,
        style_profile: str | None,
        naturalization: dict | None,
    ) -> dict:
        updated = json.loads(json.dumps(config or {}))
        genre_hints = updated.get("genre_hints") or ["general"]
        style_preferences = updated.get("style_preferences") or default_style_preferences(
            genre_hints,
            updated.get("cultural_origin_hint"),
        )
        updated["style_preferences"] = style_preferences

        if chapter_id:
            chapter_overrides = dict(style_preferences.get("chapter_overrides") or {})
            chapter_config = dict(chapter_overrides.get(chapter_id) or {})
            if style_profile is not None and style_profile in STYLE_PROFILES:
                chapter_config["style_profile"] = style_profile
            if naturalization:
                chapter_config["naturalization"] = self._deep_merge(
                    chapter_config.get("naturalization") or {},
                    naturalization,
                )
            chapter_overrides[chapter_id] = chapter_config
            style_preferences["chapter_overrides"] = chapter_overrides
        else:
            if style_profile is not None and style_profile in STYLE_PROFILES:
                updated["style_profile"] = style_profile
                style_preferences["project_profile"] = style_profile
            if naturalization:
                updated["naturalization"] = self._deep_merge(
                    updated.get("naturalization") or {},
                    naturalization,
                )
        return updated

    @staticmethod
    def _merge_generated_items(existing_items: list[dict], generated_items: list[dict]) -> list[dict]:
        merged: dict[str, dict] = {}
        for item in existing_items:
            source = str(item.get("source", "")).strip()
            if not source:
                continue
            merged[source] = dict(item)
        for item in generated_items:
            source = str(item.get("source", "")).strip()
            if not source:
                continue
            merged[source] = dict(item)
        return [
            merged[source]
            for source in sorted(merged, key=lambda value: (-len(value), value))
        ]

    def _write_report(self, project_path: Path, chapter_id: str | None, report: dict):
        report_stem = f"learning_report_{chapter_id}" if chapter_id else "learning_report"
        reports_dir = project_path / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / f"{report_stem}.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        md_lines = [
            "# Learning Report",
            "",
            f"- Chapter: {chapter_id or '(project)'}",
            f"- Style profile: {report['current_run'].get('style_profile', 'unknown')}",
            f"- QA issues: {report['current_run'].get('qa_total', 0)}",
        ]
        reference = report["current_run"].get("reference_comparison") or {}
        if reference:
            md_lines.append(f"- Word similarity: {reference.get('word_similarity', 0.0):.4f}")
        md_lines.extend(
            [
                "",
                "## Auto Applied",
            ]
        )
        if report["auto_applied"]:
            for item in report["auto_applied"]:
                md_lines.append(
                    f"- {item['setting']}: {item['old_value']} -> {item['new_value']} ({item['reason']})"
                )
        else:
            md_lines.append("- No automatic config changes.")
        md_lines.extend(
            [
                "",
                "## Recommendations",
            ]
        )
        if report["recommendations"]:
            for item in report["recommendations"]:
                md_lines.append(f"- [{item['priority']}] {item['message']}")
        else:
            md_lines.append("- No recommendations.")
        (reports_dir / f"{report_stem}.md").write_text("\n".join(md_lines), encoding="utf-8")

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = ProjectLearningEngine._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    @staticmethod
    def _load_json(path: Path, default: object):
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(path: Path, payload: object):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
