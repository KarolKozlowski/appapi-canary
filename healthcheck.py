#!/usr/bin/env python3
import socket
import sys

SOCKET_PATH = "/tmp/exapp.sock"
REQUEST = b"GET /heartbeat HTTP/1.0\r\nHost: localhost\r\n\r\n"

try:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(2)
        client.connect(SOCKET_PATH)
        client.sendall(REQUEST)
        response = client.recv(256)
except (OSError, TimeoutError) as error:
    print(f"Healthcheck failed: {error}", file=sys.stderr)
    raise SystemExit(1)

if b" 200 " not in response.split(b"\r\n", 1)[0]:
    print(response.decode("utf-8", errors="replace"), file=sys.stderr)
    raise SystemExit(1)
