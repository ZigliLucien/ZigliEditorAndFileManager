"""v99: browser defaults and optional Okular SyncTeX integration."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.pdf_viewer import PdfViewerPreference, okular_argv, launch_okular


class PdfViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "config" / "viewer.json"
        self.pdf = self.root / "cœur page.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\n")
        self.tex = self.root / "cœur page.tex"
        self.tex.write_text("LaTeX")
        self.index = self.pdf.with_suffix(".synctex.gz")
        self.index.write_bytes(b"index")

    def test_browser_is_default_and_okular_selection_persists(self):
        prefs = PdfViewerPreference(self.config)
        self.assertEqual(prefs.viewer, "browser")
        prefs.set("okular")
        self.assertEqual(PdfViewerPreference(self.config).viewer, "okular")
        prefs.set("browser")
        self.assertEqual(PdfViewerPreference(self.config).viewer, "browser")
        self.assertEqual(json.loads(self.config.read_text())["viewer"], "browser")

    def test_bad_choice_does_not_change_selection(self):
        prefs = PdfViewerPreference(self.config)
        with self.assertRaises(ValueError):
            prefs.set("evince")
        self.assertEqual(prefs.viewer, "browser")

    def test_okular_plain_view_and_synctex_forward_argv(self):
        with patch("zefm.editor.pdf_viewer.shutil.which",
                   return_value="/usr/bin/okular"):
            self.assertEqual(okular_argv(self.pdf),
                             ["/usr/bin/okular", "--unique", str(self.pdf)])
            self.assertEqual(okular_argv(self.pdf, source=self.tex, line=21),
                             ["/usr/bin/okular", "--unique",
                              self.pdf.as_uri() + "#src:21" + str(self.tex)])
            with patch("zefm.editor.pdf_viewer.subprocess.Popen") as launched:
                launch_okular(self.pdf, source=self.tex, line=21)
        self.assertEqual(launched.call_args.args[0][1], "--unique")
        self.assertNotIn("shell", launched.call_args.kwargs)

    def test_missing_okular_or_index_fails_cleanly(self):
        with patch("zefm.editor.pdf_viewer.shutil.which", return_value=None):
            with self.assertRaisesRegex(ValueError, "not installed"):
                okular_argv(self.pdf)
        self.index.unlink()
        with patch("zefm.editor.pdf_viewer.shutil.which",
                   return_value="/usr/bin/okular"):
            with self.assertRaisesRegex(ValueError, "No matching SyncTeX"):
                okular_argv(self.pdf, source=self.tex, line=1)


if __name__ == "__main__":
    unittest.main()
