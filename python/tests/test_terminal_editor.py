"""Terminal editor core and CLI dispatch (does not require a TTY)."""
import unittest
from unittest.mock import patch, Mock

from zefm.__main__ import build_parser, main
from pathlib import Path
from zefm.editor.terminal_editor import TextDocument, edit_screen


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

    def test_ctrl_b_f_p_n_bindings(self):
        doc = TextDocument.from_text("abcd\nxy")
        doc.row, doc.col = 1, 1
        screen = Mock()
        screen.getmaxyx.return_value = (24, 80)
        screen.get_wch.side_effect = [
            "\x10",  # Ctrl-P: previous line
            "\x06",  # Ctrl-F: forward
            "\x02",  # Ctrl-B: backward
            "\x0e",  # Ctrl-N: next line
            "\x11",  # Ctrl-Q: quit
        ]
        with patch("zefm.editor.terminal_editor.curses.raw"), \
             patch("zefm.editor.terminal_editor.curses.noecho"):
            edit_screen(screen, Path("sample.txt"), doc)
        self.assertEqual((doc.row, doc.col), (1, 1))
        self.assertFalse(doc.dirty)
        self.assertEqual(screen.get_wch.call_count, 5)

    def test_undo_redo_key_sequence_and_savepoint(self):
        doc = TextDocument.from_text("abc")
        doc.col = 3
        screen = Mock()
        screen.getmaxyx.return_value = (24, 80)
        screen.get_wch.side_effect = [
            "d", "\x1f", "\x18", "\x12", "\x1a", "\x11",
        ]
        with patch("zefm.editor.terminal_editor.curses.raw"), \
             patch("zefm.editor.terminal_editor.curses.noecho"):
            edit_screen(screen, Path("sample.txt"), doc)
        self.assertEqual(doc.text, "abc")
        self.assertFalse(doc.dirty)

    def test_undo_kill_and_yank(self):
        doc = TextDocument.from_text("abc def")
        doc.col = 4
        screen = Mock()
        screen.getmaxyx.return_value = (24, 80)
        screen.get_wch.side_effect = [
            "\x0b", "\x19", "\x1f", "\x11", "\x11",
        ]
        with patch("zefm.editor.terminal_editor.curses.raw"), \
             patch("zefm.editor.terminal_editor.curses.noecho"):
            edit_screen(screen, Path("sample.txt"), doc)
        self.assertEqual(doc.text, "abc ")
        self.assertTrue(doc.dirty)

    def test_go_to_line_and_search_wrap(self):
        doc = TextDocument.from_text("zero\nfirst alpha\nsecond\nthird alpha")
        doc.goto_line(3)
        self.assertEqual((doc.row, doc.col), (2, 0))
        doc.goto_line(900)
        self.assertEqual((doc.row, doc.col), (3, 0))
        self.assertTrue(doc.search("alpha", direction=-1))
        self.assertEqual((doc.row, doc.col), (1, 6))
        self.assertTrue(doc.search("alpha", direction=-1, repeat=True))
        self.assertEqual((doc.row, doc.col), (3, 6))
        self.assertTrue(doc.search("alpha", direction=1, repeat=True))
        self.assertEqual((doc.row, doc.col), (1, 6))
        before = (doc.row, doc.col)
        self.assertFalse(doc.search("not-present"))
        self.assertEqual((doc.row, doc.col), before)
        self.assertFalse(doc.dirty)

    def test_goto_search_cancel_and_repeat_keys(self):
        doc = TextDocument.from_text("first\nbanana\nthird banana")
        screen = Mock()
        screen.getmaxyx.return_value = (24, 80)
        screen.get_wch.side_effect = [
            "\x07", "2", "\n",     # Ctrl-G 2
            "\x12", "b", "a", "n", "a", "n", "a", "\n",
            "\x12", "\n",        # Ctrl-R Enter repeats last search
            "\x18", "\x06", "\n",  # Ctrl-X Ctrl-F forward repeat
            "\x07", "\x1b",     # Cancel goto line
            "\x11",
        ]
        with patch("zefm.editor.terminal_editor.curses.raw"), \
             patch("zefm.editor.terminal_editor.curses.noecho"):
            edit_screen(screen, Path("sample.txt"), doc)
        self.assertEqual((doc.row, doc.col), (1, 0))
        self.assertFalse(doc.dirty)

    def test_incremental_search_preview_and_cancel(self):
        doc = TextDocument.from_text("alpha\nsecond\nthird alpha")
        doc.goto_line(2)
        origin = (doc.row, doc.col)
        screen = Mock()
        screen.getmaxyx.return_value = (10, 40)
        screen.get_wch.side_effect = [
            "\x12", "a", "l", "p", "h", "a", "\x1b", "\x11",
        ]
        with patch("zefm.editor.terminal_editor.curses.raw"), \
             patch("zefm.editor.terminal_editor.curses.noecho"):
            edit_screen(screen, Path("sample.txt"), doc)
        self.assertEqual((doc.row, doc.col), origin)
        self.assertEqual(doc.last_search, "")
        self.assertFalse(doc.dirty)
        # The document is redrawn for each incremental search input.
        self.assertGreaterEqual(screen.erase.call_count, 7)

    def test_failed_incremental_search_preserves_last_search(self):
        doc = TextDocument.from_text("alpha\nbeta alpha")
        self.assertTrue(doc.search("alpha", direction=1))
        saved = doc.last_search
        screen = Mock()
        screen.getmaxyx.return_value = (10, 40)
        screen.get_wch.side_effect = [
            "\x12", "z", "z", "z", "\n", "\x11",
        ]
        origin = (doc.row, doc.col)
        with patch("zefm.editor.terminal_editor.curses.raw"), \
             patch("zefm.editor.terminal_editor.curses.noecho"):
            edit_screen(screen, Path("sample.txt"), doc)
        self.assertEqual(doc.last_search, saved)
        self.assertEqual((doc.row, doc.col), origin)

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
