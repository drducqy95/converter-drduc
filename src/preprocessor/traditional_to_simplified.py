#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compatibility import for Traditional -> Simplified conversion."""

from src.engine.traditional_to_simplified import ConversionTrace, TraditionalToSimplifiedConverter


class TraditionalToSimplified(TraditionalToSimplifiedConverter):
    """Legacy class name kept after removing the JavaScript module."""


__all__ = ["ConversionTrace", "TraditionalToSimplified", "TraditionalToSimplifiedConverter"]
