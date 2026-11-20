"""v131: LaTeX outline extraction and safe Tk navigation."""
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.latex_outline import OutlineHeading, latex_outline
from zefm.editor.syntax_highlight import MAX_CHARS
from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles
from zefm.editor.shortcut_config import load_menus


class LatexOutlineTests(unittest.TestCase):
    def test_heading_levels_and_starred_titles(self):
        text = (r"\part{Introduction}" "\n"
                r"\chapter*{Background}" "\n"
                r"\section{Main result}" "\n"
                r"\subsection[Short]{The {Krawtchouk} limit}" "\n"
                r"\subsubsection{Proof}" "\n"
                r"\paragraph{Details}" "\n"
                r"\subparagraph{Remark}")
        items = latex_outline(text)
        self.assertEqual(
            [item.kind for item in items],
            ["part", "chapter", "section", "subsection",
             "subsubsection", "paragraph", "subparagraph"])
        self.assertEqual([item.level for item in items], list(range(7)))
        self.assertTrue(items[1].starred)
        self.assertEqual(items[3].title, "The {Krawtchouk} limit")
        self.assertEqual(items[3].offset, text.index(r"\subsection"))

    def test_multiline_and_escaped_braces(self):
        text = (r"\section" "\n"
                r"  [Overview]" "\n"
                r"  {Spectral \{ symmetry" "\n"
                r"   and {Gaussian} limits}" "\n"
                r"\section*{Appendix}")
        items = latex_outline(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(
            items[0].title, r"Spectral \{ symmetry and {Gaussian} limits")
        self.assertTrue(items[1].starred)

    def test_comments_verbatim_inline_and_literal_escape_ignored(self):
        text = (r"% \section{Fake}" "\n"
                r"\verb|\section{fake}|" "\n"
                r"\begin{verbatim}" "\n"
                r"\chapter{literal}" "\n"
                r"\end{verbatim}" "\n"
                r"\\section{escaped}" "\n"
                r"\section{Real}")
        items = latex_outline(text)
        self.assertEqual([(item.kind, item.title) for item in items],
                         [("section", "Real")])

    def test_incomplete_and_macro_like_commands_not_treated_as_heading(self):
        text = (r"\sectional{not section}" "\n"
                r"\section{complete}" "\n"
                r"\subsection{incomplete")
        items = latex_outline(text)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "complete")

    def test_empty_whitespace_and_limits(self):
        self.assertEqual(latex_outline(""), [])
        self.assertEqual(latex_outline(r"\section{ }")[0].title, "(untitled)")
        self.assertEqual(latex_outline("x" * (MAX_CHARS + 1)), [])

    def test_registry_single_action(self):
        matches = [item for group in load_menus().values()
                   for item in group
                   if item.label == "LaTeX Document Outline"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].shortcut, "Ctrl+Shift+L")


class LatexOutlineGuiTests(unittest.TestCase):
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

    def _open_outline(self, source):
        self.app.new_buffer(path=str(self.directory / "source.tex"),
                            text=source)
        self.app.show_latex_outline()
        dialogs = [item for item in self.root.winfo_children()
                   if isinstance(item, tk.Toplevel)
                   and item.title() == "LaTeX Document Outline"]
        self.assertEqual(len(dialogs), 1)
        dialog = dialogs[0]
        frame = next(child for child in dialog.winfo_children()
                     if isinstance(child, tk.ttk.Frame)
                     and any(isinstance(w, tk.Listbox)
                             for w in child.winfo_children()))
        listing = next(child for child in frame.winfo_children()
                       if isinstance(child, tk.Listbox))
        filter_row = next(child for child in dialog.winfo_children()
                          if isinstance(child, tk.ttk.Frame)
                          and any(isinstance(w, tk.ttk.Entry)
                                  for w in child.winfo_children()))
        entry = next(child for child in filter_row.winfo_children()
                     if isinstance(child, tk.ttk.Entry))
        return dialog, listing, entry

    def test_filter_navigation_and_no_buffer_modification(self):
        source = (r"\section{First}" "\n"
                  "some body\n"
                  r"\subsection{Gaussian spectral limit}" "\n"
                  r"\section{Last}")
        dialog, listing, entry = self._open_outline(source)
        widget, editor = self.app.current()
        widget.edit_modified(False)
        self.assertEqual(listing.size(), 3)
        entry.insert(0, "gaussian")
        self.assertEqual(listing.size(), 1)
        listing.event_generate("<Return>")
        self.root.update()
        self.assertEqual(widget.index("insert"),
                         widget.index(f"1.0 + {source.index(r'\subsection')} chars"))
        self.assertEqual(widget.get("1.0", "end-1c"), source)
        self.assertFalse(widget.edit_modified())
        self.assertFalse(editor.state.buffer.modified)
        dialog.destroy()

    def test_stale_outline_refuses_then_refresh_works(self):
        source = r"\section{Old}" + "\n" + r"\section{Next}"
        dialog, listing, entry = self._open_outline(source)
        widget, _editor = self.app.current()
        widget.insert("1.0", "new text\n")
        before = widget.index("insert")
        with patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as info:
            listing.event_generate("<Return>")
            self.root.update()
        info.assert_called_once()
        self.assertEqual(widget.index("insert"), before)
        refresh = next(item for child in dialog.winfo_children()
                       for item in child.winfo_children()
                       if isinstance(item, tk.ttk.Button)
                       and item.cget("text") == "Refresh")
        refresh.invoke()
        listing.event_generate("<Return>")
        self.root.update()
        self.assertEqual(widget.index("insert"), "2.0")
        dialog.destroy()

    def test_non_latex_buffer_has_no_outline_window(self):
        self.app.new_buffer(path=str(self.directory / "code.py"),
                            text="print('hello')")
        self.app.show_latex_outline()
        self.assertIn("requires a LaTeX buffer", self.app.status.get())
        self.assertFalse(any(
            isinstance(child, tk.Toplevel) and
            child.title() == "LaTeX Document Outline"
            for child in self.root.winfo_children()))


if __name__ == "__main__":
    unittest.main()
