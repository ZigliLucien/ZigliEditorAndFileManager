"""Optional Tk launch test. Skips when no graphical display is available."""
from email.message import EmailMessage
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import patch
from urllib.request import urlopen

from zefm.editor.gui.tk_editor import Window


class MailMenuGuiTests(unittest.TestCase):
    def test_mail_archive_menu_opens_loopback_and_closes(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No Tk display")
        app = None
        try:
            with TemporaryDirectory() as directory:
                maildir = Path(directory) / "Maildir"
                (maildir / "new").mkdir(parents=True)
                (maildir / "cur").mkdir()
                msg = EmailMessage()
                msg["Subject"] = "Bonjour ייִדיש"
                msg.set_content("Hello")
                (maildir / "new" / "one-message").write_bytes(msg.as_bytes())
                app = Window(root)
                with patch("zefm.server.mail_archive.discover_maildirs",
                           return_value={"Test": str(maildir)}):
                    with patch("zefm.editor.gui.tk_editor.webbrowser.open"):
                        app.open_local_email_archive()
                self.assertIsNotNone(app.mail_browser)
                self.assertIn("Local Maildir browser", app.status.get())
                with urlopen(app.mail_browser.url, timeout=4) as response:
                    self.assertIn(b"Test", response.read())
        finally:
            if app is not None:
                app.quit()
            else:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
