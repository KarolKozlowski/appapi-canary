from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def reply(self, payload):
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/heartbeat":
            return self.reply({"status": "ok"})
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path in ("/init", "/enabled"):
            return self.reply({"status": "ok"})
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()