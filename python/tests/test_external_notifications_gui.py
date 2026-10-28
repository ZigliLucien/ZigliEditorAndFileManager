"""Optional graphical tests for v43 external-file notifications.

When no Tk display exists these tests skip; use Xvfb or a real desktop for
full coverage.
"""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock

from zefm.editor.gui.tk_editor import Window


class ExternalNotificationGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "français_ייִדיש.txt"
        self.path.write_text("initial", encoding="utf-8")
        self.app._open_path(str(self.path))
        self.root.update()

    def test_notice_dismiss_and_reload(self):
        widget, editor = self.app.current()
        self.assertFalse(self.app.external_notice.winfo_manager())
        self.path.write_text("browser update", encoding="utf-8")
        self.app._check_external_changes()
        self.root.update()
        self.assertEqual(self.app.external_notice.winfo_manager(), "pack")
        self.assertIn("changed on disk", self.app.external_notice_text.get())
        self.app._dismiss_external()
        self.assertFalse(self.app.external_notice.winfo_manager())
        self.app._check_external_changes()
        self.assertFalse(self.app.external_notice.winfo_manager())
        self.path.write_text("second browser update", encoding="utf-8")
        self.app._check_external_changes()
        self.assertEqual(self.app.external_notice.winfo_manager(), "pack")
        self.app._reload_external()
        self.root.update()
        self.assertEqual(widget.get("1.0", "end-1c"), "second browser update")
        self.assertFalse(editor.state.buffer.modified)
        self.assertFalse(self.app.external_notice.winfo_manager())

    def test_unsaved_text_survives_cancelled_reload(self):
        widget, _editor = self.app.current()
        widget.insert("end", " unsaved")
        self.root.update()
        self.path.write_text("newer disk text", encoding="utf-8")
        self.app._check_external_changes()
        with mock.patch("zefm.editor.gui.tk_editor.messagebox.askyesno", return_value=False):
            self.app._reload_external()
        self.assertIn("unsaved", widget.get("1.0", "end-1c"))
        self.assertEqual(self.path.read_text(encoding="utf-8"), "newer disk text")
        self.assertEqual(self.app.external_notice.winfo_manager(), "pack")

    def test_missing_file_disables_reload(self):
        self.path.unlink()
        self.app._check_external_changes()
        self.assertEqual(self.app.external_notice.winfo_manager(), "pack")
        self.assertTrue(self.app.external_reload.instate(["disabled"]))

    def test_conflicting_save_can_be_cancelled(self):
        widget, _editor = self.app.current()
        widget.insert("end", " unsaved")
        self.root.update()
        self.path.write_text("newer disk text", encoding="utf-8")
        with mock.patch("zefm.editor.gui.tk_editor.messagebox.askyesno", return_value=False):
            self.app.save_file()
        self.assertEqual(self.path.read_text(encoding="utf-8"), "newer disk text")
        self.assertIn("unsaved", widget.get("1.0", "end-1c"))


if __name__ == "__main__":
    unittest.main()
