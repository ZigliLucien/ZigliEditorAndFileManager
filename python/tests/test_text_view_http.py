"""End-to-end HTTP checks for View of Yiddish and unknown UTF-8 extensions."""
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from zefm.server.http import BrowserServer


class TextViewHttpTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        (root / "note.yid").write_text("שלום ייִדיש\n<test>", encoding="utf-8")
        (root / "help.info").write_text("GNU Info node\n", encoding="utf-8")
        (root / "odd.xyz").write_text("readable Cœur", encoding="utf-8")
        (root / "data.blob").write_bytes(bytes.fromhex("00 ff fe 01"))
        self.server = BrowserServer(root)
        self.server.start()
        self.addCleanup(self.server.close)

    def get(self, filename):
        url = self.server.url.rstrip("/") + "/view?" + urlencode({"path": filename})
        try:
            with urlopen(url, timeout=5) as response:
                return response.status, response.read(), response.headers
        except HTTPError as error:
            return error.code, error.read(), error.headers

    def test_yiddish_view_has_right_to_left_markup(self):
        status, body, headers = self.get("note.yid")
        self.assertEqual(status, 200)
        self.assertIn(b'lang="yi" dir="rtl"', body)
        self.assertIn("&lt;test&gt;".encode(), body)
        self.assertIn("text/html", headers["Content-Type"])

    def test_info_and_unknown_utf8_show_inline(self):
        for name, snippet in (("help.info", b"GNU Info node"),
                              ("odd.xyz", b"readable C")):
            with self.subTest(name=name):
                status, body, headers = self.get(name)
                self.assertEqual(status, 200)
                self.assertIn(snippet, body)
                self.assertIn("text/html", headers["Content-Type"])

    def test_unknown_binary_downloads_instead_of_html(self):
        status, body, headers = self.get("data.blob")
        self.assertEqual(status, 200)
        self.assertEqual(body, bytes.fromhex("00 ff fe 01"))
        self.assertIn("attachment", headers.get("Content-Disposition", ""))


if __name__ == "__main__":
    unittest.main()
