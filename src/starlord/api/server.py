"""Local API server (minimal)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Callable


class _Handler(BaseHTTPRequestHandler):
    agent_handler: Callable[[str], str]

    def _write(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            self._write(200, {"ok": True})
            return
        self._write(404, {"error": "not_found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/chat":
            self._write(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body or "{}")
        text = data.get("text", "")
        response = self.agent_handler(text)
        self._write(200, {"response": response})


class LocalAPIServer:
    def __init__(self, host: str, port: int, handler: Callable[[str], str]) -> None:
        self.host = host
        self.port = port
        self.handler = handler
        self._server: HTTPServer | None = None
        self._thread: Thread | None = None

    def start(self) -> None:
        _Handler.agent_handler = self.handler
        self._server = HTTPServer((self.host, self.port), _Handler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
