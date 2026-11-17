"""v111: interactive terminal launch is separate from captured commands."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.terminal_launcher import terminal_argv, open_terminal


class TerminalLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / 'unicode œ "quoted" dir'
        self.folder.mkdir()

    def test_linux_xterm_argv_is_interactive_and_uses_cwd(self):
        argv = terminal_argv(
            self.folder, platform="linux", executable="/usr/bin/xterm")
        self.assertEqual(argv[:2], ["/usr/bin/xterm", "-e"])
        self.assertEqual(argv[-1], "-i")
        with patch("zefm.editor.terminal_launcher.subprocess.Popen") as process:
            open_terminal(self.folder, platform="linux", executable="/usr/bin/xterm")
        process.assert_called_once()
        self.assertEqual(process.call_args.kwargs["cwd"], str(self.folder))
        self.assertTrue(process.call_args.kwargs["start_new_session"])

    def test_macos_applescript_uses_escaped_literal_directory(self):
        argv = terminal_argv(
            self.folder, platform="darwin", executable="/usr/bin/osascript")
        self.assertEqual(argv[0], "/usr/bin/osascript")
        self.assertIn('tell application "Terminal" to do script ', argv[-1])
        self.assertIn(r'\"quoted\"', argv[-1])
        self.assertIn("unicode œ", argv[-1])
        with patch("zefm.editor.terminal_launcher.subprocess.Popen") as process:
            open_terminal(self.folder, platform="darwin")
        self.assertEqual(process.call_args.kwargs["cwd"], str(self.folder))

    def test_missing_xterm_or_directory_reports_error(self):
        with patch("zefm.editor.terminal_launcher.shutil.which",
                   return_value=None):
            with self.assertRaisesRegex(ValueError, "xterm"):
                terminal_argv(self.folder, platform="linux")
        with self.assertRaises(ValueError):
            terminal_argv(self.folder / "missing", platform="linux",
                          executable="/usr/bin/xterm")

    def test_unsupported_platform_rejected(self):
        with self.assertRaises(ValueError):
            terminal_argv(self.folder, platform="win32")


if __name__ == "__main__":
    unittest.main()
