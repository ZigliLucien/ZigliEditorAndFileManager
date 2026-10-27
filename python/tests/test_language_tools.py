import unittest
from pathlib import Path
from zefm.editor.language_tools import LANGUAGES,expand_suffix,language_dictionary

ROOT=Path(__file__).resolve().parents[1]/"dictionaries"
class LanguageToolsTests(unittest.TestCase):
    def test_longest_match(self):
        self.assertEqual(expand_suffix("xxcoeur",7,{"eur":"!","coeur":"cœur"}),(2,7,"cœur"))
    def test_no_match(self):
        self.assertIsNone(expand_suffix("hello",5,{"coeur":"cœur"}))
    def test_invalid_cursor(self):
        with self.assertRaises(ValueError):expand_suffix("hi",10,{})
    def test_french(self):
        self.assertEqual(language_dictionary(ROOT,"fr")["coeur"],"cœur")
    def test_yiddish_empty_supported(self):
        self.assertEqual(language_dictionary(ROOT,"yi"),{})
    def test_system_and_invalid(self):
        self.assertEqual(language_dictionary(ROOT,"system"),{})
        with self.assertRaises(ValueError):language_dictionary(ROOT,"xx")
