"""Source-guided copy-to-directory regression tests (XCommands.runC)."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import os
import stat
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.http import BrowserServer


class CopyToDirectoryModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "root"
        (self.root / "source").mkdir(parents=True)
        (self.root / "destination").mkdir()
        self.path = self.root / "source" / "שלום cœur.txt"
        self.path.write_text("Bonjour ייִדיש\n", encoding="utf-8")
        self.path.chmod(0o640)
        self.files = LocalFiles(self.root)

    def test_copy_to_other_directory_preserves_data_mode_and_source(self):
        target = self.files.copy_file("source/שלום cœur.txt", "copy ייִדיש.txt", "destination")
        self.assertEqual(target, self.root / "destination" / "copy ייִדיש.txt")
        self.assertEqual(target.read_bytes(), self.path.read_bytes())
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)
        self.assertTrue(self.path.exists())
        self.assertEqual(list((self.root / "destination").glob(".zefm-copy-*")), [])

    def test_copy_without_destination_keeps_legacy_same_directory_behavior(self):
        target = self.files.copy_file("source/שלום cœur.txt", "Copy.txt")
        self.assertEqual(target.parent, self.path.parent)
        self.assertEqual(target.read_bytes(), self.path.read_bytes())

    def test_existing_file_directory_and_symlink_are_untouched(self):
        target = self.root / "destination" / "copy.txt"
        target.write_text("DO NOT TOUCH", encoding="utf-8")
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file("source/שלום cœur.txt", "copy.txt", "destination")
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(target.read_text(), "DO NOT TOUCH")
        target.unlink()
        target.symlink_to(self.path)
        with self.assertRaises(BrowserError) as error:
            self.files.copy_file("source/שלום cœur.txt", "copy.txt", "destination")
        self.assertEqual(error.exception.status, 409)
        self.assertTrue(target.is_symlink())
        self.assertEqual(self.path.read_text(encoding="utf-8"), "Bonjour ייִדיש\n")

    def test_destination_restrictions(self):
        (self.root / "destination-link").symlink_to(self.root / "destination")
        for location in ("..", "../escape", "/tmp", "destination-link", "missing"):
            with self.subTest(destination=location), self.assertRaises(BrowserError):
                self.files.copy_file("source/שלום cœur.txt", "new.txt", location)
        self.assertFalse((self.root / "destination" / "new.txt").exists())

    def test_no_partial_file_on_failed_publish(self):
        with patch("zefm.server.file_manager.os.link", side_effect=FileExistsError("race")):
            with self.assertRaises(BrowserError) as caught:
                self.files.copy_file("source/שלום cœur.txt", "copy.txt", "destination")
        self.assertEqual(caught.exception.status, 409)
        self.assertEqual(list((self.root / "destination").glob(".zefm-copy-*")), [])
        self.assertTrue(self.path.exists())


class CopyToDirectoryHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "source").mkdir()
        (self.root / "archive").mkdir()
        (self.root / "source" / "notes.md").write_text("# Notes", encoding="utf-8")
        self.server = BrowserServer(str(self.root))
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, path, values=None):
        body = urlencode(values).encode("utf-8") if values is not None else None
        request = Request(
            self.server.url.rstrip("/") + path, data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"} if body is not None else {})
        try:
            with urlopen(request, timeout=4) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def test_form_and_destination_copy(self):
        status, html = self.request("/copy?path=source%2Fnotes.md")
        self.assertEqual(status, 200)
        self.assertIn('name="destination"', html)
        self.assertIn('value="source"', html)
        self.assertIn('name="name"', html)
        back = "/listing?" + urlencode({"path": "source", "page": "1",
                                         "sort": "filetype", "filter": "notes"})
        form = {"csrf": self.server.token, "path": "source/notes.md",
                "name": "translated.md", "destination": "archive", "back": back}
        status, result = self.request("/copy", form)
        self.assertEqual(status, 201, result)
        self.assertEqual((self.root / "archive" / "translated.md").read_text(), "# Notes")
        self.assertTrue((self.root / "source" / "notes.md").exists())
        self.assertIn("Back to source directory", result)
        self.assertIn("Open destination directory", result)
        self.assertIn("sort=filetype", result)

    def test_copy_return_keeps_implicit_date_time_sort(self):
        # The styled listing omits sort=timekey from the URL.
        # Confirm the form's Back link does not switch to Filename sort.
        back = "/listing?path=source&page=1"
        form = {"csrf": self.server.token, "path": "source/notes.md",
                "name": "dated.md", "destination": "archive", "back": back}
        status, result = self.request("/copy", form)
        self.assertEqual(status, 201, result)
        self.assertIn("Back to source directory", result)
        self.assertIn("sort=timekey", result)
        self.assertNotIn("sort=filename", result)

    def test_forged_directory_and_existing_file_rejected(self):
        form = {"csrf": self.server.token, "path": "source/notes.md",
                "name": "notes.md", "destination": "archive"}
        (self.root / "archive" / "notes.md").write_text("KEEP")
        for data in ({**form, "csrf": "forged"},
                     {**form, "destination": "../outside"},
                     {**form, "extra": "forged"},
                     form):
            with self.subTest(data=data):
                status, _ = self.request("/copy", data)
                self.assertNotIn(status, (200, 201))
        self.assertEqual((self.root / "archive" / "notes.md").read_text(), "KEEP")

    def test_legacy_post_remains_supported(self):
        form = {"csrf": self.server.token, "path": "source/notes.md",
                "name": "Copy of notes.md"}
        status, _ = self.request("/copy", form)
        self.assertEqual(status, 201)
        self.assertTrue((self.root / "source" / "Copy of notes.md").exists())


if __name__ == "__main__":
    unittest.main()
