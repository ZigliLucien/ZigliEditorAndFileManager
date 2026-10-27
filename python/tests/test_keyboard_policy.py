import unittest
from zefm.editor.gui.keyboard_policy import install_editor_shortcut

class KeyboardPolicyTests(unittest.TestCase):
    def test_mac_native_shortcuts_not_bound_twice(self):
        for name in ("Copy", "Paste", "Cut", "Undo", "Redo"):
            self.assertFalse(install_editor_shortcut(name,"darwin"),name)
    def test_mac_file_shortcuts_remain_custom(self):
        for name in ("Open", "Save", "Quit", "Find"):
            self.assertTrue(install_editor_shortcut(name,"darwin"),name)
    def test_linux_editor_shortcuts_preserved(self):
        for name in ("Copy", "Paste", "Cut", "Undo", "Redo", "Save"):
            self.assertTrue(install_editor_shortcut(name,"linux"),name)
