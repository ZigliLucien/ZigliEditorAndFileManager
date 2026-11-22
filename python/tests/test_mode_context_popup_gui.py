"""Mode-sensitive right-click tools in the Tk editor."""
import tkinter as tk
import unittest
from unittest import mock
from types import SimpleNamespace

from zefm.editor.gui.tk_editor import Window


class ModeContextPopupTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.widget, _ = self.app.current()

    def show(self, mode):
        self.app.buffer_modes[self.app.tabs.select()] = self.app.mode_registry.modes[mode]
        self.widget.mark_set("insert", "1.0")
        with mock.patch.object(self.app.recent_popup, "tk_popup"):
            self.app._show_recent_files_popup(
                SimpleNamespace(x_root=100, y_root=200))
        self.assertEqual(self.widget.index("insert"), "1.0")
        popup = self.app.recent_popup
        entries = [(i, popup.type(i), popup.entrycget(i, "label"))
                   for i in range(popup.index("end") + 1)
                   if popup.type(i) in ("command", "cascade")]
        return popup, entries

    def test_mode_specific_tools(self):
        for mode, expected in (("python", "Python Tools"),
                               ("latex", "LaTeX Tools"),
                               ("json", "JSON / jq Tools")):
            with self.subTest(mode=mode):
                _popup, entries = self.show(mode)
                self.assertIn(expected, [label for _, _, label in entries])
                self.assertIn("Go to Line... (Ctrl+G)",
                              [label for _, _, label in entries])

    def test_json_submenu_has_record_and_jq_commands(self):
        popup, entries = self.show("json")
        index = next(i for i, kind, label in entries
                     if label == "JSON / jq Tools")
        child = popup.nametowidget(popup.entrycget(index, "menu"))
        labels = [child.entrycget(i, "label")
                  for i in range(child.index("end") + 1)
                  if child.type(i) == "command"]
        self.assertIn("Go to Record...", labels)
        self.assertIn("Next Record (]r)", labels)
        self.assertIn("Run jq on Buffer...", labels)

    def test_noncode_mode_keeps_recent_files(self):
        popup, entries = self.show("text")
        labels = [label for _, _, label in entries]
        self.assertNotIn("JSON / jq Tools", labels)
        self.assertIn("Open File...", labels)
        self.assertIn("Go to Line... (Ctrl+G)", labels)


if __name__ == "__main__":
    unittest.main()
