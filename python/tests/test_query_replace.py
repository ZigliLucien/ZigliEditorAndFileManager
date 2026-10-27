import unittest
from zefm.editor.query_replace import QueryReplace
class QueryReplaceTests(unittest.TestCase):
    def test_yes_no_all(self):
        q=QueryReplace('aa aa aa', 'aa', 'b')
        q.answer('y');q.answer('n');q.answer('!')
        self.assertEqual(q.text,'b aa b')
        self.assertEqual((q.replaced,q.skipped,q.done),(2,1,True))
    def test_quit_keeps_edits(self):
        q=QueryReplace('a a','a','b');q.answer('y');q.answer('q')
        self.assertEqual(q.text,'b a')
    def test_replacement_containing_search_does_not_loop(self):
        q=QueryReplace('a a','a','aa');q.answer('!')
        self.assertEqual(q.text,'aa aa')
    def test_empty_search_rejected(self):
        with self.assertRaises(ValueError):QueryReplace('x','','y')
