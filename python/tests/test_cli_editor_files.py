"""Filename-driven ZEFM invocation (including EDITOR-style blocking)."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import tkinter as tk

from zefm.__main__ import build_parser, main, launch_editor
from zefm.editor.gui.tk_editor import Window


class CliParserTests(TestCase):
    def test_filename_arguments(self):
        opts = build_parser().parse_args(["hello.tex", "second.py"])
        self.assertEqual(opts.mode, "editor")
        self.assertEqual(opts.filenames, ["hello.tex", "second.py"])

    def test_default_still_editor(self):
        self.assertEqual(build_parser().parse_args([]).filenames, [])

    def test_files_only_rejects_filename(self):
        with self.assertRaises(SystemExit):
            main(["--mode", "files", "hello.tex"])

    def test_launch_waits_for_tk_mainloop(self):
        with patch("zefm.editor.gui.tk_editor.Window") as MockWindow:
            launch_editor(filenames=["hello.tex"])
            MockWindow.assert_called_once_with(startup_files=["hello.tex"])
            MockWindow.return_value.root.mainloop.assert_called_once_with()


class CliStartupGuiTests(TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_existing_file_and_missing_file(self):
        existing = self.directory / "hello.tex"
        existing.write_text("hello world", encoding="utf-8")
        fresh = self.directory / "future.py"
        app = Window(self.root, startup_files=[str(existing), str(fresh)])
        self.assertEqual(len(app.views), 2)
        paths = [editor.state.buffer.path for _widget, editor in app.views.values()]
        self.assertIn(str(existing), paths)
        self.assertIn(str(fresh), paths)
        self.assertFalse(fresh.exists(), "Opening a new filename must not create it")
        current, editor = app.current()
        self.assertEqual(editor.state.buffer.path, str(fresh))
        self.assertEqual(current.get("1.0", "end-1c"), "")
        self.assertEqual(app.buffer_modes[app.tabs.select()].name, "python")


if __name__ == "__main__":
    import unittest
    unittest.main()
