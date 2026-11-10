"""Desktop-to-browser Quick Editor: source-guided XCommands.runQ adaptation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
import tkinter as tk
import unittest

from zefm.editor.gui.tk_editor import Window


class DesktopQuickEditGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.addCleanup(lambda: self.app.local_browser.close()
                        if self.app.local_browser is not None else None)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        (self.directory / "Nested").mkdir()
        self.path = self.directory / "Nested" / "cœur ייִדיש.txt"
        self.path.write_text("bonjour שלום", encoding="utf-8")
        self.app._open_path(str(self.path))
        self.root.update()

    def browser_url(self, direction="ltr"):
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as browser:
            self.app.edit_current_file_in_browser(direction)
        browser.assert_called_once()
        return browser.call_args.args[0]

    def test_ltr_edit_opens_correct_unicode_file_and_live_form(self):
        url = self.browser_url()
        parts = urlsplit(url)
        params = parse_qs(parts.query)
        self.assertEqual(parts.hostname, "127.0.0.1")
        self.assertEqual(parts.path, "/edit")
        self.assertEqual(params["dir"], ["ltr"])
        self.assertEqual(params["path"], ["cœur ייִדיש.txt"])
        with urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8")
        self.assertIn("bonjour שלום", body)
        self.assertIn('action="/edit"', body)
        self.assertIn("Browser Quick Edit opened", self.app.status.get())

    def test_browser_save_roundtrip_triggers_tk_change_notice(self):
        widget, editor = self.app.current()
        url = self.browser_url()
        params = parse_qs(urlsplit(url).query)
        relative = params["path"][0]
        previous, digest = self.app.local_browser.files.read_text(relative)
        self.assertEqual(previous, "bonjour שלום")
        data = urlencode({
            "csrf": self.app.local_browser.token,
            "path": relative, "digest": digest,
            "content": "edited via runQ browser bridge"
        }).encode("utf-8")
        request = Request(
            self.app.local_browser.url + "edit",
            data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, 200)
        self.app._drain_browser_requests()
        self.root.update()
        self.assertEqual(self.path.read_text(encoding="utf-8"),
                         "edited via runQ browser bridge")
        self.assertEqual(widget.get("1.0", "end-1c"), "bonjour שלום")
        self.assertIn("changed on disk", self.app.external_notice_text.get())
        self.assertFalse(editor.state.buffer.modified)

    def test_existing_browser_root_reused_and_nested_relative_path(self):
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open"):
            self.app.open_local_file_manager(directory=self.directory, open_browser=False)
        original_server = self.app.local_browser
        url = self.browser_url()
        self.assertIs(self.app.local_browser, original_server)
        self.assertEqual(parse_qs(urlsplit(url).query)["path"],
                         ["Nested/cœur ייִדיש.txt"])

    def test_rtl_action_uses_same_bridge(self):
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as browser:
            self.app.edit_current_file_rtl()
        browser.assert_called_once()
        params = parse_qs(urlsplit(browser.call_args.args[0]).query)
        self.assertEqual(params["dir"], ["rtl"])
        self.assertEqual(params["path"], ["cœur ייִדיש.txt"])

    def test_unsaved_buffer_does_not_open_second_editor(self):
        widget, _editor = self.app.current()
        widget.insert("end", " unsaved")
        self.root.update()
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as browser, \
             mock.patch("zefm.editor.gui.tk_editor.messagebox.showwarning") as warning:
            self.app.edit_current_file_in_browser()
        browser.assert_not_called()
        warning.assert_called_once()
        self.assertIn(" unsaved", widget.get("1.0", "end-1c"))
        self.assertEqual(self.path.read_text(encoding="utf-8"), "bonjour שלום")

    def test_untitled_buffer_must_be_saved_first(self):
        self.app.new_buffer()
        self.root.update()
        with mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as browser, \
             mock.patch("zefm.editor.gui.tk_editor.messagebox.showinfo") as info:
            self.app.edit_current_file_in_browser()
        browser.assert_not_called()
        info.assert_called_once()

    def test_non_utf8_and_oversized_content_rejected(self):
        for payload in (b"\xff\xfe\x00", b"x" * (1024 * 1024 + 1)):
            self.path.write_bytes(payload)
            with self.subTest(size=len(payload)), \
                 mock.patch("zefm.editor.gui.tk_editor.webbrowser.open") as browser, \
                 mock.patch("zefm.editor.gui.tk_editor.messagebox.showerror") as error:
                self.app.edit_current_file_in_browser()
                browser.assert_not_called()
                error.assert_called_once()
        self.assertIsNone(self.app.local_browser)

    def test_file_menu_exposes_quick_edit(self):
        menu = self.root.nametowidget(self.root["menu"])
        # Tk may add a tear-off entry at index zero; find the File cascade
        # by label, not a platform-dependent menu index.
        file_index = next(i for i in range(menu.index("end") + 1)
                          if menu.type(i) == "cascade"
                          and menu.entrycget(i, "label") == "File")
        file_menu = self.root.nametowidget(menu.entrycget(file_index, "menu"))
        labels = [file_menu.entrycget(i, "label")
                  for i in range(file_menu.index("end") + 1)
                  if file_menu.type(i) == "command"]
        self.assertIn("Quick Edit Current File in Browser...", labels)
        self.assertIn("Edit Current File RTL in Browser...", labels)


if __name__ == "__main__":
    unittest.main()
