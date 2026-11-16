"""v104: Revert Buffer discards only unsaved changes, on confirmation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import patch

from zefm.editor.gui.tk_editor import Window


class RevertBufferGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "cœur.tex"
        self.original = "original\nsecond\n"
        self.file.write_text(self.original, encoding="utf-8")
        self.app._open_path(str(self.file))
        self.root.update()

    def test_confirm_revert_restores_disk_and_resets_undo(self):
        widget, editor = self.app.current()
        widget.insert("end", "unsaved text")
        self.root.update()
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno",
                   return_value=True) as confirm:
            self.app.action("Revert Buffer")
        confirm.assert_called_once()
        self.assertEqual(widget.get("1.0", "end-1c"), self.original)
        self.assertEqual(self.file.read_text(encoding="utf-8"), self.original)
        self.assertFalse(editor.state.buffer.modified)
        self.assertEqual(self.app.saved_snapshots[self.app.tabs.select()],
                         self.original)
        with self.assertRaises(tk.TclError):
            widget.edit_undo()

    def test_cancel_leaves_unsaved_text_intact(self):
        widget, _ = self.app.current()
        widget.insert("end", "work in progress")
        self.root.update()
        before = widget.get("1.0", "end-1c")
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno",
                   return_value=False) as confirm:
            self.assertFalse(self.app.revert_buffer())
        confirm.assert_called_once()
        self.assertEqual(widget.get("1.0", "end-1c"), before)
        self.assertEqual(self.file.read_text(encoding="utf-8"), self.original)

    def test_dirty_flag_without_text_changes_does_not_prompt(self):
        widget, _ = self.app.current()
        widget.edit_modified(True)
        self.root.update()
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno") as confirm:
            self.assertTrue(self.app.revert_buffer())
        confirm.assert_not_called()

    def test_external_disk_changes_are_loaded_without_overwriting(self):
        widget, _ = self.app.current()
        self.file.write_text("external version", encoding="utf-8")
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno") as confirm:
            self.assertTrue(self.app.revert_buffer())
        confirm.assert_not_called()
        self.assertEqual(widget.get("1.0", "end-1c"), "external version")

    def test_missing_disk_file_does_not_erase_buffer(self):
        widget, _ = self.app.current()
        self.file.unlink()
        before = widget.get("1.0", "end-1c")
        with patch("zefm.editor.gui.tk_editor.messagebox.showerror") as error:
            self.assertFalse(self.app.revert_buffer())
        error.assert_called_once()
        self.assertEqual(widget.get("1.0", "end-1c"), before)

    def test_untitled_buffer_cannot_revert(self):
        self.app.new_buffer(text="unsaved")
        with patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as info:
            self.assertFalse(self.app.revert_buffer())
        info.assert_called_once()
        self.assertEqual(self.app.current()[0].get("1.0", "end-1c"), "unsaved")


if __name__ == "__main__":
    unittest.main()
