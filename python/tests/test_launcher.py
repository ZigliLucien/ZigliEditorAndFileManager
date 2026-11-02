"""v59: unified launcher mode selection and shared browser lifecycle."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest

from zefm.__main__ import build_parser, launch_files, launch_editor, main


class LauncherTests(unittest.TestCase):
    def test_default_and_explicit_modes(self):
        self.assertEqual(build_parser().parse_args([]).mode, "editor")
        self.assertEqual(build_parser().parse_args(["-m", "files"]).mode, "files")
        self.assertEqual(build_parser().parse_args(["--mode", "both"]).mode, "both")
        with self.assertRaises(SystemExit):
            build_parser().parse_args(["--mode", "invalid"])

    def test_main_editor_only(self):
        with patch("zefm.__main__.launch_editor") as editor, \
             patch("zefm.__main__.launch_files") as files:
            main([])
        editor.assert_called_once_with()
        files.assert_not_called()

    def test_main_files_with_root_port_and_browser_suppressed(self):
        with patch("zefm.__main__.launch_editor") as editor, \
             patch("zefm.__main__.launch_files") as files:
            main(["--mode", "files", "--root", "/tmp/data",
                  "--port", "8123", "--no-browser"])
        files.assert_called_once_with(
            root=Path("/tmp/data"), port=8123, open_browser=False)
        editor.assert_not_called()

    def test_main_combined_mode(self):
        with patch("zefm.__main__.launch_editor") as editor:
            main(["-m", "both", "--root", "/tmp/myfiles", "--port", "8123"])
        editor.assert_called_once_with(root=Path("/tmp/myfiles"), port=8123,
                                       with_files=True, open_browser=True)

    def test_invalid_options_rejected(self):
        for args in (["--port", "-1", "--mode", "files"],
                     ["--port", "65536", "--mode", "files"],
                     ["--mode", "editor", "--root", "/tmp"],
                     ["--mode", "editor", "--no-browser"]):
            with self.subTest(args=args), self.assertRaises(SystemExit):
                main(args)

    def test_standalone_browser_starts_and_closes(self):
        fake = Mock()
        fake.start.return_value = "http://127.0.0.1:9001/"
        with patch("zefm.server.http.BrowserServer", return_value=fake) as constructor, \
             patch("zefm.__main__.webbrowser.open") as open_url, \
             patch("zefm.__main__.threading.Event") as event:
            event.return_value.wait.side_effect = KeyboardInterrupt()
            launch_files(root=Path("/tmp/files"), port=9001)
        constructor.assert_called_once_with("/tmp/files", port=9001)
        open_url.assert_called_once_with("http://127.0.0.1:9001/listing")
        fake.close.assert_called_once()

    def test_files_no_browser(self):
        fake = Mock()
        fake.start.return_value = "http://127.0.0.1:9002/"
        with patch("zefm.server.http.BrowserServer", return_value=fake), \
             patch("zefm.__main__.webbrowser.open") as open_url, \
             patch("zefm.__main__.threading.Event") as event:
            event.return_value.wait.side_effect = KeyboardInterrupt()
            launch_files(open_browser=False)
        open_url.assert_not_called()
        fake.close.assert_called_once()

    def test_combined_uses_tk_window_and_shared_manager(self):
        window = Mock()
        with patch("zefm.editor.gui.tk_editor.Window", return_value=window):
            launch_editor(root=Path("/tmp/documents"), port=9876, with_files=True,
                          open_browser=False)
        window.root.protocol.assert_called_once_with("WM_DELETE_WINDOW", window.quit)
        window.open_local_file_manager.assert_called_once_with(
            directory=Path("/tmp/documents"), port=9876, open_browser=False)
        window.root.mainloop.assert_called_once()

    def test_editor_only_does_not_start_browser(self):
        window = Mock()
        with patch("zefm.editor.gui.tk_editor.Window", return_value=window):
            launch_editor()
        window.open_local_file_manager.assert_not_called()
        window.root.mainloop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
