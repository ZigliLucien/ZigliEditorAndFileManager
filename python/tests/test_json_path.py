import unittest
from zefm.editor.json_path import paths_at
class JsonPathTests(unittest.TestCase):
 def test_nested(self):
  text='{"people":[{"name":"Alice"},{"address":{"city":"London"}}]}'
  self.assertEqual(paths_at(text,text.index('London')+2),'.people[1].address.city')
 def test_escaped_key(self):
  text='{"first name":{"a.b":[true]}}'
  self.assertEqual(paths_at(text,text.index('true')+1),'.["first name"]["a.b"][0]')
 def test_root(self):
  self.assertEqual(paths_at('[1]',0),'.')
 def test_invalid(self):
  self.assertIsNone(paths_at('{"x":}',3))
 def test_unicode(self):
  text='{"שלום":[{"œ":12}]}'
  self.assertEqual(paths_at(text,text.index('12')),'.["שלום"][0]["œ"]')

 def test_top_level_key(self):
  text='{"alpha": 12, "beta": {"x": true}}'
  self.assertEqual(paths_at(text,text.index("alpha")+2),".alpha")
  self.assertEqual(paths_at(text,text.index("beta")+2),".beta")
  self.assertEqual(paths_at(text,text.index(":")+1),".alpha")
