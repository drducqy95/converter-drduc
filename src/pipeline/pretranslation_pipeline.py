#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""End-to-end Phase 02 orchestration for a single source document."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.engine.pinyin_processor import PinyinProcessor
from src.engine.structure_preserver import StructurePreserver
from src.engine.traditional_to_simplified import TraditionalToSimplifiedConverter
from src.pipeline.chapter_splitter import Chapter, ChapterSplitter
from src.pipeline.config_generator import ConfigGenerator
from src.pipeline.document_importer import DocumentImporter, ImportedDocument
from src.pipeline.entity_scanner import EntityScanner
from src.pipeline.relationship_builder import RelationshipBuilder
from src.pipeline.segment_classifier import SegmentClassifier
from src.pipeline.terminology_suggester import TerminologySuggester
from src.parser.dependency_parser import DependencyParser
from src.parser.morphological_analyzer import MorphologicalAnalyzer
from src.rules.syntax_transfer_rules import SyntaxTransferRules


SUPPORTED_SOURCE_SUFFIXES = {".txt", ".md", ".markdown", ".html", ".htm", ".docx", ".pdf"}
CHAPTER_NUMBER_RE = re.compile(r"(\d{1,4})")
MAX_ANALYSIS_CHARS = 500_000  # Cap text for entity/relationship scanning to prevent OOM
MAX_ENTITIES = 200            # Cap entity count to prevent O(n²) relationship explosion
MAX_RELATIONSHIPS = 500       # Cap relationship edges to prevent JSON serialization OOM
MAX_SYNTAX_SEGMENTS = 2_000   # Keep syntax artifacts bounded on large projects
MAX_SYNTAX_TEXT_CHARS = 800


@dataclass(slots=True)
class PreTranslationResult:
    imported: ImportedDocument
    normalized_text: str
    chapters: list[Chapter]
    entities: list[dict]
    relationships: list[dict]
    config: dict
    segments: list[dict] | None = None
    syntax_analysis: list[dict] | None = None
    import_errors: list[dict] | None = None


