import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from zefm.editor.gui.tk_editor import Window

class EscapeToggleTests(unittest.TestCase):
    def setUp(self):
        self.window=Window.__new__(Window)
        self.window.vim_normal=False
        self.window.current=Mock(return_value=(object(),None))
        self.window._status=Mock()
    def test_escape_toggles_both_directions(self):
        key=SimpleNamespace(keysym="Escape",state=0,char="\x1b")
        self.assertEqual(self.window._vim_key(key),"break")
        self.assertTrue(self.window.vim_normal)
        self.assertEqual(self.window._vim_key(key),"break")
        self.assertFalse(self.window.vim_normal)
        self.assertEqual(self.window._status.call_count,2)
    def test_i_still_exits_normal_mode(self):
        self.window.vim_normal=True
        self.assertEqual(self.window._vim_key(SimpleNamespace(keysym="i",state=0,char="i")),"break")
        self.assertFalse(self.window.vim_normal)
