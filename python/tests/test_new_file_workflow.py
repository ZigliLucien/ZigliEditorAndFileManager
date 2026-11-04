"""v74: safe New File workflow ported from ServPakDir file-operations intent."""
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.http import BrowserServer


class NewFileUnitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "root"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        self.files = LocalFiles(self.root)

    def test_create_empty_unicode_file_exclusively(self):
        filename = "קאַץ cœur.md"
        created = self.files.create_file("docs", filename)
        self.assertEqual(created, self.root / "docs" / filename)
        self.assertEqual(created.read_bytes(), b"")
        self.assertEqual(created.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(BrowserError) as error:
            self.files.create_file("docs", filename)
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(created.read_bytes(), b"")

    def test_existing_directory_or_symlink_never_overwritten(self):
        (self.root / "docs" / "present").mkdir()
        (self.root / "docs" / "alias").symlink_to("present")
        for name in ("present", "alias"):
            with self.subTest(name=name), self.assertRaises(BrowserError) as caught:
                self.files.create_file("docs", name)
            self.assertEqual(caught.exception.status, 409)
        self.assertTrue((self.root / "docs" / "present").is_dir())

    def test_invalid_filename_and_escaping_root(self):
        for name in ("", ".", "..", "../oops", "/tmp/oops", "a/b",
                     "a\\b", "bad\nname", "x" * 256):
            with self.subTest(name=name), self.assertRaises(BrowserError):
                self.files.create_file("docs", name)
        with self.assertRaises(BrowserError) as caught:
            self.files.create_file("../", "escape.txt")
        self.assertEqual(caught.exception.status, 403)
        self.assertFalse((self.root.parent / "escape.txt").exists())


class NewFileHttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        self.server = BrowserServer(self.root)
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, route, fields=None, host=None):
        body = urlencode(fields).encode("utf-8") if fields is not None else None
        req = Request(self.server.url.rstrip("/") + route, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"}
                      if body is not None else {})
        if host:
            req.add_header("Host", host)
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_link_form_create_and_quick_edit(self):
        state = "/listing?" + urlencode(
            {"path": "docs", "page": "1", "sort": "filetype", "filter": "draft"})
        status, shell = self.request("/listing?path=docs")
        self.assertEqual(status, 200)
        self.assertIn('id="new-file"', shell)
        status, basic = self.request("/browse?path=docs")
        self.assertEqual(status, 200)
        self.assertIn("New file", basic)
        form_url = "/new-file?" + urlencode({"path": "docs", "back": state})
        status, form = self.request(form_url)
        self.assertEqual(status, 200)
        self.assertIn('action="/new-file"', form)
        fields = {"csrf": self.server.token, "path": "docs",
                  "name": "new ייִדיש.md", "back": state}
        status, result = self.request("/new-file", fields)
        self.assertEqual(status, 201)
        self.assertEqual((self.root / "docs" / fields["name"]).read_bytes(), b"")
        self.assertIn("Quick edit new file", result)
        self.assertIn("sort=filetype", result)
        self.assertIn("filter=draft", result)
        status, edit_page = self.request("/edit?" + urlencode(
            {"path": "docs/" + fields["name"], "back": state}))
        self.assertEqual(status, 200)
        self.assertIn("textarea", edit_page)
        self.assertEqual(self.request("/new-file", fields)[0], 409)

    def test_reject_forged_requests_without_creating_files(self):
        basic = {"csrf": self.server.token, "path": "docs", "name": "new.txt"}
        for bad in (
            {**basic, "csrf": "wrong"},
            {**basic, "name": "../escape"},
            {**basic, "extra": "unexpected"},
            {**basic, "path": ".."},
        ):
            with self.subTest(bad=bad):
                status, _ = self.request("/new-file", bad)
                self.assertNotIn(status, (200, 201))
        self.assertEqual(self.request("/new-file", basic, host="attacker.test")[0], 403)
        self.assertFalse((self.root / "docs" / "new.txt").exists())


if __name__ == "__main__":
    unittest.main()
