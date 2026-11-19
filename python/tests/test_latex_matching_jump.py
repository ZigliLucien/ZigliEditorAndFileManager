"""v130: jump between matched TeX delimiters without changing source text."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.command_registry import MENUS
from zefm.editor.shortcut_config import load_menus
from zefm.editor.syntax_highlight import (
    MAX_CHARS, latex_matching_delimiter)
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles


class MatchingDelimiterTests(unittest.TestCase):
    def test_brace_round_trip(self):
        source = r"\frac{{a+b}}{c}"
        opening = source.index("{")
        closing = source.rindex("}", 0, source.index("{c}") if "{c}" in source else len(source))
        result = latex_matching_delimiter(source, opening + 1)
        self.assertEqual(result[0], (opening, opening + 1))
        self.assertEqual(result[1], (closing, closing + 1))
        self.assertEqual(latex_matching_delimiter(source, closing + 1),
                         (result[1], result[0]))

    def test_nested_environment_round_trip(self):
        source = (r"\begin{align}" "\n"
                  r"\begin{split} x = y \end{split}" "\n"
                  r"\end{align}")
        opening = (0, len(r"\begin{align}"))
        end_at = source.rindex(r"\end{align}")
        closing = (end_at, len(source))
        self.assertEqual(latex_matching_delimiter(source, 3),
                         (opening, closing))
        self.assertEqual(latex_matching_delimiter(source, len(source)),
                         (closing, opening))

    def test_math_forms_round_trip(self):
        for opening, closing in (
                ("$", "$"), ("$$", "$$"),
                (r"\(", r"\)"), (r"\[", r"\]")):
            with self.subTest(opening=opening):
                source = opening + r"\frac{x}{y}" + closing
                first = (0, len(opening))
                last = (len(source) - len(closing), len(source))
                self.assertEqual(latex_matching_delimiter(source, 0),
                                 (first, last))
                self.assertEqual(latex_matching_delimiter(source, len(source)),
                                 (last, first))

    def test_unmatched_returns_a_source_but_no_destination(self):
        self.assertEqual(latex_matching_delimiter("{oops", 1),
                         ((0, 1), None))
        source = r"\begin{equation} x"
        self.assertEqual(latex_matching_delimiter(source, 5),
                         ((0, len(r"\begin{equation}")), None))
        self.assertIsNone(latex_matching_delimiter("plain prose", 3))

    def test_skips_comments_escaped_braces_and_verbatim(self):
        source = (r"\{ escaped % { \begin{fake} $ " "\n"
                  r"\begin{verbatim}" "\n"
                  r"{ \end{wrong} $ \[ " "\n"
                  r"\end{verbatim}" "\n" r"\[x\]")
        fake_comment = source.index("{", source.index("%"))
        fake_literal = source.index("{", source.index(r"\begin{verbatim}")
                                    + len(r"\begin{verbatim}"))
        self.assertIsNone(latex_matching_delimiter(source, fake_comment+1))
        self.assertIsNone(latex_matching_delimiter(source, fake_literal+1))
        self.assertIsNone(latex_matching_delimiter(source, 2))
        last = source.rindex(r"\[")
        self.assertEqual(latex_matching_delimiter(source, last+1),
                         ((last, last+2), (len(source)-2, len(source))))

    def test_size_and_invalid_cursor(self):
        self.assertIsNone(latex_matching_delimiter("x", -1))
        self.assertIsNone(latex_matching_delimiter("x", 2))
        self.assertIsNone(latex_matching_delimiter("x"*(MAX_CHARS+1), 0))

    def test_registered_shortcut_and_single_command(self):
        menu = load_menus()
        commands = [command for entries in menu.values() for command in entries
                    if command.label == "Go to Matching LaTeX Delimiter"]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].shortcut, "Ctrl+Shift+M")


class MatchingDelimiterGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        history = RecentFiles(self.directory / "recent.json")
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(lambda: self.root.destroy()
                        if self.root.winfo_exists() else None)
        with patch("zefm.editor.gui.tk_editor.RecentFiles",
                   return_value=history):
            self.app = Window(self.root)

    def test_jump_and_jump_back_without_changing_text_or_undo(self):
        for text, name in (
                (r"\frac{a}{b}", "brace.tex"),
                (r"\begin{equation} x \end{equation}", "env.tex"),
                (r"\[x^2+y^2\]", "math.tex")):
            with self.subTest(name=name):
                self.app.new_buffer(path=str(self.directory / name), text=text)
                widget, editor = self.app.current()
                widget.mark_set("insert", "1.0")
                widget.edit_modified(False)
                if name == "brace.tex":
                    widget.mark_set("insert", f"1.0 + {text.index('{')+1} chars")
                starting = widget.index("insert")
                self.assertTrue(self.app.go_to_matching_latex_delimiter())
                jumped = widget.index("insert")
                self.assertNotEqual(jumped, starting)
                self.assertTrue(self.app.go_to_matching_latex_delimiter())
                # A jump lands after the complete partner. Returning to the
                # opener therefore lands after its delimiter, even when the
                # first jump began at the start of a multi-character command.
                offset = text.index("{") + 1 if name == "brace.tex" else (
                    len(r"\\begin{equation}") if name == "env.tex" else 2)
                self.assertEqual(
                    widget.index("insert"),
                    widget.index(f"1.0 + {offset} chars"))
                self.assertEqual(widget.get("1.0", "end-1c"), text)
                self.assertFalse(widget.edit_modified())
                self.assertFalse(editor.state.buffer.modified)

    def test_unmatched_does_not_move_cursor(self):
        self.app.new_buffer(path=str(self.directory / "bad.tex"),
                            text=r"\begin{equation} x")
        widget, _editor = self.app.current()
        widget.mark_set("insert", "1.4")
        self.assertFalse(self.app.go_to_matching_latex_delimiter())
        self.assertEqual(widget.index("insert"), "1.4")
        self.assertIn("unmatched delimiter", self.app.status.get())

    def test_non_latex_does_nothing(self):
        self.app.new_buffer(path=str(self.directory / "test.py"), text="x = 1")
        widget, _editor = self.app.current()
        widget.mark_set("insert", "1.2")
        self.assertFalse(self.app.go_to_matching_latex_delimiter())
        self.assertEqual(widget.index("insert"), "1.2")
        self.assertIn("LaTeX buffers", self.app.status.get())


if __name__ == "__main__":
    unittest.main()
