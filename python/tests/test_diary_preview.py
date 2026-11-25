"""Preview diary Markdown/HTML without writing, then save source unchanged."""
import re
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import CalendarDiary


class DiaryPreviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "calendar.csv"
        self.server = BrowserServer(temporary.name, calendar_path=self.path)
        self.server.start()
        self.addCleanup(self.server.close)
        self.store = CalendarDiary(self.path)

    def get(self, url):
        with urlopen(self.server.url + url, timeout=4) as response:
            return response.read().decode("utf-8")

    def post(self, fields):
        request = Request(self.server.url + "diary-preview",
                          data=urlencode(fields).encode("utf-8"),
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urlopen(request, timeout=4) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_new_diary_preview_is_read_only_and_source_editable(self):
        source = "# My notes\n\n**bold** <u>important</u>\n<script>alert(1)</script>"
        status, html = self.post({"csrf": self.server.token, "date": "2026-11-25",
                                  "kind": "diary", "text": source})
        self.assertEqual(status, 200)
        self.assertIn("<h1>My notes</h1>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<u>important</u>", html)
        self.assertNotIn("<script>", html)
        self.assertNotIn("alert(1)</script>", html)
        self.assertIn("Preview only: nothing has been saved.", html)
        self.assertIn('formaction="/diary-preview"', html)
        self.assertIn('action="/diary"', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertFalse(self.path.exists())

    def test_edit_preview_preserves_record_and_revision(self):
        self.store.add("2026-11-25", "old")
        revision = self.store.revision()
        status, html = self.post({
            "csrf": self.server.token, "date": "2026-11-25",
            "row": "0", "revision": revision, "new_date": "2026-11-26",
            "kind": "appointment", "text": "**new**"})
        self.assertEqual(status, 200)
        self.assertIn("<strong>new</strong>", html)
        self.assertIn('action="/diary-edit"', html)
        self.assertIn('name="new_date" value="2026-11-26"', html)
        self.assertIn('name="revision" value="' + revision + '"', html)
        self.assertEqual(self.store.read()[0]["text"], "old")
        self.assertEqual(self.store.revision(), revision)

    def test_missing_token_and_invalid_content_rejected(self):
        for fields, expected in [
            ({"csrf": "bad", "date": "2026-11-25", "kind": "diary",
              "text": "example"}, 403),
            ({"csrf": self.server.token, "date": "2026-11-25", "kind": "diary",
              "text": ""}, 400),
            ({"csrf": self.server.token, "date": "2026-02-30", "kind": "diary",
              "text": "example"}, 400)
        ]:
            code, _ = self.post(fields)
            self.assertEqual(code, expected)
        self.assertFalse(self.path.exists())

    def test_forms_offer_preview_before_save(self):
        html = self.get("diary?date=2026-11-25")
        self.assertIn('formaction="/diary-preview"', html)
        self.store.add("2026-11-25", "test")
        html = self.get("diary-edit?date=2026-11-25&row=0")
        self.assertIn('formaction="/diary-preview"', html)


if __name__ == "__main__":
    unittest.main()
