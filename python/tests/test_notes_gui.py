"""Tk Notes button stays visible even when editor text is large."""
import tempfile
import tkinter as tk
from pathlib import Path
from unittest import TestCase, mock
from tkinter import ttk

from zefm.editor.gui.tk_editor import Window
from zefm.storage.word_notes import WordNotes


class NotesDialogSmoke(TestCase):
    def setUp(self):
        try:self.root=tk.Tk()
        except tk.TclError:self.skipTest('No display available')
        self.addCleanup(self.root.destroy)
        self.app=Window(self.root)
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.notes_path=Path(self.temp.name)/'notes.json'
        self.file=Path(self.temp.name)/'test.txt'
        self.file.write_text('ייִדיש')

    def test_save_button_visible_and_saves_note(self):
        with mock.patch.object(self.app,'_get_word_notes',return_value=WordNotes(self.notes_path)):
            self.app._edit_word_note(str(self.file),'ייִדיש')
        self.root.update()
        dialogs=[w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
        self.assertEqual(len(dialogs),1)
        dialog=dialogs[0]
        self.assertTrue(dialog.winfo_viewable())
        controls=[w for child in dialog.winfo_children() for w in child.winfo_children()
                  if isinstance(w,ttk.Button)]
        save=next(w for w in controls if w.cget('text')=='Save Note')
        self.assertTrue(save.winfo_viewable())
        self.assertLess(save.winfo_rooty()+save.winfo_height(),dialog.winfo_rooty()+dialog.winfo_height())
        editor=next(w for w in dialog.winfo_children() if isinstance(w,tk.Text))
        editor.insert('1.0','אַ גוטן טאָג')
        save.invoke()
        self.assertEqual(WordNotes(self.notes_path).get(str(self.file),'ייִדיש')['data'],'אַ גוטן טאָג')
        self.assertFalse(dialog.winfo_exists())
