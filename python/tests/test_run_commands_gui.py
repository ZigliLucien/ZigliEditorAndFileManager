"""v97: Tk Run menu, saved-buffer checks and output-tab delivery."""
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import patch

from zefm.editor.gui.tk_editor import Window


class ConfiguredRunGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        with patch("zefm.editor.gui.tk_editor.RunCommands") as config:
            self.app = Window(self.root)
        # Use an independent nonpersistent run-config mock per test.
        self.app.run_commands = config.return_value
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "example.py"
        self.source.write_text("print('hi')\n", encoding="utf-8")
        self.app._open_path(str(self.source))
        self.root.update()
        self.app.run_commands.get.return_value = ["python3", "{file}"]

    def test_saved_python_file_runs_and_output_is_shown(self):
        with patch("zefm.editor.gui.tk_editor.execute_command",
                   return_value={"ok": True, "returncode": 0,
                                 "log": "hello\n"}) as runner, \
             patch("threading.Thread") as thread:
            thread.return_value.start.side_effect = (
                lambda: thread.call_args.kwargs["target"]())
            self.app.run_configured_command()
            self.assertTrue(self.app._run_busy)
            if self.app._run_poll_id is not None:
                self.root.after_cancel(self.app._run_poll_id)
                self.app._run_poll_id = None
            self.app._poll_run_command()
        runner.assert_called_once_with(["python3", "{file}"], self.source.resolve())
        widget, _ = self.app.current()
        self.assertIn("hello", widget.get("1.0", "end-1c"))
        self.assertFalse(self.app._run_busy)

    def test_dirty_source_not_executed(self):
        widget, _ = self.app.current()
        widget.insert("end", "unsaved")
        self.root.update()
        with patch("zefm.editor.gui.tk_editor.execute_command") as runner, \
             patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning:
            self.app.run_configured_command()
        runner.assert_not_called()
        warning.assert_called_once()

    def test_no_configured_command_is_nonexecuting(self):
        self.app.run_commands.get.return_value = None
        with patch("zefm.editor.gui.tk_editor.execute_command") as runner, \
             patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as info:
            self.app.run_configured_command()
        runner.assert_not_called()
        info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
