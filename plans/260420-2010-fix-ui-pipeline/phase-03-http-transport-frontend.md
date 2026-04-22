# Phase 03: HTTP Transport Frontend

Status: ⬜ Pending
Dependencies: Phase 02 (HTTP bridge phải chạy được)

## Objective
Tạo `httpTransport.ts` và tích hợp vào transport cascade để browser mode tự động detect HTTP bridge.

## Requirements

### Functional
- [ ] `createHttpTransport()` probe health endpoint trước khi return
- [ ] `send()` gọi `POST /api/sidecar` qua `fetch()`
- [ ] Bridge URL configurable qua `VITE_BRIDGE_URL` env var
- [ ] Nếu HTTP bridge không chạy → throw error (cascade tiếp sang demo/browser)

### Non-Functional
- [ ] TypeScript strict mode — no `any` types
- [ ] Consistent error handling với tauriTransport pattern

## Implementation Steps

1. [ ] **Tạo `desktop/src/httpTransport.ts`**
   ```typescript
   import {
     PROTOCOL_VERSION,
     type CommandName,
     type CommandResponse,
     type Transport,
   } from "./protocol";

   const DEFAULT_BRIDGE_URL = "http://localhost:9721";

   const SUPPORTED_COMMANDS: CommandName[] = [
     "create_project", "list_projects", "open_project",
     "get_project_overview", "set_active_chapter", "set_translation_style",
     "import_file", "translate", "load_translation_artifacts",
     "run_qa", "load_qa_report", "load_learning_report",
     "search_dictionary_entries", "list_candidate_entries",
     "review_candidate_entry", "submit_natural_feedback",
     "list_candidate_rules", "review_candidate_rule",
   ];

   export async function createHttpTransport(): Promise<Transport> {
     const baseUrl = import.meta.env.VITE_BRIDGE_URL || DEFAULT_BRIDGE_URL;
     // Probe health endpoint
     const health = await fetch(`${baseUrl}/api/health`, { signal: AbortSignal.timeout(2000) });
     if (!health.ok) throw new Error("HTTP bridge health check failed");

     return {
       mode: "http",
       supportedCommands: SUPPORTED_COMMANDS,
       async send<T>(command: CommandName, payload: Record<string, unknown> = {}): Promise<CommandResponse<T>> {
         const requestJson = JSON.stringify({
           command, payload,
           request_id: `http-${Date.now()}`,
           protocol_version: PROTOCOL_VERSION,
         });
         const response = await fetch(`${baseUrl}/api/sidecar`, {
           method: "POST",
           headers: { "Content-Type": "application/json" },
           body: requestJson,
         });
         return await response.json() as CommandResponse<T>;
       },
     };
   }
   ```

2. [ ] **Extend `TransportMode` trong `protocol.ts`**
   ```diff
   -export type TransportMode = "browser" | "demo" | "tauri";
   +export type TransportMode = "browser" | "demo" | "http" | "tauri";
   ```

3. [ ] **Update cascade trong `transport.ts`**
   ```typescript
   import { createHttpTransport } from "./httpTransport";

   export async function createPreferredTransport(): Promise<Transport> {
     try {
       return await createTauriTransport();
     } catch {
       try {
         return await createHttpTransport();
       } catch {
         // HTTP bridge not running
       }
       if (import.meta.env.VITE_ENABLE_DEMO === "1") {
         return createDemoTransport();
       }
       return createBrowserTransport();
     }
   }
   ```

4. [ ] **Update status message trong `App.tsx`**
   - Thêm case cho `transport.mode === "http"`:
   ```typescript
   if (nextTransport.mode === "http") {
     setStatusMessage("HTTP bridge detected. Browser is connected to the live Python pipeline.");
     return;
   }
   ```

## Files to Create/Modify
- `desktop/src/httpTransport.ts` — **NEW** (~ 50 lines)
- `desktop/src/protocol.ts` — **MODIFY** (1 line: TransportMode union)
- `desktop/src/transport.ts` — **MODIFY** (+ import + try/catch block)
- `desktop/src/App.tsx` — **MODIFY** (+ 4 lines: status message for http mode)

## Test Criteria
- [ ] `npm run build` compiles successfully (no TypeScript errors)
- [ ] Khi HTTP bridge đang chạy + `npm run dev` → transport mode = "http"
- [ ] Khi HTTP bridge không chạy + `npm run dev` → fallback sang browser/demo
- [ ] `send()` returns valid `CommandResponse` from real pipeline

---
Next Phase: [phase-04-integration-scripts.md](./phase-04-integration-scripts.md)
