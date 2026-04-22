#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared command protocol for the desktop sidecar bridge."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


PROTOCOL_VERSION = "2026-04-16.phase10"


@dataclass(slots=True)
class CommandRequest:
    command: str
    payload: dict = field(default_factory=dict)
    request_id: str = "req-1"
    protocol_version: str = PROTOCOL_VERSION


@dataclass(slots=True)
class CommandEvent:
    stage: str
    message: str
    progress: int
    level: str = "info"
    payload: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class CommandResponse:
    ok: bool
    command: str
    request_id: str = "req-1"
    protocol_version: str = PROTOCOL_VERSION
    data: dict = field(default_factory=dict)
    error: str = ""
    warnings: list[str] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def success(
        cls,
        request: CommandRequest,
        *,
        data: dict | None = None,
        warnings: list[str] | None = None,
        events: list[CommandEvent | dict] | None = None,
    ) -> "CommandResponse":
        return cls(
            ok=True,
            command=request.command,
            request_id=request.request_id,
            protocol_version=request.protocol_version,
            data=data or {},
            warnings=warnings or [],
            events=[event.to_dict() if isinstance(event, CommandEvent) else event for event in (events or [])],
        )

    @classmethod
    def failure(
        cls,
        request: CommandRequest,
        *,
        error: str,
        warnings: list[str] | None = None,
        events: list[CommandEvent | dict] | None = None,
    ) -> "CommandResponse":
        return cls(
            ok=False,
            command=request.command,
            request_id=request.request_id,
            protocol_version=request.protocol_version,
            error=error,
            warnings=warnings or [],
            events=[event.to_dict() if isinstance(event, CommandEvent) else event for event in (events or [])],
        )
