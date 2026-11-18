"""v126: browser actions must not rely on Emacs/default file associations."""
import unittest
from unittest.mock import patch

from zefm.editor.browser_launcher import BROWSERS, browser_command, open_browser


class BrowserLauncherTests(unittest.TestCase):
    def test_linux_ignores_emacs_browser_environment(self):
        available = {"firefox": "/usr/bin/firefox", "emacs": "/usr/bin/emacs"}
        argv = browser_command("http://127.0.0.1:8765/listing",
                               platform="linux",
                               which=available.get,
                               environ={"BROWSER": "emacs"})
        self.assertEqual(argv, ["/usr/bin/firefox",
                                "http://127.0.0.1:8765/listing"])

    def test_next_available_browser(self):
        argv = browser_command("file:///tmp/a%20b.pdf",
                               platform="linux",
                               which={"qutebrowser": "/usr/bin/qutebrowser"}.get,
                               environ={})
        self.assertEqual(argv, ["/usr/bin/qutebrowser",
                                "file:///tmp/a%20b.pdf"])

    def test_missing_browser_explains_how_to_select(self):
        with self.assertRaisesRegex(ValueError, "ZEFM_BROWSER"):
            browser_command("http://127.0.0.1/",
                            platform="linux", which={}.get, environ={})

    def test_override_is_executable_only(self):
        argv = browser_command("https://example.org",
                               platform="linux",
                               which={"firefox": "/bin/firefox"}.get,
                               environ={"ZEFM_BROWSER": "firefox"})
        self.assertEqual(argv, ["/bin/firefox", "https://example.org"])
        with self.assertRaises(ValueError):
            browser_command("https://example.org", platform="linux",
                            which={}.get,
                            environ={"ZEFM_BROWSER": "emacs --eval '(x)'"})

    def test_mac_uses_safari_not_file_association(self):
        argv = browser_command("file:///tmp/test.html",
                               platform="darwin", which={"open": "/usr/bin/open"}.get,
                               environ={"BROWSER": "emacs"})
        self.assertEqual(argv, ["/usr/bin/open", "-a", "Safari",
                                "file:///tmp/test.html"])

    def test_reject_unexpected_schemes(self):
        for url in ("javascript:alert(1)", "mailto:test@example.org", "abc"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                browser_command(url, platform="linux", which={}.get)

    def test_start_is_argv_without_shell(self):
        with patch("zefm.editor.browser_launcher.browser_command",
                   return_value=["/usr/bin/firefox", "http://localhost/"]), \
             patch("zefm.editor.browser_launcher.subprocess.Popen") as spawn:
            self.assertTrue(open_browser("http://localhost/"))
        self.assertEqual(spawn.call_args.args[0],
                         ["/usr/bin/firefox", "http://localhost/"])
        self.assertNotIn("shell", spawn.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
