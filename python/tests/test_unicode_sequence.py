import unittest
from zefm.editor.unicode_tools import character_context_description
class UnicodeSequenceTests(unittest.TestCase):
    def test_combining(self):
        text='a'+'\u0301'+'b'
        self.assertEqual(character_context_description(text,0)[0],text[:2])
        self.assertEqual(character_context_description(text,1)[0],text[:2])
        self.assertIn('COMBINING ACUTE ACCENT',character_context_description(text,1)[1][-1])
        self.assertEqual(character_context_description(text,2)[0],'b')
    def test_yiddish(self):
        self.assertEqual(character_context_description('\u05d1\u05bf',1)[0],'\u05d1\u05bf')
    def test_out_of_range(self):
        with self.assertRaises(ValueError):character_context_description('',0)
