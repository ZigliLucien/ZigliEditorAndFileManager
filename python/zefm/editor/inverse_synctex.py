"""Authenticated local inverse SyncTeX handoff from Okular to the Tk editor.

The editor listens only on 127.0.0.1. A random capability token is kept in
a private, atomically written state file. The server thread ONLY queues
requests: Tk operations happen on its main thread.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from queue import Queue
import secrets
import socket
import socketserver
import tempfile

DEFAULT_STATE = Path.home() / ".config" / "zefm" / "inverse_synctex.json"
MAX_MESSAGE = 8192


def validate_location(filename, line, column=1):
    if (not isinstance(filename, str) or not filename or "\x00" in filename
            or len(filename) > 4096):
        raise ValueError("Invalid inverse SyncTeX source filename")
    if type(line) is not int or not 1 <= line <= 10_000_000:
        raise ValueError("Invalid inverse SyncTeX line")
    if type(column) is not int or not 1 <= column <= 10_000_000:
        raise ValueError("Invalid inverse SyncTeX column")
    path = Path(filename).expanduser().resolve()
    if path.suffix.lower() != ".tex" or not path.is_file():
        raise ValueError("Inverse SyncTeX requires an existing .tex file")
    return str(path), line, column


def _read_state(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or type(data.get("port")) is not int
            or not 1 <= data["port"] <= 65535
            or not isinstance(data.get("token"), str)
            or len(data["token"]) != 64):
        raise ValueError("Invalid inverse SyncTeX server state")
    return data


def send_location(filename, line, column=1, *, state_path=None):
    path, row, col = validate_location(filename, line, column)
    state = _read_state(state_path or DEFAULT_STATE)
    payload = json.dumps({"token": state["token"], "path": path,
                          "line": row, "column": col},
                         ensure_ascii=False).encode("utf-8") + b"\n"
    with socket.create_connection(("127.0.0.1", state["port"]), timeout=3) as conn:
        conn.settimeout(3)
        conn.sendall(payload)
        response = conn.recv(64)
    if response != b"OK\n":
        raise ValueError("ZEFM rejected inverse SyncTeX request")


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        raw = self.rfile.readline(MAX_MESSAGE + 1)
        if len(raw) > MAX_MESSAGE or not raw.endswith(b"\n"):
            return
        try:
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict) or not secrets.compare_digest(
                    str(data.get("token", "")), self.server.token):
                return
            location = validate_location(
                data.get("path"), data.get("line"), data.get("column", 1))
        except (ValueError, TypeError, UnicodeDecodeError):
            return
        self.server.requests.put(location)
        self.wfile.write(b"OK\n")


class _Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = False
    daemon_threads = True


class InverseSynctexServer:
    def __init__(self, *, state_path=None):
        self.state_path = Path(state_path or DEFAULT_STATE).expanduser()
        self.requests = Queue()
        self.token = secrets.token_hex(32)
        self.server = None

    def start(self):
        if self.server is not None:
            return
        server = _Server(("127.0.0.1", 0), _Handler)
        server.requests = self.requests
        server.token = self.token
        tmp = None
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", prefix=".inverse-synctex-",
                    suffix=".tmp", dir=self.state_path.parent, delete=False) as output:
                tmp = Path(output.name)
                if os.name == "posix":
                    os.fchmod(output.fileno(), 0o600)
                json.dump({"port": server.server_address[1],
                           "token": self.token}, output)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(tmp, self.state_path)
            self.server = server
            import threading
            threading.Thread(target=server.serve_forever, daemon=True,
                             name="zefm-inverse-synctex").start()
        except Exception:
            server.server_close()
            raise
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)

    def close(self):
        if self.server is None:
            return
        self.server.shutdown()
        self.server.server_close()
        self.server = None
        try:
            data = _read_state(self.state_path)
            if data["token"] == self.token:
                self.state_path.unlink(missing_ok=True)
        except (OSError, ValueError):
            pass
