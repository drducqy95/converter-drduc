---
title: PreTranslationPipeline - ValueError Pattern
type: pattern
slug: pretranslationpipeline-valueerror-pattern
category: patterns
created: 2026-04-20T22:04:20
updated: 2026-04-20T22:04:20
status: active
source: /debug
tags: ["PreTranslationPipeline", "ValueError", "auto-generated"]
---

# PreTranslationPipeline - ValueError Pattern

> [!WARNING]
> **Origin:** `ERR_0003`
> **Module:** `PreTranslationPipeline` | **Type:** `ValueError`

## 🚨 The Issue

**Message:** 
```text
import_file failed: directory import ran splitter.split() per file causing wrong chapter mapping; also path existence was not validated causing misleading Unsupported format error
```

**Root Cause:** 
1) _prepare_directory called _chapters_from_source_file which splits chapters inside each file. 2) prepare() did not check path existence, so non-existent paths fell to _prepare_file branch. 3) Rust pick_import_path applied file extension filters even for folder picker.

## 🛠️ The Fix

1) _prepare_directory now creates 1 chapter per file without splitting. 2) prepare() validates path existence first. 3) Rust picker only applies file filter for file mode.

**Files Affected:**
- `src/pipeline/pretranslation_pipeline.py`
- `desktop/src-tauri/src/main.rs`

## 🛡️ Prevention

> [!TIP]
> - Check for similar issues in `PreTranslationPipeline` module
> - Add test case to prevent regression
