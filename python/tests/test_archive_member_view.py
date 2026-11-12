"""Source-guided XCommands.runT: read-only preview of one UTF-8 member.

The member preview neither extracts a file nor executes embedded markup.
"""
import io
from pathlib import Path
import stat
import tarfile
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
import unittest
import warnings
from zipfile import ZipFile, ZipInfo

from zefm.server.archive_extract import MAX_PREVIEW_BYTES, view_text_member
from zefm.server.archive_preview import archive_listing
from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.http import BrowserServer


class ArchiveMemberViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.zipfile = self.root / "samples.zip"
        with ZipFile(self.zipfile, "w") as archive:
            archive.writestr("notes/cœur ייִדיש.txt", "Bonjour שלום\n")
            archive.writestr("html/<script>.html", "<script>alert('x')</script>\n")
            archive.writestr("bytes/malformed.txt", b"\xff\xfe")
            archive.writestr("bytes/nul.txt", b"abc\x00def")
            archive.writestr("bytes/large.txt", b"x" * (MAX_PREVIEW_BYTES + 1))
            archive.writestr("docs/second.txt", "SECOND")
        self.files = LocalFiles(self.root)

    def test_zip_unicode_preview_does_not_extract_any_files(self):
        before = sorted(path.name for path in self.root.iterdir())
        text = view_text_member(self.files, "samples.zip", "notes/cœur ייִדיש.txt")
        self.assertEqual(text, "Bonjour שלום\n")
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), before)
        self.assertFalse((self.root / "notes").exists())

    def test_tar_gzip_utf8_text_and_link_refusal(self):
        archive_path = self.root / "sample.tgz"
        content = "אַ גוטן טאָג".encode("utf-8")
        with tarfile.open(archive_path, "w:gz") as archive:
            entry = tarfile.TarInfo("./text/ייִדיש.yid")
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))
            link = tarfile.TarInfo("outside")
            link.type = tarfile.SYMTYPE
            link.linkname = "../secret"
            archive.addfile(link)
            hardlink = tarfile.TarInfo("hardlink")
            hardlink.type = tarfile.LNKTYPE
            hardlink.linkname = "./text/ייִדיש.yid"
            archive.addfile(hardlink)
        self.assertEqual(
            view_text_member(self.files, "sample.tgz", "./text/ייִדיש.yid"),
            "אַ גוטן טאָג")
        for unsafe in ("outside", "hardlink"):
            with self.subTest(unsafe=unsafe), self.assertRaises(BrowserError) as caught:
                view_text_member(self.files, "sample.tgz", unsafe)
            self.assertEqual(caught.exception.status, 415)

    def test_utf8_bom_is_accepted_and_binary_is_rejected(self):
        with ZipFile(self.zipfile, "a") as archive:
            archive.writestr("notes/bom.txt", b"\xef\xbb\xbfBonjour")
        self.assertEqual(view_text_member(self.files, "samples.zip",
                                          "notes/bom.txt"), "Bonjour")
        for name in ("bytes/malformed.txt", "bytes/nul.txt"):
            with self.subTest(name=name), self.assertRaises(BrowserError) as caught:
                view_text_member(self.files, "samples.zip", name)
            self.assertEqual(caught.exception.status, 415)

    def test_large_member_rejected_before_decompression(self):
        with self.assertRaises(BrowserError) as caught:
            view_text_member(self.files, "samples.zip", "bytes/large.txt")
        self.assertEqual(caught.exception.status, 413)

    def test_unsafe_duplicate_or_symlink_member_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(self.zipfile, "a") as archive:
                archive.writestr("docs/second.txt", "ambiguous")
                archive.writestr("../unsafe.txt", "BAD")
                info = ZipInfo("notes/symlink.txt")
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, "../outside")
        for name, expected in (
            ("docs/second.txt", 409),
            ("../unsafe.txt", 400),
            ("notes/symlink.txt", 415)
        ):
            with self.subTest(name=name), self.assertRaises(BrowserError) as caught:
                view_text_member(self.files, "samples.zip", name)
            self.assertEqual(caught.exception.status, expected)

    def test_links_only_for_eligible_text_members(self):
        listing = archive_listing(self.files, "samples.zip",
                                  enable_extract=True, enable_preview=True)
        self.assertIn("View text", listing)
        self.assertIn("Extract…", listing)
        self.assertIn("member=notes%2Fc%C5%93ur+", listing)
        large_row = next(row for row in listing.split("<tr>") if "bytes/large.txt" in row)
        self.assertNotIn("View text", large_row)
        self.assertIn("Extract…", large_row)
        binary_row = next(row for row in listing.split("<tr>") if "bytes/malformed.txt" in row)
        self.assertIn("View text", binary_row)  # Declared .txt; invalid UTF-8 is rejected on read.
        old = archive_listing(self.files, "samples.zip")
        self.assertIn("Read-only listing", old)
        self.assertNotIn("View text", old)
        self.assertNotIn("Extract…", old)


class ArchiveMemberViewBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with ZipFile(self.root / "data.zip", "w") as archive:
            archive.writestr("source/français-ייִדיש.html",
                             "<script>alert('BAD')</script>\nسلام")
            archive.writestr("source/binary.bin", b"hello\x00world")
            archive.writestr("source/large.txt", b"X" * (MAX_PREVIEW_BYTES + 1))
        self.server = BrowserServer(self.root)
        self.server.start()
        self.addCleanup(self.server.close)

    def get(self, route):
        try:
            with urlopen(self.server.url.rstrip("/") + route, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def test_listing_to_view_text_and_back_without_writing(self):
        code, listing = self.get("/view?" + urlencode({"path": "data.zip"}))
        self.assertEqual(code, 200)
        self.assertIn("View text", listing)
        self.assertIn("Extract…", listing)
        binary_row = next(row for row in listing.split("<tr>") if "source/binary.bin" in row)
        self.assertNotIn("View text", binary_row)
        self.assertIn("Extract…", binary_row)
        target = "/view-entry?" + urlencode(
            {"path": "data.zip", "member": "source/français-ייִדיש.html"})
        code, preview = self.get(target)
        self.assertEqual(code, 200, preview)
        self.assertIn("Archive text member:", preview)
        self.assertIn("Read-only UTF-8 preview", preview)
        self.assertIn('dir="auto"', preview)
        self.assertIn("&lt;script&gt;alert", preview)
        self.assertNotIn("<script>alert", preview)
        self.assertIn("← Back to archive listing", preview)
        self.assertIn("سلام", preview)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["data.zip"])

    def test_malformed_unsafe_oversized_query_rejections(self):
        base = {"path": "data.zip"}
        cases = [
            ({"member": "source/binary.bin"}, 415),
            ({"member": "source/large.txt"}, 413),
            ({"member": "../escape.txt"}, 400),
            ({"member": "not-found.txt"}, 404),
            ({"member": "source/français-ייִדיש.html", "extra": "bad"}, 400),
            ({}, 400)
        ]
        for params, expected in cases:
            with self.subTest(params=params):
                status, _ = self.get("/view-entry?" + urlencode({**base, **params}))
                self.assertEqual(status, expected)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["data.zip"])


if __name__ == "__main__":
    unittest.main()
