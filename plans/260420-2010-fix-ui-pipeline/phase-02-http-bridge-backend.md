# Phase 02: HTTP Bridge Backend

Status: ⬜ Pending
Dependencies: None (song song với Phase 01)

## Objective
Tạo Python HTTP server sử dụng stdlib `http.server` để wrap `sidecar_bridge.handle_request()`, cho phép browser gọi pipeline qua HTTP.

## Requirements

### Functional
- [ ] `GET /api/health` trả về `{"ok": true, "version": "...", "pid": ...}`
- [ ] `POST /api/sidecar` nhận JSON body → gọi `handle_request()` → trả JSON response
- [ ] CORS headers cho phép `localhost:5173` gọi được
- [ ] Graceful shutdown khi nhận SIGINT/SIGTERM

### Non-Functional
- [ ] Zero external dependencies (chỉ dùng stdlib)
- [ ] Latency < 100ms overhead (so với direct Python call)
- [ ] Thread-safe (dùng `ThreadingHTTPServer` cho concurrent requests)

## Implementation Steps

1. [ ] **Tạo `src/ui/http_bridge.py`**
   - Import: `http.server`, `json`, `sys`, `argparse`, `threading`
   - Class `BridgeHandler(BaseHTTPRequestHandler)`:
     - `do_GET()`: handle `/api/health`
     - `do_POST()`: handle `/api/sidecar`
     - `do_OPTIONS()`: handle CORS preflight
     - `_send_cors_headers()`: helper gộp CORS headers
     - `_send_json_response(status, data)`: helper gộp JSON response
   - `main()`:
     - `argparse`: `--port 9721`, `--host 0.0.0.0`, `--cors-origin *`
     - Tạo `ThreadingHTTPServer`
     - Print banner: `HTTP bridge listening on http://host:port`
     - `server.serve_forever()` với `KeyboardInterrupt` handler

2. [ ] **Implement health endpoint**
   ```python
   def do_GET(self):
       if self.path == "/api/health":
           self._send_json_response(200, {
               "ok": True,
               "version": PROTOCOL_VERSION,
               "pid": os.getpid(),
               "supported_commands": SUPPORTED_COMMANDS,
           })
   ```

3. [ ] **Implement sidecar endpoint**
   ```python
   def do_POST(self):
       if self.path == "/api/sidecar":
           content_length = int(self.headers["Content-Length"])
           body = self.rfile.read(content_length).decode("utf-8")
           request_data = json.loads(body)
           command_request = CommandRequest(
               command=request_data["command"],
               payload=request_data.get("payload", {}),
               request_id=request_data.get("request_id", f"http-{time.time()}"),
               protocol_version=request_data.get("protocol_version", PROTOCOL_VERSION),
           )
           response = handle_request(command_request)
           self._send_json_response(200, response.to_dict())
   ```

4. [ ] **Implement CORS handling**
   ```python
   def _send_cors_headers(self):
       self.send_header("Access-Control-Allow-Origin", self.server.cors_origin)
       self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
       self.send_header("Access-Control-Allow-Headers", "Content-Type")

   def do_OPTIONS(self):
       self.send_response(204)
       self._send_cors_headers()
       self.end_headers()
   ```

5. [ ] **Implement error handling & logging**
   - Wrap `do_POST` body parse trong try/except
   - Nếu JSON parse fail → 400 Bad Request
   - Nếu `handle_request` raise Exception → 500 Internal Server Error
   - Log mỗi request: `[timestamp] command=X status=ok/error latency=Yms`
   - Override `log_message()` cho format gọn

## Files to Create/Modify
- `src/ui/http_bridge.py` — **NEW** (~ 120 lines)

## Test Criteria
- [ ] `python -m src.ui.http_bridge --port 9721` starts without error
- [ ] `curl http://localhost:9721/api/health` returns `{"ok": true}`
- [ ] `curl -X POST http://localhost:9721/api/sidecar -d '{"command":"list_projects","payload":{"base_dir":"workspace_projects"}}'` returns projects
- [ ] CORS preflight `OPTIONS /api/sidecar` returns 204 with correct headers
- [ ] Invalid JSON body returns 400

---
Next Phase: [phase-03-http-transport-frontend.md](./phase-03-http-transport-frontend.md)
