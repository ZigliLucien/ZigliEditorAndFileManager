"""v133: Python and JSON delimiter and JSON quote highlighting."""
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.code_delimiters import (
    code_bracket_match, json_quote_match, json_spans, MAX_CHARS)
from zefm.editor.syntax_highlight import syntax_spans
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles


class CodeDelimiterTests(unittest.TestCase):
    def test_python_nested_parentheses_square_and_curly_braces(self):
        text = 'items = {"a": [sum((1, 2)), {"b": 3}]}'
        for opener, closer in (("{", "}"), ("[", "]"), ("(", ")")):
            with self.subTest(pair=opener+closer):
                opening = text.index(opener)
                if opener == "(":
                    closing = text.index(")", text.index(")", text.index("2")) + 1)
                elif opener == "[":
                    closing = text.rindex("]")
                else:
                    closing = text.rindex("}")
                self.assertEqual(code_bracket_match(text, opening+1, "python"),
                                 (opening, closing))
                self.assertEqual(code_bracket_match(text, closing+1, "python"),
                                 (closing, opening))

    def test_python_string_comment_and_triple_quote_exclusions(self):
        text = ('x = {"a": "[(not code)]"} # } [ fake\n'
                'doc = """ }\n [ ] """\n'
                'numbers = [1, 2]\n')
        self.assertIsNone(code_bracket_match(
            text, text.index("not code") - 1, "python"))
        self.assertIsNone(code_bracket_match(
            text, text.index("fake") - 2, "python"))
        self.assertIsNone(code_bracket_match(
            text, text.index('""" }') + 5, "python"))
        start = text.index("[1, 2]")
        self.assertEqual(code_bracket_match(text, start + 1, "python"),
                         (start, start + len("[1, 2]") - 1))

    def test_json_brackets_ignore_quoted_braces_and_arrays(self):
        text = '{"fake": "{[ ]}", "items": [{"a": 1}]}'
        opening = 0
        closing = len(text) - 1
        self.assertEqual(code_bracket_match(text, opening + 1, "json"),
                         (opening, closing))
        fake = text.index("{[")
        self.assertIsNone(code_bracket_match(text, fake + 1, "json"))
        bracket = text.index("[{")
        self.assertEqual(code_bracket_match(text, bracket + 1, "json"),
                         (bracket, text.index("]", bracket)))

    def test_json_quotes_and_escaped_quotes(self):
        text = '{"key": "a \\"quoted\\" string", "other": null}'
        start = text.index('"a ')
        close = text.index('", "other"')
        self.assertEqual(json_quote_match(text, start+1), (start, close))
        self.assertEqual(json_quote_match(text, close+1), (close, start))
        escaped_quote = text.index('\\"quoted') + 1
        self.assertIsNone(json_quote_match(text, escaped_quote+1))
        self.assertEqual(
            [(text[a:b], style) for a, b, style in json_spans(text)
             if style == "keyword"], [("null", "keyword")])

    def test_unterminated_json_string_stays_unmatched(self):
        text = '{"key": "unterminated { ['
        opening = text.index('"unterminated')
        self.assertEqual(json_quote_match(text, opening + 1),
                         (opening, None))
        self.assertIsNone(code_bracket_match(
            text, text.index("[") + 1, "json"))
        self.assertTrue(any(style == "string" and b == len(text)
                            for _a, b, style in json_spans(text)))

    def test_crossed_nesting_does_not_appear_matched(self):
        for mode, text in (("json", "{[}]"), ("python", "([)]")):
            with self.subTest(mode=mode):
                for cursor in range(1, len(text) + 1):
                    result = code_bracket_match(text, cursor, mode)
                    self.assertIsNotNone(result)
                    self.assertIsNone(result[1])

    def test_json_strings_numbers_and_boolean_color(self):
        text = '{"n": -12.5e2, "bool": true, "null": null}'
        marked = [(text[a:b], style) for a, b, style
                  in syntax_spans(text, "json")]
        self.assertIn(('"n"', "string"), marked)
        self.assertIn(("-12.5e2", "number"), marked)
        self.assertIn(("true", "keyword"), marked)
        self.assertIn(("null", "keyword"), marked)

    def test_limits(self):
        self.assertIsNone(json_quote_match('x', -1))
        self.assertIsNone(json_quote_match('x', 2))
        large = "{" * (MAX_CHARS + 1)
        self.assertIsNone(code_bracket_match(large, 1, "json"))
        self.assertIsNone(json_quote_match(large, 1))


class CodeDelimiterGuiTests(unittest.TestCase):
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

    def test_python_and_json_bracket_tags_do_not_modify_buffer(self):
        for name, source in (
                ("a.py", "data = {'a': [1, 2]}"),
                ("b.json", '{"data": [1, 2]}')):
            with self.subTest(filename=name):
                self.app.new_buffer(path=str(self.directory / name),
                                    text=source)
                widget, editor = self.app.current()
                opening = source.index("[")
                widget.mark_set("insert", f"1.0 + {opening + 1} chars")
                widget.edit_modified(False)
                self.app._refresh_highlight(self.app.tabs.select())
                self.assertEqual(len(widget.tag_ranges("syntax_match")), 4)
                self.assertEqual(widget.get("1.0", "end-1c"), source)
                self.assertFalse(widget.edit_modified())
                self.assertFalse(editor.state.buffer.modified)

    def test_validate_json_jumps_to_unquoted_key_and_value(self):
        for source, marker in (
                ('{name: "value"}', "name"),
                ('{"name": missing}', "missing")):
            with self.subTest(source=source):
                self.app.new_buffer(
                    path=str(self.directory / "validation.json"), text=source)
                widget, editor = self.app.current()
                widget.mark_set("insert", "1.0")
                widget.edit_modified(False)
                self.app.validate_buffer()
                expected = source.index(marker)
                self.assertEqual(
                    widget.index("insert"),
                    widget.index(f"1.0 + {expected} chars"))
                self.assertEqual(widget.get("1.0", "end-1c"), source)
                self.assertIn("double quotes", self.app.status.get())
                self.assertFalse(widget.edit_modified())
                self.assertFalse(editor.state.buffer.modified)

    def test_json_pair_quotes_and_unfinished_quote(self):
        self.app.new_buffer(path=str(self.directory / "bad.json"),
                            text='{"a": "text"}')
        widget, editor = self.app.current()
        quote = widget.get("1.0", "end-1c").index('"text"')
        widget.mark_set("insert", f"1.0 + {quote + 1} chars")
        self.app._refresh_highlight(self.app.tabs.select())
        self.assertEqual(len(widget.tag_ranges("syntax_match")), 4)
        widget.delete("1.0", "end")
        widget.insert("1.0", '{"a": "unfinished')
        widget.mark_set("insert", "1.0 + 7 chars")
        widget.edit_modified(False)
        self.app._refresh_highlight(self.app.tabs.select())
        self.assertEqual(len(widget.tag_ranges("syntax_unmatched")), 2)
        self.assertEqual(widget.get("1.0", "end-1c"), '{"a": "unfinished')


if __name__ == "__main__":
    unittest.main()
