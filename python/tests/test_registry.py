import unittest
from zefm.editor.command_registry import Registry
class TestRegistry(unittest.TestCase):
 def test_menu_and_key_share_handler(self):
  r=Registry(); calls=[]
  r.bind("Cut",lambda:calls.append("cut"))
  r.invoke("Cut");r.key("Ctrl+X")
  self.assertEqual(calls,["cut","cut"])
 def test_pending_is_explicit(self):
  with self.assertRaises(NotImplementedError): Registry().invoke("Open")
