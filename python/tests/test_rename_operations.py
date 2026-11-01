"""v51 safe rename tests: preserve Notes, prevent overwrites/open-buffer hazards."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import unittest

from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.rename_ops import RenameManager
from zefm.server.http import BrowserServer
from zefm.storage.word_notes import WordNotes


class RenameTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "files"
        self.root.mkdir()
        self.notes = Path(self.tmp.name) / "notes.json"
        self.source = self.root / "cœur ייִדיש.txt"
        self.source.write_text("bonjour שלום", encoding="utf-8")
        WordNotes(self.notes).put(str(self.source), "שלום", "A precious annotation")
        self.manager = RenameManager(LocalFiles(self.root), self.notes)

    def test_rename_preserves_text_and_original_note(self):
        target, count = self.manager.rename(self.source.name, "נײַע נאָמען.txt")
        self.assertEqual(count, 1)
        self.assertFalse(self.source.exists())
        self.assertEqual(target.read_text(encoding="utf-8"), "bonjour שלום")
        notes = WordNotes(self.notes)
        self.assertEqual(notes.for_file(str(self.source)), [])
        self.assertEqual(notes.get(str(target), "שלום")["data"], "A precious annotation")

    def test_collision_never_overwrites_target_or_notes(self):
        dest = self.root / "taken.txt"
        dest.write_text("existing", encoding="utf-8")
        with self.assertRaises(BrowserError) as exc:
            self.manager.rename(self.source.name, dest.name)
        self.assertEqual(exc.exception.status, 409)
        self.assertEqual(dest.read_text(), "existing")
        self.assertTrue(self.source.exists())
        self.assertEqual(len(WordNotes(self.notes).for_file(str(self.source))), 1)

    def test_open_buffer_disables_rename(self):
        manager = RenameManager(LocalFiles(self.root), self.notes,
                                file_in_use=lambda path: path == self.source)
        with self.assertRaises(BrowserError) as exc:
            manager.rename(self.source.name, "other.txt")
        self.assertEqual(exc.exception.status, 409)
        self.assertTrue(self.source.exists())

    def test_bogus_names_and_symlink_source(self):
        for name in ("../escape", "/tmp/out", "", "bad\\name"):
            with self.subTest(name=name), self.assertRaises(BrowserError):
                self.manager.rename(self.source.name, name)
        with self.assertRaises(BrowserError) as exc:
            self.manager.rename(self.source.name, self.source.name)
        self.assertEqual(exc.exception.status, 409)
        (self.root / "link").symlink_to(self.source)
        with self.assertRaises(BrowserError):
            self.manager.rename("link", "other.txt")

    def test_failed_note_write_leaves_source_and_no_target(self):
        with patch.object(WordNotes, "_write", side_effect=OSError("no space")):
            with self.assertRaises(BrowserError) as exc:
                self.manager.rename(self.source.name, "other.txt")
        self.assertEqual(exc.exception.status, 500)
        self.assertTrue(self.source.exists())
        self.assertFalse((self.root / "other.txt").exists())
        self.assertEqual(len(WordNotes(self.notes).for_file(str(self.source))), 1)

    def test_failing_unlink_rolls_back_notes(self):
        original_unlink = __import__("os").unlink
        def fake_unlink(path, *args, **kwargs):
            if Path(path) == self.source:
                raise OSError("mock unlink failure")
            return original_unlink(path, *args, **kwargs)
        with patch("zefm.server.rename_ops.os.unlink", side_effect=fake_unlink):
            with self.assertRaises(BrowserError):
                self.manager.rename(self.source.name, "other.txt")
        self.assertTrue(self.source.exists())
        self.assertFalse((self.root / "other.txt").exists())
        self.assertEqual(len(WordNotes(self.notes).for_file(str(self.source))), 1)

    def test_notes_collision_without_destination_file(self):
        target = self.root / "old-name.txt"
        WordNotes(self.notes).put(str(target), "someword", "prior record")
        with self.assertRaises(BrowserError) as exc:
            self.manager.rename(self.source.name, target.name)
        self.assertEqual(exc.exception.status, 409)
        self.assertTrue(self.source.exists())


class RenameBrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "research.txt"
        self.source.write_text("test")
        self.notes = self.root / "notes.json"
        self.browser = BrowserServer(str(self.root), notes_path=self.notes)
        self.browser.start()
        self.addCleanup(self.browser.close)

    def request(self, route, data=None):
        body = urlencode(data).encode("utf-8") if data is not None else None
        req = Request(self.browser.url.rstrip("/") + route, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"} if body else {})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_rename_form_and_submit(self):
        status, html = self.request("/rename?path=research.txt")
        self.assertEqual(status, 200)
        self.assertIn('action="/rename"', html)
        fields = {"csrf": self.browser.token, "path": "research.txt", "name": "renamed.txt"}
        status, html = self.request("/rename", fields)
        self.assertEqual(status, 200)
        self.assertIn("Renamed to:", html)
        self.assertTrue((self.root / "renamed.txt").is_file())
        self.assertFalse(self.source.exists())

    def test_csrf_and_path_traversal(self):
        fields = {"csrf": "wrong", "path": "research.txt", "name": "other.txt"}
        self.assertEqual(self.request("/rename", fields)[0], 403)
        self.assertEqual(self.request("/rename", {**fields, "csrf": self.browser.token,
                                                  "path": "../other.txt"})[0], 403)
        self.assertEqual(self.request("/rename", {**fields, "csrf": self.browser.token,
                                                  "name": "../other.txt"})[0], 400)
        self.assertTrue(self.source.exists())

    def test_listings_expose_rename(self):
        code, html = self.request("/")
        self.assertEqual(code, 200)
        self.assertIn("Rename...", html)
        code, html = self.request("/listing")
        self.assertEqual(code, 200)
        self.assertIn('value="rename"', html)


if __name__ == "__main__":
    unittest.main()
