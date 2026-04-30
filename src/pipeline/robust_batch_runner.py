#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fault-isolated batch translation runner."""

from __future__ import annotations

import concurrent.futures
import json
import re
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class ChapterStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass(slots=True)
class ChapterInput:
    chapter_id: str
    text: str
    num: int | None = None
    config: dict[str, Any] = field(default_factory=dict)
    output_path: str | None = None


@dataclass(slots=True)
class BatchConfig:
    checkpoint_interval: int = 10
    circuit_breaker_threshold: int = 5
    chapter_timeout_seconds: float | None = None
    output_dir: str | Path | None = None
    checkpoint_path: str | Path | None = None
    translator_config: dict[str, Any] = field(default_factory=dict)
    continue_on_failure: bool = True
    reset_context_on_chapter: bool = True


@dataclass(slots=True)
class ChapterResult:
    chapter_id: str
    status: ChapterStatus
    duration_seconds: float = 0.0
    error_type: str | None = None
    error_detail: str | None = None
    output_path: str | None = None
    segments_translated: int = 0
    tm_reuse_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "chapter_id": self.chapter_id,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "error_type": self.error_type,
            "error_detail": self.error_detail,
            "output_path": self.output_path,
            "segments_translated": self.segments_translated,
            "tm_reuse_rate": self.tm_reuse_rate,
        }


@dataclass(slots=True)
class BatchReport:
    results: dict[str, ChapterResult]
    ordered_ids: list[str]
    stopped_early: bool = False
    stop_reason: str | None = None

    @property
    def success_count(self) -> int:
        return sum(1 for result in self.results.values() if result.status == ChapterStatus.SUCCESS)

    @property
    def failed_count(self) -> int:
        return sum(1 for result in self.results.values() if result.status == ChapterStatus.FAILED)

    @property
    def timeout_count(self) -> int:
        return sum(1 for result in self.results.values() if result.status == ChapterStatus.TIMEOUT)

    @property
    def completed_count(self) -> int:
        return len(self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "timeout_count": self.timeout_count,
            "completed_count": self.completed_count,
            "stopped_early": self.stopped_early,
            "stop_reason": self.stop_reason,
            "ordered_ids": self.ordered_ids,
            "results": {chapter_id: self.results[chapter_id].to_dict() for chapter_id in self.ordered_ids},
        }


def run_batch_with_fault_isolation(
    chapters: list[Any],
    translator: Any,
    config: BatchConfig | None = None,
) -> BatchReport:
    """Translate chapters while isolating per-chapter failures."""
    batch_config = config or BatchConfig()
    results: dict[str, ChapterResult] = {}
    ordered_ids: list[str] = []
    consecutive_failures = 0
    stopped_early = False
    stop_reason: str | None = None

    for index, chapter in enumerate(chapters, start=1):
        chapter_id = _chapter_id(chapter, index)
        result = _translate_chapter_safe(chapter, translator, batch_config, index=index)
        results[chapter_id] = result
        ordered_ids.append(chapter_id)

        if result.status == ChapterStatus.SUCCESS:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if not batch_config.continue_on_failure:
                stopped_early = True
                stop_reason = f"stopped_after_failure:{chapter_id}"
                break
            if consecutive_failures >= batch_config.circuit_breaker_threshold:
                stopped_early = True
                stop_reason = f"circuit_breaker:{consecutive_failures}"
                break

        if batch_config.checkpoint_interval > 0 and index % batch_config.checkpoint_interval == 0:
            _save_checkpoint(BatchReport(results, ordered_ids), batch_config)

    report = BatchReport(
        results=results,
        ordered_ids=ordered_ids,
        stopped_early=stopped_early,
        stop_reason=stop_reason,
    )
    _save_checkpoint(report, batch_config)
    return report


