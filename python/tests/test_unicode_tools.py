import unittest
from zefm.editor.unicode_tools import parse_codepoint,unicode_range,search_unicode_names
class UnicodeToolsTests(unittest.TestCase):
    def test_codepoints(self):
        self.assertEqual(parse_codepoint('U+05D0'),'א')
        self.assertEqual(parse_codepoint('03BB'),'λ')
        self.assertEqual(parse_codepoint('1F642'),'🙂')
    def test_invalid(self):
        for x in ['U+110000','D800','U+xyz','']:
            with self.assertRaises(ValueError):parse_codepoint(x)
    def test_browse(self):
        chars=unicode_range('05D0-05D2')
        self.assertEqual([chr(cp) for cp,_ in chars],['א','ב','ג'])
    def test_bounded(self):
        for x in ['0000-2000','05FF-0590','bad']:
            with self.assertRaises(ValueError):unicode_range(x)


class UnicodeSearchTests(unittest.TestCase):
    def test_search_name(self):
        found=search_unicode_names("HEBREW LETTER ALEF")
        self.assertIn((0x05D0,"HEBREW LETTER ALEF"),found)
    def test_search_multiple_terms(self):
        found=search_unicode_names("GREEK SMALL LETTER LAMDA")
        self.assertTrue(any(cp==0x03BB for cp,_ in found))
    def test_empty_and_limit(self):
        with self.assertRaises(ValueError):search_unicode_names(" ")
        self.assertEqual(len(search_unicode_names("LETTER",limit=3)),3)


class UnicodeCharacterDescriptionTests(unittest.TestCase):
    def test_plain(self):
        from zefm.editor.unicode_tools import character_description
        self.assertEqual(character_description('א'),'U+05D0  HEBREW LETTER ALEF')
    def test_combining(self):
        from zefm.editor.unicode_tools import character_description
        self.assertIn('combining class',character_description('ַ'))
    def test_reject_multiple(self):
        from zefm.editor.unicode_tools import character_description
        with self.assertRaises(ValueError):character_description('ab')
