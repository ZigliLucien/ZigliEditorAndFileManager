"""v48: regression checks for the reconstructed ZEFM listing.

Original sources: ServPak/xsl/lister.xsl, locxsorter.xsl,
ServPak/css/listing.css, ServPak/js/listing.js, NetsManager/Xlster.java.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from zefm.server.http import BrowserServer
from zefm.storage.word_notes import WordNotes


class OriginalListingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "shared"
        self.root.mkdir()
        self.note_path = Path(self.tmp.name) / "notes.json"
        (self.root / "Alpha").mkdir()
        (self.root / "beta").mkdir()
        (self.root / "cœur ייִדיש.txt").write_text("שלום", encoding="utf-8")
        (self.root / "math.tex").write_text("E=mc^2", encoding="utf-8")
        WordNotes(self.note_path).put(str((self.root / "cœur ייִדיש.txt").resolve()),
                                      "שלום", "A note with <img src=x onerror=alert(1)>")
        self.server = BrowserServer(self.root, notes_path=self.note_path,
                                    open_in_editor=lambda path: None)
        self.server.start()
        self.addCleanup(self.server.close)

    def get(self, route):
        try:
            with urlopen(self.server.url.rstrip("/") + route, timeout=4) as r:
                return r.status, r.read(), dict(r.headers)
        except HTTPError as e:
            return e.code, e.read(), dict(e.headers)

    def test_original_listing_shell_and_security_policy(self):
        status, data, headers = self.get("/listing")
        self.assertEqual(status, 200)
        html = data.decode("utf-8")
        self.assertIn('id="directory-grid"', html)
        self.assertIn('id="file-list"', html)
        self.assertIn('id="file-operations"', html)
        self.assertIn('id="pages"', html)
        self.assertIn('name="fileops" value="copy"', html)
        self.assertIn('name="fileops" value="move" disabled', html)
        self.assertIn('name="fileops" value="delete" disabled', html)
        self.assertIn('src="/listing.js"', html)
        self.assertIn('href="/listing.css"', html)
        self.assertIn('data-editor="true"', html)
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        self.assertIn("connect-src 'self'", headers["Content-Security-Policy"])
        self.assertIn("style-src 'self'", headers["Content-Security-Policy"])

    def test_json_directory_model_unicode_notes_and_metadata(self):
        status, data, headers = self.get("/api/files?path=.")
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers["Content-Type"])
        payload = json.loads(data)
        self.assertEqual(payload["relative"], ".")
        self.assertEqual(payload["parent"], None)
        self.assertEqual(payload["breadcrumbs"], [{"name": "/", "path": "."}])
        self.assertEqual({d["name"] for d in payload["folders"]}, {"Alpha", "beta"})
        row = next(row for row in payload["files"] if row["name"] == "cœur ייִדיש.txt")
        self.assertEqual(row["kind"], "file")
        self.assertEqual(row["size"], len("שלום".encode("utf-8")))
        self.assertEqual(row["note_count"], 1)
        self.assertIn("<img", row["note"])
        self.assertEqual(row["type"], "txt")
        self.assertTrue(row["date"])
        self.assertTrue(row["time"])

    def test_nested_breadcrumbs_and_parent(self):
        (self.root / "Alpha" / "Sub").mkdir()
        status, data, _ = self.get("/api/files?" + urlencode({"path": "Alpha/Sub"}))
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertEqual(payload["parent"], "Alpha")
        self.assertEqual(payload["breadcrumbs"][-1], {"name": "Sub", "path": "Alpha/Sub"})

    def test_assets_restore_original_colors_and_render_safely(self):
        status, css, _ = self.get("/listing.css")
        self.assertEqual(status, 200)
        self.assertIn(b"#ffffee", css)
        self.assertIn(b"#eeffff", css)
        self.assertIn(b"#5555ff", css)
        self.assertIn(b"#cc9908", css)
        status, script, _ = self.get("/listing.js")
        self.assertEqual(status, 200)
        self.assertIn(b"textContent", script)
        self.assertIn(b"replaceChildren", script)
        self.assertIn(b"/api/listing-page", script)
        self.assertNotIn(b".innerHTML", script)
        self.assertIn(b"pageSize: 25", script)

    def test_gofm_page_deep_links_and_invalid_page_parameters(self):
        for page in (1, 2, 25, 100):
            status, body, _ = self.get("/listing?" + urlencode({"path": ".", "page": page}))
            self.assertEqual(status, 200, body.decode("utf-8"))
        for value in ("0", "-1", "two", "1/../../", "999999999999", ""):
            status, _, _ = self.get("/listing?" + urlencode({"path": ".", "page": value}))
            self.assertEqual(status, 400)
        status, _, _ = self.get("/listing?" + urlencode({"path": "..", "page": 2}))
        self.assertEqual(status, 403)

    def test_gofm_navigation_and_extension_based_groups(self):
        status, script, _ = self.get("/listing.js")
        self.assertEqual(status, 200)
        for feature in (b'pageGroups(rows)', b'state.sort === "filetype"',
                        b'groups[groups.length - 1][0].type', b'pageSize: 25',
                        b'"Top"', b'"Bottom"', b'"Previous"', b'"Next"',
                        b'"Listing " + (state.page + 1)',
                        b'"gofm-references"', b'history.pushState',
                        b'window.addEventListener("popstate"'):
            with self.subTest(feature=feature):
                self.assertIn(feature, script)
        status, css, _ = self.get("/listing.css")
        self.assertEqual(status, 200)
        self.assertIn(b"gofm-references", css)
        self.assertIn(b"repeat(10", css)

    def test_legacy_listing_is_still_available(self):
        status, html, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"Original ZEFM-style listing", html)
        self.assertIn("Quick edit", html.decode("utf-8"))

    def test_external_symlink_is_not_exposed_in_json(self):
        outside = Path(self.tmp.name) / "secret.txt"
        outside.write_text("private")
        (self.root / "outside").symlink_to(outside)
        status, data, _ = self.get("/api/files")
        self.assertEqual(status, 200)
        model = json.loads(data)
        self.assertNotIn("outside", [item["name"] for item in model["files"]])

    def test_traversal_and_bad_parameters_are_rejected(self):
        self.assertEqual(self.get("/api/files?path=..")[0], 403)
        self.assertEqual(self.get("/listing?path=..")[0], 403)
        self.assertEqual(self.get("/listing?unknown=1")[0], 400)
        self.assertEqual(self.get("/api/files?path=.&unknown=1")[0], 400)
        self.assertEqual(self.get("/listing.js?unexpected=1")[0], 400)

    def test_untracked_missing_notes_is_empty(self):
        status, data, _ = self.get("/api/files")
        self.assertEqual(status, 200)
        model = json.loads(data)
        math_file = next(row for row in model["files"] if row["name"] == "math.tex")
        self.assertEqual(math_file["note_count"], 0)
        self.assertEqual(math_file["note"], "—")


if __name__ == "__main__":
    unittest.main()
