"""v54 safe move tests for ServPakDir-style file management."""
import errno
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from unittest.mock import patch
import unittest

from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.rename_ops import RenameManager
from zefm.server.http import BrowserServer
from zefm.storage.word_notes import WordNotes


class MoveModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "root"
        self.root.mkdir()
        (self.root / "Documents").mkdir()
        (self.root / "Research").mkdir()
        self.source = self.root / "Documents" / "cœur ייִדיש.tex"
        self.source.write_text("שלום", encoding="utf-8")
        self.notes_path = Path(self.temp.name) / "notes.json"
        WordNotes(self.notes_path).put(str(self.source), "שלום", "annotation")
        self.moves = RenameManager(LocalFiles(self.root), self.notes_path)

    def test_move_preserves_notes_utf8_and_permissions(self):
        self.source.chmod(0o640)
        result, count = self.moves.move("Documents/cœur ייִדיש.tex", "Research")
        self.assertEqual(result, self.root / "Research" / "cœur ייִדיש.tex")
        self.assertEqual(count, 1)
        self.assertFalse(self.source.exists())
        self.assertEqual(result.read_text(encoding="utf-8"), "שלום")
        self.assertEqual(result.stat().st_mode & 0o777, 0o640)
        self.assertEqual(WordNotes(self.notes_path).get(str(result), "שלום")["data"], "annotation")
        self.assertIsNone(WordNotes(self.notes_path).get(str(self.source), "שלום"))

    def test_never_overwrites_existing_file_or_symlink(self):
        target = self.root / "Research" / self.source.name
        target.write_text("KEEP")
        with self.assertRaises(BrowserError) as caught:
            self.moves.move("Documents/" + self.source.name, "Research")
        self.assertEqual(caught.exception.status, 409)
        self.assertEqual(target.read_text(), "KEEP")
        target.unlink()
        target.symlink_to(self.source)
        with self.assertRaises(BrowserError):
            self.moves.move("Documents/" + self.source.name, "Research")
        self.assertTrue(self.source.exists())

    def test_invalid_destination(self):
        for destination in ("..", "../outside", "missing", "Documents"):
            with self.subTest(destination=destination), self.assertRaises(BrowserError):
                self.moves.move("Documents/" + self.source.name, destination)
        (self.root / "link").symlink_to(self.root / "Research")
        with self.assertRaises(BrowserError):
            self.moves.move("Documents/" + self.source.name, "link")
        self.assertTrue(self.source.exists())

    def test_open_file_and_cross_device_failure(self):
        busy = RenameManager(LocalFiles(self.root), self.notes_path,
                             file_in_use=lambda p: p == self.source)
        with self.assertRaises(BrowserError) as error:
            busy.move("Documents/" + self.source.name, "Research")
        self.assertEqual(error.exception.status, 409)
        with patch("zefm.server.rename_ops.os.link",
                   side_effect=OSError(errno.EXDEV, "cross-device")):
            with self.assertRaises(BrowserError):
                self.moves.move("Documents/" + self.source.name, "Research")
        self.assertTrue(self.source.exists())
        self.assertFalse((self.root / "Research" / self.source.name).exists())

    def test_failed_notes_write_rolls_back_file(self):
        with patch.object(WordNotes, "_write", side_effect=OSError("disk full")):
            with self.assertRaises(BrowserError):
                self.moves.move("Documents/" + self.source.name, "Research")
        self.assertTrue(self.source.exists())
        self.assertFalse((self.root / "Research" / self.source.name).exists())


class MoveBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "Docs").mkdir()
        (self.root / "Archive").mkdir()
        self.source = self.root / "Docs" / "paper.txt"
        self.source.write_text("research")
        self.browser = BrowserServer(str(self.root))
        self.browser.start()
        self.addCleanup(self.browser.close)

    def request(self, route, fields=None):
        body = urlencode(fields).encode("utf-8") if fields is not None else None
        req = Request(self.browser.url.rstrip("/") + route, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"} if body else {})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def test_form_action_and_listing(self):
        status, html = self.request("/move?" + urlencode({"path": "Docs/paper.txt"}))
        self.assertEqual(status, 200)
        self.assertIn('action="/move"', html)
        self.assertIn('name="destination"', html)
        self.assertIn("No file will be overwritten", html)
        status, html = self.request("/browse?path=Docs")
        self.assertEqual(status, 200)
        self.assertIn("Move...", html)
        status, html = self.request("/listing")
        self.assertEqual(status, 200)
        self.assertIn('value="move"', html)
        self.assertNotIn('value="move" disabled', html)

    def test_move_form_with_return_location(self):
        back = "/listing?" + urlencode({"path": "Docs", "page": "1",
                                         "sort": "filename", "filter": "paper"})
        fields = {"csrf": self.browser.token, "path": "Docs/paper.txt",
                  "destination": "Archive", "back": back}
        status, html = self.request("/move", fields)
        self.assertEqual(status, 200, html)
        self.assertFalse(self.source.exists())
        self.assertTrue((self.root / "Archive" / "paper.txt").exists())
        self.assertIn("Return to previous listing", html)
        self.assertIn("Open destination directory", html)
        self.assertIn(back.replace("&", "&amp;"), html)

    def test_csrf_traversal_and_bad_field(self):
        original = {"csrf": self.browser.token, "path": "Docs/paper.txt",
                    "destination": "Archive"}
        self.assertEqual(self.request("/move", {**original, "csrf": "bad"})[0], 403)
        self.assertEqual(self.request("/move", {**original, "destination": "../"})[0], 403)
        self.assertEqual(self.request("/move", {**original, "extra": "bad"})[0], 400)
        self.assertTrue(self.source.exists())


if __name__ == "__main__":
    unittest.main()
