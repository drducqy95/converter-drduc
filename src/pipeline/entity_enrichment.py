#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Human-reviewed entity enrichment workflow for the term bank."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, replace
from pathlib import Path

from src.pipeline.entity_scanner import EntitySuggestion
from src.pipeline.term_bank import DEFAULT_TERM_BANK_ROOT, ENTITY_TYPES, TermBank, TermBankRecord
from src.pipeline.universe import resolve_project_universe_id, slugify_universe_id


class EntityEnrichmentManager:
    """Manage scan -> review -> approve -> save for term-bank candidates."""

    def __init__(
        self,
        *,
        term_bank: TermBank | None = None,
        root: str | Path | None = None,
        project_id: str | None = None,
        project_dir: str | Path | None = None,
    ):
        self.term_bank = term_bank or TermBank(root=root, project_id=project_id, project_dir=project_dir)
        self.root = Path(root or self.term_bank.root or DEFAULT_TERM_BANK_ROOT)
        self.project_id = (project_id or self.term_bank.project_id or "").strip()
        self.project_dir = Path(project_dir) if project_dir else self.term_bank.project_dir
        self.universe_id = resolve_project_universe_id(
            project_id=self.project_id,
            project_dir=self.project_dir,
        )

    def prepare_for_review(
        self,
        entities: list[EntitySuggestion],
        *,
        detected_universes: list[str | tuple[str, float]] | None = None,
        context: str = "",
    ) -> list[EntitySuggestion]:
        normalized_universes = self._normalize_detected_universes(detected_universes)
        single_universe = normalized_universes[0] if len(normalized_universes) == 1 else self.universe_id
        prepared: list[EntitySuggestion] = []
        for entity in entities:
            universe = slugify_universe_id(entity.universe or single_universe)
            suggested_record = self.term_bank.suggest_enrichment(
                replace(entity, universe=universe),
                context=context,
            )
            prepared.append(
                replace(
                    entity,
                    universe=universe or suggested_record.universe,
                    review_status=entity.review_status or "pending",
                    enrichment_ready=bool(entity.source and entity.target),
                    suggested_tags=list(dict.fromkeys([*entity.suggested_tags, *suggested_record.tags])),
                    suggested_context_markers=list(
                        dict.fromkeys([*entity.suggested_context_markers, *suggested_record.context_markers])
                    ),
                )
            )
        return prepared

    @staticmethod
    def approve_entity(entity: EntitySuggestion) -> EntitySuggestion:
        return replace(entity, review_status="approved", enrichment_ready=bool(entity.source and entity.target))

    @staticmethod
    def reject_entity(entity: EntitySuggestion) -> EntitySuggestion:
        return replace(entity, review_status="rejected", enrichment_ready=False)

    def save_to_term_bank(self, entities: list[EntitySuggestion], *, target_scope: str = "universe") -> int:
        target_scope = target_scope.strip().casefold() or "universe"
        approved = [
            entity
            for entity in entities
            if entity.review_status in {"approved", "saved"} and entity.enrichment_ready
        ]
        if not approved:
            return 0

        grouped: dict[Path, list[TermBankRecord]] = {}
        for entity in approved:
            path = self._target_path(entity, target_scope=target_scope)
            grouped.setdefault(path, []).append(self._record_from_entity(entity, target_scope=target_scope))

        saved_count = 0
        for path, records in grouped.items():
            saved_count += self._merge_jsonl(path, records)
        self.term_bank.reload_universe()
        return saved_count

    @staticmethod
    def export_review_report(entities: list[EntitySuggestion]) -> str:
        lines = ["# Entity Enrichment Review", ""]
        for entity in entities:
            lines.extend(
                [
                    f"## {entity.source}",
                    "",
                    f"- Target: {entity.target}",
                    f"- Type: {entity.entity_type}",
                    f"- Universe: {entity.universe or '(unset)'}",
                    f"- Confidence: {entity.confidence:.2f}",
                    f"- Status: {entity.review_status}",
                    f"- Ready: {'yes' if entity.enrichment_ready else 'no'}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _normalize_detected_universes(detected_universes: list[str | tuple[str, float]] | None) -> list[str]:
        normalized: list[str] = []
        for item in detected_universes or []:
            universe = item[0] if isinstance(item, tuple) else item
            universe = slugify_universe_id(str(universe or "").strip())
            if universe and universe not in normalized:
                normalized.append(universe)
        return normalized

    def _target_path(self, entity: EntitySuggestion, *, target_scope: str) -> Path:
        scope = target_scope.strip().casefold()
        if scope == "global":
            return self.root / "global" / "enriched_terms.jsonl"
        if scope == "universe":
            universe = slugify_universe_id(entity.universe or self.universe_id or "unknown")
            return self.root / "universes" / universe / "user_terms.jsonl"
        if self.project_dir:
            return self.project_dir / "knowledge" / "private_terms.jsonl"
        project_id = self.project_id or "project-001"
        return self.root / "projects" / project_id / "private_terms.jsonl"

    @staticmethod
    def _record_from_entity(entity: EntitySuggestion, *, target_scope: str) -> TermBankRecord:
        entity_type = entity.entity_type if entity.entity_type in ENTITY_TYPES else "term"
        scope = "private" if target_scope not in {"global", "universe"} else target_scope
        return TermBankRecord(
            source=entity.source,
            target=entity.target,
            entity_type=entity_type,
            scope=scope,
            confidence=min(max(float(entity.confidence), 0.0), 1.0),
            status="approved",
            source_dict="entity_enrichment",
            universe=slugify_universe_id(entity.universe),
            work=entity.work,
            tags=list(entity.suggested_tags),
            context_markers=list(entity.suggested_context_markers),
            version=1,
        )

    @staticmethod
    def _merge_jsonl(path: Path, incoming: list[TermBankRecord]) -> int:
        path.parent.mkdir(parents=True, exist_ok=True)
        rows: list[dict] = []
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                rows.append(json.loads(stripped))

        by_key: dict[tuple[str, str], dict] = {}
        for row in rows:
            source = str(row.get("source") or "").strip()
            universe = str(row.get("universe") or "").strip()
            if source:
                by_key[(source, universe)] = row

        changed = 0
        for record in incoming:
            payload = asdict(record)
            key = (record.source, record.universe)
            if by_key.get(key) != payload:
                changed += 1
            by_key[key] = payload

        tmp_path = path.with_suffix(path.suffix + ".tmp")
        ordered_rows = sorted(by_key.values(), key=lambda row: (str(row.get("source") or ""), str(row.get("universe") or "")))
        tmp_path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in ordered_rows) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp_path, path)
        return changed
