"""Browser listing date-order selection, native navigation and return links."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import urlopen
import os
import unittest

from zefm.server.file_manager import LocalFiles
from zefm.server.listing_paging import paged_listing
from zefm.server.listing_view import listing_shell
from zefm.server.navigation import safe_listing_return
from zefm.server.http import BrowserServer


class DateOrderTests(unittest.TestCase):
    def test_newest_default_and_explicit_oldest_sort(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for name, stamp in (("a.txt", 1000000000), ("b.txt", 1200000000),
                                ("c.txt", 1100000000)):
                target = root / name
                target.write_text(name)
                os.utime(target, (stamp, stamp))
            files = LocalFiles(root)
            newest = paged_listing(files)
            oldest = paged_listing(files, sort="timeold")
            self.assertEqual(newest["sort"], "timekey")
            self.assertEqual([x["name"] for x in newest["files"]],
                             ["b.txt", "c.txt", "a.txt"])
            self.assertEqual([x["name"] for x in oldest["files"]],
                             ["a.txt", "c.txt", "b.txt"])
            self.assertEqual(oldest["sort"], "timeold")
            self.assertEqual(
                [x["name"] for x in paged_listing(files, sort="timeold",
                                                     filter_text="b")["files"]],
                ["b.txt"])

    def test_native_navigation_and_return_keep_oldest_sort(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sub").mkdir()
            files = LocalFiles(root)
            incoming = "/listing?" + urlencode({
                "path": "sub", "page": 2, "sort": "timeold", "filter": "tex"})
            outgoing = safe_listing_return(files, incoming)
            self.assertEqual(outgoing, incoming)
            shell = listing_shell("localhost", "token", False).decode()
            self.assertIn('<option value="timeold">Oldest first</option>', shell)
            self.assertIn('<option value="timekey">Newest first</option>', shell)
            server = BrowserServer(root)
            server.start()
            try:
                with urlopen(server.url + "listing.js", timeout=5) as response:
                    script = response.read().decode("utf-8")
                self.assertIn("directoryListingUrl(item.path)", script)
                self.assertIn('directoryListingUrl(data.parent || ".")', script)
                self.assertIn("directoryListingUrl(folder.path)", script)
                self.assertIn('["filename", "filetype", "timekey", "timeold", "size", "notes"]',
                              script)
                with urlopen(server.url + "listing?sort=timeold", timeout=5) as response:
                    self.assertEqual(response.status, 200)
                with urlopen(server.url +
                             "api/listing-page?sort=timeold", timeout=5) as response:
                    self.assertIn(b'"sort": "timeold"', response.read())
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
