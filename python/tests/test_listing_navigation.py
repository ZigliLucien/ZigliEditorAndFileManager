"""v52: preserve originating GoFM listing position across file actions."""
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import unittest

from zefm.server.http import BrowserServer
from zefm.server.navigation import safe_listing_return
from zefm.server.file_manager import BrowserError, LocalFiles


class NavigationValidationTests(unittest.TestCase):
    def setUp(self):
        self.t = TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.files = LocalFiles(self.t.name)
        (Path(self.t.name) / "Sub").mkdir()

    def test_roundtrip_and_guard(self):
        url = "/listing?" + urlencode({"path":"Sub", "page":"3",
                 "sort":"timekey", "filter":"cœur ייִדיש"})
        self.assertEqual(safe_listing_return(self.files, url),
                         "/listing?" + urlencode({"path":"Sub", "page":"3",
                         "sort":"timekey", "filter":"cœur ייִדיש"}))
        for bad in ("https://example.org/", "//example.org/listing", 
                    "/notes?path=.", "/listing?path=..",
                    "/listing?path=.&page=0", "/listing?path=.&sort=evil",
                    "/listing?path=.&page=1&page=2", 
                    "/listing?path=.&page=1&evil=x"):
            with self.subTest(bad=bad), self.assertRaises(BrowserError):
                safe_listing_return(self.files, bad)


class NavigationBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "Sub").mkdir()
        self.path = self.root / "Sub" / "bonjour.txt"
        self.path.write_text("hello")
        self.browser = BrowserServer(str(self.root), open_in_editor=lambda _:None)
        self.browser.start()
        self.addCleanup(self.browser.close)
        self.back = "/listing?" + urlencode({
            "path":"Sub","page":"3","sort":"timekey","filter":"bonjour"})

    def get(self, route, fields=None):
        body = urlencode(fields).encode() if fields is not None else None
        request = Request(self.browser.url.rstrip("/") + route, data=body,
                          headers={"Content-Type":"application/x-www-form-urlencoded"} if body else {})
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_action_forms_return_to_exact_listing(self):
        for route in ("view", "edit", "copy", "rename", "notes", "note-edit"):
            with self.subTest(route=route):
                status, html = self.get("/" + route + "?" + urlencode({
                    "path":"Sub/bonjour.txt","back":self.back}))
                self.assertEqual(status, 200, html)
                self.assertIn(self.back.replace("&", "&amp;"), html)

    def test_rename_and_copy_confirmation_return(self):
        for route, name in (("copy", "duplicate.txt"),("rename", "newname.txt")):
            with self.subTest(route=route):
                status, html = self.get("/" + route, {
                    "csrf":self.browser.token,"path":"Sub/bonjour.txt",
                    "name":name, "back":self.back})
                self.assertEqual(status, 200 if route == "rename" else 201)
                self.assertIn(self.back.replace("&", "&amp;"), html)
                if route == "rename":
                    self.path = self.root / "Sub" / "newname.txt"

    def test_malicious_return_parameter_rejected(self):
        for bad in ("https://attacker.invalid/", "/listing?path=..",
                    "/listing?path=Sub&sort=bad"):
            with self.subTest(back=bad):
                status, _ = self.get("/view?" + urlencode({
                    "path":"Sub/bonjour.txt","back":bad}))
                self.assertIn(status, (400, 403))
        self.assertEqual(self.get("/edit?" + urlencode({
            "path":"Sub/bonjour.txt","back":self.back}))[0], 200)


if __name__ == "__main__":
    unittest.main()
