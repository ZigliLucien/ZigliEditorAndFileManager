"""Browser text viewing: Yiddish, GNU info, unknown text and binary files."""
import tempfile
import unittest
from pathlib import Path

from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.file_types import handler_for
from zefm.server.text_preview import preview_text, readable_utf8


class TextPreviewTests(unittest.TestCase):
    def test_registry_for_yiddish_info_and_unknown(self):
        self.assertEqual(handler_for("lesson.yid")["view"], "yiddish")
        self.assertEqual(handler_for("manual.info")["view"], "text")
        self.assertEqual(handler_for("notes.weird")["view"], "auto")
        self.assertEqual(handler_for("file.png")["view"], "image")
        self.assertEqual(handler_for("file.gz")["view"], "download")

    def test_yiddish_rtl_and_escaped_markup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lesson.yid").write_text(
                'שלום־עליכם ייִדיש\n<script>alert(1)</script> 42',
                encoding="utf-8")
            html = preview_text(LocalFiles(root), "lesson.yid")
            self.assertIn('lang="yi" dir="rtl"', html)
            self.assertIn('שלום־עליכם', html)
            self.assertIn('&lt;script&gt;', html)
            self.assertNotIn('<script>', html)

    def test_info_and_arbitrary_extension_as_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manual.info").write_text("File: manual.info\nNode: Top", encoding="utf-8")
            (root / "notes.xyz").write_text("Cœur ייִדיש", encoding="utf-8")
            files = LocalFiles(root)
            self.assertIn('Node: Top', preview_text(files, "manual.info"))
            self.assertIn('Cœur ייִדיש', preview_text(files, "notes.xyz", automatic=True))

    def test_unknown_binary_returns_none(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "binary.xyz").write_bytes(bytes.fromhex("00 ff 01 02"))
            self.assertIsNone(preview_text(LocalFiles(root), "binary.xyz", automatic=True))
        self.assertIsNone(readable_utf8(b'\\xff\\xfe\\x00'))
        self.assertEqual(readable_utf8(b"plain\r\ntext"), "plain\r\ntext")

    def test_large_unknown_binary_not_loaded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (root / "big.blob").open("wb") as output:
                output.seek(4 * 1024 * 1024)
                output.write(b'x')
            self.assertIsNone(preview_text(LocalFiles(root), "big.blob", automatic=True))

    def test_known_invalid_utf8_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.info").write_bytes(bytes.fromhex("ff fe 00 01"))
            with self.assertRaises(BrowserError):
                preview_text(LocalFiles(root), "bad.info")


if __name__ == "__main__":
    unittest.main()
