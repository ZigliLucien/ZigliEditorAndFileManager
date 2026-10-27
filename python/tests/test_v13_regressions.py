import unittest
from zefm.editor.vim_substitute import parse_substitute,substitution_matches
class V13RegressionTests(unittest.TestCase):
 def test_global_regex_capture(self):
  spec=parse_substitute(r"%s/(cat)([0-9]+)/\2-\1/g")
  self.assertEqual(substitution_matches("cat12 cat3",spec,0,10),[(0,5,"12-cat"),(6,10,"3-cat")])
 def test_confirm_case_insensitive(self):
  spec=parse_substitute("%s/cat/dog/gci")
  self.assertTrue(spec.confirm and spec.ignore_case and spec.global_line)
  self.assertEqual(len(substitution_matches("CAT cat",spec,0,7)),2)
 def test_current_line_only(self):
  spec=parse_substitute("s/a/b/g")
  self.assertEqual(substitution_matches("a a\na a",spec,4,7),[(4,5,"b"),(6,7,"b")])
