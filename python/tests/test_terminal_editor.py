"""Terminal editor core and CLI dispatch (does not require a TTY)."""
import unittest
from unittest.mock import patch

from zefm.__main__ import build_parser, main
from zefm.editor.terminal_editor import TextDocument


class TerminalEditingTests(unittest.TestCase):
    def test_insert_newline_and_backspace(self):
        doc = TextDocument.from_text("hello")
        doc.move(col_delta=5)
        doc.newline()
        doc.insert("world")
        self.assertEqual(doc.text, "hello\nworld")
        doc.backspace()
        self.assertEqual(doc.text, "hello\nworl")
        doc.col = 0
        doc.backspace()
        self.assertEqual(doc.text, "helloworl")
        self.assertTrue(doc.dirty)

    def test_delete_and_move(self):
        doc = TextDocument.from_text("abc\ndef")
        doc.col = 1
        doc.delete()
        self.assertEqual(doc.text, "ac\ndef")
        doc.move(row_delta=1)
        self.assertEqual((doc.row, doc.col), (1, 1))
        doc.col = 3
        doc.delete()
        self.assertEqual(doc.text, "ac\ndef")

    def test_emacs_kill_line_and_yank(self):
        doc = TextDocument.from_text("alpha beta\nsecond")
        doc.col = 6
        doc.kill_line()
        self.assertEqual(doc.text, "alpha \nsecond")
        self.assertEqual(doc.kill_buffer, "beta")
        doc.yank()
        self.assertEqual(doc.text, "alpha beta\nsecond")
        doc.col = 10
        doc.kill_line()
        self.assertEqual(doc.text, "alpha betasecond")
        self.assertEqual(doc.kill_buffer, "\n")
        doc.yank()
        self.assertEqual(doc.text, "alpha beta\nsecond")

    def test_kill_at_end_of_file_is_noop(self):
        doc = TextDocument.from_text("end")
        doc.col = 3
        doc.kill_line()
        self.assertFalse(doc.dirty)
        self.assertEqual(doc.text, "end")

    def test_terminal_dispatch(self):
        self.assertTrue(build_parser().parse_args(["-t", "file.txt"]).terminal)
        with patch("zefm.editor.terminal_editor.run_terminal_editor") as run:
            main(["--terminal", "file.txt"])
            run.assert_called_once_with("file.txt")

    def test_terminal_requires_one_file(self):
        for arguments in (["--terminal"], ["--terminal", "a", "b"],
                          ["--terminal", "--mode", "files", "file"]):
            with self.subTest(args=arguments):
                with self.assertRaises(SystemExit):
                    main(arguments)


if __name__ == "__main__":
    unittest.main()
