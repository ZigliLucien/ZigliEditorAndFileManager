"""Standalone --mode files navigation and Tk wheel-selection regression tests."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlencode
from urllib.request import urlopen
import unittest

from zefm.__main__ import launch_files
from zefm.server.http import BrowserServer
from zefm.editor.gui.file_chooser import next_row, wheel_steps


class FileChooserWheelNavigationTests(unittest.TestCase):
    def test_select_next_previous_and_bounds(self):
        values = ["a", "b", "c", "d"]
        self.assertEqual(next_row(values, "b", 1), "c")
        self.assertEqual(next_row(values, "c", -2), "a")
        self.assertEqual(next_row(values, "d", 3), "d")
        self.assertEqual(next_row(values, "a", -5), "a")
        self.assertEqual(next_row(values, None, 1), "b")
        self.assertIsNone(next_row([], None, 1))

    def test_x11_mouse_scroll_deltas(self):
        rows = list(range(75))
        item = rows[25]
        for event in [SimpleNamespace(num=5), SimpleNamespace(num=5),
                      SimpleNamespace(num=4), SimpleNamespace(delta=-120)]:
            item = next_row(rows, item, wheel_steps(event))
        self.assertEqual(item, 27)


class StandaloneFilesNavigationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        nested = self.root / "Sub" / "Deeper"
        nested.mkdir(parents=True)
        for i in range(62):
            (self.root / ("sample-%03d.txt" % i)).write_text("test", encoding="utf-8")
        (nested / "cœur ייִדיש.md").write_text("# Unicode", encoding="utf-8")
        self.browser = BrowserServer(str(self.root))
        self.browser.start()
        self.addCleanup(self.browser.close)

    def get(self, route):
        with urlopen(self.browser.url.rstrip("/") + route, timeout=5) as r:
            return r.read().decode("utf-8"), dict(r.headers)

    def page(self, **params):
        data, _ = self.get("/api/listing-page?" + urlencode(params))
        return json.loads(data)

    def test_files_only_shell_has_no_editor_and_has_navigation_controls(self):
        html, _ = self.get("/listing")
        self.assertIn('data-editor="false"', html)
        self.assertIn('id="folder-up"', html)
        self.assertIn('id="folder-home"', html)
        script, _ = self.get("/listing.js")
        self.assertIn('function navigateParent()', script)
        self.assertIn('state.data.parent', script)
        self.assertIn('function selectPage(', script)
        self.assertIn('window.addEventListener("popstate"', script)
        self.assertEqual(script.count('window.scrollTo({top: 0'), 1)

    def test_pages_and_nested_breadcrumbs(self):
        one = self.page(path=".", page=1, sort="filename")
        self.assertEqual(one["page_count"], 3)
        self.assertEqual(one["page"], 1)
        self.assertEqual(one["parent"], None)
        self.assertEqual(one["page_end"], 25)
        middle = self.page(path=".", page=2, sort="filename")
        self.assertEqual(middle["page"], 2)
        self.assertEqual(middle["page_start"], 26)
        last = self.page(path=".", page=3, sort="filename")
        self.assertEqual(last["page_end"], 62)
        clamped = self.page(path=".", page=900, sort="filename")
        self.assertEqual(clamped["page"], 3)
        nested = self.page(path="Sub/Deeper", page=1)
        self.assertEqual(nested["parent"], "Sub")
        self.assertEqual([c["path"] for c in nested["breadcrumbs"]],
                         [".", "Sub", "Sub/Deeper"])
        self.assertEqual(nested["files"][0]["name"], "cœur ייִדיש.md")

    def test_standalone_launcher_without_browser_window(self):
        # Mock the browser server rather than threading.Event, because the
        # latter is shared by HTTP worker initialization.
        from unittest.mock import Mock
        fake_server = Mock()
        fake_server.start.return_value = "http://127.0.0.1:9876/"
        with patch("zefm.server.http.BrowserServer", return_value=fake_server), \
             patch("zefm.__main__.threading.Event") as event, \
             patch("zefm.__main__.webbrowser.open") as open_browser:
            event.return_value.wait.side_effect = KeyboardInterrupt()
            launch_files(root=self.root, open_browser=False)
        open_browser.assert_not_called()
        fake_server.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
