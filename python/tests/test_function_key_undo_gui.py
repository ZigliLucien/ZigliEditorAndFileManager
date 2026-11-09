"""Verify legacy F5 Undo / F6 Redo in INSERT and NORMAL modes."""
import tkinter as tk
import unittest

from zefm.editor.gui.tk_editor import Window


class LegacyFunctionKeyGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.widget, self.editor = self.app.current()
        self.root.update()
        self.widget.focus_force()
        self.root.update()

    def trigger(self, key):
        self.widget.focus_force()
        self.root.update()
        self.widget.event_generate("<KeyPress-" + key + ">")
        self.root.update()

    def test_f5_undo_f6_redo_in_insert_mode(self):
        self.widget.insert("1.0", "hello")
        self.root.update()
        self.assertFalse(self.app.vim_normal)
        self.trigger("F5")
        self.assertEqual(self.widget.get("1.0", "end-1c"), "")
        self.trigger("F6")
        self.assertEqual(self.widget.get("1.0", "end-1c"), "hello")

    def test_f5_undo_f6_redo_in_normal_mode(self):
        self.widget.insert("1.0", "first")
        self.root.update()
        self.trigger("Escape")
        self.assertTrue(self.app.vim_normal)
        self.trigger("F5")
        self.assertEqual(self.widget.get("1.0", "end-1c"), "")
        self.assertTrue(self.app.vim_normal)
        self.trigger("F6")
        self.assertEqual(self.widget.get("1.0", "end-1c"), "first")
        self.assertTrue(self.app.vim_normal)

    def test_function_key_binds_share_edit_menu_registry(self):
        keys = {command.shortcut: command.label
                for commands in self.app.menus.values() for command in commands}
        self.assertEqual(keys["F5"], "Undo")
        self.assertEqual(keys["F6"], "Redo")
        self.assertTrue(self.root.bind_all("<F5>"))
        self.assertTrue(self.root.bind_all("<F6>"))


if __name__ == "__main__":
    unittest.main()
