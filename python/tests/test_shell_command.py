"""v110: one-off Shell menu runs argv safely without a persistent config."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
import tkinter as tk
import unittest

from zefm.editor.shell_command import parse_shell_command, run_shell_command
from zefm.editor.gui.tk_editor import Window


class ShellCommandTests(unittest.TestCase):
    def test_quoted_arguments(self):
        self.assertEqual(parse_shell_command('python3 -c "print(1 + 2)"'),
                         ["python3", "-c", "print(1 + 2)"])

    def test_operators_and_invalid_input_refused(self):
        for command in ("ls | head", "echo hi > out.txt",
                        "echo hi && touch out", "x; y", "",
                        'echo "unterminated'):
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    parse_shell_command(command)

    def test_execute_without_shell(self):
        with TemporaryDirectory() as tmp:
            result = run_shell_command(
                [sys.executable, "-c", "print('cœur שלום')"], Path(tmp))
        self.assertTrue(result["ok"])
        self.assertIn("cœur שלום", result["log"])


class ShellMenuGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.root.update()

    def test_shell_opens_interactive_terminal_in_working_directory(self):
        with patch("zefm.editor.gui.tk_editor.open_terminal") as opened:
            self.app.action("Shell")
        opened.assert_called_once()
        self.assertFalse(self.app._run_busy)

    def test_one_off_command_still_captures_output(self):
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring",
                   return_value='echo "hello world"'), \
             patch("zefm.editor.gui.tk_editor.run_shell_command",
                   return_value={"ok": True, "returncode": 0,
                                 "log": "hello world"}) as run, \
             patch("threading.Thread") as thread:
            thread.return_value.start.side_effect = (
                lambda: thread.call_args.kwargs["target"]())
            self.app.run_shell_once()
            self.assertTrue(self.app._run_busy)
            if self.app._run_poll_id is not None:
                self.root.after_cancel(self.app._run_poll_id)
                self.app._run_poll_id = None
            self.app._poll_run_command()
        self.assertEqual(run.call_args.args[0], ["echo", "hello world"])
        self.assertIn("hello world", self.app.current()[0].get("1.0", "end-1c"))
        self.assertFalse(self.app._run_busy)

    def test_one_off_cancel_does_not_execute(self):
        with patch("zefm.editor.gui.tk_editor.simpledialog.askstring",
                   return_value=None), \
             patch("zefm.editor.gui.tk_editor.run_shell_command") as run:
            self.app.run_shell_once()
        run.assert_not_called()

    def test_original_shell_shortcut(self):
        keys = {c.shortcut: c.label
                for group in self.app.menus.values() for c in group}
        self.assertEqual(keys["Ctrl+Shift+Z"], "Shell")


if __name__ == "__main__":
    unittest.main()
