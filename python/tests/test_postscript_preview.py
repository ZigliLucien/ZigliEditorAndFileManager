"""PS/EPS preview dispatch and source validation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.file_types import handler_for
from zefm.server.postscript_preview import postscript_pdf


class PostscriptPreviewTests(unittest.TestCase):
    def test_extensions(self):
        self.assertEqual(handler_for("figure.EPS")["view"], "postscript")
        self.assertEqual(handler_for("notes.ps")["view"], "postscript")
        self.assertEqual(handler_for("paper.pdf")["view"], "pdf")

    def test_missing_ghostscript(self):
        with tempfile.TemporaryDirectory() as base:
            path = Path(base) / "figure.eps"
            path.write_text("%!PS-Adobe-3.0 EPSF-3.0\n", encoding="utf-8")
            with patch("zefm.server.postscript_preview.shutil.which", return_value=None):
                with self.assertRaises(BrowserError) as error:
                    postscript_pdf(LocalFiles(base), "figure.eps")
            self.assertEqual(error.exception.status, 501)

    def test_reject_non_postscript(self):
        with tempfile.TemporaryDirectory() as base:
            (Path(base) / "other.txt").write_text("hello", encoding="utf-8")
            with self.assertRaises(BrowserError):
                postscript_pdf(LocalFiles(base), "other.txt")


if __name__ == "__main__":
    unittest.main()
