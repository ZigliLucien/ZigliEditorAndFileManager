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
    def test_disable(self):
        menus = load_menus(self.config({'shortcuts': {'Find': None}}))
        self.assertIsNone(next(c.shortcut for c in menus['Edit'] if c.label == 'Find'))
