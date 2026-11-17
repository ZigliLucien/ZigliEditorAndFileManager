"""v123: LaTeX brace matching and lightweight syntax highlighting."""
import tkinter as tk
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
import unittest

from zefm.editor.syntax_highlight import (
    syntax_spans, latex_match, latex_environment_match, MAX_CHARS)
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

    def test_environment_pair_nested_and_starred(self):
        text = (r"\begin{align*}" "\n"
                r"  \begin{split} x=y \end{split}" "\n"
                r"\end{align*}")
        outer = (0, len(r"\begin{align*}"))
        closing_start = text.index(r"\end{align*}")
        outer_end = (closing_start, len(text))
        self.assertEqual(latex_environment_match(text, 3),
                         (outer, outer_end))
        self.assertEqual(latex_environment_match(text, len(text)),
                         (outer_end, outer))
        inner_start = text.index(r"\begin{split}")
        inner_end = text.index(r"\end{split}")
        self.assertEqual(
            latex_environment_match(text, inner_start + 6),
            ((inner_start, inner_start + len(r"\begin{split}")),
             (inner_end, inner_end + len(r"\end{split}"))))

    def test_environment_mismatch_is_unmatched(self):
        text = r"\begin{equation} x \end{align}"
        self.assertEqual(latex_environment_match(text, 5),
                         ((0, len(r"\begin{equation}")), None))
        last = text.index(r"\end{align}")
        self.assertEqual(latex_environment_match(text, last + 5),
                         ((last, len(text)), None))

    def test_environment_comments_and_escaped_commands_ignored(self):
        text = (r"% \begin{fake}" "\n"
                r"\begin{real} \end{real} % \end{fake}")
        self.assertIsNone(latex_environment_match(text, 5))
        start = text.index(r"\begin{real}")
        end = text.index(r"\end{real}")
        self.assertEqual(
            latex_environment_match(text, start + 3),
            ((start, start + len(r"\begin{real}")),
             (end, end + len(r"\end{real}"))))
        self.assertIsNone(latex_environment_match(
            r"\\begin{escaped}", len(r"\\begin{escaped}")))

    def test_verbatim_region_ignores_fake_braces_comments_and_commands(self):
        text = (r"\begin{verbatim}" "\n"
                r"{ [( % \begin{fake} \end{fake}" "\n"
                r"\end{verbatim}" "\n"
                r"\frac{a}{b}")
        fake = text.index("{ [(")
        self.assertIsNone(latex_match(text, fake + 1))
        self.assertIsNone(latex_environment_match(
            text, text.index(r"\begin{fake}") + 4))
        self.assertIsNone(latex_environment_match(
            text, text.index(r"\end{fake}") + 4))
        start = text.index(r"\begin{verbatim}")
        close = text.index(r"\end{verbatim}")
        self.assertEqual(
            latex_environment_match(text, start + 4),
            ((start, start + len(r"\begin{verbatim}")),
             (close, close + len(r"\end{verbatim}"))))
        marked = [(text[x:y], style) for x, y, style
                  in syntax_spans(text, "latex")]
        self.assertTrue(any(style == "verbatim" and r"\begin{fake}" in word
                            for word, style in marked))
        self.assertIn((r"\frac", "command"), marked)
        self.assertNotIn(("% " + r"\begin{fake} \end{fake}", "comment"), marked)

    def test_minted_and_lstlisting_do_not_confuse_outer_environment(self):
        for name in ("minted", "lstlisting", "Verbatim", "verbatim*"):
            with self.subTest(name=name):
                opening = r"\begin{" + name + "}"
                closing = r"\end{" + name + "}"
                text = (r"\begin{equation}" "\n"
                        + opening + "\n"
                        + r"\end{equation} { % \begin{misleading}" + "\n"
                        + closing + "\n"
                        + r"\end{equation}")
                outer_close = text.rindex(r"\end{equation}")
                outer = latex_environment_match(text, 3)
                self.assertEqual(outer, (
                    (0, len(r"\begin{equation}")),
                    (outer_close, len(text))))
                inner_start = text.index(opening)
                inner_end = text.index(closing)
                self.assertEqual(
                    latex_environment_match(text, inner_start + 4),
                    ((inner_start, inner_start + len(opening)),
                     (inner_end, inner_end + len(closing))))

    def test_inline_verb_and_lstinline_do_not_create_delimiters(self):
        for name in (r"\verb", r"\verb*", r"\lstinline"):
            with self.subTest(name=name):
                text = name + "|{ \\\\end{fake} % ( }|" + " " + r"\frac{x}{y}"
                fake_brace = text.index("{")
                self.assertIsNone(latex_match(text, fake_brace + 1))
                self.assertIsNone(latex_environment_match(
                    text, text.index(r"\end{fake}") + 3))
                marked = [(text[x:y], style) for x, y, style
                          in syntax_spans(text, "latex")]
                self.assertIn((r"\frac", "command"), marked)
                self.assertTrue(any(style == "verbatim" and name in word
                                    for word, style in marked))

    def test_unclosed_verbatim_does_not_color_remaining_commands(self):
        text = r"\begin{verbatim}" + "\n" + r"{ % \end{equation}"
        marked = [(text[a:b], style) for a, b, style
                  in syntax_spans(text, "latex")]
        self.assertEqual([word for word, style in marked
                          if style == "command"], [r"\begin{verbatim}"])
        self.assertIsNone(latex_match(text, text.index("{", 15) + 1))
        self.assertEqual(latex_environment_match(text, 4),
                         ((0, len(r"\begin{verbatim}")), None))

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

    def test_environment_pair_tags_cover_complete_commands(self):
        source = r"\begin{equation} x+y \end{equation}"
        self.app.new_buffer(path=str(self.root_path / "env.tex"), text=source)
        widget, _editor = self.app.current()
        widget.mark_set("insert", "1.3")
        widget.edit_modified(False)
        self.app._refresh_highlight(self.app.tabs.select())
        ranges = list(widget.tag_ranges("syntax_match"))
        self.assertEqual(len(ranges), 4)
        self.assertEqual(widget.get(ranges[0], ranges[1]), r"\begin{equation}")
        self.assertEqual(widget.get(ranges[2], ranges[3]), r"\end{equation}")
        self.assertFalse(widget.edit_modified())

    def test_mismatched_environment_tag_is_red(self):
        source = r"\begin{equation} x \end{align}"
        self.app.new_buffer(path=str(self.root_path / "bad.tex"), text=source)
        widget, _editor = self.app.current()
        widget.mark_set("insert", "1.4")
        self.app._refresh_highlight(self.app.tabs.select())
        self.assertTrue(widget.tag_ranges("syntax_unmatched"))
        self.assertFalse(widget.tag_ranges("syntax_match"))

    def test_verbatim_gui_tag_and_no_modified_flag(self):
        source = (r"\begin{verbatim}" "\n"
                  r"{ \begin{equation} % }\end{verbatim}" "\n"
                  r"\frac{a}{b}")
        self.app.new_buffer(path=str(self.root_path / "literal.tex"),
                            text=source)
        widget, _ = self.app.current()
        widget.edit_modified(False)
        self.app._refresh_highlight(self.app.tabs.select())
        self.assertTrue(widget.tag_ranges("syntax_verbatim"))
        self.assertEqual(widget.get("1.0", "end-1c"), source)
        self.assertFalse(widget.edit_modified())

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
