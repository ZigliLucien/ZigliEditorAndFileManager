import unittest
from pathlib import Path
from zefm.editor.legacy_keymaps import read_keymap,translation,key_event_to_java_code
BASE=Path(__file__).resolve().parents[1]/'legacy_keymaps'

class TranslationTests(unittest.TestCase):
    def test_french(self):
        m=read_keymap(BASE/'French.keymap')
        self.assertEqual(translation(m,'e',alt=True),'é')
        self.assertEqual(translation(m,'E',alt=True,shift=True),'è')
        self.assertIsNone(translation(m,'e'))
    def test_yiddish_multicodepoint(self):
        m=read_keymap(BASE/'Yiddish.keymap')
        self.assertEqual(translation(m,'b',alt=True),'ב')
        self.assertEqual(translation(m,'i',alt=True,shift=True),'אי')
        self.assertEqual(translation(m,'y',alt=True,shift=True),'יִ')
    def test_unknown_chord(self):
        m=read_keymap(BASE/'French.keymap')
        self.assertIsNone(translation(m,'F1',alt=True))
        self.assertIsNone(translation(m,'b',alt=True))
    def test_key_codes(self):
        self.assertEqual(key_event_to_java_code('bracketleft'),91)
        self.assertEqual(key_event_to_java_code('Z'),90)
