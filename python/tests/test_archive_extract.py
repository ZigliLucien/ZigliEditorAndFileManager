"""Source-guided XCommands.runT: safe one-member ZIP/TAR extraction.

No automatic extraction, arbitrary archive paths, symlinks, or overwrite.
"""
import io
import os
from pathlib import Path
import stat
import tarfile
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import warnings
from zipfile import ZipFile, ZipInfo

from zefm.server.archive_extract import (
    MAX_EXTRACT_BYTES, _copy_limited, extract_entry, member_details)
from zefm.server.archive_preview import archive_listing
from zefm.server.file_manager import BrowserError, LocalFiles
from zefm.server.http import BrowserServer


class ExtractModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "files"
        self.root.mkdir()
        (self.root / "Dest").mkdir()
        self.files = LocalFiles(self.root)
        self.zipped = self.root / "sample.zip"
        with ZipFile(self.zipped, "w") as archive:
            archive.writestr("docs/cœur ייִדיש.txt", "Bonjour שלום".encode("utf-8"))
            archive.writestr("docs/another.txt", b"second")
            archive.writestr("empty/", b"")

    def test_zip_selected_member_unicode_and_flat_output(self):
        default, size = member_details(self.files, "sample.zip", "docs/cœur ייִדיש.txt")
        self.assertEqual(default, "cœur ייִדיש.txt")
        self.assertEqual(size, len("Bonjour שלום".encode("utf-8")))
        target = extract_entry(self.files, "sample.zip", "docs/cœur ייִדיש.txt",
                               "Dest", "renamed.txt")
        self.assertEqual(target, self.root / "Dest" / "renamed.txt")
        self.assertEqual(target.read_text(encoding="utf-8"), "Bonjour שלום")
        self.assertFalse((self.root / "docs").exists())
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        self.assertTrue(self.zipped.exists())
        self.assertEqual(list((self.root / "Dest").glob(".zefm-extract-*")), [])

    def test_existing_file_and_symlink_never_overwritten(self):
        original = self.root / "Dest" / "another.txt"
        original.write_text("KEEP", encoding="utf-8")
        with self.assertRaises(BrowserError) as error:
            extract_entry(self.files, "sample.zip", "docs/another.txt", "Dest")
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(original.read_text(), "KEEP")
        original.unlink()
        original.symlink_to(self.root / "sample.zip")
        with self.assertRaises(BrowserError):
            extract_entry(self.files, "sample.zip", "docs/another.txt", "Dest")
        self.assertTrue(original.is_symlink())
        self.assertFalse(list((self.root / "Dest").glob(".zefm-extract-*")))

    def test_symlink_destination_and_outside_root_denied(self):
        (self.root / "shortcut").symlink_to(self.root / "Dest", target_is_directory=True)
        for destination in ("shortcut", "../outside", "/tmp",
                            "Dest/../Dest"):
            with self.subTest(destination=destination), self.assertRaises(BrowserError):
                extract_entry(self.files, "sample.zip", "docs/another.txt",
                              destination)
        self.assertEqual(list((self.root / "Dest").iterdir()), [])

    def test_invalid_member_paths_are_not_offered_or_extracted(self):
        with ZipFile(self.zipped, "a") as archive:
            for member in ("../escape.txt", "/abs.txt", "C:/windows.txt",
                           "dir\\evil.txt", "dir/../escape.txt",
                           "dir//double.txt"):
                archive.writestr(member, b"unsafe")
        listing = archive_listing(self.files, "sample.zip", enable_extract=True)
        self.assertIn("docs/cœur ייִדיש.txt", listing)
        for member in ("../escape.txt", "/abs.txt", "C:/windows.txt",
                       "dir\\evil.txt", "dir/../escape.txt", "dir//double.txt"):
            with self.subTest(member=member), self.assertRaises(BrowserError):
                extract_entry(self.files, "sample.zip", member, "Dest")
        self.assertFalse((self.root / "escape.txt").exists())
        self.assertEqual(list((self.root / "Dest").iterdir()), [])

    def test_tar_gz_regular_member_only(self):
        archive_path = self.root / "backup.tgz"
        content = "שלום from tar".encode("utf-8")
        with tarfile.open(archive_path, "w:gz") as archive:
            file = tarfile.TarInfo("./research/שלום.txt")
            file.size = len(content)
            archive.addfile(file, io.BytesIO(content))
            link = tarfile.TarInfo("shortcut")
            link.type = tarfile.SYMTYPE
            link.linkname = "../outside"
            archive.addfile(link)
            hardlink = tarfile.TarInfo("hardlink")
            hardlink.type = tarfile.LNKTYPE
            hardlink.linkname = "./research/שלום.txt"
            archive.addfile(hardlink)
        path = extract_entry(self.files, "backup.tgz", "./research/שלום.txt",
                             "Dest")
        self.assertEqual(path.read_bytes(), content)
        for member in ("shortcut", "hardlink"):
            with self.subTest(member=member), self.assertRaises(BrowserError) as error:
                extract_entry(self.files, "backup.tgz", member, "Dest")
            self.assertEqual(error.exception.status, 415)
        self.assertFalse((self.root / "outside").exists())

    def test_zip_symlink_is_never_extractable(self):
        archive_path = self.root / "symlinks.zip"
        info = ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with ZipFile(archive_path, "w") as archive:
            archive.writestr(info, "../outside")
        listing = archive_listing(self.files, "symlinks.zip", enable_extract=True)
        self.assertNotIn(">Extract…</a>", listing)
        with self.assertRaises(BrowserError) as error:
            extract_entry(self.files, "symlinks.zip", "link", "Dest")
        self.assertEqual(error.exception.status, 415)

    def test_duplicate_zip_member_is_not_extractable(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(self.zipped, "a") as archive:
                archive.writestr("docs/another.txt", b"surprise")
        listing = archive_listing(self.files, "sample.zip", enable_extract=True)
        self.assertNotIn("member=docs%2Fanother.txt", listing)
        with self.assertRaises(BrowserError) as error:
            extract_entry(self.files, "sample.zip", "docs/another.txt", "Dest")
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(list((self.root / "Dest").iterdir()), [])

    def test_size_limit_and_cleanup_when_stream_exceeds_expected(self):
        output = io.BytesIO()
        with self.assertRaises(BrowserError) as error:
            _copy_limited(io.BytesIO(b"b" * 10), output, 4)
        self.assertEqual(error.exception.status, 413)
        self.assertFalse(list((self.root / "Dest").glob(".zefm-extract-*")))
        self.assertEqual(MAX_EXTRACT_BYTES, 64 * 1024 * 1024)

    def test_invalid_extension_and_filename(self):
        (self.root / "notarchive.txt").write_text("x")
        with self.assertRaises(BrowserError) as error:
            extract_entry(self.files, "notarchive.txt", "file.txt", "Dest")
        self.assertEqual(error.exception.status, 415)
        for filename in ("../escape", "file/name", "bad\\name", ""):
            if not filename:
                continue  # A blank filename requests the member's basename.
            with self.subTest(filename=filename), self.assertRaises(BrowserError):
                extract_entry(self.files, "sample.zip", "docs/another.txt",
                              "Dest", filename)


class ExtractBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "files"
        self.root.mkdir()
        (self.root / "Destination").mkdir()
        self.archive = self.root / "archive.zip"
        with ZipFile(self.archive, "w") as output:
            output.writestr("data/שלום.txt", "Test שלום".encode("utf-8"))
            output.writestr("data/other.txt", b"data")
        self.server = BrowserServer(self.root)
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, route, fields=None):
        payload = urlencode(fields).encode("utf-8") if fields is not None else None
        request = Request(self.server.url.rstrip("/") + route,
                          data=payload,
                          headers={"Content-Type": "application/x-www-form-urlencoded"}
                          if payload is not None else {})
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_archive_view_links_to_confirmation_then_post_extracts(self):
        status, html = self.request("/view?" + urlencode({"path": "archive.zip"}))
        self.assertEqual(status, 200)
        self.assertIn("Extract…", html)
        self.assertIn("/extract-entry?path=archive.zip&amp;member=", html)
        self.assertEqual(list((self.root / "Destination").iterdir()), [])

        uri = "/extract-entry?" + urlencode({
            "path": "archive.zip", "member": "data/שלום.txt"})
        status, form = self.request(uri)
        self.assertEqual(status, 200, form)
        self.assertIn('action="/extract-entry"', form)
        self.assertIn('value="שלום.txt"', form)
        self.assertIn('name="csrf"', form)
        self.assertEqual(list((self.root / "Destination").iterdir()), [])
        fields = {"csrf": self.server.token, "path": "archive.zip",
                  "member": "data/שלום.txt", "destination": "Destination",
                  "name": "renamed.txt"}
        status, result = self.request("/extract-entry", fields)
        self.assertEqual(status, 201, result)
        self.assertTrue((self.root / "Destination" / "renamed.txt").is_file())
        self.assertIn("Open destination directory", result)
        self.assertEqual((self.root / "Destination" / "renamed.txt").read_text(),
                         "Test שלום")
        self.assertEqual(self.request("/extract-entry", fields)[0], 409)

    def test_csrf_unknown_fields_and_unsafe_member_are_rejected(self):
        fields = {"csrf": self.server.token, "path": "archive.zip",
                  "member": "data/other.txt", "destination": "Destination",
                  "name": "other.txt"}
        self.assertEqual(self.request("/extract-entry",
                                      {**fields, "csrf": "bad"})[0], 403)
        self.assertEqual(self.request("/extract-entry",
                                      {**fields, "extra": "bad"})[0], 400)
        self.assertEqual(self.request("/extract-entry",
                                      {**fields, "name": "../evil"})[0], 400)
        self.assertEqual(self.request("/extract-entry?" + urlencode({
            "path": "archive.zip", "member": "../evil"}))[0], 400)
        self.assertEqual(self.request("/extract-entry?" + urlencode({
            "path": "archive.zip"}))[0], 400)
        self.assertFalse((self.root / "Destination" / "other.txt").exists())
        self.assertEqual(list((self.root / "Destination").iterdir()), [])

    def test_default_read_only_archive_preview_api_unchanged(self):
        html = archive_listing(LocalFiles(self.root), "archive.zip")
        self.assertIn("Read-only listing", html)
        self.assertNotIn("Extract…", html)


if __name__ == "__main__":
    unittest.main()
