"""v47: safe copy/create-directory regression tests for ServPakDir's file manager."""
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.file_manager import BrowserError, LocalFiles, MAX_COPY_BYTES
from zefm.server.http import BrowserServer


class LocalFileOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "files"
        self.root.mkdir()
        self.files = LocalFiles(self.root)
        self.source = self.root / "cœur ייִדיש.bin"
        self.data = b"binary\x00data\xFE" + "שלום".encode("utf-8")
        self.source.write_bytes(self.data)
        self.source.chmod(0o640)

    def test_unicode_directory_and_file_copy_preserves_original(self):
        directory = self.files.create_directory(".", "שלום français")
        self.assertEqual(directory, self.root / "שלום français")
        self.assertTrue(directory.is_dir())
        copied = self.files.copy_file(self.source.name, "קאָפּיע.bin")
        self.assertEqual(copied.read_bytes(), self.data)
        self.assertEqual(self.source.read_bytes(), self.data)
        self.assertEqual(stat.S_IMODE(copied.stat().st_mode), 0o640)
        self.assertNotEqual(copied, self.source)

    def test_no_overwrite_file_or_directory(self):
        destination = self.root / "existing.txt"
        destination.write_text("leave me alone")
        with self.assertRaises(BrowserError) as error:
            self.files.create_directory(".", destination.name)
        self.assertEqual(error.exception.status, 409)
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file(self.source.name, destination.name)
        self.assertEqual(error.exception.status, 409)
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file(self.source.name, self.source.name)
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(destination.read_text(), "leave me alone")

    def test_invalid_new_names_and_traversal(self):
        invalid = ("", ".", "..", "../escape", "/absolute", "bad/name",
                   "bad\\name", "bad\nname", "x" * 256, "יי" * 200)
        for name in invalid:
            with self.subTest(name=name), self.assertRaises(BrowserError):
                self.files.create_directory(".", name)
            with self.subTest(copy_name=name), self.assertRaises(BrowserError):
                self.files.copy_file(self.source.name, name)
        with self.assertRaises(BrowserError) as error:
            self.files.create_directory("..", "escape")
        self.assertEqual(error.exception.status, 403)
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file("../outside.bin", "copy.bin")
        self.assertEqual(error.exception.status, 403)

    def test_symlink_escape_and_existing_symlink_target(self):
        outside = Path(self.tmp.name) / "outside.bin"
        outside.write_bytes(b"secret")
        (self.root / "outside-link").symlink_to(outside)
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file("outside-link", "copy.bin")
        self.assertEqual(error.exception.status, 403)
        existing_link = self.root / "inside-link"
        existing_link.symlink_to(self.source)
        with self.assertRaises(BrowserError):
            self.files.copy_file(self.source.name, "inside-link")
        self.assertEqual(existing_link.read_bytes(), self.data)

    def test_oversize_copy_refused_without_partial_destination(self):
        huge = self.root / "huge.bin"
        with huge.open("wb") as stream:
            stream.truncate(MAX_COPY_BYTES + 1)
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file("huge.bin", "huge-copy.bin")
        self.assertEqual(error.exception.status, 413)
        self.assertFalse((self.root / "huge-copy.bin").exists())

    def test_collision_during_publish_removes_private_temp_file(self):
        with patch("zefm.server.file_manager.os.link", side_effect=FileExistsError("race")):
            with self.assertRaises(BrowserError) as error:
                self.files.copy_file(self.source.name, "race.bin")
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(list(self.root.glob(".zefm-copy-*")), [])
        self.assertFalse((self.root / "race.bin").exists())


class BrowserFileOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "bonjour ייִדיש.txt"
        self.source.write_text("Bonjour שלום", encoding="utf-8")
        self.server = BrowserServer(str(self.root))
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, route, fields=None, host=None):
        body = urlencode(fields).encode("utf-8") if fields is not None else None
        req = Request(self.server.url.rstrip("/") + route, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"} if body else {})
        if host:
            req.add_header("Host", host)
        try:
            with urlopen(req, timeout=4) as result:
                return result.status, result.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_listing_and_folder_creation(self):
        status, html = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn('action="/mkdir"', html)
        self.assertIn('Copy...', html)
        self.assertIn(self.source.name, html)
        fields = {"csrf": self.server.token, "path": ".", "name": "שלום documents"}
        status, html = self.request("/mkdir", fields)
        self.assertEqual(status, 201)
        self.assertTrue((self.root / "שלום documents").is_dir())
        self.assertIn("שלום documents", html)
        status, _ = self.request("/mkdir", fields)
        self.assertEqual(status, 409)
        self.assertEqual(self.request("/mkdir", {**fields, "csrf": "invalid"})[0], 403)

    def test_file_copy_and_no_clobber(self):
        url = "/copy?" + urlencode({"path": self.source.name})
        status, html = self.request(url)
        self.assertEqual(status, 200)
        self.assertIn('action="/copy"', html)
        self.assertIn('name="name"', html)
        fields = {"csrf": self.server.token, "path": self.source.name,
                  "name": "קאָפּיע.txt"}
        status, html = self.request("/copy", fields)
        self.assertEqual(status, 201)
        self.assertEqual((self.root / "קאָפּיע.txt").read_text(encoding="utf-8"),
                         "Bonjour שלום")
        self.assertIn("קאָפּיע.txt", html)
        status, _ = self.request("/copy", fields)
        self.assertEqual(status, 409)
        self.assertEqual(self.source.read_text(encoding="utf-8"), "Bonjour שלום")

    def test_invalid_paths_and_forged_requests(self):
        fields = {"csrf": self.server.token, "path": "..", "name": "escape"}
        self.assertEqual(self.request("/mkdir", fields)[0], 403)
        self.assertFalse((self.root.parent / "escape").exists())
        self.assertEqual(self.request("/copy", {
            "csrf": self.server.token, "path": self.source.name,
            "name": "../escape"})[0], 400)
        self.assertEqual(self.request("/copy", {
            "csrf": self.server.token, "path": self.source.name,
            "name": "copy.txt", "extra": "forged"})[0], 400)
        self.assertEqual(self.request("/mkdir", {
            "csrf": self.server.token, "path": ".", "name": "new",
            "extra": "forged"})[0], 400)
        self.assertEqual(self.request("/mkdir", {
            "csrf": self.server.token, "path": ".", "name": "new",
        }, host="attacker.example")[0], 403)
        self.assertEqual(self.request("/mkdir")[0], 404)

    def test_html_escaping_of_new_name(self):
        name = '<img src=x onerror=alert(1)>'
        status, html = self.request("/mkdir", {
            "csrf": self.server.token, "path": ".", "name": name})
        self.assertEqual(status, 201)
        self.assertIn("&lt;img", html)
        self.assertNotIn(name, html)
        self.assertTrue((self.root / name).is_dir())


if __name__ == "__main__":
    unittest.main()
