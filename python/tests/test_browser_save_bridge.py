"""Browser Quick Edit → desktop notification bridge, with no implicit reload.

HTTP workers can enqueue a save signal; only Tk's main thread handles it.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from unittest import mock
import tkinter as tk
import unittest

from zefm.server.http import BrowserServer
from zefm.editor.gui.tk_editor import Window


class BrowserSaveCallbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / "cœur ייִדיש.txt"
        self.file.write_text("original", encoding="utf-8")

    def request(self, server, path, args):
        req = Request(
            server.url.rstrip("/") + path,
            data=urlencode(args).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status
        except HTTPError as exc:
            return exc.code

    def test_successful_save_signals_exact_path(self):
        callbacks = []
        server = BrowserServer(self.root, file_saved=callbacks.append)
        server.start()
        self.addCleanup(server.close)
        content, digest = server.files.read_text(self.file.name)
        args = {"csrf": server.token, "path": self.file.name,
                "digest": digest, "content": "new saved content"}
        self.assertEqual(self.request(server, "/edit", args), 200)
        self.assertEqual(self.file.read_text(encoding="utf-8"), "new saved content")
        self.assertEqual(callbacks, [str(self.file)])
        self.assertEqual(self.request(server, "/edit", args), 409)
        self.assertEqual(callbacks, [str(self.file)])
        self.assertEqual(self.request(server, "/edit", {**args, "csrf": "invalid"}), 403)
        self.assertEqual(callbacks, [str(self.file)])

    def test_save_response_does_not_fail_when_notification_fails(self):
        def failing_callback(path):
            raise RuntimeError("UI no longer available")
        server = BrowserServer(self.root, file_saved=failing_callback)
        server.start()
        self.addCleanup(server.close)
        content, digest = server.files.read_text(self.file.name)
        args = {"csrf": server.token, "path": self.file.name,
                "digest": digest, "content": "committed"}
        self.assertEqual(self.request(server, "/edit", args), 200)
        self.assertEqual(self.file.read_text(encoding="utf-8"), "committed")


class BrowserSaveTkTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ייִדיש.txt"
        self.path.write_text("original", encoding="utf-8")
        self.app._open_path(str(self.path))
        self.root.update()
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open"):
            self.app.open_local_file_manager(directory=self.temp.name, open_browser=False)
        self.server = self.app.local_browser
        self.addCleanup(self.server.close)

    def browser_save(self, new_text):
        _old, digest = self.server.files.read_text(self.path.name)
        req = Request(self.server.url.rstrip("/") + "/edit",
                      data=urlencode({"csrf": self.server.token,
                                      "path": self.path.name, "digest": digest,
                                      "content": new_text}).encode("utf-8"),
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)

    def test_prompt_notice_without_replacing_saved_buffer(self):
        widget, editor = self.app.current()
        self.browser_save("saved through browser")
        self.assertEqual(widget.get("1.0", "end-1c"), "original")
        self.assertFalse(self.app.external_notice.winfo_manager())
        self.app._drain_browser_requests()
        self.root.update()
        self.assertIn("changed on disk", self.app.external_notice_text.get())
        self.assertEqual(self.app.external_notice.winfo_manager(), "pack")
        self.assertEqual(widget.get("1.0", "end-1c"), "original")
        self.assertFalse(editor.state.buffer.modified)

    def test_inactive_tab_marked_until_selected_and_reloaded(self):
        other = Path(self.temp.name) / "other.txt"
        other.write_text("unrelated file", encoding="utf-8")
        self.app._open_path(str(other))
        self.root.update()
        inactive = next(tab for tab, (_widget, editor) in self.app.views.items()
                        if editor.state.buffer.path == str(self.path))
        self.browser_save("changed while inactive")
        self.app._drain_browser_requests()
        self.root.update()
        self.assertIn(inactive, self.app.external_changed_tabs)
        self.assertTrue(self.app.tabs.tab(inactive, "text").startswith("↻ "))
        self.assertFalse(self.app.external_notice.winfo_manager())

        self.app.tabs.select(inactive)
        self.root.update()
        self.assertEqual(self.app.external_notice.winfo_manager(), "pack")
        widget, editor = self.app.current()
        self.assertEqual(widget.get("1.0", "end-1c"), "original")
        self.assertFalse(editor.state.buffer.modified)
        self.app._reload_external()
        self.root.update()
        self.assertEqual(widget.get("1.0", "end-1c"), "changed while inactive")
        self.assertNotIn(inactive, self.app.external_changed_tabs)
        self.assertNotIn("↻", self.app.tabs.tab(inactive, "text"))

    def test_inactive_unsaved_buffer_preserves_both_indicators_and_text(self):
        widget, editor = self.app.current()
        active_tab = self.app.tabs.select()
        widget.insert("end", " private unsaved text")
        self.root.update()
        other = Path(self.temp.name) / "other.txt"
        other.write_text("other", encoding="utf-8")
        self.app._open_path(str(other))
        self.root.update()

        self.browser_save("different disk contents")
        self.app._drain_browser_requests()
        self.root.update()
        self.assertTrue(self.app.tabs.tab(active_tab, "text").startswith("* ↻ "))
        self.assertTrue(editor.state.buffer.modified)
        self.assertFalse(self.app.external_notice.winfo_manager())

        self.app.tabs.select(active_tab)
        self.root.update()
        self.assertIn("changed on disk", self.app.external_notice_text.get())
        self.assertEqual(widget.get("1.0", "end-1c"), "original private unsaved text")
        self.assertEqual(self.path.read_text(encoding="utf-8"), "different disk contents")
        self.app._dismiss_external()
        self.assertNotIn("↻", self.app.tabs.tab(active_tab, "text"))
        self.assertTrue(self.app.tabs.tab(active_tab, "text").startswith("* "))
        self.assertIn("private unsaved text", widget.get("1.0", "end-1c"))

    def test_unchanged_content_does_not_mark_inactive_buffer(self):
        other = Path(self.temp.name) / "other.txt"
        other.write_text("other", encoding="utf-8")
        self.app._open_path(str(other))
        self.root.update()
        tab = next(tab for tab, (_widget, editor) in self.app.views.items()
                   if editor.state.buffer.path == str(self.path))
        self.browser_save("original")
        self.app._drain_browser_requests()
        self.root.update()
        self.assertNotIn(tab, self.app.external_changed_tabs)
        self.assertNotIn("↻", self.app.tabs.tab(tab, "text"))

    def test_unsaved_editor_text_survives_browser_save(self):
        widget, editor = self.app.current()
        widget.insert("end", " unsaved in editor")
        self.root.update()
        self.browser_save("new disk version")
        self.app._drain_browser_requests()
        self.root.update()
        self.assertIn("changed on disk", self.app.external_notice_text.get())
        self.assertIn("unsaved in editor", widget.get("1.0", "end-1c"))
        self.assertTrue(editor.state.buffer.modified)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "new disk version")


if __name__ == "__main__":
    unittest.main()
