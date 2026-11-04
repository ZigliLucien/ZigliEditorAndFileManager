"""Delimited previews and complete extension jump references."""
import tempfile
import unittest
from pathlib import Path

from zefm.server.delimited_preview import csv_preview
from zefm.server.file_manager import LocalFiles
from zefm.server.file_types import handler_for
from zefm.server.listing_paging import paged_listing


class TablePreviewTests(unittest.TestCase):
    def test_csv_html_escaping_and_multiline_quoted_cell(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data.csv").write_text(
                'Name,Comment\n"Cœur","<script>alert(1)</script>"\n'
                '"Yiddish","line one\nline two"\n', encoding="utf-8")
            files = LocalFiles(root)
            html = csv_preview(files, "data.csv")
            self.assertIn("<th>Name</th>", html)
            self.assertIn("<td>Cœur</td>", html)
            self.assertIn("&lt;script&gt;", html)
            self.assertNotIn("<script>", html)
            self.assertIn("line one\nline two", html)
            self.assertIn("Markdown table", html)

    def test_markdown_and_tsv(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "records.tsv").write_text(
                'Key\tValue\n"a|b"\t12\n', encoding="utf-8")
            files = LocalFiles(root)
            markdown = csv_preview(files, "records.tsv", "markdown")
            self.assertIn("| Key | Value |", markdown)
            self.assertIn(r"a\|b", markdown)
            self.assertEqual(handler_for("records.tsv")["view"], "delimited")
            self.assertEqual(handler_for("records.csv")["view"], "delimited")


class FiletypeJumpIndexTests(unittest.TestCase):
    def test_frontend_renders_full_index(self):
        script = (Path(__file__).resolve().parents[1] /
                  "zefm" / "server" / "listing.js").read_text(encoding="utf-8")
        self.assertIn("function renderFiletypeIndex(references)", script)
        self.assertIn("references.forEach((reference, i)", script)
        self.assertIn('area.hidden = state.sort !== "filetype"', script)
        self.assertIn('selectPage(i)', script)


    def test_all_extensions_are_returned_not_just_next_few(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            extensions = ("bib", "csv", "djvu", "epub", "gif", "html",
                          "jar", "jpg", "json", "md", "pdf", "png",
                          "ps", "py", "tex", "tsv", "xml", "zip")
            for extension in extensions:
                (root / ("example." + extension)).write_bytes(b"example")
            listing = paged_listing(LocalFiles(root), sort="filetype")
            references = listing["references"]
            self.assertEqual(len(references), len(extensions))
            self.assertEqual([ref["label"] for ref in references],
                             sorted(extensions))
            self.assertEqual(listing["page_count"], len(extensions))
            self.assertEqual(listing["files"][0]["type"], "bib")
            later = paged_listing(LocalFiles(root), sort="filetype",
                                  page=extensions.index("xml") + 1)
            self.assertEqual(later["files"][0]["type"], "xml")


if __name__ == "__main__":
    unittest.main()
