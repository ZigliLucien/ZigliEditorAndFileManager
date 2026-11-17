"""v120: Tk/browser Quick Edit coordination must preserve unsaved work."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
import tkinter as tk
import unittest

from zefm.editor.gui.tk_editor import Window
from zefm.server.file_manager import LocalFiles


class BrowserQuickEditSafetyTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy() if self.root.winfo_exists() else None)
        self.app = Window(self.root)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "live.tex"
        self.file.write_text("saved", encoding="utf-8")
        self.app._open_path(str(self.file))
        self.root.update()

    def test_unsaved_live_text_cannot_open_browser_even_if_model_agrees(self):
        widget, editor = self.app.current()
        widget.insert("end", " unsaved")
        # Reproduce Tk <<Modified>> having synchronized the model to
        # the unsaved buffer, causing the older guard to miss the edit.
        editor.state.buffer.text = widget.get("1.0", "end-1c")
        editor.state.buffer.modified = False
        with patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning, \
             patch("zefm.editor.gui.tk_editor.webbrowser.open") as launch:
            self.app.edit_current_file_in_browser()
        warning.assert_called_once()
        launch.assert_not_called()
        self.assertTrue(editor.state.buffer.modified)
        self.assertEqual(self.file.read_text(encoding="utf-8"), "saved")

    def test_stale_disk_content_blocks_browser_quick_edit(self):
        self.file.write_text("changed externally", encoding="utf-8")
        with patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning, \
             patch("zefm.editor.gui.tk_editor.webbrowser.open") as launch:
            self.app.edit_current_file_in_browser()
        warning.assert_called_once()
        launch.assert_not_called()
        self.assertEqual(self.app.current()[0].get("1.0", "end-1c"), "saved")

    def test_clean_matching_buffer_opens_browser_editor(self):
        browser = Mock()
        browser.files = LocalFiles(Path(self.temp.name))
        browser.start.return_value = "http://127.0.0.1:1234/"
        with patch("zefm.server.http.BrowserServer", return_value=browser), \
             patch("zefm.editor.gui.tk_editor.webbrowser.open") as launch, \
             patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning:
            self.app.edit_current_file_in_browser()
        launch.assert_called_once()
        self.assertIn("edit?", launch.call_args.args[0])
        warning.assert_not_called()


if __name__ == "__main__":
    unittest.main()
