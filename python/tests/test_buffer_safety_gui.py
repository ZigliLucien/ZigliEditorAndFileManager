"""v115: external reload and close/quit guards use the real live buffer."""
import tkinter as tk
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from zefm.editor.gui.tk_editor import Window


class BufferSafetyGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy() if self.root.winfo_exists() else None)
        self.app = Window(self.root)
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "current.tex"
        self.file.write_text("saved", encoding="utf-8")
        self.app._open_path(str(self.file))
        self.root.update()

    def test_external_reload_uses_current_revert_method(self):
        with patch.object(self.app, "revert_buffer", return_value=True) as reverted:
            self.app._reload_external()
        reverted.assert_called_once()

    def test_reopen_changed_disk_file_uses_revert_buffer(self):
        self.file.write_text("external", encoding="utf-8")
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno",
                   return_value=True) as confirm, \
             patch.object(self.app, "revert_buffer", return_value=True) as revert:
            self.app._open_path(str(self.file))
        confirm.assert_called_once()
        revert.assert_called_once()

    def test_close_buffer_prompts_on_live_unsaved_text_even_if_model_clean(self):
        widget, editor = self.app.current()
        tab = self.app.tabs.select()
        widget.insert("end", " uncommitted")
        editor.state.buffer.modified = False
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno",
                   return_value=False) as confirm:
            self.app.close_buffer()
        confirm.assert_called_once()
        self.assertIn(tab, self.app.views)
        self.assertIn("uncommitted", widget.get("1.0", "end-1c"))

    def test_close_buffer_no_prompt_after_undo_to_saved_snapshot(self):
        widget, editor = self.app.current()
        tab = self.app.tabs.select()
        widget.insert("end", " change")
        widget.edit_undo()
        editor.state.buffer.modified = True
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno") as confirm:
            self.app.close_buffer()
        confirm.assert_not_called()
        self.assertNotIn(tab, self.app.views)

    def test_quit_detects_unsaved_text_even_when_model_matches(self):
        widget, editor = self.app.current()
        widget.insert("end", " unsaved")
        editor.state.buffer.text = widget.get("1.0", "end-1c")
        editor.state.buffer.modified = False
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno",
                   return_value=False) as confirm:
            self.app.quit()
        confirm.assert_called_once()
        self.assertTrue(self.root.winfo_exists())

    def test_quit_no_prompt_for_clean_buffer(self):
        with patch("zefm.editor.gui.tk_editor.messagebox.askyesno") as confirm:
            self.app.quit()
        confirm.assert_not_called()
        self.assertFalse(self.root.winfo_exists())


if __name__ == "__main__":
    unittest.main()
