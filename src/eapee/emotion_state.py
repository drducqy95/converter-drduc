#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scene-level emotion state with decay."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EmotionState:
    dominant: str = "neutral"
    intensity: float = 0.0
    history: list[str] = field(default_factory=list)


class EmotionStateMachine:
    """Maintain emotion drift across contiguous dialogue scenes."""

    def __init__(self, decay: float = 0.15):
        self.decay = decay
        self.state = EmotionState()

    def update(self, label: str, score: float) -> EmotionState:
        if label == self.state.dominant:
            self.state.intensity = min(1.0, max(self.state.intensity, score))
        elif score >= max(0.35, self.state.intensity - self.decay):
            self.state.dominant = label
            self.state.intensity = score
        else:
            self.state.intensity = max(0.0, self.state.intensity - self.decay)
        self.state.history.append(label)
        self.state.history = self.state.history[-10:]
        return self.state

    def reset(self):
        self.state = EmotionState()
