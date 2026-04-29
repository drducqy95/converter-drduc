#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import raw documents into the standard project layout."""

from __future__ import annotations

import html
import json
import re
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path


SUPPORTED_ENCODINGS = ("utf-8", "utf-8-sig", "utf-16", "gb18030", "gbk", "big5")
DEFAULT_MAX_INPUT_BYTES = 100 * 1024 * 1024


@dataclass(slots=True)
class ImportedDocument:
    source_path: str
    detected_format: str
    detected_encoding: str
    raw_text: str
    normalized_text: str
    notes: list[str]


class ImportValidationError(ValueError):
    """Structured validation error for malformed or unsafe source documents."""

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


class DocumentImporter:
    """Import TXT/MD/HTML/DOCX/PDF into normalized text."""

    def __init__(self, *, max_file_size_bytes: int = DEFAULT_MAX_INPUT_BYTES):
        self.max_file_size_bytes = max_file_size_bytes

    def import_file(self, filepath: str | Path, output_dir: str | Path | None = None) -> ImportedDocument:
        path = Path(filepath)
        self._validate_source_path(path)
        suffix = path.suffix.lower()

        if suffix in {".txt", ".md", ".markdown"}:
            raw_text, encoding = self._read_text_file(path)
            fmt = suffix.lstrip(".")
        elif suffix in {".html", ".htm"}:
            raw_text, encoding = self._read_text_file(path)
            raw_text = self._strip_html(raw_text)
            fmt = "html"
        elif suffix == ".docx":
            raw_text = self._read_docx(path)
            encoding = "zip-xml"
            fmt = "docx"
        elif suffix == ".pdf":
            raw_text = self._read_pdf(path)
            encoding = "pdf"
            fmt = "pdf"
        else:
            raise ValueError(f"Unsupported input format: {suffix}")

        self._validate_text(raw_text, source_path=path)
        normalized = self._normalize_text(raw_text)
        notes = []
        if raw_text != normalized:
            notes.append("whitespace_normalized")

        imported = ImportedDocument(
            source_path=str(path),
            detected_format=fmt,
            detected_encoding=encoding,
            raw_text=raw_text,
            normalized_text=normalized,
            notes=notes,
        )

        if output_dir:
            self.write_import(imported, output_dir)

        return imported

    def write_import(self, imported: ImportedDocument, output_dir: str | Path):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        raw_dir = output_path / "source" / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_target = raw_dir / (Path(imported.source_path).stem + ".txt")
        meta_target = raw_dir / (Path(imported.source_path).stem + ".meta.json")
        raw_target.write_text(imported.normalized_text, encoding="utf-8")
        meta_target.write_text(json.dumps(asdict(imported), ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_text_file(self, path: Path) -> tuple[str, str]:
        content = path.read_bytes()
        for encoding in SUPPORTED_ENCODINGS:
            try:
                return content.decode(encoding), encoding
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace"), "utf-8-replace"

    def _validate_source_path(self, path: Path):
        if not path.exists():
            raise ImportValidationError(
                f"Source file does not exist: {path}",
                details={"path": str(path), "reason": "missing"},
            )
        if not path.is_file():
            raise ImportValidationError(
                f"Source path is not a file: {path}",
                details={"path": str(path), "reason": "not_file"},
            )
        size = path.stat().st_size
        if size > self.max_file_size_bytes:
            raise ImportValidationError(
                f"Source file is too large: {size} bytes",
                details={
                    "path": str(path),
                    "reason": "file_too_large",
                    "size_bytes": size,
                    "max_bytes": self.max_file_size_bytes,
                },
            )

    def _validate_text(self, text: str, *, source_path: Path):
        if "\x00" in text:
            raise ImportValidationError(
                f"Source text contains NULL characters: {source_path}",
                details={"path": str(source_path), "reason": "null_character"},
            )
        replacement_count = text.count("\ufffd")
        if replacement_count > max(20, len(text) // 100):
            raise ImportValidationError(
                f"Source text appears to have invalid encoding: {source_path}",
                details={
                    "path": str(source_path),
                    "reason": "invalid_encoding",
                    "replacement_chars": replacement_count,
                },
            )

    def _read_docx(self, path: Path) -> str:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
        text = re.sub(r"</w:p>", "\n", xml)
        text = re.sub(r"<[^>]+>", "", text)
        return html.unescape(text)

    def _read_pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader
        except Exception as exc:
            raise RuntimeError("PDF import requires `pypdf` in the environment") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _strip_html(self, content: str) -> str:
        cleaned = re.sub(r"<script[\s\S]*?</script>", "", content, flags=re.IGNORECASE)
        cleaned = re.sub(r"<style[\s\S]*?</style>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</p>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        return html.unescape(cleaned)

    def _normalize_text(self, text: str) -> str:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\ufeff", "")
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()
