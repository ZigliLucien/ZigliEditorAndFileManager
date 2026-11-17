"""v119: atomic saves preserve existing files if a write fails."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.files import save_buffer, open_buffer
from zefm.editor.model import Buffer


class AtomicSaveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.target = self.folder / "notes.tex"

    def test_save_is_utf8_and_restores_buffer_state_after_success(self):
        source = Buffer(text="∫ α\nשלום ייִדיש\n", path=None, modified=True)
        save_buffer(source, self.target)
        self.assertEqual(self.target.read_text(encoding="utf-8"), source.text)
        self.assertEqual(open_buffer(self.target).text, source.text)
        self.assertEqual(source.path, str(self.target))
        self.assertFalse(source.modified)

    def test_existing_file_mode_is_preserved(self):
        if os.name != "posix":
            self.skipTest("POSIX permissions only")
        self.target.write_text("before", encoding="utf-8")
        self.target.chmod(0o640)
        buffer = Buffer(text="after", path=str(self.target), modified=True)
        save_buffer(buffer)
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)

    def test_save_through_symlink_preserves_link(self):
        if os.name != "posix":
            self.skipTest("Symlink behavior requires POSIX")
        original = self.folder / "original.tex"
        original.write_text("before", encoding="utf-8")
        self.target.symlink_to(original)
        buffer = Buffer(text="updated", path=str(self.target), modified=True)
        save_buffer(buffer)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(original.read_text(encoding="utf-8"), "updated")
        self.assertEqual(buffer.path, str(self.target))

    def test_replace_failure_preserves_existing_file_and_buffer_dirty(self):
        self.target.write_text("original", encoding="utf-8")
        buffer = Buffer(text="new content", path=str(self.target), modified=True)
        with patch("zefm.editor.files.os.replace",
                   side_effect=OSError("simulated replacement error")):
            with self.assertRaises(OSError):
                save_buffer(buffer)
        self.assertEqual(self.target.read_text(encoding="utf-8"), "original")
        self.assertTrue(buffer.modified)
        self.assertEqual(buffer.path, str(self.target))
        self.assertFalse(list(self.folder.glob(".zefm-save-*")))

    def test_write_failure_preserves_existing_file(self):
        self.target.write_text("original", encoding="utf-8")
        buffer = Buffer(text="new content", path=str(self.target), modified=True)
        with patch("zefm.editor.files.os.fsync",
                   side_effect=OSError("simulated disk error")):
            with self.assertRaises(OSError):
                save_buffer(buffer)
        self.assertEqual(self.target.read_text(encoding="utf-8"), "original")
        self.assertTrue(buffer.modified)
        self.assertFalse(list(self.folder.glob(".zefm-save-*")))


if __name__ == "__main__":
    unittest.main()
