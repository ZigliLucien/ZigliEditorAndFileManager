"""Java XCommands.runM parity: a single Move can also change the filename.

The existing two-argument Move, Notes migration, conflict checks, and
browser listing return-state remain unchanged.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.http import BrowserServer
from zefm.server.rename_ops import RenameManager
from zefm.storage.word_notes import WordNotes


class MoveRenameModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "root"
        self.source_dir = self.root / "Research"
        self.target_dir = self.root / "Archive"
        self.source_dir.mkdir(parents=True)
        self.target_dir.mkdir()
        self.source = self.source_dir / "cœur ייִדיש.tex"
        self.source.write_text("שלום", encoding="utf-8")
        self.source.chmod(0o640)
        self.notes = Path(self.tmp.name) / "notes.json"
        WordNotes(self.notes).put(str(self.source), "שלום", "Important annotation")
        self.manager = RenameManager(LocalFiles(self.root), self.notes)

    def test_move_and_rename_together_preserves_unicode_notes_and_mode(self):
        result, count = self.manager.move("Research/cœur ייִדיש.tex",
                                          "Archive", "נײַ.tex")
        self.assertEqual(result, self.target_dir / "נײַ.tex")
        self.assertEqual(count, 1)
        self.assertFalse(self.source.exists())
        self.assertEqual(result.read_text(encoding="utf-8"), "שלום")
        self.assertEqual(result.stat().st_mode & 0o777, 0o640)
        store = WordNotes(self.notes)
        self.assertEqual(store.for_file(str(self.source)), [])
        self.assertEqual(store.get(str(result), "שלום")["data"],
                         "Important annotation")

    def test_same_directory_name_change_and_blank_name_compatibility(self):
        result, count = self.manager.move("Research/cœur ייִדיש.tex",
                                          "Research", "new.tex")
        self.assertEqual(result, self.source_dir / "new.tex")
        self.assertEqual(count, 1)
        second, count = self.manager.move("Research/new.tex", "Archive", "")
        self.assertEqual(second, self.target_dir / "new.tex")
        self.assertEqual(count, 1)
        self.assertEqual(WordNotes(self.notes).get(
            str(second), "שלום")["data"], "Important annotation")

    def test_old_two_argument_move_still_keeps_filename(self):
        result, _ = self.manager.move("Research/cœur ייִדיש.tex", "Archive")
        self.assertEqual(result.name, self.source.name)

    def test_collisions_symlinks_and_bad_filename_do_not_change_source(self):
        name = "new.tex"
        target = self.target_dir / name
        target.write_text("KEEP", encoding="utf-8")
        with self.assertRaises(BrowserError) as ctx:
            self.manager.move("Research/cœur ייִדיש.tex", "Archive", name)
        self.assertEqual(ctx.exception.status, 409)
        self.assertEqual(target.read_text(), "KEEP")
        target.unlink()
        target.symlink_to(self.source)
        with self.assertRaises(BrowserError):
            self.manager.move("Research/cœur ייִדיש.tex", "Archive", name)
        for invalid in ("../bad", "/absolute", "a/b", "back\\slash", "\x00"):
            with self.subTest(invalid=invalid), self.assertRaises(BrowserError):
                self.manager.move("Research/cœur ייִדיש.tex", "Archive", invalid)
        self.assertTrue(self.source.exists())
        self.assertEqual(WordNotes(self.notes).get(
            str(self.source), "שלום")["data"], "Important annotation")

    def test_notes_conflict_and_failed_notes_write_leave_source_intact(self):
        destination = self.target_dir / "new.tex"
        WordNotes(self.notes).put(str(destination), "hello", "Previous record")
        with self.assertRaises(BrowserError) as caught:
            self.manager.move("Research/cœur ייִדיש.tex", "Archive", "new.tex")
        self.assertEqual(caught.exception.status, 409)
        self.assertFalse(destination.exists())
        with patch.object(WordNotes, "_write", side_effect=OSError("disk full")):
            with self.assertRaises(BrowserError):
                self.manager.move("Research/cœur ייִדיש.tex", "Archive", "other.tex")
        self.assertFalse((self.target_dir / "other.tex").exists())
        self.assertTrue(self.source.exists())

    def test_open_editor_buffer_still_refuses_moving(self):
        busy = RenameManager(LocalFiles(self.root), self.notes,
                             file_in_use=lambda p: p == self.source)
        with self.assertRaises(BrowserError) as caught:
            busy.move("Research/cœur ייִדיש.tex", "Archive", "new.tex")
        self.assertEqual(caught.exception.status, 409)
        self.assertTrue(self.source.exists())


class MoveRenameBrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "root"
        (self.root / "Research").mkdir(parents=True)
        (self.root / "Archive").mkdir()
        self.source = self.root / "Research" / "paper.txt"
        self.source.write_text("content", encoding="utf-8")
        self.notes = Path(self.tmp.name) / "notes.json"
        WordNotes(self.notes).put(str(self.source), "content", "annotation")
        self.browser = BrowserServer(self.root, notes_path=self.notes)
        self.browser.start()
        self.addCleanup(self.browser.close)

    def request(self, path, data=None):
        payload = urlencode(data).encode("utf-8") if data is not None else None
        req = Request(self.browser.url.rstrip("/") + path, data=payload,
                      headers={"Content-Type": "application/x-www-form-urlencoded"}
                      if payload is not None else {})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def test_form_defaults_to_source_directory_and_offers_optional_name(self):
        code, page = self.request("/move?" + urlencode({"path": "Research/paper.txt"}))
        self.assertEqual(code, 200, page)
        self.assertIn('name="destination" required value="Research"', page)
        self.assertIn('name="new_name"', page)
        self.assertIn("leave blank to keep the name", page)

    def test_post_move_and_rename_keeps_notes_and_listing_return(self):
        back = "/listing?path=Research&page=1&sort=filename"
        data = {"csrf": self.browser.token, "path": "Research/paper.txt",
                "destination": "Archive", "new_name": "new.txt", "back": back}
        code, page = self.request("/move", data)
        self.assertEqual(code, 200, page)
        moved = self.root / "Archive" / "new.txt"
        self.assertFalse(self.source.exists())
        self.assertEqual(moved.read_text(), "content")
        self.assertIn("Archive/new.txt", page)
        self.assertIn("Return to previous listing", page)
        self.assertIn("sort=filename", page)
        self.assertEqual(WordNotes(self.notes).get(
            str(moved), "content")["data"], "annotation")

    def test_blank_name_is_legacy_move_and_rejects_bad_input(self):
        base = {"csrf": self.browser.token, "path": "Research/paper.txt",
                "destination": "Archive"}
        self.assertEqual(self.request("/move", {**base, "csrf": "bad"})[0], 403)
        self.assertEqual(self.request("/move", {**base, "new_name": "../bad"})[0], 400)
        self.assertEqual(self.request("/move", {**base, "unexpected": "oops"})[0], 400)
        self.assertTrue(self.source.exists())
        code, page = self.request("/move", {**base, "new_name": ""})
        self.assertEqual(code, 200, page)
        self.assertTrue((self.root / "Archive" / "paper.txt").exists())


if __name__ == "__main__":
    unittest.main()
