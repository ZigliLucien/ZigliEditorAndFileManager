"""v101: authenticated Okular reverse-search handoff to Tk-safe queue."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import socket
import unittest

from zefm.editor.inverse_synctex import (
    InverseSynctexServer, send_location, validate_location)


class InverseSynctexTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "cœur ייִדיש.tex"
        self.source.write_text("hello", encoding="utf-8")
        self.state = self.root / "settings" / "inverse.json"
        self.server = InverseSynctexServer(state_path=self.state)
        self.server.start()
        self.addCleanup(self.server.close)

    def test_send_authorized_location(self):
        send_location(self.source, 23, 7, state_path=self.state)
        self.assertEqual(self.server.requests.get(timeout=2),
                         (str(self.source.resolve()), 23, 7))

    def test_wrong_token_does_not_queue_request(self):
        data = json.loads(self.state.read_text(encoding="utf-8"))
        with socket.create_connection(("127.0.0.1", data["port"]), timeout=2) as conn:
            conn.settimeout(2)
            conn.sendall(json.dumps({
                "token": "0" * 64,
                "path": str(self.source),
                "line": 5,
                "column": 1}).encode("utf-8") + b"\n")
            self.assertEqual(conn.recv(20), b"")
        self.assertTrue(self.server.requests.empty())

    def test_invalid_or_missing_tex_is_refused(self):
        for line in (0, -1, True, 10_000_001):
            with self.subTest(line=line), self.assertRaises(ValueError):
                validate_location(self.source, line)
        with self.assertRaises(ValueError):
            validate_location(self.root / "missing.tex", 1)
        with self.assertRaises(ValueError):
            validate_location(self.root / "other.pdf", 1)

    def test_state_is_removed_on_close(self):
        self.assertTrue(self.state.is_file())
        self.server.close()
        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
