"""GoFM/Xlster paging: bounded responses, 25-file blocks, extension groups."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from zefm.server.http import BrowserServer
from zefm.storage.word_notes import WordNotes


class GoFMPagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "docs"
        self.root.mkdir()
        (self.root / "Folder").mkdir()
        self.note_path = Path(self.tmp.name) / "notes.json"
        for i in range(63):
            (self.root / f"document-{i:03d}.txt").write_text(
                "Test " + str(i), encoding="utf-8")
        for i in range(4):
            (self.root / f"image-{i:02d}.png").write_bytes(b"PNG" + bytes([i]))
        (self.root / ".secret").write_text("hidden")
        WordNotes(self.note_path).put(str((self.root / "document-061.txt").resolve()),
                                      "key", "Annotated document")
        self.server = BrowserServer(self.root, notes_path=self.note_path)
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, **params):
        try:
            with urlopen(self.server.url + "api/listing-page?" +
                         urlencode(params), timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as err:
            return err.code, err.read().decode()

    def test_filename_page_boundaries(self):
        status, a = self.request(path=".", page=1, sort="filename")
        self.assertEqual(status, 200)
        self.assertEqual(a["total_files"], 67)
        self.assertEqual(a["page_count"], 3)
        self.assertEqual(len(a["files"]), 25)
        self.assertEqual(a["files"][0]["name"], "document-000.txt")
        self.assertEqual(a["page_start"], 1)
        self.assertEqual(a["page_end"], 25)
        self.assertEqual(a["references"][0]["label"], "docu")
        status, b = self.request(path=".", page=3, sort="filename")
        self.assertEqual(status, 200)
        self.assertEqual(len(b["files"]), 17)
        self.assertEqual(b["page_start"], 51)
        self.assertEqual(b["page_end"], 67)
        self.assertEqual(b["files"][0]["name"], "document-050.txt")
        self.assertEqual(len(a["folders"]), 1)
        self.assertNotIn(".secret", [x["name"] for x in a["files"]])

    def test_extension_groups_match_original(self):
        status, result = self.request(page=2, sort="filetype")
        self.assertEqual(status, 200)
        self.assertEqual(result["page_count"], 2)
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["total_files"], 67)
        self.assertEqual({row["type"] for row in result["files"]}, {"txt"})
        self.assertEqual(len(result["files"]), 63)
        self.assertEqual([r["label"] for r in result["references"]], ["png", "txt"])

    def test_filter_and_notes(self):
        status, result = self.request(page=1, sort="filename", filter="document-06")
        self.assertEqual(status, 200)
        self.assertEqual(result["total_files"], 3)
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(len(result["files"]), 3)
        note_row = next(r for r in result["files"] if r["name"] == "document-061.txt")
        self.assertEqual(note_row["note_count"], 1)
        self.assertIn("Annotated document", note_row["note"])

    def test_sorting_by_size_and_notes(self):
        status, result = self.request(page=1, sort="notes")
        self.assertEqual(status, 200)
        self.assertEqual(result["page_count"], 3)
        self.assertEqual(len(result["files"]), 25)
        status, result = self.request(page=1, sort="size")
        self.assertEqual(status, 200)
        self.assertEqual(len(result["files"]), 25)

    def test_page_out_of_range_and_invalid_inputs(self):
        status, result = self.request(page=999, sort="filename")
        self.assertEqual(status, 200)
        self.assertEqual(result["page"], 3)
        for args in ({"page": 0}, {"page": -1}, {"page": "bad"},
                     {"page": "1" * 30}, {"sort": "wrong"},
                     {"filter": "x" * 201}, {"path": ".."},
                     {"unexpected": "x"}):
            code, _ = self.request(**args)
            self.assertIn(code, (400, 403), args)

    def test_empty_directory(self):
        (self.root / "Empty").mkdir()
        code, result = self.request(path="Empty", page=1)
        self.assertEqual(code, 200)
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(result["total_files"], 0)
        self.assertEqual(result["files"], [])
        self.assertEqual(result["page_start"], 0)
        self.assertEqual(result["page_end"], 0)


if __name__ == "__main__":
    unittest.main()
