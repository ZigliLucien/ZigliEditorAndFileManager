"""v116: interface type size/contrast is separate from editor document font."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import tkinter as tk
import unittest

from zefm.editor.interface_settings import (
    read_interface, write_interface, DEFAULT_INTERFACE)
from zefm.editor.gui.tk_editor import Window


class InterfaceSettingsTests(unittest.TestCase):
    def test_defaults_and_persistence(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "interface.json"
            self.assertEqual(read_interface(p), DEFAULT_INTERFACE)
            write_interface(p, {"size": 17})
            self.assertEqual(read_interface(p), {"size": 17})
            self.assertEqual(json.loads(p.read_text())["size"], 17)

    def test_bad_values_fall_back_or_rejected(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "interface.json"
            for value in ({"size": 9}, {"size": True}, {"size": 25}):
                p.write_text(json.dumps(value), encoding="utf-8")
                self.assertEqual(read_interface(p), DEFAULT_INTERFACE)
                with self.assertRaises(ValueError):
                    write_interface(p, value)


class InterfaceFontsGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy() if self.root.winfo_exists() else None)
        self.app = Window(self.root)
        self.root.update()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app.interface_settings_path = Path(self.temp.name) / "interface.json"

    def test_status_bar_has_visible_divider_and_contrast(self):
        from tkinter import ttk
        style = ttk.Style(self.root)
        self.assertEqual(style.lookup("Zefm.Status.TLabel", "foreground"), "#15263a")
        self.assertEqual(style.lookup("Zefm.Status.TFrame", "background"), "#dce6f2")
        self.assertEqual(self.app.status_divider.winfo_manager(), "pack")

    def test_interface_text_is_bold(self):
        from tkinter import font as tkfont
        self.assertEqual(self.app.interface_font.actual("weight"), "bold")
        self.assertEqual(self.app.interface_emphasis_font.actual("weight"), "bold")
        self.assertEqual(
            tkfont.nametofont("TkMenuFont", root=self.root).actual("weight"),
            "bold")

    def test_font_control_resizes_interface_only(self):
        old_editor_size = self.app.editor_font.actual("size")
        with patch("zefm.editor.gui.tk_editor.simpledialog.askinteger",
                   return_value=17):
            self.app.choose_interface_font_size()
        self.assertEqual(self.app.interface_size, 17)
        self.assertEqual(self.app.interface_font.actual("size"), 17)
        self.assertEqual(self.app.editor_font.actual("size"), old_editor_size)
        self.assertEqual(read_interface(self.app.interface_settings_path)["size"], 17)

    def test_cancel_leaves_font_unchanged(self):
        before = self.app.interface_size
        with patch("zefm.editor.gui.tk_editor.simpledialog.askinteger",
                   return_value=None):
            self.app.choose_interface_font_size()
        self.assertEqual(self.app.interface_size, before)


if __name__ == "__main__":
    unittest.main()
