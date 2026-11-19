"""v127: structural LaTeX issue discovery and non-destructive navigation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest

from zefm.editor.syntax_highlight import MAX_CHARS, latex_issues
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles


class LatexIssueScanTests(unittest.TestCase):
    def test_clean_nested_braces_and_environments(self):
        text = (r"\begin{align}" "\n"
                r"\frac{x^{2}}{\sqrt{1+y}} \begin{split} a&=b \end{split}" "\n"
                r"\end{align}")
        self.assertEqual(latex_issues(text), [])

    def test_unmatched_braces_and_environment_names(self):
        text = (r"\begin{equation}" "\n" r"\frac{x}{y" "\n"
                r"\end{align}" "\n" "}}")
        issues = latex_issues(text)
        self.assertEqual(len(issues), 3)
        descriptions = [message for _, _, message in issues]
        self.assertTrue(any("begin{equation}" in message for message in descriptions))
        self.assertTrue(any("end{align}" in message for message in descriptions))
        self.assertTrue(any("brace" in message for message in descriptions))

    def test_extra_closing_brace(self):
        self.assertEqual(latex_issues("a}b"), [(1, 1, "Unexpected closing brace }")])

    def test_ignores_escaped_braces_comments_and_literal_regions(self):
        text = (r"\{ \} % { \begin{fake}" "\n"
                r"\begin{verbatim}" "\n"
                r"{ \end{wrong} % \begin{other}" "\n"
                r"\end{verbatim}" "\n"
                r"\verb|{ \end{fake} |" "\n"
                r"\begin{equation} {x} \end{equation}")
        self.assertEqual(latex_issues(text), [])

    def test_empty_and_large(self):
        self.assertEqual(latex_issues(""), [])
        self.assertEqual(latex_issues("{" * (MAX_CHARS + 1)), [])


class LatexIssueGuiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
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

    def test_cyclic_navigation_preserves_text_and_saved_state(self):
        source = r"\begin{equation}" + "\n" + "{x" + "\n" + r"\end{align}"
        self.app.new_buffer(path=str(self.directory / "a.tex"), text=source)
        widget, editor = self.app.current()
        before = widget.get("1.0", "end-1c")
        widget.edit_modified(False)
        widget.mark_set("insert", "1.0")
        issues = latex_issues(before)
        positions = [f"1.0 + {issue[0] + (1 if issue[1] == 1 else 0)} chars"
                     for issue in issues]
        self.assertGreaterEqual(len(issues), 2)
        for expected in positions[1:] + positions[:1]:
            self.app.next_latex_issue()
            self.assertEqual(widget.index("insert"), widget.index(expected))
        self.assertEqual(widget.get("1.0", "end-1c"), before)
        self.assertFalse(widget.edit_modified())
        self.assertFalse(editor.state.buffer.modified)
        self.assertIn("LaTeX issue", self.app.status.get())

    def test_previous_navigation_cycles_backwards(self):
        source = (r"\begin{equation}" "\n"
                  "{x" "\n"
                  r"\end{align}" "\n"
                  "}")
        self.app.new_buffer(path=str(self.directory / "back.tex"), text=source)
        widget, editor = self.app.current()
        problems = latex_issues(source)
        self.assertGreaterEqual(len(problems), 3)
        widget.mark_set("insert", "1.0")
        for issue in reversed(problems):
            self.app.previous_latex_issue()
            expected = issue[0] + (1 if issue[1] == 1 else 0)
            self.assertEqual(widget.index("insert"),
                             widget.index(f"1.0 + {expected} chars"))
        self.assertEqual(widget.get("1.0", "end-1c"), source)
        self.assertFalse(editor.state.buffer.modified)

    def test_issue_list_navigation_and_stale_guard(self):
        source = r"\begin{equation}" + "\n" + "{ x"
        self.app.new_buffer(path=str(self.directory / "list.tex"), text=source)
        widget, editor = self.app.current()
        self.app.list_latex_issues()
        dialogs = [w for w in self.root.winfo_children()
                   if isinstance(w, tk.Toplevel)]
        self.assertTrue(dialogs)
        dialog = dialogs[-1]
        listing = next(w for w in dialog.winfo_children()
                       if isinstance(w, tk.Frame) for w in w.winfo_children()
                       if isinstance(w, tk.Listbox))
        self.assertEqual(listing.size(), len(latex_issues(source)))
        listing.selection_clear(0, "end")
        listing.selection_set(1)
        listing.event_generate("<Return>")
        self.assertEqual(widget.index("insert"),
                         widget.index("1.0 + 1 chars"))
        widget.insert("end", "}")
        original_index = widget.index("insert")
        listing.selection_clear(0, "end")
        listing.selection_set(0)
        with patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as notice:
            listing.event_generate("<Return>")
        notice.assert_called_once()
        self.assertEqual(widget.index("insert"), original_index)
        dialog.destroy()

    def test_no_issues_and_non_latex_buffers(self):
        self.app.new_buffer(path=str(self.directory / "a.tex"),
                            text=r"\frac{a}{b}")
        widget, _ = self.app.current()
        widget.mark_set("insert", "1.2")
        self.app.next_latex_issue()
        self.assertIn("no unmatched", self.app.status.get())
        self.assertEqual(widget.index("insert"), "1.2")
        self.app.new_buffer(path=str(self.directory / "a.py"), text="x = 2")
        self.app.next_latex_issue()
        self.assertIn("LaTeX buffers", self.app.status.get())


if __name__ == "__main__":
    unittest.main()
