#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import smoke tests for modules that used to be exercised by a root script."""

from src.pipeline.pretranslation_pipeline import PreTranslationPipeline


def test_pretranslation_pipeline_is_importable():
    assert PreTranslationPipeline is not None
