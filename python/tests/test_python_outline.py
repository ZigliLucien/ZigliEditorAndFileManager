"""Python AST outline tests including GUI navigation."""
import tkinter as tk
import unittest

from zefm.editor.python_outline import python_outline
from zefm.editor.gui.tk_editor import Window


class PythonOutlineTests(unittest.TestCase):
    def test_nested_classes_functions_and_async(self):
        source = ("def top():\n"
                  "    def inner(): pass\n"
                  "class Sample:\n"
                  "    def method(self): pass\n"
                  "    async def fetch(self): pass\n")
        headings = python_outline(source)
        self.assertEqual(
            [(x.kind, x.title, x.line, x.level) for x in headings],
            [("def", "top", 1, 0), ("def", "inner", 2, 1),
             ("class", "Sample", 3, 0), ("method", "method", 4, 1),
             ("async def", "fetch", 5, 1)])

    def test_syntax_errors_are_not_silent(self):
        with self.assertRaises(SyntaxError):
            python_outline("def broken(\n")

    def test_strings_and_comments_not_definitions(self):
        headings = python_outline(
            '# def phantom(): pass\n'
            'message = "class Phantom: pass"\n'
            'if True:\n    def real(): pass\n')
        self.assertEqual([h.title for h in headings], ["real"])


class PythonOutlineGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.widget, _ = self.app.current()
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", "class Example:\n    def method(self): pass\n")
        self.app.buffer_modes[self.app.tabs.select()] = (
            self.app.mode_registry.modes["python"])

    def test_outline_opens_and_jumps(self):
        self.app.show_python_outline()
        dialog = next(w for w in self.root.winfo_children()
                      if isinstance(w, tk.Toplevel) and w.title() == "Python Outline")
        def walk(widget, kind):
            if isinstance(widget, kind):
                yield widget
            for child in widget.winfo_children():
                yield from walk(child, kind)
        listing = next(walk(dialog, tk.Listbox))
        self.assertEqual(listing.size(), 2)
        listing.selection_clear(0, "end")
        listing.selection_set(1)
        import tkinter.ttk as ttk
        button = next(b for b in walk(dialog, ttk.Button) if b.cget("text") == "Go To")
        button.invoke()
        self.assertEqual(self.widget.index("insert"), "2.4")
        dialog.destroy()


if __name__ == "__main__":
    unittest.main()
