import unittest
from zefm.editor.mode_tools import indentation,validate_json
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
