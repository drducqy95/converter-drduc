import argparse
import json
import logging
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.ui.command_protocol import CommandRequest, PROTOCOL_VERSION
from src.ui.sidecar_bridge import SUPPORTED_COMMANDS, handle_request

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


class BridgeHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", self.server.cors_origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json_response(self, status: int, data: dict):
        response_body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json_response(200, {
                "ok": True,
                "version": PROTOCOL_VERSION,
                "pid": os.getpid(),
                "supported_commands": sorted(list(SUPPORTED_COMMANDS)),
            })
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()

    def do_POST(self):
        if self.path != "/api/sidecar":
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                raise ValueError("Empty body")
            body = self.rfile.read(content_length).decode("utf-8")
            request_data = json.loads(body)
        except Exception as exc:
            logging.error(f"Failed to parse request: {exc}")
            self._send_json_response(400, {"error": "Invalid JSON body"})
            return

        command = request_data.get("command")
        if not command:
            self._send_json_response(400, {"error": "Missing 'command' in request"})
            return

        command_request = CommandRequest(
            command=command,
            payload=request_data.get("payload", {}),
            request_id=request_data.get("request_id", f"http-{time.time()}"),
            protocol_version=request_data.get("protocol_version", PROTOCOL_VERSION),
        )

        try:
            started_at = time.time()
            response = handle_request(command_request)
            latency = int((time.time() - started_at) * 1000)
            
            status_desc = "ok" if response.ok else "error"
            logging.info(f"command={command} status={status_desc} latency={latency}ms")
            
            self._send_json_response(200, response.to_dict())
        except Exception as exc:
            logging.error(f"Internal error handling {command}: {exc}")
            self._send_json_response(500, {"error": "Internal server error", "details": str(exc)})

    def log_message(self, format, *args):
        # Override to suppress default HTTP server logging if desired, or map to logging module
        pass


def main():
    parser = argparse.ArgumentParser(description="Trinity HTTP Bridge for Translation Pipeline")
    parser.add_argument("--port", type=int, default=9721, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind to")
    parser.add_argument("--cors-origin", type=str, default="*", help="Allowed CORS origin")
    args = parser.parse_args()

    # Create server
    server_address = (args.host, args.port)
    server = ThreadingHTTPServer(server_address, BridgeHandler)
    server.cors_origin = args.cors_origin

    logging.info(f"HTTP bridge listening on http://{args.host}:{args.port} (CORS: {args.cors_origin})")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down HTTP bridge...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
