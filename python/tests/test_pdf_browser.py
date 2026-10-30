"""Native browser PDF tests: inline MIME, range requests, path guards."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.http import BrowserServer
from zefm.server.pdf_delivery import byte_range
from zefm.server.file_manager import BrowserError


class PdfRangeTests(unittest.TestCase):
    def test_ranges_and_suffix(self):
        self.assertEqual(byte_range(None, 100), (0, 99, False))
        self.assertEqual(byte_range("bytes=0-9", 100), (0, 9, True))
        self.assertEqual(byte_range("bytes=90-", 100), (90, 99, True))
        self.assertEqual(byte_range("bytes=-10", 100), (90, 99, True))
        self.assertEqual(byte_range("bytes=0-900", 100), (0, 99, True))
        for invalid in ("bytes=100-", "bytes=12-3", "bytes=-0",
                        "bytes=0-5,10-20", "not-a-range", "bytes=-"):
            with self.subTest(range=invalid), self.assertRaises(BrowserError):
                byte_range(invalid, 100)


class BrowserPdfTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "files"
        self.root.mkdir()
        self.pdf = self.root / "Math ייִדיש.PDF"
        # Minimal PDF-signature fixture (response tests, not a rendering test).
        self.bytes = b"%PDF-1.4\n" + b"0" * 2000 + b"\n%%EOF\n"
        self.pdf.write_bytes(self.bytes)
        (self.root / "hello.txt").write_text("text", encoding="utf-8")
        self.server = BrowserServer(self.root)
        self.server.start()
        self.addCleanup(self.server.close)

    def get(self, endpoint, headers=None):
        request = Request(self.server.url.rstrip("/") + endpoint, headers=headers or {})
        try:
            with urlopen(request, timeout=5) as r:
                return r.status, r.read(), dict(r.headers)
        except HTTPError as error:
            return error.code, error.read(), dict(error.headers)

    def test_native_pdf_view_and_seek(self):
        uri = "/pdf?" + urlencode({"path": self.pdf.name})
        status, body, headers = self.get(uri)
        self.assertEqual(status, 200)
        self.assertEqual(body, self.bytes)
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(headers["Content-Disposition"], "inline")
        self.assertEqual(headers["Accept-Ranges"], "bytes")
        self.assertEqual(headers["Cache-Control"], "no-store")
        status, body, headers = self.get(uri, {"Range": "bytes=5-20"})
        self.assertEqual(status, 206)
        self.assertEqual(body, self.bytes[5:21])
        self.assertEqual(headers["Content-Range"], f"bytes 5-20/{len(self.bytes)}")
        status, body, headers = self.get(uri, {"Range": "bytes=-7"})
        self.assertEqual(status, 206)
        self.assertEqual(body, self.bytes[-7:])
        status, _, headers = self.get(uri, {"Range": "bytes=999999-"})
        self.assertEqual(status, 416)
        self.assertEqual(headers["Content-Range"], f"bytes */{len(self.bytes)}")

    def test_existing_view_route_dispatches_pdf(self):
        uri = "/view?" + urlencode({"path": self.pdf.name})
        status, body, headers = self.get(uri)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(body, self.bytes)

    def test_pdf_links_and_text_still_work(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        html = body.decode()
        self.assertIn("Open PDF", html)
        self.assertIn("/pdf?path=", html)
        self.assertIn("Quick edit", html)
        status, body, headers = self.get("/view?path=hello.txt")
        self.assertEqual(status, 200)
        self.assertIn(b"text", body)
        self.assertIn("text/html", headers["Content-Type"])
        status, body, headers = self.get("/raw?" + urlencode({"path": self.pdf.name}))
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/octet-stream")
        self.assertIn("attachment", headers["Content-Disposition"])

    def test_invalid_file_and_path_rejected(self):
        self.assertEqual(self.get("/pdf?path=hello.txt")[0], 415)
        self.assertEqual(self.get("/pdf?path=missing.pdf")[0], 404)
        self.assertEqual(self.get("/pdf?path=..%2Foutside.pdf")[0], 403)
        self.assertEqual(self.get("/pdf?" + urlencode({"path": self.pdf.name}) + "&junk=1")[0], 400)
        fake = self.root / "fake.pdf"
        fake.write_bytes(b"not a pdf")
        self.assertEqual(self.get("/pdf?path=fake.pdf")[0], 415)


if __name__ == "__main__":
    unittest.main()
