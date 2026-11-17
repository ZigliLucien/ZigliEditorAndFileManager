"""v122: save and restore the insertion point of the last open document."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.cursor_positions import CursorPositions
from zefm.editor.recent_files import RecentFiles
from zefm.editor.gui.tk_editor import Window


class CursorPositionsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.store = CursorPositions(self.dir / "positions.json")

    def test_write_and_reopen_unicode_path(self):
        name = self.dir / "cœur-ייִדיש.tex"
        self.store.record(name, "27.9")
        self.assertEqual(CursorPositions(self.store.path).get(name), "27.9")
        self.assertEqual(json.loads(self.store.path.read_text())["positions"]
                         [str(name.resolve())], "27.9")

    def test_reject_bad_values_and_ignore_invalid_storage(self):
        for value in ("1.0; delete all", "0.0", "a.b", "1.-1", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.store.record(self.dir / "a.tex", value)
        self.store.path.write_text(json.dumps({"positions": {
            "bad": "xx", "good": "3.4"}}), encoding="utf-8")
        loaded = CursorPositions(self.store.path)
        self.assertEqual(loaded.positions, {"good": "3.4"})

    def test_bounded_entries(self):
        for i in range(105):
            self.store.record(self.dir / f"f{i}.tex", "2.1")
        self.assertEqual(len(self.store.positions), 100)
        self.assertIsNone(self.store.get(self.dir / "f0.tex"))


class CursorRestoreGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.recent = RecentFiles(self.dir / "recent.json")
        self.cursor_path = self.dir / "cursors.json"
        self.file = self.dir / "chapter.tex"
        self.file.write_text("\n".join(f"line {i}" for i in range(1, 90)),
                             encoding="utf-8")
        self.recent.record(self.file)
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy()
                        if self.root.winfo_exists() else None)

    def make_app(self):
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=self.recent), \
             patch("zefm.editor.gui.tk_editor.CursorPositions",
                   side_effect=lambda: CursorPositions(self.cursor_path)):
            return Window(self.root)

    def test_resume_at_saved_cursor(self):
        CursorPositions(self.cursor_path).record(self.file, "63.4")
        app = self.make_app()
        self.root.update()
        widget, editor = app.current()
        self.assertEqual(widget.index("insert"), "63.4")
        self.assertEqual(Path(editor.state.buffer.path), self.file.resolve())
        self.assertFalse(editor.state.buffer.modified)
        self.assertEqual(len(app.views), 1)

    def test_quit_remembers_cursor_without_modifying_file(self):
        app = self.make_app()
        widget, _editor = app.current()
        widget.mark_set("insert", "44.2")
        original = self.file.read_text(encoding="utf-8")
        app.quit()
        self.assertEqual(CursorPositions(self.cursor_path).get(self.file), "44.2")
        self.assertEqual(self.file.read_text(encoding="utf-8"), original)

    def test_new_buffer_remembers_previous_cursor(self):
        app = self.make_app()
        widget, _ = app.current()
        widget.mark_set("insert", "12.3")
        app.new_buffer()
        self.assertEqual(CursorPositions(self.cursor_path).get(self.file), "12.3")

    def test_position_clamped_when_file_shorter(self):
        self.file.write_text("short", encoding="utf-8")
        CursorPositions(self.cursor_path).record(self.file, "80.30")
        app = self.make_app()
        self.root.update()
        widget, _ = app.current()
        self.assertEqual(widget.index("insert"), "1.5")

    def test_cancelled_quit_does_not_overwrite_saved_position(self):
        CursorPositions(self.cursor_path).record(self.file, "5.1")
        app = self.make_app()
        widget, _editor = app.current()
        widget.insert("end", " unsaved")
        widget.mark_set("insert", "60.2")
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno",
                   return_value=False):
            app.quit()
        self.assertEqual(CursorPositions(self.cursor_path).get(self.file), "5.1")
        self.assertTrue(self.root.winfo_exists())


if __name__ == "__main__":
    unittest.main()
