"""v134: Ctrl+Shift+M navigation for LaTeX, Python and JSON pairs."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.code_delimiters import code_matching_delimiter
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles
from zefm.editor.shortcut_config import load_menus


class CodeMatchingPairsTests(unittest.TestCase):
    def test_python_parentheses_and_braces(self):
        text = 'v = {"x": [max(1, 2)]}'
        for symbol, closing in (("{", "}"), ("[", "]"), ("(", ")")):
            with self.subTest(symbol=symbol):
                pos = text.index(symbol)
                end = text.rindex(closing)
                self.assertEqual(
                    code_matching_delimiter(text, pos + 1, "python"),
                    ((pos, pos + 1), (end, end + 1)))
                self.assertEqual(
                    code_matching_delimiter(text, end + 1, "python"),
                    ((end, end + 1), (pos, pos + 1)))

    def test_json_objects_arrays_and_string_quotes(self):
        text = r'{"a": [{"quote": "a \"quoted\" string"}]}'
        for op, cl in (("{", "}"), ("[", "]")):
            pos, end = text.index(op), text.rindex(cl)
            self.assertEqual(
                code_matching_delimiter(text, pos + 1, "json"),
                ((pos, pos + 1), (end, end + 1)))
        quote = text.index('"a \\"quoted')
        closing = text.index('"}]}', quote)
        self.assertEqual(
            code_matching_delimiter(text, quote + 1, "json"),
            ((quote, quote + 1), (closing, closing + 1)))
        self.assertEqual(
            code_matching_delimiter(text, closing + 1, "json"),
            ((closing, closing + 1), (quote, quote + 1)))
        escaped = text.index(r'\"quoted') + 1
        self.assertIsNone(code_matching_delimiter(text, escaped + 1, "json"))

    def test_unmatched_and_non_structural_text(self):
        self.assertEqual(
            code_matching_delimiter("{", 1, "json"), ((0, 1), None))
        self.assertEqual(
            code_matching_delimiter('{"name": "unterminated', 10, "json"),
            ((9, 10), None))
        self.assertIsNone(code_matching_delimiter("{[ ]}", 1, "text"))
        self.assertIsNone(code_matching_delimiter('{"x": "{not a brace}"}',
                                                    8, "json"))

    def test_existing_shortcut_and_command_label(self):
        commands = [cmd for group in load_menus().values() for cmd in group
                    if cmd.label == "Go to Matching LaTeX Delimiter"]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].shortcut, "Ctrl+Shift+M")


class CodeMatchingJumpGuiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        history = RecentFiles(self.folder / "recent.json")
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(
            lambda: self.root.destroy() if self.root.winfo_exists() else None)
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=history):
            self.app = Window(self.root)

    def test_jumps_round_trip_without_touching_buffer_or_undo(self):
        cases = [
            ("a.py", "def f(a):\n    return {'x': [a, 1]}\n", "[", "]"),
            ("a.json", '{"x": {"y": [1, 2]}}', "[", "]"),
            ("strings.json", '{"name": "value"}', '"value"', '"value"'),
        ]
        for filename, source, opening, closing in cases:
            with self.subTest(filename=filename):
                self.app.new_buffer(path=str(self.folder / filename),
                                    text=source)
                widget, editor = self.app.current()
                pos = source.index(opening)
                if opening == '"value"':
                    pos = source.index('"value"')
                    end = pos + len('"value"') - 1
                else:
                    end = source.index(closing, pos + 1)
                widget.mark_set("insert", f"1.0 + {pos + 1} chars")
                widget.edit_modified(False)
                self.assertTrue(self.app.go_to_matching_delimiter())
                self.assertEqual(widget.index("insert"),
                                 widget.index(f"1.0 + {end + 1} chars"))
                self.assertTrue(self.app.go_to_matching_delimiter())
                self.assertEqual(widget.index("insert"),
                                 widget.index(f"1.0 + {pos + 1} chars"))
                self.assertEqual(widget.get("1.0", "end-1c"), source)
                self.assertFalse(widget.edit_modified())
                self.assertFalse(editor.state.buffer.modified)

    def test_registered_action_reaches_code_handler(self):
        source = '{"x": [1, 2]}'
        self.app.new_buffer(path=str(self.folder / "test.json"),
                            text=source)
        widget, _editor = self.app.current()
        pos = source.index("[")
        widget.mark_set("insert", f"1.0 + {pos + 1} chars")
        # The historical registry key remains the same so existing keyboard
        # configuration continues to work with the expanded command.
        self.app.action("Go to Matching LaTeX Delimiter")
        self.assertEqual(widget.get("insert -1c", "insert"), "]")
        self.assertIn("JSON matching delimiter", self.app.status.get())

    def test_unmatched_or_unsupported_never_moves_caret(self):
        for filename, source, pos in (
                ("broken.json", '{"items": [', 11),
                ("broken.py", "items = [", 9),
                ("note.md", "[ordinary]", 1)):
            with self.subTest(filename=filename):
                self.app.new_buffer(path=str(self.folder / filename),
                                    text=source)
                widget, _editor = self.app.current()
                widget.mark_set("insert", f"1.0 + {pos} chars")
                before = widget.index("insert")
                self.assertFalse(self.app.go_to_matching_delimiter())
                self.assertEqual(widget.index("insert"), before)


if __name__ == "__main__":
    unittest.main()
