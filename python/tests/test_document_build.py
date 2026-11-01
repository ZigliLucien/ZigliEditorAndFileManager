"""v55: extension registry, Markdown preview and guarded PDF compilation."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import unittest

from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.file_types import handler_for
from zefm.server.document_build import build_pdf, markdown_html
from zefm.server.http import BrowserServer


class BuildModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = LocalFiles(self.root)
        self.md = self.root / "notes ייִדיש.md"
        self.md.write_text("# שלום\n\n**bold**", encoding="utf-8")
        self.tex = self.root / "paper.tex"
        self.tex.write_text(r"\documentclass{article}\begin{document}hello\end{document}")

    def test_registry(self):
        self.assertEqual(handler_for("a.MD")["view"], "markdown")
        self.assertEqual(handler_for("a.tex")["build"], "lualatex")
        self.assertEqual(handler_for("a.pdf")["view"], "pdf")
        self.assertIsNone(handler_for("a.txt")["build"])

    def test_markdown_fallback_without_pandoc(self):
        with patch("zefm.server.document_build.shutil.which", return_value=None):
            html = markdown_html(self.files, self.md.name).decode()
        self.assertIn("שלום", html)
        self.assertIn("# שלום", html)
        self.assertIn("<pre>", html)

    def test_markdown_pandoc_rendered_html(self):
        class Result:
            returncode = 0
            stdout = "<h1>שלום</h1>"
            stderr = ""
        with patch("zefm.server.document_build.shutil.which", return_value="/usr/bin/pandoc"), \
             patch("zefm.server.document_build.subprocess.run", return_value=Result()) as run:
            html = markdown_html(self.files, self.md.name).decode()
        self.assertIn("<h1>שלום</h1>", html)
        self.assertIn("--from=markdown-raw_html", run.call_args.args[0])

    def test_tex_success_verified_new_pdf(self):
        def fake_run(command, **kwargs):
            self.assertIn("-no-shell-escape", command)
            directory = next(x.split("=", 1)[1] for x in command
                             if x.startswith("-output-directory="))
            (Path(directory) / "paper.pdf").write_bytes(b"%PDF-1.7\nnew pdf")
            class Result:
                returncode = 0
                stdout = "compiled"
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which", return_value="/usr/bin/lualatex"), \
             patch("zefm.server.document_build.subprocess.run", side_effect=fake_run):
            result = build_pdf(self.files, "paper.tex")
        self.assertTrue(result["ok"])
        self.assertIn("compiled", result["log"])
        self.assertTrue((self.root / result["pdf"]).is_file())
        self.assertTrue(result["pdf"].endswith(".pdf"))

    def test_build_failure_does_not_open_stale_pdf(self):
        class Result:
            returncode = 1
            stdout = "! Undefined control sequence"
            stderr = "compile failed"
        with patch("zefm.server.document_build.shutil.which", return_value="/usr/bin/lualatex"), \
             patch("zefm.server.document_build.subprocess.run", return_value=Result()):
            result = build_pdf(self.files, "paper.tex")
        self.assertFalse(result["ok"])
        self.assertNotIn("pdf", result)
        self.assertIn("Undefined", result["log"])

    def test_refuse_traversal_and_invalid_types(self):
        with self.assertRaises(BrowserError):
            build_pdf(self.files, "../escape.tex")
        (self.root / "other.txt").write_text("text")
        with self.assertRaises(BrowserError):
            build_pdf(self.files, "other.txt")


class BuildBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "cœur.md").write_text("# Heading")
        self.server = BrowserServer(self.root)
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, route, data=None):
        body = urlencode(data).encode() if data is not None else None
        request = Request(self.server.url.rstrip("/") + route,
                          data=body,
                          headers={"Content-Type": "application/x-www-form-urlencoded"} if body else {})
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, response.read(), dict(response.headers)
        except HTTPError as exc:
            return exc.code, exc.read(), dict(exc.headers)

    def test_markdown_browser_preview_and_csp(self):
        code, data, headers = self.request("/view?path=c%C5%93ur.md")
        self.assertEqual(code, 200)
        self.assertIn(b"Heading", data)
        self.assertIn("sandbox", headers["Content-Security-Policy"])
        self.assertNotIn("allow-scripts", headers["Content-Security-Policy"])

    def test_build_popup_and_post_validation(self):
        status, html, headers = self.request("/build?path=c%C5%93ur.md")
        self.assertEqual(status, 200)
        self.assertIn(b'id="zefm-build-form"', html)
        self.assertIn(b'/build.js', html)
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        code, script, _ = self.request("/build.js")
        self.assertEqual(code, 200)
        self.assertIn(b'fetch("/build"', script)
        self.assertEqual(self.request("/build", {"csrf":"bad","path":"cœur.md"})[0], 403)
        self.assertEqual(self.request("/build", {"csrf":self.server.token,
                          "path":"cœur.md","extra":"unexpected"})[0], 400)

    def test_build_failure_diagnostics_json(self):
        with patch("zefm.server.document_build.shutil.which", return_value=None):
            status, body, headers = self.request("/build", {
                "csrf":self.server.token, "path":"cœur.md"})
        self.assertEqual(status, 503)
        result = json.loads(body)
        self.assertFalse(result["ok"])
        self.assertIn("Pandoc", result["error"])
        self.assertIn("application/json", headers["Content-Type"])


if __name__ == "__main__":
    unittest.main()
