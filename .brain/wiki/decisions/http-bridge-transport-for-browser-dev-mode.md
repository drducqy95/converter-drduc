---
title: HTTP Bridge Transport for Browser Dev Mode
type: decision
slug: http-bridge-transport-for-browser-dev-mode
category: decisions
created: 2026-04-20T20:13:21
updated: 2026-04-20T20:13:21
status: active
source: /plan
tags: ["fix-ui-pipeline", "architecture", "auto"]
---

# HTTP Bridge Transport for Browser Dev Mode

Context: UI pipeline fails in browser mode due to browserTransport blocking all sidecar commands. Rationale: Add Python stdlib http.server bridge (zero deps) that wraps sidecar_bridge.handle_request(). Alternatives: (1) Always use tauri:dev — rejected because Rust build adds friction for frontend-only changes. (2) WebSocket bridge — over-engineered for request-response pattern. Impact: Enables npm run dev with real pipeline access via port 9721.
