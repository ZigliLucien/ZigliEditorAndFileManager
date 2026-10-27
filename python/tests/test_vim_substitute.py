import unittest
from zefm.editor.vim_substitute import parse_substitute,substitution_matches
class VimTests(unittest.TestCase):
 def test_global_regex_capture(self):
  spec=parse_substitute(r'%s/(foo)(\d+)/\2-\1/gc')
  self.assertTrue(spec.confirm)
  self.assertEqual(substitution_matches('foo12 foo3',spec,0,10),[(0,5,'12-foo'),(6,10,'3-foo')])
 def test_first_per_line(self):
  spec=parse_substitute('s/a/b/')
  self.assertEqual(len(substitution_matches('aa\naa',spec,0,5)),2)
 def test_escaped_delimiter(self):
  self.assertEqual(parse_substitute(r's/a\/b/c/').pattern,'a/b')
