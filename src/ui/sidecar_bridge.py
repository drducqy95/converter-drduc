#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI sidecar bridge used by the desktop workflow."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from src.core.md_dictionary_compiler import DictionaryCompiler
from src.core.runtime_support import RuntimeDictionaryAccessor
from src.engine.rbmt_translator import RBMTTranslator, SegmentTranslation, TranslationResult
from src.engine.style_profiles import STYLE_PROFILES, default_style_preferences, resolve_style_selection
from src.learning.grammar_pattern_scanner import GrammarLearningPatternScanner, write_grammar_learning_report
from src.learning.natural_feedback_engine import NaturalFeedbackEngine
from src.learning.project_learning_engine import ProjectLearningEngine
from src.pipeline.name_reading import HanVietNameResolver
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline
from src.qa.report_generator import QAReportGenerator
from src.state.project_manager import ProjectManager
from src.tools.pos_seeder import POSSeeder
from src.tools.source_file_rewriter import resolve_dictionary_source_path, update_dictionary_source_entry
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
    "update_project_translation_config",
    "upsert_project_entity",
    "delete_project_entity",
    "delete_project_entities",
    "suggest_entity_targets",
    "search_dictionary_entries",
    "list_dictionary_entries",
    "update_dictionary_entry",
    "get_pipeline_status",
    "run_pipeline_stage",
    "list_candidate_entries",
    "review_candidate_entry",
    "submit_natural_feedback",
    "scan_grammar_learning_patterns",
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
            filepath = str(_normalize_path(str(payload["filepath"])))
            try:
                events.append(_event("import_started", "Running pre-translation pipeline", 20))
                started_at = perf_counter()
                result = pipeline.prepare(filepath, project_dir)
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
                        "filepath": filepath,
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

        if command == "update_project_translation_config":
            manager, project_id, project_dir = _resolve_project(payload)
            incoming_config = payload.get("config")
            if not isinstance(incoming_config, dict):
                raise ValueError("config must be an object")
            config_path = project_dir / "working" / "config" / "translation_config.json"
            _write_json(config_path, incoming_config)
            events.append(_event("config_updated", "Saved project translation config", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "config": incoming_config,
                    "config_path": str(config_path),
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "upsert_project_entity":
            manager, project_id, project_dir = _resolve_project(payload)
            entity_payload = payload.get("entity")
            if not isinstance(entity_payload, dict):
                raise ValueError("entity must be an object")
            entity = _normalize_project_entity(entity_payload)
            if not entity["source"]:
                raise ValueError("entity.source is required")
            if entity["entity_type"] != "junk_phrase" and not entity["target"]:
                raise ValueError("entity.target is required")
            sync_locked = bool(payload.get("sync_locked", True))
            result = _upsert_project_entity(project_dir, entity, sync_locked=sync_locked)
            events.append(_event("entity_updated", "Saved project entity override", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    **result,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "delete_project_entity":
            manager, project_id, project_dir = _resolve_project(payload)
            source = str(payload.get("source") or "").strip()
            if not source:
                raise ValueError("source is required")
            sync_locked = bool(payload.get("sync_locked", True))
            result = _delete_project_entity(project_dir, source, sync_locked=sync_locked)
            events.append(_event("entity_deleted", "Deleted project entity override", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    **result,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "delete_project_entities":
            manager, project_id, project_dir = _resolve_project(payload)
            sources_payload = payload.get("sources")
            if not isinstance(sources_payload, list):
                raise ValueError("sources must be a list")
            sources = [str(item or "").strip() for item in sources_payload]
            sources = [item for item in sources if item]
            if not sources:
                raise ValueError("sources must contain at least one entity source")
            sync_locked = bool(payload.get("sync_locked", True))
            result = _delete_project_entities(project_dir, sources, sync_locked=sync_locked)
            events.append(_event("entities_deleted", "Deleted project entity overrides", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    **result,
                    "overview": manager.get_project_overview(project_id),
                },
                warnings=warnings,
                events=events,
            )

        if command == "suggest_entity_targets":
            source = str(payload.get("source") or "").strip()
            if not source:
                raise ValueError("source is required")
            project_id = str(payload.get("project_id") or payload.get("project_name") or "").strip()
            project_dir = None
            if payload.get("project_dir"):
                project_dir = Path(str(payload.get("project_dir")))
            accessor = RuntimeDictionaryAccessor(_resolve_db_path(payload, allow_missing=False))
            try:
                suggestions = _build_entity_target_suggestions(
                    accessor,
                    source,
                    project_id=project_id or None,
                    project_dir=project_dir,
                )
            finally:
                accessor.close()
            events.append(_event("entity_targets_suggested", "Generated entity target suggestions", 100))
            return CommandResponse.success(
                request,
                data={
                    "source": source,
                    "suggestions": suggestions,
                },
                warnings=warnings,
                events=events,
            )

        if command == "get_pipeline_status":
            pipeline_status = _build_pipeline_status(payload)
            events.append(_event("pipeline_loaded", "Loaded pipeline status", 100))
            return CommandResponse.success(
                request,
                data=pipeline_status,
                warnings=warnings,
                events=events,
            )

        if command == "run_pipeline_stage":
            stage = str(payload.get("stage") or "").strip()
            if not stage:
                raise ValueError("stage is required")

            if stage in {"import", "translate", "qa"}:
                nested_command = {
                    "import": "import_file",
                    "translate": "translate",
                    "qa": "run_qa",
                }[stage]
                nested_payload = dict(payload)
                nested_payload.pop("stage", None)
                nested_response = handle_request(
                    CommandRequest(
                        command=nested_command,
                        payload=nested_payload,
                        request_id=request.request_id,
                        protocol_version=request.protocol_version,
                    )
                )
                pipeline_status = _build_pipeline_status(payload)
                return CommandResponse.success(
                    request,
                    data={
                        "stage": stage,
                        "stage_result": nested_response.data if nested_response.ok else {},
                        "pipeline": pipeline_status,
                    },
                    warnings=warnings + list(nested_response.warnings),
                    events=nested_response.events,
                ) if nested_response.ok else CommandResponse.failure(
                    request,
                    error=nested_response.error,
                    warnings=warnings + list(nested_response.warnings),
                    events=nested_response.events,
                )

            if stage == "compile":
                dict_root = _resolve_dict_root(payload)
                db_path = _resolve_db_path(payload, dict_root=dict_root)
                compiled_dir = db_path.parent
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                    compiler = DictionaryCompiler(str(dict_root), str(compiled_dir))
                    compile_stats = compiler.compile(project_name=payload.get("project_name"))
                output = capture.getvalue().strip()
                if output:
                    warnings.append(output)
                events.append(_event("compile_completed", "Compiled dictionary database", 100))
                return CommandResponse.success(
                    request,
                    data={
                        "stage": stage,
                        "stats": compile_stats,
                        "db_path": str(db_path),
                        "dict_root": str(dict_root),
                        "pipeline": _build_pipeline_status(payload),
                    },
                    warnings=warnings,
                    events=events,
                )

            if stage == "assign_pos":
                db_path = _resolve_db_path(payload)
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                    POSSeeder(str(db_path)).seed()
                output = capture.getvalue().strip()
                if output:
                    warnings.append(output)
                events.append(_event("pos_completed", "Seeded POS and metadata", 100))
                return CommandResponse.success(
                    request,
                    data={
                        "stage": stage,
                        "db_path": str(db_path),
                        "pipeline": _build_pipeline_status(payload),
                    },
                    warnings=warnings,
                    events=events,
                )

            if stage == "export":
                events.append(_event("export_verified", "Verified export artifacts", 100))
                return CommandResponse.success(
                    request,
                    data={
                        "stage": stage,
                        "pipeline": _build_pipeline_status(payload),
                    },
                    warnings=warnings,
                    events=events,
                )

            raise ValueError(f"Unsupported pipeline stage: {stage}")

        if command == "search_dictionary_entries":
            query = str(payload.get("query", "")).strip()
            limit = int(payload.get("limit", 20))
            accessor = RuntimeDictionaryAccessor(_resolve_db_path(payload, allow_missing=False))
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

        if command == "list_dictionary_entries":
            accessor = RuntimeDictionaryAccessor(_resolve_db_path(payload, allow_missing=False))
            try:
                page = max(1, int(payload.get("page", 1)))
                page_size = max(1, min(200, int(payload.get("page_size", 50))))
                offset = (page - 1) * page_size
                records, total = accessor.list_entries(
                    query=str(payload.get("query", "")).strip(),
                    source_dict=str(payload.get("source_dict", "")).strip() or None,
                    pos_tag=str(payload.get("pos_tag", "")).strip() or None,
                    entity_type=str(payload.get("entity_type", "")).strip() or None,
                    table_name=str(payload.get("table_name", "")).strip() or None,
                    limit=page_size,
                    offset=offset,
                )
                entries = [_serialize_dictionary_record(accessor, record) for record in records]
                filters = accessor.get_filter_values()
                stats = accessor.get_dictionary_stats()
            finally:
                accessor.close()
            events.append(_event("dictionary_list_loaded", "Loaded paginated dictionary entries", 100))
            return CommandResponse.success(
                request,
                data={
                    "entries": entries,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "filters": filters,
                    "stats": stats,
                },
                warnings=warnings,
                events=events,
            )

        if command == "update_dictionary_entry":
            accessor = RuntimeDictionaryAccessor(_resolve_db_path(payload, allow_missing=False))
            try:
                table_name = str(payload.get("table_name") or "").strip()
                record_id = int(payload.get("record_id") or 0)
                if not table_name or record_id <= 0:
                    raise ValueError("table_name and record_id are required")

                current = accessor.get_record(table_name, record_id)
                if current is None:
                    raise ValueError(f"Dictionary record not found: {table_name}:{record_id}")

                metadata = _merge_dictionary_metadata(current.metadata, payload.get("metadata"))
                if "full_explanation" in payload:
                    metadata["full_explanation"] = str(payload.get("full_explanation") or "").strip()
                if "hit_count" in payload:
                    metadata["hit_count"] = int(payload.get("hit_count") or 0)
                if "han_viet_readings" in payload:
                    metadata["han_viet_readings"] = str(payload.get("han_viet_readings") or "").strip()

                sqlite_updates = {
                    "source": _coalesce_update(payload, "source"),
                    "target": _coalesce_update(payload, "target_vi"),
                    "priority": payload.get("priority"),
                    "notes": _coalesce_update(payload, "notes"),
                    "locked": int(bool(payload.get("locked"))) if "locked" in payload else None,
                    "metadata_json": json.dumps(
                        {key: value for key, value in metadata.items() if value not in (None, "", [])},
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                    "pos_tag": _coalesce_update(payload, "pos_tag"),
                    "pos_sub": _coalesce_update(payload, "pos_sub"),
                    "entity_type": _coalesce_update(payload, "entity_type"),
                    "pinyin": _coalesce_update(payload, "pinyin"),
                    "traditional": _coalesce_update(payload, "traditional"),
                    "luat_nhan_trigger": int(bool(payload.get("luat_nhan_trigger"))) if "luat_nhan_trigger" in payload else None,
                    "reorder_role": _coalesce_update(payload, "reorder_role"),
                    "cultural_origin": _coalesce_update(payload, "cultural_origin"),
                    "genre_affinity": _coalesce_update(payload, "genre_affinity"),
                    "register_level": _coalesce_update(payload, "register_level"),
                }
                provided_keys = set(payload.keys())
                sqlite_updates = {
                    key: value
                    for key, value in sqlite_updates.items()
                    if value is not None or (
                        {
                            "source": "source",
                            "target": "target_vi",
                            "notes": "notes",
                            "pos_tag": "pos_tag",
                            "pos_sub": "pos_sub",
                            "entity_type": "entity_type",
                            "pinyin": "pinyin",
                            "traditional": "traditional",
                            "reorder_role": "reorder_role",
                            "cultural_origin": "cultural_origin",
                            "genre_affinity": "genre_affinity",
                            "register_level": "register_level",
                        }.get(key) in provided_keys
                    )
                }

                updated = accessor.update_entry(table_name, record_id, sqlite_updates)
                updated_entry = _serialize_dictionary_record(accessor, updated)
                source_path = update_dictionary_source_entry(
                    dict_root=_resolve_dict_root(payload, accessor=accessor),
                    source_file=current.source_file,
                    source_text=current.source,
                    entry=updated_entry,
                )
            finally:
                accessor.close()
            if source_path is None:
                warnings.append("Updated SQLite entry but could not resolve the backing Markdown file path.")
            events.append(_event("dictionary_updated", "Updated dictionary entry", 100))
            return CommandResponse.success(
                request,
                data={
                    "entry": updated_entry,
                    "source_path": str(source_path) if source_path else "",
                    "pipeline": _build_pipeline_status(payload),
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

        if command == "scan_grammar_learning_patterns":
            manager, project_id, project_dir = _resolve_project(payload)
            input_paths = payload.get("paths")
            if isinstance(input_paths, list):
                scan_paths = [str(item) for item in input_paths if str(item).strip()]
            else:
                scan_path = (
                    str(payload.get("filepath") or payload.get("input_path") or "").strip()
                    or str(project_dir / "source" / "chapters")
                )
                scan_paths = [scan_path]
            if not scan_paths:
                raise ValueError("paths, filepath, or input_path is required")

            scanner = GrammarLearningPatternScanner()
            events.append(_event("grammar_scan_started", "Scanning source grammar patterns for coach learning", 20))
            report = scanner.analyze_paths(
                scan_paths,
                unknown_min_count=int(payload.get("unknown_min_count") or 5),
                max_files=int(payload["max_files"]) if payload.get("max_files") not in (None, "") else None,
                max_bytes_per_file=int(payload["max_bytes_per_file"]) if payload.get("max_bytes_per_file") not in (None, "") else None,
                max_sentences=int(payload["max_sentences"]) if payload.get("max_sentences") not in (None, "") else None,
                candidate_limit=int(payload.get("candidate_limit") or 200),
                include_name_scan=str(payload.get("include_name_scan", "true")).lower() not in {"0", "false", "no", "off"},
                name_min_count=int(payload.get("name_min_count") or 2),
                name_candidate_limit=int(payload.get("name_candidate_limit") or 200),
            )
            out_dir = Path(str(payload.get("out_dir") or project_dir / "reports" / "grammar_learning"))
            report_paths = write_grammar_learning_report(report, out_dir)

            created_rules = []
            if bool(payload.get("enqueue_candidates", True)):
                max_candidate_rules = int(payload.get("max_candidate_rules") or 50)
                for candidate in report.get("unknown_candidates", [])[:max_candidate_rules]:
                    rule_payload = _grammar_candidate_to_rule_payload(
                        candidate,
                        report_paths=report_paths,
                        scope=str(payload.get("scope") or "project"),
                    )
                    rule_id = manager.add_candidate_rule(
                        project_id,
                        "grammar_pattern_candidate",
                        rule_payload,
                        status="candidate",
                    )
                    created_rules.append(rule_id)

            rules = manager.list_candidate_rules(project_id, status=payload.get("status"))
            manager.update_state(
                project_id,
                {
                    "last_grammar_learning_scan": {
                        "summary": report.get("summary", {}),
                        "report_paths": report_paths,
                        "created_rule_ids": created_rules,
                    }
                },
            )
            events.append(_event("grammar_scan_completed", "Grammar learning scan report generated", 100))
            return CommandResponse.success(
                request,
                data={
                    "project_id": project_id,
                    "report": report,
                    "report_paths": report_paths,
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


def _normalize_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def _resolve_db_path(payload: dict, *, dict_root: Path | None = None, allow_missing: bool = True) -> Path:
    if payload.get("db_path"):
        db_path = _normalize_path(str(payload["db_path"]))
    else:
        root = dict_root or _resolve_dict_root(payload)
        db_path = root / "_compiled" / "trie_cache.db"
    if not allow_missing and not db_path.exists():
        raise FileNotFoundError(f"Compiled dictionary DB not found: {db_path}")
    return db_path


def _resolve_dict_root(payload: dict, accessor: RuntimeDictionaryAccessor | None = None) -> Path:
    if payload.get("dict_root"):
        return _normalize_path(str(payload["dict_root"]))
    if accessor is not None:
        return accessor.dict_root
    db_path = payload.get("db_path")
    if db_path:
        resolved = _normalize_path(str(db_path))
        if resolved.parent.name == "_compiled":
            return resolved.parent.parent
    return (Path(__file__).resolve().parents[2] / "data" / "dictionaries").resolve()


def _resolve_project(payload: dict, *, create_if_missing: bool = False) -> tuple[ProjectManager, str, Path]:
    if "project_dir" in payload:
        project_dir = _normalize_path(str(payload["project_dir"]))
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

    ignored_phrases = [
        normalized_item
        for normalized_item in (_normalize_junk_phrase_entry(item) for item in resolved.get("ignored_phrases", []))
        if normalized_item
    ]
    for item in learned_terms.get("ignored_phrases", []):
        normalized_item = _normalize_junk_phrase_entry(item)
        if normalized_item:
            ignored_phrases = _upsert_item(ignored_phrases, normalized_item, key_fields=("source", "target"))
    if ignored_phrases:
        resolved["ignored_phrases"] = ignored_phrases
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
    source_path = ""
    if record.source_file:
        source_path = str(
            _resolve_dictionary_source_path_for_record(
                accessor=accessor,
                record=record,
            )
            or ""
        )
    return {
        "record_id": f"{record.table_name}:{record.record_id}" if record.record_id else "",
        "row_id": record.record_id,
        "table_name": record.table_name,
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
        "source_file": record.source_file,
        "source_path": source_path,
        "pos_tag": record.pos_tag,
        "pos_sub": record.pos_sub,
        "entity_type": record.entity_type,
        "traditional": record.traditional or "",
        "is_function_word": bool(record.is_function_word),
        "luat_nhan_trigger": bool(record.luat_nhan_trigger),
        "reorder_role": record.reorder_role,
        "cultural_origin": record.cultural_origin,
        "genre_affinity": record.genre_affinity,
        "register_level": record.register_level,
        "metadata": metadata,
    }


def _resolve_dictionary_source_path_for_record(
    *,
    accessor: RuntimeDictionaryAccessor,
    record,
) -> Path | None:
    if not record.source_file:
        return None
    return resolve_dictionary_source_path(
        record.source_file,
        dict_root=_resolve_dict_root({}, accessor=accessor),
        category=record.category,
    )


def _merge_dictionary_metadata(existing: dict, incoming: object) -> dict:
    merged = dict(existing or {})
    if isinstance(incoming, dict):
        for key, value in incoming.items():
            if value in (None, "", []):
                merged.pop(key, None)
            else:
                merged[key] = value
    return merged


def _coalesce_update(payload: dict, key: str) -> str | None:
    if key not in payload:
        return None
    value = payload.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _build_pipeline_status(payload: dict) -> dict:
    dict_root = _resolve_dict_root(payload)
    db_path = _resolve_db_path(payload, dict_root=dict_root, allow_missing=True)
    dictionary_stats: dict[str, object] = {
        "runtime_total": 0,
        "reference_total": 0,
        "total": 0,
        "pos_total": 0,
        "pinyin_total": 0,
        "entity_total": 0,
        "pos_coverage_pct": 0.0,
        "pinyin_coverage_pct": 0.0,
        "compiled_at": None,
        "entry_readings_total": 0,
        "metadata": {},
    }
    if db_path.exists():
        accessor = RuntimeDictionaryAccessor(db_path)
        try:
            dictionary_stats = accessor.get_dictionary_stats()
        finally:
            accessor.close()
    try:
        compiler = DictionaryCompiler(str(dict_root), str(db_path.parent))
        cache_status = compiler.source_cache_status(project_name=payload.get("project_name"))
    except Exception as exc:
        cache_status = {
            "stale": not db_path.exists(),
            "reason": f"source_status_error:{exc}",
            "cached_hash": "",
            "current_hash": "",
            "cached_files": 0,
            "current_files": 0,
            "added_files": [],
            "removed_files": [],
            "changed_files": [],
        }

    project_payload_present = "project_dir" in payload or "project_id" in payload
    overview = None
    project_dir: Path | None = None
    active_chapter: str | None = None
    if project_payload_present:
        try:
            manager, project_id, project_dir = _resolve_project(payload)
            overview = manager.get_project_overview(project_id)
            active_chapter = overview["project"].get("active_chapter")
        except Exception:
            overview = None
            project_dir = None

    import_completed = bool(overview and overview["counts"]["chapters"] > 0)
    translate_paths = _translation_paths(project_dir, active_chapter) if project_dir else {}
    qa_paths = _qa_report_paths(project_dir, active_chapter) if project_dir else {}
    clean_exists = bool(translate_paths and translate_paths["clean"].exists())
    draft_exists = bool(translate_paths and translate_paths["draft"].exists())
    trace_exists = bool(translate_paths and translate_paths["trace"].exists())
    qa_exists = bool(qa_paths and qa_paths["json"].exists())
    compile_completed = db_path.exists() and not bool(cache_status.get("stale"))
    compile_stale = db_path.exists() and bool(cache_status.get("stale"))
    pos_progress = int(round(float(dictionary_stats.get("pos_coverage_pct", 0.0) or 0.0)))
    pinyin_progress = int(round(float(dictionary_stats.get("pinyin_coverage_pct", 0.0) or 0.0)))

    stages = [
        {
            "id": "import",
            "label": "Nhap",
            "status": "completed" if import_completed else "pending",
            "progress": 100 if import_completed else 0,
            "message": f"{overview['counts']['chapters']} chapter da duoc nap." if import_completed else "Chua co nguon duoc import.",
            "metrics": {
                "chapters": overview["counts"]["chapters"] if overview else 0,
            },
        },
        {
            "id": "compile",
            "label": "Bien dich",
            "status": "completed" if compile_completed else "pending",
            "progress": 100 if compile_completed else (50 if compile_stale else 0),
            "message": (
                f"SQLite san sang: {db_path}"
                if compile_completed
                else (
                    f"trie_cache.db can bien dich lai: {cache_status.get('reason')}"
                    if compile_stale
                    else "Chua co trie_cache.db duoc bien dich."
                )
            ),
            "metrics": {
                "db_path": str(db_path),
                "entries_total": dictionary_stats.get("total", 0),
                "compiled_at": dictionary_stats.get("compiled_at"),
                "source_cache": cache_status,
            },
        },
        {
            "id": "assign_pos",
            "label": "Gan POS",
            "status": "completed" if pos_progress >= 95 else ("running" if compile_completed and pos_progress > 0 else "pending"),
            "progress": pos_progress,
            "message": f"POS {dictionary_stats.get('pos_coverage_pct', 0)}% | Pinyin {dictionary_stats.get('pinyin_coverage_pct', 0)}%",
            "metrics": {
                "pos_coverage_pct": dictionary_stats.get("pos_coverage_pct", 0.0),
                "pinyin_coverage_pct": dictionary_stats.get("pinyin_coverage_pct", 0.0),
                "entity_total": dictionary_stats.get("entity_total", 0),
                "pinyin_progress": pinyin_progress,
            },
        },
        {
            "id": "translate",
            "label": "Dich",
            "status": "completed" if clean_exists else "pending",
            "progress": 100 if clean_exists else 0,
            "message": f"Da xuat ban dich cho {active_chapter or 'slice hien tai'}." if clean_exists else "Chua co output dich.",
            "metrics": {
                "active_chapter": active_chapter,
                "output_path": str(translate_paths["clean"]) if translate_paths else "",
            },
        },
        {
            "id": "qa",
            "label": "QA",
            "status": "completed" if qa_exists else "pending",
            "progress": 100 if qa_exists else 0,
            "message": "Bao cao QA da san sang." if qa_exists else "Chua co bao cao QA.",
            "metrics": {
                "qa_report_path": str(qa_paths["json"]) if qa_paths else "",
                "issues": overview["counts"]["qa_issues"] if overview else 0,
            },
        },
        {
            "id": "export",
            "label": "Xuat",
            "status": "completed" if clean_exists and draft_exists and trace_exists else "pending",
            "progress": 100 if clean_exists and draft_exists and trace_exists else 0,
            "message": "Clean, draft va trace deu da xuat." if clean_exists and draft_exists and trace_exists else "Artifact xuat chua day du.",
            "metrics": {
                "clean": str(translate_paths["clean"]) if translate_paths else "",
                "draft": str(translate_paths["draft"]) if translate_paths else "",
                "trace": str(translate_paths["trace"]) if translate_paths else "",
            },
        },
    ]

    return {
        "stages": stages,
        "dictionary_stats": dictionary_stats,
        "project": overview["project"] if overview else None,
        "artifacts": overview["artifacts"] if overview else {},
        "last_state": overview["state"] if overview else {},
    }


def _translation_paths(project_dir: Path | None, chapter_id: str | None) -> dict[str, Path]:
    if project_dir is None:
        return {}
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


def _qa_report_paths(project_dir: Path | None, chapter_id: str | None) -> dict[str, Path]:
    if project_dir is None:
        return {}
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


def _learning_report_paths(project_dir: Path | None, chapter_id: str | None) -> dict[str, Path]:
    if project_dir is None:
        return {}
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


def _normalize_project_entity(payload: dict) -> dict:
    positions = payload.get("positions")
    if not isinstance(positions, list):
        positions = []
    return {
        "source": str(payload.get("source") or "").strip(),
        "target": str(payload.get("target") or "").strip(),
        "entity_type": str(payload.get("entity_type") or "project_term").strip() or "project_term",
        "confidence": _coerce_float(payload.get("confidence"), 1.0),
        "source_dict": str(payload.get("source_dict") or "user_review").strip() or "user_review",
        "ambiguity_flag": bool(payload.get("ambiguity_flag", False)),
        "count": max(1, int(_coerce_float(payload.get("count"), 1))),
        "positions": [int(item) for item in positions if isinstance(item, (int, float))],
    }


def _coerce_float(value: object, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _normalize_junk_phrase_entry(item: object) -> dict | None:
    if isinstance(item, str):
        source = item.strip()
        if not source:
            return None
        return {
            "source": source,
            "target": "",
            "clean_text": "",
            "origin": "user_review",
            "enabled": True,
        }
    if not isinstance(item, dict):
        return None
    source = str(item.get("source") or item.get("raw_pattern") or item.get("phrase") or item.get("text") or "").strip()
    target = str(item.get("target") or item.get("target_vi") or "").strip()
    if not source and not target:
        return None
    return {
        "source": source,
        "target": target,
        "clean_text": str(item.get("clean_text") or item.get("replacement") or "").strip(),
        "origin": str(item.get("origin") or item.get("source_dict") or "user_review").strip() or "user_review",
        "enabled": item.get("enabled", True) is not False,
    }


def _upsert_config_junk_phrase(config: dict, entity: dict) -> tuple[dict, int]:
    entries = config.get("ignored_phrases", [])
    if not isinstance(entries, list):
        entries = []
    normalized = [
        normalized_item
        for normalized_item in (_normalize_junk_phrase_entry(item) for item in entries)
        if normalized_item and normalized_item["enabled"]
    ]
    new_item = {
        "source": entity["source"],
        "target": entity.get("target", ""),
        "clean_text": "",
        "origin": "user_review",
        "enabled": True,
    }
    config["ignored_phrases"] = _upsert_item(normalized, new_item, key_fields=("source", "target"))
    return config, len(config["ignored_phrases"])


def _delete_config_junk_phrases(config: dict, sources: set[str]) -> tuple[dict, int]:
    deleted_total = 0
    for key in ("ignored_phrases", "junk_phrases", "user_noise_phrases"):
        entries = config.get(key, [])
        if not isinstance(entries, list):
            continue
        normalized = [
            normalized_item
            for normalized_item in (_normalize_junk_phrase_entry(item) for item in entries)
            if normalized_item
        ]
        updated = [
            item
            for item in normalized
            if item["source"] not in sources and item["target"] not in sources
        ]
        deleted_total += len(normalized) - len(updated)
        config[key] = updated
    return config, deleted_total


def _upsert_project_entity(project_dir: Path, entity: dict, *, sync_locked: bool) -> dict:
    entities_path = project_dir / "working" / "entities" / "entities_suggested.json"
    entities = _load_json(entities_path, [])
    if not isinstance(entities, list):
        entities = []
    normalized_entities = [dict(item) for item in entities if isinstance(item, dict)]
    updated_entities = _upsert_item(normalized_entities, entity, key_fields=("source",))
    _write_json(entities_path, updated_entities)

    config_path = project_dir / "working" / "config" / "translation_config.json"
    config = _load_json(config_path, {})
    if not isinstance(config, dict):
        config = {}
    locked_count = len(config.get("locked_entities", []) if isinstance(config.get("locked_entities"), list) else [])
    junk_phrase_count = len(config.get("ignored_phrases", []) if isinstance(config.get("ignored_phrases"), list) else [])
    if entity.get("entity_type") == "junk_phrase":
        config, junk_phrase_count = _upsert_config_junk_phrase(config, entity)
        _write_json(config_path, config)
        sync_locked = False
    elif sync_locked:
        locked_item = {
            "source": entity["source"],
            "target": entity["target"],
            "entity_type": entity["entity_type"],
            "origin": "user_review",
        }
        locked_entities = config.get("locked_entities", [])
        if not isinstance(locked_entities, list):
            locked_entities = []
        config["locked_entities"] = _upsert_item(
            [dict(item) for item in locked_entities if isinstance(item, dict)],
            locked_item,
            key_fields=("source",),
        )
        locked_count = len(config["locked_entities"])
        _write_json(config_path, config)

    return {
        "entity": entity,
        "entities_path": str(entities_path),
        "entity_count": len(updated_entities),
        "sync_locked": sync_locked,
        "config_path": str(config_path),
        "locked_entity_count": locked_count,
        "junk_phrase_count": junk_phrase_count,
    }


def _delete_project_entity(project_dir: Path, source: str, *, sync_locked: bool) -> dict:
    result = _delete_project_entities(project_dir, [source], sync_locked=sync_locked)
    normalized_source = result["sources"][0] if result["sources"] else str(source or "").strip()
    return {
        "source": normalized_source,
        "deleted": result["deleted_count"] > 0,
        "entities_path": result["entities_path"],
        "entity_count": result["entity_count"],
        "sync_locked": sync_locked,
        "config_path": result["config_path"],
        "locked_deleted": result["locked_deleted_count"] > 0,
        "locked_entity_count": result["locked_entity_count"],
    }


def _delete_project_entities(project_dir: Path, sources: list[str], *, sync_locked: bool) -> dict:
    normalized_sources = [str(source or "").strip() for source in sources]
    normalized_sources = [source for source in normalized_sources if source]
    source_set = set(normalized_sources)
    entities_path = project_dir / "working" / "entities" / "entities_suggested.json"
    entities = _load_json(entities_path, [])
    if not isinstance(entities, list):
        entities = []
    normalized_entities = [dict(item) for item in entities if isinstance(item, dict)]
    updated_entities = [
        item
        for item in normalized_entities
        if str(item.get("source") or "").strip() not in source_set
    ]
    _write_json(entities_path, updated_entities)

    config_path = project_dir / "working" / "config" / "translation_config.json"
    config = _load_json(config_path, {})
    if not isinstance(config, dict):
        config = {}
    locked_deleted_count = 0
    junk_deleted_count = 0
    locked_count = len(config.get("locked_entities", []) if isinstance(config.get("locked_entities"), list) else [])
    junk_phrase_count = len(config.get("ignored_phrases", []) if isinstance(config.get("ignored_phrases"), list) else [])
    config, junk_deleted_count = _delete_config_junk_phrases(config, source_set)
    junk_phrase_count = len(config.get("ignored_phrases", []) if isinstance(config.get("ignored_phrases"), list) else [])
    if sync_locked:
        locked_entities = config.get("locked_entities", [])
        if not isinstance(locked_entities, list):
            locked_entities = []
        normalized_locked = [dict(item) for item in locked_entities if isinstance(item, dict)]
        updated_locked = [
            item
            for item in normalized_locked
            if str(item.get("source") or "").strip() not in source_set
        ]
        locked_deleted_count = len(normalized_locked) - len(updated_locked)
        config["locked_entities"] = updated_locked
        locked_count = len(updated_locked)
    if sync_locked or junk_deleted_count:
        _write_json(config_path, config)

    return {
        "sources": normalized_sources,
        "deleted_count": len(normalized_entities) - len(updated_entities),
        "entities_path": str(entities_path),
        "entity_count": len(updated_entities),
        "sync_locked": sync_locked,
        "config_path": str(config_path),
        "locked_deleted_count": locked_deleted_count,
        "locked_entity_count": locked_count,
        "junk_deleted_count": junk_deleted_count,
        "junk_phrase_count": junk_phrase_count,
    }


def _build_entity_target_suggestions(
    accessor: RuntimeDictionaryAccessor,
    source: str,
    *,
    project_id: str | None = None,
    project_dir: Path | None = None,
) -> list[dict]:
    suggestions: list[dict] = []
    seen: set[str] = set()
    from src.pipeline.term_bank import TermBank

    name_resolver = HanVietNameResolver(accessor, TermBank(project_id=project_id, project_dir=project_dir))

    def add(kind: str, label: str, value: str, detail: str, confidence: float):
        normalized = " ".join(str(value or "").split()).strip()
        if not normalized:
            return
        key = normalized.casefold()
        if key in seen:
            return
        seen.add(key)
        suggestions.append({
            "kind": kind,
            "label": label,
            "value": normalized,
            "detail": detail,
            "confidence": round(confidence, 3),
        })

    stored_target = name_resolver.resolve_stored_keyword(source)
    if stored_target:
        add(
            "stored_keyword",
            "Từ khóa lưu sẵn",
            stored_target,
            "Target lấy từ mục tên/entity đã có trong dictionary.",
            0.98,
        )

    direct_hv = name_resolver.pick_han_viet_reading(source)
    if direct_hv:
        add(
            "han_viet_dictionary",
            "Hán Việt dictionary",
            _title_case_words(direct_hv),
            "Đọc Hán Việt theo mục từ có sẵn.",
            0.96,
        )

    word_hv = name_resolver.resolve_word_by_word(source)
    if word_hv:
        add(
            "han_viet_word",
            "Hán Việt word by word",
            word_hv,
            "Ghép từng Hán tự theo thứ tự source.",
            0.9,
        )

    latin_from_dict = _resolve_latin_dictionary_targets(accessor, source)
    for value in latin_from_dict:
        add(
            "latin_dictionary",
            "Latinh dictionary",
            value,
            "Tên phương Tây lấy từ dictionary.",
            0.92,
        )

    latin_generated = name_resolver.resolve_latin_target(source, allow_phonetic=True)
    if latin_generated:
        add(
            "latin_name",
            "Latinh proper name",
            latin_generated,
            "Tên Latin lấy từ term bank, reference hoặc phiên âm tên Tây.",
            0.88,
        )

    latin_from_source = _extract_latin_name(source)
    if latin_from_source:
        add(
            "latin_source",
            "Latinh source",
            latin_from_source,
            "Giữ phần chữ Latin có sẵn trong source.",
            0.86,
        )

    pinyin = _resolve_pinyin_word_by_word(accessor, source)
    if pinyin and latin_from_dict and _has_latin_letter(pinyin):
        add(
            "latin_pinyin",
            "Latinh pinyin",
            pinyin,
            "Pinyin tham khảo khi cần phiên âm Latin.",
            0.72,
        )

    return suggestions


def _pick_han_viet_reading(accessor: RuntimeDictionaryAccessor, source: str) -> str:
    for record in accessor.get_entry_readings(source):
        value = _normalize_reading(record.han_viet_readings)
        if value:
            return value
    return ""


def _resolve_han_viet_word_by_word(accessor: RuntimeDictionaryAccessor, source: str) -> str:
    parts: list[str] = []
    has_cjk = False
    for char in source:
        if _is_cjk_char(char):
            has_cjk = True
            reading = _pick_han_viet_reading(accessor, char)
            parts.append(reading or char)
        elif char.isspace():
            continue
        else:
            parts.append(char)
    if not has_cjk:
        return ""
    return _title_case_words(" ".join(parts))


def _resolve_pinyin_word_by_word(accessor: RuntimeDictionaryAccessor, source: str) -> str:
    parts: list[str] = []
    has_cjk = False
    for char in source:
        if _is_cjk_char(char):
            has_cjk = True
            pinyin = ""
            for record in accessor.get_entry_readings(char):
                pinyin = _normalize_reading(record.pinyin)
                if pinyin:
                    break
            parts.append(pinyin or char)
        elif char.isspace():
            continue
        else:
            parts.append(char)
    if not has_cjk:
        return ""
    return " ".join(parts).strip()


def _resolve_latin_dictionary_targets(accessor: RuntimeDictionaryAccessor, source: str) -> list[str]:
    values: list[str] = []
    for record in accessor.lookup_all(source):
        if not _looks_like_western_name_record(record):
            continue
        value = _first_target_variant(record.target)
        if value and _has_latin_letter(value):
            values.append(_title_case_latin(value))
    return values


def _looks_like_western_name_record(record: object) -> bool:
    source_file = str(getattr(record, "source_file", "") or "").casefold()
    category = str(getattr(record, "category", "") or "").casefold()
    cultural_origin = str(getattr(record, "cultural_origin", "") or "").casefold()
    metadata = getattr(record, "metadata", {}) or {}
    metadata_origin = str(metadata.get("cultural_origin", "") or "").casefold() if isinstance(metadata, dict) else ""
    return (
        "west" in source_file
        or "latin" in category
        or cultural_origin in {"western", "west", "latin"}
        or metadata_origin in {"western", "west", "latin"}
    )


def _extract_latin_name(source: str) -> str:
    spans = re.findall(r"[A-Za-z][A-Za-z0-9'._-]*(?:\s+[A-Za-z][A-Za-z0-9'._-]*)*", source)
    if not spans:
        return ""
    return _title_case_latin(" ".join(spans))


def _first_target_variant(value: str) -> str:
    return re.split(r"[|,;/]", value or "", maxsplit=1)[0].strip()


def _normalize_reading(value: str) -> str:
    if not value:
        return ""
    return re.split(r"[|,;/]", value, maxsplit=1)[0].strip()


def _title_case_words(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in value.split() if part)


def _title_case_latin(value: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in value.split() if part)


def _has_latin_letter(value: str) -> bool:
    return bool(re.search(r"[A-Za-z]", value or ""))


def _is_cjk_char(value: str) -> bool:
    return "\u4e00" <= value <= "\u9fff"


def _grammar_candidate_to_rule_payload(candidate: dict, *, report_paths: dict, scope: str) -> dict:
    pattern_text = str(candidate.get("pattern_text") or "").strip()
    pattern_type = str(candidate.get("pattern_type") or "").strip()
    guessed_category = str(candidate.get("guessed_category") or "").strip()
    frequency = int(candidate.get("frequency") or 0)
    chapter_count = int(candidate.get("chapter_count") or 0)
    confidence = float(candidate.get("confidence") or 0.0)
    return {
        "title": f"Grammar candidate: {pattern_text}",
        "summary": (
            f"{pattern_type} repeated {frequency} time(s) across "
            f"{chapter_count} chapter(s); review before promoting to a grammar rule."
        ),
        "payload": {
            **candidate,
            "report_paths": report_paths,
            "scope": scope,
        },
        "confidence": round(confidence, 3),
        "scope": scope,
        "chapter_id": None,
        "origin": "grammar_pattern_scanner",
        "review_note": "Coach-only candidate. Verification writes to grammar learning backlog, not translation config.",
        "suggested_rule": {
            "pattern_text": pattern_text,
            "pattern_type": pattern_type,
            "category": guessed_category or None,
            "regex": candidate.get("suggested_regex"),
            "status": "review",
        },
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

    if rule_type == "grammar_pattern_candidate":
        backlog_path = project_dir / "working" / "grammar_learning" / "verified_patterns.json"
        existing_backlog = _load_json(backlog_path, [])
        if not isinstance(existing_backlog, list):
            existing_backlog = []
        candidate_payload = dict(suggestion_payload or payload)
        candidate_id = str(candidate_payload.get("candidate_id") or payload.get("title") or rule.get("id") or "").strip()
        candidate_payload["verified_rule_id"] = rule.get("id")
        candidate_payload["verified_from"] = "candidate_rule"
        candidate_payload["chapter_id"] = effective_chapter_id or ""
        candidate_payload["scope"] = scope
        normalized_backlog = [
            item
            for item in existing_backlog
            if isinstance(item, dict) and str(item.get("candidate_id") or "") != candidate_id
        ]
        normalized_backlog.append(candidate_payload)
        _write_json(backlog_path, normalized_backlog)
        applied_changes["updated"] = "grammar_learning_backlog"
        applied_changes["backlog_path"] = str(backlog_path)
        applied_changes["effective_config"] = _resolve_translation_config(
            project_dir,
            config,
            effective_chapter_id if scope == "chapter" else None,
        )
        return applied_changes

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
    parser.add_argument("--request-json", help="JSON encoded CommandRequest")
    parser.add_argument("--request-json-stdin", action="store_true", help="Read JSON encoded CommandRequest from stdin")
    args = parser.parse_args()
    request_payload = sys.stdin.read() if args.request_json_stdin else args.request_json
    if not request_payload:
        raise SystemExit("--request-json or --request-json-stdin is required")
    request = CommandRequest(**json.loads(request_payload))
    response = handle_request(request)
    print(json.dumps(response.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
