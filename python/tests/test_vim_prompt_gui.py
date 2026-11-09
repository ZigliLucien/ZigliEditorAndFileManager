"""Regression for Vim-style / search prompt visibility in the Tk editor.

The expanding notebook must not swallow the transient command bar.
"""
import tkinter as tk
import unittest
from types import SimpleNamespace

from zefm.editor.gui.tk_editor import Window


class VimPromptVisibilityTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.root.geometry("640x420")
        widget, editor = self.app.current()
        widget.insert("1.0", "first alpha second alpha third")
        widget.mark_set("insert", "1.0")
        self.root.update()

    @staticmethod
    def key(keysym, char, state=0):
        return SimpleNamespace(keysym=keysym, char=char, state=state)

    def test_esc_slash_opens_visible_search_and_n_continues(self):
        widget, editor = self.app.current()
        self.assertEqual(self.app._vim_key(self.key("Escape", "\x1b")), "break")
        self.assertTrue(self.app.vim_normal)
        self.assertEqual(self.app._vim_key(self.key("slash", "/")), "break")
        self.root.update()

        self.assertEqual(self.app.command_label.cget("text"), "/")
        self.assertEqual(self.app.command_bar.winfo_manager(), "pack")
        self.assertTrue(self.app.command_bar.winfo_ismapped())
        self.assertTrue(self.app.command_entry.winfo_ismapped())
        self.assertLess(self.app.command_bar.winfo_rooty(),
                        self.app.status_bar.winfo_rooty())
        self.assertLessEqual(
            self.app.command_bar.winfo_rootx() + self.app.command_bar.winfo_width(),
            self.root.winfo_rootx() + self.root.winfo_width())
        self.assertEqual(self.app.vim_normal, True)

        self.app.command_value.set("alpha")
        self.assertEqual(self.app._vim_submit(), "break")
        self.assertFalse(self.app.command_bar.winfo_manager())
        self.assertEqual(widget.get("sel.first", "sel.last"), "alpha")
        initial = widget.index("sel.first")
        self.assertEqual(self.app._vim_key(self.key("n", "n")), "break")
        self.assertEqual(widget.get("sel.first", "sel.last"), "alpha")
        self.assertNotEqual(widget.index("sel.first"), initial)
        self.assertEqual(widget.get("1.0", "end-1c"), "first alpha second alpha third")

    def test_backward_search_and_colon_command_remain_visible(self):
        widget, _editor = self.app.current()
        self.app._vim_key(self.key("Escape", "\x1b"))
        self.app._vim_key(self.key("question", "?", state=1))
        self.root.update()
        self.assertTrue(self.app.command_entry.winfo_ismapped())
        self.assertEqual(self.app.command_label.cget("text"), "?")
        self.app._vim_cancel()
        self.app._vim_key(self.key("colon", ":", state=1))
        self.root.update()
        self.assertTrue(self.app.command_entry.winfo_ismapped())
        self.assertEqual(self.app.command_label.cget("text"), ":")
        self.app._vim_cancel()
        self.assertEqual(self.app._vim_key(self.key("i", "i")), "break")
        self.assertFalse(self.app.vim_normal)

    def test_slash_from_insert_mode_does_not_pop_up(self):
        widget, _editor = self.app.current()
        self.assertFalse(self.app.vim_normal)
        self.assertIsNone(self.app._vim_key(self.key("slash", "/")))
        self.assertFalse(self.app.command_bar.winfo_manager())


if __name__ == "__main__":
    unittest.main()
