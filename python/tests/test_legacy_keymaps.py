import unittest
from pathlib import Path
from zefm.editor.legacy_keymaps import parse_keymap,read_keymap
ROOT=Path(__file__).resolve().parents[1]/'legacy_keymaps'
class LegacyKeymapTests(unittest.TestCase):
    def test_yiddish(self):
        data=read_keymap(ROOT/'Yiddish.keymap')
        self.assertEqual(data[(66,'')].single_character,'ב')
        self.assertEqual(data[(66,'S')].single_character,chr(64332))
        self.assertEqual(data[(73,'S')].decimal_payload,'14881497')
        self.assertIsNone(data[(73,'S')].single_character)
    def test_all_archived_keymaps(self):
        for path in ROOT.glob('*.keymap'):
            with self.subTest(path=path):self.assertGreater(len(read_keymap(path)),5)
    def test_invalid_and_duplicate(self):
        with self.assertRaises(ValueError):parse_keymap('bogus')
        with self.assertRaises(ValueError):parse_keymap('65=97\n65=98')
