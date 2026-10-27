import unittest
from zefm.editor.json_path import locate_path,navigate,paths_at
from zefm.editor.json_tools import parse_simple_path
class JsonV20(unittest.TestCase):
 def setUp(self):self.text='{"people":[{"name":"A"},{"name":"B"}],"empty":{}}'
 def test_locate(self):
  offset=locate_path(self.text,parse_simple_path('.people[1].name'))
  self.assertEqual(paths_at(self.text,offset),'.people[1].name')
 def test_child(self):
  offset=locate_path(self.text,['people'])
  target=navigate(self.text,offset,'child')
  self.assertEqual(target[1],'.people[0]')
 def test_empty_child(self):
  offset=locate_path(self.text,['empty'])
  self.assertIsNone(navigate(self.text,offset,'child'))
 def test_missing(self):
  self.assertIsNone(locate_path(self.text,['missing']))
