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
        self.assertIn("sandbox allow-top-navigation-by-user-activation", headers["Content-Security-Policy"])
        self.assertNotIn("allow-scripts", headers["Content-Security-Policy"])
        self.assertNotIn("allow-same-origin", headers["Content-Security-Policy"])
        for path, mime in (("/site/docs/theme.css", "text/css"),
                           ("/site/docs/logo.png", "image/png")):
            status, _, h, _ = self.get(path)
            self.assertEqual(status, 200)
            self.assertIn(mime, h["Content-Type"])

    def test_xhtml_links_follow_sandboxed_html_preview(self):
        xhtml = self.root / "docs" / "page.xhtml"
        xhtml.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<html xmlns="http://www.w3.org/1999/xhtml">'
            '<body><p>XHTML page</p><a href="next.html">Next</a></body></html>',
            encoding="utf-8")
        status, body, headers, url = self.get("/view?path=docs%2Fpage.xhtml")
        self.assertEqual(status, 200)
        self.assertIn(b"XHTML page", body)
        self.assertIn("/site/docs/page.xhtml", url)
        self.assertIn("application/xhtml+xml", headers["Content-Type"])
        self.assertIn("sandbox", headers["Content-Security-Policy"])

    def test_absolute_local_file_links_are_rewritten_within_root(self):
        (self.root / "docs" / "data.txt").write_text("example text", encoding="utf-8")
        (self.root / "docs" / "sub").mkdir(exist_ok=True)
        html = ('<a href="' + (self.root / "docs" / "data.txt").as_uri()
                + '">file URL</a><a href="/docs/data.txt">root-relative</a>'
                + '<a href="' + (self.root / "docs" / "sub").as_uri()
                + '">directory</a>'
                + '<a href="https://example.org/page">external</a>'
                + '<a href="file:///etc/passwd">outside</a>')
        (self.root / "docs" / "links.html").write_text(html, encoding="utf-8")
        code, output, _, _ = self.get("/site/docs/links.html")
        self.assertEqual(code, 200)
        self.assertIn(b'/site/docs/data.txt', output)
        self.assertIn(b'/site/docs/sub/', output)
        self.assertIn(b'https://example.org/page', output)
        self.assertIn(b'file:///etc/passwd', output)
        self.assertNotIn((self.root / "docs" / "data.txt").as_uri().encode(), output)
        code, text, _, _ = self.get("/site/docs/data.txt")
        self.assertEqual(code, 200)
        self.assertIn(b'example text', text)

    def test_html_directory_links_open_file_listing(self):
        (self.root / "docs" / "sub").mkdir()
        (self.root / "docs" / "sub" / "readme.txt").write_text(
            "nested document", encoding="utf-8")
        # A relative HTML href="sub/" or href="sub" should navigate to
        # the normal ZEFM directory listing, not yield a file error.
        for uri in ("/site/docs/sub", "/site/docs/sub/"):
            with self.subTest(uri=uri):
                code, html, headers, final_url = self.get(uri)
                self.assertEqual(code, 200)
                self.assertIn(b'id="folder-home"', html)
                self.assertIn("/listing?path=docs%2Fsub", final_url)

    def test_site_link_outside_root_denied(self):
        with self.assertRaises(Exception):
            site_relative_path("/site/docs/../..")
        status, _, _, _ = self.get("/site/docs/missing-folder/")
        self.assertEqual(status, 404)

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
        for url in ("/site/../private.bin", "/site/docs/no.pdf",
                    "/site/docs/nonexistent.png"):
            with self.subTest(url=url):
                status, _, _, _ = self.get(url)
                self.assertNotEqual(status, 200)
        self.assertEqual(self.get("/site/docs/theme.css")[0], 200)
        # A JS hyperlink is a source-text view, never a script resource.
        status, body, headers, _ = self.get("/site/docs/unsafe.js")
        self.assertEqual(status, 200)
        self.assertIn(b"alert", body)
        self.assertIn("text/html", headers["Content-Type"])

    def test_linked_extensions_follow_normal_view_dispatch(self):
        from zipfile import ZipFile
        (self.root / "docs" / "data.json").write_text(
            '{"answer":42}', encoding="utf-8")
        (self.root / "docs" / "source.py").write_text(
            'print("hello")', encoding="utf-8")
        (self.root / "docs" / "file.unknown").write_bytes(b"opaque payload")
        (self.root / "docs" / "script.js").write_text(
            "alert('not executed')", encoding="utf-8")
        with ZipFile(self.root / "docs" / "bundle.jar", "w") as archive:
            archive.writestr("Example.class", b"binary")
        cases = (
            ("/site/docs/data.json", b"answer", "text/html"),
            ("/site/docs/source.py", b"print", "text/html"),
            ("/site/docs/script.js", b"alert", "text/html"),
            ("/site/docs/bundle.jar", b"Example.class", "text/html"),
            ("/site/docs/file.unknown", b"opaque payload", "application/octet-stream"),
        )
        for uri, expected, mime in cases:
            with self.subTest(uri=uri):
                status, body, headers, target = self.get(uri)
                self.assertEqual(status, 200)
                self.assertIn(expected, body)
                self.assertIn(mime, headers["Content-Type"])
                self.assertNotEqual(target.split("?", 1)[0], self.server.url.rstrip("/") + uri)

    def test_normal_text_pdf_routes_unchanged(self):
        (self.root / "docs" / "plain.txt").write_text("text")
        code, body, _, _ = self.get("/view?path=docs%2Fplain.txt")
        self.assertEqual(code, 200)
        self.assertIn(b"<pre>text</pre>", body)

    def test_bad_extension_rejected(self):
        code, body, headers, target = self.get("/site/private.bin")
        self.assertEqual(code, 200)
        self.assertEqual(body, b"secrets")
        self.assertIn("application/octet-stream", headers["Content-Type"])
        self.assertEqual(self.get("/view?path=docs%2Fabsent.html")[0], 404)


if __name__ == "__main__":
    unittest.main()
