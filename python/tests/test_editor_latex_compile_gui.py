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

    def test_saved_buffer_with_delayed_modified_notification_compiles(self):
        # Tk may deliver <<Modified>> after F1 has already finished writing.
        widget, editor = self.app.current()
        widget.insert("end", " updated")
        self.root.update()
        self.app.save_file()
        self.root.update()
        self.assertFalse(editor.state.buffer.modified)
        widget.edit_modified(True)
        self.root.update()
        self.assertFalse(editor.state.buffer.modified)
        self.assertEqual(
            self.app.saved_snapshots[self.app.tabs.select()],
            widget.get("1.0", "end-1c"))
        pdf = self.tex.parent / ".zefm-build" / "math.tex-test.pdf"
        pdf.parent.mkdir(exist_ok=True)
        pdf.write_bytes(b"%PDF-1.7\\n")
        with patch("zefm.editor.gui.tk_editor.webbrowser.open"):
            build = self._compile_synchronously(
                {"ok": True, "pdf": ".zefm-build/math.tex-test.pdf",
                 "log": "ok", "returncode": 0})
        build.assert_called_once()

    def test_mac_compile_alternative_shortcut_is_registered(self):
        import sys
        if sys.platform != "darwin":
            self.skipTest("macOS shortcut requires a native Tk Aqua session")
        self.assertTrue(self.root.bind_all("<Command-Shift-B>"))
        self.assertTrue(self.root.bind_all("<F4>"))

    def test_magic_comment_compiles_project_master_not_section(self):
        root_source = Path(self.temp.name) / "main.tex"
        root_source.write_text("main", encoding="utf-8")
        self.app.current()[0].insert(
            "1.0", "% !TEX root = main.tex\n")
        self.root.update()
        self.app.save_file()
        self.root.update()
        pdf = Path(self.temp.name) / ".zefm-build" / "main-preview.pdf"
        pdf.parent.mkdir(exist_ok=True)
        pdf.write_bytes(b"%PDF-1.7\\n")
        with patch("zefm.editor.gui.tk_editor.webbrowser.open"):
            build = self._compile_synchronously(
                {"ok": True, "pdf": ".zefm-build/main-preview.pdf",
                 "output_pdf": "main.pdf", "log": "ok", "returncode": 0})
        self.assertEqual(build.call_args.args[1], "main.tex")
        self.assertTrue(build.call_args.kwargs["publish_adjacent"])

    def test_explicit_master_overrides_directive(self):
        alternate = Path(self.temp.name) / "alternate.tex"
        alternate.write_text("alternate", encoding="utf-8")
        self.app.latex_masters[self.app.tabs.select()] = alternate
        pdf = Path(self.temp.name) / ".zefm-build" / "alternate-preview.pdf"
        pdf.parent.mkdir(exist_ok=True)
        pdf.write_bytes(b"%PDF-1.7\\n")
        with patch("zefm.editor.gui.tk_editor.webbrowser.open"):
            build = self._compile_synchronously(
                {"ok": True, "pdf": ".zefm-build/alternate-preview.pdf",
                 "log": "ok", "returncode": 0})
        self.assertEqual(build.call_args.args[1], "alternate.tex")

    def test_dirty_open_master_is_not_compiled(self):
        master = Path(self.temp.name) / "main.tex"
        master.write_text("main", encoding="utf-8")
        self.app.latex_masters[self.app.tabs.select()] = master
        section_tab = self.app.tabs.select()
        self.app._open_path(master)
        self.app.current()[0].insert("end", " unsaved")
        self.root.update()
        self.app.tabs.select(section_tab)
        self.root.update()
        with patch("zefm.server.document_build.build_pdf") as build, \
             patch("zefm.editor.gui.tk_editor.messagebox.showerror") as error:
            self.app.action("Compile")
        build.assert_not_called()
        error.assert_called_once()
        self.assertIn("Save the LaTeX master", error.call_args.args[1])

    def test_log_error_opens_source_line_without_changing_text(self):
        source_widget, _ = self.app.current()
        source_widget.delete("1.0", "end")
        source_widget.insert("1.0", "\n".join(["source"] * 25))
        self.root.update()
        self.app.save_file()
        self.root.update()
        source_tab = self.app.tabs.select()
        original = self.app.current()[0].get("1.0", "end-1c")
        log = "(./math.tex\n! Undefined control sequence.\nl.12 \\broken\n"
        log_widget = self.app._show_latex_log(
            self.tex, {"ok": False, "log": log})
        log_tab = self.app.tabs.select()
        self.assertIn(log_tab, self.app.latex_error_lists)
        self.assertEqual(len(self.app.latex_error_lists[log_tab][0]), 1)
        self.assertTrue(log_widget.tag_ranges("latex_error"))
        self.app.next_latex_error()
        self.assertEqual(self.app.tabs.select(), source_tab)
        self.assertEqual(self.app.current()[0].index("insert"), "12.0")
        self.assertEqual(self.app.current()[0].get("1.0", "end-1c"), original)

    def test_log_error_rejects_source_outside_project(self):
        other = Path(self.temp.name).parent / "outside.tex"
        from zefm.editor.latex_diagnostics import LatexDiagnostic
        diag = LatexDiagnostic(other, 2, "error", 1)
        with patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning:
            self.app.open_latex_error(diag, self.tex)
        warning.assert_called_once()

    def test_selected_engine_is_forwarded_to_builder(self):
        self.app.latex_engine_preference.engine = "xelatex"
        pdf = self.tex.parent / ".zefm-build" / "math-engine-test.pdf"
        pdf.parent.mkdir(exist_ok=True)
        pdf.write_bytes(b"%PDF-1.7\\n")
        with patch("zefm.editor.gui.tk_editor.webbrowser.open"):
            build = self._compile_synchronously(
                {"ok": True, "pdf": ".zefm-build/math-engine-test.pdf",
                 "log": "ok", "returncode": 0})
        self.assertEqual(build.call_args.kwargs["latex_engine"], "xelatex")
        self.assertTrue(build.call_args.kwargs["publish_adjacent"])

    def test_forward_synctex_opens_matching_pdf_page(self):
        preview = self.tex.parent / ".zefm-build" / "math-unique.pdf"
        preview.parent.mkdir(exist_ok=True)
        preview.write_bytes(b"%PDF-1.7\nnew")
        self.app.latest_synctex_pdfs[self.tex.resolve()] = preview
        with patch("zefm.editor.gui.tk_editor.synctex_page",
                   return_value=3) as locate, \
             patch("zefm.editor.gui.tk_editor.webbrowser.open") as opened, \
             patch("threading.Thread") as thread:
            thread.return_value.start.side_effect = (
                lambda: thread.call_args.kwargs["target"]())
            self.app.forward_synctex()
            if self.app._synctex_poll_id is not None:
                self.root.after_cancel(self.app._synctex_poll_id)
                self.app._synctex_poll_id = None
            self.app._poll_synctex()
        self.assertEqual(locate.call_args.args[0], self.tex.resolve())
        opened.assert_called_once_with(preview.as_uri() + "#page=3")

    def test_forward_synctex_requires_fresh_compile(self):
        with patch("zefm.editor.gui.tk_editor.synctex_page") as locate, \
             patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as info:
            self.app.forward_synctex()
        locate.assert_not_called()
        info.assert_called_once()

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
