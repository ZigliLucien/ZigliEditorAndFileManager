"""v107: optional ClickPad inserts Undo-able characters without saving."""
import tkinter as tk
import unittest

from zefm.editor.clickpad import PALETTES, palette_for
from zefm.editor.gui.tk_editor import Window


class PaletteTests(unittest.TestCase):
    def test_palette_contents(self):
        self.assertIn("∫", PALETTES["Math"])
        self.assertIn(r"\int", PALETTES["LaTeX"])
        self.assertIn("װ", PALETTES["Yiddish"])
        self.assertEqual(palette_for("latex"), "LaTeX")
        self.assertEqual(palette_for("text", "yiddish"), "Yiddish")


class ClickPadGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.root.update()

    def test_hidden_by_default_and_toggleable(self):
        self.assertFalse(self.app.clickpad_frame.winfo_manager())
        self.app.action("Toggle ClickPad")
        self.root.update()
        self.assertTrue(self.app.clickpad_frame.winfo_manager())
        self.assertTrue(self.app.clickpad_buttons.winfo_children())
        self.app.action("Toggle ClickPad")
        self.assertFalse(self.app.clickpad_frame.winfo_manager())

    def test_insert_at_cursor_and_undo(self):
        widget, editor = self.app.current()
        widget.insert("1.0", "abcd")
        widget.edit_separator()
        widget.mark_set("insert", "1.2")
        self.app._insert_clickpad("∑")
        self.assertEqual(widget.get("1.0", "end-1c"), "ab∑cd")
        widget.edit_undo()
        self.assertEqual(widget.get("1.0", "end-1c"), "abcd")

    def test_tex_mode_selects_latex_palette(self):
        self.app.buffer_modes[self.app.tabs.select()] = type(
            "Mode", (), {"name": "latex"})()
        self.app.action("Toggle ClickPad")
        self.assertEqual(self.app.clickpad_palette.get(), "LaTeX")

    def test_existing_shortcut(self):
        commands = {c.shortcut: c.label
                    for group in self.app.menus.values() for c in group}
        self.assertEqual(commands["Ctrl+F"], "Toggle ClickPad")


if __name__ == "__main__":
    unittest.main()