class PreTranslationPipeline:
    """Prepare project inputs before translation."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path
        self.importer = DocumentImporter()
        self.splitter = ChapterSplitter()
        self.preserver = StructurePreserver()
        self.converter = TraditionalToSimplifiedConverter()
        self.pinyin = PinyinProcessor(db_path=db_path)
        self.scanner = EntityScanner(db_path=db_path)
        self.relationship_builder = RelationshipBuilder()
        self.suggester = TerminologySuggester(db_path=db_path)
        self.config_generator = ConfigGenerator(db_path=db_path)
        self.segment_classifier = SegmentClassifier()
        self.morphological_analyzer = MorphologicalAnalyzer()
        self.dependency_parser = DependencyParser()
        self.syntax_transfer_rules = SyntaxTransferRules()
        self.accessor = RuntimeDictionaryAccessor(db_path) if db_path else None

    def close(self):
        self.pinyin.close()
        self.suggester.close()
        self.config_generator.close()
        if self.accessor:
            self.accessor.close()

    def prepare(self, filepath: str | Path, project_dir: str | Path) -> PreTranslationResult:
        source_path = Path(filepath)
        if not source_path.exists():
            raise ValueError(f"Source path does not exist: {source_path}")
        if source_path.is_dir():
            return self._prepare_directory(source_path, project_dir)
        return self._prepare_file(source_path, project_dir)

    def _prepare_file(self, source_path: Path, project_dir: str | Path) -> PreTranslationResult:
        imported = self.importer.import_file(source_path, output_dir=project_dir)
        normalized_text = self._transform_text(imported.normalized_text)
        chapters = self.splitter.split(normalized_text)
        return self._finalize_preparation(
            imported=imported,
            normalized_text=normalized_text,
            chapters=chapters,
            project_dir=project_dir,
            metadata_source=source_path,
        )

    def _prepare_directory(self, source_path: Path, project_dir: str | Path) -> PreTranslationResult:
        source_dir = self._resolve_source_directory(source_path)
        source_files = self._discover_source_files(source_dir)
        if not source_files:
            raise ValueError(f"No supported source files found in directory: {source_path}")

        imported_docs: list[ImportedDocument] = []
        chapters: list[Chapter] = []
        import_errors: list[dict] = []
        used_chapter_ids: set[str] = set()

        # Directory import: each file is one logical chapter, with the file heading
        # kept as the chapter title when present.
        for source_file in source_files:
            try:
                imported_doc = self.importer.import_file(source_file, output_dir=project_dir)
                transformed_text = self._transform_text(imported_doc.normalized_text)
            except Exception as exc:
                import_errors.append(self._import_error_payload(source_file, exc))
                continue
            imported_docs.append(imported_doc)
            chapter_id = self._allocate_chapter_id(
                used_chapter_ids,
                self._extract_chapter_number(source_file),
            )
            title, chapter_text = self._extract_single_file_chapter(source_file, transformed_text)
            chapters.append(
                Chapter(
                    chapter_id=chapter_id,
                    title=title,
                    text=chapter_text,
                    start=0,
                    end=len(chapter_text),
                )
            )

        if not imported_docs:
            raise ValueError(f"No source files could be imported from directory: {source_path}")

        chapters = self._reindex_chapters(chapters)
        normalized_text = "\n\n".join(self._compose_chapter_block(chapter) for chapter in chapters).strip()
        imported = ImportedDocument(
            source_path=str(source_dir),
            detected_format="directory",
            detected_encoding="mixed",
            raw_text="\n\n".join(doc.raw_text for doc in imported_docs).strip(),
            normalized_text=normalized_text,
            notes=[
                "directory_import",
                f"source_files={len(source_files)}",
                f"imported_files={len(imported_docs)}",
                f"skipped_files={len(import_errors)}",
            ],
        )
        return self._finalize_preparation(
            imported=imported,
            normalized_text=normalized_text,
            chapters=chapters,
            project_dir=project_dir,
            metadata_source=source_files[0],
            import_errors=import_errors,
        )

    def _finalize_preparation(
        self,
        *,
        imported: ImportedDocument,
        normalized_text: str,
        chapters: list[Chapter],
        project_dir: str | Path,
        metadata_source: Path,
        import_errors: list[dict] | None = None,
    ) -> PreTranslationResult:
        self.splitter.write(chapters, project_dir)

        # Cap text for entity/relationship analysis to prevent OOM on large imports
        analysis_text = normalized_text[:MAX_ANALYSIS_CHARS] if len(normalized_text) > MAX_ANALYSIS_CHARS else normalized_text

        entities = self.scanner.scan(analysis_text)
        # Cap entities to prevent O(n²) explosion in relationship builder
        if len(entities) > MAX_ENTITIES:
            entities = sorted(entities, key=lambda e: e.count, reverse=True)[:MAX_ENTITIES]
        relationships = self.relationship_builder.build(analysis_text, entities)
        # Cap relationships to prevent JSON serialization OOM
        if len(relationships) > MAX_RELATIONSHIPS:
            relationships = sorted(relationships, key=lambda r: r.confidence, reverse=True)[:MAX_RELATIONSHIPS]
        terminology = self.suggester.suggest(entities)
        config = self.config_generator.generate(
            text=analysis_text,
            entities=entities,
            relationships=relationships,
            terminology=terminology,
        )
        config = self._merge_external_project_metadata(config, metadata_source)
        self.config_generator.write(config, project_dir)
        segment_packets = self._build_segment_packets(chapters)
        syntax_analysis = self._build_syntax_analysis(segment_packets)

        self._write_json(project_dir, "working/entities/entities_suggested.json", [item.to_dict() for item in entities])
        self._write_json(project_dir, "working/relationships/relationships_suggested.json", [item.to_dict() for item in relationships])
        self._write_json(project_dir, "working/config/terminology_suggestions.json", [item.to_dict() for item in terminology])
        self._write_json(project_dir, "working/segments/segments_classified.json", segment_packets)
        self._write_json(project_dir, "working/segments/syntax_analysis.json", syntax_analysis)
        if import_errors:
            self._write_json(project_dir, "working/import_errors.json", import_errors)

        return PreTranslationResult(
            imported=imported,
            normalized_text=normalized_text,
            chapters=chapters,
            entities=[item.to_dict() for item in entities],
            relationships=[item.to_dict() for item in relationships],
            config=config,
            segments=segment_packets,
            syntax_analysis=syntax_analysis,
            import_errors=import_errors or [],
        )

    def _transform_text(self, text: str) -> str:
        normalized = self._apply_normalization(text)
        preserved = self.preserver.preserve(normalized)
        simplified = self.converter.convert(preserved.text)
        restored = self.preserver.restore(simplified, preserved.placeholders)
        return self.pinyin.resolve(restored)

    def _resolve_source_directory(self, source_path: Path) -> Path:
        if (source_path / "source").is_dir():
            nested_source = source_path / "source"
            if self._discover_source_files(nested_source):
                return nested_source
        return source_path

    def _discover_source_files(self, source_dir: Path) -> list[Path]:
        if not source_dir.exists() or not source_dir.is_dir():
            return []
        source_files = [
            child
            for child in sorted(source_dir.iterdir())
            if child.is_file() and child.suffix.lower() in SUPPORTED_SOURCE_SUFFIXES
        ]
        if source_files:
            return source_files
        chapter_dir = source_dir / "chapters"
        if not chapter_dir.is_dir():
            return []
        return [
            child
            for child in sorted(chapter_dir.iterdir())
            if child.is_file() and child.suffix.lower() in SUPPORTED_SOURCE_SUFFIXES
        ]

    def _chapters_from_source_file(self, *, source_file: Path, text: str, used_chapter_ids: set[str]) -> list[Chapter]:
        split_chapters = self.splitter.split(text)
        if not split_chapters:
            split_chapters = [
                Chapter(
                    chapter_id="",
                    title=self._default_chapter_title(source_file),
                    text=text.strip(),
                    start=0,
                    end=len(text),
                )
            ]

        chapters: list[Chapter] = []
        preferred_number = self._extract_chapter_number(source_file)
        for index, split_chapter in enumerate(split_chapters):
            chapter_id = self._allocate_chapter_id(
                used_chapter_ids,
                preferred_number if index == 0 else None,
            )
            title = self._chapter_title_for_import(split_chapter.title, source_file, index)
            chapter_text = split_chapter.text.strip() or text.strip()
            chapters.append(
                Chapter(
                    chapter_id=chapter_id,
                    title=title,
                    text=chapter_text,
                    start=0,
                    end=0,
                )
            )
        return chapters

    def _allocate_chapter_id(self, used_chapter_ids: set[str], preferred_number: int | None) -> str:
        if preferred_number is not None:
            preferred_id = f"chapter-{preferred_number:03d}"
            if preferred_id not in used_chapter_ids:
                used_chapter_ids.add(preferred_id)
                return preferred_id

        next_number = 1
        while f"chapter-{next_number:03d}" in used_chapter_ids:
            next_number += 1
        chapter_id = f"chapter-{next_number:03d}"
        used_chapter_ids.add(chapter_id)
        return chapter_id

    def _reindex_chapters(self, chapters: list[Chapter]) -> list[Chapter]:
        reindexed: list[Chapter] = []
        cursor = 0
        for chapter in chapters:
            block = self._compose_chapter_block(chapter)
            start = cursor
            end = start + len(block)
            reindexed.append(
                Chapter(
                    chapter_id=chapter.chapter_id,
                    title=chapter.title,
                    text=chapter.text,
                    start=start,
                    end=end,
                )
            )
            cursor = end + 2
        return reindexed

    @staticmethod
    def _compose_chapter_block(chapter: Chapter) -> str:
        parts = [chapter.title.strip(), chapter.text.strip()]
        return "\n".join(part for part in parts if part).strip()

    def _extract_single_file_chapter(self, source_file: Path, text: str) -> tuple[str, str]:
        split_chapters = self.splitter.split(text)
        if split_chapters:
            chapter = split_chapters[0]
            if chapter.title and not chapter.title.lower().startswith("auto split"):
                body = chapter.text.strip()
                if len(split_chapters) > 1:
                    rest = [self._compose_chapter_block(item) for item in split_chapters[1:]]
                    body = "\n\n".join(part for part in [body, *rest] if part).strip()
                return chapter.title, body
        return self._default_chapter_title(source_file), text.strip()

    @staticmethod
    def _chapter_title_for_import(title: str, source_file: Path, index: int) -> str:
        cleaned = title.strip()
        if cleaned and not cleaned.lower().startswith("auto split"):
            return cleaned
        if index == 0:
            return PreTranslationPipeline._default_chapter_title(source_file)
        return f"{PreTranslationPipeline._default_chapter_title(source_file)} / Part {index + 1}"

    @staticmethod
    def _default_chapter_title(source_file: Path) -> str:
        return source_file.stem.replace("_", " ").replace("-", " ").strip() or source_file.name

    @staticmethod
    def _extract_chapter_number(source_file: Path) -> int | None:
        matches = CHAPTER_NUMBER_RE.findall(source_file.stem)
        return int(matches[-1]) if matches else None

    def _apply_normalization(self, text: str) -> str:
        if not self.accessor:
            return text
        normalized = text
        for rule in self.accessor.get_normalization_rules():
            if rule.rule_type in {"replace", "punctuation_map", "mark_map"} and rule.source_text:
                normalized = normalized.replace(rule.source_text, rule.target_text)
            elif rule.rule_type == "ignored_phrase":
                normalized = normalized.replace(rule.source_text, rule.target_text)
        return normalized

    def _write_json(self, project_dir: str | Path, relative_path: str, payload: object):
        target = Path(project_dir) / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _import_error_payload(source_file: Path, exc: Exception) -> dict:
        details = getattr(exc, "details", None)
        return {
            "source_path": str(source_file),
            "error_type": type(exc).__name__,
            "message": str(exc),
            "details": details if isinstance(details, dict) else {},
        }

    def _build_segment_packets(self, chapters: list[Chapter]) -> list[dict]:
        packets: list[dict] = []
        for chapter in chapters:
            raw_segments = [
                line.strip()
                for line in self._compose_chapter_block(chapter).splitlines()
                if line.strip()
            ]
            for position, segment_text in enumerate(raw_segments):
                packet = self.segment_classifier.build_packet(
                    segment_text,
                    chapter_id=chapter.chapter_id,
                    position=position,
                    total_segments=len(raw_segments),
                )
                packets.append({
                    "segment_id": packet.segment_id,
                    "trace_id": packet.trace_id,
                    "chapter_id": packet.chapter_id,
                    "position": packet.position,
                    "raw_text": packet.raw_text,
                    "normalized_text": packet.normalized_text,
                    "seg_type": packet.seg_type.value,
                    "confidence": packet.confidence,
                    "protected_spans": [asdict(span) for span in packet.protected_spans],
                    "metadata": packet.metadata,
                    "trace": [event.to_dict() for event in packet.trace],
                })
        return packets

    def _build_syntax_analysis(self, segment_packets: list[dict]) -> list[dict]:
        analysis_packets: list[dict] = []
        for packet in segment_packets[:MAX_SYNTAX_SEGMENTS]:
            text = str(packet.get("normalized_text") or packet.get("raw_text") or "").strip()
            if not text:
                continue
            clipped = text[:MAX_SYNTAX_TEXT_CHARS]
            morphology = self.morphological_analyzer.analyze(clipped)
            dependencies = self.dependency_parser.parse(morphology)
            transfer = self.syntax_transfer_rules.apply(
                dependencies,
                context={
                    "chapter_id": packet.get("chapter_id"),
                    "segment_id": packet.get("segment_id"),
                    "seg_type": packet.get("seg_type"),
                },
            )
            analysis_packets.append({
                "segment_id": packet.get("segment_id"),
                "trace_id": packet.get("trace_id"),
                "chapter_id": packet.get("chapter_id"),
                "position": packet.get("position"),
                "seg_type": packet.get("seg_type"),
                "text": clipped,
                "tokens": dependencies.get("tokens", []),
                "posTags": dependencies.get("posTags", []),
                "dependencies": dependencies.get("dependencies", []),
                "root": dependencies.get("root"),
                "syntax_rules_applied": transfer.get("syntax_rules_applied", []),
                "transformed": transfer.get("transformed", False),
            })
        return analysis_packets

    def _merge_external_project_metadata(self, config: dict, source_path: Path) -> dict:
        project_root = self._detect_external_project_root(source_path)
        if project_root is None:
            return config

        locked_entities = {
            item["source"]: dict(item)
            for item in config.get("locked_entities", [])
            if item.get("source") and item.get("target")
        }

        glossary_items = self._load_glossary_locked_entities(project_root / "glossary.json")
        character_items = self._load_character_locked_entities(project_root / "characters.json")
        external_items = glossary_items + character_items

        external_count = 0
        for item in external_items:
            locked_entities[item["source"]] = item
            external_count += 1

        if not external_count:
            return config

        self._drop_shadowed_prefix_entities(locked_entities, external_items)

        merged = dict(config)
        merged["locked_entities"] = sorted(
            locked_entities.values(),
            key=lambda item: (-len(item["source"]), item["source"]),
        )
        merged["external_project_metadata"] = {
            "root_dir": str(project_root),
            "source_file": str(source_path),
            "source_basename": source_path.name,
            "glossary_loaded": (project_root / "glossary.json").exists(),
            "characters_loaded": (project_root / "characters.json").exists(),
        }
        return merged

    @staticmethod
    def _detect_external_project_root(source_path: Path) -> Path | None:
        if source_path.parent.name.lower() != "source":
            return None
        project_root = source_path.parent.parent
        if not project_root.exists():
            return None
        if any((project_root / name).exists() for name in ("glossary.json", "characters.json")):
            return project_root
        return None

    def _load_glossary_locked_entities(self, glossary_path: Path) -> list[dict]:
        if not glossary_path.exists():
            return []
        payload = json.loads(glossary_path.read_text(encoding="utf-8"))
        locked: list[dict] = []
        for entry in payload.get("entries", []):
            source = str(entry.get("source", "")).strip()
            target = str(entry.get("target") or entry.get("source_target") or "").strip()
            if not source or not target:
                continue
            locked.append(
                {
                    "source": source,
                    "target": target,
                    "entity_type": self._map_project_entity_type(
                        str(entry.get("category", "")),
                        context=str(entry.get("context", "")),
                        source=source,
                    ),
                }
            )
        return locked

    def _load_character_locked_entities(self, characters_path: Path) -> list[dict]:
        if not characters_path.exists():
            return []
        payload = json.loads(characters_path.read_text(encoding="utf-8"))
        locked: list[dict] = []
        for entry in payload.get("characters", []):
            source = str(entry.get("name_source", "")).strip()
            target = str(entry.get("name_target", "")).strip()
            if not source or not target:
                continue
            locked.append(
                {
                    "source": source,
                    "target": target,
                    "entity_type": "person",
                }
            )
        return locked

    @staticmethod
    def _map_project_entity_type(category: str, *, context: str = "", source: str = "") -> str:
        normalized = " ".join(part for part in (category, context, source) if part).lower()
        if any(token in normalized for token in ("street", "road", "city", "village", "town", "district", "county", "province")):
            return "location"
        if source.endswith(("街", "路", "巷", "村", "镇", "市", "县", "省", "区", "楼", "大厦", "写字楼")):
            return "location"
        if any(token in normalized for token in ("org", "organization", "company", "school", "academy", "college", "university", "hospital", "bookstore", "bank", "building", "library")):
            return "organization"
        if source.endswith(("学院", "大学", "学校", "中学", "小学", "书店", "公司", "医院", "银行")):
            return "organization"
        if "person" in normalized or "name" in normalized:
            return "person"
        return "project_term"

    @staticmethod
    def _drop_shadowed_prefix_entities(locked_entities: dict[str, dict], external_items: list[dict]):
        protected_sources = {
            item["source"]
            for item in external_items
            if item.get("source") and item.get("entity_type") in {"organization", "location", "project_term"}
        }
        for source, item in list(locked_entities.items()):
            if source in protected_sources:
                continue
            if item.get("entity_type") != "person":
                continue
            for protected_source in protected_sources:
                if len(protected_source) <= len(source):
                    continue
                if not protected_source.startswith(source):
                    continue
                next_char = protected_source[len(source):len(source) + 1]
                if next_char and "\u4e00" <= next_char <= "\u9fff":
                    locked_entities.pop(source, None)
                    break
