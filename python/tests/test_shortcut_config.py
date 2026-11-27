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
        menus = load_menus(self.config({'shortcuts': {'Find': 'Shift+Ctrl+j'}}))
        self.assertEqual(next(c.shortcut for c in menus['Edit'] if c.label == 'Find'), 'Ctrl+Shift+J')

    def test_goto_line_shortcut_cannot_be_reused(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate shortcut'):
            load_menus(self.config({'shortcuts': {'Find': 'Ctrl+G'}}))
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            load_menus(self.config({'shortcuts': {'Find': 'Ctrl+R'}}))
    def test_fixed_new_close_shortcuts_cannot_be_stolen(self):
        for shortcut in ('Ctrl+N', 'Ctrl+Shift+W', 'Shift+Ctrl+W'):
            with self.subTest(shortcut=shortcut):
                with self.assertRaisesRegex(ValueError, 'Duplicate shortcut'):
                    load_menus(self.config(
                        {'shortcuts': {'Find': shortcut}}))

    def test_malformed_shortcuts_are_rejected(self):
        for shortcut in ('NotAKey', 'Ctrl+', 'Ctrl+Ctrl+G',
                         'Shift+DeleteEverything', 'Q', 'Ctrl+Q+P',
                         'Ctrl+Shift+Shift+G', ' Ctrl+G'):
            with self.subTest(shortcut=shortcut):
                with self.assertRaises(ValueError):
                    load_menus(self.config(
                        {'shortcuts': {'Find': shortcut}}))

    def test_function_keys_and_disabled_mapping_remain_supported(self):
        menu = load_menus(self.config({'shortcuts': {
            'Find': 'F12', 'Replace': None}}))
        edit = {c.label: c.shortcut for c in menu['Edit']}
        self.assertEqual(edit['Find'], 'F12')
        self.assertIsNone(edit['Replace'])

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
        # Ctrl+Shift+M was repurposed in v130 for matching LaTeX
        # delimiters and extended in v134 to Python and JSON.
        self.assertIn('Ctrl+Shift+M', shortcuts)
        self.assertEqual(
            next(cmd.shortcut for group in menus.values() for cmd in group
                 if cmd.label == 'Go to Matching LaTeX Delimiter'),
            'Ctrl+Shift+M')
        self.assertNotIn('Ctrl+W', shortcuts)
        self.assertNotIn('Shift+F1', shortcuts)
        self.assertNotIn('Revert File', labels)
        self.assertIn('Revert Buffer', labels)
        self.assertEqual(next(c.shortcut for c in menus['File']
                              if c.label == 'Revert Buffer'), 'Ctrl+F9')
    def test_disable(self):
        menus = load_menus(self.config({'shortcuts': {'Find': None}}))
        self.assertIsNone(next(c.shortcut for c in menus['Edit'] if c.label == 'Find'))
