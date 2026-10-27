import unittest
from zefm.editor.model import Buffer
from zefm.editor.selection import MemoryClipboard
from zefm.editor.tp_editor import TPEditor

class EditorTests(unittest.TestCase):
    def test_cut_reposition_and_copy(self):
        clip=MemoryClipboard()
        ed=TPEditor(clip,Buffer("abc שלום xyz"))
        ed.state.move(4)
        ed.state.move(8,selecting=True)
        self.assertTrue(ed.shortcut("Ctrl+C"))
        self.assertEqual(clip.read(),"שלום")
        self.assertTrue(ed.menu("Cut"))
        self.assertEqual(ed.state.buffer.text,"abc  xyz")
        ed.state.move(len(ed.state.buffer.text))
        ed.shortcut("Ctrl+V")
        self.assertEqual(ed.state.buffer.text,"abc  xyzשלום")
        self.assertTrue(ed.state.buffer.modified)
    def test_paste_replaces_selection(self):
        ed=TPEditor(MemoryClipboard("œ"),Buffer("abc"))
        ed.state.move(1);ed.state.move(2,selecting=True)
        ed.menu("Paste")
        self.assertEqual(ed.state.buffer.text,"aœc")
    def test_copy_without_selection_does_not_clear_clipboard(self):
        clip=MemoryClipboard("keep")
        ed=TPEditor(clip,Buffer("abc"))
        self.assertFalse(ed.shortcut("Ctrl+C"))
        self.assertEqual(clip.read(),"keep")
