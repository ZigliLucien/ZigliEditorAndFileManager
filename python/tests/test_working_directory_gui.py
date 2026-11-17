"""v112: Set Working Directory stays fixed across editor file operations."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.gui.tk_editor import Window
from zefm.editor.working_directory import WorkingDirectory


class WorkingDirectoryGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root_dir = Path(self.temp.name)
        self.app.working_directory = WorkingDirectory(
            str(self.root_dir), True, self.root_dir / "session.json")
        self.fixed = self.root_dir / "fixed"
        self.fixed.mkdir()
        self.elsewhere = self.root_dir / "elsewhere"
        self.elsewhere.mkdir()
        self.source = self.elsewhere / "source.tex"
        self.source.write_text("source\n", encoding="utf-8")
        self.root.update()

    def test_set_directory_persists_through_open_and_save(self):
        with patch("zefm.editor.gui.tk_editor.filedialog.askdirectory",
                   return_value=str(self.fixed)):
            self.app.set_working_directory()
        self.assertTrue(self.app.working_directory.pinned)
        self.app._open_path(str(self.source))
        self.root.update()
        self.assertEqual(self.app.working_directory.initial_directory(),
                         str(self.fixed.resolve()))
        self.assertTrue(self.app.save_file())
        self.assertEqual(self.app.working_directory.initial_directory(),
                         str(self.fixed.resolve()))

    def test_explicit_directory_is_used_for_shell(self):
        self.app.working_directory.set_directory(self.fixed)
        self.app._open_path(str(self.source))
        with patch("zefm.editor.gui.tk_editor.open_terminal") as opened:
            self.app.open_shell_terminal()
        opened.assert_called_once_with(self.fixed.resolve())

    def test_return_to_follow_last_file(self):
        self.app.working_directory.set_directory(self.fixed)
        self.app.reset_working_directory()
        self.assertFalse(self.app.working_directory.pinned)
        self.app._open_path(str(self.source))
        self.assertEqual(self.app.working_directory.initial_directory(),
                         str(self.elsewhere.resolve()))


if __name__ == "__main__":
    unittest.main()
