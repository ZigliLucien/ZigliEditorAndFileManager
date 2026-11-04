"""JPEG/PNG regressions for the browser image preview.

The old handler accidentally used escaped text (b"\\\\xff") rather than
binary JPEG and PNG signature bytes.
"""
import tempfile
import unittest
from pathlib import Path

from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.image_preview import image_preview, valid_image_header


class ImagePreviewTests(unittest.TestCase):
    def test_correct_binary_magic_headers(self):
        good = {
            ".jpg": bytes.fromhex("ff d8 ff e0") + b"JFIF",
            ".jpeg": bytes.fromhex("ff d8 ff e1") + b"Exif",
            ".png": bytes.fromhex("89 50 4e 47 0d 0a 1a 0a"),
            ".gif": b"GIF89a",
            ".webp": b"RIFF" + (8).to_bytes(4, "little") + b"WEBPVP8 ",
            ".bmp": b"BM" + bytes(30),
            ".avif": bytes.fromhex("00 00 00 18") + b"ftypavif" + bytes(20),
        }
        for suffix, header in good.items():
            with self.subTest(suffix=suffix):
                self.assertTrue(valid_image_header(suffix, header))

    def test_reject_textual_escape_sequence_and_mismatched_type(self):
        self.assertFalse(valid_image_header(".jpg", b"\\\\xff\\\\xd8\\\\xff"))
        self.assertFalse(valid_image_header(".png", b"not a png"))
        self.assertFalse(valid_image_header(".webp", b"RIFF" + bytes(4) + b"NOPE"))

    def test_jpeg_file_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            body = bytes.fromhex("ff d8 ff e0") + b"JFIF" + bytes(64)
            (root / "photo.JPG").write_bytes(body)
            self.assertEqual(image_preview(LocalFiles(root), "photo.JPG", ".jpg"), body)

    def test_bad_jpeg_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "false.jpg").write_bytes(b"not a JPEG")
            with self.assertRaises(BrowserError):
                image_preview(LocalFiles(root), "false.jpg", ".jpg")


if __name__ == "__main__":
    unittest.main()
