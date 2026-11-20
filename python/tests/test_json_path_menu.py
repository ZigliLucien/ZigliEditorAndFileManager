"""v135: regression checks for JSON/jq path menu commands and navigation."""
import unittest
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from zefm.editor.json_path import (
    paths_at, navigate, locate_path, source_spans, jq_path)
from zefm.editor.json_tools import parse_simple_path, value_at_path
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles

DATA = ('{\n'
        '  "people": [\n'
        '    {"name": "Alice"},\n'
        '    {"name": "Bob", "address": {"city": "Paris"}}\n'
        '  ],\n'
        '  "flags": [true, false, null]\n'
        '}')


class JsonPathPureTests(unittest.TestCase):
    def test_deep_paths_unicode_and_special_keys(self):
        source = '{"שלום": [{"first name": {"x.y": 3}}]}'
        offset = source.index('3')
        expected = '.[\"שלום\"][0][\"first name\"][\"x.y\"]'
        self.assertEqual(paths_at(source, offset), expected)
        self.assertEqual(parse_simple_path(expected),
                         ['שלום', 0, 'first name', 'x.y'])
        self.assertEqual(value_at_path(source, parse_simple_path(expected)), 3)
        self.assertIsNotNone(locate_path(
            source, ['שלום', 0, 'first name', 'x.y']))

    def test_path_navigation_from_keys_and_values(self):
        self.assertEqual(paths_at(DATA, DATA.index("Alice")), ".people[0].name")
        self.assertEqual(paths_at(DATA, DATA.index("Paris")), 
                         ".people[1].address.city")
        offset = DATA.index("Bob")
        pos, path = navigate(DATA, offset, "parent")
        self.assertEqual(path, ".people[1]")
        self.assertEqual(paths_at(DATA, pos), path)
        pos, path = navigate(DATA, offset, "next")
        self.assertEqual(path, ".people[1].address")
        self.assertEqual(paths_at(DATA, pos), path)
        pos, path = navigate(DATA, DATA.index('"people"') + 2, "child")
        self.assertEqual(path, ".people[0]")
        self.assertEqual(paths_at(DATA, pos), path)

    def test_child_scans_large_array_just_once(self):
        source = '{"rows": [' + ",".join(
            '{"id": ' + str(i) + '}' for i in range(400)) + ']}'
        with patch("zefm.editor.json_path.source_spans",
                   wraps=source_spans) as scan:
            pos, path = navigate(source, source.index("[") + 1, "child")
        self.assertEqual(path, ".rows[0]")
        self.assertEqual(paths_at(source, pos), path)
        self.assertEqual(scan.call_count, 1)

    def test_invalid_buffer_never_claims_a_valid_path(self):
        self.assertIsNone(paths_at('{"name": unquoted}', 3))
        self.assertIsNone(navigate('{"name": unquoted}', 1, "child"))


class JsonPathGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        recent = RecentFiles(self.directory / "recent.json")
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(
            lambda: self.root.destroy() if self.root.winfo_exists() else None)
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=recent):
            self.app = Window(self.root)
        self.app.new_buffer(path=str(self.directory / "data.json"), text=DATA)
        self.widget, self.editor = self.app.current()

    def caret_at(self, target):
        self.widget.mark_set(
            "insert", f"1.0 + {DATA.index(target) + 1} chars")

    def test_show_and_copy_jq_path_at_cursor(self):
        self.caret_at("Paris")
        before = self.widget.get("1.0", "end-1c")
        self.widget.edit_modified(False)
        with patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as info:
            self.app.show_json_path()
        info.assert_called_once()
        self.assertIn(".people[1].address.city", info.call_args.args[1])
        self.app.copy_json_path()
        self.assertEqual(self.root.clipboard_get(), ".people[1].address.city")
        self.assertEqual(self.widget.get("1.0", "end-1c"), before)
        self.assertFalse(self.widget.edit_modified())

    def test_child_parent_sibling_and_jump_commands(self):
        self.caret_at("Bob")
        self.app.navigate_json("parent")
        self.assertIn("JSON parent: .people[1]", self.app.status.get())
        self.app.navigate_json("child")
        self.assertIn("JSON child: .people[1].name", self.app.status.get())
        self.app.navigate_json("next")
        self.assertIn("JSON next: .people[1].address", self.app.status.get())
        self.app.navigate_json("previous")
        self.assertIn("JSON previous: .people[1].name", self.app.status.get())
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring",
                   return_value=".people[1].address.city"):
            self.app.jump_json_path()
        self.assertEqual(self.app._json_path(), ".people[1].address.city")

    def test_get_json_value_at_path_creates_valid_new_buffer(self):
        self.caret_at("Paris")
        before = self.widget.get("1.0", "end-1c")
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring",
                   return_value=".people[1].address.city"):
            self.app.json_value_at_path()
        value_widget, _value_editor = self.app.current()
        result = value_widget.get("1.0", "end-1c")
        self.assertEqual(result, '"Paris"\n')
        self.assertNotIn("\\n", result)
        self.assertEqual(self.widget.get("1.0", "end-1c"), before)

    def test_invalid_json_reports_error_instead_of_silent_failure(self):
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", '{"key": unquoted}')
        self.widget.mark_set("insert", "1.3")
        self.assertIsNone(self.app._json_path())
        self.assertIn("JSON:", self.app.status.get())
        self.assertIn("double quotes", self.app.status.get())
        self.app.navigate_json("child")
        self.assertIn("JSON:", self.app.status.get())
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring") as dialog:
            self.app.json_value_at_path()
        dialog.assert_not_called()
        self.assertIn("JSON:", self.app.status.get())

    def test_non_json_buffer_explains_why_paths_unavailable(self):
        self.app.new_buffer(path=str(self.directory / "code.py"),
                            text="x = {'a': 1}")
        self.assertIsNone(self.app._json_path())
        self.assertIn("requires a JSON buffer", self.app.status.get())


if __name__ == "__main__":
    unittest.main()
