from http.server import BaseHTTPRequestHandler
from socketserver import UnixStreamServer
from pathlib import Path
import json
import os

SOCKET_PATH = "/tmp/exapp.sock"


class Handler(BaseHTTPRequestHandler):
    def reply(self, payload: dict[str, str]) -> None:
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/heartbeat":
            self.reply({"status": "ok"})
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/init":
            self.reply({"status": "ok"})
            return
        self.send_error(404)

    def do_PUT(self) -> None:
        if self.path.startswith("/enabled"):
            self.reply({"status": "ok"})
            return
        self.send_error(404)

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


try:
    Path(SOCKET_PATH).unlink()
except FileNotFoundError:
    pass

server = UnixStreamServer(SOCKET_PATH, Handler)
os.chmod(SOCKET_PATH, 0o666)
server.serve_forever()