"""Recoverable Trash: Notes-aware file moves and guarded browser restore."""
from pathlib import Path
from tempfile import TemporaryDirectory
import stat
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.rename_ops import RenameManager
from zefm.server.trash_ops import TrashManager
from zefm.server.http import BrowserServer
from zefm.storage.word_notes import WordNotes


class TrashModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "files"
        (self.root / "docs").mkdir(parents=True)
        self.original = self.root / "docs" / "cœur ייִדיש.yid"
        self.original.write_text("שלום\n", encoding="utf-8")
        self.original.chmod(0o640)
        self.notes = Path(self.tmp.name) / "notes.json"
        WordNotes(self.notes).put(str(self.original), "שלום", "Original annotation")
        self.files = LocalFiles(self.root)
        self.trash = TrashManager(self.files, RenameManager(self.files, self.notes))

    def test_trash_restore_roundtrip_preserves_file_and_notes(self):
        item, count = self.trash.trash("docs/cœur ייִדיש.yid")
        self.assertEqual(count, 1)
        self.assertFalse(self.original.exists())
        self.assertEqual(WordNotes(self.notes).for_file(str(self.original)), [])
        entries = self.trash.list_items()
        self.assertEqual(entries[0]["id"], item)
        self.assertEqual(entries[0]["original"], "docs/cœur ייִדיש.yid")
        restored, note_count = self.trash.restore(item)
        self.assertEqual(restored, self.original)
        self.assertEqual(note_count, 1)
        self.assertEqual(restored.read_text(encoding="utf-8"), "שלום\n")
        self.assertEqual(stat.S_IMODE(restored.stat().st_mode), 0o640)
        self.assertEqual(WordNotes(self.notes).get(str(restored), "שלום")["data"],
                         "Original annotation")
        self.assertEqual(self.trash.list_items(), [])

    def test_restore_never_clobbers_new_file(self):
        item, _ = self.trash.trash("docs/cœur ייִדיש.yid")
        self.original.write_text("New data", encoding="utf-8")
        with self.assertRaises(BrowserError) as caught:
            self.trash.restore(item)
        self.assertEqual(caught.exception.status, 409)
        self.assertEqual(self.original.read_text(), "New data")
        self.assertEqual(len(self.trash.list_items()), 1)

    def test_refuse_symlinks_invalid_ids_and_trash_internal(self):
        (self.root / "docs" / "shortcut").symlink_to(self.original)
        with self.assertRaises(BrowserError):
            self.trash.trash("docs/shortcut")
        for key in ("../../passwd", "abc", "", "f" * 32):
            with self.subTest(key=key), self.assertRaises(BrowserError):
                self.trash.restore(key)
        with self.assertRaises(BrowserError):
            self.trash.trash("../outside.txt")

    def test_open_desktop_file_not_trashed(self):
        busy = TrashManager(self.files, RenameManager(
            self.files, self.notes, file_in_use=lambda path: path == self.original))
        with self.assertRaises(BrowserError) as caught:
            busy.trash("docs/cœur ייִדיש.yid")
        self.assertEqual(caught.exception.status, 409)
        self.assertTrue(self.original.exists())
        self.assertEqual(busy.list_items(), [])

    def test_failed_notes_update_rolls_back_file_and_temp_record(self):
        with patch.object(WordNotes, "_write", side_effect=OSError("full disk")):
            with self.assertRaises(BrowserError):
                self.trash.trash("docs/cœur ייִדיש.yid")
        self.assertTrue(self.original.exists())
        self.assertEqual(self.trash.list_items(), [])
        self.assertEqual(list((self.root / ".zefm-trash").iterdir()), [])

    def test_dangerous_trash_symlink_is_not_followed(self):
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        (self.root / ".zefm-trash").symlink_to(other, target_is_directory=True)
        with self.assertRaises(BrowserError) as caught:
            self.trash.trash("docs/cœur ייִדיש.yid")
        self.assertEqual(caught.exception.status, 403)
        self.assertTrue(self.original.exists())


class TrashBrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "root"
        (self.root / "docs").mkdir(parents=True)
        self.original = self.root / "docs" / "intro.md"
        self.original.write_text("Text", encoding="utf-8")
        self.notes_path = Path(self.tmp.name) / "notes.json"
        WordNotes(self.notes_path).put(str(self.original), "Text", "Keep this note")
        self.browser = BrowserServer(self.root, notes_path=self.notes_path)
        self.browser.start()
        self.addCleanup(self.browser.close)

    def request(self, route, values=None):
        payload = urlencode(values).encode("utf-8") if values is not None else None
        req = Request(self.browser.url.rstrip("/") + route, data=payload,
                      headers={"Content-Type": "application/x-www-form-urlencoded"}
                      if payload is not None else {})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def test_confirmation_trash_list_and_restore(self):
        back = "/listing?path=docs&page=1"
        status, confirm = self.request("/delete?" + urlencode(
            {"path": "docs/intro.md", "back": back}))
        self.assertEqual(status, 200)
        self.assertIn('action="/delete"', confirm)
        self.assertTrue(self.original.exists())
        wrong = {"csrf": self.browser.token, "path": "docs/intro.md", "confirm": "no"}
        self.assertEqual(self.request("/delete", wrong)[0], 400)
        self.assertTrue(self.original.exists())
        values = {**wrong, "confirm": "trash", "back": back}
        status, result = self.request("/delete", values)
        self.assertEqual(status, 200, result)
        self.assertFalse(self.original.exists())
        self.assertIn("sort=timekey", result)
        self.assertIn("Open Trash and Restore", result)
        status, page = self.request("/trash")
        self.assertEqual(status, 200)
        self.assertIn("docs/intro.md", page)
        self.assertIn('action="/restore"', page)
        item = next((self.root / ".zefm-trash").iterdir())
        status, result = self.request("/restore", {
            "csrf": self.browser.token, "id": item.name})
        self.assertEqual(status, 200, result)
        self.assertEqual(self.original.read_text(), "Text")
        self.assertEqual(WordNotes(self.notes_path).get(
            str(self.original), "Text")["data"], "Keep this note")
        self.assertIn("Open restored directory", result)

    def test_malformed_requests_and_links(self):
        bad = {"csrf": self.browser.token, "path": "docs/intro.md",
               "confirm": "trash"}
        self.assertEqual(self.request("/delete", {**bad, "csrf": "incorrect"})[0], 403)
        self.assertEqual(self.request("/delete", {**bad, "extra": "bad"})[0], 400)
        self.assertEqual(self.request("/restore", {"csrf": self.browser.token,
                                                  "id": "../bad"})[0], 400)
        self.assertEqual(self.request("/trash?unexpected=1")[0], 400)
        self.assertTrue(self.original.exists())
        status, html = self.request("/listing")
        self.assertEqual(status, 200)
        self.assertIn('value="delete"', html)
        self.assertNotIn('value="delete" disabled', html)
        self.assertIn('id="trash-link"', html)
        status, basic = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn("Trash...", basic)


if __name__ == "__main__":
    unittest.main()
