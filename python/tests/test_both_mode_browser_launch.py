"""Regression for --mode both: boolean open_browser must not shadow launcher."""
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from zefm.editor.gui.tk_editor import Window


class BothModeBrowserLaunchTests(unittest.TestCase):
    def make_window(self):
        directory = Path("/tmp")
        state = SimpleNamespace()
        state.working_directory = SimpleNamespace(
            home=directory,
            initial_directory=lambda: str(directory))
        state.local_browser = None
        state.browser_open_requests = Mock()
        state.browser_saved_requests = Mock()
        state._browser_file_in_use = Mock()
        state.browser_poll_id = 1  # Already scheduled; no Tk interaction.
        state.status = Mock()
        state.root = Mock()
        return state

    def test_browser_opens_in_combined_mode(self):
        window = self.make_window()
        server = Mock()
        server.start.return_value = "http://127.0.0.1:9090/"
        with patch("zefm.server.http.BrowserServer", return_value=server), \
             patch("zefm.server.browser_location.browser_location",
                   return_value=(Path("/tmp"), ".")), \
             patch("zefm.editor.browser_launcher.open_browser") as launch:
            url = Window.open_local_file_manager(
                window, directory=Path("/tmp"), port=9090, open_browser=True)
        self.assertEqual(url, server.start.return_value)
        launch.assert_called_once_with("http://127.0.0.1:9090/listing?path=.")

    def test_no_browser_keeps_server_running(self):
        window = self.make_window()
        server = Mock()
        server.start.return_value = "http://127.0.0.1:9090/"
        with patch("zefm.server.http.BrowserServer", return_value=server), \
             patch("zefm.server.browser_location.browser_location",
                   return_value=(Path("/tmp"), ".")), \
             patch("zefm.editor.browser_launcher.open_browser") as launch:
            url = Window.open_local_file_manager(window, open_browser=False)
        self.assertEqual(url, server.start.return_value)
        launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
