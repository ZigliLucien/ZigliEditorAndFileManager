"""v99: forward SyncTeX source line -> PDF page."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest
from unittest.mock import patch

from zefm.editor.synctex_forward import pdf_page_uri, synctex_page


class ForwardSynctexTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "cœur.tex"
        self.source.write_text("hello", encoding="utf-8")
        self.pdf = self.root / "cœur-unique.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\n")
        self.index = self.pdf.with_suffix(".synctex.gz")
        self.index.write_bytes(b"mock index")

    def test_valid_page_uses_argv_without_shell(self):
        output = "SyncTeX result begin\nOutput:foo.pdf\nPage:7\nx:5\ny:2\n"
        with patch("zefm.editor.synctex_forward.shutil.which",
                   return_value="/usr/bin/synctex"), \
             patch("zefm.editor.synctex_forward.subprocess.run",
                   return_value=subprocess.CompletedProcess(
                       [], 0, stdout=output, stderr="")) as runner:
            page = synctex_page(self.source, 32, self.pdf, column=5)
        self.assertEqual(page, 7)
        self.assertEqual(runner.call_args.args[0], [
            "/usr/bin/synctex", "view", "-i",
            f"32:5:{self.source}", "-o", str(self.pdf)])
        self.assertNotIn("shell", runner.call_args.kwargs)
        self.assertEqual(runner.call_args.kwargs["timeout"], 8)
        self.assertTrue(pdf_page_uri(self.pdf, page).endswith("#page=7"))

    def test_missing_matching_index_prevents_lookup(self):
        self.index.unlink()
        with patch("zefm.editor.synctex_forward.subprocess.run") as runner:
            with self.assertRaisesRegex(ValueError, "matching SyncTeX"):
                synctex_page(self.source, 1, self.pdf)
        runner.assert_not_called()

    def test_missing_executable_and_unmapped_line(self):
        with patch("zefm.editor.synctex_forward.shutil.which",
                   return_value=None):
            with self.assertRaisesRegex(ValueError, "not installed"):
                synctex_page(self.source, 1, self.pdf)
        with patch("zefm.editor.synctex_forward.shutil.which",
                   return_value="/usr/bin/synctex"), \
             patch("zefm.editor.synctex_forward.subprocess.run",
                   return_value=subprocess.CompletedProcess(
                       [], 0, stdout="SyncTeX result begin\n", stderr="")):
            with self.assertRaisesRegex(ValueError, "No corresponding"):
                synctex_page(self.source, 1, self.pdf)

    def test_source_line_validation(self):
        with self.assertRaises(ValueError):
            synctex_page(self.source, 0, self.pdf)
        with self.assertRaises(ValueError):
            pdf_page_uri(self.pdf, 0)


if __name__ == "__main__":
    unittest.main()
