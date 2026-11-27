"""Tests for source-directory navigation in rendered previews."""
import unittest
from zefm.server.navigation import preview_navigation


class PreviewNavigationTests(unittest.TestCase):
    def test_insert_inside_body_and_escape_url(self):
        document = '<html><head><title>Notes</title></head><BODY class="notes"><p>Text</p></BODY></html>'
        result = preview_navigation(document, "/listing?path=notes&sort=filename")
        self.assertIn('<BODY class="notes"><nav', result)
        self.assertIn('href="/listing?path=notes&amp;sort=filename"', result)
        self.assertIn("<p>Text</p></BODY>", result)

    def test_previous_listing_is_distinct(self):
        result = preview_navigation("<body>content</body>", "/listing?path=notes",
                                    "/listing?path=notes&page=2")
        self.assertIn("Open source directory", result)
        self.assertIn("Return to previous listing", result)
        self.assertIn("page=2", result)
        same = preview_navigation("<body>content</body>", "/listing", "/listing")
        self.assertNotIn("Return to previous listing", same)

    def test_fragment_and_absolute_loopback_link(self):
        result = preview_navigation("<p>Notes</p>",
                                    "http://127.0.0.1:12345/listing?path=.")
        self.assertTrue(result.startswith("<nav"))
        self.assertIn("http://127.0.0.1:12345/listing?path=.", result)
        self.assertTrue(result.endswith("<p>Notes</p>"))


if __name__ == "__main__":
    unittest.main()
