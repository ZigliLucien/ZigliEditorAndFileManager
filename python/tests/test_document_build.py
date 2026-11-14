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

    def test_markdown_fallback_without_discount(self):
        with patch("zefm.server.document_build.shutil.which", return_value=None):
            html = markdown_html(self.files, self.md.name).decode()
        self.assertIn("שלום", html)
        self.assertIn("# שלום", html)
        self.assertIn("<pre>", html)

    def test_markdown_makepage_full_document(self):
        class Result:
            returncode = 0
            stdout = "<!doctype html><html><head></head><body><h1>שלום</h1></body></html>"
            stderr = ""
        with patch("zefm.server.document_build.shutil.which",
                   side_effect=lambda name: "/usr/local/bin/makepage" if name == "makepage" else None), \
             patch("zefm.server.document_build.subprocess.run", return_value=Result()) as run:
            html = markdown_html(self.files, self.md.name).decode()
        self.assertIn("<h1>שלום</h1>", html)
        self.assertEqual(html.count("<html>"), 1)
        self.assertIn("latex,nostyle,nohtml", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["input"], "# שלום\n\n**bold**")

    def test_discount_markdown_cli_fallback(self):
        class Result:
            returncode = 0
            stdout = "<h1>שלום</h1>"
        with patch("zefm.server.document_build.shutil.which",
                   side_effect=lambda name: "/usr/local/bin/markdown" if name == "markdown" else None), \
             patch("zefm.server.document_build.subprocess.run", return_value=Result()) as run:
            html = markdown_html(self.files, self.md.name).decode()
        self.assertIn('<body class="zefm-math-page"><h1>שלום</h1></body>', html)
        self.assertEqual(html.count("<html>"), 1)

    def test_markdown_pdf_pipeline_uses_discount_and_weasyprint(self):
        def fake_run(command, **kwargs):
            if command[0].endswith("makepage"):
                class Rendered:
                    returncode = 0
                    stdout = "<html><body><h1>שלום</h1></body></html>"
                return Rendered()
            self.assertTrue(command[0].endswith("weasyprint"))
            self.assertEqual(Path(command[1]).name, "document.html")
            self.assertEqual(Path(command[2]).name, "document.pdf")
            self.assertIn("<h1>שלום</h1>", Path(command[1]).read_text())
            Path(command[2]).write_bytes(b"%PDF-1.7\nvalid")
            class Compiled:
                returncode = 0
                stdout = "Rendered with WeasyPrint"
                stderr = ""
            return Compiled()
        with patch("zefm.server.document_build.shutil.which",
                   side_effect=lambda name: "/usr/bin/" + name), \
             patch("zefm.server.document_build.subprocess.run", side_effect=fake_run):
            result = build_pdf(self.files, self.md.name)
        self.assertTrue(result["ok"])
        self.assertIn("Rendered", result["log"])

    def test_mactex_standard_path_when_gui_path_lacks_lualatex(self):
        from zefm.server.document_build import _command
        descriptor = handler_for("paper.tex")
        with patch("zefm.server.document_build.sys.platform", "darwin"), \
             patch("zefm.server.document_build.shutil.which", return_value=None), \
             patch("zefm.server.document_build.Path.is_file", return_value=True), \
             patch("zefm.server.document_build.os.access", return_value=True):
            command = _command(self.tex, self.root, descriptor)
        self.assertEqual(command[0], "/Library/TeX/texbin/lualatex")
        self.assertIn("-no-shell-escape", command)

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
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            result = build_pdf(self.files, "paper.tex")
        self.assertTrue(result["ok"])
        self.assertIn("compiled", result["log"])
        self.assertTrue((self.root / result["pdf"]).is_file())
        self.assertTrue(result["pdf"].endswith(".pdf"))

    def test_repeated_tex_builds_publish_distinct_pdf_paths(self):
        # The old stable path was overwritten, leaving the Mac's PDF viewer
        # displaying a cached copy. Each successful build needs a fresh URL.
        count = [0]
        def fake_run(command, **kwargs):
            count[0] += 1
            directory = next(value.split("=", 1)[1] for value in command
                             if value.startswith("-output-directory="))
            (Path(directory) / "paper.pdf").write_bytes(
                b"%PDF-1.7\\n" + str(count[0]).encode())
            class Result:
                returncode = 0
                stdout = "compiled"
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run",
                   side_effect=fake_run):
            first = build_pdf(self.files, "paper.tex")
            second = build_pdf(self.files, "paper.tex")
        self.assertTrue(first["ok"])
        self.assertTrue(second["ok"])
        self.assertNotEqual(first["pdf"], second["pdf"])
        self.assertTrue((self.root / first["pdf"]).is_file())
        self.assertTrue((self.root / second["pdf"]).is_file())
        self.assertNotEqual((self.root / first["pdf"]).read_bytes(),
                            (self.root / second["pdf"]).read_bytes())

    def test_tex_build_publishes_matching_synctex_preview(self):
        def fake_run(command, **kwargs):
            self.assertIn("-synctex=1", command)
            directory = Path(next(value.split("=", 1)[1] for value in command
                             if value.startswith("-output-directory=")))
            (directory / "paper.pdf").write_bytes(b"%PDF-1.7\nnew")
            (directory / "paper.synctex.gz").write_bytes(b"synctex-bytes")
            class Result:
                returncode = 0
                stdout = "compiled"
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run",
                   side_effect=fake_run):
            result = build_pdf(self.files, "paper.tex", publish_adjacent=True)
        self.assertTrue(result["ok"])
        pdf = self.root / result["pdf"]
        companion = self.root / result["synctex"]
        self.assertEqual(companion, pdf.with_suffix(".synctex.gz"))
        self.assertEqual(companion.read_bytes(), b"synctex-bytes")
        self.assertEqual(result["output_pdf"], "paper.pdf")
        self.assertTrue((self.root / "paper.pdf").is_file())

    def test_no_synctex_metadata_is_not_a_compile_failure(self):
        def fake_run(command, **kwargs):
            directory = Path(next(value.split("=", 1)[1] for value in command
                             if value.startswith("-output-directory=")))
            (directory / "paper.pdf").write_bytes(b"%PDF-1.7\nnew")
            class Result:
                returncode = 0
                stdout = "compiled"
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run",
                   side_effect=fake_run):
            result = build_pdf(self.files, "paper.tex", publish_adjacent=True)
        self.assertTrue(result["ok"])
        self.assertNotIn("synctex", result)

    def test_editor_build_updates_adjacent_pdf_atomically(self):
        adjacent = self.root / "paper.pdf"
        adjacent.write_bytes(b"%PDF-1.7\\nold")
        def fake_run(command, **kwargs):
            directory = next(value.split("=", 1)[1] for value in command
                             if value.startswith("-output-directory="))
            (Path(directory) / "paper.pdf").write_bytes(b"%PDF-1.7\\nnew")
            class Result:
                returncode = 0
                stdout = "compiled"
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            result = build_pdf(self.files, "paper.tex", publish_adjacent=True)
        self.assertTrue(result["ok"])
        self.assertEqual(result["output_pdf"], "paper.pdf")
        self.assertEqual(adjacent.read_bytes(), b"%PDF-1.7\\nnew")
        self.assertNotEqual(result["pdf"], "paper.pdf")
        self.assertTrue((self.root / result["pdf"]).exists())

    def test_browser_build_does_not_replace_adjacent_pdf(self):
        adjacent = self.root / "paper.pdf"
        adjacent.write_bytes(b"%PDF-1.7\\nkeep")
        def fake_run(command, **kwargs):
            directory = next(value.split("=", 1)[1] for value in command
                             if value.startswith("-output-directory="))
            (Path(directory) / "paper.pdf").write_bytes(b"%PDF-1.7\\nbuilt")
            class Result:
                returncode = 0
                stdout = "compiled"
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            result = build_pdf(self.files, "paper.tex")
        self.assertTrue(result["ok"])
        self.assertNotIn("output_pdf", result)
        self.assertEqual(adjacent.read_bytes(), b"%PDF-1.7\\nkeep")

    def test_editor_build_refuses_pdf_symlink(self):
        adjacent = self.root / "paper.pdf"
        outside = self.root / "outside.pdf"
        outside.write_bytes(b"%PDF-1.7\\nkeep")
        adjacent.symlink_to(outside)
        def fake_run(command, **kwargs):
            directory = next(value.split("=", 1)[1] for value in command
                             if value.startswith("-output-directory="))
            (Path(directory) / "paper.pdf").write_bytes(b"%PDF-1.7\\nnew")
            class Result:
                returncode = 0
                stdout = ""
                stderr = ""
            return Result()
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            with self.assertRaises(BrowserError):
                build_pdf(self.files, "paper.tex", publish_adjacent=True)
        self.assertEqual(outside.read_bytes(), b"%PDF-1.7\\nkeep")

    def test_failed_editor_build_leaves_existing_pdf_unchanged(self):
        adjacent = self.root / "paper.pdf"
        adjacent.write_bytes(b"%PDF-1.7\\nold")
        class Result:
            returncode = 1
            stdout = "! error"
            stderr = ""
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run", return_value=Result()):
            result = build_pdf(self.files, "paper.tex", publish_adjacent=True)
        self.assertFalse(result["ok"])
        self.assertEqual(adjacent.read_bytes(), b"%PDF-1.7\\nold")

    def test_build_failure_does_not_open_stale_pdf(self):
        class Result:
            returncode = 1
            stdout = "! Undefined control sequence"
            stderr = "compile failed"
        with patch("zefm.server.document_build.shutil.which", return_value="/usr/bin/lualatex"), \
             patch("zefm.server.latex_sequence.subprocess.run", return_value=Result()):
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
        self.assertIn("sandbox allow-scripts", headers["Content-Security-Policy"])
        self.assertNotIn("allow-same-origin", headers["Content-Security-Policy"])

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
        self.assertIn("Discount", result["error"])
        self.assertIn("application/json", headers["Content-Type"])


if __name__ == "__main__":
    unittest.main()
