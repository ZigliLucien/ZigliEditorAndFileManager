"""v113: QuickMail prepares a draft; ZEFM never sends the email."""
import tkinter as tk
import unittest
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from zefm.editor.quickmail import quickmail_url, validate_recipient
from zefm.editor.gui.tk_editor import Window


class QuickMailTests(unittest.TestCase):
    def test_unicode_message_and_subject(self):
        url = quickmail_url("person@example.org", "cœur", "ייִדיש ∫\nnext")
        self.assertTrue(url.startswith("mailto:person@example.org?"))
        parsed = parse_qs(urlsplit(url).query)
        self.assertEqual(parsed["subject"], ["cœur"])
        self.assertEqual(parsed["body"], ["ייִדיש ∫\nnext"])

    def test_invalid_recipients_and_large_bodies(self):
        for recipient in ("", "person", "person\nBCC:secret@example.org",
                          "a@example.org,b@example.org", "a@missing"):
            with self.subTest(recipient=recipient), self.assertRaises(ValueError):
                validate_recipient(recipient)
        with self.assertRaises(ValueError):
            quickmail_url("person@example.org", "Hello", "x" * 12001)
        with self.assertRaises(ValueError):
            quickmail_url("person@example.org", "Header\nInjected", "Body")


class QuickMailGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.root.update()

    def test_quickmail_creates_dialog_without_sending(self):
        widget, _editor = self.app.current()
        widget.insert("1.0", "unsaved mathematical α and ייִדיש")
        before = widget.get("1.0", "end-1c")
        with patch("zefm.editor.gui.tk_editor.webbrowser.open") as opened:
            self.app.action("QuickMail")
        opened.assert_not_called()
        dialogs = [child for child in self.root.winfo_children()
                   if isinstance(child, tk.Toplevel)]
        self.assertTrue(dialogs)
        self.assertIn("QuickMail", dialogs[-1].title())
        self.assertEqual(widget.get("1.0", "end-1c"), before)
        dialogs[-1].destroy()

    def test_original_shortcut(self):
        keys = {cmd.shortcut: cmd.label
                for group in self.app.menus.values() for cmd in group}
        self.assertEqual(keys["Ctrl+M"], "QuickMail")


if __name__ == "__main__":
    unittest.main()
