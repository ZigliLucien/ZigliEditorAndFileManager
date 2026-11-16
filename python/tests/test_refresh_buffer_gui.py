"""v105: F7 refresh is nondestructive, and F5 Undo survives Save."""
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import patch

from zefm.editor.gui.tk_editor import Window


class RefreshBufferGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "working.tex"
        self.source.write_text("original", encoding="utf-8")
        self.app._open_path(str(self.source))
        self.root.update()

    def test_f7_keeps_text_selection_and_undo(self):
        widget, _editor = self.app.current()
        widget.insert("end", " editing")
        self.root.update()
        widget.mark_set("insert", "1.4")
        before = widget.get("1.0", "end-1c")
        point = widget.index("insert")
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno") as ask:
            self.app.action("Refresh Buffer")
        ask.assert_not_called()
        self.assertEqual(widget.get("1.0", "end-1c"), before)
        self.assertEqual(widget.index("insert"), point)
        self.assertEqual(self.source.read_text(encoding="utf-8"), "original")
        widget.edit_undo()
        self.assertEqual(widget.get("1.0", "end-1c"), "original")

    def test_refresh_does_not_reload_external_disk_version(self):
        widget, _ = self.app.current()
        widget.insert("end", " unsaved")
        self.root.update()
        self.source.write_text("external revision", encoding="utf-8")
        before = widget.get("1.0", "end-1c")
        self.app.action("Refresh Buffer")
        self.assertEqual(widget.get("1.0", "end-1c"), before)
        self.assertEqual(self.source.read_text(encoding="utf-8"),
                         "external revision")

    def test_undo_still_works_after_save_and_refresh(self):
        widget, _ = self.app.current()
        widget.insert("end", " saved change")
        self.root.update()
        self.assertTrue(self.app.save_file())
        self.assertEqual(self.source.read_text(encoding="utf-8"),
                         "original saved change")
        self.app.action("Refresh Buffer")
        widget.edit_undo()
        self.root.update()
        self.assertEqual(widget.get("1.0", "end-1c"), "original")
        self.assertEqual(self.source.read_text(encoding="utf-8"),
                         "original saved change")

    def test_original_f7_shortcut_is_preserved(self):
        keys = {cmd.shortcut: cmd.label
                for group in self.app.menus.values() for cmd in group}
        self.assertEqual(keys["F7"], "Refresh Buffer")


if __name__ == "__main__":
    unittest.main()
