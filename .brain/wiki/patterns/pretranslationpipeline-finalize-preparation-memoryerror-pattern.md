---
title: PreTranslationPipeline._finalize_preparation - MemoryError Pattern
type: pattern
slug: pretranslationpipeline-finalize-preparation-memoryerror-pattern
category: patterns
created: 2026-04-21T11:59:00
updated: 2026-04-21T15:50:13
status: active
source: /debug
tags: ["PreTranslationPipeline._finalize_preparation", "MemoryError", "auto-generated"]
---

# PreTranslationPipeline._finalize_preparation - MemoryError Pattern

> [!WARNING]
> **Origin:** `ERR_0004`
> **Module:** `PreTranslationPipeline._finalize_preparation` | **Type:** `MemoryError`

## 🚨 The Issue

**Message:** 
```text
MemoryError in relationship_builder.build() when importing directory with 774 files
```

**Root Cause:** 
O(n^2) entity pair loop in relationship_builder.build() on concatenated text from 774 source files exhausts process memory

## 🛠️ The Fix

Added MAX_ANALYSIS_CHARS=500000 constant; _finalize_preparation now truncates text before passing to entity_scanner and relationship_builder

**Files Affected:**
- `src/pipeline/pretranslation_pipeline.py`
- `src/pipeline/relationship_builder.py`

## 🛡️ Prevention

> [!TIP]
> - Check for similar issues in `PreTranslationPipeline._finalize_preparation` module
> - Add test case to prevent regression



---

### 🐛 Occurrence: ERR_0005 (2026-04-21)

**Error:** `MemoryError in json.dumps when serializing 37119 relationships from 5.2MB HTML entity scan`

**Root Cause:** entity_scanner produces too many entities from 500K analysis text; relationship_builder O(n^2) creates 37K+ edges; json.dumps on the resulting config dict exceeds memory

**Fix:** Added MAX_ENTITIES=200 and MAX_RELATIONSHIPS=500 caps in _finalize_preparation; entities sorted by frequency, relationships sorted by confidence

**Files:** `src/pipeline/pretranslation_pipeline.py`, `src/ui/sidecar_bridge.py`

