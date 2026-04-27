---
title: desktop-ui-transport - ConfigurationError Pattern
type: pattern
slug: desktop-ui-transport-configurationerror-pattern
category: patterns
created: 2026-04-20T19:50:00
updated: 2026-04-20T19:50:00
status: active
source: /debug
tags: ["desktop-ui-transport", "ConfigurationError", "auto-generated"]
---

# desktop-ui-transport - ConfigurationError Pattern

> [!WARNING]
> **Origin:** `ERR_0001`
> **Module:** `desktop-ui-transport` | **Type:** `ConfigurationError`

## 🚨 The Issue

**Message:** 
```text
UI operations fail because browserTransport returns error for all commands - Tauri binary not built
```

**Root Cause:** 
User runs npm run dev (browser-only) instead of tauri:dev. createPreferredTransport falls back to browserTransport which rejects all sidecar commands

## 🛠️ The Fix

Run npm run tauri:dev to start with Tauri runtime, or add HTTP bridge for browser mode development

**Files Affected:**
- `desktop/src/transport.ts`
- `desktop/src/browserTransport.ts`
- `desktop/src-tauri/src/main.rs`

## 🛡️ Prevention

> [!TIP]
> - Check for similar issues in `desktop-ui-transport` module
> - Add test case to prevent regression
