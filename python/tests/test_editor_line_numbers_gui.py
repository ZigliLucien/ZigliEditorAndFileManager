"""v102: visible line-number gutter with the original Edit command."""
import tkinter as tk
import unittest

from zefm.editor.gui.tk_editor import Window


class LineNumberTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.root.update()

    def test_toggle_keeps_buffer_text_and_undo_intact(self):
        widget, _editor = self.app.current()
        widget.insert("1.0", "first\nsecond\nthird\n")
        self.root.update()
        original = widget.get("1.0", "end-1c")
        tab = self.app.tabs.select()
        canvas, enabled = self.app.line_gutters[tab]
        self.assertFalse(enabled)
        self.app.action("Line Numbers")
        self.root.update()
        self.assertTrue(self.app.line_gutters[tab][1])
        self.assertTrue(canvas.winfo_manager())
        self.assertTrue(canvas.find_all())
        self.assertEqual(widget.get("1.0", "end-1c"), original)
        self.app.action("Line Numbers")
        self.root.update()
        self.assertFalse(self.app.line_gutters[tab][1])
        self.assertFalse(canvas.winfo_manager())
        self.assertEqual(widget.get("1.0", "end-1c"), original)

    def test_gutters_are_per_tab(self):
        self.app.action("Line Numbers")
        first = self.app.tabs.select()
        self.app.new_buffer(text="new\nother")
        second = self.app.tabs.select()
        self.assertTrue(self.app.line_gutters[first][1])
        self.assertFalse(self.app.line_gutters[second][1])
        self.app.action("Line Numbers")
        self.assertTrue(self.app.line_gutters[second][1])
        self.app.tabs.select(first)
        self.assertTrue(self.app.line_gutters[first][1])

    def test_original_keyboard_action_still_exists(self):
        keys = {item.shortcut: item.label
                for items in self.app.menus.values() for item in items}
        self.assertEqual(keys["Ctrl+F2"], "Line Numbers")


if __name__ == "__main__":
    unittest.main()
