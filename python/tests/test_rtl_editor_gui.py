"""Graphical RTL smoke tests; skip on headless machines without Tk display."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit

from zefm.editor.gui.tk_editor import Window


class RtlEditorTests(unittest.TestCase):
    def setUp(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No Tk display")
        self.app = Window(root)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "ייִדיש.txt"
        self.file.write_text("שלום עולם 123 English", encoding="utf-8")
        self.app._open_path(str(self.file))
        root.update()

    def tearDown(self):
        if hasattr(self, "app"):
            with mock.patch("zefm.editor.gui.tk_editor.messagebox.askyesno", return_value=True):
                self.app.quit()

    def test_yiddish_alignment_is_per_buffer(self):
        widget, _ = self.app.current()
        self.app.choose_language("yi")
        self.assertEqual(widget.tag_cget("zefm-rtl-alignment", "justify"), "right")
        self.assertTrue(widget.tag_ranges("zefm-rtl-alignment"))
        # Keymap and dictionary language independently select right alignment.
        self.app.choose_language("system")
        self.assertFalse(widget.tag_ranges("zefm-rtl-alignment"))
        if "Yiddish" in self.app.available_keymaps:
            self.app.choose_keymap("Yiddish")
            self.assertTrue(widget.tag_ranges("zefm-rtl-alignment"))
            self.app.choose_keymap(None)
            self.assertFalse(widget.tag_ranges("zefm-rtl-alignment"))
        self.assertEqual(widget.get("1.0", "end-1c"), "שלום עולם 123 English")

    def test_browser_uses_native_rtl_form(self):
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as open_browser:
            self.app.edit_current_file_rtl()
        open_browser.assert_called_once()
        destination = open_browser.call_args.args[0]
        parsed = urlsplit(destination)
        self.assertEqual(parsed.hostname, "127.0.0.1")
        self.assertEqual(parsed.path, "/edit")
        self.assertEqual(parse_qs(parsed.query)["dir"], ["rtl"])
        self.assertEqual(parse_qs(parsed.query)["path"], ["ייִדיש.txt"])

    def test_unsaved_editor_text_blocks_browser_launch(self):
        widget, _ = self.app.current()
        widget.insert("end", " unsaved")
        self.app.root.update()
        with mock.patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning:
            with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as open_browser:
                self.app.edit_current_file_rtl()
        warning.assert_called_once()
        open_browser.assert_not_called()
        self.assertIn("unsaved", widget.get("1.0", "end-1c"))


if __name__ == "__main__":
    unittest.main()
