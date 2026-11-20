"""Regression tests for line jumps, JSONL record jumps and NORMAL commands."""
import tkinter as tk
import unittest
from types import SimpleNamespace

from zefm.editor.gui.tk_editor import Window


class LineRecordNavigationTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.widget, _ = self.app.current()
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", '{"a": 1}\n{"b": [1, 2]}\n{"c": 3}')
        self.widget.mark_set("insert", "1.0")
        self.app.buffer_modes[self.app.tabs.select()] = self.app.mode_registry.modes["json"]

    @staticmethod
    def key(char):
        return SimpleNamespace(keysym=char, char=char, state=0)

    def test_go_to_line_preserves_column(self):
        self.widget.mark_set("insert", "1.4")
        self.app.go_to_line(2)
        self.assertEqual(self.widget.index("insert"), "2.4")

    def test_go_to_record(self):
        self.app.go_to_record(3)
        self.assertEqual(self.widget.index("insert"), "3.0")

    def test_normal_shortcuts(self):
        self.app.vim_normal = True
        for char in "2G":
            self.app._vim_key(self.key(char))
        self.assertEqual(self.widget.index("insert"), "2.0")
        self.app._vim_key(self.key("]"))
        self.app._vim_key(self.key("r"))
        self.assertEqual(self.widget.index("insert"), "3.0")
        self.app._vim_key(self.key("["))
        self.app._vim_key(self.key("r"))
        self.assertEqual(self.widget.index("insert"), "2.0")
        self.app._vim_key(self.key("g"))
        self.app._vim_key(self.key("g"))
        self.assertEqual(self.widget.index("insert"), "1.0")

    def test_colon_record(self):
        self.app.vim_normal = True
        self.app.command_label.configure(text=":")
        self.app.command_value.set("r 2")
        self.app._vim_submit()
        self.assertEqual(self.widget.index("insert"), "2.0")

    def test_jsonl_mode_detection(self):
        detected = self.app.mode_registry.detect("sample.jsonl", "")
        self.assertEqual(detected.name, "json")


if __name__ == "__main__":
    unittest.main()
