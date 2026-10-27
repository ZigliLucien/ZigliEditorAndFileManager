import unittest
from zefm.editor.json_tools import parse_simple_path,value_at_path,format_json
class ToolsTests(unittest.TestCase):
 def test_path(self):
  p=parse_simple_path('.people[1]["first name"]')
  self.assertEqual(p,['people',1,'first name'])
  self.assertEqual(value_at_path('{"people":[{},{"first name":"Bob"}]}',p),'Bob')
 def test_format(self):
  self.assertIn(chr(10),format_json('{"a":1}'))
