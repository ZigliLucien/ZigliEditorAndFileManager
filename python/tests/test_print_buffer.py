"""v106: printing shows the live buffer without saving or altering Undo."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.print_preview import render_print_html
from zefm.editor.gui.tk_editor import Window


class PrintPreviewTests(unittest.TestCase):
    def test_unicode_and_html_are_escaped(self):
        html = render_print_html("<tag>&\nשלום ייִדיש café œ", "draft <&>")
        self.assertIn("&lt;tag&gt;&amp;", html)
        self.assertIn("שלום ייִדיש café œ", html)
        self.assertIn("draft &lt;&amp;&gt;", html)
        self.assertIn('charset="utf-8"', html)
        self.assertIn("@media print", html)
        self.assertNotIn("<tag>", html)

    def test_large_buffers_are_refused(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            render_print_html("x" * 4_000_001, "large")


class PrintBufferGuiTests(unittest.TestCase):
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
        self.source.write_text("saved", encoding="utf-8")
        self.app._open_path(str(self.source))
        self.root.update()

    def test_print_uses_unsaved_contents_without_saving(self):
        widget, _ = self.app.current()
        widget.insert("end", " + unsaved <math> & שלום")
        self.root.update()
        before = widget.get("1.0", "end-1c")
        with patch.object(self.app, "_show_print_preview_dialog") as shown:
            self.app.action("Print")
        shown.assert_called_once()
        target = shown.call_args.args[0]
        html = target.read_text(encoding="utf-8")
        self.assertIn("unsaved &lt;math&gt; &amp; שלום", html)
        self.assertEqual(self.source.read_text(encoding="utf-8"), "saved")
        self.assertEqual(widget.get("1.0", "end-1c"), before)
        widget.edit_undo()
        self.assertEqual(widget.get("1.0", "end-1c"), "saved")

    def test_print_preview_is_cleaned_on_quit(self):
        with patch.object(self.app, "_show_print_preview_dialog"):
            self.app.action("Print")
        directory = Path(self.app.print_preview_directory.name)
        self.assertTrue(directory.is_dir())
        self.app.quit()
        self.assertFalse(directory.exists())

    def test_print_shows_visible_dialog_without_silent_browser_launch(self):
        with patch("zefm.editor.gui.tk_editor.webbrowser.open_new_tab") as browser:
            self.app.action("Print")
        browser.assert_not_called()
        dialogs = [x for x in self.root.winfo_children()
                   if isinstance(x, tk.Toplevel)]
        self.assertTrue(dialogs, "Print should explain how to open the preview")
        previews = list(Path(self.app.print_preview_directory.name)
                        .glob("print-*.html"))
        self.assertEqual(len(previews), 1)
        dialogs[-1].destroy()

    def test_ctrl_p_is_registered(self):
        commands = {cmd.shortcut: cmd.label
                    for group in self.app.menus.values() for cmd in group}
        self.assertEqual(commands["Ctrl+P"], "Print")


if __name__ == "__main__":
    unittest.main()