def _translate_chapter_safe(
    chapter: Any,
    translator: Any,
    config: BatchConfig,
    *,
    index: int,
) -> ChapterResult:
    chapter_id = _chapter_id(chapter, index)
    start = time.monotonic()
    try:
        output = _run_with_optional_timeout(
            lambda: _translate_chapter(chapter, translator, config),
            timeout_seconds=config.chapter_timeout_seconds,
        )
        output_text = _output_text(output)
        output_path = _write_output(chapter, chapter_id, output_text, config)
        return ChapterResult(
            chapter_id=chapter_id,
            status=ChapterStatus.SUCCESS,
            duration_seconds=round(time.monotonic() - start, 3),
            output_path=output_path,
            segments_translated=_segment_count(output),
            tm_reuse_rate=_tm_reuse_rate(output),
        )
    except TimeoutError as exc:
        return ChapterResult(
            chapter_id=chapter_id,
            status=ChapterStatus.TIMEOUT,
            duration_seconds=round(time.monotonic() - start, 3),
            error_type=type(exc).__name__,
            error_detail=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 - deliberate per-chapter isolation
        return ChapterResult(
            chapter_id=chapter_id,
            status=ChapterStatus.FAILED,
            duration_seconds=round(time.monotonic() - start, 3),
            error_type=type(exc).__name__,
            error_detail="".join(traceback.format_exception_only(type(exc), exc)).strip(),
        )


def _run_with_optional_timeout(fn: Callable[[], Any], *, timeout_seconds: float | None) -> Any:
    if timeout_seconds is None or timeout_seconds <= 0:
        return fn()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout_seconds)
    except concurrent.futures.TimeoutError as exc:
        future.cancel()
        raise TimeoutError(f"Chapter exceeded timeout of {timeout_seconds:.2f}s") from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _translate_chapter(chapter: Any, translator: Any, config: BatchConfig) -> Any:
    if config.reset_context_on_chapter:
        context = getattr(translator, "context", None)
        reset = getattr(context, "reset_for_chapter", None)
        if callable(reset):
            reset()

    if hasattr(translator, "translate_chapter"):
        return translator.translate_chapter(chapter)

    chapter_config = dict(config.translator_config)
    chapter_config.update(_chapter_config(chapter))
    if hasattr(translator, "translate_text"):
        return translator.translate_text(_chapter_text(chapter), config=chapter_config)
    if callable(translator):
        return translator(chapter)
    raise TypeError("translator must expose translate_chapter(), translate_text(), or be callable")


def _chapter_id(chapter: Any, index: int) -> str:
    if isinstance(chapter, dict):
        value = chapter.get("chapter_id") or chapter.get("id") or chapter.get("name")
        if value:
            return str(value)
        path = chapter.get("path") or chapter.get("source_path")
        if path:
            return Path(path).stem
    for attr in ("chapter_id", "id", "name"):
        value = getattr(chapter, attr, None)
        if value:
            return str(value)
    path_value = getattr(chapter, "path", None) or getattr(chapter, "source_path", None)
    if path_value:
        return Path(path_value).stem
    return f"{index:04d}"


def _chapter_text(chapter: Any) -> str:
    if isinstance(chapter, str):
        path = Path(chapter)
        return path.read_text(encoding="utf-8") if path.exists() else chapter
    if isinstance(chapter, Path):
        return chapter.read_text(encoding="utf-8")
    if isinstance(chapter, dict):
        if "text" in chapter:
            return str(chapter["text"])
        path = chapter.get("path") or chapter.get("source_path")
        if path:
            return Path(path).read_text(encoding="utf-8")
    text = getattr(chapter, "text", None)
    if text is not None:
        return str(text)
    path_value = getattr(chapter, "path", None) or getattr(chapter, "source_path", None)
    if path_value:
        return Path(path_value).read_text(encoding="utf-8")
    raise ValueError(f"Chapter has no text or readable path: {_chapter_id(chapter, 0)}")


def _chapter_config(chapter: Any) -> dict[str, Any]:
    if isinstance(chapter, dict):
        return dict(chapter.get("config") or {})
    return dict(getattr(chapter, "config", {}) or {})


def _output_text(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        return str(output.get("clean_text") or output.get("text") or output.get("output_text") or "")
    return str(getattr(output, "clean_text", None) or getattr(output, "text", None) or output)


def _segment_count(output: Any) -> int:
    segments = output.get("segments") if isinstance(output, dict) else getattr(output, "segments", None)
    return len(segments or [])


def _tm_reuse_rate(output: Any) -> float:
    config = output.get("config") if isinstance(output, dict) else getattr(output, "config", None)
    if not isinstance(config, dict):
        return 0.0
    value = config.get("tm_reuse_rate", 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _write_output(chapter: Any, chapter_id: str, output_text: str, config: BatchConfig) -> str | None:
    explicit_output = None
    if isinstance(chapter, dict):
        explicit_output = chapter.get("output_path")
    else:
        explicit_output = getattr(chapter, "output_path", None)

    output_path: Path | None = Path(explicit_output) if explicit_output else None
    if output_path is None and config.output_dir is not None:
        output_path = Path(config.output_dir) / f"{_safe_filename(chapter_id)}.txt"
    if output_path is None:
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    return str(output_path)


def _save_checkpoint(report: BatchReport, config: BatchConfig):
    if config.checkpoint_path is None:
        return
    checkpoint_path = Path(config.checkpoint_path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _safe_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._")
    return safe or "chapter"
