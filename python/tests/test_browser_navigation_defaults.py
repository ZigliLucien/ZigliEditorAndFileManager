"""Navigation and default time-order regression tests."""
import tempfile
import time
import unittest
from pathlib import Path

from zefm.server.file_manager import LocalFiles
from zefm.server.listing_paging import paged_listing
from zefm.server.listing_view import listing_shell


class BrowserNavigationTests(unittest.TestCase):
    def test_navigation_controls_are_links(self):
        html = listing_shell("localhost", "token", False).decode("utf-8")
        self.assertIn('id="folder-home" href="/listing?path=."', html)
        self.assertIn('id="folder-up" href="/listing?path=."', html)

    def test_nested_breadcrumbs_and_parent(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            (root / "A" / "B").mkdir(parents=True)
            data = paged_listing(LocalFiles(root), "A/B")
            self.assertEqual(data["parent"], "A")
            self.assertEqual(data["relative"], "A/B")
            self.assertEqual([c["path"] for c in data["breadcrumbs"]],
                             [".", "A", "A/B"])

    def test_date_time_sort_is_default_newest_first(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            older = root / "older.txt"
            newer = root / "newer.txt"
            older.write_text("older")
            newer.write_text("newer")
            import os
            os.utime(older, (1000000000, 1000000000))
            os.utime(newer, (1100000000, 1100000000))
            data = paged_listing(LocalFiles(root))
            self.assertEqual(data["sort"], "timekey")
            self.assertEqual([x["name"] for x in data["files"]],
                             ["newer.txt", "older.txt"])


if __name__ == "__main__":
    unittest.main()
