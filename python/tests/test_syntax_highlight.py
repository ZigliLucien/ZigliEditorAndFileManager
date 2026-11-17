"""v123: LaTeX brace matching and lightweight syntax highlighting."""
import tkinter as tk
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
import unittest

from zefm.editor.syntax_highlight import (
    syntax_spans, latex_match, MAX_CHARS)
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles


class SyntaxHighlightTests(unittest.TestCase):
    def test_python_keywords_strings_comments(self):
        text = 'def hello(x):\n    return "if" # comment\n'
        spans = syntax_spans(text, "python")
        marked = [(text[a:b], style) for a, b, style in spans]
        self.assertIn(("def", "keyword"), marked)
        self.assertIn(("return", "keyword"), marked)
        self.assertIn(('"if"', "string"), marked)
        self.assertIn(("# comment", "comment"), marked)
        self.assertNotIn(("if", "keyword"), marked)

    def test_java_comments_strings_and_keywords(self):
        text = 'public class Hello { String s = "class"; /* if */ return; }'
        spans = syntax_spans(text, "java")
        marked = [(text[a:b], style) for a, b, style in spans]
        self.assertIn(("public", "keyword"), marked)
        self.assertIn(("class", "keyword"), marked)
        self.assertIn(('\"class\"', "string"), marked)
        self.assertIn(("/* if */", "comment"), marked)
        self.assertIn(("return", "keyword"), marked)

    def test_latex_comments_commands_and_escaped_percent(self):
        text = r'\frac{a}{b} \% literal % \section{ignored}'
        marked = [(text[a:b], style) for a, b, style
                  in syntax_spans(text, "latex")]
        self.assertIn((r"\frac", "command"), marked)
        self.assertIn((r"\%", "command"), marked)
        self.assertIn(("% " + r"\section{ignored}", "comment"), marked)

    def test_latex_matched_braces_and_nested_delimiters(self):
        text = r'\frac{(a+[b])}{c}'
        opening = text.index("{")
        ending = text.index("}", opening)
        self.assertEqual(latex_match(text, opening + 1), (opening, ending))
        inner = text.index("(")
        self.assertEqual(latex_match(text, inner + 1),
                         (inner, text.index(")")))

    def test_unmatched_braces_and_ignored_comments(self):
        self.assertEqual(latex_match("{unclosed", 1), (0, None))
        text = r'\{ ignored % { comment'
        self.assertIsNone(latex_match(text, text.index("{") + 1))
        self.assertIsNone(latex_match(text, text.rindex("{") + 1))
        self.assertIsNone(latex_match("plain", 3))

    def test_size_cap(self):
        text = "x" * (MAX_CHARS + 1)
        self.assertEqual(syntax_spans(text, "latex"), [])
        self.assertIsNone(latex_match(text, 1))

    def test_unrecognized_mode(self):
        self.assertEqual(syntax_spans("hello", "text"), [])


class SyntaxHighlightGuiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root_path = Path(self.tmp.name)
        self.recent = RecentFiles(self.root_path / "recent.json")
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy()
                        if self.root.winfo_exists() else None)
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=self.recent):
            self.app = Window(self.root)

    def test_latex_tags_not_text_and_no_extra_undo(self):
        self.app.new_buffer(path=str(self.root_path / "math.tex"),
                            text=r'\frac{a}{b}')
        tab = self.app.tabs.select()
        widget, _ = self.app.current()
        initial = widget.get("1.0", "end-1c")
        widget.mark_set("insert", "1.6")
        widget.edit_modified(False)
        self.app._refresh_highlight(tab)
        self.assertEqual(widget.get("1.0", "end-1c"), initial)
        self.assertFalse(widget.edit_modified())
        self.assertTrue(widget.tag_ranges("syntax_command"))
        self.assertTrue(widget.tag_ranges("syntax_match"))

    def test_python_and_java_modes(self):
        for name, text, tag in (
                ("code.py", "def hello(): pass", "syntax_keyword"),
                ("Code.java", "public class Code {}", "syntax_keyword")):
            self.app.new_buffer(path=str(self.root_path / name), text=text)
            widget, _ = self.app.current()
            self.app._refresh_highlight(self.app.tabs.select())
            self.assertTrue(widget.tag_ranges(tag), name)


if __name__ == "__main__":
    unittest.main()
