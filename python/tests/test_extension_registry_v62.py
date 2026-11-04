"""Regression tests for extension detection and archive previews."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from zefm.server.archive_preview import archive_listing
from zefm.server.file_manager import LocalFiles
from zefm.server.file_types import handler_for


class FileTypeTests(unittest.TestCase):
    def test_common_formats(self):
        expected = {
            "image.JPG": ("image", "image/jpeg"),
            "image.PNG": ("image", "image/png"),
            "image.gif": ("image", "image/gif"),
            "backup.tgz": ("archive", "application/gzip"),
            "backup.tar.gz": ("archive", "application/gzip"),
            "library.jar": ("archive", "application/java-archive"),
            "archive.ZIP": ("archive", "application/zip"),
            "book.epub": ("epub", "application/epub+zip"),
            "paper.djvu": ("djvu", "image/vnd.djvu"),
        }
        for name, (action, mime) in expected.items():
            with self.subTest(name=name):
                desc = handler_for(name)
                self.assertEqual(desc["view"], action)
                self.assertEqual(desc["mime"], mime)

    def test_unknown_binary_not_interpreted_as_text(self):
        self.assertEqual(handler_for("mystery.pnf")["view"], "auto")

    def test_jar_archive_lists_without_extraction(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            with ZipFile(root / "hello.jar", "w") as archive:
                archive.writestr("example/Hello.class", b"data")
            html = archive_listing(LocalFiles(root), "hello.jar")
            self.assertIn("example/Hello.class", html)
            self.assertFalse((root / "example").exists())


if __name__ == "__main__":
    unittest.main()
