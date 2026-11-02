"""Regression checks for ZEFM book handlers (standard library only)."""
import io
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from zipfile import ZipFile

from zefm.server.book_preview import _ppm_to_png, epub_page
from zefm.server.file_types import handler_for
from zefm.server.file_manager import LocalFiles


class BookPreviewTests(unittest.TestCase):
    def test_file_associations(self):
        for name, kind in (("book.EPUB", "epub"), ("scan.djvu", "djvu"),
                           ("scan.DJV", "djvu"), ("notes.tex", "text"),
                           ("paper.pdf", "pdf")):
            self.assertEqual(handler_for(name)["view"], kind)

    def test_rgb_ppm_to_png(self):
        png = _ppm_to_png(b"P6\n2 1\n255\n" + bytes([255, 0, 0, 0, 255, 0]))
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", png[16:24]), (2, 1))

    def test_epub_chapter_navigation_and_escaping(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "book.epub"
            with ZipFile(path, "w") as book:
                book.writestr("META-INF/container.xml",
                    '<container><rootfiles><rootfile full-path="OPS/book.opf"/></rootfiles></container>')
                book.writestr("OPS/book.opf",
                    '<package><manifest><item id="c1" href="a.xhtml" media-type="application/xhtml+xml"/>'
                    '<item id="c2" href="b.xhtml" media-type="application/xhtml+xml"/></manifest>'
                    '<spine><itemref idref="c1"/><itemref idref="c2"/></spine></package>')
                book.writestr("OPS/a.xhtml", "<html><body><p>First &amp; safe</p></body></html>")
                book.writestr("OPS/b.xhtml", "<html><body><p>Second chapter</p></body></html>")
            files = LocalFiles(Path(root))
            first = epub_page(files, "book.epub")
            self.assertIn("First &amp; safe", first)
            self.assertIn("Next", first)
            second = epub_page(files, "book.epub", 1)
            self.assertIn("Second chapter", second)
            self.assertIn("Previous", second)


if __name__ == "__main__":
    unittest.main()
