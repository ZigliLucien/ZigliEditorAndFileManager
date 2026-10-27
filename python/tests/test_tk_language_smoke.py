"""Optional Tk smoke tests: skip automatically on machines without a display."""
import tkinter as tk
import unittest
from zefm.editor.gui.tk_editor import Window

class LanguageGuiSmoke(unittest.TestCase):
    def setUp(self):
        try:
            self.root=tk.Tk()
        except tk.TclError:
            self.skipTest('No Tk display available')
        self.app=Window(self.root)

    def tearDown(self):
        if hasattr(self,'root'):
            self.root.destroy()

    def test_keymap_viewer(self):
        self.app.show_keymap()
        self.root.update()
        titles=[w.title() for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
        self.assertIn('ZEFM keymap reference',titles)

    def test_lexical_lookup_dialog(self):
        self.app.new_buffer(text='cœur')
        self.app.choose_language('fr')
        self.app.lookup_lexical_word()
        self.root.update()
        titles=[w.title() for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
        self.assertIn('French: cœur',titles)
