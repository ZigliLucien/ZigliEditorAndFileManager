"""Regression tests: Home and Up must escape the remembered directory."""
import tempfile
import unittest
from pathlib import Path

from zefm.server.browser_location import browser_location
from zefm.server.file_manager import LocalFiles
from zefm.server.listing_paging import paged_listing


class BrowserRootTests(unittest.TestCase):
    def test_recent_directory_is_not_browsing_root(self):
        with tempfile.TemporaryDirectory() as base:
            home = Path(base)
            (home / "Projects" / "ZEFM").mkdir(parents=True)
            root, start = browser_location(home, home / "Projects" / "ZEFM")
            self.assertEqual(root, home)
            self.assertEqual(start, "Projects/ZEFM")
            files = LocalFiles(root)
            deep = paged_listing(files, start)
            self.assertEqual(deep["parent"], "Projects")
            self.assertEqual(deep["breadcrumbs"][0]["path"], ".")
            self.assertEqual(paged_listing(files, deep["parent"])["parent"], ".")

    def test_explicit_root_remains_restricted(self):
        with tempfile.TemporaryDirectory() as base:
            home = Path(base)
            (home / "A" / "B").mkdir(parents=True)
            root, start = browser_location(home, home / "A" / "B", home / "A")
            self.assertEqual(root, home / "A")
            self.assertEqual(start, ".")

    def test_outside_home_no_filesystem_wide_root(self):
        with tempfile.TemporaryDirectory() as base:
            parent = Path(base)
            (parent / "home").mkdir()
            (parent / "other" / "recent").mkdir(parents=True)
            root, start = browser_location(parent / "home", parent / "other" / "recent")
            self.assertEqual(root, parent / "other")
            self.assertEqual(start, "recent")


if __name__ == "__main__":
    unittest.main()
