"""v88: F4 LaTeX compilation integration with the existing document builder."""
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import patch

from zefm.editor.gui.tk_editor import Window


class CompileLatexGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tex = Path(self.temp.name) / "math.tex"
        self.tex.write_text(
            r"\\documentclass{article}\\begin{document}Hello\\end{document}",
            encoding="utf-8")
        self.app._open_path(str(self.tex))
        self.root.update()

    def _compile_synchronously(self, result):
        # Run the worker synchronously, but still verify the queue-to-Tk path.
        with patch("zefm.server.document_build.build_pdf", return_value=result) as build, \
             patch("threading.Thread") as thread:
            thread.return_value.start.side_effect = (
                lambda: thread.call_args.kwargs["target"]())
            self.app.action("Compile")
            self.assertTrue(self.app._compile_running)
            if self.app._compile_poll_id is not None:
                self.root.after_cancel(self.app._compile_poll_id)
                self.app._compile_poll_id = None
            self.app._poll_latex_build()
        return build

    def test_f4_registry_and_success(self):
        keys = {cmd.shortcut: cmd.label
                for items in self.app.menus.values() for cmd in items}
        self.assertEqual(keys["F4"], "Compile")
        self.assertTrue(self.root.bind_all("<F4>"))
        pdf = self.tex.parent / ".zefm-build" / "math.tex-test.pdf"
        pdf.parent.mkdir()
        pdf.write_bytes(b"%PDF-1.7\\n")
        with patch("zefm.editor.gui.tk_editor.webbrowser.open") as opened:
            build = self._compile_synchronously(
                {"ok": True, "pdf": ".zefm-build/math.tex-test.pdf",
                 "log": "Compiled successfully", "returncode": 0})
        build.assert_called_once()
        self.assertEqual(build.call_args.args[1], "math.tex")
        opened.assert_called_once_with(pdf.as_uri())
        widget, _ = self.app.current()
        self.assertIn("Compiled successfully", widget.get("1.0", "end-1c"))
        self.assertFalse(self.app._compile_running)

    def test_failure_shows_log_without_opening_stale_pdf(self):
        with patch("zefm.editor.gui.tk_editor.webbrowser.open") as opened:
            self._compile_synchronously(
                {"ok": False, "log": "! Undefined control sequence",
                 "returncode": 1})
        opened.assert_not_called()
        widget, _ = self.app.current()
        self.assertIn("Undefined control sequence", widget.get("1.0", "end-1c"))

    def test_unsaved_buffer_is_not_compiled(self):
        widget, _ = self.app.current()
        widget.insert("end", "new unsaved text")
        self.root.update()
        with patch("zefm.server.document_build.build_pdf") as build, \
             patch("zefm.editor.gui.tk_editor.messagebox.showwarning"):
            self.app.action("Compile")
        build.assert_not_called()
        self.assertFalse(self.app._compile_running)


if __name__ == "__main__":
    unittest.main()
