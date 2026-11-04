"""Root-confined content search, source matching and HTTP integration."""
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from zefm.server.content_search import search_text, MAX_RESULTS
from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.http import BrowserServer


class ContentSearchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "root"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        (self.root / "docs" / "French.txt").write_text("Cœur et cœur\n", encoding="utf-8")
        (self.root / "docs" / "Yiddish.yid").write_text("אַ גוטן טאָג\n", encoding="utf-8")
        (self.root / "docs" / "code.py").write_text(
            "print('SearchThis')\nprint('<script>SearchThis</script>')\n", encoding="utf-8")
        (self.root / "docs" / "binary.bin").write_bytes(b"SearchThis\x00secret")
        (self.root / ".hidden").mkdir()
        (self.root / ".hidden" / "secret.txt").write_text("SearchThis", encoding="utf-8")
        self.files = LocalFiles(self.root)

    def test_unicode_and_case_sensitivity(self):
        matches = search_text(self.files, "docs", "cœur")
        self.assertEqual([(hit.path, hit.line) for hit in matches.hits],
                         [("docs/French.txt", 1)])
        self.assertEqual(len(search_text(self.files, "docs", "CŒUR", case_sensitive=True).hits), 0)
        self.assertEqual(search_text(self.files, "docs", "טאָג").hits[0].path,
                         "docs/Yiddish.yid")

    def test_binary_hidden_and_symlinks_not_scanned(self):
        (self.root / "docs" / "outside").symlink_to(self.root / ".hidden", target_is_directory=True)
        matches = search_text(self.files, ".", "SearchThis")
        self.assertEqual([hit.path for hit in matches.hits],
                         ["docs/code.py", "docs/code.py"])
        self.assertNotIn("binary.bin", str(matches.hits))

    def test_result_limit_and_bad_query(self):
        (self.root / "lots.txt").write_text("match\n" * (MAX_RESULTS + 8), encoding="utf-8")
        results = search_text(self.files, ".", "match")
        self.assertEqual(len(results.hits), MAX_RESULTS)
        self.assertTrue(results.truncated)
        for invalid in ("", "  ", "x" * 201, "new\nline"):
            with self.subTest(invalid=invalid), self.assertRaises(BrowserError):
                search_text(self.files, ".", invalid)
        with self.assertRaises(BrowserError):
            search_text(self.files, "../", "hello")

    def test_http_escaped_results_and_directory_back(self):
        server = BrowserServer(self.root)
        server.start()
        self.addCleanup(server.close)
        root_url = server.url.rstrip("/")
        url = root_url + "/search-text?" + urlencode({"path": "docs", "q": "SearchThis"})
        with urlopen(url, timeout=5) as response:
            html = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
        self.assertIn("Search file contents", html)
        self.assertIn("docs%2Fcode.py", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>SearchThis</script>", html)
        self.assertIn("Back to directory", html)
        with urlopen(root_url + "/listing?path=docs", timeout=5) as response:
            self.assertIn("search-string", response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
