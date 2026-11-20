import unittest
from zefm.editor.mode_tools import indentation,validate_json,validate_json_details
from zefm.editor.modes import ModeSpec
class ModeToolTests(unittest.TestCase):
 def test_indentation(self):
  self.assertEqual(indentation(ModeSpec("python",4,False)),"    ")
  self.assertEqual(indentation(ModeSpec("makefile",4,True)),chr(9))
 def test_json(self):
  self.assertEqual(validate_json('{"a":1}'),(True,"Valid JSON"))
  ok,why=validate_json('{"a":}')
  self.assertFalse(ok)
  self.assertIn("line 1, column 6",why)
 def test_json_quotes_and_error_offsets(self):
  valid,detail,pos=validate_json_details('{"name": text}')
  self.assertFalse(valid)
  self.assertEqual(pos, len('{"name": '))
  self.assertIn("double quotes",detail)
  valid,detail,pos=validate_json_details('{name: "text"}')
  self.assertFalse(valid)
  self.assertEqual(pos, 1)
  self.assertIn("double quotes",detail)
  self.assertEqual(validate_json_details('{"name": true}'),
                   (True,"Valid JSON",None))
