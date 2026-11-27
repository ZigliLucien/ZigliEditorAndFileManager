"""latexmk uses the bounded one-process build path and publishes verified PDFs."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import subprocess
import unittest

from zefm.server.document_build import build_pdf
from zefm.server.file_manager import LocalFiles


class LatexmkBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "paper.tex"
        self.source.write_text(r"\\documentclass{article}\\begin{document}ok\\end{document}")

    def test_one_latexmk_process_and_adjacent_pdf(self):
        calls = []
        def fake_run(argv, **kwargs):
            calls.append((argv, kwargs))
            outdir = next(x.split("=", 1)[1] for x in argv
                          if x.startswith("-outdir="))
            produced = Path(outdir) / "paper.pdf"
            produced.write_bytes(b"%PDF-1.4\\nvalid content")
            (Path(outdir) / "paper.synctex.gz").write_bytes(b"index")
            return subprocess.CompletedProcess(argv, 0, "latexmk succeeded", "")
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/latexmk"), \
             patch("zefm.server.document_build.subprocess.run",
                   side_effect=fake_run):
            result = build_pdf(LocalFiles(self.root), "paper.tex",
                               publish_adjacent=True, latex_engine="latexmk")
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0][0], "/usr/bin/latexmk")
        self.assertEqual(calls[0][1]["cwd"], self.root)
        self.assertEqual((self.root / "paper.pdf").read_bytes(),
                         b"%PDF-1.4\\nvalid content")
        self.assertTrue((self.root / result["pdf"]).exists())
        self.assertTrue((self.root / result["synctex"]).exists())

    def test_failure_does_not_publish_stale_pdf(self):
        (self.root / "paper.pdf").write_bytes(b"old PDF")
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/latexmk"), \
             patch("zefm.server.document_build.subprocess.run",
                   return_value=subprocess.CompletedProcess(
                       ["latexmk"], 12, "", "bad source")):
            result = build_pdf(LocalFiles(self.root), "paper.tex",
                               publish_adjacent=True, latex_engine="latexmk")
        self.assertFalse(result["ok"])
        self.assertEqual(result["returncode"], 12)
        self.assertIn("bad source", result["log"])
        self.assertEqual((self.root / "paper.pdf").read_bytes(), b"old PDF")


if __name__ == "__main__":
    unittest.main()
