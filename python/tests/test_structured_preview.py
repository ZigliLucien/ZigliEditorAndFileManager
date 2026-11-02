"""Tests for port-8000 style structured-document previews."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.file_types import handler_for
from zefm.server.structured_preview import transformed_document


class StructuredPreviewTests(unittest.TestCase):
    def test_extensions(self):
        for filename in ("a.json", "a.xml", "a.ipynb"):
            self.assertEqual(handler_for(filename)["view"], "structured")

    def test_json_xml_escaped(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "a.json").write_text('{"x":"<script>"}', encoding="utf-8")
            (root / "a.xml").write_text('<root><x>&amp;</x></root>', encoding="utf-8")
            files = LocalFiles(root)
            self.assertIn("&lt;script&gt;", transformed_document(files, "a.json"))
            self.assertIn("&lt;root&gt;", transformed_document(files, "a.xml"))

    def test_notebook_missing_nbconvert(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "a.ipynb").write_text("{}", encoding="utf-8")
            with patch("zefm.server.structured_preview.shutil.which", return_value=None):
                with self.assertRaises(BrowserError) as error:
                    transformed_document(LocalFiles(folder), "a.ipynb")
            self.assertEqual(error.exception.status, 501)


if __name__ == "__main__":
    unittest.main()
