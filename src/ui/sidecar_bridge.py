#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI sidecar bridge used by the desktop workflow."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.engine.rbmt_translator import RBMTTranslator, SegmentTranslation, TranslationResult
from src.engine.style_profiles import STYLE_PROFILES, default_style_preferences, resolve_style_selection
from src.learning.natural_feedback_engine import NaturalFeedbackEngine
from src.learning.project_learning_engine import ProjectLearningEngine
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline
from src.qa.report_generator import QAReportGenerator
from src.state.project_manager import ProjectManager
from src.ui.command_protocol import CommandEvent, CommandRequest, CommandResponse, PROTOCOL_VERSION


SUPPORTED_COMMANDS = {
    "create_project",
    "list_projects",
    "open_project",
    "get_project_overview",
    "set_active_chapter",
    "set_translation_style",
    "import_file",
    "translate",
    "load_translation_artifacts",
    "run_qa",
    "load_qa_report",
    "load_learning_report",
    "search_dictionary_entries",
    "list_candidate_entries",
    "review_candidate_entry",
    "submit_natural_feedback",
    "list_candidate_rules",
    "review_candidate_rule",
}


def handle_request(request: CommandRequest) -> CommandResponse:
    payload = request.payload
    command = request.command
    warnings: list[str] = []
    events = [
        _event(
            "received",
            f"Received `{command}` request",
            5,
            payload={"supported_commands": sorted(SUPPORTED_COMMANDS)},
        )
    ]

    if request.protocol_version != PROTOCOL_VERSION:
        warnings.append(
            f"Protocol mismatch: request={request.protocol_version}, sidecar={PROTOCOL_VERSION}"
        )

    try:
        if command == "create_project":
            manager = ProjectManager(payload.get("base_dir", "workspace_projects"))
            project = manager.create_project(
                payload["project_id"],
                source_language=payload.get("source_language", "zh"),
                target_language=payload.get("target_language", "vi"),
            )
            events.append(_event("project_created", f"Created project `{project.project_id}`", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project.project_id,
                    "project_dir": project.project_dir,
                    "project": project.to_dict(),
                    "overview": manager.get_project_overview(project.project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "list_projects":
            manager = ProjectManager(payload.get("base_dir", "workspace_projects"))
            events.append(_event("projects_loaded", "Loaded project index", 100))
            return CommandResponse.success(
                request,
                data={
                    "projects": [project.to_dict() for project in manager.list_projects()],
                    "supported_commands": sorted(SUPPORTED_COMMANDS),
                },
                warnings=warnings,
                events=events,
            )

        if command in {"open_project", "get_project_overview"}:
            manager, project_id, _ = _resolve_project(payload)
            events.append(_event("project_loaded", f"Loaded overview for `{project_id}`", 100))
            return CommandResponse.success(
                request,
                data=manager.get_project_overview(project_id),
                warnings=warnings,
                events=events,
            )

        if command == "set_active_chapter":
            manager, project_id, project_dir = _resolve_project(payload)
            chapter_id = str(payload["chapter_id"]).strip()
            if not chapter_id:
                raise ValueError("chapter_id is required")
            known_chapters = {
                item["chapter_id"]
                for item in _load_json(project_dir / "source" / "chapters" / "chapters_index.json", [])
            }
            if known_chapters and chapter_id not in known_chapters:
                raise ValueError(f"Unknown chapter_id: {chapter_id}")
            manager.set_active_chapter(project_id, chapter_id)
            events.append(_event("chapter_selected", f"Selected active chapter `{chapter_id}`", 100))
            return CommandResponse.success(
                request,
                data=manager.get_project_overview(project_id),
                warnings=warnings,
                events=events,
            )

        if command == "set_translation_style":
            manager, project_id, project_dir = _resolve_project(payload, create_if_missing=True)
            chapter_id = str(payload.get("chapter_id") or "").strip() or None
            style_profile = payload.get("style_profile")
            if style_profile is not None and style_profile not in STYLE_PROFILES:
                raise ValueError(f"Unknown style_profile: {style_profile}")

            config = _load_json(project_dir / "working" / "config" / "translation_config.json", {})
            config = _apply_style_preference_update(
                config,
                chapter_id=chapter_id,
                style_profile=style_profile,
                style_context=payload.get("style_context"),
                naturalization=payload.get("naturalization"),
            )
            _write_json(project_dir / "working" / "config" / "translation_config.json", config)

            effective_style = resolve_style_selection(config, chapter_id=chapter_id)
            manager.update_state(
                project_id,
                {
                    "style_profile": config.get("style_profile"),
                    "style_preferences": config.get("style_preferences", {}),
                },
            )
            events.append(_event("style_updated", "Updated translation style preferences", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "chapter_id": chapter_id,
                    "config": config,
                    "effective_style": effective_style,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "import_file":
            manager, project_id, project_dir = _resolve_project(payload, create_if_missing=True)
            pipeline = PreTranslationPipeline()
            try:
                events.append(_event("import_started", "Running pre-translation pipeline", 20))
                started_at = perf_counter()
                result = pipeline.prepare(payload["filepath"], project_dir)
                prepare_seconds = perf_counter() - started_at
            finally:
                pipeline.close()
            if result.chapters:
                manager.set_active_chapter(project_id, result.chapters[0].chapter_id)
            manager.record_runtime_stat(project_id, "prepare_seconds", prepare_seconds, result.chapters[0].chapter_id if result.chapters else "")
            manager.update_state(
                project_id,
                {
                    "last_import": {
                        "filepath": payload["filepath"],
                        "chapters": len(result.chapters),
                        "entities": len(result.entities),
                        "prepare_seconds": round(prepare_seconds, 4),
                    }
                },
            )
            events.append(_event("import_completed", "Project artifacts prepared", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "project_dir": str(project_dir),
                    "chapters": [asdict(chapter) for chapter in result.chapters],
                    "entities": result.entities,
                    "relationships": result.relationships,
                    "config": result.config,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "translate":
            manager, project_id, project_dir = _resolve_project(payload, create_if_missing=True)
            project = manager.open_project(project_id)
            chapter_id = payload.get("chapter_id") or project.active_chapter or _first_chapter_id(project_dir)
            if chapter_id:
                manager.set_active_chapter(project_id, chapter_id)
            source_text = payload.get("text") or _load_project_source_text(project_dir, chapter_id)
            if not source_text:
                raise ValueError("No source text available for translation")
            learning = ProjectLearningEngine()
            learning_sync = learning.sync_verified_candidates(
                project_dir=project_dir,
                manager=manager,
                project_id=project_id,
            )
            config = payload.get("config") or _load_json(
                project_dir / "working" / "config" / "translation_config.json",
                {},
            )
            config = _resolve_translation_config(project_dir, config, chapter_id)

            translator = RBMTTranslator(tm_db_path=project_dir / "state" / "tm.sqlite")
            try:
                events.append(_event("translation_started", "Running RBMT translation", 25))
                started_at = perf_counter()
                result = translator.translate_text(source_text, config=config)
                translate_seconds = perf_counter() - started_at
                artifact_stem = chapter_id or "translated"
                translator.export(result, project_dir, artifact_stem=artifact_stem)
                if artifact_stem != "translated":
                    translator.export(result, project_dir)
            finally:
                translator.close()

            candidate_ids: set[int] = set()
            for segment in result.segments:
                stored_segment_id = f"{chapter_id}:{segment.sentence_id}" if chapter_id else segment.sentence_id
                manager.record_segment(
                    project_id,
                    segment_id=stored_segment_id,
                    chapter_id=chapter_id or "",
                    source_text=segment.source_text,
                    target_text=segment.clean_text,
                    trace_json=segment.trace,
                    fallback_level=_segment_fallback_level(segment.trace),
                )
                for candidate in _collect_candidate_payloads(segment):
                    candidate_ids.add(
                        manager.add_candidate_entry(
                            project_id,
                            candidate["source_text"],
                            candidate["target_text"],
                            chapter_id=chapter_id or "",
                            segment_id=stored_segment_id,
                            fallback_level=candidate["fallback_level"],
                            candidates=candidate["candidates"],
                            reason=candidate["reason"],
                        )
                    )

            manager.record_runtime_stat(project_id, "segments_translated", len(result.segments), chapter_id or "")
            manager.record_runtime_stat(project_id, "candidate_entries_added", len(candidate_ids), chapter_id or "")
            manager.record_runtime_stat(project_id, "translate_seconds", translate_seconds, chapter_id or "")
            manager.record_runtime_stat(project_id, "source_chars", len(source_text), chapter_id or "")
            manager.record_runtime_stat(project_id, "output_chars", len(result.clean_text), chapter_id or "")
            manager.update_state(
                project_id,
                {
                    "last_translation": {
                        "chapter_id": chapter_id,
                        "segments": len(result.segments),
                        "candidate_entries_added": len(candidate_ids),
                        "translate_seconds": round(translate_seconds, 4),
                        "source_chars": len(source_text),
                        "output_chars": len(result.clean_text),
                    }
                },
            )
            events.append(_event("translation_completed", "Translation artifacts exported", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "project_dir": str(project_dir),
                    "chapter_id": chapter_id,
                    "clean_text": result.clean_text,
                    "draft_text": result.draft_text,
                    "segments": len(result.segments),
                    "candidate_entries_added": len(candidate_ids),
                    "translate_seconds": round(translate_seconds, 4),
                    "learning_sync": learning_sync,
                    "translation_artifacts": _load_translation_artifacts(manager, project_id, project_dir, chapter_id),
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "load_translation_artifacts":
            manager, project_id, project_dir = _resolve_project(payload)
            chapter_id = payload.get("chapter_id") or manager.open_project(project_id).active_chapter
            events.append(_event("artifacts_loaded", "Loaded translation artifacts", 100))
            return CommandResponse.success(
                request,
                data=_load_translation_artifacts(manager, project_id, project_dir, chapter_id),
                warnings=warnings,
                events=events,
            )

        if command == "run_qa":
            manager, project_id, project_dir = _resolve_project(payload)
            chapter_id = payload.get("chapter_id") or manager.open_project(project_id).active_chapter
            config = payload.get("config") or _load_json(
                project_dir / "working" / "config" / "translation_config.json",
                {},
            )
            config = _resolve_translation_config(project_dir, config, chapter_id)
            translation_result = _load_translation_result(
                payload.get("translation_result"),
                manager=manager,
                project_id=project_id,
                project_dir=project_dir,
                chapter_id=chapter_id,
                config=config,
            )
            source_text = payload.get("source_text") or _load_project_source_text(project_dir, chapter_id)
            if not source_text and translation_result.segments:
                source_text = "\n".join(segment.source_text for segment in translation_result.segments)

            generator = QAReportGenerator()
            events.append(_event("qa_started", "Running QA checks", 30))
            qa_started_at = perf_counter()
            report = generator.run(
                source_text=source_text,
                translation_result=translation_result,
                config=config,
            )
            qa_seconds = perf_counter() - qa_started_at
            report_stem = f"qa_report_{chapter_id}" if chapter_id else "qa_report"
            generator.write(report, project_dir, report_stem=report_stem)
            if report_stem != "qa_report":
                generator.write(report, project_dir)
            manager.record_runtime_stat(project_id, "qa_issues", report["summary"]["issues"], chapter_id or "")
            manager.record_runtime_stat(project_id, "qa_seconds", qa_seconds, chapter_id or "")
            state_payload = _load_json(project_dir / "state" / "project_state.json", {})
            last_translation = state_payload.get("last_translation", {})
            runtime_metrics = {"qa_seconds": qa_seconds}
            if last_translation.get("chapter_id") == chapter_id:
                for metric_name in ("translate_seconds", "source_chars", "output_chars"):
                    metric_value = last_translation.get(metric_name)
                    if isinstance(metric_value, (int, float)):
                        runtime_metrics[metric_name] = metric_value
            learning = ProjectLearningEngine()
            learning_report = learning.record_run(
                project_dir=project_dir,
                manager=manager,
                project_id=project_id,
                chapter_id=chapter_id,
                translation_result=translation_result,
                qa_report=report,
                config=config,
                runtime_metrics=runtime_metrics,
            )
            manager.update_state(
                project_id,
                {
                    "last_qa": {
                        "chapter_id": chapter_id,
                        "issues": report["summary"]["issues"],
                        "qa_seconds": round(qa_seconds, 4),
                    },
                    "last_learning": {
                        "chapter_id": chapter_id,
                        "auto_applied": learning_report["auto_applied"],
                        "recommendations": learning_report["recommendations"],
                    }
                },
            )
            events.append(_event("qa_completed", "QA reports written", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "chapter_id": chapter_id,
                    "report": report,
                    "qa_seconds": round(qa_seconds, 4),
                    "qa_report_path": str(_qa_report_paths(project_dir, chapter_id)["json"]),
                    "learning_report": learning_report,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "load_qa_report":
            manager, project_id, project_dir = _resolve_project(payload)
            chapter_id = payload.get("chapter_id") or manager.open_project(project_id).active_chapter
            report = _load_json(_qa_report_paths(project_dir, chapter_id)["json"], {
                "summary": {"issues": 0, "segments": 0},
                "issues": [],
            })
            events.append(_event("qa_loaded", "Loaded QA report", 100))
            return CommandResponse.success(
                request,
                data={"project_id": project_id, "chapter_id": chapter_id, "report": report},
                warnings=warnings,
                events=events,
            )

        if command == "load_learning_report":
            manager, project_id, project_dir = _resolve_project(payload)
            chapter_id = payload.get("chapter_id") or manager.open_project(project_id).active_chapter
            report = _load_json(_learning_report_paths(project_dir, chapter_id)["json"], {})
            events.append(_event("learning_loaded", "Loaded learning report", 100))
            return CommandResponse.success(
                request,
                data={"project_id": project_id, "chapter_id": chapter_id, "report": report},
                warnings=warnings,
                events=events,
            )

        if command == "search_dictionary_entries":
            query = str(payload.get("query", "")).strip()
            limit = int(payload.get("limit", 20))
            accessor = RuntimeDictionaryAccessor(payload.get("db_path"))
            try:
                records = accessor.search_entries(query, limit=limit)
                entries = [_serialize_dictionary_record(accessor, record) for record in records]
            finally:
                accessor.close()
            events.append(_event("dictionary_loaded", "Loaded dictionary entries", 100))
            return CommandResponse.success(
                request,
                data={
                    "query": query,
                    "entries": entries,
                },
                warnings=warnings,
                events=events,
            )

        if command == "list_candidate_entries":
            manager, project_id, _ = _resolve_project(payload)
            entries = manager.list_candidate_entries(project_id, status=payload.get("status"))
            events.append(_event("candidates_loaded", "Loaded candidate entries", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "entries": [entry.to_dict() for entry in entries],
                },
                warnings=warnings,
                events=events,
            )

        if command == "submit_natural_feedback":
            manager, project_id, project_dir = _resolve_project(payload)
            feedback_engine = NaturalFeedbackEngine()
            analysis = feedback_engine.analyze(
                feedback_text=str(payload.get("feedback_text") or "").strip(),
                source_text=str(payload.get("source_text") or "").strip(),
                current_translation=str(payload.get("current_translation") or "").strip(),
                preferred_translation=str(payload.get("preferred_translation") or "").strip(),
                chapter_id=str(payload.get("chapter_id") or "").strip() or None,
                scope=str(payload.get("scope") or "project"),
                rule_type_hint=str(payload.get("rule_type_hint") or "auto"),
                llm=payload.get("llm") if isinstance(payload.get("llm"), dict) else None,
            )
            created_rules = []
            for suggestion in analysis["suggestions"]:
                rule_id = manager.add_candidate_rule(
                    project_id,
                    suggestion["rule_type"],
                    suggestion,
                    status="candidate",
                )
                created_rules.append(rule_id)
            rules = manager.list_candidate_rules(project_id, status=payload.get("status"))
            events.append(_event("feedback_analyzed", "Generated candidate rules from natural-language feedback", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "analysis": analysis,
                    "created_rule_ids": created_rules,
                    "rules": [rule.to_dict() for rule in rules],
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "list_candidate_rules":
            manager, project_id, _ = _resolve_project(payload)
            rules = manager.list_candidate_rules(project_id, status=payload.get("status"))
            events.append(_event("rules_loaded", "Loaded candidate rules", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "rules": [rule.to_dict() for rule in rules],
                },
                warnings=warnings,
                events=events,
            )

        if command == "review_candidate_entry":
            manager, project_id, project_dir = _resolve_project(payload)
            entry = manager.review_candidate_entry(
                project_id,
                int(payload["candidate_id"]),
                payload["status"],
                payload.get("reason", ""),
            )
            learning_sync = ProjectLearningEngine().sync_verified_candidates(
                project_dir=project_dir,
                manager=manager,
                project_id=project_id,
            )
            events.append(_event("candidate_reviewed", "Candidate entry updated", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "entry": entry.to_dict() if entry else None,
                    "learning_sync": learning_sync,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "review_candidate_rule":
            manager, project_id, project_dir = _resolve_project(payload)
            rule = manager.review_candidate_rule(
                project_id,
                int(payload["rule_id"]),
                payload["status"],
                payload.get("reason", ""),
            )
            applied = None
            if rule and rule.status == "verified":
                applied = _apply_candidate_rule(
                    project_dir=project_dir,
                    chapter_id=str(payload.get("chapter_id") or "").strip() or None,
                    rule=rule.to_dict(),
                )
            events.append(_event("rule_reviewed", "Candidate rule updated", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "rule": rule.to_dict() if rule else None,
                    "applied": applied,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        return CommandResponse.failure(
            request,
            error=f"Unsupported command: {command}",
            warnings=warnings,
            events=events + [_event("failed", "Command is not supported by the sidecar", 100, level="error")],
        )
    except Exception as exc:
        error_msg = str(exc) or f"{type(exc).__name__}: {repr(exc)}"
        return CommandResponse.failure(
            request,
            error=error_msg,
            warnings=warnings,
            events=events + [_event("failed", error_msg, 100, level="error")],
        )


def _resolve_project(payload: dict, *, create_if_missing: bool = False) -> tuple[ProjectManager, str, Path]:
    if "project_dir" in payload:
        project_dir = Path(payload["project_dir"])
        manager = ProjectManager(project_dir.parent)
        project_id = payload.get("project_id", project_dir.name)
    else:
        manager = ProjectManager(payload.get("base_dir", "workspace_projects"))
        project_id = payload["project_id"]
        project_dir = manager.base_dir / project_id

    if create_if_missing:
        try:
            manager.open_project(project_id)
        except FileNotFoundError:
            manager.create_project(
                project_id,
                source_language=payload.get("source_language", "zh"),
                target_language=payload.get("target_language", "vi"),
            )

    return manager, project_id, project_dir


def _load_project_source_text(project_dir: Path, chapter_id: str | None) -> str:
    if chapter_id:
        chapter_path = project_dir / "source" / "chapters" / f"{chapter_id}.txt"
        if chapter_path.exists():
            return chapter_path.read_text(encoding="utf-8")

    raw_dir = project_dir / "source" / "raw"
    for raw_file in sorted(raw_dir.glob("*.txt")):
        return raw_file.read_text(encoding="utf-8")
    return ""


def _first_chapter_id(project_dir: Path) -> str | None:
    chapters = _load_json(project_dir / "source" / "chapters" / "chapters_index.json", [])
    if not chapters:
        return None
    return chapters[0]["chapter_id"]


def _resolve_translation_config(project_dir: Path, config: dict, chapter_id: str | None) -> dict:
    resolved = _merge_learned_terms(project_dir, config)
    if "style_preferences" not in resolved:
        resolved["style_preferences"] = default_style_preferences(
            resolved.get("genre_hints") or ["general"],
            resolved.get("cultural_origin_hint"),
        )
    style_selection = resolve_style_selection(resolved, chapter_id=chapter_id)
    resolved["active_chapter_id"] = chapter_id
    resolved["style_profile"] = style_selection["effective_profile"]
    resolved["style_context"] = style_selection["effective_context"]
    resolved["naturalization"] = style_selection["naturalization"]
    resolved["style_resolution"] = style_selection
    return resolved


def _merge_learned_terms(project_dir: Path, config: dict) -> dict:
    resolved = json.loads(json.dumps(config or {}))
    learned_terms = _load_json(project_dir / "working" / "config" / "learned_terms.json", {})
    if not learned_terms:
        return resolved

    locked_entities = {
        item["source"]: dict(item)
        for item in resolved.get("locked_entities", [])
        if item.get("source") and item.get("target")
    }
    for item in learned_terms.get("locked_entities", []):
        source = str(item.get("source", "")).strip()
        target = str(item.get("target", "")).strip()
        if not source or not target:
            continue
        locked_entities[source] = {
            "source": source,
            "target": target,
            "entity_type": item.get("entity_type", "project_term"),
        }
    if locked_entities:
        resolved["locked_entities"] = sorted(
            locked_entities.values(),
            key=lambda item: (-len(item["source"]), item["source"]),
        )

    project_phrase_overrides = {
        str(key).strip(): str(value).strip()
        for key, value in (resolved.get("project_phrase_overrides") or {}).items()
        if str(key).strip() and str(value).strip()
    }
    for item in learned_terms.get("phrase_overrides", []):
        source = str(item.get("source", "")).strip()
        target = str(item.get("target", "")).strip()
        if not source or not target:
            continue
        project_phrase_overrides[source] = target
    if project_phrase_overrides:
        resolved["project_phrase_overrides"] = project_phrase_overrides
    return resolved


def _apply_style_preference_update(
    config: dict,
    *,
    chapter_id: str | None,
    style_profile: str | None,
    style_context: dict | None,
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
        if style_profile is not None:
            chapter_config["style_profile"] = style_profile
            chapter_config["naturalization"] = _deep_merge(
                chapter_config.get("naturalization") or {},
                {"enabled": style_profile != "source_faithful"},
            )
        if style_context:
            chapter_config["style_context"] = _deep_merge(chapter_config.get("style_context") or {}, style_context)
        if naturalization:
            chapter_config["naturalization"] = _deep_merge(chapter_config.get("naturalization") or {}, naturalization)
        chapter_overrides[chapter_id] = chapter_config
        style_preferences["chapter_overrides"] = chapter_overrides
    else:
        if style_profile is not None:
            updated["style_profile"] = style_profile
            style_preferences["project_profile"] = style_profile
            updated["naturalization"] = _deep_merge(
                updated.get("naturalization") or {},
                {"enabled": style_profile != "source_faithful"},
            )
        if style_context:
            updated["style_context"] = _deep_merge(updated.get("style_context") or {}, style_context)
            style_preferences["project_context"] = _deep_merge(style_preferences.get("project_context") or {}, style_context)
        if naturalization:
            updated["naturalization"] = _deep_merge(updated.get("naturalization") or {}, naturalization)
    return updated


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _segment_fallback_level(traces: list[dict]) -> str:
    severity_order = (
        "unresolved",
        "ambiguous",
        "reading_fallback",
        "tm_fuzzy",
        "tm_exact",
        "project_entity",
        "function_map",
        "pronoun",
        "number",
        "runtime",
    )
    observed = {trace.get("fallback_level") for trace in traces}
    for level in severity_order:
        if level in observed:
            return level
    return "runtime"


def _collect_candidate_payloads(segment: SegmentTranslation) -> list[dict]:
    payloads: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for trace in segment.trace:
        fallback_level = trace.get("fallback_level")
        if fallback_level not in {"ambiguous", "unresolved"}:
            continue
        source_text = str(trace.get("source", "")).strip()
        if not source_text:
            continue
        target_text = str(trace.get("selected") or source_text).strip() or source_text
        key = (source_text, target_text, fallback_level)
        if key in seen:
            continue
        seen.add(key)
        payloads.append({
            "source_text": source_text,
            "target_text": target_text,
            "fallback_level": fallback_level,
            "candidates": [str(item) for item in trace.get("candidates") or [target_text]],
            "reason": str(trace.get("reason", "")),
        })
    return payloads


def _serialize_dictionary_record(accessor: RuntimeDictionaryAccessor, record) -> dict:
    readings = accessor.get_entry_readings(record.source)
    pinyin = [item.pinyin for item in readings if item.pinyin]
    han_viet = [item.han_viet_readings for item in readings if item.han_viet_readings]
    metadata = record.metadata or {}
    status = "locked" if record.locked else (record.entry_role or "runtime")
    return {
        "source": record.source,
        "target_vi": record.target,
        "alternative_meanings": record.alternatives[1:],
        "full_explanation": metadata.get("full_explanation") or record.notes,
        "source_dict": record.category,
        "priority": record.priority,
        "status": status,
        "hit_count": int(metadata.get("hit_count", 0) or 0),
        "pinyin": pinyin or ([metadata.get("pinyin")] if metadata.get("pinyin") else []),
        "han_viet_readings": han_viet or ([metadata.get("han_viet_readings")] if metadata.get("han_viet_readings") else []),
        "entry_role": record.entry_role,
        "source_language": record.source_language,
        "target_language": record.target_language,
        "one_mean": record.one_mean,
        "locked": record.locked,
        "notes": record.notes,
    }


def _translation_paths(project_dir: Path, chapter_id: str | None) -> dict[str, Path]:
    if chapter_id:
        specific = {
            "clean": project_dir / "output" / f"{chapter_id}.txt",
            "draft": project_dir / "drafts" / f"{chapter_id}_draft.txt",
            "trace": project_dir / "drafts" / f"{chapter_id}_trace.json",
        }
        if specific["clean"].exists() or specific["trace"].exists():
            return specific
    return {
        "clean": project_dir / "output" / "translated.txt",
        "draft": project_dir / "drafts" / "translated_draft.txt",
        "trace": project_dir / "drafts" / "translation_trace.json",
    }


def _qa_report_paths(project_dir: Path, chapter_id: str | None) -> dict[str, Path]:
    if chapter_id:
        specific = {
            "md": project_dir / "reports" / f"qa_report_{chapter_id}.md",
            "json": project_dir / "reports" / f"qa_report_{chapter_id}.json",
        }
        if specific["json"].exists():
            return specific
    return {
        "md": project_dir / "reports" / "qa_report.md",
        "json": project_dir / "reports" / "qa_report.json",
    }


def _learning_report_paths(project_dir: Path, chapter_id: str | None) -> dict[str, Path]:
    if chapter_id:
        specific = {
            "md": project_dir / "reports" / f"learning_report_{chapter_id}.md",
            "json": project_dir / "reports" / f"learning_report_{chapter_id}.json",
        }
        if specific["json"].exists():
            return specific
    return {
        "md": project_dir / "reports" / "learning_report.md",
        "json": project_dir / "reports" / "learning_report.json",
    }


def _apply_candidate_rule(project_dir: Path, chapter_id: str | None, rule: dict) -> dict:
    rule_type = str(rule.get("rule_type") or "").strip()
    payload = dict(rule.get("rule_payload") or {})
    scope = str(payload.get("scope") or "project").strip()
    effective_chapter_id = str(payload.get("chapter_id") or chapter_id or "").strip() or None
    suggestion_payload = dict(payload.get("payload") or {})

    config_path = project_dir / "working" / "config" / "translation_config.json"
    config = _load_json(config_path, {})
    learned_terms_path = project_dir / "working" / "config" / "learned_terms.json"
    learned_terms = _load_json(learned_terms_path, {})
    applied_changes: dict[str, object] = {
        "rule_type": rule_type,
        "scope": scope,
        "chapter_id": effective_chapter_id,
        "config_path": str(config_path),
        "learned_terms_path": str(learned_terms_path),
    }

    if rule_type in {"phrase_override", "locked_entity"}:
        if rule_type == "phrase_override":
            phrase_overrides = list(learned_terms.get("phrase_overrides", []))
            phrase_overrides = _upsert_item(
                phrase_overrides,
                {
                    "source": str(suggestion_payload.get("source") or "").strip(),
                    "target": str(suggestion_payload.get("target") or "").strip(),
                    "origin": "candidate_rule",
                    "chapter_id": effective_chapter_id or "",
                },
                key_fields=("source",),
            )
            learned_terms["phrase_overrides"] = phrase_overrides
        else:
            locked_entities = list(learned_terms.get("locked_entities", []))
            locked_entities = _upsert_item(
                locked_entities,
                {
                    "source": str(suggestion_payload.get("source") or "").strip(),
                    "target": str(suggestion_payload.get("target") or "").strip(),
                    "entity_type": str(suggestion_payload.get("entity_type") or "project_term"),
                    "origin": "candidate_rule",
                },
                key_fields=("source",),
            )
            learned_terms["locked_entities"] = locked_entities
        learned_terms["generated_at"] = payload.get("generated_at") or learned_terms.get("generated_at") or ""
        _write_json(learned_terms_path, learned_terms)
        applied_changes["updated"] = "learned_terms"
        applied_changes["effective_config"] = _resolve_translation_config(
            project_dir,
            config,
            effective_chapter_id if scope == "chapter" else None,
        )
        return applied_changes

    if rule_type == "style_profile":
        config = _apply_style_preference_update(
            config,
            chapter_id=effective_chapter_id if scope == "chapter" else None,
            style_profile=str(suggestion_payload.get("style_profile") or "").strip() or None,
            style_context=None,
            naturalization=None,
        )
    elif rule_type == "style_context":
        config = _apply_style_preference_update(
            config,
            chapter_id=effective_chapter_id if scope == "chapter" else None,
            style_profile=None,
            style_context=suggestion_payload.get("style_context") if isinstance(suggestion_payload.get("style_context"), dict) else None,
            naturalization=None,
        )
    elif rule_type == "naturalization":
        config = _apply_style_preference_update(
            config,
            chapter_id=effective_chapter_id if scope == "chapter" else None,
            style_profile=None,
            style_context=None,
            naturalization=suggestion_payload.get("naturalization") if isinstance(suggestion_payload.get("naturalization"), dict) else None,
        )
    elif rule_type == "style_guidance":
        guidance = list(config.get("style_guidance") or [])
        guidance = _upsert_item(
            guidance,
            {
                "guidance": str(suggestion_payload.get("guidance") or "").strip(),
                "source_text": str(suggestion_payload.get("source_text") or "").strip(),
                "current_translation": str(suggestion_payload.get("current_translation") or "").strip(),
                "preferred_translation": str(suggestion_payload.get("preferred_translation") or "").strip(),
                "scope": scope,
                "chapter_id": effective_chapter_id or "",
            },
            key_fields=("guidance", "scope", "chapter_id"),
        )
        config["style_guidance"] = guidance

    _write_json(config_path, config)
    applied_changes["updated"] = "translation_config"
    applied_changes["effective_config"] = _resolve_translation_config(
        project_dir,
        config,
        effective_chapter_id if scope == "chapter" else None,
    )
    return applied_changes


def _upsert_item(items: list[dict], new_item: dict, *, key_fields: tuple[str, ...]) -> list[dict]:
    normalized = [dict(item) for item in items if isinstance(item, dict)]
    new_key = tuple(str(new_item.get(field) or "").strip() for field in key_fields)
    if not any(new_key):
        return normalized
    updated: list[dict] = []
    replaced = False
    for item in normalized:
        item_key = tuple(str(item.get(field) or "").strip() for field in key_fields)
        if item_key == new_key:
            merged = dict(item)
            merged.update(new_item)
            updated.append(merged)
            replaced = True
        else:
            updated.append(item)
    if not replaced:
        updated.append(new_item)
    return updated


def _load_translation_artifacts(
    manager: ProjectManager,
    project_id: str,
    project_dir: Path,
    chapter_id: str | None,
) -> dict:
    paths = _translation_paths(project_dir, chapter_id)
    trace_payload = _load_json(paths["trace"], [])
    segments = trace_payload or [
        {
            "sentence_id": segment.segment_id,
            "source_text": segment.source_text,
            "clean_text": segment.target_text,
            "draft_text": segment.target_text,
            "emotion": None,
            "trace": segment.trace,
            "fallback_level": segment.fallback_level,
        }
        for segment in manager.list_segments(project_id, chapter_id=chapter_id)
    ]
    return {
        "project_id": project_id,
        "chapter_id": chapter_id,
        "clean_text": _read_text_if_exists(paths["clean"]),
        "draft_text": _read_text_if_exists(paths["draft"]),
        "segments": segments,
        "paths": {name: str(path) for name, path in paths.items()},
    }


def _load_translation_result(
    payload: dict | None,
    *,
    manager: ProjectManager,
    project_id: str,
    project_dir: Path,
    chapter_id: str | None,
    config: dict,
) -> TranslationResult:
    if payload:
        return _translation_result_from_payload(payload)

    artifacts = _load_translation_artifacts(manager, project_id, project_dir, chapter_id)
    segments: list[SegmentTranslation] = []
    for segment in artifacts["segments"]:
        segments.append(
            SegmentTranslation(
                sentence_id=segment.get("sentence_id") or segment.get("segment_id", ""),
                source_text=segment["source_text"],
                clean_text=segment["clean_text"],
                draft_text=segment.get("draft_text", segment["clean_text"]),
                emotion=segment.get("emotion"),
                trace=segment.get("trace", []),
            )
        )
    return TranslationResult(
        clean_text=artifacts["clean_text"],
        draft_text=artifacts["draft_text"],
        segments=segments,
        config=config,
    )


def _translation_result_from_payload(payload: dict) -> TranslationResult:
    segments = [SegmentTranslation(**segment) for segment in payload["segments"]]
    return TranslationResult(
        clean_text=payload["clean_text"],
        draft_text=payload["draft_text"],
        segments=segments,
        config=payload.get("config", {}),
    )


def _read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path, default: object):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _event(stage: str, message: str, progress: int, *, level: str = "info", payload: dict | None = None) -> CommandEvent:
    return CommandEvent(stage=stage, message=message, progress=progress, level=level, payload=payload or {})


def main():
    parser = argparse.ArgumentParser(description="Desktop sidecar bridge")
    parser.add_argument("--request-json", required=True, help="JSON encoded CommandRequest")
    args = parser.parse_args()
    request = CommandRequest(**json.loads(args.request_json))
    response = handle_request(request)
    print(json.dumps(response.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
