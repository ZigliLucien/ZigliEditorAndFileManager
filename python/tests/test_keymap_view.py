import unittest
from pathlib import Path
from zefm.editor.legacy_keymaps import read_keymap
from zefm.editor.keymap_view import shortcut_name,mapping_rows,mapping_text
BASE=Path(__file__).resolve().parents[1]/'legacy_keymaps'

class KeymapReferenceTests(unittest.TestCase):
    def test_chords(self):
        self.assertEqual(shortcut_name(66,''),'Alt+B')
        self.assertEqual(shortcut_name(66,'S'),'Alt+Shift+B')
        self.assertEqual(shortcut_name(66,'C'),'Alt+Meta+B')
        self.assertEqual(shortcut_name(91,''),'Alt+[')
    def test_yiddish(self):
        mapping=read_keymap(BASE/'Yiddish.keymap')
        rows=mapping_rows(mapping)
        self.assertIn(('Alt+B','ב','U+05D1 HEBREW LETTER BET'),rows)
        self.assertIn('HEBREW',mapping_text(mapping,'Yiddish'))
        self.assertIn('Alt+Shift+I',mapping_text(mapping,'Yiddish'))
        self.assertIn('U+05D0',mapping_text(mapping,'Yiddish'))
    def test_french(self):
        rows=mapping_rows(read_keymap(BASE/'French.keymap'))
        self.assertIn(('Alt+E','é','U+00E9 LATIN SMALL LETTER E WITH ACUTE'),rows)

if __name__=='__main__':unittest.main()
