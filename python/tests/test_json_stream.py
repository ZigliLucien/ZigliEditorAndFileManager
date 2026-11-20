"""v139: jq-style multi-value JSON streams and record-local path navigation."""
import json
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.json_stream import json_values
from zefm.editor.json_path import (
    paths_at, navigate, locate_path, record_at)
from zefm.editor.json_tools import format_json, value_at_path
from zefm.editor.mode_tools import validate_json, validate_json_details
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles


STREAM = ('{"section": {"name": "first", "values": [1, 2]}}\n'
          '{"section": {"name": "second", "values": [3, 4]}}\n'
          '{"section": {"name": "third", "values": [5, 6]}}\n')


class JsonStreamTests(unittest.TestCase):
    def test_json_decoder_accepts_successive_top_level_objects(self):
        values = json_values(STREAM)
        self.assertEqual(len(values), 3)
        self.assertEqual(
            [obj["section"]["name"] for _a, _b, obj in values],
            ["first", "second", "third"])
        self.assertEqual(
            [STREAM[a:b] for a, b, _obj in values],
            [STREAM[a:b].rstrip() for a, b, _obj in values])
        self.assertEqual(
            validate_json(STREAM), (True, "Valid JSON stream (3 top-level values)"))
        self.assertEqual(validate_json('{"one": 1}'), (True, "Valid JSON"))

    def test_adjacent_objects_without_any_separator(self):
        text = '{"a":1}{"a":2}{"a":3}'
        self.assertEqual(len(json_values(text)), 3)
        self.assertEqual(paths_at(text, text.rindex("3")), ".a")
        self.assertEqual(record_at(text, text.rindex("3")), (2, 3))
        self.assertEqual(validate_json_details(text)[0], True)

    def test_paths_are_scoped_to_cursor_record(self):
        for i, word in enumerate(("first", "second", "third")):
            with self.subTest(record=i):
                offset = STREAM.index(word)
                self.assertEqual(paths_at(STREAM, offset), ".section.name")
                self.assertEqual(record_at(STREAM, offset), (i, 3))
                self.assertEqual(
                    locate_path(STREAM, ("section", "name"), cursor=offset),
                    STREAM.rfind('"name"', 0, offset))
                self.assertEqual(
                    value_at_path(STREAM, ["section", "name"],
                                  record_index=i),
                    word)
        self.assertEqual(
            locate_path(STREAM, ["section", "name"]),
            STREAM.index('"name"'))

    def test_navigation_does_not_leak_into_other_records(self):
        offset = STREAM.index("second")
        pos, path = navigate(STREAM, offset, "parent")
        self.assertEqual(path, ".section")
        self.assertEqual(record_at(STREAM, pos), (1, 3))
        pos, path = navigate(STREAM, offset, "next")
        self.assertEqual(path, ".section.values")
        self.assertEqual(record_at(STREAM, pos), (1, 3))
        self.assertIsNone(navigate(STREAM, STREAM.index("second"), "previous"))
        pos, path = navigate(STREAM, STREAM.index("second"), "next_record")
        self.assertEqual(path, ".")
        self.assertEqual(pos, STREAM.index('{"section"', STREAM.index("third") - 40))
        self.assertEqual(record_at(STREAM, pos), (2, 3))
        pos, path = navigate(STREAM, pos, "previous_record")
        self.assertEqual(path, ".")
        self.assertEqual(record_at(STREAM, pos), (1, 3))
        self.assertIsNone(navigate(STREAM, 0, "previous_record"))
        self.assertIsNone(navigate(STREAM, STREAM.index("third"),
                                   "next_record"))

    def test_stream_format_preserves_separate_records(self):
        formatted = format_json(STREAM)
        self.assertIn("}\n\n{", formatted)
        self.assertTrue(formatted.endswith("\n"))
        self.assertEqual(len(json_values(formatted)), 3)
        self.assertEqual(
            [val for _start, _end, val in json_values(formatted)],
            [val for _start, _end, val in json_values(STREAM)])

    def test_bad_later_record_has_real_source_offset(self):
        invalid = '{"good": 1}\n{"bad": unquoted}\n'
        valid, message, position = validate_json_details(invalid)
        self.assertFalse(valid)
        self.assertEqual(position, invalid.index("unquoted"))
        self.assertIn("double quotes", message)
        self.assertIsNone(paths_at(invalid, invalid.index("good")))
        self.assertIsNone(locate_path(invalid, ["good"]))
        with self.assertRaises(json.JSONDecodeError):
            json_values(invalid)
        self.assertFalse(validate_json_details('')[0])


class JsonStreamGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        history = RecentFiles(self.directory / "recent.json")
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(
            lambda: self.root.destroy() if self.root.winfo_exists() else None)
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=history):
            self.app = Window(self.root)
        self.app.new_buffer(
            path=str(self.directory / "stream.json"), text=STREAM)
        self.widget, self.editor = self.app.current()

    def cursor_in(self, token):
        self.widget.mark_set(
            "insert", f"1.0 + {STREAM.index(token) + 1} chars")

    def test_validation_and_path_show_record_number(self):
        self.cursor_in("second")
        self.widget.edit_modified(False)
        self.app.validate_buffer()
        self.assertEqual(self.app.status.get(),
                         "Valid JSON stream (3 top-level values)")
        with patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as popup:
            self.app.show_json_path()
        popup.assert_called_once()
        self.assertIn("Record 2 of 3", popup.call_args.args[1])
        self.assertIn(".section.name", popup.call_args.args[1])
        self.app.copy_json_path()
        self.assertEqual(self.root.clipboard_get(), ".section.name")
        self.assertEqual(self.widget.get("1.0", "end-1c"), STREAM)
        self.assertFalse(self.widget.edit_modified())
        self.assertFalse(self.editor.state.buffer.modified)

    def test_jump_value_and_next_record_are_relative_to_cursor(self):
        self.cursor_in("second")
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring",
                   return_value=".section.values[0]"):
            self.app.jump_json_path()
        expected = STREAM.index("3")
        self.assertEqual(self.widget.index("insert"),
                         self.widget.index(f"1.0 + {expected} chars"))
        self.app.navigate_json("next_record")
        self.assertEqual(
            record_at(STREAM, len(self.widget.get("1.0", "insert"))), (2, 3))
        self.app.navigate_json("previous_record")
        self.assertEqual(
            record_at(STREAM, len(self.widget.get("1.0", "insert"))), (1, 3))

        self.cursor_in("second")
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring",
                   return_value=".section.name"):
            self.app.json_value_at_path()
        widget, _editor = self.app.current()
        self.assertEqual(widget.get("1.0", "end-1c"), '"second"\n')
        self.assertEqual(
            self.app.buffer_modes[self.app.tabs.select()].name, "json")
        self.assertEqual(self.widget.get("1.0", "end-1c"), STREAM)


if __name__ == "__main__":
    unittest.main()
