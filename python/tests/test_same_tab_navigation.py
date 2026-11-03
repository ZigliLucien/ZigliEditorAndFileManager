"""Regression: ordinary ZEFM file clicks stay in the same browser tab."""
from pathlib import Path
import unittest

from zefm.server.listing_view import listing_shell


class SameTabNavigationTests(unittest.TestCase):
    def test_listing_js_does_not_open_new_tabs(self):
        script = (Path(__file__).resolve().parents[1] /
                  "zefm" / "server" / "listing.js").read_text(encoding="utf-8")
        # View includes HTML, PDF, PS/EPS, image, archive and books via /view.
        self.assertIn('location.assign(operationUrl(row.type === "pdf" ? "/pdf" : "/view", path))', script)
        self.assertIn('location.assign(operationUrl("/build", path))', script)
        self.assertNotIn('window.open(operationUrl(', script)

    def test_browser_shell_keeps_breadcrumbs(self):
        shell = listing_shell("localhost", "token", False).decode("utf-8")
        self.assertIn('id="breadcrumbs"', shell)
        self.assertIn('id="folder-home"', shell)
        self.assertIn('id="folder-up"', shell)


if __name__ == "__main__":
    unittest.main()
