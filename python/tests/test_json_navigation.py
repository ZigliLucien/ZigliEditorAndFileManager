import unittest
from zefm.editor.json_path import navigate,paths_at
class NavigationTests(unittest.TestCase):
 def test_siblings_and_parent(self):
  text='{"a": 1, "b": {"x": 2, "y": 3}, "c": 4}'
  start=text.index('"x"')+1
  offset,path=navigate(text,start,'next')
  self.assertEqual(path,'.b.y')
  self.assertEqual(paths_at(text,offset),'.b.y')
  offset,path=navigate(text,offset,'parent')
  self.assertEqual(path,'.b')
  self.assertEqual(paths_at(text,offset),'.b')
  offset,path=navigate(text,offset,'previous')
  self.assertEqual(path,'.a')
 def test_arrays(self):
  text='[10,20,30]'
  offset,path=navigate(text,text.index('20'),'next')
  self.assertEqual((offset,path),(text.index('30'),'.[2]'))
  self.assertIsNone(navigate(text,text.index('30'),'next'))
 def test_invalid_and_root(self):
  self.assertIsNone(navigate('{bad}',0,'parent'))
  self.assertIsNone(navigate('{"a":1}',0,'parent'))
