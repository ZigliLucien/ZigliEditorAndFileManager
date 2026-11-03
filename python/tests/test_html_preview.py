"""v53: natural HTML viewing and confined related resources."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.http import BrowserServer
from zefm.server.html_preview import site_url, site_relative_path


class HtmlPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "files"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        self.html = self.root / "docs" / "cœur ייִדיש.html"
        self.html_text = ('<!doctype html><html><head>'
                          '<link rel="stylesheet" href="theme.css"></head>'
                          '<body><h1>Hello שלום</h1><img src="logo.png">'
                          '<script>alert("should not run")</script></body></html>')
        self.html.write_text(self.html_text, encoding="utf-8")
        (self.root / "docs" / "theme.css").write_text("h1{color:navy}", encoding="utf-8")
        (self.root / "docs" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\nFAKE")
        (self.root / "private.bin").write_bytes(b"secrets")
        self.server = BrowserServer(self.root)
        self.server.start()
        self.addCleanup(self.server.close)

    def get(self, uri):
        req = Request(self.server.url.rstrip("/") + uri)
        try:
            with urlopen(req, timeout=4) as result:
                return result.status, result.read(), dict(result.headers), result.geturl()
        except HTTPError as err:
            return err.code, err.read(), dict(err.headers), err.geturl()

    def test_site_relative_path_export_and_server_import(self):
        # Catch startup failures from mismatched function names in http.py.
        from zefm.server.http import BrowserServer
        self.assertTrue(BrowserServer)
        self.assertEqual(site_relative_path("/site/docs/paper.pdf"), "docs/paper.pdf")
        with self.assertRaises(Exception):
            site_relative_path("/site/docs/../private.pdf")

    def test_html_is_rendered_not_escaped_and_relative_assets_work(self):
        code, body, headers, url = self.get("/view?" + urlencode({"path":"docs/" + self.html.name}))
        self.assertEqual(code, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(body.decode(), self.html_text)
        self.assertIn("/site/docs/", url)
        self.assertIn("sandbox;", headers["Content-Security-Policy"])
        self.assertNotIn("allow-scripts", headers["Content-Security-Policy"])
        self.assertNotIn("allow-same-origin", headers["Content-Security-Policy"])
        for path, mime in (("/site/docs/theme.css", "text/css"),
                           ("/site/docs/logo.png", "image/png")):
            status, _, h, _ = self.get(path)
            self.assertEqual(status, 200)
            self.assertIn(mime, h["Content-Type"])

    def test_local_html_links_to_other_html_and_pdf(self):
        (self.root / "docs" / "next.html").write_text(
            '<p>Other page</p><a href="paper.pdf">Read PDF</a>', encoding="utf-8")
        (self.root / "docs" / "paper.pdf").write_bytes(
            b"%PDF-1.4\\n1 0 obj\\n<<>>\\nendobj\\n%%EOF\\n")
        status, html, headers, _ = self.get("/site/docs/next.html")
        self.assertEqual(status, 200)
        self.assertIn(b'paper.pdf', html)
        self.assertIn("allow-top-navigation-by-user-activation",
                      headers["Content-Security-Policy"])
        self.assertNotIn("allow-scripts", headers["Content-Security-Policy"])
        self.assertNotIn("allow-forms", headers["Content-Security-Policy"])
        status, pdf, headers, _ = self.get("/site/docs/paper.pdf")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(headers["Content-Disposition"], "inline")
        self.assertTrue(pdf.startswith(b"%PDF-"))
        status, _, _, _ = self.get("/site/docs/next.html")
        self.assertEqual(status, 200)

    def test_pdf_link_cannot_escape_root(self):
        (self.root / "docs" / "paper.pdf").write_bytes(b"%PDF-1.4\\n%%EOF\\n")
        self.assertNotEqual(self.get("/site/docs/%2e%2e/private.bin")[0], 200)
        self.assertNotEqual(self.get("/site/docs/untrusted.js")[0], 200)

    def test_confined_resources_and_forbidden_script(self):
        (self.root / "docs" / "unsafe.js").write_text("alert(1)")
        for url in ("/site/../private.bin", "/site/docs/unsafe.js",
                    "/site/docs/no.pdf", "/site/docs/nonexistent.png"):
            with self.subTest(url=url):
                status, _, _, _ = self.get(url)
                self.assertNotEqual(status, 200)
        self.assertEqual(self.get("/site/docs/theme.css")[0], 200)

    def test_normal_text_pdf_routes_unchanged(self):
        (self.root / "docs" / "plain.txt").write_text("text")
        code, body, _, _ = self.get("/view?path=docs%2Fplain.txt")
        self.assertEqual(code, 200)
        self.assertIn(b"<pre>text</pre>", body)

    def test_bad_extension_rejected(self):
        self.assertEqual(self.get("/site/private.bin")[0], 415)
        self.assertEqual(self.get("/view?path=docs%2Fabsent.html")[0], 404)


if __name__ == "__main__":
    unittest.main()
