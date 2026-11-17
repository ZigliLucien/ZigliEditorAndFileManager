import json
import tempfile
import unittest
from pathlib import Path
from zefm.editor.shortcut_config import load_menus

class ShortcutTests(unittest.TestCase):
    def config(self, obj):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / 'keyboard.json'
        path.write_text(json.dumps(obj), encoding='utf-8')
        return path

    def test_default(self):
        menus = load_menus()
        self.assertEqual(next(c.shortcut for c in menus['Edit'] if c.label == 'Find'), 'Ctrl+S')
    def test_override(self):
        menus = load_menus(self.config({'shortcuts': {'Find': 'Ctrl+G'}}))
        self.assertEqual(next(c.shortcut for c in menus['Edit'] if c.label == 'Find'), 'Ctrl+G')
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            load_menus(self.config({'shortcuts': {'Find': 'Ctrl+R'}}))
    def test_unknown_rejected(self):
        with self.assertRaises(ValueError):
            load_menus(self.config({'shortcuts': {'Nonexistent': 'Ctrl+G'}}))
    def test_retired_java_file_actions_are_absent(self):
        menus = load_menus()
        labels = {cmd.label for commands in menus.values() for cmd in commands}
        shortcuts = {cmd.shortcut for commands in menus.values() for cmd in commands}
        self.assertNotIn('DocSave', labels)
        self.assertNotIn('ConvertStyle', labels)
        self.assertNotIn('Shift+F2', shortcuts)
        self.assertNotIn('Shift+F3', shortcuts)
        self.assertNotIn('DBClear', labels)
        self.assertNotIn('Close Shell Window', labels)
        self.assertNotIn('QuickMail', labels)
        self.assertNotIn('Get Mail', labels)
        self.assertNotIn('Ctrl+M', shortcuts)
        self.assertNotIn('Ctrl+Shift+M', shortcuts)
        self.assertNotIn('Ctrl+W', shortcuts)
        self.assertNotIn('Shift+F1', shortcuts)
        self.assertNotIn('Revert File', labels)
        self.assertIn('Revert Buffer', labels)
        self.assertEqual(next(c.shortcut for c in menus['File']
                              if c.label == 'Revert Buffer'), 'Ctrl+F9')
    def test_disable(self):
        menus = load_menus(self.config({'shortcuts': {'Find': None}}))
        self.assertIsNone(next(c.shortcut for c in menus['Edit'] if c.label == 'Find'))
