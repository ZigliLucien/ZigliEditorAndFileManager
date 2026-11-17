"""v121: startup restores the most recent readable file with no blank tab."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.recent_files import RecentFiles
from zefm.editor.startup_file import last_recent_buffer
from zefm.editor.gui.tk_editor import Window


class StartupRecentSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.history = RecentFiles(self.dir / "recent.json")

    def test_latest_readable_file_is_selected(self):
        a = self.dir / "older.tex"
        b = self.dir / "newer.tex"
        a.write_text("alpha", encoding="utf-8")
        b.write_text("β ייִדיש", encoding="utf-8")
        self.history.record(a)
        self.history.record(b)
        selected = last_recent_buffer(self.history)
        self.assertEqual(Path(selected.path), b.resolve())
        self.assertEqual(selected.text, "β ייִדיש")

    def test_missing_and_invalid_utf8_files_are_skipped(self):
        good = self.dir / "good.tex"
        bad = self.dir / "bad.txt"
        good.write_text("good", encoding="utf-8")
        bad.write_bytes(b"\xff")
        self.history.record(good)
        self.history.record(bad)
        self.history.record(self.dir / "gone.tex")
        selected = last_recent_buffer(self.history)
        self.assertEqual(Path(selected.path), good.resolve())
        # Preserve the history: a temporarily unavailable mount may return.
        self.assertEqual(len(self.history.entries), 3)

    def test_none_when_no_recent_file_is_usable(self):
        self.history.record(self.dir / "missing")
        self.assertIsNone(last_recent_buffer(self.history))


class StartupRecentGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.history = RecentFiles(self.dir / "recent.json")
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy() if self.root.winfo_exists() else None)

    def make_app(self):
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=self.history):
            return Window(self.root)

    def test_startup_restores_file_without_empty_tab(self):
        source = self.dir / "document.tex"
        source.write_text("restored ᾶ", encoding="utf-8")
        self.history.record(source)
        app = self.make_app()
        self.assertEqual(len(app.views), 1)
        widget, editor = app.current()
        self.assertEqual(widget.get("1.0", "end-1c"), "restored ᾶ")
        self.assertEqual(Path(editor.state.buffer.path), source.resolve())
        self.assertFalse(editor.state.buffer.modified)

    def test_startup_falls_back_to_blank(self):
        self.history.record(self.dir / "missing.tex")
        app = self.make_app()
        self.assertEqual(len(app.views), 1)
        widget, editor = app.current()
        self.assertEqual(widget.get("1.0", "end-1c"), "")
        self.assertIsNone(editor.state.buffer.path)

    def test_user_can_still_create_untitled_buffer(self):
        source = self.dir / "document.tex"
        source.write_text("a", encoding="utf-8")
        self.history.record(source)
        app = self.make_app()
        app.new_buffer()
        self.assertEqual(len(app.views), 2)
        self.assertIsNone(app.current()[1].state.buffer.path)


if __name__ == "__main__":
    unittest.main()
